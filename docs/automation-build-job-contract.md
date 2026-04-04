# Automation Build Job Contract

## Purpose

Define the minimum required fields and constraints for an `automation_build` batch job. This contract is the authoritative reference for any future preflight validator, policy enforcement logic, or execution handler built for the `automation_build` workflow type. Nothing should be implemented for `automation_build` that contradicts this document.

---

## Status

**Not yet executable.**

`automation_build` is a planned workflow type. No preflight validation, batch execution logic, or execution handler exists for it. It must not be added to `allowed_workflow_types` in `migration-execution-policy.json` until all preconditions in this contract are satisfied and the corresponding infrastructure is built.

---

## Minimum Required Fields

| Field | Type | Required | Source |
|---|---|---|---|
| `workflow_type` | string | Yes | Must be explicit |
| `workflow_spec_version` | string | Yes | Must be explicit |
| `job_type` | string | Yes | Must be explicit |
| `automation_name` | string | Yes | Must be explicit |
| `target_repo` | string | Yes | Must be explicit |
| `target_path` | string | Yes | Must be explicit |
| `automation_type` | string | Yes | Must be explicit |
| `runtime` | string | Yes | Must be explicit |
| `goal` | string | Yes | Must be explicit |
| `constraints` | array of strings | Yes | Must be explicit |
| `acceptance_criteria` | array of strings | Yes | Must be explicit |

---

## Field Definitions

### `workflow_type`
- **Type:** string
- **Required value:** `"automation_build"`
- **Purpose:** Identifies this job as an automation build workflow. Used by preflight and policy enforcement to route to the correct validator and allowlist.
- **Must be explicit.** Never inferred.

### `workflow_spec_version`
- **Type:** string
- **Required value:** `"1"` (when version 1 is finalized)
- **Purpose:** Locks the job to a specific contract version so future contract changes do not silently affect old jobs.
- **Must be explicit.** Never inferred.

### `job_type`
- **Type:** string
- **Required value:** `"automation_build"`
- **Purpose:** Identifies the category of work being performed. Used alongside `workflow_type` for policy gating.
- **Must be explicit.** Never inferred.

### `automation_name`
- **Type:** string
- **Purpose:** Human-readable identifier for the automation being built. Used in artifact naming and run records. Must be a valid identifier (no spaces, no special characters).
- **Must be explicit.** Never inferred from goal or target_path.

### `target_repo`
- **Type:** string
- **Purpose:** The name of the target repository under `~/workspace/repos/` where the automation will be written. Must exist before execution begins.
- **Must be explicit.** Never inferred.

### `target_path`
- **Type:** string
- **Purpose:** The path within `target_repo` where the automation file(s) will be written. Relative paths are resolved against the repo root. Must be an empty path or a path that does not yet exist unless the job is explicitly defined as a full deterministic overwrite.
- **Must be explicit.**

### `automation_type`
- **Type:** string
- **Purpose:** Classifies the kind of automation being generated. Determines what validation logic and reviewer checks apply. Allowed values at contract version 1: `"shell_script"`, `"ci_pipeline"`, `"cron_job"`.
- **Must be explicit.** No defaults. Values outside the allowed set are invalid at preflight time.

### `runtime`
- **Type:** string
- **Purpose:** The execution environment the automation will run in (e.g., `"bash"`, `"python3.12"`, `"github-actions"`). Used by the reviewer to verify compatibility between the output and the declared environment.
- **Must be explicit.** Never inferred from automation_type.

### `goal`
- **Type:** string
- **Purpose:** A single concise statement of what the automation must do. Feeds directly into the planner prompt. Must not contain multiple goals or ambiguous scope.
- **Must be explicit.**

### `constraints`
- **Type:** array of strings
- **Purpose:** An explicit list of hard constraints the output must satisfy (e.g., "must not require root privileges", "must be idempotent", "must not modify files outside target_path"). Each constraint must be independently verifiable.
- **Must be explicit.** An empty array is not acceptable — at minimum, scope, file boundary, and privilege constraints must be stated.

### `acceptance_criteria`
- **Type:** array of strings
- **Purpose:** An explicit list of conditions that must be true for the automation to be considered correct. Used by the reviewer stage to assess the output. Each criterion must be independently checkable via static analysis, dry-run, or structural inspection.
- **Must be explicit.** An empty array is not acceptable.

---

## Example Job Shape

```json
{
  "workflow_type": "automation_build",
  "workflow_spec_version": "1",
  "job_type": "automation_build",
  "automation_name": "db-backup-cron",
  "target_repo": "ops-scripts",
  "target_path": "cron/db-backup.sh",
  "automation_type": "shell_script",
  "runtime": "bash",
  "goal": "Write a cron-compatible shell script that backs up a PostgreSQL database to a local directory and rotates backups older than 7 days",
  "constraints": [
    "Must not require root privileges",
    "Must be idempotent — safe to run multiple times in the same day",
    "Must not modify any files outside the backup target directory",
    "Must not include hardcoded credentials"
  ],
  "acceptance_criteria": [
    "Script is valid bash and passes shellcheck with no errors",
    "Backup file is named with a UTC timestamp",
    "Files older than 7 days in the backup directory are deleted",
    "Script exits nonzero on pg_dump failure with a clear error message"
  ]
}
```

---

## Preconditions Before Preflight

The following must all be true before any preflight or execution infrastructure for `automation_build` can be built:

1. `workflow_spec_version: "1"` is finalized — the contract above is stable and reviewed
2. `allowed_workflow_types` in `migration-execution-policy.json` has been extended with an `automation_build` entry
3. `allowed_job_types` has been extended with `"automation_build"`
4. `run-migration-preflight` has been extended to validate all fields in this contract, including the `automation_type` allowlist
5. A planner prompt template exists for each supported `automation_type`
6. A validation stage exists appropriate to the output file type (e.g., shellcheck for `shell_script`, schema validation for `ci_pipeline`)
7. A reviewer stage exists that can evaluate output against `acceptance_criteria` using static analysis or structural inspection
8. A classification system exists for `automation_build` with its own class and reason code definitions
9. Safe apply logic exists that prevents writes outside `target_path`

None of these may be assumed or partially implemented at execution time.

---

## What Is Explicitly Out of Scope

- Automations that require runtime execution to verify correctness (no test runs at scaffold time)
- Automations that register services, modify infrastructure state, or create external resources
- Automations that span multiple files unless all files are within a single `target_path` directory
- Automations that require secrets or credentials at generation time
- Any job that cannot be fully specified by the fields in this contract

---

## Notes

- `automation_type` determines which validator runs at the coder stage. `shell_script` requires shellcheck or equivalent. `ci_pipeline` requires schema validation against the target CI platform's format. `cron_job` requires cron syntax validation plus a shell validator for the underlying script.
- `runtime` and `automation_type` are independent fields. A `ci_pipeline` that runs `python3.12` steps must declare both.
- `target_path` must be verified as empty or nonexistent at preflight time, not at execution time, unless the job explicitly declares a full deterministic overwrite.
- `acceptance_criteria` must be statically or structurally checkable. Criteria that require a live system to verify (e.g., "backup actually succeeds against a running database") are out of scope for the reviewer stage and must not be included.
- This contract governs version `"1"` only. A `workflow_spec_version: "2"` job must be governed by a separate contract document.
