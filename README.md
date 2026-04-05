# AI Factory

## Purpose

AI Factory is the execution and orchestration layer of the workspace. It runs controlled, policy-gated workflows — currently focused on deterministic code migration.

## Role in System

- second-brain = thinking and documentation
- repos = source code
- ai-agency-core = reusable standards, prompts, templates
- ai-factory = execution and orchestration

## Rules

- product source code does not live here
- reusable standards do not originate here
- this layer wraps, runs, and coordinates work
- each venture should have a clear execution folder

---

## Code Migration System

Automates multi-stage code migration across repos using a structured pipeline:
**analyzer → planner → coder → apply → reviewer**

Each stage produces a logged artifact. The only stage that writes to the target repo is **apply**.

Only `code_migration` jobs are executable through the controlled pipeline right now. `app_build`, `automation_build`, and `ui_conversion` are policy-defined but not yet runnable.

### Repo-root entrypoints

```
./run-migration-start      # Scaffold prompt and artifact files for a new step
./run-migration-execute    # Execute a migration step (auto or manual)
./run-migration-preflight  # Assess a batch jobs file, generate report + queue state
./approve-batch-report     # Mark a preflight report approved for execution
./run-migration-batch      # Execute from an approved preflight report
./run-migration-queue      # Execute from an approved queue-state file (coordinator)
./run-migration-cycle      # Full cycle wrapper: preflight or approved execution
./classify-migration-job   # Classify a single step without executing
./show-latest-manifest     # Print the newest run manifest for a venture + step
```

### Controlled execution flow

```
1. run-migration-start      → scaffold artifacts for a new step
2. run-migration-preflight  → assess jobs, generate batch-report + queue-state
3. approve-batch-report     → set approved=true, advance queue-state to approved
4. run-migration-cycle      → execute approved queue (via run-migration-queue)
```

- `run-migration-batch` executes from an approved preflight report directly.
- `run-migration-queue` executes from an approved queue-state file with policy enforcement.
- `run-migration-cycle` is the single operator entrypoint that wraps both preflight and queue execution.
- Approval is a required explicit gate. Nothing executes from an unapproved report.

### Execution policy

Policy lives in `config/migration-execution-policy.json`. It controls:
- allowed job types, workflow types, workflow spec versions
- allowed classes (currently: A only)
- allowed reason codes (currently: `A_EXACT_PORT`, `A_SCHEMA_PORT`)

### Reason codes

| Code | Meaning |
|---|---|
| `A_EXACT_PORT` | Deterministic function/module port with required imports and signatures |
| `A_SCHEMA_PORT` | Schema/dataclass/model extraction only, no business logic |

### Artifact locations

All migration artifacts are written to:
```
ventures/<venture>/migration-logs/<date>_step-<NN>_<artifact>.md
```

Preflight reports and queue-state files:
```
batch-reports/<timestamp>_batch-report.json
batch-reports/<timestamp>_queue-state.json
```

Queue run records:
```
queue-runs/<timestamp>_queue-run.json
```

### Current product progress — resume-saas

Steps 17 and 18 are the first real product migrations completed through the controlled queue:

| Step | Target | Reason Code | Status |
|---|---|---|---|
| 17 | `backend/services/rewrite_orchestrator_v5.py` | `A_EXACT_PORT` | Completed 2026-04-05 |
| 18 | `backend/schemas/proposal_schema.py` | `A_SCHEMA_PORT` | Completed 2026-04-05 |

### Safety rules

- **apply is the only stage that writes to the target repo.**
- Planner, coder, and reviewer outputs are each validated before the next stage runs.
- Use `--force` to overwrite existing artifacts intentionally.
- A fresh preflight + approval cycle is required before re-executing any queue.
