# Current System State

## Purpose

Operational snapshot of ai-factory based on reconciled repository reality.

This file reflects what is actually implemented and currently true.

---

## Current Phase

Core System Stabilization — Enforcement Gap

The system is past early migration proof and now needs control-layer alignment.

Current reality:

- migration pipeline is real and proven
- state surface has been reconciled to repo reality
- ECS exists but does not control runtime execution
- Guardian exists but does not gate runtime execution
- Context Engine is not implemented
- resume-saas is the active migration validation harness

---

## Architecture Position

ai-factory is the execution and orchestration layer.

| Layer | Role |
|---|---|
| second-brain | documentation |
| repos | product code |
| ai-agency-core | prompts/templates |
| ai-factory | execution system |

---

## Executable Workflow

Only code_migration is executable.

- workflow_type: code_migration
- workflow_spec_version: "1"
- job_type: migration
- class: A only
- reason codes: A_EXACT_PORT, A_SCHEMA_PORT

Execution path:

run-migration-start → run-migration-preflight → approve-batch-report → run-migration-cycle

---

## Control Layer Status

### ECS
- implemented
- reads state files
- not used by runtime execution

Status: PARTIAL

### Guardian
- implemented checks exist
- runs manually
- not required before execution

Status: PARTIAL

### Context System
- no implementation
- relies on state files only

Status: MISSING

### Knowledge OS
- not present in repo

Status: NOT IMPLEMENTED

---

## Migration System

- fully operational
- queue + policy gating works
- artifacts and manifests produced

Status: COMPLETE (current scope)

---

## resume-saas Status

Implemented:
- API handlers and routes exist
- app.py wired
- orchestrator versions present

Tests:
- 40 passing with PYTHONPATH=.

Empty:
- backend/models/
- backend/utils/

---

## Known Risks

- ECS not controlling execution
- Guardian not enforcing execution
- context transfer manual
- queue policy partially hardcoded
- stale-state coverage incomplete
- orchestrator duplication
- test env dependency

---

## Immediate Next Step

Make Guardian a required pre-execution gate.

---

## Constraints

- do not expand workflows
- do not treat ECS as controlling yet
- do not treat Guardian as enforced yet
- do not expand product scope
