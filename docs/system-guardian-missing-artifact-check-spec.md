# System Guardian: Missing Control Artifact Check Spec

## Purpose

Detect when authoritative state claims a control layer or phase is complete but one or more required artifacts for that claim are missing or empty on the filesystem.

If state claims completion without the artifacts to support it, subsequent work is built on a false foundation. This check makes the completion claims in `Current Phase` and `Current Objective` verifiable against the filesystem.

This check is deterministic. It operates from an explicit local mapping table. It does not infer claims from vague wording — a claim must contain a defined trigger substring to be evaluated.

---

## Version

Missing Control Artifact Check v1.

---

## Inputs

| File | Sections extracted |
|---|---|
| `system-state/current-system-state.md` | `Current Phase` |
| `system-state/current-objective.md` | `Current Objective` |
| `system-state/authoritative-files.md` | Parsed for structural validation; no content used in check logic |

All artifact paths are checked relative to the ai-factory repo root.

---

## Parser Rules

Identical to the established ECS and Guardian parser contract:

1. Read file as UTF-8 text.
2. Recognize only `##` and `###` headers followed by a single space. H1 skipped. H4 and deeper ignored.
3. Normalize header text: strip `#` markers, strip whitespace, lowercase.
4. Accumulate lines into section until the next recognized header.
5. Strip `---` and blank lines from section bodies.
6. Join all stripped body lines with `" | "` for prose sections (same rule as `read_state.py`).

---

## Claim-to-Artifact Mapping Model

The check operates from an explicit mapping table. Each entry defines:

- **Trigger substring**: a case-insensitive substring that, if found in the combined `Current Phase` + `Current Objective` text, activates the check.
- **Required artifacts**: repo-relative paths that must exist and be non-empty.

A claim is **applicable** if its trigger substring is found in the combined text. A claim is **not applicable** if the trigger is not found — it is skipped entirely and reported as `NOT_APPLICABLE`.

**Mapping table (v1):**

| Claim name | Trigger substring | Required artifacts |
|---|---|---|
| `system_state_surface_complete` | `system state surface complete` | `system-state/current-system-state.md`, `system-state/current-objective.md`, `system-state/authoritative-files.md` |
| `ecs_mvp_complete` | `ecs mvp complete` | `docs/ecs-mvp-spec.md`, `tools/ecs/resolve_next_action.py`, `docs/ecs-gate-check-spec.md`, `tools/ecs/check_action_allowed.py`, `docs/ecs-read-state-spec.md`, `tools/ecs/read_state.py`, `docs/ecs-mvp-exit-review.md` |

All entries in the mapping table are always evaluated. Only entries whose trigger is absent from state text are `NOT_APPLICABLE`.

---

## Applicability Rules

For each mapping entry:

1. Combine the full stripped `Current Phase` section (joined with `" | "`) and the full stripped `Current Objective` section (joined with `" | "`) into a single lowercase string.
2. Check whether the trigger substring (lowercased) appears in that combined string.
3. If present → applicable → verify artifacts.
4. If absent → not applicable → report as `NOT_APPLICABLE`, do not check artifacts.

---

## Classification Rules

For each applicable claim:

| Classification | Condition |
|---|---|
| `PASS` | All required artifacts exist and are non-empty (size > 0 bytes) |
| `FAIL` | One or more required artifacts are missing or empty |

For non-applicable claims:

| Classification | Condition |
|---|---|
| `NOT_APPLICABLE` | Trigger substring not found in combined state text |

---

## Pass / Fail Rules

| Verdict | Condition |
|---|---|
| `PASS` | No applicable claim has a missing or empty artifact |
| `FAIL` | One or more applicable claims have at least one missing or empty artifact |

`NOT_APPLICABLE` claims do not affect the verdict.

---

## Failure Behavior (Parse / Input Errors)

These conditions cause a non-zero exit with an error to stderr. No JSON is emitted.

| Condition | Error |
|---|---|
| Any required input file missing or unreadable | `ERROR: MISSING_FILE: <path>` |
| `Current Phase` section absent in `current-system-state.md` | `ERROR: MISSING_SECTION: Current Phase in current-system-state.md` |
| `Current Phase` section duplicated | `ERROR: DUPLICATE_SECTION: Current Phase in current-system-state.md` |
| `Current Phase` section empty after stripping | `ERROR: EMPTY_SECTION: Current Phase in current-system-state.md` |
| `Current Objective` section absent in `current-objective.md` | `ERROR: MISSING_SECTION: Current Objective in current-objective.md` |
| `Current Objective` section duplicated | `ERROR: DUPLICATE_SECTION: Current Objective in current-objective.md` |
| `Current Objective` section empty after stripping | `ERROR: EMPTY_SECTION: Current Objective in current-objective.md` |

---

## JSON Output Contract

A single JSON object printed to stdout on successful completion. One entry in `checks` per mapping table entry, in definition order.

```json
{
  "status": "PASS",
  "check_name": "missing_control_artifact_check",
  "checks": [
    {
      "name": "system_state_surface_complete",
      "status": "PASS",
      "claim_text": "system state surface complete",
      "required_artifacts": [
        "system-state/current-system-state.md",
        "system-state/current-objective.md",
        "system-state/authoritative-files.md"
      ],
      "missing_artifacts": [],
      "empty_artifacts": []
    },
    {
      "name": "ecs_mvp_complete",
      "status": "PASS",
      "claim_text": "ecs mvp complete",
      "required_artifacts": ["..."],
      "missing_artifacts": [],
      "empty_artifacts": []
    }
  ],
  "failures": []
}
```

On partial failure:

```json
{
  "status": "FAIL",
  "check_name": "missing_control_artifact_check",
  "checks": [
    {
      "name": "ecs_mvp_complete",
      "status": "FAIL",
      "claim_text": "ecs mvp complete",
      "required_artifacts": ["docs/ecs-mvp-exit-review.md"],
      "missing_artifacts": ["docs/ecs-mvp-exit-review.md"],
      "empty_artifacts": []
    }
  ],
  "failures": ["ecs_mvp_complete"]
}
```

On not-applicable claim:

```json
{
  "name": "ecs_mvp_complete",
  "status": "NOT_APPLICABLE",
  "claim_text": "ecs mvp complete",
  "required_artifacts": ["..."],
  "missing_artifacts": [],
  "empty_artifacts": []
}
```

Field definitions:

| Field | Always present | Value |
|---|---|---|
| `status` | Yes | `"PASS"` or `"FAIL"` |
| `check_name` | Yes | Always `"missing_control_artifact_check"` |
| `checks` | Yes | One entry per mapping table entry, in definition order |
| `checks[].name` | Yes | Mapping entry identifier |
| `checks[].status` | Yes | `"PASS"`, `"FAIL"`, or `"NOT_APPLICABLE"` |
| `checks[].claim_text` | Yes | The trigger substring for this entry |
| `checks[].required_artifacts` | Yes | All artifact paths defined for this entry |
| `checks[].missing_artifacts` | Yes | Paths that do not exist; empty list if none |
| `checks[].empty_artifacts` | Yes | Paths that exist but are 0 bytes; empty list if none |
| `failures` | Yes | List of claim names that returned `FAIL`; empty list if none |

---

## Limitations

- Trigger matching is case-insensitive substring only. A completion claim phrased differently from the trigger will be `NOT_APPLICABLE` even if semantically equivalent.
- Artifact existence and non-emptiness are the only verifications. Content correctness is not checked.
- The mapping table covers only the control layers completed as of v1 (System State Surface, ECS MVP). Future layers (System Guardian) must be added to the table explicitly when their completion is claimed in state text.
- If state text makes a false completion claim (i.e., the trigger is present but the completion was never real), and the artifacts happen to exist from a prior incomplete attempt, this check will PASS. It cannot detect fraudulent completion claims.

---

## What This Check Is NOT Allowed To Do

- Infer completion claims from vague state wording
- Match triggers using fuzzy or semantic comparison
- Check artifact content beyond existence and byte size
- Add itself to the mapping table automatically
- Suggest corrective actions
- Modify any file
- Use external libraries or subprocess calls
- Continue past parse / input failure conditions
