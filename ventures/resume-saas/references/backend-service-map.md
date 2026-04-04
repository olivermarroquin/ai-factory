# Resume SaaS Backend Service Map

## Goal

Define the initial backend service structure for Resume SaaS based on the reusable engine extracted from Resume Factory.

The purpose is to map old source logic into a cleaner web-app backend shape.

---

## Backend Design Principle

Resume SaaS backend should be organized by responsibility, not by old script names.

Do not recreate the old repo structure directly.

The new backend should separate:

- parsing
- validation
- generation
- formatting
- orchestration

---

## Proposed Backend Service Structure

/backend
/services
resume_parser.py
jd_parser.py
proposal_validator.py
rewrite_formatter.py
rewrite_orchestrator.py
/schemas
proposal_schema.py
/api
resume.py
jobs.py
rewrite.py

---

## Service Map

### 1. resume_parser.py

Purpose:

- read uploaded resume files
- normalize content
- extract sections
- create prompt-ready resume blocks

Primary source:

- rf_docx_extract.py

Notes:
This is one of the strongest direct-reuse candidates.

---

### 2. jd_parser.py

Purpose:

- process raw job description input
- extract relevant skills / tools / terms
- normalize JD language for downstream use

Primary source:

- rf_jd_terms.py
- possibly later:
  - rf_job_ai_extract_jd.py
  - rf_job_ai_parse_openai.py

Notes:
Start with deterministic term extraction first.
Do not overcomplicate with AI parsing on day one.

---

### 3. proposal_validator.py

Purpose:

- validate AI-generated edit proposals
- enforce allowed sections and operations
- reject malformed outputs

Primary source:

- rf_proposal_schema.py

Notes:
Critical reliability layer.
Should remain deterministic.

---

### 4. rewrite_formatter.py

Purpose:

- format rewrite packet data into human-readable output
- support debug, review, and admin inspection

Primary source:

- rf_render_rewrite_packet.py

Notes:
Useful support layer, but not the core engine.

---

### 5. rewrite_orchestrator.py

Purpose:

- coordinate the full rewrite pipeline
- combine parsed resume input, JD terms, AI calls, validation, and output packaging

Primary source:

- not directly extracted from one file
- assembled from current workflow knowledge across resume-factory

Notes:
This is the first true app-level orchestration layer.
It should call services, not contain all business logic itself.

---

## Schema Layer

### proposal_schema.py

Purpose:

- define shared schema objects and validation structures for proposal data

Primary source:

- rf_proposal_schema.py

Notes:
May start by importing or adapting logic from proposal_validator layer.
Can remain small early on.

---

## API Layer

### resume.py

Purpose:

- resume upload endpoint
- resume parsing endpoint
- preview extracted resume sections

### jobs.py

Purpose:

- accept raw JD text
- parse JD terms
- create job-processing requests

### rewrite.py

Purpose:

- trigger rewrite flow
- return structured rewrite output
- support validation and formatted results

---

## Build Order

### Phase 1

Build:

- resume_parser.py
- jd_parser.py
- proposal_validator.py

Reason:
These are the strongest existing core modules.

### Phase 2

Build:

- rewrite_formatter.py
- basic rewrite_orchestrator.py

Reason:
This adds review and coordination.

### Phase 3

Build:

- API endpoints
- UI integration

Reason:
Only after services are stable.

---

## What Not To Migrate Directly

Do not directly copy into backend:

- 07_system/bin command wrappers
- project/session switching logic
- local state files
- local checkpoints
- venv contents
- local output folder assumptions

---

## Rule

The backend should be:

- service-oriented
- deterministic where possible
- separated from shell/CLI behavior
- built from reusable engine pieces, not copied local workflow clutter
