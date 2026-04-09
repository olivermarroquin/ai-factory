#!/usr/bin/env python3
"""
Context Bundle Builder — v1

Reads an Operator Snapshot (JSON) and returns the minimal repo file set
required for the current next action. Pure snapshot-to-context mapper —
no file writes, no ECS/Guardian calls, no repo scanning.

Usage:
    python tools/operator/build_context_bundle.py               # reads stdin
    python tools/operator/build_context_bundle.py --file <path> # reads file
"""

import argparse
import json
import sys

VALID_ACTION_TYPES = {"execute", "transition", "record_outcome", "none"}

# Fields required per action type (beyond base context_bundle_refs)
ACTION_REQUIRED_FIELDS = {
    "execute":        ["active_queue_state"],
    "record_outcome": ["active_queue_state", "active_queue_run"],
    "transition":     ["active_outcome_record", "active_queue_state"],
    "none":           [],
}


def _abort(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def build(snapshot):
    # Validate next_action_type
    next_action_type = snapshot.get("next_action_type")
    if next_action_type not in VALID_ACTION_TYPES:
        _abort(f"invalid next_action_type: {next_action_type!r}")

    # Validate context_bundle_refs present
    if "context_bundle_refs" not in snapshot:
        _abort("missing required field 'context_bundle_refs' in snapshot")

    base_refs = snapshot["context_bundle_refs"]
    if not isinstance(base_refs, list):
        _abort("'context_bundle_refs' must be a list")

    # Validate action-specific required fields are present and non-null
    for field in ACTION_REQUIRED_FIELDS[next_action_type]:
        if field not in snapshot:
            _abort(f"missing required field '{field}' for action '{next_action_type}'")
        if snapshot[field] is None:
            _abort(f"required field '{field}' is null for action '{next_action_type}'")

    # Build ordered, deduplicated ref list
    seen = set()
    refs = []

    def _add(path):
        if path is not None and path not in seen:
            seen.add(path)
            refs.append(path)

    # Rule 1: base files always first
    for ref in base_refs:
        _add(ref)

    # Action-specific additions
    if next_action_type == "execute":
        # Rule 2
        _add(snapshot["active_queue_state"])

    elif next_action_type == "record_outcome":
        # Rule 3
        _add(snapshot["active_queue_state"])
        _add(snapshot["active_queue_run"])

    elif next_action_type == "transition":
        # Rule 4
        _add(snapshot["active_outcome_record"])
        _add(snapshot["active_queue_state"])

    # Rule 5 (none): base only — no additions

    return {
        "next_action_type":    next_action_type,
        "context_bundle_refs": refs,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Context Bundle Builder: map snapshot to minimal context file set."
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
            _abort(f"file not found: {args.file}")
        except OSError as e:
            _abort(f"cannot read file: {e}")
    else:
        raw = sys.stdin.read()

    try:
        snapshot = json.loads(raw)
    except json.JSONDecodeError as e:
        _abort(f"invalid JSON input: {e}")

    result = build(snapshot)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
