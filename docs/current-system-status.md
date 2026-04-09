# Current System Status

## Purpose

Provide a concise, accurate snapshot of the ai-factory controlled execution system based on current repository reality.

This file is an operational status document. It must reflect actual implemented behavior, not intended architecture.

---

## Current System Phase

**Phase: Controlled Execution — Control Loop Enforced, Post-Execution Outcome Control Pending**

The system has a functioning, enforced control loop. Guardian is a required blocking gate. ECS is connected to Guardian's consistency check. The operator entrypoint coordinates the full control loop. Objective transitions are controlled.

Current reality:

- migration pipeline is real and proven
- ECS reads state and resolves next action — used by Guardian consistency check
- Guardian is now a required blocking gate in migration execution
- operator entrypoint (`ai-factory-run`) coordinates state → ECS → Guardian → execution
- objective transitions are controlled via `ai-factory-transition`
- the system can intentionally block migration execution when the objective is system-building
- context transfer still depends on manual state files and operator discipline
- post-execution outcome acknowledgment and state update is designed but not yet implemented as a command
- the system is controlled, not autonomous

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

The policy file is the **single source of truth** for all five of these fields. Both `run-migration-queue` and `run-migration-batch` read them from `config/migration-execution-policy.json`. Nothing is hardcoded.

Migration execution is **allowed only when the current objective is migration-aligned**. When the objective is system-building, Guardian blocks migration execution before any work begins.

---

## Operator Entrypoints

### Primary Entrypoint — `ai-factory-run`

```
./ai-factory-run                         # inspect mode (default)
./ai-factory-run --mode inspect
./ai-factory-run --mode execute-allowed-step --queue-state <path>
```

- **inspect**: reads state, runs ECS, runs Guardian, reports outcome — never invokes execution
- **execute-allowed-step**: same as inspect, then invokes `run-migration-queue` only if all gates pass

Status: **implemented and enforced**

### Objective Transition — `ai-factory-transition`

```
./ai-factory-transition --to system-building --reason "<text>"
./ai-factory-transition --to migration-execution --queue-state <path> --reason "<text>"
```

- validates preconditions before any write
- atomically updates `system-state/current-objective.md`
- re-runs full Guardian and ECS after the write
- writes a transition record to `transition-records/`

Status: **implemented and enforced**

### Migration Pipeline Commands (lower-level)

```
./run-migration-start
./run-migration-preflight
./approve-batch-report
./run-migration-batch
./run-migration-queue
./run-migration-execute
./run-migration-cycle
./classify-migration-job
./show-latest-manifest
```

Under normal operation, these are invoked through `ai-factory-run`, not directly.

---

## Control Component Status

### ECS

Implemented tools:

```
tools/ecs/resolve_next_action.py
tools/ecs/check_action_allowed.py
tools/ecs/read_state.py
```

Current status:

- reads system-state files and resolves a next action
- ECS consistency and clear-action are validated by Guardian before execution
- ECS is re-run as part of post-transition validation in `ai-factory-transition`
- ECS tools are not directly invoked by migration runtime scripts — they run through the control loop

Assessment: **implemented and connected to control loop via Guardian**

---

### Guardian

Implemented tools:

```
tools/guardian/run_guardian.py
tools/guardian/check_stale_state.py
tools/guardian/check_ecs_consistency.py
tools/guardian/check_forbidden_transition.py
tools/guardian/check_missing_artifact.py
tools/guardian/check_policy_integrity.py
tools/guardian/check_objective_alignment.py
```

Current status:

- Guardian runs as a required blocking gate inside `migration_execute.py` (auto-openai mode)
- Guardian runs as part of the `ai-factory-run` control loop before any execution is allowed
- Guardian runs pre- and post-write in `ai-factory-transition`
- a FAIL on any check halts execution with no bypass

Guardian validates:

| Check | What it enforces |
|---|---|
| `check_stale_state` | Next steps are not already completed |
| `check_ecs_consistency` | ECS surfaces agree with state; ECS returns a clear action |
| `check_forbidden_transition` | No invalid phase transitions in progress |
| `check_missing_artifact` | Artifacts required by claimed-complete states exist |
| `check_policy_integrity` | Policy file exists, is valid JSON, has all required keys |
| `check_objective_alignment` | Objective has actionable next step; execution is not misaligned with objective mode |

Assessment: **implemented and enforced as a blocking runtime gate**

---

### Context System

Current status:

- no dedicated Context Engine implementation exists
- effective context transfer relies on:
  - `system-state/current-system-state.md`
  - `system-state/current-objective.md`
  - `system-state/authoritative-files.md`

Assessment: **not implemented — relies on manual state discipline**

---

### Knowledge OS

No implemented component exists.

Assessment: **not implemented**

---

## Migration System Status

The migration system is the most mature and operational part of the system.

Implemented capabilities:

- preflight classification with policy gating
- operator approval gate
- queue-state creation and advancement
- per-job policy enforcement (all five fields read from policy file)
- analyzer → planner → coder → apply → reviewer execution path
- per-run manifests with stage artifacts
- queue-run and batch-run records
- Guardian pre-execution gate inside `migration_execute.py`

Status: **operational — current scope complete**

---

## Post-Execution State Update Control

A canonical design exists for controlled post-execution outcome acknowledgment:

```
docs/post-execution-state-update-control.md
```

This design covers:
- outcome types (succeeded, partially succeeded, failed before work, failed after work)
- operator-driven acknowledgment command (`ai-factory-record-outcome`)
- atomic update of `current-system-state.md`
- duplicate-detection guard
- outcome record in `outcome-records/`
- relationship to `ai-factory-transition`

Status: **design complete, command not yet implemented**

---

## Current Known Limitations

- post-execution outcome acknowledgment has no command yet — operator must update state manually after execution
- Guardian stale-state check has incomplete artifact mapping for some current step language
- multiple orchestrator versions remain in the resume-saas repo simultaneously
- tests in resume-saas require `PYTHONPATH=.` to run
- context transfer depends on manual operator discipline — no Context Engine

---

## Immediate Next System Objective

Implement `ai-factory-record-outcome` to close the post-execution state update gap.

---

## Notes

- `workflow_spec_version` is a string, not an integer.
- `app_build`, `automation_build`, and `ui_conversion` are policy-defined only — not executable.
- The system is controlled but not autonomous. All execution and phase transitions require explicit operator invocation.
- State surface files (`system-state/*.md`) must be updated only through controlled mechanisms. Direct edits outside the defined commands are not part of the controlled flow.
