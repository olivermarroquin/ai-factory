# File Naming Convention

## Purpose

Define a consistent naming format for migration log artifacts.

This should be readable by humans now and easy for automation later.

## Naming Pattern

YYYY-MM-DD_step-XX_artifact-name.md

## Examples

2026-04-03_step-01_analyzer.md
2026-04-03_step-01_planner.md
2026-04-03_step-01_reviewer.md
2026-04-03_step-01_summary.md

2026-04-03_step-02_planner.md
2026-04-03_step-02_reviewer.md
2026-04-03_step-02_summary.md

## Rules

- use the same date for all artifacts created during the same working session
- increment step numbers sequentially
- keep step numbers zero-padded:
  - step-01
  - step-02
  - step-03
- artifact names should be one of:
  - analyzer
  - planner
  - reviewer
  - summary

## Venture Location

Store venture-specific migration artifacts in:

ai-factory/ventures/<venture>/migration-logs/

## Example Venture Path

ai-factory/ventures/resume-saas/migration-logs/2026-04-03_step-01_planner.md

## Rule

Do not invent new naming formats casually.
Consistency matters more than cleverness.
