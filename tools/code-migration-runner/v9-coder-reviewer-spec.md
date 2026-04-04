# V9 Coder/Reviewer Execution Spec

## Purpose

Define the next automation layer for the code-migration runner.

V9 should automate the workflow after planner output exists.

It should support:

- coder prompt execution
- coder output capture
- reviewer prompt execution
- reviewer output capture
- pass/revise decision handling

V9 should NOT yet:

- apply git commits automatically
- merge changes automatically
- auto-approve revised code without review
- execute multiple coder/reviewer loops without operator visibility

## Current State

The system already supports:

- migration step setup
- analyzer prompt generation
- analyzer output capture
- planner prompt generation
- planner output capture
- no-change verification handling through operator review

The main remaining manual bottleneck is:

- running coder prompts
- capturing coder results
- running reviewer prompts
- deciding pass vs revise in a structured way

## Goal

Reduce friction after planning while preserving strong approval gates.

## Proposed V9 Flow

Inputs:

- venture
- step
- date
- planner-output.md must already exist

Flow:

1. load planner output
2. determine whether coder action is required
3. if planner says no code change needed:
   - skip coder
   - create/update reviewer output as pass-ready verification note
   - stop
4. if planner says implementation is required:
   - load coder prompt packet
   - execute coder stage
   - save coder output artifact
   - load reviewer prompt packet
   - execute reviewer stage
   - save reviewer output artifact
   - stop for operator decision

## Required New Artifacts

### 1. Coder Output

YYYY-MM-DD_step-XX_coder-output.md

Captures:

- updated file content or code change
- short explanation
- any blocking issue

### 2. Reviewer Output

Already exists, but should be treated as required structured output after coder execution.

## Optional New Artifact

### Decision File

YYYY-MM-DD_step-XX_decision.md

Captures:

- accepted
- revise
- blocked

This may be deferred to a later version.

## Execution Modes

### Mode A

manual-capture-coder-reviewer

Behavior:

- print coder prompt
- wait for pasted coder output
- save coder-output.md
- print reviewer prompt
- wait for pasted reviewer output
- save reviewer.md

### Mode B

auto-coder-reviewer

Behavior:

- future API-based execution
- not required for initial V9 implementation

## Recommended Initial Implementation

Start with Mode A only.

Reason:

- keeps safety high
- reduces operator confusion
- mirrors the analyzer/planner capture pattern already proven

## Stop Conditions

V9 must stop if:

- planner-output.md is missing
- coder prompt file is missing
- reviewer prompt file is missing
- coder output is empty
- reviewer output is empty
- reviewer output does not clearly indicate pass or revise

## Approval Gate

V9 must not auto-apply code changes to the repo.
V9 must not auto-commit.
V9 must not auto-merge.

Human approval remains required after reviewer output.

## Pass/Revise Handling

### If reviewer says pass

- operator may accept step
- operator updates summary
- operator may commit separately

### If reviewer says revise

- operator may rerun coder with a corrected prompt
- original reviewer output should remain saved
- revised attempt should not silently overwrite prior artifacts unless forced

## Logging

V9 should log:

- execution start
- whether coder was skipped
- files written
- any failure reason

## Validation Rules

### Coder output

Must be non-empty.

### Reviewer output

Must include at least:

- status
- what is correct
- issues
- drift_detected
- next_safe_step

## Design Rule

V9 should preserve the same discipline as the earlier workflow:

- narrow scope
- explicit handoffs
- visible approval gates
- no silent automation of risky steps

## Recommended Next Implementation

Create a new version of migration_execute.py that supports a second mode:

--mode manual-capture-coder-reviewer

This mode should:

- read planner-output.md
- determine whether coding is needed
- if yes, print coder prompt and capture coder output
- then print reviewer prompt and capture reviewer output
- save both artifacts
- stop
