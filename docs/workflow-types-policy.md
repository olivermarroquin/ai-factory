# Workflow Types Policy

## Purpose

Define the supported and planned workflow types for the controlled execution system. This policy governs what may be executed via `run-migration-batch`, what is gated by preflight and approval, and what is not yet runnable. It is the authoritative reference for expanding the system beyond code migration.

---

## Current Supported Workflow Types

### code_migration

| Field | Value |
|---|---|
| `workflow_type` | `code_migration` |
| `workflow_spec_version` | `1` |
| `job_type` | `migration` |
| Status | **Executable** |

A code migration job ports or transforms a single Python source file into a new target file using the analyzer → planner → coder → apply → reviewer pipeline. Execution is fully automated when the job is classified as Class A with reason code `A_EXACT_PORT`.

**Execution path:** `run-migration-preflight` → `approve-batch-report` → `run-migration-batch` → `run-migration-execute --mode auto-openai`

**Artifacts produced:** analyzer output, planner output, coder output, reviewer output, applied target file, run manifest, batch run record.

---

## Planned Workflow Types (Policy Only)

The following workflow types are defined as policy placeholders. They are not yet runnable. No execution code, preflight logic, or policy enforcement exists for them. They must not be added to `allowed_workflow_types` in `migration-execution-policy.json` until their execution infrastructure is complete.

---

### app_build

**Intended purpose:** Scaffold or build a new application from a structured specification, producing a complete runnable codebase rather than transforming an existing file.

**What it would eventually build:** Full application directories, entrypoints, configuration files, and initial test structure across potentially multiple target files.

**What must exist before it can execute safely:**
- A defined app specification format and version
- A multi-file planner that can scope work across a directory tree without drift
- Target directory safety checks (empty or explicitly overwrite-approved)
- A reviewer stage capable of validating multi-file output coherence
- An updated classification system with app_build-specific classes and reason codes
- Policy entries in `migration-execution-policy.json` for its allowed classes and reason codes

**Status: Not yet runnable. Do not add to allowed_workflow_types.**

---

### automation_build

**Intended purpose:** Generate automation scripts, pipelines, or scheduled task definitions from a structured specification.

**What it would eventually build:** Shell scripts, CI/CD configuration files, cron definitions, or task runner files targeting a specific automation goal.

**What must exist before it can execute safely:**
- A defined automation specification format and version
- Validation logic appropriate to the target file type (not Python-only AST)
- A reviewer stage capable of assessing automation scripts for correctness and safety
- Explicit scope constraints preventing unintended modification of shared infrastructure files
- Policy entries for its allowed classes and reason codes

**Status: Not yet runnable. Do not add to allowed_workflow_types.**

---

### ui_conversion

**Intended purpose:** Convert UI component files from one framework, language, or pattern to another while preserving visual and behavioral intent.

**What it would eventually build:** Converted component files (e.g., Vue to React, class component to functional component) with equivalent structure and props.

**What must exist before it can execute safely:**
- A source/target framework pair specification
- A planner that can reason about component structure without inventing new behavior
- Validation logic for the target language (TypeScript AST, JSX structure, etc.)
- A reviewer stage that can compare source and target component interfaces
- A definition of "exact port" equivalent for UI components (no new props, no logic changes)
- Policy entries for its allowed classes and reason codes

**Status: Not yet runnable. Do not add to allowed_workflow_types.**

---

## Common Control Requirements

All workflow types, once executable, must pass through the same control pipeline:

| Stage | Requirement |
|---|---|
| Preflight | Job fields validated, classification performed, status and execution_allowed computed |
| Approval | Report must have `approved: true` before batch execution |
| Policy gating | `workflow_type`, `workflow_spec_version`, `job_type`, class, and reason code must all be in their respective allowlists |
| Execution artifacts | Each stage must produce a logged artifact |
| Failure manifests | Any failure must write a manifest recording the failed stage and context |
| Batch run record | Every batch execution must produce a `batch-runs/` JSON record |

These requirements are non-negotiable. A workflow type that cannot satisfy all of them is not ready for execution.

---

## What Is Not Yet Supported

- Multi-file apply in a single job
- Parallel job execution within a batch
- Partial batch recovery (resume from failed step)
- Cross-venture batches
- Human-in-the-loop apply confirmation within an automated batch
- Any workflow type other than `code_migration`

---

## Notes

- `workflow_spec_version` is a string, not an integer. Version `"1"` is the only valid value for `code_migration` at this time.
- Adding a new workflow type requires: a policy entry, a preflight validation path, an execution handler in or alongside `migration_execute.py`, and a reviewer stage appropriate to the output type.
- Class A / `A_EXACT_PORT` semantics are specific to `code_migration`. Planned workflow types must define their own classification semantics before they can use the batch runner.
- When in doubt, add to this document before writing code.
