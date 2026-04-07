# Current Objective

## Purpose

Working direction for the current phase of ai-factory development. Tells an operator or model what to do next, why, and what to skip.

---

## Current Objective

**Select the next step after resume API route validation.**

The resume API slice is route-validated: spec accepted, handler spec-reviewed, 12 tests passing, Flask Blueprint implemented and smoke-tested. No next step has been selected. A controlled decision is required before any new work begins.

---

## Why This Is Next

The resume API slice has reached the same route-validated milestone as the rewrite API slice. The next step must be explicitly chosen — it is not automatically app wiring or jobs.py.

---

## Current Constraints

- Only `code_migration` jobs are executable. Do not attempt to run `app_build`, `automation_build`, or `ui_conversion` jobs.
- No additional API implementation or app wiring may begin until a next step is explicitly selected from the decision in Immediate Next Steps.
- `backend/api/jobs.py` has no spec and is blocked until the resume API path is complete or a new selection is explicitly made.
- System-level improvements (config, logging, app structure) are blocked until explicitly selected.
- A fresh preflight + approval cycle is required before any queue execution. Do not rerun from an old queue-state.
- Class B work (e.g., consolidating `rewrite_orchestrator_v1` through `v5`) requires human review and must not go through the automated queue.
- Policy file (`config/migration-execution-policy.json`) is the gate. Nothing executes that is not in the allowlist.

---

## Immediate Next Steps

1. **Decide next step after resume API route validation: app wiring vs expanding API surface** — options are: (a) register `resume_bp` in `app.py` and confirm end-to-end HTTP path, (b) spec and implement `backend/api/jobs.py`, (c) other explicitly selected work. No option may begin without an explicit selection.

---

## Not Doing Yet

- Any further API expansion or app wiring until next step is explicitly selected from the decision in Immediate Next Steps
- Implementing `backend/api/jobs.py` — blocked until resume API path is complete or explicitly re-selected
- System-level improvements (config, logging, app structure) — blocked until explicitly selected
- Adding `app_build`, `automation_build`, or `ui_conversion` to the execution pipeline
- Consolidating `rewrite_orchestrator_v1` through `v5` — Class B work, not automated
- Parallel job execution, partial batch recovery, or cross-venture batches
- Any new `code_migration` steps

---

## Exit Condition

This phase is complete when: a next step is explicitly selected from the decision options in Immediate Next Steps and work on that selection begins.
