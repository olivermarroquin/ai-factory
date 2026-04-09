#!/usr/bin/env python3
"""
ai-factory post-execution outcome recording command.

Records the outcome of a completed migration queue run, updates the state
surface, and writes an auditable outcome record.

This is NOT a retry tool. This is NOT a transition command.
It records what happened after execution and updates state surface accordingly.

Usage:
    python ai_factory_record_outcome.py --queue-state <path> --outcome succeeded [--notes "<text>"]
    python ai_factory_record_outcome.py --queue-state <path> --outcome failed [--notes "<text>"]
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Repo layout
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.dirname(__file__))

STATE_FILES = {
    "current-system-state.md": os.path.join(REPO_ROOT, "system-state", "current-system-state.md"),
    "current-objective.md":    os.path.join(REPO_ROOT, "system-state", "current-objective.md"),
    "authoritative-files.md":  os.path.join(REPO_ROOT, "system-state", "authoritative-files.md"),
}

SYSTEM_STATE_PATH = STATE_FILES["current-system-state.md"]
SYSTEM_STATE_TMP  = os.path.join(REPO_ROOT, "system-state", ".current-system-state.md.tmp")
OUTCOME_RECORDS_DIR = os.path.join(REPO_ROOT, "outcome-records")
QUEUE_RUNS_DIR      = os.path.join(REPO_ROOT, "queue-runs")
GUARDIAN_ENGINE     = os.path.join(REPO_ROOT, "tools", "guardian", "run_guardian.py")

BLOCK_START = "<!-- EXECUTION_CYCLE_STATUS_START -->"
BLOCK_END   = "<!-- EXECUTION_CYCLE_STATUS_END -->"

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _print(tag, message):
    print(f"[{tag}] {message}")


def _print_block(tag, lines):
    print(f"[{tag}]")
    for line in lines:
        print(f"  {line}")


def _die(tag, lines):
    _print_block(tag, lines)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Step 1 — Read and verify state surface files
# ---------------------------------------------------------------------------

def check_state_files():
    missing = [
        name for name, path in STATE_FILES.items()
        if not os.path.isfile(path)
    ]
    if missing:
        _die("OUTCOME ERROR", [
            "state surface unreadable — missing files:",
            *[f"  {name}" for name in missing],
        ])


# ---------------------------------------------------------------------------
# Step 2 — Read and validate queue-state file
# ---------------------------------------------------------------------------

def load_queue_state(queue_state_path):
    if not os.path.isfile(queue_state_path):
        _die("OUTCOME BLOCK", [f"queue-state file not found: {queue_state_path}"])

    try:
        with open(queue_state_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        _die("OUTCOME BLOCK", [
            f"queue-state file is not valid JSON: {queue_state_path}",
            f"detail: {exc}",
        ])
    except OSError as exc:
        _die("OUTCOME BLOCK", [
            f"queue-state file is not readable: {queue_state_path}",
            f"detail: {exc}",
        ])

    jobs = data.get("jobs")
    if not isinstance(jobs, list) or len(jobs) == 0:
        _die("OUTCOME BLOCK", [
            "queue-state 'jobs' must be a non-empty array",
            f"file: {queue_state_path}",
        ])

    if "batch_status" not in data:
        _die("OUTCOME BLOCK", [
            "queue-state missing 'batch_status' field",
            f"file: {queue_state_path}",
        ])

    return data


# ---------------------------------------------------------------------------
# Step 3 — Verify terminal status
# ---------------------------------------------------------------------------

TERMINAL_STATUSES = {"succeeded", "failed"}


def check_terminal_status(queue_state_data, queue_state_path):
    batch_status = queue_state_data["batch_status"]
    if batch_status not in TERMINAL_STATUSES:
        _die("OUTCOME BLOCK", [
            f"queue-state batch_status is '{batch_status}' — must be 'succeeded' or 'failed' to record outcome",
            f"file: {queue_state_path}",
            "do not record outcome while execution is still in progress",
        ])
    return batch_status


# ---------------------------------------------------------------------------
# Step 4 — Verify declared outcome against actual state
# ---------------------------------------------------------------------------

def verify_outcome_match(declared_outcome, batch_status, jobs, queue_state_path):
    if declared_outcome == "succeeded":
        if batch_status != "succeeded":
            _die("OUTCOME BLOCK", [
                f"declared --outcome succeeded but batch_status is '{batch_status}'",
                f"file: {queue_state_path}",
            ])
        failed_jobs = [
            j for j in jobs
            if isinstance(j, dict) and j.get("status") != "succeeded"
        ]
        if failed_jobs:
            statuses = [j.get("status", "unknown") for j in failed_jobs]
            _die("OUTCOME BLOCK", [
                f"declared --outcome succeeded but {len(failed_jobs)} job(s) do not have status == 'succeeded'",
                f"non-succeeded statuses: {', '.join(statuses)}",
                f"file: {queue_state_path}",
            ])

    elif declared_outcome == "failed":
        if batch_status != "failed":
            _die("OUTCOME BLOCK", [
                f"declared --outcome failed but batch_status is '{batch_status}'",
                f"file: {queue_state_path}",
            ])
        non_succeeded = [
            j for j in jobs
            if isinstance(j, dict) and j.get("status") != "succeeded"
        ]
        if not non_succeeded:
            _die("OUTCOME BLOCK", [
                "declared --outcome failed but all jobs have status == 'succeeded'",
                f"file: {queue_state_path}",
            ])


# ---------------------------------------------------------------------------
# Step 5 — Locate and validate queue run record
# ---------------------------------------------------------------------------

def find_queue_run_record(queue_state_data, queue_state_path):
    """
    Locate the queue run record using two strategies in order:
    1. Read latest_queue_run_record_path from any job in the queue-state.
    2. Scan queue-runs/ for a record whose source_queue_state_path matches.
    """
    jobs = queue_state_data.get("jobs", [])

    # Strategy 1: follow job-embedded reference
    for job in jobs:
        if not isinstance(job, dict):
            continue
        ref = job.get("latest_queue_run_record_path")
        if ref and isinstance(ref, str):
            candidate = ref if os.path.isabs(ref) else os.path.join(REPO_ROOT, ref)
            if os.path.isfile(candidate):
                return _load_queue_run_record(candidate)

    # Strategy 2: scan queue-runs/ directory for matching source_queue_state_path
    abs_queue_state = os.path.realpath(queue_state_path)
    if os.path.isdir(QUEUE_RUNS_DIR):
        candidates = sorted(
            [f for f in os.listdir(QUEUE_RUNS_DIR) if f.endswith(".json")],
            reverse=True,
        )
        for fname in candidates:
            fpath = os.path.join(QUEUE_RUNS_DIR, fname)
            try:
                with open(fpath, encoding="utf-8") as f:
                    record = json.load(f)
                src = record.get("source_queue_state_path", "")
                if src and os.path.realpath(src) == abs_queue_state:
                    return record, fpath
            except (json.JSONDecodeError, OSError):
                continue

    _die("OUTCOME BLOCK", [
        "cannot locate a queue run record for the provided queue-state",
        f"queue-state: {queue_state_path}",
        "ensure the queue run record exists in queue-runs/ or is referenced in job data",
    ])


def _load_queue_run_record(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        _die("OUTCOME BLOCK", [
            f"queue run record is not valid JSON: {path}",
            f"detail: {exc}",
        ])
    except OSError as exc:
        _die("OUTCOME BLOCK", [
            f"queue run record is not readable: {path}",
            f"detail: {exc}",
        ])
    return data, path


# ---------------------------------------------------------------------------
# Step 6 — Duplicate outcome protection
# ---------------------------------------------------------------------------

def check_duplicate(queue_state_path):
    if not os.path.isdir(OUTCOME_RECORDS_DIR):
        return  # no records exist yet

    abs_qs = os.path.realpath(queue_state_path)
    for fname in os.listdir(OUTCOME_RECORDS_DIR):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(OUTCOME_RECORDS_DIR, fname)
        try:
            with open(fpath, encoding="utf-8") as f:
                record = json.load(f)
            stored = record.get("queue_state_path", "")
            if stored and os.path.realpath(stored) == abs_qs:
                _die("OUTCOME BLOCK", [
                    "duplicate outcome record detected for this queue-state",
                    f"queue-state: {queue_state_path}",
                    f"existing record: {fpath}",
                    "outcome for this queue-state has already been recorded",
                ])
        except (json.JSONDecodeError, OSError):
            continue


# ---------------------------------------------------------------------------
# Step 7 — Guardian check
# ---------------------------------------------------------------------------

def run_guardian(label):
    try:
        proc = subprocess.run(
            [sys.executable, GUARDIAN_ENGINE],
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        _die("OUTCOME BLOCK", [
            f"{label}: guardian engine could not be launched",
            f"detail: {exc}",
        ])

    if proc.returncode != 0:
        snippet = proc.stderr.strip()[:400]
        _die("OUTCOME BLOCK", [
            f"{label}: guardian engine exited {proc.returncode}",
            *([f"detail: {snippet}"] if snippet else []),
        ])

    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        _die("OUTCOME BLOCK", [f"{label}: guardian returned invalid JSON"])

    if "status" not in result:
        _die("OUTCOME BLOCK", [f"{label}: guardian output missing 'status' field"])

    if result["status"] != "PASS":
        failures = result.get("failures", [])
        _die("OUTCOME BLOCK", [
            f"{label}: guardian status is {result['status']}",
            f"failed checks: {', '.join(str(f) for f in failures)}",
        ])

    return result


# ---------------------------------------------------------------------------
# Step 8 — Write outcome record
# ---------------------------------------------------------------------------

def write_outcome_record(
    queue_state_path, queue_run_record_path, declared_outcome,
    notes, batch_status, jobs, guardian_status,
):
    os.makedirs(OUTCOME_RECORDS_DIR, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ts_iso    = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record_path = os.path.join(OUTCOME_RECORDS_DIR, f"{timestamp}_outcome.json")

    job_statuses = [
        {"venture": j.get("venture"), "step": j.get("step"), "status": j.get("status")}
        for j in jobs
        if isinstance(j, dict)
    ]

    record = {
        "timestamp":             ts_iso,
        "queue_state_path":      os.path.realpath(queue_state_path),
        "queue_run_record_path": queue_run_record_path,
        "outcome":               declared_outcome,
        "notes":                 notes or "",
        "batch_status":          batch_status,
        "job_statuses":          job_statuses,
        "guardian_status":       guardian_status,
    }

    try:
        with open(record_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
    except OSError as exc:
        _die("OUTCOME ERROR", [
            "failed to write outcome record",
            f"path: {record_path}",
            f"detail: {exc}",
        ])

    # Verify written
    if not os.path.isfile(record_path):
        _die("OUTCOME ERROR", ["outcome record file does not exist after write"])
    try:
        with open(record_path, encoding="utf-8") as f:
            json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        _die("OUTCOME ERROR", [
            "outcome record is not readable/valid after write",
            f"detail: {exc}",
        ])

    return record_path


# ---------------------------------------------------------------------------
# Step 9 — Build execution cycle status block
# ---------------------------------------------------------------------------

REQUIRED_BLOCK_FIELDS = [
    "- queue_state:",
    "- queue_run_record:",
    "- outcome:",
    "- batch_status:",
    "- recorded_at:",
    "### Notes",
]


def build_cycle_block(queue_state_path, queue_run_record_path, declared_outcome, batch_status, notes):
    ts         = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    notes_text = notes.strip() if notes and notes.strip() else "None"

    # Ensure no value is None or empty — each field must be a non-empty string
    qs_val  = str(queue_state_path).strip()   or "<missing>"
    qr_val  = str(queue_run_record_path).strip() or "<missing>"
    out_val = str(declared_outcome).strip()   or "<missing>"
    bs_val  = str(batch_status).strip()       or "<missing>"

    block = (
        f"{BLOCK_START}\n"
        f"## Latest Execution Cycle Status\n\n"
        f"- queue_state: {qs_val}\n"
        f"- queue_run_record: {qr_val}\n"
        f"- outcome: {out_val}\n"
        f"- batch_status: {bs_val}\n"
        f"- recorded_at: {ts}\n\n"
        f"### Notes\n"
        f"{notes_text}\n\n"
        f"{BLOCK_END}\n"
    )

    # Assert all required fields are present before returning
    missing_fields = [f for f in REQUIRED_BLOCK_FIELDS if f not in block]
    if missing_fields:
        _die("OUTCOME ERROR", [
            "execution cycle block is missing required fields — aborting before any write",
            *[f"  missing: {f}" for f in missing_fields],
        ])

    return block


# ---------------------------------------------------------------------------
# Step 10 — Atomic update of current-system-state.md
# ---------------------------------------------------------------------------

def _cleanup_tmp():
    try:
        if os.path.exists(SYSTEM_STATE_TMP):
            os.remove(SYSTEM_STATE_TMP)
    except OSError:
        pass


def atomic_update_system_state(cycle_block):
    try:
        with open(SYSTEM_STATE_PATH, encoding="utf-8") as f:
            original = f.read()
    except OSError as exc:
        _die("OUTCOME ERROR", [
            f"cannot read current-system-state.md: {exc}",
        ])

    # Replace existing block or append new one
    if BLOCK_START in original and BLOCK_END in original:
        start_idx = original.index(BLOCK_START)
        end_idx   = original.index(BLOCK_END) + len(BLOCK_END)
        # consume trailing newline after end marker if present
        if end_idx < len(original) and original[end_idx] == "\n":
            end_idx += 1
        updated = original[:start_idx] + cycle_block + original[end_idx:]
    else:
        # Append — ensure clean separation
        updated = original.rstrip("\n") + "\n\n" + cycle_block

    # Write to temp file
    try:
        with open(SYSTEM_STATE_TMP, "w", encoding="utf-8") as f:
            f.write(updated)
    except OSError as exc:
        _cleanup_tmp()
        _die("OUTCOME ERROR", [
            "failed to write temporary state file",
            f"path: {SYSTEM_STATE_TMP}",
            f"detail: {exc}",
        ])

    # Validate temp file
    try:
        with open(SYSTEM_STATE_TMP, encoding="utf-8") as f:
            written = f.read()
    except OSError as exc:
        _cleanup_tmp()
        _die("OUTCOME ERROR", [
            "cannot read back temporary state file",
            f"detail: {exc}",
        ])

    if not written.strip():
        _cleanup_tmp()
        _die("OUTCOME ERROR", ["temporary state file is empty after write"])

    missing_in_tmp = [f for f in REQUIRED_BLOCK_FIELDS if f not in written]
    if BLOCK_START not in written or BLOCK_END not in written or missing_in_tmp:
        _cleanup_tmp()
        problems = []
        if BLOCK_START not in written:
            problems.append(f"missing block start marker")
        if BLOCK_END not in written:
            problems.append(f"missing block end marker")
        problems.extend([f"missing field: {f}" for f in missing_in_tmp])
        _die("OUTCOME ERROR", [
            "temporary state file is missing required execution cycle content after write",
            *problems,
            "current-system-state.md was NOT modified",
        ])

    # Atomic replace
    try:
        os.replace(SYSTEM_STATE_TMP, SYSTEM_STATE_PATH)
    except OSError as exc:
        _cleanup_tmp()
        _die("OUTCOME ERROR", [
            "atomic replace of current-system-state.md failed",
            f"detail: {exc}",
            "current-system-state.md was NOT modified",
        ])


# ---------------------------------------------------------------------------
# Step 11 — Post-write validation
# ---------------------------------------------------------------------------

def post_write_validate():
    try:
        with open(SYSTEM_STATE_PATH, encoding="utf-8") as f:
            content = f.read()
    except OSError as exc:
        _die("OUTCOME ERROR", [
            f"cannot re-read current-system-state.md after write: {exc}",
            "current-system-state.md has been updated but validation failed",
        ])

    if BLOCK_START not in content or BLOCK_END not in content:
        _die("OUTCOME ERROR", [
            "execution cycle block not found in current-system-state.md after write",
            "current-system-state.md has been updated but is inconsistent",
        ])

    # Post-write Guardian
    try:
        proc = subprocess.run(
            [sys.executable, GUARDIAN_ENGINE],
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        _die("OUTCOME ERROR", [
            "post-write Guardian check: engine could not be launched",
            f"detail: {exc}",
            "current-system-state.md has been updated but transition is NOT confirmed",
        ])

    if proc.returncode != 0:
        snippet = proc.stderr.strip()[:400]
        _die("OUTCOME ERROR", [
            f"post-write Guardian check: engine exited {proc.returncode}",
            *([f"detail: {snippet}"] if snippet else []),
            "current-system-state.md has been updated but transition is NOT confirmed",
        ])

    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        _die("OUTCOME ERROR", [
            "post-write Guardian check: invalid JSON returned",
            "current-system-state.md has been updated but transition is NOT confirmed",
        ])

    if result.get("status") != "PASS":
        failures = result.get("failures", [])
        _die("OUTCOME ERROR", [
            f"post-write Guardian check: status is {result.get('status')}",
            f"failed checks: {', '.join(str(f) for f in failures)}",
            "current-system-state.md has been updated but Guardian does not pass",
            "inspect and correct the state surface manually",
        ])


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="ai-factory post-execution outcome recording command.",
    )
    parser.add_argument(
        "--queue-state",
        metavar="PATH",
        required=True,
        help="Path to the queue-state JSON file for the completed execution",
    )
    parser.add_argument(
        "--outcome",
        choices=["succeeded", "failed"],
        required=True,
        help="Declared execution outcome (succeeded or failed)",
    )
    parser.add_argument(
        "--notes",
        default="",
        help="Optional operator notes for the outcome record",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()
    queue_state_path = args.queue_state
    declared_outcome = args.outcome
    notes            = args.notes

    # 1. Verify state surface
    check_state_files()

    # 2. Load and validate queue-state
    queue_state_data = load_queue_state(queue_state_path)

    # 3. Verify terminal status
    batch_status = check_terminal_status(queue_state_data, queue_state_path)

    # 4. Verify declared outcome vs actual
    jobs = queue_state_data["jobs"]
    verify_outcome_match(declared_outcome, batch_status, jobs, queue_state_path)

    # 5. Locate queue run record
    queue_run_data, queue_run_record_path = find_queue_run_record(queue_state_data, queue_state_path)
    _print("OUTCOME", f"queue run record located: {queue_run_record_path}")

    # 6. Duplicate protection
    check_duplicate(queue_state_path)

    # 7. Pre-write Guardian
    _print("OUTCOME", "pre-write Guardian check ...")
    pre_guardian = run_guardian("pre-write Guardian")
    _print("OUTCOME", "pre-write Guardian: PASS")

    # 8. Write outcome record
    outcome_record_path = write_outcome_record(
        queue_state_path=queue_state_path,
        queue_run_record_path=queue_run_record_path,
        declared_outcome=declared_outcome,
        notes=notes,
        batch_status=batch_status,
        jobs=jobs,
        guardian_status=pre_guardian.get("status"),
    )
    _print("OUTCOME", f"outcome record written: {outcome_record_path}")

    # 9 + 10. Build and atomically write execution cycle block
    cycle_block = build_cycle_block(
        queue_state_path=queue_state_path,
        queue_run_record_path=queue_run_record_path,
        declared_outcome=declared_outcome,
        batch_status=batch_status,
        notes=notes,
    )
    _print("OUTCOME", "updating current-system-state.md ...")
    atomic_update_system_state(cycle_block)
    _print("OUTCOME", "current-system-state.md updated atomically")

    # 11. Post-write validation
    _print("OUTCOME", "post-write validation ...")
    post_write_validate()
    _print("OUTCOME", "post-write Guardian: PASS")

    # Success output
    print()
    _print("OUTCOME OK", f"queue-state:        {queue_state_path}")
    _print("OUTCOME OK", f"queue run record:   {queue_run_record_path}")
    _print("OUTCOME OK", f"outcome record:     {outcome_record_path}")
    _print("OUTCOME OK", f"system-state:       {SYSTEM_STATE_PATH}")

    print()
    if declared_outcome == "failed":
        _print("OUTCOME OK", "advisory: consider ai-factory-transition --to system-building")
    else:
        _print("OUTCOME OK", "advisory: consider another migration run or ai-factory-transition --to system-building")

    sys.exit(0)


if __name__ == "__main__":
    main()
