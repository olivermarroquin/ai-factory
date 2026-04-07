# Rewrite API Spec v1

## Purpose

Define the contract for `backend/api/rewrite.py`: a single synchronous HTTP endpoint that accepts a resume and a job description and returns a list of structured edit proposals. This spec is the authoritative contract for implementation. No code is written until this spec is reviewed and accepted.

---

## Scope

This spec covers exactly one endpoint: `POST /rewrite`.

It does not cover resume parsing, job description parsing, authentication, persistence, background processing, or any other endpoint.

---

## Endpoint

```
POST /rewrite
Content-Type: application/json
```

Synchronous. Returns a JSON response body. No side effects. No persistence.

---

## Request Shape

```json
{
  "resume_text": "<string>",
  "job_description": "<string>"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `resume_text` | string | Yes | Full plain-text content of the current resume |
| `job_description` | string | Yes | Full plain-text content of the target job description |

Additional fields are rejected. Both `resume_text` and `job_description` are passed directly to `backend/services/rewrite_orchestrator_v5.py` without transformation, matching the current service interface.

---

## Response Shape

### 200 OK

```json
{
  "proposals": [
    {
      "id": 1,
      "section": "SUMMARY",
      "op": "REPLACE_LINE",
      "before": ["<original line>"],
      "after": ["<replacement line>"],
      "rationale": "<reason for this edit>"
    }
  ],
  "narrative": "<optional high-level summary of proposed changes>"
}
```

| Field | Type | Always present | Description |
|---|---|---|---|
| `proposals` | array | Yes | Ordered list of edit proposals. May be empty `[]` if no changes are proposed. |
| `narrative` | string | No | Optional high-level summary of the proposed changes. May be absent. |

**Proposal object fields:**

| Field | Type | Required | Allowed values |
|---|---|---|---|
| `id` | integer | Yes | `id` is a deterministic integer assigned by the API layer. Exact sequencing behavior is implementation-defined in v1. |
| `section` | string | Yes | `SUMMARY`, `SKILLS`, `EXPERIENCE` |
| `op` | string | Yes | `REPLACE_LINE`, `ADD_LINE`, `DELETE_LINE`, `REPLACE_PHRASE` |
| `before` | array of strings | Yes | Non-empty list of non-empty strings. Length 1 for `REPLACE_LINE` and `REPLACE_PHRASE`. |
| `after` | array of strings | Yes | Non-empty list of non-empty strings. For `DELETE_LINE`, must be `[""]`. Length 1 for `REPLACE_LINE` and `REPLACE_PHRASE`. |
| `rationale` | string | Yes | Non-empty string explaining the edit |

Proposal field semantics are defined by and validated against `backend/schemas/proposal_schema.py`.

---

## Validation Rules

Applied at the API boundary before calling any backend service:

1. Request body must be valid JSON.
2. `resume_text` must be present and a non-empty string (after stripping whitespace).
3. `job_description` must be present and a non-empty string (after stripping whitespace).
4. No further input validation at the API layer — downstream service validates proposal output.

Response proposals are validated by `backend/schemas/proposal_schema.validate_proposals()` before the response is returned. If validation fails, the endpoint returns 500 (see Error Cases).

---

## Error Cases

| Condition | Status | Response body |
|---|---|---|
| Request body is not valid JSON | 400 | `{ "error": "invalid_json", "message": "Request body must be valid JSON." }` |
| `resume_text` missing or empty | 400 | `{ "error": "missing_field", "message": "resume_text is required and must be non-empty." }` |
| `job_description` missing or empty | 400 | `{ "error": "missing_field", "message": "job_description is required and must be non-empty." }` |
| Backend service raises an exception | 500 | `{ "error": "service_error", "message": "Rewrite service failed." }` |
| Proposal output fails schema validation | 500 | `{ "error": "invalid_output", "message": "Rewrite service returned invalid proposals." }` |

No other error shapes are defined in v1.

---

## Dependencies

| Dependency | Role |
|---|---|
| `backend/schemas/proposal_schema.py` | Defines `ALLOWED_SECTIONS`, `ALLOWED_OPS`, `Proposal` dataclass, and `validate_proposals()`. The API response shape is derived directly from this schema. |
| `backend/services/rewrite_orchestrator_v5.py` | Called to produce the rewrite output. The orchestrator is responsible for calling the AI model and producing the raw proposal payload. The API layer does not call the model directly. |

The implementation must call the orchestrator, receive the raw output, validate it with `validate_proposals()`, and return the validated proposals as the response body.

---

## Non-Goals

The following are explicitly out of scope for this spec and this implementation:

- Authentication or authorization
- Persistence of resume text, job descriptions, or proposals
- Background job execution or async processing
- Queue integration
- File upload (resume or JD must be provided as plain text in the request body)
- Resume parsing from PDF or other formats
- `backend/api/resume.py` or `backend/api/jobs.py`
- Multiple endpoint variants (v2, streaming, etc.)
- Rate limiting
- Applying proposals to the resume (apply is a separate operation, not defined here)

---

## Exit Condition

This spec is complete when:

1. `docs/rewrite-api-spec-v1.md` is written and reviewed.
2. The spec is accepted as the contract for `backend/api/rewrite.py`.
3. Implementation of `backend/api/rewrite.py` begins only after acceptance.
