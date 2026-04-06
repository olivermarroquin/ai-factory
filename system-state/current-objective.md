# Current Objective

## Purpose

Working direction for the current phase of ai-factory development. Tells an operator or model what to do next, why, and what to skip.

---

## Current Objective

**Complete the Execution Control System MVP.**

System State Surface V1 is complete. ECS MVP spec and resolver exist and have been validated structurally. Work remaining is inside ECS MVP only.

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
- System Guardian must not be started until ECS MVP exit condition is met.
- API spec work must not be started until ECS MVP exit condition is met.

---

## Immediate Next Steps

1. **Update authoritative state files** — bring `current-system-state.md` and `current-objective.md` into alignment with actual current reality so the ECS resolver produces accurate output.
2. **Validate resolver output against updated state** — run `tools/ecs/resolve_next_action.py` and confirm the decision reflects the correct current next step.
3. **Define ECS gate-check** — specify and implement the rule that determines whether a proposed action is allowed to execute given the current state. This is the core gate mechanism of ECS MVP.
4. **Define ECS read-state interface** — specify and implement how the ECS surfaces current system state to an operator or agent in a structured, queryable form.
5. **ECS MVP exit review** — confirm all exit condition criteria are met before proceeding to System Guardian.

---

## Not Doing Yet

- System Guardian MVP — not started; blocked until ECS MVP exit condition is met
- API spec (`docs/rewrite-api-spec-v1.md`) — not started; blocked until ECS MVP exit condition is met
- Implementing `backend/api/rewrite.py`, `resume.py`, or `jobs.py` — no spec exists
- Adding `app_build`, `automation_build`, or `ui_conversion` to the execution pipeline
- Consolidating `rewrite_orchestrator_v1` through `v5` — Class B work, not automated
- Parallel job execution, partial batch recovery, or cross-venture batches
- Any new `code_migration` steps until ECS MVP exit condition is met

---

## Exit Condition

ECS MVP is complete when: (1) authoritative state files are current and the resolver produces accurate output against them, (2) the gate-check mechanism is specified and implemented, (3) the read-state interface is specified and implemented, and (4) an exit review confirms all three criteria are met. System Guardian begins immediately after.
