# App Build Classification Policy

## Purpose

Define the job classes and reason codes for the `app_build` workflow type. This policy governs which app build jobs may be executed automatically, which require human review before apply, and which must be blocked entirely. It is the authoritative reference for any future classification logic built for `app_build`. No classification code may be written for `app_build` that contradicts this document.

---

## Status

**Not yet implemented.**

These classes and reason codes are policy placeholders. No classification logic, preflight enforcement, or batch gating exists for `app_build` at this time. This policy must be finalized and reviewed before any implementation begins.

---

## Planned Classes

| Class | Name | Automated Apply Allowed |
|---|---|---|
| A | Auto-Apply Eligible | Yes, under strict conditions |
| B | Review Before Apply | Generation only; human approves apply |
| C | No Automated Execution | Manual execution required |

---

## Class A — Auto-Apply Eligible

Class A is intentionally narrow. Most app builds will not qualify. A job qualifies for Class A only if **all** of the following are true:

- The target path does not exist or is provably empty
- The output is a single self-contained file (not a directory scaffold)
- The goal is a deterministic transformation with no inferred behavior
- The `stack.language` has a supported AST validator
- All `constraints` are independently verifiable at review time
- All `acceptance_criteria` are structurally checkable by the reviewer stage
- No external dependencies are introduced beyond an explicit allowlist
- The planner output demonstrates a one-to-one mapping from spec to output with no invented behavior
- The planner output passes structural validation

**Class A is not appropriate for any job that generates more than one file.**

---

## Class B — Review Before Apply

A job is Class B if any of the following are true:

- The output spans more than one file but is contained within a single `target_path` directory
- The goal requires judgment calls that are derivable from the spec but not mechanically verifiable
- The `acceptance_criteria` include behavioral or UX conditions that cannot be checked structurally
- The `stack` includes a framework the reviewer stage has not been validated against
- The operator is uncertain whether the planner correctly scoped the work

For Class B:
- Planner output must be explicitly reviewed before the coder stage runs
- Coder output must be reviewed against the spec before apply
- Apply must only occur after explicit human confirmation

---

## Class C — No Automated Execution

A job must be Class C if any of the following are true:

- The goal involves architectural decisions not fully specified in the job
- The output requires modifying existing files in the target repo
- The target path contains non-empty content and is not explicitly defined as a full overwrite
- External API calls, service registrations, or infrastructure changes are required at scaffold time
- The `constraints` or `acceptance_criteria` arrays are empty
- The `stack.language` has no supported AST validator
- The planner output cannot pass validation without manual correction
- The job has previously failed Class A or Class B validation more than once

Class C jobs must not proceed through the automated pipeline under any circumstances.

---

## Planned Reason Codes

| Reason Code | Class | Meaning |
|---|---|---|
| `A_MINIMAL_SCAFFOLD` | A | Single-file, fully specified, deterministic output with no external dependencies |
| `B_REVIEW_REQUIRED` | B | Multi-file or judgment-requiring output; generation allowed, apply requires human sign-off |
| `C_MULTI_FILE_APP` | C | Output requires generating a directory of files; not safe for automated apply |
| `C_AMBIGUOUS_SPEC` | C | Goal, constraints, or acceptance_criteria are underspecified or contradictory |
| `C_EXTERNAL_DEP_RISK` | C | Job introduces external dependencies or service interactions not in the allowlist |

---

## Disqualifiers for Class A

Any of the following immediately removes Class A eligibility:

- Output is more than one file
- `target_path` is non-empty and the job is not explicitly a full deterministic overwrite
- `constraints` array is empty
- `acceptance_criteria` array is empty
- Planner output contains invented behavior not derivable from the spec
- Coder output contains markdown fences or prose markers
- Coder output fails AST parse for the declared `stack.language`
- Reviewer output is missing any required schema field
- Any external dependency is introduced that is not in the explicit allowlist

---

## Notes

- `A_MINIMAL_SCAFFOLD` is expected to be rare. Most real app builds will be Class B or C.
- `C_MULTI_FILE_APP` is the expected default class for any job whose `target_path` is a directory. Multi-file automated apply is explicitly out of scope until a safe multi-file apply stage is built and validated.
- Reason codes are machine-readable. They must be short, uppercase, and underscore-separated. No new reason codes may be added without updating this document.
- Class A / `A_MINIMAL_SCAFFOLD` semantics are entirely separate from `code_migration` Class A / `A_EXACT_PORT`. The two classification systems must not share logic.
- This policy governs `workflow_spec_version: "1"` only.
