# Code Migration Workflow

## Purpose

This workflow defines how to migrate logic from an existing codebase into a new codebase in a controlled, repeatable way.

It is designed to prevent:

- blind copying
- architecture drift
- vague AI prompting
- uncontrolled refactors
- mixing core logic with glue code

## Core Pattern

source analysis
→ migration planning
→ scoped implementation
→ review

## Roles

- analyzer
- planner
- coder
- reviewer

## Rule

No implementation happens until:

1. the source is classified
2. the target file is defined
3. the migration scope is narrowed
4. the output contract is clear
