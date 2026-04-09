# Current System Status

## Purpose

Provide a concise, accurate snapshot of the ai-factory controlled execution system based on current repository reality and reconciled state.

This file is an operational status document. It must reflect actual implemented behavior, not intended architecture.

---

## Current System Phase

**Phase: Core System Stabilization — State Sync Completed, Enforcement Still Partial**

The system has moved beyond early migration proof-of-concept status, but it is not yet a fully controlled execution system.

Current reality:

- the migration system is implemented and operational
- resume-saas has advanced materially as a migration validation harness
- ECS exists as implemented tooling but does not control runtime execution
- Guardian exists as implemented tooling but does not enforce runtime execution
- Context transfer still depends on manual state files and operator discipline

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

```text
run-migration-start
  → run-migration-preflight <batch-jobs.json>
  → approve-batch-report <batch-report.json>
  → run-migration-cycle --approved-report <batch-report.json>
run-migration-cycle delegates queue execution to run-migration-queue.

Current Control Components
ECS

Implemented files exist for:

tools/ecs/resolve_next_action.py
tools/ecs/check_action_allowed.py
tools/ecs/read_state.py

Current status:

reads system-state files
resolves a next action
supports consistency checking
not invoked by migration runtime scripts

Assessment: implemented, but not runtime-controlling execution.

Guardian

Implemented files exist for:

tools/guardian/run_guardian.py
tools/guardian/check_stale_state.py
tools/guardian/check_ecs_consistency.py
tools/guardian/check_forbidden_transition.py
tools/guardian/check_missing_artifact.py

Current status:

checks are implemented
Guardian is invoked manually
no execution path requires Guardian pass before runtime execution

Assessment: implemented, but not runtime-enforcing execution.

Context System

Current status:

no dedicated Context Engine implementation exists
no tools/context/ runtime component exists
effective context transfer relies on:
system-state/current-system-state.md
system-state/current-objective.md
system-state/authoritative-files.md

Assessment: documented, but not implemented.

Knowledge OS

No implemented component has been verified in current repo reality.

Assessment: not currently represented as an implemented system component.

Current Migration System Status

The migration system is the most mature and operational part of the system.

Implemented capabilities include:

preflight classification
approval gate
queue-state creation and advancement
per-job policy gating
analyzer → planner → coder → apply → reviewer execution path
per-run manifests
queue-run and batch-run records

This is the only currently proven execution system.

Current Product-Harness Status — resume-saas

resume-saas is currently serving as the migration validation harness and system test target.

Confirmed implemented backend/API files
backend/api/rewrite.py
backend/api/rewrite_routes.py
backend/api/resume.py
backend/api/resume_routes.py
backend/api/jobs.py
backend/api/jobs_routes.py
backend/schemas/proposal_schema.py
backend/services/jd_parser.py
backend/services/proposal_validator.py
backend/services/resume_parser.py
backend/services/rewrite_formatter.py
backend/services/rewrite_orchestrator.py
backend/services/rewrite_orchestrator_v2.py
backend/services/rewrite_orchestrator_v3.py
backend/services/rewrite_orchestrator_v4.py
backend/services/rewrite_orchestrator_v5.py
app.py
Tests

Confirmed current test state:

tests/backend/test_rewrite_api.py
tests/backend/test_resume_api.py
tests/backend/test_jobs_api.py

All 40 tests pass when run with PYTHONPATH=.

Empty directories
backend/models/
backend/utils/
Important framing

resume-saas progress must be treated as validation-harness progress, not as permission to expand product-building scope.

Current Proven Constraints
only code_migration is executable
ECS is not the runtime controller yet
Guardian is not an execution gate yet
Context transfer is manual
state files must be kept aligned with repo reality
no new workflow type is executable unless full execution infrastructure exists
Current Known Drift / Risk Areas
queue policy enforcement is partially duplicated and partially hardcoded
Guardian stale-state checking has incomplete mapping for current step language
state documents had drifted behind repo reality prior to reconciliation
multiple orchestrator versions remain in the repo at the same time
tests currently require PYTHONPATH=. to collect and run successfully
Immediate System Objective

Bring official state files into alignment with verified repo reality, then continue system-building from a clean checkpoint.

Notes
workflow_spec_version is a string, not an integer.
app_build, automation_build, and ui_conversion remain policy-defined only and are not executable.
Migration runtime is real and operational. ECS and Guardian are real but only partially connected to enforcement/runtime flow.
