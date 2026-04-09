#!/usr/bin/env python3
"""
Instruction Generator — v1

Consumes Operator Snapshot, Router Output, and Context Bundle.
Produces a single structured instruction block. Pure translator only —
no decisions, no ECS/Guardian calls, no file writes.

Usage:
    python tools/operator/generate_instruction.py               # reads stdin
    python tools/operator/generate_instruction.py --file <path> # reads file

Input JSON structure:
    {
      "snapshot": {...},
      "router":   {...},
      "context":  {...}
    }
"""

import argparse
import json
import sys


def _abort(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def _require(d, field, source):
    if field not in d:
        _abort(f"missing required field '{field}' in {source}")
    return d[field]


def _context_lines(refs):
    if not refs:
        return ""
    return "\n".join(refs)


def build_instruction(snapshot, router, context):
    # Extract required fields
    _require(snapshot, "mode",            "snapshot")
    _require(snapshot, "execution_phase", "snapshot")

    next_action_type = _require(router, "next_action_type", "router")
    next_command     = _require(router, "next_command",     "router")
    allowed          = _require(router, "allowed",          "router")
    reason           = _require(router, "reason",           "router")

    refs = _require(context, "context_bundle_refs", "context")

    ctx_block = _context_lines(refs)

    # Template selection order
    if not allowed:
        block = (
            f"ACTION: NONE\n"
            f"\n"
            f"REASON:\n"
            f"{reason}\n"
            f"\n"
            f"CONTEXT:\n"
            f"{ctx_block}"
        )
        return block

    if next_action_type == "none":
        block = (
            f"ACTION: NONE\n"
            f"\n"
            f"REASON:\n"
            f"no_action\n"
            f"\n"
            f"CONTEXT:\n"
            f"{ctx_block}"
        )
        return block

    if next_action_type == "execute":
        block = (
            f"ACTION: EXECUTE\n"
            f"\n"
            f"COMMAND:\n"
            f"{next_command}\n"
            f"\n"
            f"CONTEXT:\n"
            f"{ctx_block}"
        )
        return block

    if next_action_type == "record_outcome":
        block = (
            f"ACTION: RECORD_OUTCOME\n"
            f"\n"
            f"COMMAND:\n"
            f"{next_command}\n"
            f"\n"
            f"CONTEXT:\n"
            f"{ctx_block}"
        )
        return block

    if next_action_type == "transition":
        cmd_line = str(next_command) if next_command is not None else "null"
        block = (
            f"ACTION: TRANSITION\n"
            f"\n"
            f"COMMAND:\n"
            f"{cmd_line}\n"
            f"\n"
            f"REQUIRED_INPUT:\n"
            f"target_mode\n"
            f"\n"
            f"CONTEXT:\n"
            f"{ctx_block}"
        )
        return block

    _abort(f"unrecognized next_action_type: {next_action_type!r}")


def main():
    parser = argparse.ArgumentParser(
        description="Instruction Generator: translate snapshot/router/context into instruction block."
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Path to combined input JSON file (default: read from stdin)",
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
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        _abort(f"invalid JSON input: {e}")

    snapshot = _require(payload, "snapshot", "input")
    router   = _require(payload, "router",   "input")
    context  = _require(payload, "context",  "input")

    instruction_block = build_instruction(snapshot, router, context)
    print(json.dumps({"instruction_block": instruction_block}, indent=2))


if __name__ == "__main__":
    main()
