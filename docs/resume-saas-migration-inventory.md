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

### Active / In-Progress

| Step | Source | Target | Class | Reason Code | Ready | Rationale |
|---|---|---|---|---|---|---|
| 15 | `backend/services/rewrite_orchestrator_v3.py` | `backend/services/rewrite_orchestrator_v4.py` | A | `A_EXACT_PORT` | Yes | Planner confirmed exact port, `Source Context Required: yes`, single file, deterministic |
| 16 | `backend/services/rewrite_orchestrator_v3.py` | `backend/services/rewrite_orchestrator_v4.py` | A | `A_EXACT_PORT` | Yes — same as step 15, planner artifact exists | Planner output matches Class A criteria |
| 17 | `backend/services/rewrite_orchestrator_v3.py` | `backend/services/rewrite_orchestrator_v5.py` | A | `A_EXACT_PORT` | Yes — use 2026-04-05 artifact cycle (2026-04-04 cycle was incomplete, do not queue from it) | Same deterministic port pattern, `Source Context Required: yes` |

> **Note:** Steps 15–17 target rewrite_orchestrator variant files. The v5 file does not yet exist in the repo. Step 17 should only run after step 15/16 are confirmed stable, since v4 is the intermediate step.

---

### New Candidates — Ready Now

| Step | Source | Target | Class | Reason Code | Ready | Rationale |
|---|---|---|---|---|---|---|
| 18 | `backend/services/proposal_validator.py` | `backend/schemas/proposal_schema.py` | A | `A_EXACT_PORT` | Yes — source is a single complete module, target is empty | `proposal_schema.py` is currently 0 bytes; extracting the JSON schema constant and `Proposal` dataclass from `proposal_validator.py` is a deterministic, single-file port with no new behavior |

---

### New Candidates — Blocked (Class B or C)

| Target | Class | Reason Code | Blocked Because |
|---|---|---|---|
| `backend/api/rewrite.py` | C | `C_AMBIGUOUS_SPEC` | 0 bytes, no spec, requires API design decisions and integration with multiple services — not a port |
| `backend/api/resume.py` | C | `C_AMBIGUOUS_SPEC` | 0 bytes, no spec, upload/parse endpoint requires framework decisions and error-handling design |
| `backend/api/jobs.py` | C | `C_AMBIGUOUS_SPEC` | 0 bytes, no spec, purpose not defined |
| `backend/models/` | C | `C_AMBIGUOUS_SPEC` | Empty directory, no source to port, requires architectural decisions |
| Consolidation of `rewrite_orchestrator_v*` into a single canonical file | B | `B_REVIEW_REQUIRED` | Multi-version rationalization requires judgment; output is not a direct port of any single source file |

---

## Recommended First Queue

Only jobs with existing planner artifacts and confirmed Class A classification.

```json
[
  {
    "workflow_type": "code_migration",
    "workflow_spec_version": "1",
    "job_type": "migration",
    "venture": "resume-saas",
    "step": 17,
    "date": "2026-04-04",
    "expected_class": "A"
  }
]
```

> Step 15 is the current active job. Step 16 targets the same file as step 15 — run 15 first and confirm. Step 17 (`rewrite_orchestrator_v5.py`) is the cleanest next queue candidate. Use the **2026-04-05** artifact cycle — the 2026-04-04 step-17 artifact set was incomplete and must not be used for queueing. The 2026-04-05 cycle has a confirmed successful artifact set and its target file does not yet exist (no overwrite risk).

**Step 18 (`proposal_schema.py`)** is the second recommended queue entry once step 17 is confirmed. Its planner artifact does not yet exist and must be created with `run-migration-start` before it can run.

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

- Steps 2–13 are complete. The migration log records for those steps are the source of truth; do not re-run them.
- The `rewrite_orchestrator.py` (no version suffix) at `backend/services/` is the established v1 foundation. It must not be overwritten by any batch job without explicit operator review.
- `proposal_schema.py` is 0 bytes and is the cleanest new Class A candidate once a planner artifact is created for it.
- The API layer is the next major phase of work but requires a separate planning pass before any job can be queued.
- All steps 15–17 exist in the migration logs as manual runs from earlier sessions. Before re-queuing any of them through the batch system, confirm that the target files are in their expected state.
