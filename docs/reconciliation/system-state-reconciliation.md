# System State Reconciliation

## Purpose

This document reconciles documented system state against observed repository reality before any state-surface files are updated.

It exists to prevent writing incorrect or partially verified information into:

- `system-state/current-system-state.md`
- `system-state/current-objective.md`
- `system-state/authoritative-files.md`
- `docs/current-system-status.md`

This document is a reconciliation artifact, not a replacement for the authoritative state files.

---

## Scope

Repositories inspected:

- `ai-factory`
- `resume-saas`

Inputs used for reconciliation:

- current state and policy docs
- Claude Code factual extraction report
- observed file presence, execution scripts, test status, and repo structure

No assumptions are allowed beyond those inputs.

---

## Reconciliation Outcome Summary

### Confirmed True From Code / Repo Reality

1. **The migration system is implemented and operational.**
   - Preflight, approval, queue, batch, execute, and start scripts are present.
   - The real execution path exists and is wired.
   - Policy gating is active in both batch and queue paths, though not identically implemented.

2. **Only `code_migration` is executable right now.**
   - Policy file allows only:
     - `job_type = migration`
     - `workflow_type = code_migration`
     - `workflow_spec_version = "1"`
     - `class = A`
     - `reason_code in {A_EXACT_PORT, A_SCHEMA_PORT}`

3. **ECS exists as implemented tooling, but is not connected to execution runtime.**
   - `resolve_next_action.py`, `check_action_allowed.py`, and `read_state.py` are present.
   - They read state files and produce decisions/checks.
   - Migration execution scripts do not call ECS directly.

4. **Guardian exists as implemented tooling, but is not connected as an enforced runtime gate.**
   - `run_guardian.py` and all four checks exist.
   - Guardian is invoked manually.
   - No execution script requires Guardian pass before execution.

5. **Context system is not implemented as a tool or runtime component.**
   - No context engine directory or execution layer exists.
   - Current context transfer depends on manual state files and operator discipline.

6. **Resume-saas has moved beyond the earlier "not yet implemented API layer" state.**
   - `backend/api/rewrite.py`, `resume.py`, `jobs.py` all exist and are non-empty.
   - Their route adapters exist.
   - `app.py` exists and registers the API blueprints.
   - Tests exist and pass when run with `PYTHONPATH=.`

7. **`backend/models/` is present and empty.**

8. **`backend/utils/` is present and empty.**
   - This exists in code reality and is not currently represented in state documentation.

9. **Multiple orchestrator versions exist simultaneously.**
   - `rewrite_orchestrator.py`
   - `rewrite_orchestrator_v2.py`
   - `rewrite_orchestrator_v3.py`
   - `rewrite_orchestrator_v4.py`
   - `rewrite_orchestrator_v5.py`

---

## Confirmed Documentation Drift

### Drift 1 — Older current-system-status snapshot is stale

`docs/current-system-status.md` contained an older snapshot that reported the API layer as not yet implemented.

Observed code reality contradicted that snapshot:

- API handler files exist and are non-empty
- route files exist
- app wiring exists
- tests exist and pass with environment setup

### Drift 2 — State claims completion while some supporting files are uncommitted

Claude Code reported:

- `docs/config-improvement-scope-v1.md` exists as untracked
- `docs/persistence-layer-spec-v1.md` exists as untracked

This means repo state and declared completion status are not yet aligned as a committed checkpoint.

### Drift 3 — Guardian stale-state coverage is incomplete

`check_stale_state.py` uses a hardcoded artifact map with limited historical coverage.

Current immediate-next-step language is not fully mapped.

Result:

- stale-state detection can return `UNMAPPED`
- Guardian cannot fully validate current planning state

### Drift 4 — Queue policy enforcement is partially duplicated and partially hardcoded

`run-migration-batch` reads more gate values directly from policy.

`run-migration-queue` hardcodes checks for:

- `workflow_type`
- `workflow_spec_version`
- `job_type`

This creates divergence risk between policy file and runtime enforcement.

---

## Items Verified but Needing Explicit Framing Decision

These are real, but how they are represented in state must be chosen deliberately.

### 1. Resume-saas API implementation status

Observed reality shows implemented API slices and passing tests.

Decision required:

- Should state describe this as **product completion**, or as **migration-system validation output / controlled test harness progress**?

This matters because the system intent says the project is being used as a test harness, not as the primary product-building objective.

### 2. System phase naming

The codebase indicates more progress than the older status file, but less control than the canonical ECS/Guardian documents imply.

Decision required:

- exact phase label to use in `current-system-state.md`
- exact objective wording to use in `current-objective.md`

### 3. Orchestrator version sprawl

Multiple orchestrator versions are present.

Decision required:

- whether state should call this out as accepted temporary history or active consolidation debt

---

## Unverified / Not Proven From Current Extraction Alone

These must not be written as confirmed state without additional direct validation.

1. Whether every scope document listed as complete was actually fully validated in the repo history.
2. Whether all claims in `current-system-state.md` correspond to committed artifacts rather than working-tree state.
3. Whether all route smoke tests and end-to-end confirmations are reproducible from current checkout without hidden environment assumptions.
4. Whether `show-latest-manifest`, `templates/`, and unread supporting files contain additional execution dependencies not covered by the factual report.
5. Whether Claude Code's reported test counts reflect the exact latest file contents after all local modifications.

---

## Reconciliation Decisions

### Accepted as Ground Truth Now

The following can be treated as grounded current reality:

- migration system exists and runs
- only `code_migration` is executable
- ECS is implemented but not runtime-controlling execution
- Guardian is implemented but not runtime-enforcing execution
- Context system is not implemented
- resume-saas API layer exists and is implemented
- tests pass with `PYTHONPATH=.`
- `backend/models/` is empty
- `backend/utils/` is empty
- orchestrator versions are duplicated in the repo

### Blocked From Immediate State-Surface Update

The following should not yet be written directly into final state files without explicit update decisions:

- language implying the product is now the system objective
- claims that Guardian is an enforced gate
- claims that ECS controls execution
- claims that Context Engine is implemented
- claims based on uncommitted files being treated as durable truth

---

## Required State File Update Targets After Reconciliation Approval

Once this reconciliation is accepted, the following files should be updated together in one controlled state-sync pass:

- `docs/current-system-status.md`
- `system-state/current-system-state.md`
- `system-state/current-objective.md`
- `system-state/authoritative-files.md` (only if authoritative relationships need adjustment)

These updates must be made together, not independently.

---

## Proposed State-Sync Principles

When the state files are updated, the update must obey these rules:

1. Prefer newer verified repo reality over stale status snapshots.
2. Distinguish clearly between:
   - implemented
   - enforced
   - documented-only
3. Represent resume-saas as a validation harness unless explicitly re-scoped.
4. Do not mark any control component complete unless it is actually connected to runtime enforcement.
5. Do not treat uncommitted files as stable checkpoint truth until they are reviewed and committed.

---

## Final Reconciliation Conclusion

The system is **not in early migration proof anymore**.

It is in a more advanced but unstable state:

- the migration engine is real and proven
- resume-saas implementation has advanced materially
- ECS and Guardian exist but are not yet controlling execution
- Context Engine is still absent
- state documents are partially stale and must be synchronized

The next safe move is not new implementation.

The next safe move is a **controlled state-sync update** based on this reconciliation, followed by a clean git checkpoint.
