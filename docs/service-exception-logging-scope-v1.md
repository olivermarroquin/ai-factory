# Service Exception Logging Scope v1

## Purpose

Define the minimal handler-level logging for `rewrite.py`, `resume.py`, and `jobs.py` so that service failures produce an observable traceback instead of being silently discarded. This document is the authoritative scope for the implementation. No code is written until this scope is reviewed and accepted.

---

## Current State

App-level request logging is in place (`app.py` logs `METHOD path → status_code` for every request). However, all three handler files catch service exceptions silently:

- `backend/api/rewrite.py` — `except Exception: return _error("service_error", ...)` — traceback discarded
- `backend/api/resume.py` — `except Exception: return _error("service_error", ...)` — traceback discarded
- `backend/api/jobs.py` — `except Exception: return _error("service_error", ...)` — traceback discarded

When a service call fails, the app-level log shows `POST /rewrite → 500` but nothing records what raised, where, or why.

---

## Improvement Goal

Add `logging.exception()` inside each `except Exception` block so that when a service call raises, the full traceback is emitted to the log before the handler returns the `500` response.

The error contract is unchanged: `handle()` still never raises, still returns `500 service_error` on exception. The only addition is a log line that captures the exception before it is consumed.

---

## Minimal Logging Change

Each of the three handler files is modified as follows:

1. Add `import logging` at the top of the file (after existing imports).
2. Add a module-level named logger immediately after the imports:
   ```
   logger = logging.getLogger(__name__)
   ```
3. Inside each `except Exception` block, add a `logger.exception()` call before the `return _error(...)` line:
   - `rewrite.py`: `logger.exception("rewrite service call failed")`
   - `resume.py`: `logger.exception("resume parse service call failed")`
   - `jobs.py`: `logger.exception("job description parse service call failed")`

`logger.exception()` logs at `ERROR` level and automatically appends the full exception traceback. The `return _error(...)` line that follows is unchanged.

No other lines in any handler file are modified.

**Propagation note:** Module-level loggers named `backend.api.rewrite`, `backend.api.resume`, and `backend.api.jobs` propagate to the root logger. Python's last-resort handler (`logging.lastResort`) emits `ERROR`-level messages to `stderr` even without explicit root logger configuration, so tracebacks will be visible in any standard output-capturing environment. Explicit root logger configuration is out of scope for this improvement.

---

## Boundaries

- Only `backend/api/rewrite.py`, `backend/api/resume.py`, and `backend/api/jobs.py` are modified.
- Each file receives exactly two additions: one `import logging` line and one `logger = logging.getLogger(__name__)` line.
- Each `except Exception` block receives exactly one addition: `logger.exception(...)` before the existing `return _error(...)`.
- The `return _error(...)` lines are not modified — error contracts are unchanged.
- No changes to `app.py`.
- No changes to route files.
- No changes to test files.
- No external logging services, file handlers, or log rotation.
- No request or response body content is logged.

---

## Validation Rule

After the change, the following is confirmed for each handler file:

1. Import the `handle` function from each handler module.
2. Patch the service call in each handler to raise `RuntimeError("test failure")`.
3. Call `handle()` with a valid body while capturing log output (via `unittest.mock` or `logging.handlers.MemoryHandler`).
4. Assert the return value is `({"error": "service_error", "message": "<expected message>"}, 500)` — error contract unchanged.
5. Assert that a log record at `ERROR` level was emitted and its message contains `"failed"` and the exception info includes `"test failure"`.

Minimum per-file validation assertions:

| File | Valid body | Expected response | Expected log message |
|---|---|---|---|
| `rewrite.py` | `{"resume_text": "x", "job_description": "y"}` | `500 service_error` | `"rewrite service call failed"` |
| `resume.py` | `{"resume_text": "x"}` | `500 service_error` | `"resume parse service call failed"` |
| `jobs.py` | `{"job_description": "x"}` | `500 service_error` | `"job description parse service call failed"` |

No live service calls required. All service calls are patched to raise.

---

## Non-Goals

- Logging inside validation branches (invalid_json, missing_field) — not in scope; these are client errors, not service failures
- Structured log format or JSON output
- Log level configuration via environment variables
- External logging services
- File-based log handlers
- Root logger configuration
- Changes to `app.py`
- Changes to route files or test files
- Request or response body logging of any kind

---

## Exit Condition

This scope is complete when:

1. `docs/service-exception-logging-scope-v1.md` is written and reviewed.
2. The scope is accepted as the contract for the handler file changes.
3. Implementation of the three handler changes begins only after acceptance.
