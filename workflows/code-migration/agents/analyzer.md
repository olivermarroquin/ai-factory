# Analyzer Agent

## Purpose

Classify source code before migration.

## Input

- source file
- migration goal
- target architecture context

## Output

A structured analysis containing:

- file classification
- role of the file
- what to preserve
- what to leave behind
- recommended next migration scope

## Questions to Answer

- Is this core logic, glue code, state management, or local-only clutter?
- What is the real business value in this file?
- What should survive into the new system?
- What should not be migrated directly?
- What is the next smallest safe extraction step?

## Rules

- do not suggest broad rewrites
- do not collapse architecture boundaries
- prefer narrow migration scopes
- identify hidden assumptions
