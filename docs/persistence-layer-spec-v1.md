# Persistence Layer Spec v1

## Purpose

Define the purpose of introducing persistence into the current backend system.

The current backend is request/response only and does not persist outputs. Each handler processes a request, calls a service, and returns a response — no record of the operation is retained after the response is sent.

This spec defines:

- what must be persisted
- when it must be persisted
- what behavior must remain unchanged

This is a specification document only. Storage technology, implementation details, and file layout are not defined here.

---

## Current State

The following API slices exist and are fully validated:

- Rewrite API slice (`POST /rewrite`) — implemented, tested, Flask-wired, end-to-end confirmed
- Resume API slice (`POST /resume/parse`) — implemented, tested, Flask-wired, end-to-end confirmed
- Jobs API slice (`POST /jobs/parse`) — implemented, tested, Flask-wired, end-to-end confirmed

The following system-level improvements are also implemented and validated:

- App routing and application factory pattern (`create_app()`)
- App-level request logging (`after_request` hook)
- Handler-level exception logging (`logger.exception()` in all three handler files)
- Config integration (`backend/config.py`, `LOG_LEVEL` resolution)

No persistence layer exists yet.

No existing stored-record contract exists yet.

---

## Minimal Use Cases

This spec defines only three use cases for v1:

1. Persist a successful rewrite operation result
2. Persist a successful resume parse result
3. Persist a successful job description parse result

Explicitly excluded from v1:

- No read or query use case is included in v1
- No update or delete use case is included in v1
- No user or account-scoped persistence is included in v1

---

## Required Persisted Record Types

### A. Rewrite Record

Represents one successful rewrite request and its produced output.

Required fields:

- `record_id` — uniquely identifies this persisted record
- `resume_text` — the validated resume text used in this request
- `job_description` — the validated job description used in this request
- `rewrite_result` — the successful output returned by the rewrite handler flow
- `created_at` — captures when this successful operation was recorded

---

### B. Resume Parse Record

Represents one successful resume parse request and its produced output.

Required fields:

- `record_id` — uniquely identifies this persisted record
- `resume_text` — the validated resume text used in this request
- `parsed_resume` — the successful output returned by the resume parse handler flow
- `created_at` — captures when this successful operation was recorded

---

### C. Job Parse Record

Represents one successful job description parse request and its produced output.

Required fields:

- `record_id` — uniquely identifies this persisted record
- `job_description` — the validated job description used in this request
- `parsed_terms` — the successful output returned by the job parse handler flow
- `created_at` — captures when this successful operation was recorded

---

## Record Requirements

- `record_id` must uniquely identify a persisted record
- `created_at` must capture when the successful operation was recorded
- Stored request fields must reflect the validated request content actually used by the handler
- Stored output fields must reflect the successful service result actually returned by the handler flow
- This spec defines required record contents only, not storage representation

---

## Write Behavior

Persistence must occur under the following conditions only:

- Persistence is required only for successful handler executions
- A successful handler execution means the handler returns a success response for the requested operation
- Persistence must occur after successful service-layer completion
- Persistence must not change the existing API response contract
- Persistence is part of backend processing responsibility, but not part of the public response schema

---

## Failure Behavior

When persistence cannot complete:

- Persistence failure must not change an otherwise successful API result into a failure response
- Existing handler success contracts must remain unchanged
- Persistence failure must be observable through logging
- Persistence failure handling must not swallow or alter existing service-level error behavior
- Failed requests and validation errors are not persisted

---

## Boundaries

This spec explicitly does not:

- Choose a storage technology
- Define a database schema
- Define ORM models or data classes
- Define file layout or module structure
- Define repository or service implementation details
- Add new API endpoints
- Change request validation rules
- Change success or error response shapes

---

## Non-Goals

- Selecting a storage backend
- Defining implementation classes or modules
- Designing read, query, or search endpoints
- Authentication or authorization
- Multi-user or tenant isolation
- Data retention policy
- Search, indexing, analytics, or reporting
- Background processing, retries, or async workflows

---

## Validation Expectations

Once a separate persistence scope document and implementation exist, the following must be proven:

- A successful rewrite operation produces one persisted Rewrite Record
- A successful resume parse operation produces one persisted Resume Parse Record
- A successful job parse operation produces one persisted Job Parse Record
- `400` responses do not create persisted records
- `500` service-error responses do not create persisted records
- Persistence failure does not alter the existing success response contract
- Persistence failures are logged
- Existing API request/response behavior remains unchanged

---

## Exit Condition

This spec is complete when:

- Persistence responsibilities are clearly defined
- Required record types and fields are explicitly defined
- Write and failure behavior are explicit
- Boundaries and non-goals are explicit
- The system is ready for a separate persistence scope document

No implementation has begun under this spec alone.
