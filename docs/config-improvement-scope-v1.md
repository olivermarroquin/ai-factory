# Config Improvement Scope v1

## Purpose

Define the minimal configuration system for the resume-saas backend.

This document establishes:

- what configuration problems currently exist
- what the config system must solve
- the minimal safe implementation boundary

This is the authoritative scope for config improvement. No code is written until this scope is reviewed and accepted.

---

## Current State

Configuration is currently implicit and hardcoded across the backend:

- logging level is fixed in `app.py`
- no environment-based behavior exists
- no centralized configuration module exists
- values are embedded directly in code

There is no single source of truth for runtime configuration.

---

## Problem

As the system grows, lack of configuration control will cause:

- scattered hardcoded values
- inconsistent behavior across environments
- unsafe modifications to core files
- inability to control logging or runtime behavior without code changes

This creates drift risk and violates controlled execution principles.

---

## Improvement Goal

Introduce a minimal configuration system that:

1. centralizes configuration in one place
2. supports environment-based values (dev, test, future prod)
3. does not change existing behavior by default
4. does not introduce external dependencies

The system must remain simple, explicit, and auditable.

---

## Minimal Scope

The config system will include:

### 1. Config Module

A single file:

backend/config.py

Responsibilities:

- define configuration values
- read environment variables where applicable
- provide defaults that match current behavior

---

### 2. Initial Config Values

Only include:

- LOG_LEVEL (default: INFO)

#### LOG_LEVEL Rules

- Accepted values: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Input is case-insensitive (e.g., "error" → "ERROR")
- Invalid values must fall back to default: INFO
- No exceptions should be raised for invalid input

No other values are introduced in this version.

---

### 3. Logging Integration

Update `app.py` to:

- read LOG_LEVEL from config
- apply it to the existing logger

No change to logging structure or format.

---

## Config Input Sources (Truth Inputs)

The configuration system reads from:

- OS environment variables (via `os.getenv`)
- No other sources are allowed in this version

Rules:

- Environment variables are read at application startup only
- No runtime mutation or reloading
- No file-based config (e.g., `.env`, YAML, JSON)

---

## Normalization Rules

- All `LOG_LEVEL` inputs must be converted to uppercase before validation
- Leading and trailing whitespace must be stripped
- Validation is performed after normalization

---

## Fallback Behavior

If `LOG_LEVEL` is:

- missing → default to `INFO`
- empty string → default to `INFO`
- invalid value → default to `INFO`

No warnings or exceptions are emitted in this version.

---

## App Integration Contract

`app.py` must:

1. import config access from `backend/config.py`
2. resolve `LOG_LEVEL` using the config module
3. apply the resolved value to the existing application logger

No other logging behavior is modified.

---

## Non-Regression Guarantee

The introduction of the config system must not:

- change default logging behavior
- change request handling behavior
- change response formats
- introduce new side effects

The system must behave identically when no environment variables are set.

---

## Boundaries

- Only introduce backend/config.py
- Only modify app.py to read config
- Do not modify handler files
- Do not modify route files
- Do not introduce external libraries
- Do not introduce complex config patterns (classes, inheritance, frameworks)
- Do not change default behavior
- Do not add new config fields beyond LOG_LEVEL

---

## Validation Rule

After implementation, the following must be confirmed:

1. Run app with no environment variables set:
   - effective log level is `INFO`
   - behavior is unchanged from current default behavior

2. Run app with `LOG_LEVEL=ERROR`:
   - effective log level is `ERROR`
   - INFO-level request completion logs are suppressed

3. Run app with `LOG_LEVEL=error`:
   - input is normalized to `ERROR`
   - effective log level is `ERROR`

4. Run app with `LOG_LEVEL=" error "`:
   - leading/trailing whitespace is stripped
   - input is normalized to `ERROR`
   - effective log level is `ERROR`

5. Run app with `LOG_LEVEL=` (empty string):
   - effective log level falls back to `INFO`

6. Run app with `LOG_LEVEL=INVALID`:
   - effective log level falls back to `INFO`
   - no exception is raised

7. All endpoints continue to return exact same responses as before

8. No tests break

---

## Non-Goals

- Full config system (multiple files, environments, profiles)
- Secrets management
- Database configuration
- API keys or credentials
- Dynamic runtime config reload
- External config services
- Refactoring other modules to use config

---

## Exit Condition

This scope is complete when:

1. docs/config-improvement-scope-v1.md is written and reviewed
2. scope is accepted as the implementation contract
3. implementation has not yet started

---

## Scope Review Status

Status: ACCEPTED

Reviewed by: Operator

Notes:

- Scope validated against ECS and Guardian constraints
- All normalization, fallback, and integration rules are explicitly defined
- Validation rules enforce deterministic behavior
- Safe to proceed to implementation phase
