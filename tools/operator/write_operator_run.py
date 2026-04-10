#!/usr/bin/env python3
"""
Operator Run Recorder — v1

Creates and updates operator run records in operator-runs/.

Usage:
    <stdin> | python tools/operator/write_operator_run.py create
    <stdin> | python tools/operator/write_operator_run.py update --file <path>
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OPERATOR_RUNS_DIR = os.path.join(REPO_ROOT, "operator-runs")

RECORD_VERSION = "1"

CREATE_REQUIRED_FIELDS = [
    "mode",
    "execution_phase",
    "objective_step_raw",
    "ecs_decision_resolved",
    "guardian_status",
    "snapshot_next_action_type",
    "router_next_action_type",
    "router_allowed",
    "router_reason",
    "next_command",
    "context_bundle_refs",
    "instruction_block",
]

VALID_HUMAN_ACTION_STATUSES = {"ran", "skipped", "failed"}

UPDATE_ALLOWED_FIELDS = {"human_action_status", "human_action_notes", "result_artifact_refs"}

IMMUTABLE_FIELDS = {
    "record_version", "recorded_at", "operator_run_id",
    "mode", "execution_phase", "objective_step_raw",
    "ecs_decision_resolved", "guardian_status",
    "snapshot_next_action_type", "router_next_action_type",
    "router_allowed", "router_reason", "next_command",
    "context_bundle_refs", "instruction_block",
}


def _abort(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def _now_utc():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _atomic_write(path, data):
    """Write JSON to a temp file in the same directory, then os.replace to target."""
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        os.replace(tmp_path, path)
    except OSError as e:
        # Clean up temp if possible
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        _abort(f"write failed: {e}")


def cmd_create(stdin_data):
    try:
        payload = json.loads(stdin_data)
    except json.JSONDecodeError as e:
        _abort(f"invalid JSON input: {e}")

    for field in CREATE_REQUIRED_FIELDS:
        if field not in payload:
            _abort(f"Missing required field: {field}")

    ts = _now_utc()
    iso = _now_iso()
    operator_run_id = f"{ts}_operator-run"

    record = {
        "record_version":            RECORD_VERSION,
        "recorded_at":               iso,
        "operator_run_id":           operator_run_id,
        "mode":                      payload["mode"],
        "execution_phase":           payload["execution_phase"],
        "objective_step_raw":        payload["objective_step_raw"],
        "ecs_decision_resolved":     payload["ecs_decision_resolved"],
        "guardian_status":           payload["guardian_status"],
        "snapshot_next_action_type": payload["snapshot_next_action_type"],
        "router_next_action_type":   payload["router_next_action_type"],
        "router_allowed":            payload["router_allowed"],
        "router_reason":             payload["router_reason"],
        "next_command":              payload["next_command"],
        "context_bundle_refs":       payload["context_bundle_refs"],
        "instruction_block":         payload["instruction_block"],
        "human_action_status":       "not_run",
        "human_action_notes":        None,
        "result_artifact_refs":      [],
    }

    filename = f"{ts}_operator-run.json"
    target = os.path.join(OPERATOR_RUNS_DIR, filename)
    _atomic_write(target, record)


def cmd_update(stdin_data, file_path):
    if not os.path.isfile(file_path):
        _abort(f"File not found: {file_path}")

    try:
        with open(file_path, encoding="utf-8") as f:
            record = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        _abort(f"Cannot read record: {e}")

    try:
        payload = json.loads(stdin_data)
    except json.JSONDecodeError as e:
        _abort(f"invalid JSON input: {e}")

    # Single update enforcement
    if record.get("human_action_status") != "not_run":
        _abort("Record already updated")

    # Validate human_action_status value
    new_status = payload.get("human_action_status")
    if new_status is None:
        _abort("Missing required field: human_action_status")
    if new_status not in VALID_HUMAN_ACTION_STATUSES:
        _abort(f"Invalid human_action_status: {new_status!r}. Allowed: {', '.join(sorted(VALID_HUMAN_ACTION_STATUSES))}")

    # Apply allowed fields only
    record["human_action_status"] = new_status
    if "human_action_notes" in payload:
        record["human_action_notes"] = payload["human_action_notes"]
    if "result_artifact_refs" in payload:
        record["result_artifact_refs"] = payload["result_artifact_refs"]

    _atomic_write(file_path, record)


def main():
    parser = argparse.ArgumentParser(
        description="Operator Run Recorder: create and update operator run records."
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("create", help="Create a new operator run record from stdin")

    update_parser = subparsers.add_parser("update", help="Update an existing operator run record")
    update_parser.add_argument("--file", required=True, metavar="PATH", help="Path to record file")

    args = parser.parse_args()

    if args.command is None:
        parser.print_usage(sys.stderr)
        sys.exit(1)

    stdin_data = sys.stdin.read()

    if args.command == "create":
        cmd_create(stdin_data)
    elif args.command == "update":
        cmd_update(stdin_data, args.file)


if __name__ == "__main__":
    main()
