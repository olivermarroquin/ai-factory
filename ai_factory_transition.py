#!/usr/bin/env python3
"""
ai-factory objective transition command.

Performs controlled transitions between system-building and migration-execution
modes by validating preconditions, atomically updating current-objective.md,
and verifying the new state before writing a transition record.

Usage:
    python ai_factory_transition.py --to migration-execution --queue-state <path> --reason "<text>"
    python ai_factory_transition.py --to system-building --reason "<text>"
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
    "current-objective.md":    os.path.join(REPO_ROOT, "system-state", "current-objective.md"),
    "current-system-state.md": os.path.join(REPO_ROOT, "system-state", "current-system-state.md"),
    "authoritative-files.md":  os.path.join(REPO_ROOT, "system-state", "authoritative-files.md"),
}

OBJECTIVE_PATH  = STATE_FILES["current-objective.md"]
OBJECTIVE_TMP   = os.path.join(REPO_ROOT, "system-state", ".current-objective.md.tmp")
RECORDS_DIR     = os.path.join(REPO_ROOT, "transition-records")

GUARDIAN_ENGINE      = os.path.join(REPO_ROOT, "tools", "guardian", "run_guardian.py")
POLICY_INTEGRITY_CHECK = os.path.join(REPO_ROOT, "tools", "guardian", "check_policy_integrity.py")
ECS_RESOLVER         = os.path.join(REPO_ROOT, "tools", "ecs", "resolve_next_action.py")

# ---------------------------------------------------------------------------
# Mode detection keywords
# ---------------------------------------------------------------------------

SYSTEM_BUILDING_KEYWORDS = ["guardian", "enforcement", "ecs", "control", "system"]

# ---------------------------------------------------------------------------
# Objective templates
# ---------------------------------------------------------------------------

TEMPLATE_SYSTEM_BUILDING = """\
# Current Objective

## Current Objective

Re-establish full system control by enforcing execution correctness, preventing drift, and aligning all execution with system state and policy.

---

## Why This Is The Current Objective

The system is in system-building mode. Execution must remain constrained until control enforcement, policy integrity, and objective alignment are stable.

---

## Immediate Next Steps

1. Strengthen Guardian enforcement to fully prevent execution drift across all workflows
2. Align ECS decisions with execution paths to eliminate ambiguity in next-step selection
3. Ensure all execution is gated by validated system state, policy, and objective alignment

---

## Success Condition

This objective is complete when:

1. execution cannot proceed without a Guardian pass
2. invalid or stale system state can block execution before runtime begins
3. the control layer is more than documentation and manual discipline

---

## Current Constraints

- do not execute migration work while system enforcement is incomplete
- do not expand workflow types beyond code_migration
- do not bypass Guardian or ECS checks
- do not introduce automation before control is fully enforced

---

## Not Doing Yet

- app_build execution
- automation_build execution
- ui_conversion execution
- multi-agent orchestration
- broad cleanup of product repo structure
- non-essential feature work in resume-saas

---

## Transition Basis

{reason}

---

## Approved Basis

This objective was written by ai_factory_transition.py through an explicit operator transition.
"""

TEMPLATE_MIGRATION_EXECUTION = """\
# Current Objective

## Current Objective

Execute approved migration work through the controlled execution path while maintaining Guardian enforcement, policy integrity, and state correctness.

---

## Why This Is The Current Objective

The system is in migration-execution mode. Only approved migration work may proceed, and all execution must remain gated by Guardian, ECS, and policy controls.

---

## Immediate Next Steps

1. Execute approved migration work through the controlled queue path
2. Preserve Guardian enforcement and policy integrity during execution
3. Return to system-building mode if control gaps, drift, or blocking issues are discovered

---

## Success Condition

This objective is complete when:

1. approved migration work for the selected queue-state has been executed or intentionally halted
2. Guardian and policy controls remain intact during execution
3. any newly discovered control gaps are brought back into system-building mode explicitly

---

## Current Constraints

- do not bypass Guardian, ECS, or policy enforcement
- do not execute unapproved or out-of-scope migration work
- do not expand workflow types beyond code_migration
- do not silently change objective direction during execution

---

## Not Doing Yet

- app_build execution
- automation_build execution
- ui_conversion execution
- multi-agent orchestration
- autonomous objective switching
- uncontrolled automation

---

## Transition Basis

{reason}

---

## Approved Basis

This objective was written by ai_factory_transition.py through an explicit operator transition.
"""

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
# Step 1 — Read and verify state surface
# ---------------------------------------------------------------------------

def check_state_files():
    missing = [
        name for name, path in STATE_FILES.items()
        if not os.path.isfile(path)
    ]
    if missing:
        _die("TRANSITION ERROR", [
            "state surface unreadable — missing files:",
            *[f"  {name}" for name in missing],
        ])


# ---------------------------------------------------------------------------
# Step 2 — Determine current mode from current-objective.md
# ---------------------------------------------------------------------------

def detect_current_mode():
    try:
        with open(OBJECTIVE_PATH, encoding="utf-8") as f:
            content = f.read()
    except OSError as exc:
        _die("TRANSITION ERROR", [f"cannot read current-objective.md: {exc}"])

    # Extract the first Immediate Next Steps list item
    first_item = _extract_first_next_step(content)

    if first_item is None:
        # Cannot determine mode — treat as system-building (safe default)
        return "system-building"

    first_item_lower = first_item.lower()
    first_item_words = set(first_item_lower.split())
    for keyword in SYSTEM_BUILDING_KEYWORDS:
        keyword_words = keyword.split()
        if len(keyword_words) == 1:
            matched = keyword_words[0] in first_item_words
        else:
            matched = keyword in first_item_lower
        if matched:
            return "system-building"

    return "migration-execution"


def _extract_first_next_step(content):
    """Return the text of the first list item under ## Immediate Next Steps, or None."""
    in_section = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("##") and not stripped.startswith("###"):
            header = stripped.lstrip("#").strip().lower()
            if header == "immediate next steps":
                in_section = True
                continue
            elif in_section:
                break
        if not in_section:
            continue
        item = _parse_list_item(stripped)
        if item is not None:
            return item
    return None


def _parse_list_item(line):
    """Return list item text if line is a list item, else None."""
    if line.startswith("- ") or line.startswith("* "):
        return line[2:].strip()
    if line.startswith("-") or line.startswith("*"):
        return line[1:].strip()
    # Ordered: digits followed by ". "
    i = 0
    while i < len(line) and line[i].isdigit():
        i += 1
    if i > 0 and i < len(line) and line[i] == "." and i + 1 < len(line) and line[i + 1] == " ":
        return line[i + 2:].strip()
    return None

# ---------------------------------------------------------------------------
# Step 3 — Common transition requirements
# ---------------------------------------------------------------------------

def validate_reason(reason):
    if not reason or not reason.strip():
        _die("TRANSITION BLOCK", ["--reason is required and must be non-empty"])


def run_policy_integrity_check():
    """
    Run only the policy integrity check as the pre-transition gate.
    Does NOT run full Guardian — objective_alignment must not block the transition
    before the objective file is updated.
    """
    try:
        proc = subprocess.run(
            [sys.executable, POLICY_INTEGRITY_CHECK],
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        _die("TRANSITION BLOCK", [
            "pre-transition policy check: could not launch check_policy_integrity.py",
            f"detail: {exc}",
        ])

    if proc.returncode != 0:
        snippet = proc.stderr.strip()[:400]
        _die("TRANSITION BLOCK", [
            f"pre-transition policy check: script exited {proc.returncode}",
            *([f"detail: {snippet}"] if snippet else []),
        ])

    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        _die("TRANSITION BLOCK", ["pre-transition policy check: invalid JSON returned"])

    if result.get("status") != "PASS":
        failures = result.get("failures", [])
        _die("TRANSITION BLOCK", [
            "pre-transition policy check: FAIL",
            f"failures: {', '.join(str(f) for f in failures)}",
        ])


def run_guardian_check(label):
    """Run Guardian and return parsed result. Dies on any failure."""
    try:
        proc = subprocess.run(
            [sys.executable, GUARDIAN_ENGINE],
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        _die("TRANSITION BLOCK", [
            f"{label}: guardian engine could not be launched",
            f"detail: {exc}",
        ])

    if proc.returncode != 0:
        snippet = proc.stderr.strip()[:400]
        _die("TRANSITION BLOCK", [
            f"{label}: guardian engine exited {proc.returncode}",
            *([f"detail: {snippet}"] if snippet else []),
        ])

    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        _die("TRANSITION BLOCK", [f"{label}: guardian returned invalid JSON"])

    if "status" not in result:
        _die("TRANSITION BLOCK", [f"{label}: guardian output missing 'status' field"])

    if result["status"] != "PASS":
        failures = result.get("failures", [])
        _die("TRANSITION BLOCK", [
            f"{label}: guardian status is {result['status']}",
            f"failed checks: {', '.join(str(f) for f in failures)}",
        ])

    return result

# ---------------------------------------------------------------------------
# Step 4 — Type-specific preconditions
# ---------------------------------------------------------------------------

def validate_queue_state(queue_state_path):
    if not queue_state_path:
        _die("TRANSITION BLOCK", [
            "--queue-state is required for --to migration-execution",
        ])

    if not os.path.isfile(queue_state_path):
        _die("TRANSITION BLOCK", [
            f"queue-state file not found: {queue_state_path}",
        ])

    try:
        with open(queue_state_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        _die("TRANSITION BLOCK", [
            f"queue-state file is not valid JSON: {queue_state_path}",
            f"detail: {exc}",
        ])
    except OSError as exc:
        _die("TRANSITION BLOCK", [
            f"queue-state file is not readable: {queue_state_path}",
            f"detail: {exc}",
        ])

    jobs = data.get("jobs")
    if not isinstance(jobs, list):
        _die("TRANSITION BLOCK", [
            "queue-state file has no top-level 'jobs' array",
            f"file: {queue_state_path}",
        ])

    if len(jobs) == 0:
        _die("TRANSITION BLOCK", [
            "queue-state 'jobs' array is empty — no executable work",
            f"file: {queue_state_path}",
        ])

    approved = [j for j in jobs if isinstance(j, dict) and j.get("status") == "approved"]
    if not approved:
        _die("TRANSITION BLOCK", [
            "queue-state has no jobs with status == 'approved'",
            f"file: {queue_state_path}",
            f"total jobs: {len(jobs)}",
        ])

# ---------------------------------------------------------------------------
# Step 5 — Build target objective content
# ---------------------------------------------------------------------------

def build_objective_content(target_mode, reason):
    if target_mode == "system-building":
        return TEMPLATE_SYSTEM_BUILDING.format(reason=reason)
    return TEMPLATE_MIGRATION_EXECUTION.format(reason=reason)

# ---------------------------------------------------------------------------
# Step 6 — Atomic write
# ---------------------------------------------------------------------------

REQUIRED_HEADERS = [
    "## Current Objective",
    "## Immediate Next Steps",
    "## Current Constraints",
]


def atomic_write_objective(content):
    # Write to temp file
    try:
        with open(OBJECTIVE_TMP, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError as exc:
        _die("TRANSITION ERROR", [
            "failed to write temporary objective file",
            f"path: {OBJECTIVE_TMP}",
            f"detail: {exc}",
        ])

    # Validate temp file
    try:
        with open(OBJECTIVE_TMP, encoding="utf-8") as f:
            written = f.read()
    except OSError as exc:
        _cleanup_tmp()
        _die("TRANSITION ERROR", [
            "failed to read back temporary objective file",
            f"detail: {exc}",
        ])

    if not written.strip():
        _cleanup_tmp()
        _die("TRANSITION ERROR", ["temporary objective file is empty after write"])

    for header in REQUIRED_HEADERS:
        if header not in written:
            _cleanup_tmp()
            _die("TRANSITION ERROR", [
                f"temporary objective file missing required header: {header}",
                "transition aborted — current-objective.md was not modified",
            ])

    # Atomic replace
    try:
        os.replace(OBJECTIVE_TMP, OBJECTIVE_PATH)
    except OSError as exc:
        _cleanup_tmp()
        _die("TRANSITION ERROR", [
            "atomic replace of current-objective.md failed",
            f"detail: {exc}",
            "current-objective.md was NOT modified",
        ])


def _cleanup_tmp():
    try:
        if os.path.exists(OBJECTIVE_TMP):
            os.remove(OBJECTIVE_TMP)
    except OSError:
        pass

# ---------------------------------------------------------------------------
# Step 7A — Post-write Guardian validation
# ---------------------------------------------------------------------------

def _rollback_objective(previous_content):
    """
    Atomically restore current-objective.md to its previous content.
    Uses the same temp-file + os.replace pattern as atomic_write_objective().
    Does NOT call _die() — caller handles exit after rollback.
    """
    try:
        with open(OBJECTIVE_TMP, "w", encoding="utf-8") as f:
            f.write(previous_content)
        os.replace(OBJECTIVE_TMP, OBJECTIVE_PATH)
    except OSError as exc:
        _print_block("TRANSITION ROLLBACK FAILED", [
            "could not restore previous objective file",
            f"detail: {exc}",
            "MANUAL INTERVENTION REQUIRED: restore current-objective.md from transition record or git",
        ])
        sys.exit(1)


def post_write_guardian():
    """
    Run Guardian after the objective write.
    Returns (passed: bool, result_dict) — does NOT call _die().
    Caller is responsible for rollback on failure.
    """
    try:
        proc = subprocess.run(
            [sys.executable, GUARDIAN_ENGINE],
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return False, {"status": "FAIL", "failures": [f"engine could not be launched: {exc}"]}

    if proc.returncode != 0:
        snippet = proc.stderr.strip()[:400]
        return False, {"status": "FAIL", "failures": [f"engine exited {proc.returncode}: {snippet}"]}

    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return False, {"status": "FAIL", "failures": ["invalid JSON returned by Guardian"]}

    if result.get("status") != "PASS":
        return False, result

    return True, result

# ---------------------------------------------------------------------------
# Step 7B — Post-write ECS validation
# ---------------------------------------------------------------------------

def post_write_ecs():
    """
    Run ECS resolver after the objective write.
    Returns (decision_str, error_str) — decision_str is None on failure.
    Caller is responsible for rollback on failure.
    """
    try:
        proc = subprocess.run(
            [sys.executable, ECS_RESOLVER],
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return None, f"resolver could not be launched: {exc}"

    if proc.returncode != 0:
        snippet = proc.stderr.strip()[:400]
        return None, f"resolver exited {proc.returncode}: {snippet}"

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None, "invalid JSON returned by ECS resolver"

    decision = data.get("decision")
    if not decision or not isinstance(decision, str) or not decision.strip():
        return None, "resolver returned empty or missing decision"

    return decision, None

# ---------------------------------------------------------------------------
# Step 7C — Write transition record
# ---------------------------------------------------------------------------

def write_transition_record(from_mode, to_mode, reason, guardian_status, queue_state_path):
    os.makedirs(RECORDS_DIR, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    record_path = os.path.join(RECORDS_DIR, f"{timestamp}_transition.json")

    record = {
        "timestamp":        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "from_mode":        from_mode,
        "to_mode":          to_mode,
        "reason":           reason,
        "guardian_status":  guardian_status,
        "queue_state_path": queue_state_path,
    }

    try:
        with open(record_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
    except OSError as exc:
        _die("TRANSITION ERROR", [
            "failed to write transition record",
            f"path: {record_path}",
            f"detail: {exc}",
            "current-objective.md has been updated but transition is NOT confirmed",
        ])

    # Verify readable
    if not os.path.isfile(record_path):
        _die("TRANSITION ERROR", [
            "transition record file does not exist after write",
            f"path: {record_path}",
            "current-objective.md has been updated but transition is NOT confirmed",
        ])

    return record_path

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="ai-factory objective transition command.",
    )
    parser.add_argument(
        "--to",
        choices=["system-building", "migration-execution"],
        required=True,
        help="Target objective mode",
    )
    parser.add_argument(
        "--queue-state",
        metavar="PATH",
        default=None,
        help="Path to queue-state JSON file (required for --to migration-execution)",
    )
    parser.add_argument(
        "--reason",
        required=True,
        help="Operator-provided reason for this transition (required)",
    )
    return parser.parse_args()

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()
    target_mode    = args.to
    queue_state    = args.queue_state
    reason         = args.reason

    # 1. Verify state surface
    check_state_files()

    # 2. Determine current mode
    current_mode = detect_current_mode()

    if current_mode == target_mode:
        _die("TRANSITION BLOCK", [
            f"current mode is already '{current_mode}'",
            "no transition needed",
        ])

    # 3. Validate common requirements
    validate_reason(reason)

    _print("TRANSITION", "pre-transition policy integrity check ...")
    run_policy_integrity_check()
    _print("TRANSITION", "pre-transition policy integrity: PASS")

    # 4. Type-specific preconditions
    if target_mode == "migration-execution":
        validate_queue_state(queue_state)
        _print("TRANSITION", f"queue-state validated: {queue_state}")

    # 5. Build target content
    content = build_objective_content(target_mode, reason)

    # 5B. Read previous objective content for rollback
    try:
        with open(OBJECTIVE_PATH, encoding="utf-8") as f:
            previous_objective_content = f.read()
    except OSError as exc:
        _die("TRANSITION ERROR", [f"cannot read current-objective.md for rollback snapshot: {exc}"])

    # 6. Atomic write
    _print("TRANSITION", "writing new objective ...")
    atomic_write_objective(content)
    _print("TRANSITION", f"current-objective.md updated atomically")

    # 7A. Post-write Guardian — rollback on failure
    _print("TRANSITION", "post-write Guardian check ...")
    guardian_passed, post_guardian = post_write_guardian()

    if not guardian_passed:
        failures = post_guardian.get("failures", [])
        _print_block("TRANSITION ROLLBACK", [
            "post-write Guardian check failed",
            f"failed checks: {', '.join(str(f) for f in failures)}",
            "restoring previous objective state",
        ])
        _rollback_objective(previous_objective_content)
        _print_block("TRANSITION ROLLBACK", ["state restored successfully"])
        sys.exit(1)

    _print("TRANSITION", "post-write Guardian: PASS")

    # 7B. Post-write ECS — rollback on failure
    _print("TRANSITION", "post-write ECS check ...")
    decision, ecs_error = post_write_ecs()

    if decision is None:
        _print_block("TRANSITION ROLLBACK", [
            "post-write ECS check failed",
            f"detail: {ecs_error}",
            "restoring previous objective state",
        ])
        _rollback_objective(previous_objective_content)
        _print_block("TRANSITION ROLLBACK", ["state restored successfully"])
        sys.exit(1)

    _print("TRANSITION", f"post-write ECS: resolved action — {decision}")

    # 7C. Transition record
    record_path = write_transition_record(
        from_mode=current_mode,
        to_mode=target_mode,
        reason=reason,
        guardian_status=post_guardian.get("status"),
        queue_state_path=queue_state,
    )

    # 8. Success output
    print()
    _print("TRANSITION OK", f"from_mode:         {current_mode}")
    _print("TRANSITION OK", f"to_mode:           {target_mode}")
    _print("TRANSITION OK", f"objective:         {OBJECTIVE_PATH}")
    _print("TRANSITION OK", f"transition record: {record_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
