# Rewrite API Framework Adapter Scope v1

## Purpose

Define the minimal contract for wiring `backend/api/rewrite.py:handle()` to a real HTTP route. This document is the authoritative scope for the framework adapter implementation. No code is written until this scope is reviewed and accepted.

---

## Scope

This scope covers exactly one thing: exposing `POST /rewrite` through a Flask route that delegates entirely to `handle()`.

It does not cover additional endpoints, app factory patterns, authentication, persistence, dependency injection, or any other backend infrastructure.

---

## Framework Selection

**Framework: Flask**

Rationale:
- Flask is the existing framework in the resume-saas repo. No new dependency is introduced.
- `handle()` is framework-agnostic and returns `(dict, int)` — mapping directly to Flask's `(response, status_code)` return convention.
- Minimal adapter requires one route function and one import.

---

## Route Contract

```
POST /rewrite
Content-Type: application/json
```

- Route is defined in `backend/api/rewrite_routes.py` (new file, adapter only).
- Route registers a Blueprint named `rewrite_bp` with no URL prefix.
- The single route is `POST /rewrite`.
- Route function calls `handle()` and returns its output directly as a Flask JSON response.

---

## Request Handling Rules

1. The adapter calls `flask.request.get_json(force=False, silent=True)` to parse the request body.
2. If `get_json()` returns `None` (body is not valid JSON or `Content-Type` is not `application/json`), the adapter passes `None` into `handle()`.
   - `handle()` will reject `None` with `400 invalid_json` — no special-casing needed at the adapter layer.
3. The parsed body (dict, list, string, or `None`) is passed to `handle()` without transformation.
4. The adapter does not perform any input validation itself — all validation is inside `handle()`.

---

## Response Handling Rules

1. `handle()` returns `(response_dict, status_code)`.
2. The adapter wraps `response_dict` in `flask.jsonify()` and returns `(jsonify(response_dict), status_code)`.
3. No transformation, filtering, or augmentation of `response_dict` at the adapter layer.
4. All response shapes (200, 400, 500) are returned identically — the adapter does not special-case error responses.

---

## Error Handling Rules

All error cases are handled by `handle()` and returned as structured JSON per the spec. The adapter does not catch exceptions from `handle()` — `handle()` is specified to never raise. The adapter has no try/except block.

| Condition | Handled by |
|---|---|
| Body not valid JSON | `handle()` — `400 invalid_json` |
| Extra fields | `handle()` — `400 invalid_json` |
| Missing/empty fields | `handle()` — `400 missing_field` |
| Orchestrator exception | `handle()` — `500 service_error` |
| Invalid output | `handle()` — `500 invalid_output` |

---

## Non-Goals

- App factory (`create_app`) — not in scope; Blueprint registration method is implementation-defined
- Authentication or authorization
- Rate limiting
- Middleware of any kind
- CORS headers
- Logging or request tracing at the adapter layer
- Additional endpoints (`/resume`, `/jobs`, etc.)
- FastAPI, Starlette, or any other framework
- Request streaming or chunked responses
- Blueprint URL prefix (none — route is exactly `/rewrite`)

---

## Exit Condition

This scope is complete when:

1. `docs/rewrite-api-framework-adapter-scope-v1.md` is written and reviewed.
2. The scope is accepted as the contract for `backend/api/rewrite_routes.py`.
3. Implementation of `backend/api/rewrite_routes.py` begins only after acceptance.
