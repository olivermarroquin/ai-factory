# Jobs API Test Scope v1

## Purpose

Define the exact test cases required to validate `backend/api/jobs.py` before any test code is written. This document is the authoritative contract for what must be tested. Tests may only be written after this scope is reviewed and accepted.

---

## Scope

Tests cover `backend/api/jobs.py:handle()` only.

`handle()` is a framework-agnostic function that accepts a parsed body and returns `(response_dict, status_code)`. Tests call it directly — no HTTP layer, no framework, no live network, no filesystem.

Tests do not cover:
- `backend/services/jd_parser.py` internals or term extraction heuristics
- any framework adapter or route binding

---

## Test Categories

| Category | Description |
|---|---|
| A — Input validation | Invalid body types, extra fields, missing/empty fields |
| B — Service failure | `extract_jd_terms` raises an exception |
| C — Success path | Correct response shape, term preservation, empty result handling |

---

## Required Test Cases

### Category A — Input Validation

**A1. Body is not a dict (string)**
- Input: `body = "not a dict"`
- Expected: `400`, `{"error": "invalid_json", "message": "Request body must be valid JSON."}`

**A2. Body is not a dict (list)**
- Input: `body = [{"job_description": "Python developer"}]`
- Expected: `400`, `{"error": "invalid_json", "message": "Request body must be valid JSON."}`

**A3. Extra field present**
- Input: `body = {"job_description": "Python developer", "extra": "z"}`
- Expected: `400`, `{"error": "invalid_json", "message": "Request body must be valid JSON."}`
- Note: message must be exactly `"Request body must be valid JSON."` — same as spec

**A4. `job_description` absent**
- Input: `body = {}`
- Expected: `400`, `{"error": "missing_field", "message": "job_description is required and must be non-empty."}`

**A5. `job_description` is empty string**
- Input: `body = {"job_description": ""}`
- Expected: `400`, `{"error": "missing_field", "message": "job_description is required and must be non-empty."}`

**A6. `job_description` is whitespace only**
- Input: `body = {"job_description": "   \n\t"}`
- Expected: `400`, `{"error": "missing_field", "message": "job_description is required and must be non-empty."}`

---

### Category B — Service Failure

**B1. `extract_jd_terms` raises an exception**
- Setup: mock `extract_jd_terms` to raise `RuntimeError("parse failed")`
- Input: valid body with non-empty `job_description`
- Expected: `500`, `{"error": "service_error", "message": "Job description parse service failed."}`

---

### Category C — Success Path

**C1. Service returns a non-empty list of terms**
- Setup: mock `extract_jd_terms` to return `["python", "selenium", "jenkins"]`
- Input: valid body
- Expected: `200`, `{"terms": ["python", "selenium", "jenkins"]}`

**C2. Service returns an empty list**
- Setup: mock `extract_jd_terms` to return `[]`
- Input: valid body
- Expected: `200`, `{"terms": []}`

**C3. Response shape is exactly `{"terms": [...]}`**
- Setup: mock `extract_jd_terms` to return any list
- Input: valid body
- Expected: `200`, response dict has exactly one key (`"terms"`); no extra keys present

**C4. Returned terms preserved without transformation**
- Setup: mock `extract_jd_terms` to return `["api", "ci/cd", "restassured", "hp alm"]`
- Input: valid body
- Expected: `200`, `response["terms"]` matches service output exactly — no sorting, deduplication, case change, or filtering

**C5. No request-level `max_terms` override**
- Setup: mock `extract_jd_terms` to capture call arguments
- Input: valid body
- Expected: `extract_jd_terms` is called with exactly one positional argument (`job_description`); `max_terms` is not passed

---

## Mocking / Isolation Rules

1. **`extract_jd_terms` must be mocked.** All Category B and C tests mock `backend.api.jobs._jd_parser.extract_jd_terms`. No live parser call is permitted in any test.

2. **No filesystem access.** No test reads from disk or requires a file path.

3. **No network or environment variables required.** Tests must be runnable with no external services available.

4. **Mocking target is the name as imported in `jobs.py`:**
   - `backend.api.jobs._jd_parser.extract_jd_terms`

---

## Pass Criteria

- All 11 test cases pass.
- No test calls `extract_jd_terms` live — all Category B and C tests mock it.
- No test reads from disk or requires external services.
- Error response dicts match spec exactly (including message strings character-for-character).
- Success responses contain exactly `{"terms": [...]}` — no extra keys.
- Returned terms are not transformed.
- `extract_jd_terms` is never called with a `max_terms` argument.

---

## Non-Goals

- Framework route tests (Flask adapter) — not in scope until route wiring is selected
- Testing `extract_jd_terms` term extraction logic — covered by jd_parser tests, not here
- Load, performance, or concurrency testing
- Authentication or authorization
- Persistence

---

## Exit Condition

This scope is complete when:

1. `docs/jobs-api-test-scope-v1.md` is written and reviewed.
2. The scope is accepted as the contract for test implementation.
3. Test implementation begins only after acceptance.
