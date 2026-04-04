# Automation Build Classification Policy

## Purpose

Define the job classes and reason codes for the `automation_build` workflow type. This policy governs which automation build jobs may be executed automatically, which require human review before apply, and which must be blocked entirely. It is the authoritative reference for any future classification logic built for `automation_build`. No classification code may be written for `automation_build` that contradicts this document.

---

## Status

**Not yet implemented.**

These classes and reason codes are policy placeholders. No classification logic, preflight enforcement, or batch gating exists for `automation_build` at this time. This policy must be finalized and reviewed before any implementation begins.

---

## Planned Classes

| Class | Name | Automated Apply Allowed |
|---|---|---|
| A | Auto-Apply Eligible | Yes, under strict conditions |
| B | Review Before Apply | Generation only; human approves apply |
| C | No Automated Execution | Manual execution required |

---

## Class A — Auto-Apply Eligible

Class A is intentionally narrow. Most automation builds will not qualify. A job qualifies for Class A only if **all** of the following are true:

- The output is a single self-contained file
- `target_path` does not exist or is provably empty
- `automation_type` is `"shell_script"` or `"cron_job"` — types with deterministic, statically validatable output
- The declared `runtime` has a supported static validator (e.g., shellcheck for bash)
- All `constraints` are independently verifiable via static analysis
- All `acceptance_criteria` are structurally checkable without runtime execution
- The automation does not interact with external services, infrastructure, or credentials
- The planner output demonstrates a one-to-one mapping from spec to output with no invented behavior
- The planner output passes structural validation

**Class A is not appropriate for `ci_pipeline` automation types, multi-file output, or any automation that touches infrastructure state.**

---

## Class B — Review Before Apply

A job is Class B if any of the following are true:

- `automation_type` is `"ci_pipeline"`
- The output is a single file but contains external service references that are declared and bounded
- The `acceptance_criteria` include conditions that require structural inspection beyond static analysis
- The `runtime` is not bash (e.g., a shell script targeting a non-standard interpreter)
- The operator is uncertain whether the planner correctly scoped the work

For Class B:
- Planner output must be explicitly reviewed before the coder stage runs
- Coder output must be reviewed against the spec and validated before apply
- Apply must only occur after explicit human confirmation

---

## Class C — No Automated Execution

A job must be Class C if any of the following are true:

- The output spans more than one file
- The automation registers services, modifies infrastructure state, or creates external resources
- The automation requires credentials or secrets at generation time
- The goal involves logic not fully derivable from the spec (architectural decisions, branching behavior not specified in constraints)
- `constraints` or `acceptance_criteria` arrays are empty
- The `automation_type` is not in the supported allowlist for this contract version
- The `runtime` has no supported static validator
- The planner output cannot pass validation without manual correction
- The job has previously failed Class A or Class B validation more than once

Class C jobs must not proceed through the automated pipeline under any circumstances.

---

## Planned Reason Codes

| Reason Code | Class | Meaning |
|---|---|---|
| `A_MINIMAL_AUTOMATION` | A | Single-file, statically validatable, no infrastructure interaction, fully specified |
| `B_REVIEW_REQUIRED` | B | Single-file but review-required due to automation_type, runtime, or criteria complexity |
| `C_INFRA_RISK` | C | Automation touches infrastructure state, external services, or requires credentials |
| `C_MULTI_FILE_AUTOMATION` | C | Output requires more than one file; not safe for automated apply |
| `C_AMBIGUOUS_SPEC` | C | Goal, constraints, or acceptance_criteria are underspecified or contradictory |

---

## Disqualifiers for Class A

Any of the following immediately removes Class A eligibility:

- Output is more than one file
- `automation_type` is `"ci_pipeline"`
- `target_path` is non-empty and the job is not explicitly a full deterministic overwrite
- `constraints` array is empty
- `acceptance_criteria` array is empty
- Any acceptance criterion requires runtime execution to verify
- The automation references external services, APIs, or credentials
- Planner output contains invented behavior not derivable from the spec
- Coder output fails static validation for the declared `runtime`
- Reviewer output is missing any required schema field

---

## Notes

- `A_MINIMAL_AUTOMATION` is expected to be rare. Shell scripts that are fully self-contained, statically validatable, and touch no external state are the only realistic candidates.
- `C_INFRA_RISK` takes precedence over all other classes. Any automation that could affect infrastructure state or external services is Class C regardless of size or spec quality.
- Reason codes are machine-readable. They must be short, uppercase, and underscore-separated. No new reason codes may be added without updating this document.
- Class A / `A_MINIMAL_AUTOMATION` semantics are entirely separate from `code_migration` Class A / `A_EXACT_PORT` and `app_build` Class A / `A_MINIMAL_SCAFFOLD`. The three classification systems must not share logic.
- `ci_pipeline` is hardcoded to Class B minimum. It must never be classified as Class A regardless of spec quality, because CI pipeline changes affect shared infrastructure by definition.
- This policy governs `workflow_spec_version: "1"` only.
