# Current System State

## Purpose

Operational snapshot of ai-factory based on actual system behavior.

This file reflects what is implemented, enforced, and currently true. It is used by ECS and Guardian as an authoritative input.

---

## Current Phase

Controlled Execution — Full Lifecycle Control Implemented

The system has a functioning, enforced control loop covering the entire execution lifecycle: transition → execute → record outcome → transition. Guardian is a required blocking gate before any migration execution and before any outcome write. ECS resolution is required and validated by Guardian. The operator entrypoint coordinates the full control sequence. Objective transitions and post-execution outcome recording are both controlled.

---

## Architecture Position

ai-factory is the execution and orchestration layer.

| Layer | Role |
|---|---|
| second-brain | documentation |
| repos | product code |
| ai-agency-core | prompts/templates |
| ai-factory | execution system |

---

## Executable Workflow

Only code_migration is executable.

- workflow_type: code_migration
- workflow_spec_version: "1"
- job_type: migration
- class: A only
- reason codes: A_EXACT_PORT, A_SCHEMA_PORT

All five fields are read from `config/migration-execution-policy.json`. That file is the single source of truth for execution permission in both queue and batch paths.

Migration execution is allowed only when the current objective is migration-aligned. When the objective is system-building, Guardian blocks execution before any work begins.

---

## Execution Flow

Official execution path through the operator entrypoint:

```
ai-factory-run --mode execute-allowed-step --queue-state <path>
  → reads state surface
  → runs ECS resolver
  → validates ECS output (non-empty, unambiguous)
  → runs Guardian (all checks must pass)
  → evaluates scope (resolved action must be executable)
  → invokes run-migration-queue
    → per-job policy gate (reads from policy file)
    → run-migration-execute (Guardian gate inside execution)
```

No step is skippable. No bypass flags exist on the entrypoint or transition command.

---

## Control Layer Status

### ECS

- implemented: resolve_next_action.py, check_action_allowed.py, read_state.py
- resolves next action from state surface
- ECS consistency and clear-action are validated by Guardian before execution
- not invoked directly by migration runtime scripts — runs through control loop

Status: IMPLEMENTED — connected to control loop via Guardian

---

### Guardian

- implemented: run_guardian.py + six check scripts
- runs as a required blocking gate inside migration_execute.py (auto-openai mode)
- runs as part of ai-factory-run control loop before any execution
- runs pre- and post-write inside ai-factory-transition
- runs pre- and post-write inside ai-factory-record-outcome

Checks enforced:

| Check | Enforces |
|---|---|
| check_stale_state | next steps are not already completed |
| check_ecs_consistency | ECS surfaces agree with state; ECS returns a clear action |
| check_forbidden_transition | no invalid phase transitions in progress |
| check_missing_artifact | artifacts required by claimed-complete states exist |
| check_policy_integrity | policy file exists, is valid JSON, has all required keys |
| check_objective_alignment | objective has actionable next step; execution is aligned with objective mode |

Status: ENFORCED — blocking gate on all execution paths

---

### Operator Entrypoint

- ai_factory_run.py / ai-factory-run: official front door for execution
- inspect mode: reads state, runs ECS, runs Guardian, reports outcome — no execution
- execute-allowed-step mode: same as inspect, then invokes run-migration-queue if all gates pass

Status: IMPLEMENTED AND ENFORCED

---

### Objective Transition Control

- ai_factory_transition.py / ai-factory-transition: controls phase transitions
- validates preconditions, atomically updates current-objective.md, re-runs Guardian and ECS after write
- writes transition record to transition-records/
- direct edits to current-objective.md outside this command are not part of the controlled flow

Status: IMPLEMENTED AND ENFORCED

---

### Context System

- no Context Engine implementation exists
- relies on manual state files and operator discipline

Status: NOT IMPLEMENTED

---

### Knowledge OS

- no implementation present

Status: NOT IMPLEMENTED

---

## Migration System

- fully operational
- queue + policy gating works (all five fields from policy file)
- Guardian gate active inside execution path
- artifacts and manifests produced per run

Status: COMPLETE (current scope)

---

## Post-Execution State Update Control

- ai_factory_record_outcome.py / ai-factory-record-outcome: IMPLEMENTED
- validates declared outcome against actual queue-state job statuses
- checks for duplicate outcome records per queue-state
- runs Guardian pre- and post-write
- atomically updates current-system-state.md with execution cycle status block
- writes outcome record to outcome-records/
- prints advisory for next transition

Status: IMPLEMENTED AND ENFORCED

---

## resume-saas Status

- API handlers and routes exist
- app.py wired
- 40 tests passing with PYTHONPATH=.
- multiple orchestrator versions present in repo
- backend/models/ and backend/utils/ are empty
- resume-saas serves as the migration validation harness, not the primary objective

---

## Known Gaps

- Guardian stale-state check has incomplete artifact mapping for some current step language
- context transfer depends on manual operator discipline
- transition-records/ directory is not yet populated (no ai-factory-transition run has been committed)

---

## Immediate Next Step

Extend Guardian stale-state coverage to current step language, or continue migration execution and outcome recording cycles.

---

## Constraints

- do not expand workflows
- do not claim ECS is autonomous
- do not claim Guardian enforcement exists where it does not
- do not expand product scope
- do not treat uncommitted or unverified state as ground truth

<!-- EXECUTION_CYCLE_STATUS_START -->
## Latest Execution Cycle Status

- queue_state: batch-reports/20260409T154208Z_queue-state.json
- queue_run_record: /Users/olivermarroquin/workspace/ai-factory/queue-runs/20260409T154918Z_queue-run.json
- outcome: succeeded
- batch_status: succeeded
- recorded_at: 2026-04-09T16:18:11Z

### Notes
approved migration batch completed

<!-- EXECUTION_CYCLE_STATUS_END -->
