# Current Objective

## Current Objective

Execute approved migration work through the controlled execution path while maintaining Guardian enforcement, policy integrity, and state correctness.

---

## Why This Is The Current Objective

The system is in migration-execution mode. Only approved migration work may proceed, and all execution must remain gated by Guardian, ECS, and policy controls.

---

## Immediate Next Steps

1. Execute approved migration work through the controlled queue path
2. Preserve Guardian enforcement and policy integrity during execution
3. Return to system-building mode if control gaps, drift, or blocking issues are discovered

---

## Success Condition

This objective is complete when:

1. approved migration work for the selected queue-state has been executed or intentionally halted
2. Guardian and policy controls remain intact during execution
3. any newly discovered control gaps are brought back into system-building mode explicitly

---

## Current Constraints

- do not bypass Guardian, ECS, or policy enforcement
- do not execute unapproved or out-of-scope migration work
- do not expand workflow types beyond code_migration
- do not silently change objective direction during execution

---

## Not Doing Yet

- app_build execution
- automation_build execution
- ui_conversion execution
- multi-agent orchestration
- autonomous objective switching
- uncontrolled automation

---

## Transition Basis

manifest_test

---

## Approved Basis

This objective was written by ai_factory_transition.py through an explicit operator transition.
