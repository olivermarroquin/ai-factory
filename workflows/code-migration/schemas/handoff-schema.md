# Code Migration Handoff Schema

## Purpose

Standardize what one agent passes to the next.

## Analyzer → Planner

```json
{
  "source_file": "",
  "classification": "",
  "role": "",
  "preserve": [],
  "leave_behind": [],
  "recommended_next_scope": "",
  "notes": []
}
```

## Planner → Coder

```json
{
  "target_file": "",
  "target_scope": "",
  "goal": "",
  "constraints": [],
  "do_not_touch": [],
  "source_context_required": true,
  "expected_output": ""
}
```

## Coder → Reviewer

```json
{
  "target_file": "",
  "changes_made": "",
  "notes": [],
  "blocked_on": []
}
```

## Reviewer → Operator

```json
{
  "status": "pass|revise",
  "correct": [],
  "issues": [],
  "drift_detected": false,
  "next_safe_step": ""
}
```
