# Rewrite API Test Scope v1

## Purpose

Define the exact test cases required to validate `backend/api/rewrite.py` before any test code is written. This document is the authoritative contract for what must be tested. Tests may only be written after this scope is reviewed and accepted.

---

## Scope

Tests cover `backend/api/rewrite.py:handle()` only.

`handle()` is a framework-agnostic function that accepts a parsed body and returns `(response_dict, status_code)`. Tests call it directly — no HTTP layer, no framework, no live network.

Tests do not cover:
- `backend/services/rewrite_orchestrator_v5.py` internals
- `backend/schemas/proposal_schema.py` internals
- any framework adapter or route binding

---

## Test Categories

| Category | Description |
|---|---|
| A — Input validation | Invalid body types, extra fields, missing/empty fields |
| B — Service failure | Orchestrator raises an exception |
| C — Output validation failure | `validate_proposals()` returns `(False, reason)` |
| D — Success path normalization | Correct response shape, id assignment, narrative handling |

---

## Required Test Cases

### Category A — Input Validation

**A1. Body is not a dict**
- Input: `body = "not a dict"` (a string)
- Expected: `400`, `{"error": "invalid_json", "message": "Request body must be valid JSON."}`

**A2. Body is a list**
- Input: `body = [{"resume_text": "x", "job_description": "y"}]`
- Expected: `400`, `{"error": "invalid_json", "message": "Request body must be valid JSON."}`

**A3. Extra field present**
- Input: `body = {"resume_text": "x", "job_description": "y", "extra": "z"}`
- Expected: `400`, `{"error": "invalid_json", "message": "Request body must be valid JSON."}`
- Note: message must be exactly `"Request body must be valid JSON."` — not a field-list variant

**A4. `resume_text` absent**
- Input: `body = {"job_description": "y"}`
- Expected: `400`, `{"error": "missing_field", "message": "resume_text is required and must be non-empty."}`

**A5. `resume_text` is empty string**
- Input: `body = {"resume_text": "", "job_description": "y"}`
- Expected: `400`, `{"error": "missing_field", "message": "resume_text is required and must be non-empty."}`

**A6. `resume_text` is whitespace only**
- Input: `body = {"resume_text": "   ", "job_description": "y"}`
- Expected: `400`, `{"error": "missing_field", "message": "resume_text is required and must be non-empty."}`

**A7. `job_description` absent**
- Input: `body = {"resume_text": "x"}`
- Expected: `400`, `{"error": "missing_field", "message": "job_description is required and must be non-empty."}`

**A8. `job_description` is empty string**
- Input: `body = {"resume_text": "x", "job_description": ""}`
- Expected: `400`, `{"error": "missing_field", "message": "job_description is required and must be non-empty."}`

**A9. `job_description` is whitespace only**
- Input: `body = {"resume_text": "x", "job_description": "\n\t"}`
- Expected: `400`, `{"error": "missing_field", "message": "job_description is required and must be non-empty."}`

---

### Category B — Service Failure

**B1. Orchestrator raises an exception**
- Setup: mock `run_rewrite` to raise `RuntimeError("model failed")`
- Input: valid body
- Expected: `500`, `{"error": "service_error", "message": "Rewrite service failed."}`

---

### Category C — Output Validation Failure

**C1. `validate_proposals()` returns `(False, reason)`**
- Setup: mock `run_rewrite` to return a structurally valid payload (e.g., `{"proposals": [<valid proposal dict>]}`); mock `validate_proposals` to return `(False, "bad schema")` — failure is driven solely by the mocked validation result, not by malformed orchestrator output
- Input: valid body
- Expected: `500`, `{"error": "invalid_output", "message": "Rewrite service returned invalid proposals."}`

---

### Category D — Success Path Normalization

**D1. Raw output is a dict with `proposals` and `narrative`**
- Setup: mock `run_rewrite` to return `{"proposals": [<one valid proposal dict>], "narrative": "Summary of changes"}`; mock `validate_proposals` to return `(True, None)`
- Input: valid body
- Expected: `200`, response contains `proposals` with `id` assigned starting at 1, `narrative` present with correct value

**D2. Raw output is a dict with `proposals` only (no `narrative`)**
- Setup: mock `run_rewrite` to return `{"proposals": [<one valid proposal dict>]}`; mock `validate_proposals` to return `(True, None)`
- Input: valid body
- Expected: `200`, response contains `proposals`, `narrative` key is absent (not `null`)

**D3. Raw output is a list**
- Setup: mock `run_rewrite` to return `[<one valid proposal dict>, <second valid proposal dict>]`; mock `validate_proposals` to return `(True, None)`
- Input: valid body
- Expected: `200`, response contains `proposals` list, `narrative` key is absent

**D4. Sequential id assignment starting at 1**
- Setup: mock `run_rewrite` to return a list of three proposal dicts (none with `id` set); mock `validate_proposals` to return `(True, None)`
- Input: valid body
- Expected: `200`, proposals have `id` values `1`, `2`, `3` in order

**D5. `narrative` is not a string — omitted from response**
- Setup: mock `run_rewrite` to return `{"proposals": [<one valid proposal dict>], "narrative": None}`; mock `validate_proposals` to return `(True, None)`
- Input: valid body
- Expected: `200`, `narrative` key is absent from response (only `isinstance(narrative, str)` adds it)

---

## Mocking / Isolation Rules

1. **Orchestrator must be mocked.** All tests mock `backend.api.rewrite._orchestrator.run_rewrite`. No live model call is permitted in any test.

2. **`validate_proposals` may be mocked** to isolate Category C (invalid output path). For Category D success cases, `validate_proposals` must be mocked to return `(True, None)` so tests do not depend on schema internals.

3. **No network, no disk, no environment variables required.** Tests must be runnable with no external services available.

4. **Mocking target is the name as imported in `rewrite.py`**, not the origin module, to ensure patches take effect:
   - `backend.api.rewrite._orchestrator.run_rewrite`
   - `backend.api.rewrite.validate_proposals`

---

## Pass Criteria

- All 14 test cases pass.
- No test makes a live model call.
- No test depends on the filesystem or environment variables.
- Error response dicts match spec exactly (including message strings character-for-character).
- Success responses include `proposals` always; `narrative` is present only when the raw output provides a non-None string value.

---

## Non-Goals

- Framework route tests (Flask, FastAPI) — not in scope until framework wiring is selected
- Testing `validate_proposals` schema rules directly — covered by proposal_schema tests, not here
- Testing `run_rewrite` model behavior — covered by orchestrator tests, not here
- Load, performance, or concurrency testing
- Authentication or authorization
- Persistence

---

## Exit Condition

This scope is complete when:

1. `docs/rewrite-api-test-scope-v1.md` is written and reviewed.
2. The scope is accepted as the contract for test implementation.
3. Test implementation begins only after acceptance.
