#!/usr/bin/env python3
"""
Operator Router — v1

Reads an Operator Snapshot (JSON) and returns routing output only.
Pure interpreter of the snapshot — no file writes, no ECS/Guardian calls,
no state parsing.

Usage:
    python tools/operator/route_action.py               # reads stdin
    python tools/operator/route_action.py --file <path> # reads file
"""

import argparse
import json
import sys

REQUIRED_FIELDS = [
    "execution_phase",
    "guardian_status",
    "next_action_type",
    "next_command",
]

ACTIONABLE_TYPES = {"execute", "transition", "record_outcome"}

PHASE_REQUIREMENTS = {
    "execute":        "ready",
    "record_outcome": "executed",
    "transition":     "recorded",
}


def _blocked(reason):
    return {
        "next_action_type": "none",
        "next_command":     None,
        "allowed":          False,
        "reason":           reason,
    }


def route(snapshot):
    # Validate required fields present
    for field in REQUIRED_FIELDS:
        if field not in snapshot:
            print(f"ERROR: missing required field '{field}' in snapshot", file=sys.stderr)
            sys.exit(1)

    guardian_status  = snapshot["guardian_status"]
    next_action_type = snapshot["next_action_type"]
    next_command     = snapshot["next_command"]
    execution_phase  = snapshot["execution_phase"]

    # Rule 1: Guardian block
    if guardian_status != "PASS":
        return _blocked("guardian_block")

    # Rule 2: No action available
    if next_action_type == "none":
        return _blocked("no_action")

    # Rule 3: Actionable type with missing command
    if next_action_type in ACTIONABLE_TYPES and not next_command:
        return _blocked("missing_command")

    # Rules 4–6: Phase validation for actionable types
    if next_action_type in PHASE_REQUIREMENTS:
        required_phase = PHASE_REQUIREMENTS[next_action_type]
        if execution_phase != required_phase:
            return _blocked("invalid_phase")

    # Rule 7: Success
    return {
        "next_action_type": next_action_type,
        "next_command":     next_command,
        "allowed":          True,
        "reason":           "ok",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Operator Router: interpret snapshot and return routing output."
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Path to snapshot JSON file (default: read from stdin)",
    )
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, encoding="utf-8") as f:
                raw = f.read()
        except FileNotFoundError:
            print(f"ERROR: file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        except OSError as e:
            print(f"ERROR: cannot read file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        raw = sys.stdin.read()

    try:
        snapshot = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    result = route(snapshot)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
