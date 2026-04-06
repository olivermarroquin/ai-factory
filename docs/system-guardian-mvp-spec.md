# System Guardian MVP Spec

## Purpose

System Guardian MVP is a deterministic validation engine that enforces system integrity by detecting drift, inconsistencies, and invariant violations in ai-factory state and artifacts. It reads authoritative state files and known artifact locations, runs a defined set of checks, and emits a structured pass/fail report.

System Guardian is NOT a planner, executor, or assistant. It does not suggest next actions, interpret intent, or replace ECS. It only validates.

---

## Role in Architecture

| Layer | Role |
|---|---|
| State Surface | Authoritative truth files (`system-state/*.md`) |
| ECS | Reads state, gates and resolves actions |
| System Guardian | Validates state integrity and artifact consistency |

System Guardian runs after state changes and after ECS operations. It does not gate execution — ECS does. System Guardian reports whether the system is in a valid state. Acting on Guardian failures is the operator's responsibility.

---

## Authoritative Inputs

| Input | Role |
|---|---|
| `system-state/current-system-state.md` | Phase and architecture truth |
| `system-state/current-objective.md` | Objective, next steps, constraints, blocked actions, exit condition |
| `system-state/authoritative-files.md` | File authority index |
| ECS tool output (`resolve_next_action.py`) | Live resolver decision |
| ECS tool output (`read_state.py`) | Live state snapshot |
| Artifact filesystem paths | Presence/absence of required files |

Guardian reads these inputs directly. It does not modify them.

---

## Validation Model

```
Guardian reads:
  authoritative state files
  ECS tool outputs (run live)
  filesystem artifact presence

Guardian runs:
  each defined check in sequence

Guardian emits per check:
  PASS or FAIL
  deterministic reason string

Guardian emits overall:
  status = PASS if all checks pass
  status = FAIL if any check fails
  failures = list of failed check names
```

Guardian does not decide what to do next. It only reports what is true or false about the current state.

---

## Guardian Checks (MVP Set)

---

### Check 1: Stale State Check

**Purpose:** Detect when `Immediate Next Steps` still contains work that has already been completed.

**Inputs:**
- `system-state/current-objective.md` → `Immediate Next Steps` section
- Known completed artifact paths (defined per phase)

**Deterministic rule:**
For each item in `Immediate Next Steps`, check whether the item names a deliverable that is already present on the filesystem as a completed artifact. If an item's named artifact exists AND is non-empty, and the item was the previous phase's terminal step, it is stale.

Concretely for the current phase: if `Immediate Next Steps` contains any reference to ECS MVP steps (resolver, gate-check, read-state, exit review) AND those artifacts already exist at their canonical paths, the step is stale.

**Pass condition:** No item in `Immediate Next Steps` refers to a deliverable already confirmed complete by artifact presence.

**Fail condition:** One or more items in `Immediate Next Steps` name deliverables whose artifacts already exist and are non-empty.

**Why it matters:** Stale next steps cause ECS resolver to emit an incorrect decision, breaking the integrity of the entire control pipeline.

---

### Check 2: ECS Consistency Check

**Purpose:** Detect contradictions between the live resolver decision, the live read-state snapshot, and the written state in `current-objective.md`.

**Inputs:**
- Live output of `tools/ecs/resolve_next_action.py`
- Live output of `tools/ecs/read_state.py`
- `system-state/current-objective.md` → `Immediate Next Steps` section

**Deterministic rule:**
1. Run `resolve_next_action.py`. Extract `decision`.
2. Run `read_state.py`. Extract `immediate_next_steps[0]`.
3. Read `current-objective.md`. Extract first item from `Immediate Next Steps`.
4. Compare all three strings (case-insensitive, stripped).
5. If all three match → PASS. If any differ → FAIL.

**Pass condition:** `resolver.decision` == `read_state.immediate_next_steps[0]` == first item in `current-objective.md` Immediate Next Steps (case-insensitive, stripped).

**Fail condition:** Any of the three values differ from the others.

**Why it matters:** If ECS tools and written state disagree on the next step, the control system is incoherent. No further action should be taken until the contradiction is resolved.

---

### Check 3: Forbidden Transition Check

**Purpose:** Detect when `Immediate Next Steps` or active work contains a step that is explicitly blocked by `Current Constraints` or `Not Doing Yet`.

**Inputs:**
- `system-state/current-objective.md` → `Immediate Next Steps`
- `system-state/current-objective.md` → `Current Constraints`
- `system-state/current-objective.md` → `Not Doing Yet`

**Deterministic rule:**
For each item in `Immediate Next Steps`, check whether any item from `Current Constraints` or `Not Doing Yet` is a case-insensitive substring of the step text. If any match is found, the transition is forbidden.

This uses the same substring matching rule as `check_action_allowed.py`.

**Pass condition:** No item in `Immediate Next Steps` contains a substring that appears in `Current Constraints` or `Not Doing Yet`.

**Fail condition:** One or more items in `Immediate Next Steps` contain text that is explicitly blocked by written constraints.

**Why it matters:** A forbidden item appearing in `Immediate Next Steps` means the state file is internally contradictory. ECS gate-check would block execution, but the state surface itself is invalid.

---

### Check 4: Missing Control Artifact Check

**Purpose:** Detect when authoritative state claims a component is complete but its required artifacts are absent or empty on the filesystem.

**Inputs:**
- `system-state/current-system-state.md` → `Current Phase` section
- Canonical artifact paths for each claimed-complete component

**Deterministic rule:**
Parse `Current Phase` for completion claims. For each claim, check the canonical artifact path(s). If any claimed-complete component is missing its required artifact(s) or any required file is empty (0 bytes), the check fails.

**Canonical artifact map (MVP):**

| Claimed complete | Required artifacts |
|---|---|
| System State Surface complete | `system-state/current-system-state.md`, `system-state/authoritative-files.md`, `system-state/current-objective.md` — all non-empty |
| ECS MVP complete | `docs/ecs-mvp-spec.md`, `tools/ecs/resolve_next_action.py`, `docs/ecs-gate-check-spec.md`, `tools/ecs/check_action_allowed.py`, `docs/ecs-read-state-spec.md`, `tools/ecs/read_state.py`, `docs/ecs-mvp-exit-review.md` — all non-empty |
| ECS exit review referenced | `docs/ecs-mvp-exit-review.md` — non-empty, contains "ECS MVP COMPLETE" |

**Pass condition:** Every artifact named by a completion claim exists at its canonical path and is non-empty. Exit review doc contains the expected verdict string.

**Fail condition:** Any required artifact is absent, empty, or (for exit review) does not contain the expected verdict string.

**Why it matters:** If state claims completion but artifacts are missing, the system has diverged from reality. Any further work built on that claim is on a false foundation.

---

## Failure / Alert Conditions

| Condition | Check | Severity |
|---|---|---|
| Stale step in Immediate Next Steps | Stale State Check | FAIL |
| ECS resolver, read-state, and written state disagree | ECS Consistency Check | FAIL |
| Immediate Next Steps contains a forbidden transition | Forbidden Transition Check | FAIL |
| Claimed-complete artifact is missing or empty | Missing Control Artifact Check | FAIL |

All failures are treated as equal severity in MVP. Any single FAIL causes overall `status = FAIL`.

---

## Output Contract

System Guardian emits a single JSON object to stdout on successful completion of all checks (even if some checks fail). Parse errors and missing required files cause a non-zero exit with an error to stderr and no JSON output.

```json
{
  "status": "PASS",
  "checks": [
    {
      "name": "Stale State Check",
      "status": "PASS",
      "reason": "<deterministic reason>"
    },
    {
      "name": "ECS Consistency Check",
      "status": "PASS",
      "reason": "<deterministic reason>"
    },
    {
      "name": "Forbidden Transition Check",
      "status": "PASS",
      "reason": "<deterministic reason>"
    },
    {
      "name": "Missing Control Artifact Check",
      "status": "PASS",
      "reason": "<deterministic reason>"
    }
  ],
  "failures": []
}
```

On partial or full failure:

```json
{
  "status": "FAIL",
  "checks": [
    {
      "name": "Stale State Check",
      "status": "FAIL",
      "reason": "Immediate Next Steps contains 'ECS MVP exit review' but docs/ecs-mvp-exit-review.md already exists and is non-empty."
    }
  ],
  "failures": ["Stale State Check"]
}
```

Field definitions:

| Field | Always present | Value |
|---|---|---|
| `status` | Yes | `"PASS"` if all checks pass; `"FAIL"` if any check fails |
| `checks` | Yes | Ordered list of all check results; each has `name`, `status`, `reason` |
| `failures` | Yes | List of check names that returned `FAIL`; empty list if none |

---

## MVP Boundaries

System Guardian MVP does NOT:

- Suggest corrective actions for failures
- Perform semantic interpretation of state content
- Use fuzzy or probabilistic matching
- Replace or override ECS gate-check
- Run automatically or on a schedule (manual invocation only in MVP)
- Validate product source code (repos)
- Check content correctness of artifacts (only presence and non-emptiness, plus literal string checks where defined)
- Modify any file

---

## Exit Condition

System Guardian MVP is complete when:

1. `docs/system-guardian-mvp-spec.md` is written and defines all four checks explicitly.
2. `tools/guardian/run_guardian.py` is implemented and runs all four checks against live state.
3. `run_guardian.py` produces correct JSON output against current live state.
4. An exit review confirms all three criteria are met.

API spec work (`docs/rewrite-api-spec-v1.md`) begins immediately after.
