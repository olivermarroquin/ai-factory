# Resume SaaS Migration Inventory

## Purpose

Identify all remaining migration candidates for the `resume-saas` venture and classify them for execution through the current controlled batch pipeline. This document is the authoritative reference for what goes into the next batch-jobs file and what must wait.

---

## Source System

- **Repo:** `~/workspace/repos/resume-factory/` (CLI-based, bash + Python, single user)
- **Core source files:** `rf_docx_extract.py`, `rf_jd_terms.py`, `rf_proposal_schema.py`, `rf_render_rewrite_packet.py`
- **Pattern:** Deterministic, stateless Python modules with no web dependencies

## Target System

- **Repo:** `~/workspace/repos/resume-saas/`
- **Structure:** `backend/services/`, `backend/api/`, `backend/schemas/`, `backend/models/`
- **Pattern:** Service-oriented, web-ready, no CLI behavior, no filesystem assumptions

---

## Candidate Migration Jobs

### Completed — Do Not Re-Run

| Source | Target | Status |
|---|---|---|
| `rf_jd_terms.py` | `backend/services/jd_parser.py` | Done (175 lines) |
| `rf_docx_extract.py` | `backend/services/resume_parser.py` | Done (169 lines) |
| `rf_proposal_schema.py` | `backend/services/proposal_validator.py` | Done (126 lines) |
| `rf_render_rewrite_packet.py` | `backend/services/rewrite_formatter.py` | Done (76 lines) |
| foundation | `backend/services/rewrite_orchestrator.py` | Done (76 lines) |

---

### Completed Through Controlled Queue — 2026-04-05

| Step | Source | Target | Reason Code | Status |
|---|---|---|---|---|
| 17 | `backend/services/rewrite_orchestrator_v3.py` | `backend/services/rewrite_orchestrator_v5.py` | `A_EXACT_PORT` | **Completed** via controlled queue, 2026-04-05 |
| 18 | `backend/services/proposal_validator.py` | `backend/schemas/proposal_schema.py` | `A_SCHEMA_PORT` | **Completed** via controlled queue, 2026-04-05 |

Steps 17 and 18 are the first migrations to complete through the full preflight → approve → queue cycle. Do not re-run them. A fresh preflight cycle is required to queue any follow-on work.

---

### Blocked (Class B or C)

| Target | Class | Reason Code | Blocked Because |
|---|---|---|---|
| `backend/api/rewrite.py` | C | `C_AMBIGUOUS_SPEC` | 0 bytes, no spec. **Next planning target** — a rewrite API spec must be written before any job can be queued. |
| `backend/api/resume.py` | C | `C_AMBIGUOUS_SPEC` | 0 bytes, no spec, upload/parse endpoint requires framework decisions and error-handling design |
| `backend/api/jobs.py` | C | `C_AMBIGUOUS_SPEC` | 0 bytes, no spec, purpose not defined |
| `backend/models/` | C | `C_AMBIGUOUS_SPEC` | Empty directory, no source to port, requires architectural decisions |
| Consolidation of `rewrite_orchestrator_v*` into a single canonical file | B | `B_REVIEW_REQUIRED` | Multi-version rationalization requires judgment; output is not a direct port of any single source file |

---

## Next Queue

Steps 17 and 18 are complete. There are no Class A candidates ready to queue right now.

The next action is to produce a spec for `backend/api/rewrite.py` (`docs/rewrite-api-spec-v1.md`). No migration job can be queued for the API layer until that spec exists and a planner artifact is generated from it.

---

## Blocked / Non-Class-A Work

### API Layer (`backend/api/`)

All three API files (`rewrite.py`, `resume.py`, `jobs.py`) are 0 bytes with no spec. They cannot be generated as ports — they require:
- FastAPI or Flask route design
- Request/response schema definition
- Error handling strategy
- Integration with the service layer

These are Class C until a formal spec exists for each endpoint. Do not queue them through the current pipeline.

### Backend Models (`backend/models/`)

Empty directory. No source to port. Requires data model design, ORM decisions, and schema definition. Class C.

### Orchestrator Version Rationalization

`rewrite_orchestrator_v2.py` through `v4.py` (and `v5.py` once generated) need to be reconciled into a single canonical `rewrite_orchestrator.py` once the iteration phase is complete. This rationalization:
- Requires comparing all versions and choosing the authoritative one
- Is not a port — it is a consolidation with judgment
- Should be Class B with explicit human review before apply

Do not queue this through the automated pipeline.

---

## Notes

- Steps 2–13 are complete (pre-controlled-pipeline). The migration log records for those steps are the source of truth; do not re-run them.
- Steps 17 and 18 are the first steps completed through the full controlled queue (preflight → approve → queue). Their artifacts are final.
- The `rewrite_orchestrator.py` (no version suffix) at `backend/services/` is the established v1 foundation. It must not be overwritten by any batch job without explicit operator review.
- `proposal_schema.py` is now populated by step 18 (`A_SCHEMA_PORT`). Do not re-run step 18.
- The API layer is the next major phase. `backend/api/rewrite.py` is the first target. A spec document must exist before any migration job can be created for it.
- The orchestrator version rationalization (`v1`–`v5` → single canonical file) remains Class B work requiring human review. Do not queue it through the automated pipeline.
