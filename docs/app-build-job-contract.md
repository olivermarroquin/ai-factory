# App Build Job Contract

## Purpose

Define the minimum required fields and constraints for an `app_build` batch job. This contract is the authoritative reference for any future preflight validator, policy enforcement logic, or execution handler built for the `app_build` workflow type. Nothing should be implemented for `app_build` that contradicts this document.

---

## Status

**Not yet executable.**

`app_build` is a planned workflow type. No preflight validation, batch execution logic, or execution handler exists for it. It must not be added to `allowed_workflow_types` in `migration-execution-policy.json` until all preconditions in this contract are satisfied and the corresponding infrastructure is built.

---

## Minimum Required Fields

| Field | Type | Required | Source |
|---|---|---|---|
| `workflow_type` | string | Yes | Must be explicit |
| `workflow_spec_version` | string | Yes | Must be explicit |
| `job_type` | string | Yes | Must be explicit |
| `app_name` | string | Yes | Must be explicit |
| `target_repo` | string | Yes | Must be explicit |
| `target_path` | string | Yes | Must be explicit |
| `stack` | object | Yes | Must be explicit |
| `goal` | string | Yes | Must be explicit |
| `constraints` | array of strings | Yes | Must be explicit |
| `acceptance_criteria` | array of strings | Yes | Must be explicit |

---

## Field Definitions

### `workflow_type`
- **Type:** string
- **Required value:** `"app_build"`
- **Purpose:** Identifies this job as an app build workflow. Used by preflight and policy enforcement to route to the correct validator and allowlist.
- **Must be explicit.** Never inferred.

### `workflow_spec_version`
- **Type:** string
- **Required value:** `"1"` (when version 1 is finalized)
- **Purpose:** Locks the job to a specific contract version so future contract changes do not silently affect old jobs.
- **Must be explicit.** Never inferred.

### `job_type`
- **Type:** string
- **Required value:** `"app_build"`
- **Purpose:** Identifies the category of work being performed. Used alongside `workflow_type` for policy gating.
- **Must be explicit.** Never inferred.

### `app_name`
- **Type:** string
- **Purpose:** Human-readable identifier for the application being built. Used in artifact naming and run records.
- **Must be explicit.** Must be a valid identifier (no spaces, no special characters).

### `target_repo`
- **Type:** string
- **Purpose:** The name of the target repository under `~/workspace/repos/` where the application will be scaffolded. Must exist before execution begins.
- **Must be explicit.** Never inferred from app_name.

### `target_path`
- **Type:** string
- **Purpose:** The path within `target_repo` where the application will be written. Relative paths are resolved against the repo root. Must be an empty directory or a path that does not yet exist.
- **Must be explicit.**

### `stack`
- **Type:** object
- **Purpose:** Defines the technology stack for the application. Minimum required subfields: `language`, `framework`. Additional subfields (e.g., `runtime`, `database`) are optional but must be explicit if provided.
- **Must be explicit.** No defaults are assumed.

### `goal`
- **Type:** string
- **Purpose:** A single concise statement of what the application must do. Feeds directly into the planner prompt. Must not contain multiple goals or ambiguous scope.
- **Must be explicit.**

### `constraints`
- **Type:** array of strings
- **Purpose:** An explicit list of hard constraints the output must satisfy (e.g., "no external dependencies beyond the standard library", "must expose a REST API on port 8080"). Each constraint must be independently verifiable.
- **Must be explicit.** An empty array is not acceptable — at minimum, scope and file boundary constraints must be stated.

### `acceptance_criteria`
- **Type:** array of strings
- **Purpose:** An explicit list of conditions that must be true for the output to be considered correct. Used by the reviewer stage to assess the built application. Each criterion must be independently checkable.
- **Must be explicit.** An empty array is not acceptable.

---

## Example Job Shape

```json
{
  "workflow_type": "app_build",
  "workflow_spec_version": "1",
  "job_type": "app_build",
  "app_name": "invoice-parser",
  "target_repo": "tools-internal",
  "target_path": "apps/invoice-parser",
  "stack": {
    "language": "python",
    "framework": "none",
    "runtime": "3.12"
  },
  "goal": "Build a CLI tool that parses PDF invoices and outputs line items as JSON",
  "constraints": [
    "No external dependencies beyond the Python standard library and pdfplumber",
    "Must not modify any existing files in the repo",
    "Output must write to stdout only"
  ],
  "acceptance_criteria": [
    "Accepts a PDF file path as a CLI argument",
    "Outputs a JSON array of line items with keys: description, quantity, unit_price, total",
    "Exits nonzero on parse failure with a clear error message"
  ]
}
```

---

## Preconditions Before Preflight

The following must all be true before any preflight or execution infrastructure for `app_build` can be built:

1. `workflow_spec_version: "1"` is finalized — the contract above is stable and reviewed
2. `allowed_workflow_types` in `migration-execution-policy.json` has been extended with an `app_build` entry
3. `allowed_job_types` has been extended with `"app_build"`
4. `run-migration-preflight` has been extended to validate all fields in this contract
5. A planner prompt template exists for `app_build` jobs
6. A multi-file apply stage exists that can safely write to `target_path` within `target_repo`
7. A reviewer stage exists that can evaluate output against `acceptance_criteria`
8. A classification system exists for `app_build` with its own class and reason code definitions

None of these may be assumed or partially implemented at execution time.

---

## What Is Explicitly Out of Scope

- Incremental or iterative app builds (one job = one complete scaffold)
- Builds that span multiple target repos
- Builds that modify existing files in the target repo
- Builds with external API calls at scaffold time
- Any job that cannot be fully specified by the fields in this contract

---

## Notes

- `stack.language` is the only field that affects validation logic (e.g., AST parsing is language-specific). All other stack fields are passed through to the planner prompt unchanged.
- `target_path` must be verified as empty or nonexistent at preflight time, not at execution time.
- `acceptance_criteria` is the reviewer's input. If the reviewer cannot check a criterion programmatically or structurally, it must be flagged as out of scope before the job is approved.
- This contract governs version `"1"` only. A `workflow_spec_version: "2"` job must be governed by a separate contract document.
