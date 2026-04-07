# Rewrite API App Wiring Scope v1

## Purpose

Define the minimal contract for registering `backend/api/rewrite_routes.py:rewrite_bp` into a Flask application and confirming the end-to-end HTTP path for `POST /rewrite`. This document is the authoritative scope for the app wiring implementation. No code is written until this scope is reviewed and accepted.

---

## Scope

This scope covers exactly one thing: creating a minimal Flask app entrypoint that registers `rewrite_bp` and making `POST /rewrite` reachable through the real app.

It does not cover additional Blueprints, app factory patterns, environment configuration, authentication, persistence, or any other infrastructure.

---

## Existing App Entry Point

**No Flask app entrypoint exists in the resume-saas repo.**

The repo currently contains:
- `backend/api/rewrite.py` — framework-agnostic handler
- `backend/api/rewrite_routes.py` — Flask Blueprint (`rewrite_bp`)
- No `app.py`, `main.py`, `run.py`, `server.py`, or `wsgi.py` at the repo root or in `backend/`

The wiring step must create the app entrypoint as part of this work.

---

## Registration Contract

A new file `app.py` is created at the repo root with the following minimal contract:

1. Creates a `Flask` app instance.
2. Imports `rewrite_bp` from `backend.api.rewrite_routes`.
3. Registers `rewrite_bp` on the app with no URL prefix: `app.register_blueprint(rewrite_bp)`.
4. Exposes the app instance for use by a dev server or test client.

No other Blueprints, routes, middleware, or configuration are added. The file must remain minimal — only what is required to register `rewrite_bp` and run the app.

---

## End-to-End Validation Rule

After wiring, the end-to-end path is confirmed by sending a `POST /rewrite` request through a Flask test client instantiated from `app.py`.

Minimum validation:

1. Import `app` from `app.py`.
2. Create a test client: `client = app.test_client()`.
3. Send a `POST /rewrite` with a valid JSON body (real orchestrator must be mocked or the request must produce a handled error response — a `400 missing_field` or `400 invalid_json` is acceptable confirmation of route reachability).
4. Assert the response status is not `404` — confirming the route is registered and reachable.

Live model calls are not required for validation. A `400` from `handle()` confirms the route is wired correctly.

---

## Non-Goals

- App factory (`create_app` function) — not in scope
- Environment variable configuration or `.env` loading
- Authentication or authorization
- CORS or middleware of any kind
- Logging
- Additional Blueprints or routes
- Production WSGI server configuration (gunicorn, uWSGI, etc.)
- Docker or deployment configuration
- Any changes to `backend/api/rewrite.py` or `backend/api/rewrite_routes.py`

---

## Exit Condition

This scope is complete when:

1. `docs/rewrite-api-app-wiring-scope-v1.md` is written and reviewed.
2. The scope is accepted as the contract for `app.py`.
3. Implementation of `app.py` begins only after acceptance.
