# Current Objective

## Purpose

Working direction for the current phase of ai-factory development. Tells an operator or model what to do next, why, and what to skip.

---

## Current Objective

**Select the next step after full rewrite API validation.**

The rewrite API slice is fully validated end-to-end: spec, implementation, 14 passing tests, Flask Blueprint, and live app wiring all confirmed. No next step has been selected. A controlled decision is required before any new work begins.

---

## Why This Is Next

The rewrite API slice has completed every planned validation layer: spec, unit/integration tests, Flask adapter, and live app wiring. The next step must be explicitly chosen — it is not automatically a new API endpoint or system improvement.

---

## Current Constraints

- Only `code_migration` jobs are executable. Do not attempt to run `app_build`, `automation_build`, or `ui_conversion` jobs.
- `backend/api/resume.py` and `backend/api/jobs.py` have no spec. No implementation work may begin on either.
- A fresh preflight + approval cycle is required before any queue execution. Do not rerun from an old queue-state.
- Class B work (e.g., consolidating `rewrite_orchestrator_v1` through `v5`) requires human review and must not go through the automated queue.
- Policy file (`config/migration-execution-policy.json`) is the gate. Nothing executes that is not in the allowlist.
- No additional API implementation or system improvement may begin until a next step is explicitly selected from the decision in Immediate Next Steps.

---

## Immediate Next Steps

1. **Decide next step after full rewrite API validation: expand API surface vs system-level improvements** — options are: (a) spec and implement `backend/api/resume.py`, (b) spec and implement `backend/api/jobs.py`, (c) system-level improvements (e.g., config, logging, app structure). No option may begin without an explicit selection.

---

## Not Doing Yet

- Implementing `backend/api/resume.py`, `backend/api/jobs.py` — no spec exists for either
- Adding `app_build`, `automation_build`, or `ui_conversion` to the execution pipeline
- Consolidating `rewrite_orchestrator_v1` through `v5` — Class B work, not automated
- Parallel job execution, partial batch recovery, or cross-venture batches
- Any new `code_migration` steps
- Any further API expansion or system improvement until next step is explicitly selected from the decision in Immediate Next Steps

---

## Exit Condition

This phase is complete when: a next step is explicitly selected from the decision options in Immediate Next Steps and work on that selection begins.
