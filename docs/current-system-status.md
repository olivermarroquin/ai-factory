# Current System Status

## Purpose

Provide a concise, accurate snapshot of the ai-factory controlled execution system based on current repository reality.

This file is an operational status document. It must reflect actual implemented behavior, not intended architecture.

---

## Current System Phase

**Phase: Controlled Execution — Full Lifecycle Control Implemented**

The system has a functioning, enforced control loop covering the entire execution lifecycle. Guardian is a required blocking gate at every write point. ECS is connected to Guardian's consistency check. The operator entrypoint, transition command, and outcome recording command are all implemented.

Current reality:

- migration pipeline is real and proven
- ECS reads state and resolves next action — used by Guardian consistency check
- Guardian is a required blocking gate in migration execution, objective transitions, and outcome recording
- operator entrypoint (`ai-factory-run`) coordinates state → ECS → Guardian → execution
- objective transitions are controlled via `ai-factory-transition`
- post-execution outcome recording is controlled via `ai-factory-record-outcome`
- the system can intentionally block migration execution when the objective is system-building
- context transfer still depends on manual state files and operator discipline
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
- **rollback enforced**: if post-write Guardian fails, previous objective is atomically restored before exit — system is never left in an invalid objective state

Status: **implemented and enforced**

### Post-Execution Outcome Recording — `ai-factory-record-outcome`

```
./ai-factory-record-outcome --queue-state <path> --outcome succeeded [--notes "<text>"]
./ai-factory-record-outcome --queue-state <path> --outcome failed [--notes "<text>"]
```

- validates declared outcome against actual queue-state job statuses
- checks for duplicate outcome records per queue-state (write-once per batch)
- runs Guardian pre- and post-write
- atomically updates `system-state/current-system-state.md` with execution cycle block
- writes outcome record to `outcome-records/`
- prints advisory for next step (another run or transition to system-building)

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
- Guardian runs pre- and post-write in `ai-factory-record-outcome`
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

### Operator Layer

New layer in `tools/operator/`. Advisory and orchestration only — does not modify system state or invoke execution.

Entrypoint: `ai-factory-operator`

```
./ai-factory-operator                        # instruction block (default)
./ai-factory-operator --json                 # full structured output
./ai-factory-operator --export-required-input
./ai-factory-operator --export-record-create
./ai-factory-operator --export-all
./ai-factory-operator --transition-to <mode> # inject transition command
./ai-factory-operator --advisor              # model-backed advisory output
./ai-factory-operator --advisor-with-history # same + recent run context
```

Components:

| Tool | Role |
|---|---|
| `generate_snapshot.py` | Structured JSON snapshot of current control state |
| `route_action.py` | Pure interpreter: snapshot → next allowed action |
| `build_context_bundle.py` | Snapshot → minimal context file set |
| `generate_instruction.py` | Snapshot + router + context → instruction block |
| `run_operator.py` | Orchestrates all layers with snapshot validation gate |
| `write_operator_run.py` | Creates and updates operator run records |
| `run_advisor.py` | Model-backed advisor (uses claude binary via session credentials) |

Operator run recording: `ai-factory-record-run create` / `ai-factory-record-run update --file <path>`

Operator run records stored in: `operator-runs/`

Known limitations:
- advisor requires `claude` binary with Claude Code session credentials (`CLAUDE_CODE_EXECPATH`)
- operator layer is advisory only — does not gate or block execution
- snapshot validation gate in `run_operator.py` enforces phase/action consistency before routing

Assessment: **implemented — advisory and orchestration layer**

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

`ai-factory-record-outcome` is implemented. Canonical design reference: `docs/post-execution-state-update-control.md`

Implemented behavior:
- validates declared outcome against actual job statuses (all jobs succeeded / at least one failed)
- duplicate-detection guard — write-once per queue-state
- Guardian pre- and post-write gate
- atomically updates `system-state/current-system-state.md` with execution cycle block
- writes outcome record to `outcome-records/`
- prints advisory for transition decision

Status: **implemented and enforced**

---

## Current Known Limitations

- Guardian stale-state check has incomplete artifact mapping for some current step language
- multiple orchestrator versions remain in the resume-saas repo simultaneously
- tests in resume-saas require `PYTHONPATH=.` to run
- context transfer depends on manual operator discipline — no Context Engine
- operator advisor requires `claude` binary with active Claude Code session — not portable to non-Claude-Code environments
- `python3` binary resolution differs between bash wrappers; `ai-factory-advisor` uses `python3.12` explicitly (environment-specific)
- operator layer is not authoritative — outputs are advisory only, do not gate execution

---

## Immediate Next System Objective

Transition to migration-execution mode for next cycle, or extend Guardian stale-state coverage.

---

## Notes

- `workflow_spec_version` is a string, not an integer.
- `app_build`, `automation_build`, and `ui_conversion` are policy-defined only — not executable.
- The system is controlled but not autonomous. All execution and phase transitions require explicit operator invocation.
- State surface files (`system-state/*.md`) must be updated only through controlled mechanisms. Direct edits outside the defined commands are not part of the controlled flow.
- `ai-factory-transition` now includes atomic rollback: if post-write Guardian fails, the previous objective is restored before exit.
- transition-records/ is populated with records from completed transitions.
