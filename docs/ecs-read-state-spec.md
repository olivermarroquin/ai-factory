# ECS Read-State Spec

## Purpose

Read authoritative system state and emit a structured JSON snapshot for operator or script consumption. Does not resolve actions, apply gate logic, or interpret content. Surfaces exactly what the authoritative files contain.

---

## Version

ECS Read-State v1. Deterministic parser + structured output only.

---

## Authoritative Inputs

| File | Role |
|---|---|
| `system-state/current-system-state.md` | System phase truth |
| `system-state/authoritative-files.md` | Parsed for structural validation; content not surfaced |
| `system-state/current-objective.md` | Objective, next steps, constraints, blocked actions, exit condition |

All paths resolved relative to the ai-factory repo root.

---

## Parser Rules

Identical to `resolve_next_action.py` and `check_action_allowed.py`:

1. Read each file as UTF-8 text.
2. Recognize only `##` and `###` headers followed by a single space. H1 skipped as document title. H4 and deeper ignored. `#` sequences not immediately followed by a space are not headers.
3. Normalize header text: strip `#` markers, strip whitespace, lowercase.
4. Accumulate lines into the current section until the next recognized header.
5. Strip `---` and blank lines from section bodies before evaluation.
6. Treat content as plain text; do not interpret markdown formatting.

---

## Required Sections

| Section | Required | Source file |
|---|---|---|
| `Current Phase` | Yes | `current-system-state.md` |
| `Current Objective` | Yes | `current-objective.md` |
| `Immediate Next Steps` | Yes | `current-objective.md` |
| `Current Constraints` | Yes | `current-objective.md` |
| `Not Doing Yet` | No (empty list if absent) | `current-objective.md` |
| `Exit Condition` | No (`NOT_EXPLICIT_IN_STATE` if absent) | `current-objective.md` |

---

## Surfaced Sections

All recognized sections are surfaced in the output. No sections are omitted, summarized, or interpreted.

---

## JSON Output Contract

A single JSON object printed to stdout on success:

```json
{
  "current_phase": "<full stripped Current Phase section, joined with ' | ' if multi-line>",
  "current_objective": "<full stripped Current Objective section, joined with ' | ' if multi-line>",
  "immediate_next_steps": ["<ordered list items from Immediate Next Steps>"],
  "current_constraints": ["<list items from Current Constraints>"],
  "not_doing_yet": ["<list items from Not Doing Yet, or empty list if section absent>"],
  "exit_condition": "<full stripped Exit Condition section, joined with ' | ', or NOT_EXPLICIT_IN_STATE>",
  "authoritative_inputs": [
    "system-state/current-system-state.md",
    "system-state/authoritative-files.md",
    "system-state/current-objective.md"
  ]
}
```

Field rules:

| Field | Rule |
|---|---|
| `current_phase` | Full stripped content of `Current Phase`. Multi-line joined with `" \| "`. |
| `current_objective` | Full stripped content of `Current Objective`. Multi-line joined with `" \| "`. |
| `immediate_next_steps` | Ordered list items extracted from `Immediate Next Steps`. Original order preserved. |
| `current_constraints` | List items extracted from `Current Constraints`. |
| `not_doing_yet` | List items extracted from `Not Doing Yet`. Empty list `[]` if section absent. |
| `exit_condition` | Full stripped content of `Exit Condition`. Multi-line joined with `" \| "`. `NOT_EXPLICIT_IN_STATE` if absent or empty. |
| `authoritative_inputs` | Fixed list of the three input file paths (repo-relative). Always present. |

---

## Failure Behavior

| Condition | Behavior |
|---|---|
| Required input file missing or unreadable | Print `ERROR: MISSING_FILE: <path>` to stderr; exit non-zero |
| Required section absent | Print `ERROR: MISSING_SECTION: <section> in <file>` to stderr; exit non-zero |
| Required section appears more than once | Print `ERROR: DUPLICATE_SECTION: <section> in <file>` to stderr; exit non-zero |
| Required section empty after stripping | Print `ERROR: EMPTY_SECTION: <section> in <file>` to stderr; exit non-zero |

The tool never produces JSON output on failure. All failure output goes to stderr only.

---

## What This Tool Is NOT Allowed To Do

- Interpret or summarize section content
- Infer meaning from phrasing
- Omit or transform any list item
- Add fields not defined in the output contract
- Resolve next actions or apply gate logic
- Continue past any failure condition
- Read files other than the three authoritative inputs
- Use external libraries or network access
- Modify any file
