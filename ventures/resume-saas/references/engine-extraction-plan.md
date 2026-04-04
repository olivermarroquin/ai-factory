# Resume SaaS Engine Extraction Plan

## Goal

Extract the reusable engine from Resume Factory and prepare it for a web-based Resume SaaS architecture.

## Confirmed Core Files Reviewed

- rf_docx_extract.py
- rf_jd_terms.py
- rf_proposal_schema.py

## Confirmed Supporting File Reviewed

- rf_render_rewrite_packet.py

## Core Engine Roles Identified

### 1. Resume Parsing

File:

- rf_docx_extract.py

Role:

- read DOCX resumes
- normalize content
- locate resume sections
- create numbered prompt-ready blocks

### 2. Job Description Parsing

File:

- rf_jd_terms.py

Role:

- extract relevant JD terms
- suppress junk
- promote useful phrases
- return structured keyword candidates

### 3. Validation / Contract Layer

File:

- rf_proposal_schema.py

Role:

- define valid AI proposal structure
- validate AI outputs
- provide JSON schema for structured outputs

### 4. Human Review Formatting

File:

- rf_render_rewrite_packet.py

Role:

- render rewrite packet results into deterministic Markdown for review

## Extraction Principle

Do not migrate the whole repo.

Extract the engine from:

- 01_projects/resume-factory/lib
- 01_projects/resume-factory/scripts

Avoid directly migrating:

- 07_system/bin
- 07_system/state
- 07_system/checkpoints
- 07_system/venvs
- local job folder structure
- local output folders

## Likely Future Backend Shape

/backend
/services
resume_parser.py
jd_parser.py
proposal_validator.py
rewrite_formatter.py

## Expected Migration Pattern

1. identify engine files
2. move/adapt logic into backend service modules
3. create backend endpoints around them
4. connect UI later

## Rule

Preserve deterministic logic.
Replace local shell workflow.
Do not carry over one-user operating structure into the SaaS app.
