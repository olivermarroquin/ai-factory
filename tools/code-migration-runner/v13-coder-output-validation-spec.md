# V13 Coder Output Validation Spec

## Purpose

Add a validation layer for coder output before any apply stage can trust it.

## Problem

Current system can generate coder output that:

- omits required imports
- includes markdown formatting corruption
- breaks Python indentation
- diverges from planner constraints

This makes automatic apply unsafe.

## Goal

Reject invalid coder output before it can be applied to a real repo file.

## Scope

V13 should validate coder output for:

- non-empty content
- no markdown fences
- no markdown emphasis markers in code
- valid Python parse
- optional required-line presence when planner implies exact port

## Required Validation Checks

### 1. Non-empty

Fail if coder output is empty or whitespace only.

### 2. No markdown fences

Fail if coder output contains:

- ```

  ```
- ```python

  ```

### 3. No markdown emphasis corruption

Fail if coder output contains likely formatting artifacts such as:

- `**`
- escaped underscores in function names like `\_`

### 4. Valid Python parse

Use `ast.parse(...)`
Fail if Python syntax is invalid.

### 5. Exact-import check (initial simple version)

If planner output says:

- preserve exact imports
- port exact top-level imports
  then require expected import line(s) to be present in coder output.

For the current migration style, a simple heuristic is acceptable:

- if source contains `from __future__ import annotations`, require it in coder output

## Stop Rule

If coder output fails validation:

- do not apply
- do not run reviewer
- stop immediately with clear error

## Files To Modify

- migration_execute.py

## New Helper Functions Recommended

- validate_coder_output(...)
- coder_output_requires_future_import(...)
- detect_markdown_artifacts(...)

## Definition of Done

V13 is successful when:

- invalid coder output is rejected before apply
- apply never runs on corrupted markdown-style code
- reviewer never runs on unapplied invalid code
