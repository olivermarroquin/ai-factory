# Authoritative Files

## Purpose

Index of which files are authoritative, which are derived, and which are historical. Prevents reading stale or secondary sources when making execution decisions.

---

## Global Truth Files

These files define what the system is and how it must behave. They are the highest-authority sources.

| File                                     | What it governs                                                                    |
| ---------------------------------------- | ---------------------------------------------------------------------------------- |
| `README.md`                              | System role, entrypoints, execution flow, safety rules                             |
| `docs/current-system-status.md`          | Operational snapshot: what is executable, what is proven, current progress         |
| `docs/workflow-types-policy.md`          | Supported and planned workflow types, what must exist before each can run          |
| `config/migration-execution-policy.json` | Allowed workflow types, job types, spec versions, classes, reason codes — the gate |

**Rule:** If something is not in the policy file, it does not execute. Policy file is the single source of truth for gating.

---

## Workflow / Policy Files

These define the shape and requirements of specific workflows. Authoritative for their domain; do not override global truth files.

| File                                             | What it governs                                                                          |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| `docs/migration-job-classification-policy.md`    | Classification rules for `code_migration` jobs (classes, reason codes, criteria)         |
| `docs/resume-saas-migration-inventory.md`        | Step-by-step inventory of all resume-saas migration targets, with status and assignments |
| `docs/app-build-classification-policy.md`        | Future classification policy for `app_build` (policy only, not yet runnable)             |
| `docs/app-build-job-contract.md`                 | Future job contract for `app_build` (policy only)                                        |
| `docs/automation-build-classification-policy.md` | Future classification policy for `automation_build` (policy only)                        |
| `docs/automation-build-job-contract.md`          | Future job contract for `automation_build` (policy only)                                 |
| `docs/migration-queue-state-spec.md`             | Spec for queue-state file format                                                         |

---

## Execution Artifacts

These files are produced during execution. They are authoritative records of what happened. Do not edit them after they are written.

| Artifact type         | Location                                                           | Authoritative for                                       |
| --------------------- | ------------------------------------------------------------------ | ------------------------------------------------------- |
| Preflight report      | `batch-reports/<ts>_batch-report.json`                             | Job list, classification results, approval status       |
| Queue-state file      | `batch-reports/<ts>_queue-state.json`                              | Current queue position and approval flag                |
| Queue-run record      | `queue-runs/<ts>_queue-run.json`                                   | Per-cycle execution outcome                             |
| Batch-run record      | `batch-runs/<ts>_batch-run.json`                                   | Per-batch execution outcome                             |
| Per-step run manifest | `ventures/<venture>/migration-logs/<date>_step-<NN>_run-<ts>.json` | Per-step artifact paths, stage results, success/failure |
| Stage artifacts       | `ventures/<venture>/migration-logs/<date>_step-<NN>_<stage>.md`    | Output of each pipeline stage for a given run           |

**Rule:** Execution artifacts are write-once records. Re-running requires new artifacts from a new preflight cycle.

---

## Product Planning Files

These files track product migration scope and intent. They are authoritative for what needs to be done, not for how the system runs.

| File                                      | What it governs                                                                                     |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `batch-jobs.json`                         | Operator input file for preflight generation only; not authoritative evidence of execution or state |
| `batch-jobs-resume-saas-phase1.json`      | Phase 1 job definitions for resume-saas                                                             |
| `batch-jobs-resume-saas-phase2.json`      | Phase 2 job definitions for resume-saas                                                             |
| `docs/resume-saas-migration-inventory.md` | Canonical list of all steps, targets, and completion status                                         |

---

## State Surface Files

These files are the system's working memory for human operators and future agents.

| File                                   | What it governs                                       |
| -------------------------------------- | ----------------------------------------------------- |
| `system-state/current-system-state.md` | Operational snapshot for current conversation context |
| `system-state/authoritative-files.md`  | This file — index of what to read and trust           |
| `system-state/current-objective.md`    | Current objective, constraints, and next steps        |

---

## Rules for Using Authoritative Files

1. **Before making any execution decision**, read `config/migration-execution-policy.json`. Do not infer what is allowed from docs or memory.
2. **Before describing system state**, read `docs/current-system-status.md`. Do not rely on conversation history.
3. **Before modifying the job list**, read `docs/resume-saas-migration-inventory.md` to confirm step status.
4. **Execution artifacts are historical records**, not inputs. Do not re-execute from a previous queue-state. Run a fresh preflight.
5. **Policy-only workflow types** (`app_build`, `automation_build`, `ui_conversion`) must never appear in `config/migration-execution-policy.json` until their infrastructure is built.
6. **State surface files** (`system-state/*.md`) are summaries derived from authoritative sources. When they conflict with a primary source, trust the primary source and update the state surface.
7. **When repository reality is found to contradict a state-surface file, create or approve a reconciliation artifact before updating the state surface.** Do not update state files from raw observation alone.
