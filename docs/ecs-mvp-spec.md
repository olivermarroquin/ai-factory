# ECS MVP Spec

## Purpose

The Execution Control System MVP (ECS MVP) is a deterministic parser and rule-based resolver that reads authoritative system-state markdown files and emits the single next allowed action. It does not perform semantic interpretation, make inferences beyond explicit written state, or invent decisions.

---

## Version

ECS MVP v1. This version is a deterministic parser + rule-based resolver only.

---

## Authoritative Inputs

The ECS MVP reads exactly these three files, in this order:

| File | Role |
|---|---|
| `system-state/current-system-state.md` | System phase and architecture truth |
| `system-state/authoritative-files.md` | File authority index (parsed but not used for resolution) |
| `system-state/current-objective.md` | Objective, constraints, next steps, blocked actions |

All paths are resolved relative to the ai-factory repo root.

---

## Required Section Headers

The parser recognizes these section headers by exact normalized name (case-insensitive, stripped of leading `#` markers and surrounding whitespace):

| Section | Required for resolution | File expected in |
|---|---|---|
| `Current Phase` | Yes | `current-system-state.md` |
| `Current Objective` | Yes | `current-objective.md` |
| `Immediate Next Steps` | Yes | `current-objective.md` |
| `Current Constraints` | Yes | `current-objective.md` |
| `Not Doing Yet` | No (used if present) | `current-objective.md` |
| `Exit Condition` | No (used if present) | `current-objective.md` |

Any other section headers encountered during parsing are ignored.

---

## Parser Behavior

1. Read each file as UTF-8 text.
2. Split into sections by detecting lines that begin with exactly `##` or `###` followed by a single space. H1 lines (single `#`) are treated as document titles and are skipped. H4 and deeper (`####` or more) are ignored. Lines where `#` sequences are not immediately followed by a space are not recognized as headers.
3. Normalize header text: strip leading `#` characters, strip surrounding whitespace, lowercase.
4. Assign all lines following a header to that section, until the next recognized header line is encountered.
5. Strip horizontal rules (`---`) and blank lines from section bodies before evaluation.
6. Do not interpret markdown formatting (bold, italic, links). Treat content as plain text.

---

## Failure Behavior

The parser must fail, print a clear error to stderr, and exit non-zero in any of the following conditions:

| Condition | Error |
|---|---|
| A required input file is missing or unreadable | `MISSING_FILE: <path>` |
| A required section is absent from its expected file | `MISSING_SECTION: <section name> in <file>` |
| A required section appears more than once in a file | `DUPLICATE_SECTION: <section name> in <file>` |
| A required section is present but empty after stripping | `EMPTY_SECTION: <section name> in <file>` |
| Zero valid next actions remain after constraint filtering | `NO_VALID_ACTION: all actions excluded by constraints or not-doing-yet` |
| Multiple actions remain and no explicit first is deterministically identifiable | `AMBIGUOUS_ACTION: cannot determine single next action from explicit state` |

The parser must never continue past a failure condition.

---

## Resolver Behavior

Resolution is strictly rule-based:

1. Extract the ordered list of items from `Immediate Next Steps`. These are the candidate actions.
2. Extract the list of items from `Current Constraints`. These are hard blockers.
3. Extract the list of items from `Not Doing Yet` (if present). These are additional blockers.
4. Filter candidates: remove any candidate whose text explicitly matches or contains an action described in the blockers.
5. The first remaining candidate in original order is the `decision`.
6. If no candidates survive filtering, fail with `NO_VALID_ACTION`.
7. If step numbering or explicit ordering is absent and multiple candidates survive, fail with `AMBIGUOUS_ACTION`.

The resolver does not:
- Infer intent from tone or framing
- Read between lines
- Propose actions not listed in `Immediate Next Steps`
- Expand or elaborate on next steps beyond what is written

---

## Output Format

The ECS MVP prints a single JSON object to stdout on success. Core fields are always present. `efficiency_warning` is optional and omitted when not supported by explicit state.

```json
{
  "decision": "<single next allowed action, taken verbatim from Immediate Next Steps>",
  "why": "Derived from Current Objective and Immediate Next Steps (explicit state).",
  "exact_next_steps": ["<step 1 — full original ordered list, unfiltered>", "<step 2>", "..."],
  "placement": "<full Exit Condition text, or NOT_EXPLICIT_IN_STATE>",
  "state_impact": "Current Phase: <exact extracted text from Current Phase section>",
  "delegation_opportunity": "NONE_IN_MVP",
  "blocked_actions": ["<action excluded by constraints>", "..."]
}
```

`efficiency_warning` is omitted from the output when no explicit constraint or not-doing-yet text supports it.

Field rules:

| Field | Required | Rule |
|---|---|---|
| `decision` | Yes | First valid candidate from `Immediate Next Steps` after constraint filtering |
| `why` | Yes | Fixed string: "Derived from Current Objective and Immediate Next Steps (explicit state)." No line selection. |
| `exact_next_steps` | Yes | Full original ordered list from `Immediate Next Steps`, unfiltered |
| `placement` | Yes | Full stripped content of `Exit Condition` section if present. If multiple lines, joined with `" \| "`. No line selection. If absent or empty, `NOT_EXPLICIT_IN_STATE`. |
| `state_impact` | Yes | Full stripped content of `Current Phase` section: `"Current Phase: <text>"`. If multiple lines, joined with `" \| "`. No line selection. No added interpretation. |
| `efficiency_warning` | No | Omit key entirely if no explicit constraint supports it |
| `delegation_opportunity` | Yes | Always `NONE_IN_MVP` in this version |
| `blocked_actions` | Yes | Every item excluded by `Current Constraints` or `Not Doing Yet` |

---

## Blocker Matching Limitations

Blocker matching uses strict case-insensitive substring matching only.

- A candidate is blocked only if a blocker string is a literal substring of the candidate string.
- This does not handle semantic similarity. A logically equivalent constraint phrased differently will not be detected.
- This is intentional for MVP determinism: the resolver does not infer meaning.
- Operators must write blocker text to match candidate text literally if blocking is required.

---

## What ECS MVP Is NOT Allowed To Do

- Perform semantic interpretation of section content
- Infer actions not explicitly listed in `Immediate Next Steps`
- Suggest API work unless it appears in `Immediate Next Steps` and is not blocked
- Expand blocked actions beyond what `Current Constraints` and `Not Doing Yet` explicitly state
- Output vague strategic advice
- Continue past any failure condition
- Read files other than the three authoritative inputs
- Use external libraries or network access
- Modify any file
