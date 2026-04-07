# Jobs API Spec v1

## Purpose

Define the contract for `backend/api/jobs.py`: a single synchronous HTTP endpoint that accepts a job description as plain text and returns an extracted list of skill terms. This spec is the authoritative contract for implementation. No code is written until this spec is reviewed and accepted.

---

## Scope

This spec covers exactly one endpoint: `POST /jobs/parse`.

It does not cover resume parsing, rewrite proposals, authentication, persistence, file upload, background processing, or any other endpoint.

---

## Endpoint

```
POST /jobs/parse
Content-Type: application/json
```

Synchronous. Returns a JSON response body. No side effects. No persistence.

---

## Request Shape

```json
{
  "job_description": "<string>"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `job_description` | string | Yes | Full plain-text content of the job description |

Additional fields are rejected. `job_description` is passed to `backend/services/jd_parser.extract_jd_terms()` after normalization inside the service.

---

## Response Shape

### 200 OK

```json
{
  "terms": ["<skill_term>", ...]
}
```

| Field | Type | Always present | Description |
|---|---|---|---|
| `terms` | array of strings | Yes | Ordered list of extracted skill/technology terms. May be empty `[]` if no terms are detected. |

The `terms` array reflects the output of `extract_jd_terms()` directly. The API layer does not filter, sort, or transform the terms beyond returning them.

---

## Validation Rules

Applied at the API boundary before calling any backend service:

1. Request body must be valid JSON.
2. `job_description` must be present and a non-empty string (after stripping whitespace).
3. Additional fields are rejected.
4. No further input validation at the API layer — term extraction heuristics are handled entirely inside the service.

---

## Error Cases

| Condition | Status | Response body |
|---|---|---|
| Request body is not valid JSON | 400 | `{ "error": "invalid_json", "message": "Request body must be valid JSON." }` |
| `job_description` missing or empty | 400 | `{ "error": "missing_field", "message": "job_description is required and must be non-empty." }` |
| Additional fields present | 400 | `{ "error": "invalid_json", "message": "Request body must be valid JSON." }` |
| Backend service raises an exception | 500 | `{ "error": "service_error", "message": "Job description parse service failed." }` |

No other error shapes are defined in v1.

---

## Dependencies

| Dependency | Role |
|---|---|
| `backend/services/jd_parser.py` | Provides `extract_jd_terms(text: str, max_terms: int = 18) -> List[str]`. Called with `job_description` directly — no pre-processing at the API layer. Returns an ordered list of skill term strings that maps directly to the `terms` response field. |

The implementation must call `extract_jd_terms(job_description)` and return the result as `{"terms": [...]}`. The API layer does not interpret, filter, or transform the service output.

---

## Non-Goals

The following are explicitly out of scope for this spec and this implementation:

- File upload (job description must be provided as plain text in the request body)
- Custom `max_terms` override via request parameter — default of 18 is used
- Authentication or authorization
- Persistence of job descriptions or extracted terms
- `backend/api/resume.py` or `backend/api/rewrite.py`
- Matching terms against a resume
- Scoring or ranking of terms beyond service output order
- Multiple endpoint variants

---

## Exit Condition

This spec is complete when:

1. `docs/jobs-api-spec-v1.md` is written and reviewed.
2. The spec is accepted as the contract for `backend/api/jobs.py`.
3. Implementation of `backend/api/jobs.py` begins only after acceptance.
