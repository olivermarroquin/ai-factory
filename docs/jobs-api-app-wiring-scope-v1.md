# Jobs API App Wiring Scope v1

## Purpose

Define the minimal contract for registering `backend/api/jobs_routes.py:jobs_bp` into the existing Flask app and confirming the end-to-end HTTP path for `POST /jobs/parse`. This document is the authoritative scope for the app wiring implementation. No code is written until this scope is reviewed and accepted.

---

## Scope

This scope covers exactly one thing: adding `jobs_bp` to the existing `app.py` so that `POST /jobs/parse` is reachable through the real app.

It does not cover additional Blueprints, app factory patterns, environment configuration, authentication, persistence, or any other infrastructure.

---

## Existing App Entry Point

**`app.py` at the repo root.**

Current state of `app.py`:

```python
from flask import Flask

from backend.api.rewrite_routes import rewrite_bp
from backend.api.resume_routes import resume_bp

app = Flask(__name__)
app.register_blueprint(rewrite_bp)
app.register_blueprint(resume_bp)
```

`rewrite_bp` and `resume_bp` are already registered. The wiring step adds `jobs_bp` registration to the same file.

---

## Registration Contract

`app.py` is modified with the following minimal changes only:

1. Import `jobs_bp` from `backend.api.jobs_routes`.
2. Register `jobs_bp` on the app with no URL prefix: `app.register_blueprint(jobs_bp)`.

No other changes to `app.py`. The file must remain minimal — only what is required to register all three Blueprints.

---

## End-to-End Validation Rule

After wiring, the end-to-end path is confirmed by sending a `POST /jobs/parse` request through a Flask test client instantiated from `app.py`.

Minimum validation:

1. Import `app` from `app.py`.
2. Create a test client: `client = app.test_client()`.
3. Send a `POST /jobs/parse` with a valid JSON body. A `400 missing_field` or `400 invalid_json` is acceptable confirmation of route reachability — live service calls are not required.
4. Assert the response status is not `404` — confirming the route is registered and reachable.

---

## Non-Goals

- App factory (`create_app` function) — not in scope
- Environment variable configuration or `.env` loading
- Authentication or authorization
- CORS or middleware of any kind
- Logging
- Additional Blueprints or routes beyond `jobs_bp`
- Production WSGI server configuration
- Docker or deployment configuration
- Any changes to `backend/api/jobs.py` or `backend/api/jobs_routes.py`
- Any changes to `rewrite_bp` or `resume_bp` registration or their respective route files

---

## Exit Condition

This scope is complete when:

1. `docs/jobs-api-app-wiring-scope-v1.md` is written and reviewed.
2. The scope is accepted as the contract for the `app.py` change.
3. Implementation of the `app.py` change begins only after acceptance.
