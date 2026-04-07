# App Structure Improvement Scope v1

## Purpose

Define the minimal structural cleanup for `app.py` now that rewrite, resume, and jobs API slices are all fully validated. This document is the authoritative scope for the structural improvement. No code is written until this scope is reviewed and accepted.

---

## Current Structure

`app.py` at the repo root:

```python
from flask import Flask

from backend.api.rewrite_routes import rewrite_bp
from backend.api.resume_routes import resume_bp
from backend.api.jobs_routes import jobs_bp

app = Flask(__name__)
app.register_blueprint(rewrite_bp)
app.register_blueprint(resume_bp)
app.register_blueprint(jobs_bp)
```

Three route files (`rewrite_routes.py`, `resume_routes.py`, `jobs_routes.py`) each define one Blueprint with one route and delegate entirely to their respective `handle()` functions. The route files are complete and do not require structural changes.

The current `app.py` creates a module-level `app` instance. This means any test that imports `app` shares the same application instance, and any future environment-specific configuration (test vs. production) cannot be injected without restructuring.

---

## Improvement Goal

Introduce an application factory function (`create_app()`) in `app.py` so that:

1. The app instance is created on demand, not at import time.
2. Blueprint registration is consolidated inside `create_app()`.
3. Test clients and future environment-specific setup can use `create_app()` as the single entry point.

This is the standard Flask pattern for apps with multiple Blueprints and the smallest change that meaningfully improves maintainability.

---

## Minimal Structural Change

`app.py` is modified as follows:

1. Wrap the existing Flask instantiation and Blueprint registrations inside a `create_app()` function.
2. `create_app()` returns the configured `app` instance.
3. No arguments to `create_app()` — no config injection, no environment parameter. The function signature is `create_app() -> Flask`.
4. The module-level `app` variable is removed.

No other files change. Route files, handler files, and test files are not modified.

---

## Boundaries

- Only `app.py` is modified.
- `create_app()` takes no arguments — no config object, no environment string.
- No middleware, CORS, logging, or error handlers are added inside `create_app()`.
- No new files are created.
- No changes to `rewrite_routes.py`, `resume_routes.py`, or `jobs_routes.py`.
- No changes to any `handle()` implementation or test files.

---

## Validation Rule

After the change, the end-to-end path is confirmed for all three routes using a test client instantiated from `create_app()`. No live service or model calls are required — each request is crafted to trigger a handled `400` response from `handle()` directly.

Minimum validation:

1. Import `create_app` from `app`.
2. Call `app = create_app()` and create a test client: `client = app.test_client()`.
3. Send the following requests and assert the exact status code and JSON body for each:
   - `POST /rewrite` with `{"resume_text": "", "job_description": "x"}` → `400`, `{"error": "missing_field", "message": "resume_text is required and must be non-empty."}`
   - `POST /resume/parse` with `{"resume_text": ""}` → `400`, `{"error": "missing_field", "message": "resume_text is required and must be non-empty."}`
   - `POST /jobs/parse` with `{"job_description": ""}` → `400`, `{"error": "missing_field", "message": "job_description is required and must be non-empty."}`
4. All three routes must return the expected status and exact JSON body — confirming both route reachability and unbroken handler delegation after the structural change.

---

## Non-Goals

- Config injection or environment switching via `create_app()` arguments — not in scope
- App factory pattern with multiple factory variants
- Logging or request tracing setup
- Error handler registration
- CORS or middleware
- Any changes to route files or handler files
- Any new API routes or slices
- Persistence layer or database initialization
- Docker or deployment configuration

---

## Exit Condition

This scope is complete when:

1. `docs/app-structure-improvement-scope-v1.md` is written and reviewed.
2. The scope is accepted as the contract for the `app.py` change.
3. Implementation of `app.py` begins only after acceptance.
