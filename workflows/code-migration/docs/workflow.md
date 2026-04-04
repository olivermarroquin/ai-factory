# Code Migration Workflow

## Goal

Move useful logic from an old system into a new system without dragging old structure, local assumptions, or unnecessary complexity with it.

## Steps

### Step 1 — Source Analysis

Analyze the source file and determine:

- what it does
- whether it is core logic, glue, state, or local-only clutter
- whether it should be kept, adapted, replaced, or left behind

### Step 2 — Migration Planning

Based on the analysis:

- identify the target file
- define the exact function or scope to migrate
- define constraints
- define expected output

### Step 3 — Scoped Coding

A coder agent implements only the requested scope.

The coder must:

- modify only the target area
- avoid unrelated refactors
- follow the architecture
- stop if more changes are required

### Step 4 — Review

A reviewer checks:

- whether the implementation matches the requested scope
- whether architecture boundaries were respected
- whether any drift occurred
- what the next safe step is

## Rule

One migration step should usually touch:

- one file
- one function
- one responsibility
