# Resume API Test Scope v1

## Purpose

Define the exact test cases required to validate `backend/api/resume.py` before any test code is written. This document is the authoritative contract for what must be tested. Tests may only be written after this scope is reviewed and accepted.

---

## Scope

Tests cover `backend/api/resume.py:handle()` only.

`handle()` is a framework-agnostic function that accepts a parsed body and returns `(response_dict, status_code)`. Tests call it directly — no HTTP layer, no framework, no live network, no filesystem.

Tests do not cover:
- `backend/services/resume_parser.py` internals
- DOCX parsing or file-based resume parsing
- any framework adapter or route binding

---

## Test Categories

| Category | Description |
|---|---|
| A — Input validation | Invalid body types, extra fields, missing/empty fields |
| B — Service failure | `extract_resume_sections` raises an exception |
| C — Success path normalization | Correct response shape, section key handling, content preservation |

---

## Required Test Cases

### Category A — Input Validation

**A1. Body is not a dict (string)**
- Input: `body = "not a dict"`
- Expected: `400`, `{"error": "invalid_json", "message": "Request body must be valid JSON."}`

**A2. Body is not a dict (list)**
- Input: `body = [{"resume_text": "x"}]`
- Expected: `400`, `{"error": "invalid_json", "message": "Request body must be valid JSON."}`

**A3. Extra field present**
- Input: `body = {"resume_text": "x", "extra": "z"}`
- Expected: `400`, `{"error": "invalid_json", "message": "Request body must be valid JSON."}`
- Note: message must be exactly `"Request body must be valid JSON."` — same as spec

**A4. `resume_text` absent**
- Input: `body = {}`
- Expected: `400`, `{"error": "missing_field", "message": "resume_text is required and must be non-empty."}`

**A5. `resume_text` is empty string**
- Input: `body = {"resume_text": ""}`
- Expected: `400`, `{"error": "missing_field", "message": "resume_text is required and must be non-empty."}`

**A6. `resume_text` is whitespace only**
- Input: `body = {"resume_text": "   \n\t"}`
- Expected: `400`, `{"error": "missing_field", "message": "resume_text is required and must be non-empty."}`

---

### Category B — Service Failure

**B1. `extract_resume_sections` raises an exception**
- Setup: mock `extract_resume_sections` to raise `RuntimeError("parse failed")`
- Input: valid body with non-empty `resume_text`
- Expected: `500`, `{"error": "service_error", "message": "Resume parse service failed."}`

---

### Category C — Success Path Normalization

**C1. Service returns all four section keys**
- Setup: mock `extract_resume_sections` to return `{"header": ["Jane Doe"], "summary": ["Experienced engineer"], "skills": ["Python"], "experience": ["Company A"]}`
- Input: valid body
- Expected: `200`, response is `{"sections": {"header": ["Jane Doe"], "summary": ["Experienced engineer"], "skills": ["Python"], "experience": ["Company A"]}}`

**C2. Service omits one key — missing key defaults to `[]`**
- Setup: mock `extract_resume_sections` to return `{"header": ["Jane Doe"], "summary": ["Summary"], "experience": ["Company A"]}` (no `skills` key)
- Input: valid body
- Expected: `200`, `response["sections"]["skills"] == []`, other keys preserved

**C3. Service omits all keys — all default to `[]`**
- Setup: mock `extract_resume_sections` to return `{}`
- Input: valid body
- Expected: `200`, all four section keys present, all equal `[]`

**C4. Service-provided array values preserved without transformation**
- Setup: mock `extract_resume_sections` to return `{"header": ["Line 1", "Line 2"], "summary": [], "skills": ["a", "b", "c"], "experience": ["x"]}`
- Input: valid body
- Expected: `200`, section arrays in response match service output exactly — no sorting, deduplication, or content change

**C5. Response shape is exactly `{"sections": {...}}`**
- Setup: mock `extract_resume_sections` to return all four keys
- Input: valid body
- Expected: `200`, response dict has exactly one key (`"sections"`); no extra keys present

---

## Mocking / Isolation Rules

1. **`extract_resume_sections` must be mocked.** All Category B and C tests mock `backend.api.resume._resume_parser.extract_resume_sections`. No live parser call is permitted in any test.

2. **No filesystem access.** No test reads from disk or requires a file path. `resume_text` is provided as a string in the request body.

3. **No DOCX parsing.** `parse_resume_docx` and `read_docx_lines` must not be called in any test.

4. **No network or environment variables required.** Tests must be runnable with no external services available.

5. **Mocking target is the name as imported in `resume.py`:**
   - `backend.api.resume._resume_parser.extract_resume_sections`

---

## Pass Criteria

- All 12 test cases pass.
- No test calls `extract_resume_sections` for live: all Category B and C tests mock it.
- No test reads from disk or requires external services.
- Error response dicts match spec exactly (including message strings character-for-character).
- Success responses contain exactly `{"sections": {...}}` with all four keys always present.
- Missing section keys default to `[]`; present values are not transformed.

---

## Non-Goals

- Framework route tests (Flask adapter) — not in scope until route wiring is selected
- Testing `extract_resume_sections` section detection logic directly — covered by resume_parser tests, not here
- DOCX or file-based resume parsing
- Load, performance, or concurrency testing
- Authentication or authorization
- Persistence

---

## Exit Condition

This scope is complete when:

1. `docs/resume-api-test-scope-v1.md` is written and reviewed.
2. The scope is accepted as the contract for test implementation.
3. Test implementation begins only after acceptance.
