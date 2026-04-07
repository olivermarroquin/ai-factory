# Logging Improvement Scope v1

## Purpose

Define the minimal logging addition for the resume-saas backend now that rewrite, resume, and jobs API slices are all fully validated. This document is the authoritative scope for the logging implementation. No code is written until this scope is reviewed and accepted.

---

## Current State

No logging exists anywhere in the backend:

- `app.py` — no logging configuration, no request hooks
- `backend/api/rewrite_routes.py`, `resume_routes.py`, `jobs_routes.py` — no logging
- `backend/api/rewrite.py`, `resume.py`, `jobs.py` — handlers catch all service exceptions and return `500 service_error`, but log nothing; the original exception traceback is silently discarded

The result: a `500` response is returned but leaves no observable trace of what failed or when.

---

## Improvement Goal

Add the minimal logging that makes the running app observable without modifying handler logic, route contracts, or test files.

Two additions, both in `app.py` only:

1. **Configure stdlib logging** — set up a `StreamHandler` to stdout at `INFO` level inside `create_app()`, so log output is visible during development and in any environment that captures stdout.
2. **Log every request completion** — register an `@app.after_request` hook inside `create_app()` that emits one `INFO` line per request: `METHOD path → status_code`.

This gives operational visibility for all three routes without touching handler files, exposing request/response body content, or introducing any external dependency.

---

## Minimal Logging Change

`app.py` is modified as follows:

1. Add `import logging` and `import sys` at the top of the file.
2. Inside `create_app()`, before Blueprint registrations:
   - Obtain a named logger: `logger = logging.getLogger(__name__)`.
   - Attach a `StreamHandler` to stdout only if the logger has no handlers yet:
     ```
     if not logger.handlers:
         handler = logging.StreamHandler(sys.stdout)
         handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
         logger.addHandler(handler)
     logger.setLevel(logging.INFO)
     ```
3. Inside `create_app()`, after Blueprint registrations:
   - Register an `@app.after_request` function that calls `logger.info("%s %s → %s", request.method, request.path, response.status_code)` and returns the response unchanged.
4. Import `request` from `flask` for use in the `after_request` hook.

No other files change. Route files, handler files, and test files are not modified.

---

## Boundaries

- Only `app.py` is modified.
- Logging is configured via a named logger with a `StreamHandler` attached conditionally — `logging.basicConfig()` is not used. No external log services, no file handlers, no log rotation.
- Log level is `INFO`. No `DEBUG`-level request body logging.
- The `after_request` hook logs method, path, and status code only — no request headers, no request or response body content.
- No changes to `rewrite_routes.py`, `resume_routes.py`, or `jobs_routes.py`.
- No changes to `rewrite.py`, `resume.py`, or `jobs.py`.
- No changes to test files.
- Service exception logging (inside handler `except` blocks) is out of scope for this improvement — that is a follow-on step.

---

## Validation Rule

After the change, the following is confirmed:

1. Import `create_app` from `app`.
2. Call `app = create_app()` and create a test client: `client = app.test_client()`.
3. Send the following requests and assert each returns the expected status and exact JSON body (no regression):
   - `POST /rewrite` with `{"resume_text": "", "job_description": "x"}` → `400`, `{"error": "missing_field", "message": "resume_text is required and must be non-empty."}`
   - `POST /resume/parse` with `{"resume_text": ""}` → `400`, `{"error": "missing_field", "message": "resume_text is required and must be non-empty."}`
   - `POST /jobs/parse` with `{"job_description": ""}` → `400`, `{"error": "missing_field", "message": "job_description is required and must be non-empty."}`
4. Confirm log output is emitted to stdout for each request (manual inspection or captured log assertion) — each line must contain method, path, and status code.

No live service calls required. The `400` responses confirm route reachability and unbroken handler delegation. The log output confirms the `after_request` hook is active.

---

## Non-Goals

- External logging services (Datadog, Sentry, CloudWatch, etc.)
- File-based log handlers or log rotation
- Request/response body logging
- Request header logging
- Structured JSON log format — not in scope for this improvement
- Service exception logging inside handler files — follow-on step
- Log level configuration via environment variables — not in scope
- Config system integration
- New API routes or slices
- Any changes to route files or handler files
- Any changes to test files

---

## Exit Condition

This scope is complete when:

1. `docs/logging-improvement-scope-v1.md` is written and reviewed.
2. The scope is accepted as the contract for the `app.py` change.
3. Implementation of the logging change begins only after acceptance.
