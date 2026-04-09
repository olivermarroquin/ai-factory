#!/usr/bin/env python3
"""
Operator Entrypoint — v1

Orchestrates: snapshot → router → context → instruction.
No new logic — calls existing operator modules in order.

Usage:
    python tools/operator/run_operator.py              # instruction block (default)
    python tools/operator/run_operator.py --instruction
    python tools/operator/run_operator.py --json
    python tools/operator/run_operator.py --transition-to <mode>
"""

import argparse
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

VALID_TRANSITION_MODES = {"system-building", "migration-execution"}

SNAPSHOT_TOOL    = os.path.join(REPO_ROOT, "tools", "operator", "generate_snapshot.py")
ROUTER_TOOL      = os.path.join(REPO_ROOT, "tools", "operator", "route_action.py")
CONTEXT_TOOL     = os.path.join(REPO_ROOT, "tools", "operator", "build_context_bundle.py")
INSTRUCTION_TOOL = os.path.join(REPO_ROOT, "tools", "operator", "generate_instruction.py")


def _abort(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


VALID_EXECUTION_PHASES = {"idle", "ready", "executing", "executed", "recorded"}

PHASE_REQUIRED_BY_ACTION = {
    "execute":        {"ready"},
    "record_outcome": {"executed"},
    "transition":     {"idle", "recorded"},
}


def _validate_snapshot(snapshot):
    """
    Validate snapshot fields before routing. Exits non-zero on first failure.
    Prints errors to stderr only.
    """
    required_fields = [
        "mode",
        "execution_phase",
        "objective_step_raw",
        "ecs_decision_resolved",
        "guardian_status",
        "next_action_type",
    ]
    for field in required_fields:
        if field not in snapshot:
            _abort(f"Invalid snapshot: missing field {field}")

    phase = snapshot["execution_phase"]
    if phase not in VALID_EXECUTION_PHASES:
        _abort(f"Invalid snapshot: invalid execution_phase value: {phase!r}")

    action = snapshot["next_action_type"]
    if action in PHASE_REQUIRED_BY_ACTION:
        allowed_phases = PHASE_REQUIRED_BY_ACTION[action]
        if phase not in allowed_phases:
            expected = " or ".join(f"execution_phase={p!r}" for p in sorted(allowed_phases))
            _abort(f"Invalid snapshot: {action} requires {expected}, got {phase!r}")


def _run(tool, stdin_data=None):
    """
    Run a tool as a subprocess. Pass stdin_data (str) if provided.
    Returns parsed JSON dict. Aborts on non-zero exit or invalid JSON.
    """
    tool_name = os.path.basename(tool)
    try:
        result = subprocess.run(
            [sys.executable, tool],
            input=stdin_data,
            capture_output=True,
            text=True,
        )
    except OSError as e:
        _abort(f"{tool_name} could not be launched: {e}")

    if result.returncode != 0:
        stderr_snippet = result.stderr.strip()
        print(result.stderr, file=sys.stderr, end="")
        _abort(f"{tool_name} exited {result.returncode}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        _abort(f"{tool_name} produced invalid JSON: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Operator Entrypoint: snapshot → router → context → instruction."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--instruction",
        action="store_true",
        default=False,
        help="Output instruction block only (default behavior)",
    )
    group.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output full structured result as JSON",
    )
    parser.add_argument(
        "--transition-to",
        default=None,
        metavar="MODE",
        help="Inject transition command for the given mode (system-building or migration-execution)",
    )
    args = parser.parse_args()

    # Step 1 — Generate Snapshot
    snapshot = _run(SNAPSHOT_TOOL)

    # Validation gate — before routing
    _validate_snapshot(snapshot)

    snapshot_json = json.dumps(snapshot)

    # Step 2 — Route Action
    router = _run(ROUTER_TOOL, stdin_data=snapshot_json)

    # Step 3 — Transition injection (in-memory only, before context/instruction)
    if args.transition_to is not None:
        mode = args.transition_to

        # Validate mode value
        if mode not in VALID_TRANSITION_MODES:
            _abort(
                f"invalid --transition-to value: {mode!r}. "
                f"Allowed: {', '.join(sorted(VALID_TRANSITION_MODES))}"
            )

        # Validate router state allows injection.
        # The router converts transition-with-null-command to next_action_type="none"
        # (Rule 3 in route_action.py). The authoritative signal is snapshot.next_action_type
        # == "transition" combined with router.reason == "missing_command".
        if not (
            snapshot.get("next_action_type") == "transition"
            and router.get("allowed") is False
            and router.get("reason") == "missing_command"
        ):
            _abort(
                "--transition-to is only valid when snapshot.next_action_type=transition "
                "and router.allowed=false and router.reason=missing_command. "
                f"Current state: snapshot.next_action_type={snapshot.get('next_action_type')!r}, "
                f"router.allowed={router.get('allowed')!r}, router.reason={router.get('reason')!r}"
            )

        # Inject command — override router in-memory only
        cmd = f'./ai-factory-transition --to {mode} --reason "operator_transition"'
        router = {
            "next_action_type": "transition",
            "next_command":     cmd,
            "allowed":          True,
            "reason":           "ok",
        }

    # Step 4 — Build Context (uses original snapshot; router override is separate)
    context = _run(CONTEXT_TOOL, stdin_data=snapshot_json)

    # Step 5 — Generate Instruction
    combined = json.dumps({
        "snapshot": snapshot,
        "router":   router,
        "context":  context,
    })
    instruction = _run(INSTRUCTION_TOOL, stdin_data=combined)

    # Output
    if args.json:
        output = {
            "snapshot":    snapshot,
            "router":      router,
            "context":     context,
            "instruction": instruction,
        }
        print(json.dumps(output, indent=2))
    else:
        # --instruction or default: print instruction_block string only
        block = instruction.get("instruction_block", "")
        print(block)


if __name__ == "__main__":
    main()
