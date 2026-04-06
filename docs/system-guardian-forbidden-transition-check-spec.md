# System Guardian: Forbidden Transition Check Spec

## Purpose

Detect when `Immediate Next Steps` contains items that are explicitly forbidden by `Current Constraints` or `Not Doing Yet`. A step is forbidden if any blocker text is a literal case-insensitive substring of the step text.

This check makes the state file internally self-consistent: if a step is in `Immediate Next Steps` but also covered by a constraint or not-doing-yet entry, the state is contradictory and must be corrected before any further action.

This check is deterministic. It uses only explicit substring matching against written state. No semantic reasoning, no inference, no fuzzy matching.

---

## Version

Forbidden Transition Check v1.

---

## Inputs

| File | Sections extracted |
|---|---|
| `system-state/current-objective.md` | `Immediate Next Steps`, `Current Constraints`, `Not Doing Yet` |
| `system-state/current-system-state.md` | Parsed for structural validation; no content used in check logic |
| `system-state/authoritative-files.md` | Parsed for structural validation; no content used in check logic |

All paths resolved relative to the ai-factory repo root.

---

## Parser Rules

Identical to the established ECS and Guardian parser contract:

1. Read file as UTF-8 text.
2. Recognize only `##` and `###` headers followed by a single space. H1 skipped. H4 and deeper ignored.
3. Normalize header text: strip `#` markers, strip whitespace, lowercase.
4. Accumulate lines into section until the next recognized header.
5. Strip `---` and blank lines from section bodies.
6. Extract ordered/unordered list items (lines beginning with `N. `, `- `, `* `). Strip bold markers (`**`).

---

## Forbidden Transition Rules

A step in `Immediate Next Steps` is **forbidden** if:

- Any item from `Current Constraints` is a case-insensitive substring of the step text, **OR**
- Any item from `Not Doing Yet` is a case-insensitive substring of the step text.

If a step is not forbidden by either source, it is **allowed**.

### Matching rule

Exact case-insensitive substring: `blocker.lower() in step.lower()`.

No fuzzy matching. No semantic comparison. No partial word matching beyond what the literal substring test produces.

### Known forbidden transitions in current phase (illustrative, not exhaustive)

These are examples of what the current constraints and not-doing-yet entries would catch if present in Immediate Next Steps:

| Forbidden transition | Blocked by |
|---|---|
| Any step referencing API spec work | `Current Constraints`: "API spec work must not be started until System Guardian MVP is complete" |
| Any step referencing `backend/api/rewrite.py`, `resume.py`, `jobs.py` | `Current Constraints` and `Not Doing Yet` |
| Any step adding `app_build`, `automation_build`, or `ui_conversion` | `Current Constraints` and `Not Doing Yet` |
| Any step targeting Class B consolidation work | `Current Constraints` |
| Any new `code_migration` execution step | `Not Doing Yet` |

These entries are not hard-coded in the check. They are detected automatically by reading the live `Current Constraints` and `Not Doing Yet` sections from authoritative state files.

---

## Check Structure

One check entry is emitted per `Immediate Next Steps` item. Each entry records:
- The step text
- Whether it is `ALLOWED` or `FORBIDDEN`
- Which blocker(s) triggered the verdict (if forbidden)
- The deterministic reason string

---

## Pass / Fail Rules

| Verdict | Condition |
|---|---|
| `PASS` | No step in `Immediate Next Steps` is forbidden by any constraint or not-doing-yet item |
| `FAIL` | One or more steps are forbidden |

---

## Failure Behavior (Parse / Input Errors)

These conditions cause a non-zero exit with an error to stderr. No JSON is emitted.

| Condition | Error |
|---|---|
| Any required input file missing or unreadable | `ERROR: MISSING_FILE: <path>` |
| `Immediate Next Steps` section absent | `ERROR: MISSING_SECTION: Immediate Next Steps in current-objective.md` |
| `Immediate Next Steps` section duplicated | `ERROR: DUPLICATE_SECTION: Immediate Next Steps in current-objective.md` |
| `Immediate Next Steps` section empty after stripping | `ERROR: EMPTY_SECTION: Immediate Next Steps in current-objective.md` |
| `Immediate Next Steps` contains no list items | `ERROR: EMPTY_SECTION: Immediate Next Steps contained no list items` |
| `Current Constraints` section absent | `ERROR: MISSING_SECTION: Current Constraints in current-objective.md` |
| `Current Constraints` section duplicated | `ERROR: DUPLICATE_SECTION: Current Constraints in current-objective.md` |
| `Current Constraints` section empty after stripping | `ERROR: EMPTY_SECTION: Current Constraints in current-objective.md` |

`Not Doing Yet` is optional. If absent, it contributes no blockers. If present and duplicated, that is a parse error.

---

## JSON Output Contract

A single JSON object printed to stdout on successful completion. One entry in `checks` per `Immediate Next Steps` item, in original order.

```json
{
  "status": "PASS",
  "check_name": "forbidden_transition_check",
  "checks": [
    {
      "name": "step_1_forbidden_check",
      "status": "PASS",
      "subject": "<step text>",
      "reason": "No constraint or not-doing-yet item is a substring of this step."
    }
  ],
  "failures": []
}
```

On failure:

```json
{
  "status": "FAIL",
  "check_name": "forbidden_transition_check",
  "checks": [
    {
      "name": "step_1_forbidden_check",
      "status": "FAIL",
      "subject": "<step text>",
      "reason": "Blocked by Current Constraints: \"<blocker text>\""
    }
  ],
  "failures": ["step_1_forbidden_check"]
}
```

Field definitions:

| Field | Always present | Value |
|---|---|---|
| `status` | Yes | `"PASS"` or `"FAIL"` |
| `check_name` | Yes | Always `"forbidden_transition_check"` |
| `checks` | Yes | One entry per step in `Immediate Next Steps`, in original order |
| `checks[].name` | Yes | `"step_N_forbidden_check"` where N is 1-based position |
| `checks[].status` | Yes | `"PASS"` or `"FAIL"` |
| `checks[].subject` | Yes | Exact step text as extracted from `Immediate Next Steps` |
| `checks[].reason` | Yes | Deterministic explanation citing the blocking rule and blocker text if applicable |
| `failures` | Yes | List of check names that returned `FAIL`; empty list if none |

---

## Limitations

- Blocking is detected by substring only. A constraint phrased differently from the step text will not be detected. Operators must write constraint text that textually overlaps with forbidden step text if blocking is required.
- A step containing multiple blockers will report only the first blocker found (from `Current Constraints` first, then `Not Doing Yet`).
- Non-list content in `Current Constraints` and `Not Doing Yet` sections is ignored; only list items are used as blockers.
- `Not Doing Yet` absence is not a failure; it simply means no not-doing-yet blockers are active.

---

## What This Check Is NOT Allowed To Do

- Infer that a step is "related to" a blocked area without a literal substring match
- Perform semantic comparison of step and blocker text
- Suggest alternative steps
- Modify any file
- Use external libraries or subprocess calls
- Continue past parse / input failure conditions
