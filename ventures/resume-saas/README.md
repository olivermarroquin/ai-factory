# Resume SaaS Venture Wrapper

## Purpose

This folder represents the **AI Factory execution wrapper** for the `resume-saas` venture.

It does not contain product source code.

It defines how this venture is:

- executed
- tracked
- validated
- evolved through controlled workflows

---

## System Context

This venture operates within the AI Factory system:

- **ai-factory** → execution + orchestration layer (this folder lives here)
- **resume-saas repo** → product source code (target of execution)
- **second-brain / knowledge OS** → planning, strategy, structured knowledge
- **ai-agency-core** → reusable patterns and standards

This wrapper connects all of them through **controlled execution**.

---

## Role of This Folder

This folder is responsible for:

- mapping execution steps to product changes
- tracking migration and build workflows
- storing venture-specific execution context
- linking artifacts to system state
- enabling future automation and agent-driven execution

It is the **bridge between system execution and product code**.

---

## Current Execution Model

All work for this venture follows the AI Factory model:
state → decision → spec → scope → review → implement → validate → update state

Execution is:

- determined by ECS (Execution Control System)
- validated by System Guardian
- tracked through artifacts and system-state files

---

## Current Workflows

### Code Migration (Active)

The resume-saas venture has been built through controlled migration workflows:

Pipeline:
analyzer → planner → coder → apply → reviewer

All steps:

- produce artifacts
- are validated before progression
- are recorded under venture-specific logs

---

## Artifact Locations

Migration artifacts:
ventures/resume-saas/migration-logs/

Batch + queue execution:
batch-reports/
queue-runs/

These provide full traceability of:

- what was executed
- how it was validated
- what was changed

---

## Source / Target Mapping

- Source logic:
  ~/workspace/repos/resume-factory

- Target product:
  ~/workspace/repos/resume-saas

- Planning + strategy:
  ~/workspace/second-brain/03_ventures/resume-saas

---

## Future Workflows (Planned)

This venture will expand beyond migration into:

- app_build workflows
- automation systems
- feature development pipelines
- agent-assisted execution

All future workflows must:

- follow ECS decisioning
- be scoped before implementation
- produce validation evidence
- pass Guardian checks

---

## Agent Integration (Future)

This folder will support:

- venture-specific agent configs
- execution memory for agents
- reusable patterns derived from this venture
- cross-project learning integration

Agents will:

- read system state
- execute scoped work
- produce artifacts
- update system state

---

## Constraints

- No product source code lives here
- No direct edits to target repo outside controlled execution
- No unscoped work
- No skipping validation steps
- All work must be traceable through artifacts

---

## Exit Condition

This wrapper is correct when:

- execution flow is clearly defined
- artifact locations are consistent
- source/target relationships are clear
- workflows align with AI Factory system
- future automation paths are supported
