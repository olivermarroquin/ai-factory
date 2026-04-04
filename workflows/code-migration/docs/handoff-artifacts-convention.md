# Handoff Artifacts Convention

## Purpose

Define the standard artifact structure for each code-migration step so outputs are consistent, reviewable, and usable by future automation.

## Principle

Each migration step should produce a small set of structured artifacts.

These artifacts should make it possible to answer:

- what source file was analyzed
- what target file was changed
- what the intended scope was
- what was actually implemented
- whether the reviewer approved it
- what the next safe step is

---

## Migration Step ID Format

Use this format:

`NNN_slug`

Examples:

- `001_resume_parser_read_lines`
- `002_resume_parser_extract_sections`
- `003_resume_parser_numbered_view`

Rules:

- `NNN` = 3-digit sequence number within the venture
- `slug` = short, descriptive, lowercase, underscore-separated
- slug should describe the migration scope, not the whole feature

---

## Recommended Folder Structure Per Venture

Example:
`ai-factory/ventures/<venture>/migration-logs/NNN_slug/`

Inside each step folder:

- `analyzer.md`
- `planner.md`
- `coder.md`
- `reviewer.md`
- `meta.json`

Optional:

- `notes.md`
- `source-snippet.md`
- `diff.md`

---

## Required Files

### analyzer.md

Contains:

- source file
- classification
- role
- preserve
- leave_behind
- recommended_next_scope
- notes

### planner.md

Contains:

- target file
- target scope
- goal
- constraints
- do_not_touch
- source_context_required
- implementation prompt

### coder.md

Contains:

- target file
- changes made
- short explanation
- any blockers

### reviewer.md

Contains:

- status
- correct
- issues
- drift_detected
- next_safe_step

### meta.json

Contains minimal machine-readable metadata.

Example shape:

```json
{
  "step_id": "001_resume_parser_read_lines",
  "venture": "resume-saas",
  "source_file": "resume-factory/01_projects/resume-factory/scripts/rf_docx_extract.py",
  "target_file": "resume-saas/backend/services/resume_parser.py",
  "scope": "implement read_docx_lines helper",
  "status": "approved",
  "created_at": "",
  "updated_at": ""
}
```
