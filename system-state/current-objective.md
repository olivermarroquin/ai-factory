# Current Objective

## Purpose

Working direction for the current phase of ai-factory development. Tells an operator or model what to do next, why, and what to skip.

---

## Current Objective

**Select the next step after service exception logging.**

App-level request logging and service exception logging are both in place. All three handler files emit ERROR-level tracebacks on service failure. No active implementation work is in progress. The current task is to make an explicit next-step selection before any further work begins. Config improvements and broader product direction are both available options — neither may proceed until explicitly selected.

---

## Why This Is Next

Service exception logging is complete. The backend now has both request-level visibility (`app.py` after_request hook) and failure-level visibility (handler `logger.exception()` on service errors). The system requires an explicit selection before any further work — config improvement, a new API slice, or other — to prevent uncontrolled scope advancement.

---

## Current Constraints

- Only `code_migration` jobs are executable. Do not attempt to run `app_build`, `automation_build`, or `ui_conversion` jobs.
- No implementation work of any kind may begin until an explicit next-step selection is made.
- A fresh preflight + approval cycle is required before any queue execution. Do not rerun from an old queue-state.
- Class B work (e.g., consolidating `rewrite_orchestrator_v1` through `v5`) requires human review and must not go through the automated queue.
- Policy file (`config/migration-execution-policy.json`) is the gate. Nothing executes that is not in the allowlist.

---

## Immediate Next Steps

1. **Decide next step after service exception logging** — select one: (a) config improvement, (b) broader product direction (new API slice, service layer, persistence), or (c) other explicitly named work. No implementation begins until a selection is recorded here.

---

## Not Doing Yet

- Any implementation work until next step is explicitly selected
- Config improvements — available but not selected
- New API slices — available but not selected
- Persistence layer, auth, or any other infrastructure
- Consolidating `rewrite_orchestrator_v1` through `v5` — Class B work, not automated
- System-level improvements (config, logging, app structure) — blocked until explicitly selected
- Adding `app_build`, `automation_build`, or `ui_conversion` to the execution pipeline
- Consolidating `rewrite_orchestrator_v1` through `v5` — Class B work, not automated
- Parallel job execution, partial batch recovery, or cross-venture batches
- Any new `code_migration` steps

---

## Exit Condition

This phase is complete when: an explicit next-step selection is recorded in this file and implementation of that selected path begins.
