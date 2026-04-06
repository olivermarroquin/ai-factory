# System Guardian: Stale State Check Spec

## Purpose

Detect when `Immediate Next Steps` in `current-objective.md` lists work that is already complete, based only on whether required artifacts for that step exist as non-empty files. A stale step in the objective causes the ECS resolver to emit an incorrect decision, corrupting the control pipeline.

This check is deterministic. It does not interpret phrasing, infer completion, or guess artifact locations.

---

## Version

Stale State Check v1.

---

## Inputs

| Input | Role |
|---|---|
| `system-state/current-objective.md` | Source of `Immediate Next Steps` list |
| Filesystem (artifact paths) | Checked for existence and non-emptiness |

`system-state/authoritative-files.md` is parsed for structural validation only; its content is not used in check logic.

All artifact paths are resolved relative to the ai-factory repo root.

---

## Parser Rules

Identical to the established ECS parser contract:

1. Read file as UTF-8 text.
2. Recognize only `##` and `###` headers followed by a single space. H1 skipped. H4 and deeper ignored.
3. Normalize header text: strip `#` markers, strip whitespace, lowercase.
4. Accumulate lines into section until the next recognized header.
5. Strip `---` and blank lines from section bodies.
6. Extract ordered list items (lines beginning with `N. `, `- `, or `* `). Strip bold markers (`**`).

---

## Deterministic Mapping Model

The check operates from an explicit mapping table defined in the implementation. Each entry maps an exact step text to one or more required artifact paths.

A step is evaluated only if its text exactly matches a mapped key (case-insensitive, stripped). If no match exists, the step is `UNMAPPED` — it is not stale, not current, just not covered by v1.

**Mapping table (v1):**

| Step text (normalized) | Required artifacts |
|---|---|
| `complete system state surface (this conversation) — write \`current-system-state.md\`, \`authoritative-files.md\`, \`current-objective.md\`.` | `system-state/current-system-state.md`, `system-state/authoritative-files.md`, `system-state/current-objective.md` |
| `validate resolver output against updated state — run \`tools/ecs/resolve_next_action.py\` and confirm the decision reflects the correct current next step.` | `tools/ecs/resolve_next_action.py` |
| `define ecs gate-check — specify and implement the rule that determines whether a proposed action is allowed to execute given the current state. this is the core gate mechanism of ecs mvp.` | `docs/ecs-gate-check-spec.md`, `tools/ecs/check_action_allowed.py` |
| `define ecs read-state interface — specify and implement how the ecs surfaces current system state to an operator or agent in a structured, queryable form.` | `docs/ecs-read-state-spec.md`, `tools/ecs/read_state.py` |
| `ecs mvp exit review — confirm all exit condition criteria are met before proceeding to system guardian.` | `docs/ecs-mvp-exit-review.md` |
| `system guardian mvp — define scope, specify invariant checks, drift detection, and health reporting for the controlled pipeline.` | `docs/system-guardian-mvp-spec.md` |

---

## Classification Rules

Each step in `Immediate Next Steps` is classified exactly once:

| Classification | Condition |
|---|---|
| `STALE` | Step text matches a mapping AND all required artifacts exist AND all are non-empty (size > 0 bytes) |
| `CURRENT` | Step text matches a mapping AND at least one required artifact is missing OR empty |
| `UNMAPPED` | Step text does not match any entry in the mapping table |

No other classifications exist.

---

## Pass / Fail Rules

| Verdict | Condition |
|---|---|
| `PASS` | No step is classified `STALE` |
| `FAIL` | One or more steps are classified `STALE` |

`UNMAPPED` steps do not affect the verdict. They are reported in the output for transparency.

---

## JSON Output Contract

A single JSON object printed to stdout on success:

```json
{
  "status": "PASS",
  "check_name": "stale_state_check",
  "results": [
    {
      "step": "<exact Immediate Next Steps item text>",
      "classification": "CURRENT",
      "required_artifacts": ["<path>"],
      "missing_artifacts": [],
      "empty_artifacts": []
    }
  ],
  "failures": []
}
```

On failure:

```json
{
  "status": "FAIL",
  "check_name": "stale_state_check",
  "results": [
    {
      "step": "<step text>",
      "classification": "STALE",
      "required_artifacts": ["<path1>", "<path2>"],
      "missing_artifacts": [],
      "empty_artifacts": []
    }
  ],
  "failures": ["<step text>"]
}
```

Field definitions:

| Field | Always present | Value |
|---|---|---|
| `status` | Yes | `"PASS"` or `"FAIL"` |
| `check_name` | Yes | Always `"stale_state_check"` |
| `results` | Yes | One entry per step in `Immediate Next Steps`, in original order |
| `results[].step` | Yes | Exact text extracted from the step list |
| `results[].classification` | Yes | `"CURRENT"`, `"STALE"`, or `"UNMAPPED"` |
| `results[].required_artifacts` | Yes | List of artifact paths for this step; empty list if `UNMAPPED` |
| `results[].missing_artifacts` | Yes | Paths that do not exist; empty list if none |
| `results[].empty_artifacts` | Yes | Paths that exist but are 0 bytes; empty list if none |
| `failures` | Yes | List of step texts classified `STALE`; empty list if none |

---

## Failure Behavior (Parse / Input Errors)

These conditions cause a non-zero exit and an error message to stderr. No JSON is emitted.

| Condition | Error |
|---|---|
| `current-objective.md` missing or unreadable | `ERROR: MISSING_FILE: <path>` |
| `Immediate Next Steps` section absent | `ERROR: MISSING_SECTION: Immediate Next Steps in current-objective.md` |
| `Immediate Next Steps` section duplicated | `ERROR: DUPLICATE_SECTION: Immediate Next Steps in current-objective.md` |
| `Immediate Next Steps` section empty after stripping | `ERROR: EMPTY_SECTION: Immediate Next Steps in current-objective.md` |
| `Immediate Next Steps` contains no list items | `ERROR: EMPTY_SECTION: Immediate Next Steps contained no list items` |

---

## Limitations

- v1 mapping table covers only ECS MVP and System State Surface steps. Steps from future phases are `UNMAPPED` and do not fail the check.
- A step is stale only if it exactly matches a mapping key (case-insensitive). Rephrased steps are `UNMAPPED`, not stale — the mapping must be updated when step text changes.
- The check verifies artifact existence and non-emptiness only. It does not verify artifact correctness, content validity, or whether artifacts were produced by the correct process.
- `UNMAPPED` steps are not validated. If a step is genuinely complete but not in the mapping, this check will not catch it.

---

## What This Check Is NOT Allowed To Do

- Infer completion from step wording or phrasing
- Fuzzy-match step text against mapping keys
- Read artifact contents (only existence and size are checked)
- Suggest corrective actions
- Modify any file
- Use external libraries
- Continue past parse/input failure conditions
