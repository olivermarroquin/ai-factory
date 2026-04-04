# Code Migration Operator Playbook

## Purpose

This playbook defines how to run the code-migration workflow manually in a consistent, repeatable way.

It is the human-operated version of the future automated code-migration pipeline.

## Goal

Migrate useful logic from an old system into a new system without:

- blindly copying files
- dragging local CLI behavior into the new app
- breaking architecture boundaries
- allowing vague AI coding behavior

---

## Core Workflow

source file
→ analyzer
→ planner
→ coder
→ reviewer
→ approved next step

---

## Roles and Tools

### Operator

The human operator controls scope, reviews outputs, and decides whether to continue.

### Analyzer

Used to classify source code and identify what should be migrated.

### Planner

Used to convert analysis into a narrow implementation instruction.

### Coder

Used to implement one small migration step in one target file.

### Reviewer

Used to verify whether the implementation stayed on scope and respected architecture.

### Tools

- ChatGPT = analyzer / planner / reviewer
- Claude Code = coder
- local repo = source of truth for code
- ai-factory = workflow and venture context
- ai-agency-core = reusable prompt templates

---

## Inputs Required Before Starting

Before starting a migration step, the operator must know:

1. source file
2. target repo
3. target file
4. migration goal
5. current target architecture
6. what has already been migrated

---

## Step 1 — Prepare Context

### Actions

- identify the source file
- identify the target file
- confirm the migration goal
- confirm the current file state

### Save / Update

- source mapping docs in venture wrapper
- engine extraction notes
- backend service map if needed

### Rule

Do not start coding until the source and target are clearly defined.

---

## Step 2 — Run Analyzer

### Inputs

- source file path
- source code content
- migration goal
- target architecture context

### Prompt Source

- `ai-agency-core/prompts/code-migration/analyzer-prompt.md`

### Output

The analyzer should return:

- classification
- role
- preserve
- leave_behind
- recommended_next_scope
- notes

### Save Output

Save analyzer output into a venture-specific note if the step is meaningful enough to keep.

Example location:

- `ai-factory/ventures/<venture>/notes/`

### Rule

Do not ask the coder to implement anything until the file has been classified.

---

## Step 3 — Run Planner

### Inputs

- analyzer output
- target file path
- current target file state
- architecture constraints
- optional source snippet

### Prompt Source

- `ai-agency-core/prompts/code-migration/planner-prompt.md`

### Output

The planner should return:

- target_file
- target_scope
- goal
- constraints
- do_not_touch
- source_context_required
- implementation_prompt

### Rule

The planner must define one narrow implementation step only.

Good scope examples:

- implement one helper function
- migrate one validation function
- wire one service function

Bad scope examples:

- refactor whole module
- convert full repo
- redesign architecture

---

## Step 4 — Run Coder

### Inputs

- target file
- implementation prompt
- optional source snippet

### Tool

- Claude Code

### Prompt Source

- `ai-agency-core/prompts/code-migration/coder-prompt.md`

### Output

The coder should return:

- exact code change
- short explanation
- any blocking issue

### Rule

The coder must not:

- modify unrelated functions
- perform broad cleanup
- redesign architecture
- continue if more context is required without saying so

---

## Step 5 — Review the Result

### Inputs

- updated target file
- original migration instruction
- expected output contract

### Prompt Source

- `ai-agency-core/prompts/code-migration/reviewer-prompt.md`

### Output

The reviewer should return:

- status
- correct
- issues
- drift_detected
- next_safe_step

### Rule

Do not continue to the next migration step until the current one is reviewed.

---

## Step 6 — Apply / Commit / Record

### Actions

If the change is acceptable:

- keep the edit
- optionally test it
- commit it when appropriate
- update venture notes if the step changed system understanding

### Suggested Commit Style

Use commits like:

- `extract resume line reader into service`
- `implement deterministic section extraction`
- `add proposal validation service`

### Rule

Prefer small commits aligned with migration steps.

---

## Step 7 — Decide Next Step

The operator decides whether to:

- continue with the next migration step
- stop and document blockers
- revise the current step
- update architecture docs

### Rule

Never chain too many migrations without review.
One file, one function, one responsibility is preferred.

---

## Recommended File Artifacts Per Migration Step

### Minimum

- target file updated
- reviewer result captured in chat or notes

### Better

- analyzer result saved
- planner result saved
- reviewer result saved

### Best

- all handoff outputs saved in a venture-specific folder

Example:
`ai-factory/ventures/resume-saas/migration-logs/`

---

## Stop Conditions

Stop and do not continue automatically if:

- source file role is unclear
- target architecture is unclear
- coder wants to modify unrelated functions
- reviewer detects drift
- source assumptions are still unknown
- the next step is larger than one narrow scope

---

## Quality Rules

Every migration step should be:

- narrow
- deterministic where possible
- architecture-safe
- reviewable
- reversible

---

## Example Pattern

Example:

1. analyze `rf_docx_extract.py`
2. plan `read_docx_lines` migration
3. coder implements helper in `resume_parser.py`
4. reviewer checks scope
5. commit
6. plan next step: section extraction
7. repeat

---

## Long-Term Role

This playbook exists so that the current human-operated process can later be converted into:

- a runner
- a multi-agent workflow
- a partially autonomous code migration system

It is not the end state.
It is the bridge to the end state.
