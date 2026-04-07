# Current System State

## Purpose

Operational snapshot of ai-factory as of 2026-04-06. Provides enough context for execution-control work without reading chat history or source code.

---

## Current Phase

**Phase: Logging Improvement Implemented — Next-Step Selection**

- Migration pipeline complete and proven (steps 17 and 18)
- System State Surface complete (`current-system-state.md`, `authoritative-files.md`, `current-objective.md`)
- ECS MVP complete — resolver, gate-check, and read-state all specified, implemented, and exit-reviewed
- System Guardian MVP complete — all four checks (stale state, ECS consistency, forbidden transition, missing artifact) and engine specified, implemented, and exit-reviewed
- Rewrite API slice FULLY VALIDATED — spec → implementation → 14 tests → Flask Blueprint → app wiring → end-to-end HTTP confirmed
  - `docs/rewrite-api-spec-v1.md` — written and accepted
  - `docs/rewrite-api-test-scope-v1.md` — written and accepted
  - `docs/rewrite-api-framework-adapter-scope-v1.md` — written and accepted
  - `docs/rewrite-api-app-wiring-scope-v1.md` — written and accepted
  - `backend/api/rewrite.py` — implemented, spec-reviewed, error contract corrected
  - `backend/services/rewrite_orchestrator_v5.run_rewrite()` — implemented
  - `tests/backend/test_rewrite_api.py` — 14 tests implemented, all passing
  - `backend/api/rewrite_routes.py` — Flask Blueprint implemented, route smoke-tested
  - `app.py` — Flask app created, `rewrite_bp` registered, `POST /rewrite` end-to-end confirmed
- Resume API slice FULLY VALIDATED — spec → implementation → 12 tests → Flask Blueprint → app wiring → end-to-end HTTP confirmed
  - `docs/resume-api-spec-v1.md` — written and accepted
  - `docs/resume-api-test-scope-v1.md` — written and accepted
  - `docs/resume-api-framework-adapter-scope-v1.md` — written and accepted
  - `docs/resume-api-app-wiring-scope-v1.md` — written and accepted
  - `backend/api/resume.py` — implemented, spec-reviewed
  - `tests/backend/test_resume_api.py` — 12 tests implemented, all passing
  - `backend/api/resume_routes.py` — Flask Blueprint implemented, route smoke-tested
  - `app.py` — `resume_bp` registered, `POST /resume/parse` end-to-end confirmed
- Jobs API slice FULLY VALIDATED — spec → implementation → 11 tests → Flask Blueprint → app wiring → end-to-end HTTP confirmed
  - `docs/jobs-api-spec-v1.md` — written and accepted
  - `docs/jobs-api-test-scope-v1.md` — written and accepted
  - `docs/jobs-api-framework-adapter-scope-v1.md` — written and accepted
  - `docs/jobs-api-app-wiring-scope-v1.md` — written and accepted
  - `backend/api/jobs.py` — implemented, spec-reviewed
  - `tests/backend/test_jobs_api.py` — 11 tests implemented, all passing
  - `backend/api/jobs_routes.py` — Flask Blueprint implemented, route smoke-tested
  - `app.py` — updated, `jobs_bp` registered, `POST /jobs/parse` end-to-end confirmed
- App structure improvement IMPLEMENTED AND VALIDATED — `app.py` refactored to application factory pattern
  - `docs/app-structure-improvement-scope-v1.md` — written and accepted
  - `app.py` — refactored to `create_app() -> Flask`; all three routes reachable, exact 400-contract validation confirmed
- Logging improvement IMPLEMENTED AND VALIDATED — minimal app-level request logging added to `app.py`
  - `docs/logging-improvement-scope-v1.md` — written and accepted
  - `app.py` — named logger with conditional `StreamHandler`; `after_request` hook logs method, path, status code; all three routes confirmed with exact 400-contract responses

---

## Current Architecture

ai-factory is the execution and orchestration layer of the workspace.

| Layer          | Role                                    |
| -------------- | --------------------------------------- |
| second-brain   | Thinking and documentation              |
| repos          | Product source code                     |
| ai-agency-core | Reusable standards, prompts, templates  |
| ai-factory     | Execution and orchestration (this repo) |

Product source code lives in `repos/`. ai-factory does not implement product logic; it orchestrates, validates, and executes workflows against those repos.

---

## Current Executable Workflow

**Only `code_migration` is executable.**

| Field                   | Value                           |
| ----------------------- | ------------------------------- |
| `workflow_type`         | `code_migration`                |
| `workflow_spec_version` | `"1"`                           |
| `job_type`              | `migration`                     |
| Allowed classes         | `A` only                        |
| Allowed reason codes    | `A_EXACT_PORT`, `A_SCHEMA_PORT` |

**Full execution path:**

```
run-migration-start
  → run-migration-preflight <batch-jobs.json>
  → approve-batch-report <batch-report.json>
  → run-migration-cycle --approved-report <batch-report.json>
```

`run-migration-cycle` is the preferred operator entrypoint. It delegates to `run-migration-queue`, which is the coordinator that reads queue-state and enforces policy-driven execution.

**Pipeline stages per job:** analyzer → planner → coder → apply → reviewer

`apply` is the only stage that writes to the target repo. All other stages produce logged artifacts only.

No workflow other than `code_migration` may be executed, even if defined in docs or policy drafts. Execution capability is defined by implemented tooling, not documentation.

---

## Current Proven Capabilities

- Full preflight → approve → queue cycle works end-to-end for `code_migration`
- `A_EXACT_PORT` and `A_SCHEMA_PORT` both classify, validate, and execute correctly through the same pipeline
- Planner, coder, and reviewer outputs are each validated before the next stage runs
- Coder validation is branched by reason code: `A_EXACT_PORT` enforces specific functions; `A_SCHEMA_PORT` enforces schema structure and rejects business logic
- Policy-driven class/reason-code gating enforced at both `run-migration-batch` and `run-migration-queue`
- Queue state is produced by preflight, advanced by approval, consumed by coordinator — no manual syncing required
- Immutable per-run manifests written to `ventures/<venture>/migration-logs/`

---

## Current Project Progress

**resume-saas venture**

Steps completed before controlled pipeline (pre-automation, steps 2–13):

| Target                                     | Status |
| ------------------------------------------ | ------ |
| `backend/services/jd_parser.py`            | Done   |
| `backend/services/resume_parser.py`        | Done   |
| `backend/services/proposal_validator.py`   | Done   |
| `backend/services/rewrite_formatter.py`    | Done   |
| `backend/services/rewrite_orchestrator.py` | Done   |

Steps completed through the controlled queue (2026-04-05):

| Step | Target                                        | Reason Code     |
| ---- | --------------------------------------------- | --------------- |
| 17   | `backend/services/rewrite_orchestrator_v5.py` | `A_EXACT_PORT`  |
| 18   | `backend/schemas/proposal_schema.py`          | `A_SCHEMA_PORT` |

Steps 17 and 18 are the proof that the controlled system works end-to-end for both reason-code variants.

Implemented (rewrite API slice):

| File | Status |
| ---- | ------ |
| `backend/api/rewrite.py` | Complete — implemented, spec-reviewed, error contract fixed |
| `backend/services/rewrite_orchestrator_v5.py` | Complete — `run_rewrite()` added |
| `docs/rewrite-api-spec-v1.md` | Complete — accepted contract |
| `docs/rewrite-api-test-scope-v1.md` | Complete — 14 test cases defined and accepted |
| `docs/rewrite-api-framework-adapter-scope-v1.md` | Complete — Flask adapter scope accepted |
| `tests/backend/test_rewrite_api.py` | Complete — 14 tests implemented, all passing |
| `backend/api/rewrite_routes.py` | Complete — Flask Blueprint, route smoke-tested |
| `docs/rewrite-api-app-wiring-scope-v1.md` | Complete — app wiring scope accepted |
| `app.py` | Complete — Flask app, `rewrite_bp` registered, end-to-end confirmed |

Complete (resume API slice):

| File | Status |
| ---- | ------ |
| `docs/resume-api-spec-v1.md` | Complete — accepted contract |
| `docs/resume-api-test-scope-v1.md` | Complete — 12 test cases defined and accepted |
| `docs/resume-api-framework-adapter-scope-v1.md` | Complete — Flask adapter scope accepted |
| `docs/resume-api-app-wiring-scope-v1.md` | Complete — app wiring scope accepted |
| `backend/api/resume.py` | Complete — implemented, spec-reviewed |
| `tests/backend/test_resume_api.py` | Complete — 12 tests implemented, all passing |
| `backend/api/resume_routes.py` | Complete — Flask Blueprint, route smoke-tested |
| `app.py` | Updated — `resume_bp` registered, `POST /resume/parse` end-to-end confirmed |

Complete (jobs API slice):

| File | Status |
| ---- | ------ |
| `docs/jobs-api-spec-v1.md` | Complete — accepted contract |
| `docs/jobs-api-test-scope-v1.md` | Complete — 11 test cases defined and accepted |
| `docs/jobs-api-framework-adapter-scope-v1.md` | Complete — Flask adapter scope accepted |
| `docs/jobs-api-app-wiring-scope-v1.md` | Complete — app wiring scope accepted |
| `backend/api/jobs.py` | Complete — implemented, spec-reviewed |
| `tests/backend/test_jobs_api.py` | Complete — 11 tests implemented, all passing |
| `backend/api/jobs_routes.py` | Complete — Flask Blueprint implemented, route smoke-tested |
| `app.py` | Updated — `jobs_bp` registered, `POST /jobs/parse` end-to-end confirmed |

Not yet implemented:

- `backend/models/` — empty directory

---

## Current Planned But Not Executable Workflows

| Workflow type      | Status                                                                                 |
| ------------------ | -------------------------------------------------------------------------------------- |
| `app_build`        | Policy-defined only. No execution code, preflight logic, or policy enforcement exists. |
| `automation_build` | Policy-defined only. Same.                                                             |
| `ui_conversion`    | Policy-defined only. Same.                                                             |

These must not be added to `config/migration-execution-policy.json` until their full execution infrastructure is built.

---

## Current Operational Truth Sources

| Source                                   | What it governs                                                                  |
| ---------------------------------------- | -------------------------------------------------------------------------------- |
| `config/migration-execution-policy.json` | Allowed workflow types, classes, reason codes                                    |
| `batch-reports/<ts>_queue-state.json`    | Active queue state                                                               |
| `batch-reports/<ts>_batch-report.json`   | Preflight report and approval status                                             |
| `queue-runs/<ts>_queue-run.json`         | Per-cycle execution record                                                       |
| `ventures/<venture>/migration-logs/`     | Per-step manifests and stage artifacts (ground truth for what actually executed) |

---

## Notes

- A successful queue must not be rerun directly. Any repeat execution requires a fresh preflight + approval cycle.
- `run-migration-batch` and `run-migration-queue` are independent entrypoints that both enforce the same policy file. `run-migration-cycle` is preferred.
- `workflow_spec_version` is a string. `"1"` is the only valid value for `code_migration`.
