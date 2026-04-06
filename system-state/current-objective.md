# Current Objective

## Purpose

Working direction for the current phase of ai-factory development. Tells an operator or model what to do next, why, and what to skip.

---

## Current Objective

**Build the System Guardian MVP.**

ECS MVP is complete (exit review passed 2026-04-06). System State Surface and ECS MVP are both done. System Guardian is the next phase.

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
- API spec work must not be started until System Guardian MVP is complete.

---

## Immediate Next Steps

1. **Implement Guardian Missing Control Artifact Check** — build `tools/guardian/check_missing_artifact.py` per `docs/system-guardian-mvp-spec.md` Check 4.
4. **Implement Guardian engine** — build `tools/guardian/run_guardian.py` that runs all four checks and emits the full JSON output defined in `docs/system-guardian-mvp-spec.md`.
5. **System Guardian MVP exit review** — confirm all exit condition criteria in `docs/system-guardian-mvp-spec.md` are met.

---

## Not Doing Yet

- API spec (`docs/rewrite-api-spec-v1.md`) — not started; blocked until System Guardian MVP is complete
- Implementing `backend/api/rewrite.py`, `resume.py`, or `jobs.py` — no spec exists
- Adding `app_build`, `automation_build`, or `ui_conversion` to the execution pipeline
- Consolidating `rewrite_orchestrator_v1` through `v5` — Class B work, not automated
- Parallel job execution, partial batch recovery, or cross-venture batches
- Any new `code_migration` steps until System Guardian MVP is complete

---

## Exit Condition

System Guardian MVP is complete when: invariant checks, drift detection, and health reporting are specified, implemented, and exit-reviewed. API spec work begins immediately after.
