# AI Factory

## Purpose

AI Factory is the **execution and orchestration layer** of the system.

It runs **controlled, state-driven workflows** under strict policy and validation rules.

This is not a code repository or knowledge base — it is the system responsible for:

- executing work
- enforcing correctness
- coordinating workflows across projects
- preventing drift and invalid actions

---

## System Role

AI Factory operates within a larger system:

- **second-brain / knowledge OS** → thinking, structured knowledge, long-term intelligence
- **repos (e.g., resume-saas)** → source code and product implementations
- **ai-agency-core** → reusable standards, prompts, templates
- **ai-factory** → execution, orchestration, validation, and control

AI Factory does not own ideas or code — it **executes and governs them**.

---

## System Model (Non-Negotiable)

All work follows a strict execution model:
state → decision → spec → scope → review → implement → validate → update state

Key rules:

- No work begins without an **explicit state selection**
- No implementation occurs without a **defined and accepted scope**
- Every step must produce **validation evidence**
- State must be updated after every completed phase

This model is enforced by system components below.

---

## Core Systems

### Execution Control System (ECS)

ECS determines **what happens next**.

Responsibilities:

- reads current system state
- evaluates allowed transitions
- outputs the next valid action

Entrypoint:
python3 tools/ecs/resolve_next_action.py

ECS guarantees:

- no arbitrary execution
- no skipped steps
- deterministic progression

---

### System Guardian

System Guardian validates **whether actions are allowed and complete**.

Responsibilities:

- detects stale or inconsistent state
- blocks invalid transitions
- ensures required artifacts exist
- verifies validation evidence before progression

Guardian enforces:

- no silent failures
- no missing steps
- no invalid system transitions

---

## Current Capabilities

The system has fully implemented and validated:

### API Slices (resume-saas)

- rewrite API (spec → tests → route → app wiring)
- resume API (spec → tests → route → app wiring)
- jobs API (spec → tests → route → app wiring)

### Backend Structure

- Flask routing via Blueprints
- `create_app()` application factory pattern
- app-level request logging (method, path, status)
- handler-level exception logging with full traceback

All routes:

- fully tested
- validated end-to-end
- aligned with strict API contracts

---

## Code Migration System (Current Primary Workflow)

AI Factory currently executes **deterministic code migration workflows**.

Pipeline:
analyzer → planner → coder → apply → reviewer

- Each stage produces a logged artifact
- Only **apply** writes to the target repository
- Every stage is validated before progression

---

### Repo-root Entrypoints

./run-migration-start
./run-migration-execute
./run-migration-preflight
./approve-batch-report
./run-migration-batch
./run-migration-queue
./run-migration-cycle
./classify-migration-job
./show-latest-manifest

---

### Controlled Execution Flow

1. run-migration-start
2. run-migration-preflight
3. approve-batch-report
4. run-migration-cycle

Key rules:

- approval is mandatory
- no execution from unapproved state
- queue execution is policy-gated

---

### Execution Policy

Defined in:
config/migration-execution-policy.json

Controls:

- allowed job types
- allowed workflow types
- allowed classes and reason codes

---

### Reason Codes

| Code          | Meaning                            |
| ------------- | ---------------------------------- |
| A_EXACT_PORT  | Deterministic function/module port |
| A_SCHEMA_PORT | Schema/model extraction only       |

---

### Artifact Locations

Migration artifacts:
ventures/<venture>/migration-logs/

Batch + queue:
batch-reports/
queue-runs/

---

### Current Progress (resume-saas)

| Step | Target                     | Reason Code   | Status    |
| ---- | -------------------------- | ------------- | --------- |
| 17   | rewrite_orchestrator_v5.py | A_EXACT_PORT  | Completed |
| 18   | proposal_schema.py         | A_SCHEMA_PORT | Completed |

---

## Safety Rules

- **Only `apply` writes to target repos**
- No execution without approval
- All stages must validate before proceeding
- No overwriting without explicit `--force`
- Every run must produce traceable artifacts

---

## Supported Workflow Types (System-Level)

Currently executable:

- code_migration

Defined but not yet executable:

- app_build
- automation_build
- ui_conversion

Future:

- all workflows must conform to ECS + Guardian enforcement

---

## Future Direction (Critical)

AI Factory is evolving into a **general-purpose execution system** for:

- migrations
- app builds
- automation systems
- multi-step AI workflows

All future workflows must:

- be state-driven
- be spec/scoped before execution
- produce validation evidence
- pass Guardian validation

---

## Constraints (Non-Negotiable)

- No product source code lives here
- No reusable standards originate here
- No unscoped execution is allowed
- No skipping ECS decisions
- No bypassing validation steps

Everything must support:

- execution
- correctness
- scalability
- future automation

---

## Exit Condition

This README is accurate when:

- AI Factory is clearly defined as the execution layer
- ECS and Guardian roles are explicit
- migration system is fully documented
- system constraints are enforced
- future workflow direction is clear
