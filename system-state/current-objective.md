# Current Objective

## Purpose

Working direction for the current phase of ai-factory development. Tells an operator or model what to do next, why, and what to skip.

---

## Current Objective

**Write the rewrite API spec.**

System Guardian MVP is complete (exit review passed 2026-04-06). The next step is writing `docs/rewrite-api-spec-v1.md` — the contract for `backend/api/rewrite.py`. No implementation yet.

---

## Why This Is Next

The controlled migration pipeline works end-to-end (steps 17 and 18 proven). The execution mechanics are sound. What is missing is:

1. A clean, reliable state surface that any agent or operator can read to understand system state without digging through source code or chat history — **this is being built now**.
2. An Execution Control System that can inspect state, gate actions, and surface decisions without human ad-hoc coordination — **this is next**.
3. A System Guardian that monitors system health, detects drift, and enforces invariants — **this follows**.

After that, the first API work begins: writing the spec for `backend/api/rewrite.py`, not implementing it yet.

---

## Current Constraints

- Only `code_migration` jobs are executable. Do not attempt to run `app_build`, `automation_build`, or `ui_conversion` jobs.
- `backend/api/rewrite.py`, `resume.py`, `jobs.py` have no spec. No migration jobs can be queued for them yet.
- A fresh preflight + approval cycle is required before any queue execution. Do not rerun from an old queue-state.
- Class B work (e.g., consolidating `rewrite_orchestrator_v1` through `v5`) requires human review and must not go through the automated queue.
- Policy file (`config/migration-execution-policy.json`) is the gate. Nothing executes that is not in the allowlist.
- `backend/api/rewrite.py` implementation must not be started until `docs/rewrite-api-spec-v1.md` is written and reviewed.

---

## Immediate Next Steps

1. **Write rewrite API spec** — write `docs/rewrite-api-spec-v1.md` defining the full contract for `backend/api/rewrite.py`. No implementation.

---

## Not Doing Yet

- Implementing `backend/api/rewrite.py` — blocked until `docs/rewrite-api-spec-v1.md` is complete
- Implementing `backend/api/resume.py`, `jobs.py` — no spec exists for either
- Adding `app_build`, `automation_build`, or `ui_conversion` to the execution pipeline
- Consolidating `rewrite_orchestrator_v1` through `v5` — Class B work, not automated
- Parallel job execution, partial batch recovery, or cross-venture batches
- Any new `code_migration` steps until API spec is complete and reviewed

---

## Exit Condition

Rewrite API spec is complete when: `docs/rewrite-api-spec-v1.md` is written, defines the full contract for `backend/api/rewrite.py`, and has been reviewed. Backend implementation work begins immediately after.
