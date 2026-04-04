# V8 Auto-Execution Spec

## Purpose

Define the first automatic execution layer for the code-migration runner.

V8 should automate:

- analyzer execution
- analyzer output saving
- planner execution
- planner output saving

V8 should NOT yet automate:

- coder execution
- code application
- reviewer execution
- git commits
- merge decisions

## Goal

Reduce manual copy/paste between analyzer and planner while keeping approval gates in place before code changes happen.

## Why This Exists

The current runner already:

- creates migration artifacts
- creates prompt packets
- injects source and target context
- creates analyzer-output stubs
- creates next-action guidance

The main remaining manual bottleneck is:

- pasting analyzer prompt into a model
- copying analyzer output into file
- pasting planner prompt into a model
- copying planner output into file

V8 should remove that bottleneck.

## Proposed V8 Flow

Inputs:

- venture
- step
- source
- target
- goal

Flow:

1. runner creates artifacts and prompt packets
2. runner sends analyzer packet to model
3. runner saves analyzer output to analyzer-output.md
4. runner sends planner packet plus analyzer output to model
5. runner saves planner output to planner-output.md
6. runner stops
7. human reviews planner output before coder step

## New Artifacts

### Required

- YYYY-MM-DD_step-XX_analyzer-output.md
- YYYY-MM-DD_step-XX_planner-output.md

### Already Existing

- planner.md
- reviewer.md
- summary.md
- analyzer-prompt.md
- planner-prompt.md
- coder-prompt.md
- reviewer-prompt.md
- next-action.md

## New Command Ideas

### Option A

Extend:
migration_start.py

### Option B

Create a second command:
migration_execute.py

## Recommendation

Use Option B.

Reason:

- keeps setup separate from execution
- easier to debug
- safer to evolve
- avoids mixing artifact generation with model execution

## Proposed New Command

python migration_execute.py \
 --venture resume-saas \
 --step 10 \
 --model claude

## Proposed Responsibilities of migration_execute.py

- locate the generated analyzer prompt packet
- send it to the configured model
- save output to analyzer-output.md
- locate the generated planner prompt packet
- append analyzer-output contents if needed
- send planner prompt to the configured model
- save output to planner-output.md
- stop and report success/failure

## Model Execution Options

### Option 1

Use Claude Code manually
Not real automation. Reject for V8.

### Option 2

Use API calls through Python
Best long-term direction.

### Option 3

Use a local wrapper script that calls an external model CLI
Acceptable if available later.

## Recommendation

Design V8 for API execution, even if the first implementation uses a simple wrapper.

## Output Contracts

### Analyzer output contract

Must return:

- classification
- role
- preserve
- leave_behind
- recommended_next_scope
- notes

### Planner output contract

Must return:

- target_file
- target_scope
- goal
- constraints
- do_not_touch
- source_context_required
- implementation_prompt

## Stop Conditions

V8 must stop if:

- prompt packet file is missing
- source file is missing
- model call fails
- analyzer output is empty
- planner output is empty
- planner output does not contain required sections

## Approval Gate

V8 must NOT continue automatically to coder execution.

Required human review after planner output.

## Logging

V8 should log:

- execution start
- model used
- files written
- any failure reason

## Validation Rules

Before saving outputs:

- ensure analyzer output is non-empty
- ensure planner output is non-empty
- optionally check for required headings

## Safety Rules

- no code modification in V8
- no git operations in V8
- no automatic approval
- no silent overwrite unless explicitly forced

## Implementation Phases

### Phase 1

Spec only

### Phase 2

Create migration_execute.py stub

### Phase 3

Implement file loading + output writing with mocked model calls

### Phase 4

Implement real model integration

## Definition of Done for V8

V8 is successful when:

- analyzer prompt is executed automatically
- analyzer output is saved automatically
- planner prompt is executed automatically
- planner output is saved automatically
- runner stops before coder step
- no code files are modified
