# Current Objective

## Current Objective

Re-establish full system control by enforcing execution correctness, preventing drift, and aligning all execution with system state and policy.

---

## Why This Is The Current Objective

Verified repo reality shows:

- the migration system is real and operational
- ECS exists but does not control runtime execution
- Guardian exists but does not gate runtime execution
- Context transfer is still manual
- official state had drifted and required reconciliation

Because of that, the system's bottleneck is no longer basic migration proof.

The bottleneck is enforcement.

---

## Immediate Next Steps

1. Strengthen Guardian enforcement to fully prevent execution drift across all workflows
2. Align ECS decisions with execution paths to eliminate ambiguity in next-step selection
3. Ensure all execution is gated by validated system state, policy, and objective alignment

---

## Success Condition

This objective is complete when:

1. execution cannot proceed without a Guardian pass
2. invalid or stale system state can block execution before runtime begins
3. the control layer is more than documentation and manual discipline

---

## Current Constraints

- do not execute migration work while system enforcement is incomplete
- do not expand workflow types beyond code_migration
- do not bypass Guardian or ECS checks
- do not introduce automation before control is fully enforced

---

## Not Doing Yet

- app_build execution
- automation_build execution
- ui_conversion execution
- multi-agent orchestration
- broad cleanup of product repo structure
- non-essential feature work in resume-saas

---

## Approved Basis

This objective is based on the approved reconciliation baseline and verified repo reality from the latest inspection.
