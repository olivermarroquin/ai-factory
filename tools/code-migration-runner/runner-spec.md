# Runner Spec

## Command Goal

Start one code migration step in a consistent, reusable way.

## Proposed Command

migration-start

## Required Inputs

- venture
- step
- source
- target
- goal

## Optional Inputs

- date
- notes
- source-context-required (yes/no)

## Required Outputs

Inside:
ai-factory/ventures/<venture>/migration-logs/

Create:

- YYYY-MM-DD_step-XX_planner.md
- YYYY-MM-DD_step-XX_reviewer.md
- YYYY-MM-DD_step-XX_summary.md
- YYYY-MM-DD_step-XX_analyzer-prompt.md
- YYYY-MM-DD_step-XX_planner-prompt.md
- YYYY-MM-DD_step-XX_coder-prompt.md
- YYYY-MM-DD_step-XX_reviewer-prompt.md

## Behavior

The runner should:

1. validate inputs
2. create the migration log files
3. prefill planner/reviewer/summary using templates
4. generate prompt files using reusable prompt assets from ai-agency-core
5. insert step-specific context into those prompt files

## Rules

- do not overwrite existing files unless explicitly allowed
- keep naming deterministic
- keep prompt generation readable
- store everything in the venture-specific migration log folder

## Future Expansion

Later versions may:

- call models directly
- parse source files automatically
- generate analyzer packets
- enforce approval gates
- integrate with agent orchestrators
