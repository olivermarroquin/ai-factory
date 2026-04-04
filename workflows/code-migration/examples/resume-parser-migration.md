# Example: Resume Parser Migration

## Source

- resume-factory/scripts/rf_docx_extract.py

## Target

- resume-saas/backend/services/resume_parser.py

## Analyzer Output

Classification:

- core logic

Preserve:

- DOCX reading
- section extraction
- numbered prompt view logic

Leave behind:

- old file organization
- old prompt formatting structure if not needed
- any local workflow assumptions

Recommended next scope:

- migrate read_docx_lines
- then migrate locate_sections
- then migrate numbered view

## Planner Output

Target file:

- backend/services/resume_parser.py

Target scope:

- implement build_numbered_resume_view()

Constraints:

- deterministic only
- no CLI behavior
- no unrelated refactors
- respect lowercase section keys

## Reviewer Output

Check:

- scope stayed local
- numbering format is correct
- line index uses exact original strings
- no architecture drift
