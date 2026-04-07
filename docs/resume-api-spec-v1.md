# Resume API Spec v1

## Purpose

Define the contract for `backend/api/resume.py`: a single synchronous HTTP endpoint that accepts plain-text resume content and returns a structured section breakdown. This spec is the authoritative contract for implementation. No code is written until this spec is reviewed and accepted.

---

## Scope

This spec covers exactly one endpoint: `POST /resume/parse`.

It does not cover job description parsing, authentication, persistence, file upload, background processing, or any other endpoint.

---

## Endpoint

```
POST /resume/parse
Content-Type: application/json
```

Synchronous. Returns a JSON response body. No side effects. No persistence.

---

## Request Shape

```json
{
  "resume_text": "<string>"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `resume_text` | string | Yes | Full plain-text content of the resume |

Additional fields are rejected. `resume_text` is split into lines and passed to `backend/services/resume_parser.extract_resume_sections()`. The API layer normalizes the result to ensure all four section keys are present in the response.

---

## Response Shape

### 200 OK

```json
{
  "sections": {
    "header":     ["<line>", ...],
    "summary":    ["<line>", ...],
    "skills":     ["<line>", ...],
    "experience": ["<line>", ...]
  }
}
```

| Field | Type | Always present | Description |
|---|---|---|---|
| `sections` | object | Yes | Structured breakdown of resume content by section |
| `sections.header` | array of strings | Yes | Name, contact info, and other header lines. May be empty `[]`. |
| `sections.summary` | array of strings | Yes | Professional summary lines. May be empty `[]`. |
| `sections.skills` | array of strings | Yes | Technical skills lines. May be empty `[]`. |
| `sections.experience` | array of strings | Yes | Work experience lines. May be empty `[]`. |

All four section keys are always present in the response. Any section with no detected content returns an empty array, never `null`.

---

## Validation Rules

Applied at the API boundary before calling any backend service:

1. Request body must be valid JSON.
2. `resume_text` must be present and a non-empty string (after stripping whitespace).
3. Additional fields are rejected.
4. No further input validation at the API layer — section detection is best-effort inside the service.

---

## Error Cases

| Condition | Status | Response body |
|---|---|---|
| Request body is not valid JSON | 400 | `{ "error": "invalid_json", "message": "Request body must be valid JSON." }` |
| `resume_text` missing or empty | 400 | `{ "error": "missing_field", "message": "resume_text is required and must be non-empty." }` |
| Additional fields present | 400 | `{ "error": "invalid_json", "message": "Request body must be valid JSON." }` |
| Backend service raises an exception | 500 | `{ "error": "service_error", "message": "Resume parse service failed." }` |

No other error shapes are defined in v1.

---

## Dependencies

| Dependency | Role |
|---|---|
| `backend/services/resume_parser.py` | Provides `extract_resume_sections(lines: List[str]) -> Dict[str, List[str]]`. Called with `resume_text.splitlines()`. Returns a section dict; the API layer normalizes it to guarantee all four keys (`header`, `summary`, `skills`, `experience`) are present as arrays, defaulting to `[]` if any key is missing. |

The implementation must split `resume_text` into lines, call `extract_resume_sections()`, normalize the result to guarantee the response contract, and return it. The API layer does not interpret or transform the section content beyond this normalization.

---

## Non-Goals

The following are explicitly out of scope for this spec and this implementation:

- File upload (resume must be provided as plain text in the request body)
- DOCX parsing — `resume_parser.parse_resume_docx()` and `read_docx_lines()` are not used
- Numbered view output (`build_numbered_resume_view`) — not exposed in this endpoint
- Authentication or authorization
- Persistence of resume text or parsed sections
- `backend/api/jobs.py` or `backend/api/rewrite.py`
- Section validation or scoring
- Multiple endpoint variants

---

## Exit Condition

This spec is complete when:

1. `docs/resume-api-spec-v1.md` is written and reviewed.
2. The spec is accepted as the contract for `backend/api/resume.py`.
3. Implementation of `backend/api/resume.py` begins only after acceptance.
