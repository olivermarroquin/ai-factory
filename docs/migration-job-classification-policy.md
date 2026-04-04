# Migration Job Classification Policy

## Purpose

Define the conditions under which a code migration job may be executed automatically, executed with human review of apply, or must be handled manually. This policy governs use of the `run-migration-execute` pipeline.

---

## Job Classes

| Class | Name | Automated Apply Allowed |
|---|---|---|
| A | Auto-Apply Eligible | Yes, via `auto-openai` |
| B | Review Before Apply | Generation only; human approves apply |
| C | No Automated Execution | Manual execution required |

---

## Class A — Auto-Apply Eligible

A job qualifies for Class A if **all** of the following are true:

- The source file is a single, self-contained Python module
- The target file is new or empty
- The migration goal is a faithful port or deterministic transformation (no new behavior)
- The planner output passes structural validation
- The coder output passes syntax, import, and function-signature validation
- The reviewer output passes schema validation
- No architecture boundaries are crossed
- No shared utilities, base classes, or external interfaces are modified
- The job scope is limited to one target file
- The planner output demonstrates a one-to-one mapping from source to target with no inferred or new behavior

---

## Class B — Review Before Apply

A job is Class B if any of the following are true:

- The target file already contains non-trivial content
- The migration adds new logic not present in the source
- The goal introduces new function signatures or public interfaces
- The source file is large (>300 lines) or has ambiguous responsibilities
- The job touches a file that is imported by other modules in the repo
- The operator is uncertain whether the planner correctly scoped the work

For Class B:
- Planner output must be explicitly approved before trusting coder output
- Coder output must be reviewed against the source to confirm no unintended behavior changes
- Apply must only occur after explicit human confirmation

---

## Class C — No Automated Execution

A job must be Class C if any of the following are true:

- The migration involves refactoring, architectural change, or interface redesign
- Multiple target files must change together
- The source is not a Python file
- The job requires judgment calls that are not derivable from the source text
- The planner output cannot pass validation without manual correction
- The job has previously failed Class A validation more than once

Class C jobs must be executed fully manually. Artifacts may still be scaffolded via `run-migration-start`.

---

## Disqualifiers for Class A

Any of the following immediately removes Class A eligibility:

- `planner_valid` is false
- Coder output contains markdown fences or prose markers
- Coder output fails AST parse
- Coder output is missing required imports or function signatures
- Reviewer output is missing any required schema field
- The target path cannot be resolved from planner output
- The target file is non-empty and the job is not explicitly defined as a full deterministic overwrite

---

## Allowed Execution Behavior by Class

| Stage | Class A | Class B | Class C |
|---|---|---|---|
| Analyzer | Auto | Auto or manual | Manual |
| Planner | Auto | Auto or manual | Manual |
| Coder | Auto | Auto | Manual |
| Apply | Auto | Human-approved | Manual |
| Reviewer | Auto | Manual | Manual |

---

## Minimum Preconditions Before Apply

Regardless of class, apply must not proceed unless:

1. The planner output contains all required sections and passes drift-term validation
2. The coder output passes syntax validation (AST parse)
3. The coder output contains all required imports and function signatures when source context is required
4. The target parent directory exists
5. A run manifest will be written regardless of outcome

---

## Notes

- The manifest records `failed_stage` and `applied_target_path` per run. Use `./show-latest-manifest` to inspect.
- Class A is intentionally narrow. When in doubt, use Class B.
- Unattended batch execution is not yet supported. Each run must be operator-initiated.
- This policy should be enforced by a preflight check before `auto-openai` is invoked.
- Job class must be declared before execution begins, not inferred after the fact.
- Reviewer validation enforces structure only; it does not guarantee semantic correctness
- In future batch execution, any Class A failure must halt the batch unless explicitly overridden
