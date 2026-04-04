# V12 Real Backend Spec

## Purpose

Replace the fake `auto-stub` transport with a real model backend for analyzer and planner stages only.

This is a transport upgrade, not a workflow redesign.

---

## Scope

Implement:

- one real backend (OpenAI)
- analyzer execution through backend
- planner execution through backend
- raw output artifact saving
- hard-stop validation on failure

Do NOT implement:

- coder automation
- apply automation changes
- reviewer automation
- retries
- fallback backends
- multi-provider abstraction

---

## Backend Choice

OpenAI API

---

## Environment Requirements

Required:

- OPENAI_API_KEY

Optional:

- CODE_MIGRATION_MODEL (default: gpt-4.1-mini)

---

## Execution Mode

Add:

--mode auto-openai

---

## Behavior

auto-openai should:

1. Read analyzer prompt file
2. Call OpenAI backend
3. Save analyzer-output.md
4. Read planner prompt file
5. Call OpenAI backend
6. Save planner-output.md
7. Stop after planner

Do NOT touch coder/apply/reviewer.

---

## model_backend.py Responsibilities

Provide:

### ModelRunResult

- raw_text
- backend_name
- model_name
- status
- error_message
- duration_ms

### run_model(...)

Signature:

run_model(stage: str, prompt_text: str, backend_name: str = "stub") -> ModelRunResult

Behavior:

- stub → existing behavior
- openai → real API call
- otherwise → backend_error

---

## OpenAI Call Contract

- send prompt text as-is
- receive raw text
- return raw text only
- no parsing
- no file writes
- no decisions

---

## Safety Rules

Hard fail if:

- OPENAI_API_KEY missing
- API call fails
- output is empty
- output is whitespace
- write fails

Do NOT:

- retry
- fallback
- auto-fix output

---

## Validation Layers

### Transport Validation

- non-empty output
- backend success
- write success

### Stage Validation

Use existing logic unchanged.

---

## migration_execute.py Changes

Add:

--mode auto-openai

Behavior identical to auto-stub except:

run_model(..., backend_name="openai")

---

## Logging

Print:

- analyzer output saved path
- planner output saved path
- backend used
- model used (if available)

---

## Definition of Done

- auto-openai mode exists
- analyzer runs via OpenAI
- planner runs via OpenAI
- outputs written automatically
- stops after planner
- no repo writes
- failures stop cleanly

---

## Non-Goals

Not:

- full automation
- multi-backend system
- retry system
- autonomous pipeline

Only:

- real model transport for analyzer/planner
