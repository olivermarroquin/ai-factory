# System Guardian: ECS Consistency Check Spec

## Purpose

Detect contradictions between the ECS tool surfaces and the authoritative state files. Specifically, verify that `resolve_next_action.py`, `read_state.py`, and `current-objective.md` all agree on the current next step and current objective text.

If any of the three surfaces disagrees, the control system is incoherent and no further action should be taken until the contradiction is resolved.

This check is deterministic. It compares exact string values only. No semantic matching, no fuzzy comparison, no "close enough."

---

## Version

ECS Consistency Check v1.

---

## Inputs

**Files parsed directly:**

| File | What is extracted |
|---|---|
| `system-state/current-objective.md` | First item from `Immediate Next Steps`; full stripped `Current Objective` section |

**Tool outputs (via subprocess):**

| Tool | What is extracted |
|---|---|
| `tools/ecs/resolve_next_action.py` | `decision` field from JSON stdout |
| `tools/ecs/read_state.py` | `immediate_next_steps[0]` and `current_objective` fields from JSON stdout |

`system-state/current-system-state.md` and `system-state/authoritative-files.md` are read by the ECS tools internally; this check does not parse them directly.

---

## Parser Rules

Identical to the established ECS and Guardian parser contract:

1. Read file as UTF-8 text.
2. Recognize only `##` and `###` headers followed by a single space. H1 skipped. H4 and deeper ignored.
3. Normalize header text: strip `#` markers, strip whitespace, lowercase.
4. Accumulate lines into section until the next recognized header.
5. Strip `---` and blank lines from section bodies.
6. Extract ordered list items (lines beginning with `N. `, `- `, `* `). Strip bold markers (`**`).
7. For prose sections (`Current Objective`): join all stripped non-empty lines with `" | "` — identical to the rule used by `read_state.py`.

---

## Exact Comparisons (v1)

Three comparisons are run in sequence. Each is independent; all are always evaluated.

### Comparison 1: `resolver_decision_vs_read_state_step_0`

| | Value |
|---|---|
| Expected | `resolve_next_action.py` JSON → `decision` field |
| Actual | `read_state.py` JSON → `immediate_next_steps[0]` |
| Rule | Exact case-sensitive string equality |
| Pass | Both strings are identical |
| Fail | Strings differ in any way |

### Comparison 2: `read_state_step_0_vs_parsed_objective`

| | Value |
|---|---|
| Expected | First list item extracted directly from `current-objective.md` `Immediate Next Steps` section |
| Actual | `read_state.py` JSON → `immediate_next_steps[0]` |
| Rule | Exact case-sensitive string equality |
| Pass | Both strings are identical |
| Fail | Strings differ in any way |

### Comparison 3: `read_state_objective_vs_parsed_objective`

| | Value |
|---|---|
| Expected | Full stripped `Current Objective` section from `current-objective.md`, lines joined with `" \| "` |
| Actual | `read_state.py` JSON → `current_objective` field |
| Rule | Exact case-sensitive string equality |
| Pass | Both strings are identical |
| Fail | Strings differ in any way |

---

## Pass / Fail Rules

| Verdict | Condition |
|---|---|
| `PASS` | All three comparisons pass |
| `FAIL` | One or more comparisons fail |

---

## Failure Behavior (Parse / Subprocess Errors)

These conditions cause a non-zero exit with an error to stderr. No JSON is emitted.

| Condition | Error |
|---|---|
| `current-objective.md` missing or unreadable | `ERROR: MISSING_FILE: <path>` |
| `Immediate Next Steps` section absent | `ERROR: MISSING_SECTION: Immediate Next Steps in current-objective.md` |
| `Immediate Next Steps` section duplicated | `ERROR: DUPLICATE_SECTION: Immediate Next Steps in current-objective.md` |
| `Immediate Next Steps` section empty or no list items | `ERROR: EMPTY_SECTION: Immediate Next Steps in current-objective.md` |
| `Current Objective` section absent | `ERROR: MISSING_SECTION: Current Objective in current-objective.md` |
| `Current Objective` section duplicated | `ERROR: DUPLICATE_SECTION: Current Objective in current-objective.md` |
| `Current Objective` section empty after stripping | `ERROR: EMPTY_SECTION: Current Objective in current-objective.md` |
| ECS tool subprocess exits non-zero | `ERROR: ECS_TOOL_FAILED: <tool path> exited <code>: <stderr>` |
| ECS tool JSON output is malformed | `ERROR: ECS_TOOL_INVALID_JSON: <tool path>` |
| ECS tool JSON missing a required field | `ERROR: ECS_TOOL_MISSING_FIELD: <field> in <tool path> output` |
| `immediate_next_steps` is empty list in read_state output | `ERROR: ECS_TOOL_MISSING_FIELD: immediate_next_steps[0] in read_state.py output` |

---

## JSON Output Contract

A single JSON object printed to stdout on successful completion of all comparisons (regardless of whether comparisons pass or fail):

```json
{
  "status": "PASS",
  "check_name": "ecs_consistency_check",
  "checks": [
    {
      "name": "resolver_decision_vs_read_state_step_0",
      "status": "PASS",
      "expected": "<resolve_next_action decision>",
      "actual": "<read_state immediate_next_steps[0]>"
    },
    {
      "name": "read_state_step_0_vs_parsed_objective",
      "status": "PASS",
      "expected": "<parsed first step from current-objective.md>",
      "actual": "<read_state immediate_next_steps[0]>"
    },
    {
      "name": "read_state_objective_vs_parsed_objective",
      "status": "PASS",
      "expected": "<parsed current objective from current-objective.md>",
      "actual": "<read_state current_objective>"
    }
  ],
  "failures": []
}
```

On failure:

```json
{
  "status": "FAIL",
  "check_name": "ecs_consistency_check",
  "checks": [
    {
      "name": "resolver_decision_vs_read_state_step_0",
      "status": "FAIL",
      "expected": "<value from resolver>",
      "actual": "<value from read_state>"
    }
  ],
  "failures": ["resolver_decision_vs_read_state_step_0"]
}
```

Field definitions:

| Field | Always present | Value |
|---|---|---|
| `status` | Yes | `"PASS"` or `"FAIL"` |
| `check_name` | Yes | Always `"ecs_consistency_check"` |
| `checks` | Yes | One entry per comparison, in definition order |
| `checks[].name` | Yes | Comparison identifier |
| `checks[].status` | Yes | `"PASS"` or `"FAIL"` |
| `checks[].expected` | Yes | The reference value for this comparison |
| `checks[].actual` | Yes | The value being compared against expected |
| `failures` | Yes | List of comparison names that returned `FAIL`; empty list if none |

---

## Limitations

- Comparisons are exact string equality only. A one-character difference (whitespace, unicode, encoding) causes a FAIL regardless of whether the values are semantically equivalent.
- The check does not validate that the ECS tool outputs are internally correct — it only validates that the three surfaces agree with each other.
- If both ECS tools and the state file are consistently wrong (all three disagree with reality but agree with each other), this check will PASS. The Stale State Check addresses that scenario.
- Only `immediate_next_steps[0]` is compared. Remaining steps are not checked for cross-surface agreement in v1.

---

## What This Check Is NOT Allowed To Do

- Perform semantic comparison of string values
- Treat similar strings as equivalent
- Infer that a difference is "minor" or "acceptable"
- Modify any file
- Use external libraries
- Continue past subprocess or parse failure conditions
- Suggest corrective actions
