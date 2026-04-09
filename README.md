# AI Factory

## Purpose

AI Factory is the **controlled execution and orchestration layer** of the system.

It runs **state-driven workflows** under enforced policy, Guardian validation, and ECS decision control.

This is not a code repository or knowledge base — it is the system responsible for:

- executing work through a validated control loop
- enforcing correctness before, during, and after execution
- preventing drift between system state and actual execution
- coordinating phase transitions between system-building and execution modes

---

## System Role

AI Factory operates within a larger system:

- **second-brain / knowledge OS** → thinking, structured knowledge, long-term intelligence
- **repos (e.g., resume-saas)** → source code and product implementations
- **ai-agency-core** → reusable standards, prompts, templates
- **ai-factory** → execution, orchestration, validation, and control

AI Factory does not own ideas or code — it **executes and governs them**.

---

## Current System Phase

**Core System Stabilization — Controlled Execution**

The system has moved past early migration proof. It now has a functioning control loop with enforced gates at every layer. The current focus is maintaining and extending that control before expanding execution scope.

Current reality:

- migration pipeline is real and proven
- ECS reads state and resolves next action
- Guardian validates state coherence, policy integrity, objective alignment, and ECS clarity before execution
- operator entrypoint (`ai-factory-run`) coordinates the full control loop
- objective transitions are controlled (`ai-factory-transition`)
- the system can intentionally block migration execution when the objective is system-building
- the system is controlled, but not autonomous

---

## Control Loop

All execution follows this exact sequence:

```
1. Read state surface
   - system-state/current-system-state.md
   - system-state/current-objective.md
   - system-state/authoritative-files.md

2. ECS resolves next action
   - tools/ecs/resolve_next_action.py
   - must return exactly one clear, non-empty action

3. Guardian validates system state
   - tools/guardian/run_guardian.py
   - must return PASS — any FAIL blocks execution

4. Scope evaluation
   - resolved action must be executable in current phase

5. Execution (if all gates pass)
   - run-migration-queue with approved queue-state
```

No step is skippable. No bypass flags exist.

---

## Core Systems

### Execution Control System (ECS)

ECS determines **what happens next**.

- reads current system state and objective
- evaluates candidates against constraints and blockers
- outputs the single next valid action

ECS tools:

```
tools/ecs/resolve_next_action.py   — resolves next allowed action
tools/ecs/check_action_allowed.py  — validates a proposed action
tools/ecs/read_state.py            — surfaces current state in structured form
```

ECS is connected to the control loop through Guardian's ECS consistency check. A clear ECS action is required before execution proceeds.

---

### System Guardian

System Guardian validates **whether the system is in a state that allows execution to proceed**.

Guardian runs four checks plus two added enforcement checks:

| Check | What it validates |
|---|---|
| `check_stale_state.py` | Next steps are not already completed |
| `check_ecs_consistency.py` | ECS surfaces agree with each other and with state files; ECS returns a clear action |
| `check_forbidden_transition.py` | No invalid phase transitions are being attempted |
| `check_missing_artifact.py` | Artifacts required by claimed-complete states exist |
| `check_policy_integrity.py` | Policy file exists, is valid JSON, and has all required keys |
| `check_objective_alignment.py` | Objective defines an actionable next step; execution is not misaligned with objective mode |

Guardian blocks execution if:

- state structure is invalid or incoherent
- objective is system-building while migration execution is attempted
- policy file is missing or malformed
- ECS cannot return a clear next action
- claimed-complete artifacts are missing

---

## Operator Commands

### Primary Entrypoint

```
./ai-factory-run                        # inspect mode (default — never executes)
./ai-factory-run --mode inspect
./ai-factory-run --mode execute-allowed-step --queue-state <path>
```

`ai-factory-run` is the front door. It coordinates the full control loop:
reads state → runs ECS → runs Guardian → evaluates scope → optionally executes.

- **inspect mode**: runs the full control loop, reports outcome, never invokes execution
- **execute-allowed-step mode**: same as inspect, then invokes run-migration-queue only if all gates pass

No execution happens without explicit `--mode execute-allowed-step`.

---

### Objective Transition

```
./ai-factory-transition --to system-building --reason "<text>"
./ai-factory-transition --to migration-execution --queue-state <path> --reason "<text>"
```

`ai-factory-transition` controls phase changes between system-building mode and migration-execution mode.

- validates preconditions before any write
- atomically updates `system-state/current-objective.md`
- re-runs full Guardian and ECS after the write
- writes a transition record to `transition-records/`
- exits non-zero if any gate fails — no partial state

Objective transitions are the only authorized mechanism for changing the objective mode. Direct edits to `current-objective.md` outside this command are not part of the controlled flow.

---

### Migration Pipeline Commands

These are the lower-level execution commands. Under normal operation, they are invoked through `ai-factory-run`, not directly.

```
./run-migration-start         — initialize venture execution context
./run-migration-preflight     — generate batch report from job definitions
./approve-batch-report        — operator approval gate
./run-migration-batch         — execute a full batch
./run-migration-queue         — execute jobs from an approved queue-state
./run-migration-execute       — execute a single migration step
./run-migration-cycle         — start → preflight → approve → queue in one cycle
./classify-migration-job      — classify a job for policy matching
./show-latest-manifest        — display most recent run manifest
```

---

## Execution Policy

Defined in:
```
config/migration-execution-policy.json
```

This is the **single source of truth** for what is permitted to execute. Both `run-migration-queue` and `run-migration-batch` read all policy values from this file. Nothing is hardcoded.

Currently allowed:

| Field | Allowed Values |
|---|---|
| workflow_type | code_migration |
| workflow_spec_version | 1 |
| job_type | migration |
| class | A |
| reason_codes | A_EXACT_PORT, A_SCHEMA_PORT |

---

## Currently Executable

Only one workflow type is executable:

**`code_migration`** — deterministic code migration pipeline

Pipeline:
```
analyzer → planner → coder → apply → reviewer
```

- each stage produces a logged artifact
- only `apply` writes to the target repository
- Guardian runs as a required pre-execution gate inside the execute path

Defined but **not yet executable**:

- `app_build`
- `automation_build`
- `ui_conversion`

These may not appear in the policy file until their infrastructure is built.

---

## Artifact Locations

| Artifact | Location |
|---|---|
| Per-step run manifests | `ventures/<venture>/migration-logs/` |
| Batch reports | `batch-reports/` |
| Queue run records | `queue-runs/` |
| Transition records | `transition-records/` |

Execution artifacts are write-once records. They are never modified after creation.

---

## State Surface

The system's working state is maintained in three files:

| File | Purpose |
|---|---|
| `system-state/current-system-state.md` | Operational snapshot of what is implemented and true |
| `system-state/current-objective.md` | Current objective, next steps, constraints |
| `system-state/authoritative-files.md` | Index of what to read and trust for each decision type |

State surface files are updated only through controlled mechanisms (transition command, reconciliation artifacts). They are never edited casually.

---

## What Is Not Automated

The following remain intentionally operator-driven in the current phase:

- choosing when to run execution (operator runs `ai-factory-run`)
- approving batch reports (`approve-batch-report` requires explicit operator action)
- transitioning between system-building and migration-execution modes (`ai-factory-transition`)
- acknowledging execution outcomes and updating state surface post-execution
- deciding whether a failure warrants a transition back to system-building

The system is controlled. It is not autonomous.

---

## Safety Rules

- **Only `apply` writes to target repos** — all other stages are read-only against target code
- No execution without Guardian pass
- No execution without ECS clear action
- No execution without policy gate pass
- Approval is mandatory before queue execution
- No overwriting without explicit `--force` in execute scripts
- Every run must produce traceable artifacts
- No bypass flags on the operator entrypoint or transition command

---

## Constraints (Non-Negotiable)

- No product source code lives here
- No reusable standards originate here
- No unscoped execution is allowed
- No skipping ECS decisions
- No bypassing Guardian validation
- No direct edits to state surface files outside controlled mechanisms
- No execution of workflow types not present in the policy file
