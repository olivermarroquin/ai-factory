# Handoff Artifacts

## Purpose

Define the standard artifacts created during a code-migration step.

These artifacts make the workflow:

- easier to review
- easier to resume later
- easier to automate in the future

## Standard Handoff Artifacts

### 1. Analyzer Output

Captures:

- source file classification
- file role
- preserve list
- leave-behind list
- recommended next scope
- notes

### 2. Planner Output

Captures:

- target file
- target scope
- goal
- constraints
- do-not-touch rules
- whether source context is required
- implementation prompt

### 3. Reviewer Output

Captures:

- pass/revise status
- what is correct
- what is wrong
- whether drift was detected
- next safe step

### 4. Step Summary

Captures:

- what step was attempted
- what changed
- whether it was accepted
- any blockers
- commit reference if applicable

## When to Save Artifacts

Do save artifacts when the step:

- changes architecture understanding
- adds a meaningful migration step
- creates a reusable pattern
- surfaces an important issue
- will likely need to be resumed later

Do not save artifacts for every trivial exchange.

## Minimum Useful Set

For meaningful steps, save:

- planner output
- reviewer output
- step summary

## Best Set

For larger or important steps, save:

- analyzer output
- planner output
- reviewer output
- step summary
