# ECS Gate-Check Spec

## Purpose

Given a proposed action string, determine whether that action is allowed to execute based only on authoritative system state. Emits a deterministic JSON verdict. Does not perform semantic interpretation or infer intent.

---

## Version

ECS Gate-Check v1. Deterministic text-matching only.

---

## Authoritative Inputs

| File | Role |
|---|---|
| `system-state/current-system-state.md` | System phase truth |
| `system-state/authoritative-files.md` | Parsed for structural validation; not used in gate logic |
| `system-state/current-objective.md` | Next steps, constraints, blocked actions |

All paths resolved relative to the ai-factory repo root.

---

## Required Sections

Uses the same section recognition rules as `resolve_next_action.py`:

| Section | Required | Source file |
|---|---|---|
| `Current Phase` | Yes | `current-system-state.md` |
| `Current Objective` | Yes | `current-objective.md` |
| `Immediate Next Steps` | Yes | `current-objective.md` |
| `Current Constraints` | Yes | `current-objective.md` |
| `Not Doing Yet` | No (used if present) | `current-objective.md` |
| `Exit Condition` | No (used if present) | `current-objective.md` |

---

## Parser Rules

Identical to `resolve_next_action.py`:

1. Read each file as UTF-8 text.
2. Recognize only `##` and `###` headers followed by a single space. H1 skipped. H4 and deeper ignored.
3. Normalize header text: strip `#` markers, strip whitespace, lowercase.
4. Accumulate lines into the current section until the next recognized header.
5. Strip `---` and blank lines from section bodies before evaluation.
6. Treat content as plain text; do not interpret markdown formatting.

---

## Allow / Block Rules

### allowed = true

A proposed action is allowed if and only if ALL of the following are true:

1. The proposed action string exactly matches at least one item in `Immediate Next Steps` (case-insensitive, stripped).
2. No item in `Current Constraints` is a literal substring of the proposed action (case-insensitive).
3. No item in `Not Doing Yet` is a literal substring of the proposed action (case-insensitive).

### allowed = false

A proposed action is blocked if ANY of the following are true:

- The proposed action does not match any item in `Immediate Next Steps`.
- Any item in `Current Constraints` is a literal substring of the proposed action.
- Any item in `Not Doing Yet` is a literal substring of the proposed action.

---

## Matching Rules

- **Next step matching**: case-insensitive exact string equality between the proposed action and each list item extracted from `Immediate Next Steps`, after stripping whitespace and bold markers from both sides.
- **Blocker matching**: case-insensitive substring — a blocker item blocks the proposed action if the blocker string is found literally within the proposed action string.
- No fuzzy matching. No semantic similarity. No partial intent matching. No inference.

---

## Failure Behavior

| Condition | Behavior |
|---|---|
| Required input file missing or unreadable | Print `ERROR: MISSING_FILE: <path>` to stderr; exit non-zero |
| Required section absent | Print `ERROR: MISSING_SECTION: <section> in <file>` to stderr; exit non-zero |
| Required section appears more than once | Print `ERROR: DUPLICATE_SECTION: <section> in <file>` to stderr; exit non-zero |
| Required section empty after stripping | Print `ERROR: EMPTY_SECTION: <section> in <file>` to stderr; exit non-zero |
| `--action` flag not provided | Print usage error to stderr; exit non-zero |

The tool never produces JSON output on failure. All failures go to stderr only.

---

## JSON Output Contract

On success, a single JSON object is printed to stdout:

```json
{
  "proposed_action": "<input string, as provided>",
  "allowed": true,
  "reason": "<deterministic reason string>",
  "matched_next_step": "<exact matching item from Immediate Next Steps, or null>",
  "blocked_by": []
}
```

```json
{
  "proposed_action": "<input string, as provided>",
  "allowed": false,
  "reason": "<deterministic reason string>",
  "matched_next_step": null,
  "blocked_by": ["<blocking item>"]
}
```

Field definitions:

| Field | Always present | Value |
|---|---|---|
| `proposed_action` | Yes | The input string exactly as provided |
| `allowed` | Yes | `true` or `false` |
| `reason` | Yes | Deterministic explanation citing which rule applied |
| `matched_next_step` | Yes | Exact text of the matching step, or `null` if none |
| `blocked_by` | Yes | List of blocking items (empty list if none) |

---

## What This Tool Is NOT Allowed To Do

- Perform semantic interpretation of section content
- Use fuzzy or partial matching to determine intent
- Infer that an action is "close enough" to a next step
- Emit a verdict of `allowed = true` for any action not explicitly listed in `Immediate Next Steps`
- Continue past any failure condition
- Read files other than the three authoritative inputs
- Use external libraries or network access
- Modify any file
- Suggest alternative actions
