# Current System Status

## Purpose

Provide a concise, accurate snapshot of the ai-factory controlled execution system as of 2026-04-05. This document gives an operator or model enough context to understand where the system stands without reading chat history or source code.

---

## Current Executable Workflow

**Only `code_migration` is executable right now.**

| Field | Value |
|---|---|
| `workflow_type` | `code_migration` |
| `workflow_spec_version` | `1` |
| `job_type` | `migration` |
| Supported classes | `A` only |
| Supported reason codes | `A_EXACT_PORT`, `A_SCHEMA_PORT` |

The full execution path is:
```
run-migration-start
  → run-migration-preflight <batch-jobs.json>
  → approve-batch-report <batch-report.json>
  → run-migration-cycle --approved-report <batch-report.json>
```

`run-migration-cycle` delegates execution to `run-migration-queue`, which reads the queue-state file and applies policy-driven gating before running each job.

---

## Current Control Mechanisms

| Mechanism | Where enforced |
|---|---|
| Planner structural validation | `migration_execute.py` before coder runs |
| Coder output validation (syntax, imports, signatures) | `migration_execute.py` — branched by reason code |
| Reviewer output validation | `migration_execute.py` before reviewer artifact is saved |
| Classification (class + reason code) | `classify_job()` in `migration_execute.py` |
| Expected vs actual class enforcement | `run-migration-preflight`, `run-migration-batch` |
| Preflight report | `run-migration-preflight` → `batch-reports/` |
| Explicit approval gate | `approve-batch-report` sets `approved=true` |
| Queue state | Written by `run-migration-preflight`, advanced by `approve-batch-report`, consumed by `run-migration-queue` |
| Policy-driven class/reason-code gating | `config/migration-execution-policy.json`, enforced by `run-migration-batch` and `run-migration-queue` |
| Immutable per-run manifests | Written by `migration_execute.py` to `ventures/<venture>/migration-logs/` |
| Queue-run records | Written by `run-migration-queue` to `queue-runs/` |

---

## Current Product Migration Progress — resume-saas

### Completed (pre-controlled-pipeline, steps 2–13)

| Target | Status |
|---|---|
| `backend/services/jd_parser.py` | Done |
| `backend/services/resume_parser.py` | Done |
| `backend/services/proposal_validator.py` | Done |
| `backend/services/rewrite_formatter.py` | Done |
| `backend/services/rewrite_orchestrator.py` | Done |

### Completed (controlled queue, 2026-04-05)

| Step | Target | Reason Code |
|---|---|---|
| 17 | `backend/services/rewrite_orchestrator_v5.py` | `A_EXACT_PORT` |
| 18 | `backend/schemas/proposal_schema.py` | `A_SCHEMA_PORT` |

Steps 17 and 18 are the first migrations to complete through the full preflight → approve → queue cycle. They are the proof that the controlled system works end-to-end for both reason-code variants.

### Not yet implemented

- `backend/api/rewrite.py` — 0 bytes, no spec
- `backend/api/resume.py` — 0 bytes, no spec
- `backend/api/jobs.py` — 0 bytes, no spec
- `backend/models/` — empty directory

---

## Current Artifacts and State Files

| Artifact type | Location |
|---|---|
| Migration logs (per step) | `ventures/<venture>/migration-logs/` |
| Run manifests | `ventures/<venture>/migration-logs/<date>_step-<NN>_run-<timestamp>.json` |
| Preflight reports | `batch-reports/<timestamp>_batch-report.json` |
| Queue-state files | `batch-reports/<timestamp>_queue-state.json` |
| Queue-run records | `queue-runs/<timestamp>_queue-run.json` |
| Batch run records | `batch-runs/<timestamp>_batch-run.json` |
| Execution policy | `config/migration-execution-policy.json` |

---

## What Is Proven

- The full preflight → approve → queue cycle works end-to-end for `code_migration` jobs.
- `A_EXACT_PORT` and `A_SCHEMA_PORT` both classify, validate, and execute correctly through the same pipeline.
- Policy-driven gating (class + reason code) is enforced at both `run-migration-batch` and `run-migration-queue`.
- Queue state is produced by preflight, advanced by approval, and consumed by the coordinator — no manual syncing required.
- Coder validation is correctly branched by reason code: `A_EXACT_PORT` enforces specific functions; `A_SCHEMA_PORT` enforces schema structure and rejects business logic.

---

## What Is Planned Next

1. **Write `docs/rewrite-api-spec-v1.md`** — define the contract for `backend/api/rewrite.py` before any migration job can be queued for the API layer.
2. **Rationalize orchestrator versions** — `rewrite_orchestrator_v1` through `v5` need to be consolidated into a single canonical file. This is Class B work requiring human review; it must not go through the automated queue.
3. **API layer migration** — `backend/api/rewrite.py`, `resume.py`, `jobs.py` — each requires a spec, a planner artifact, and a new classification scheme appropriate to API endpoint generation. Not started.

---

## Notes

- `app_build`, `automation_build`, and `ui_conversion` are defined in `docs/workflow-types-policy.md` but are not executable. They must not be added to `config/migration-execution-policy.json` until their full execution infrastructure is built.
- A successful queue must not be rerun directly. Any repeat execution requires a fresh preflight + approval cycle.
- The policy file at `config/migration-execution-policy.json` is the single source of truth for what classes and reason codes are allowed to execute. Changes to allowed reason codes require editing that file only.
- `run-migration-batch` and `run-migration-queue` both enforce the same policy file but are independent entrypoints. `run-migration-cycle` is the preferred single operator entrypoint.
