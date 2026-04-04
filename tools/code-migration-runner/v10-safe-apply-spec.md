# V10 Safe Apply Spec

## Purpose

Define a safe apply stage for the code-migration runner.

V10 should ensure that coder output is written to the real target file before reviewer approval is treated as final.

## Problem

Current flow allows this sequence:

- coder prompt runs
- coder output is captured
- reviewer prompt runs
- reviewer passes
- real target file may still be unchanged

This creates a mismatch between:

- reviewed output
- actual repository state

## Goal

Add an explicit apply stage between coder output capture and reviewer execution.

The new flow should be:

planner output
→ coder prompt
→ coder output capture
→ apply coder output to target file
→ verify target file updated
→ reviewer prompt
→ reviewer output capture

## Scope

V10 should only define safe apply behavior for file replacement mode.

It should NOT yet:

- apply diffs
- merge patches
- auto-commit changes
- auto-push changes
- auto-approve reviewer pass

## Proposed V10 Flow

### If planner says no code changes required

- skip coder
- skip apply
- skip reviewer or treat as verification-only path
- stop cleanly

### If planner says implementation required

1. capture coder output
2. resolve target file path
3. write coder output into target file
4. verify target file is non-empty
5. then run reviewer
6. save reviewer output

## Required Inputs

- venture
- step
- date
- planner-output.md
- coder-output.md
- target path

## Required Artifacts

Already existing:

- coder-output.md
- reviewer.md
- planner-output.md

Possible new artifact:

- apply-log.md

## Recommended Initial Implementation

Do not create a separate apply command yet.

Add a new execution mode to migration_execute.py:

--mode manual-capture-coder-apply-reviewer

This mode should:

- read planner-output.md
- decide whether coder is required
- if yes:
  - print coder prompt
  - capture coder output
  - save coder-output.md
  - write coder output into the real target file
  - verify target file updated
  - then print reviewer prompt
  - capture reviewer output
  - save reviewer.md

## Target File Resolution

V10 needs a reliable way to determine the real target file path.

Recommendation:
Parse target path from planner-output.md or derive it from the step metadata already stored in prompt packets.

Do not hardcode venture-specific repo paths.

## Safety Rules

- do not overwrite target file silently unless operator uses --force
- do not apply empty coder output
- do not run reviewer if apply failed
- do not auto-commit changes
- do not auto-merge changes
- do not suppress file write errors

## Validation Rules

Before apply:

- coder output must be non-empty
- planner output must indicate code changes are required

After apply:

- target file must exist
- target file contents must match applied coder output
- target file must not be empty

## Stop Conditions

V10 must stop if:

- planner-output.md is missing
- coder prompt file is missing
- coder output is empty
- target file cannot be resolved
- target file write fails
- post-apply verification fails

## Logging

V10 should log:

- target file path resolved
- coder output saved
- target file written
- apply verification success/failure
- reviewer execution start
- reviewer output saved

## Reviewer Contract

Reviewer output should only be trusted after target file has actually been updated.

This is the main purpose of V10.

## Non-Goals

V10 is not:

- patch-based editing
- automatic diff merging
- git-aware deployment
- autonomous approval

## Definition of Done

V10 is successful when:

- coder output is captured
- coder output is applied to the real target file
- reviewer runs only after successful apply
- no reviewer pass can exist against an unchanged repo file
