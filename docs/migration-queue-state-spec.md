# Migration Queue State Spec

## Purpose

Define the queue state file format and job lifecycle for the `code_migration` controlled execution system. This spec is the authoritative reference for any future coordinator, worker, or operator tool that needs to track the state of migration jobs across the pipeline. It replaces ad hoc file chaining (preflight report → batch run record → manifest) with a single, durable per-queue state object.

---

## Status

**Implemented.**

Queue state files are written by `run-migration-preflight`, updated by `approve-batch-report`, and consumed by `run-migration-queue`. Queue run records are written to `queue-runs/` by `run-migration-queue`.

---

## Queue State Object

A queue state file is a single JSON file per batch. It lives alongside the preflight report that originated the batch.

**Location:**
```
batch-reports/<timestamp>_queue-state.json
```

The queue state file is created when a preflight report is generated and updated in place as the batch progresses. It is never deleted or rotated — it is the durable record of the batch lifecycle.

**Top-level fields:**

| Field | Type | Description |
|---|---|---|
| `schema_version` | string | Queue state schema version. Must be `"1"` for this spec. |
| `created_at_utc` | string | UTC timestamp when the queue state file was first created. |
| `updated_at_utc` | string | UTC timestamp of the last state update. |
| `source_preflight_report` | string | Absolute path to the preflight report this queue was derived from. |
| `batch_status` | string | Aggregate status of the batch. One of: `pending`, `approved`, `executing`, `succeeded`, `failed`, `blocked`. |
| `jobs` | array | Array of per-job state objects. |

---

## Per-Job State Fields

Each entry in `jobs` represents one migration job and its current state.

| Field | Type | Required | Description |
|---|---|---|---|
| `workflow_type` | string | Yes | Must be `"code_migration"` |
| `workflow_spec_version` | string | Yes | Must be `"1"` |
| `job_type` | string | Yes | Must be `"migration"` |
| `venture` | string | Yes | Venture name |
| `step` | integer | Yes | Migration step number |
| `date` | string | Yes | Run date in YYYY-MM-DD format |
| `expected_class` | string | Yes | Class declared in the batch job file |
| `actual_class` | string | Yes | Class determined by preflight classifier |
| `classification_reason_code` | string | Yes | Reason code from preflight classifier |
| `status` | string | Yes | Current job status (see allowed values below) |
| `preflight_report_path` | string | Yes | Absolute path to the preflight report that assessed this job |
| `approval_timestamp` | string or null | Yes | UTC timestamp when the batch report was approved; null if not yet approved |
| `latest_run_manifest_path` | string or null | Yes | Absolute path to the most recent per-step run manifest; null if not yet executed |
| `latest_queue_run_record_path` | string or null | Yes | Absolute path to the queue-run record written by `run-migration-queue`; null if not yet executed |

---

## Allowed Job Status Values

| Status | Meaning |
|---|---|
| `pending` | Job is in the queue but preflight has not been run |
| `preflight_ready` | Preflight completed; job is assessed and waiting for approval |
| `approved` | Batch report has been approved; job is authorized to execute |
| `executing` | Job is currently being executed by the batch runner |
| `succeeded` | Job completed execution successfully; run manifest confirms success |
| `failed` | Job execution failed; run manifest records the failed stage |
| `blocked` | Job was blocked by the batch runner due to policy gate failure (class mismatch, reason code not allowed, etc.) |

---

## State Transitions

Only the following transitions are valid. Any other transition is a state machine violation.

```
pending
  └─> preflight_ready    (preflight report generated; job assessed)

preflight_ready
  └─> approved           (batch report approved via approve-batch-report)

approved
  └─> executing          (batch runner begins executing this job)

executing
  └─> succeeded          (run-migration-execute completed; run manifest status = "success")
  └─> failed             (run-migration-execute failed; run manifest records failed_stage)
  └─> blocked            (batch runner halted before execution due to policy gate failure)
```

**Transition rules:**
- A job must not move from `approved` to `executing` unless `actual_class` is in `allowed_classes` and `classification_reason_code` is in `allowed_reason_codes` per the current policy file.
- A job must not move from `executing` to `succeeded` unless a valid run manifest exists at `latest_run_manifest_path` with `status = "success"`.
- A job must not skip states. A `pending` job cannot move directly to `approved`.
- Once a job reaches `succeeded`, `failed`, or `blocked`, it must not be transitioned again without operator intervention and a new batch cycle.

---

## Source of Truth Rules

1. The queue state file is the single source of truth for job status within a batch cycle.
2. Preflight reports, batch run records, and run manifests are the underlying evidence. The queue state file summarizes and indexes them; it does not replace them.
3. If the queue state file and a run manifest disagree on job outcome, the run manifest is authoritative for that job's execution result. The queue state file must be corrected to match.
4. The queue state file must be updated atomically — write to a temp file, then rename — to prevent partial writes from corrupting state.
5. A queue state file with `batch_status = "executing"` and no `updated_at_utc` change in more than a configurable timeout period must be treated as stale by any operator tool. No automatic recovery is defined at this time.

---

## Notes

- `batch_status` is derived from the aggregate of per-job statuses. If any job is `failed` or `blocked`, `batch_status` is `failed`. If all jobs are `succeeded`, `batch_status` is `succeeded`. If any job is `executing`, `batch_status` is `executing`.
- `approval_timestamp` is copied from the preflight report's `approved_at_utc` field at the time the queue state transitions to `approved`. It is not re-read from the report after that point.
- `latest_run_manifest_path` and `latest_queue_run_record_path` are nullable until execution occurs. On failure, they must still be populated if the coordinator wrote any artifacts before halting. `latest_queue_run_record_path` points to a file under `queue-runs/` written by `run-migration-queue`, not `batch-runs/`.
- This spec governs `schema_version: "1"` only. A schema change requires a new spec version.
- The queue state file is intended for operator and coordinator use. Individual pipeline scripts (`run-migration-execute`, `run-migration-batch`) must not depend on it — they write their own manifests and run records. The queue state file reads from those; it does not replace them.
