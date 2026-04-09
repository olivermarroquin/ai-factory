#!/usr/bin/env python3
"""
Operator Entrypoint — v1

Orchestrates: snapshot → router → context → instruction.
No new logic — calls existing operator modules in order.

Usage:
    python tools/operator/run_operator.py              # instruction block (default)
    python tools/operator/run_operator.py --instruction
    python tools/operator/run_operator.py --json
"""

import argparse
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

SNAPSHOT_TOOL    = os.path.join(REPO_ROOT, "tools", "operator", "generate_snapshot.py")
ROUTER_TOOL      = os.path.join(REPO_ROOT, "tools", "operator", "route_action.py")
CONTEXT_TOOL     = os.path.join(REPO_ROOT, "tools", "operator", "build_context_bundle.py")
INSTRUCTION_TOOL = os.path.join(REPO_ROOT, "tools", "operator", "generate_instruction.py")


def _abort(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


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
    args = parser.parse_args()

    # Step 1 — Generate Snapshot
    snapshot = _run(SNAPSHOT_TOOL)

    snapshot_json = json.dumps(snapshot)

    # Step 2 — Route Action
    router = _run(ROUTER_TOOL, stdin_data=snapshot_json)

    # Step 3 — Build Context
    context = _run(CONTEXT_TOOL, stdin_data=snapshot_json)

    # Step 4 — Generate Instruction
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
