# Current Objective

## Purpose

Working direction for the current phase of ai-factory development. Tells an operator or model what to do next, why, and what to skip.

---

## Current Objective

**Build the System State Surface V1, then the Execution Control System MVP.**

This phase establishes the System State Surface V1. The next phase is Execution Control System MVP.

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

---

## Immediate Next Steps

1. **Complete System State Surface** (this conversation) — write `current-system-state.md`, `authoritative-files.md`, `current-objective.md`.
2. **Execution Control System MVP** — define what it means to inspect and gate execution state programmatically. Likely a read-state tool, a gate-check tool, and a decision surface.
3. **System Guardian MVP** — define invariant checks, drift detection, and health reporting for the controlled pipeline.
4. **API spec first** — write `docs/rewrite-api-spec-v1.md` to define the contract for `backend/api/rewrite.py` before any migration job can target the API layer.

---

## Not Doing Yet

- Implementing `backend/api/rewrite.py`, `resume.py`, or `jobs.py` — no spec exists
- Adding `app_build`, `automation_build`, or `ui_conversion` to the execution pipeline
- Consolidating `rewrite_orchestrator_v1` through `v5` — Class B work, not automated
- Parallel job execution, partial batch recovery, or cross-venture batches
- Any new `code_migration` steps until the state surface and execution control are in place

---

## Exit Condition

System State Surface is complete when all three files (`current-system-state.md`, `authoritative-files.md`, `current-objective.md`) are written and accurate. Execution Control System MVP begins immediately after.
