#!/usr/bin/env python3
"""
ai-factory operator entrypoint.

Coordinates state reading, ECS resolution, Guardian gating, and (optionally)
execution. Does not make decisions — delegates authority to existing tools.

Usage:
    python ai_factory_run.py
    python ai_factory_run.py --mode inspect
    python ai_factory_run.py --mode execute-allowed-step --queue-state <path>

Modes:
    inspect               Read state, resolve action, run Guardian, report outcome.
                          Never invokes execution. Safe to run at any time. (default)
    execute-allowed-step  Same as inspect, then invokes run-migration-queue if and
                          only if Guardian passes and the resolved action is executable.
                          Requires --queue-state.
"""

import argparse
import json
import os
import subprocess
import sys

# ---------------------------------------------------------------------------
# Repo layout
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.dirname(__file__))

STATE_FILES = {
    "current-system-state.md": os.path.join(REPO_ROOT, "system-state", "current-system-state.md"),
    "current-objective.md":    os.path.join(REPO_ROOT, "system-state", "current-objective.md"),
    "authoritative-files.md":  os.path.join(REPO_ROOT, "system-state", "authoritative-files.md"),
}

ECS_RESOLVER    = os.path.join(REPO_ROOT, "tools", "ecs", "resolve_next_action.py")
GUARDIAN_ENGINE = os.path.join(REPO_ROOT, "tools", "guardian", "run_guardian.py")
QUEUE_RUNNER    = os.path.join(REPO_ROOT, "run-migration-queue")

# ---------------------------------------------------------------------------
# Scope — what actions are considered executable in the current phase
# ---------------------------------------------------------------------------

# Keywords that identify a resolved action as migration execution work.
# The action must contain at least one of these to be considered executable.
EXECUTABLE_SCOPE_KEYWORDS = ["migration", "code_migration"]

# Keywords that identify a resolved action as system-building work.
# If the action contains any of these, execution is blocked regardless of
# whether it also contains an executable keyword.
SYSTEM_BUILDING_KEYWORDS = ["guardian", "enforcement", "ecs", "control", "system"]

# ---------------------------------------------------------------------------
# Ambiguity signals — resolver decision must not contain these
# ---------------------------------------------------------------------------

AMBIGUOUS_SIGNALS = ["ambiguous", "unclear", "unknown", "no clear", "none"]

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
# Step 1 — Verify state surface
# ---------------------------------------------------------------------------

def check_state_files():
    missing = [
        name for name, path in STATE_FILES.items()
        if not os.path.isfile(path)
    ]
    if missing:
        _die("ENTRYPOINT ERROR", [
            "state surface unreadable",
            *[f"missing: {name}" for name in missing],
        ])


# ---------------------------------------------------------------------------
# Step 2 — Run ECS resolver
# ---------------------------------------------------------------------------

def run_ecs_resolver():
    try:
        proc = subprocess.run(
            [sys.executable, ECS_RESOLVER],
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        _die("ECS BLOCK", [
            "resolver could not be launched",
            f"detail: {exc}",
        ])

    if proc.returncode != 0:
        stderr_snippet = proc.stderr.strip()[:400]
        _die("ECS BLOCK", [
            f"resolver exited {proc.returncode}",
            *([f"detail: {stderr_snippet}"] if stderr_snippet else []),
        ])

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        _die("ECS BLOCK", ["resolver returned invalid JSON"])

    return data


# ---------------------------------------------------------------------------
# Step 3 — Validate resolver output
# ---------------------------------------------------------------------------

def validate_resolver_output(data):
    decision = data.get("decision")

    if decision is None:
        _die("ECS BLOCK", ["resolver output missing 'decision' field"])

    if not isinstance(decision, str) or not decision.strip():
        _die("ECS BLOCK", ["resolver returned empty decision"])

    decision_lower = decision.lower()
    for signal in AMBIGUOUS_SIGNALS:
        if signal in decision_lower:
            _die("ECS BLOCK", [
                "resolver decision contains ambiguity signal",
                f"matched: '{signal}'",
                f"decision: {decision}",
            ])

    return decision


# ---------------------------------------------------------------------------
# Step 4 — Run Guardian
# ---------------------------------------------------------------------------

def run_guardian():
    try:
        proc = subprocess.run(
            [sys.executable, GUARDIAN_ENGINE],
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        _die("GUARDIAN BLOCK", [
            "guardian engine could not be launched",
            f"detail: {exc}",
        ])

    if proc.returncode != 0:
        stderr_snippet = proc.stderr.strip()[:400]
        _die("GUARDIAN BLOCK", [
            f"guardian engine exited {proc.returncode}",
            *([f"detail: {stderr_snippet}"] if stderr_snippet else []),
        ])

    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        _die("GUARDIAN BLOCK", ["guardian returned invalid JSON"])

    return result


# ---------------------------------------------------------------------------
# Step 5 — Evaluate Guardian result
# ---------------------------------------------------------------------------

def evaluate_guardian(result):
    status = result.get("status")

    if status == "PASS":
        return

    failures = result.get("failures", [])
    checks   = result.get("checks", [])

    lines = [
        f"guardian status: FAIL",
        f"failed checks: {', '.join(str(f) for f in failures)}",
        "---",
    ]

    for check in checks:
        if isinstance(check, dict) and check.get("status") == "FAIL":
            lines.append(f"check: {check.get('name', 'unknown')}")
            detail = check.get("result") or check
            if isinstance(detail, dict):
                sub_failures = detail.get("failures", [])
                reason       = detail.get("reason", "")
                if sub_failures:
                    lines.append(f"  failures: {', '.join(str(f) for f in sub_failures)}")
                if reason:
                    lines.append(f"  reason: {reason}")
            lines.append("---")

    _die("GUARDIAN BLOCK", lines)


# ---------------------------------------------------------------------------
# Scope evaluation
# ---------------------------------------------------------------------------

def evaluate_scope(decision):
    """
    Returns True if the resolved action is executable in the current scope.
    Returns False if the action is system-building or otherwise out of scope.
    """
    decision_lower = decision.lower()

    # System-building takes precedence — block even if migration keyword also present.
    for keyword in SYSTEM_BUILDING_KEYWORDS:
        if keyword in decision_lower:
            return False

    for keyword in EXECUTABLE_SCOPE_KEYWORDS:
        if keyword in decision_lower:
            return True

    return False


# ---------------------------------------------------------------------------
# Inspect mode output
# ---------------------------------------------------------------------------

def report_inspect(decision, executable):
    print()
    _print("ENTRYPOINT", "Guardian passed")
    _print("ENTRYPOINT", f"resolved action: {decision}")

    if executable:
        _print("ENTRYPOINT", "status: EXECUTABLE")
        _print("ENTRYPOINT", "run with --mode execute-allowed-step --queue-state <path> to proceed")
    else:
        _print("ENTRYPOINT", "status: NOT EXECUTABLE — objective is system-building or action is out of scope")
        _print("ENTRYPOINT", "no migration execution allowed in current phase")


# ---------------------------------------------------------------------------
# Execute mode
# ---------------------------------------------------------------------------

def run_execute(queue_state_path, decision):
    if not os.path.isfile(queue_state_path):
        _die("ENTRYPOINT ERROR", [
            f"queue state file not found: {queue_state_path}",
        ])

    executable = evaluate_scope(decision)
    if not executable:
        _die("ENTRYPOINT ERROR", [
            "execution requested but resolved action is not in executable scope",
            f"resolved action: {decision}",
            "no migration execution allowed in current phase",
        ])

    _print("ENTRYPOINT", f"invoking run-migration-queue with: {queue_state_path}")

    try:
        proc = subprocess.run(
            [QUEUE_RUNNER, queue_state_path],
        )
    except OSError as exc:
        _die("ENTRYPOINT ERROR", [
            "run-migration-queue could not be launched",
            f"detail: {exc}",
        ])

    if proc.returncode != 0:
        _die("ENTRYPOINT ERROR", [
            f"run-migration-queue exited {proc.returncode}",
            f"queue state: {queue_state_path}",
        ])

    print()
    _print("ENTRYPOINT", "execution complete")
    _print("ENTRYPOINT", f"queue state: {queue_state_path}")


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="ai-factory operator entrypoint — controlled front door for system execution.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Modes:\n"
            "  inspect               Read state, resolve next action, run Guardian, report outcome.\n"
            "                        Never invokes execution. Safe to run at any time. (default)\n"
            "  execute-allowed-step  Same as inspect, then invokes run-migration-queue if Guardian\n"
            "                        passes and the resolved action is executable.\n"
            "                        Requires --queue-state."
        ),
    )
    parser.add_argument(
        "--mode",
        choices=["inspect", "execute-allowed-step"],
        default="inspect",
        help="Entrypoint mode (default: inspect)",
    )
    parser.add_argument(
        "--queue-state",
        metavar="PATH",
        default=None,
        help="Path to queue-state JSON file (required for execute-allowed-step mode)",
    )
    args = parser.parse_args()

    if args.mode == "execute-allowed-step" and not args.queue_state:
        parser.error("--queue-state is required when --mode is execute-allowed-step")

    if args.queue_state and args.mode != "execute-allowed-step":
        parser.error("--queue-state is only valid with --mode execute-allowed-step")

    return args


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    # 1. Verify state surface
    check_state_files()

    # 2. Run ECS resolver
    resolver_data = run_ecs_resolver()

    # 3. Validate resolver output
    decision = validate_resolver_output(resolver_data)

    # 4. Run Guardian
    guardian_result = run_guardian()

    # 5. Evaluate Guardian — exits non-zero on FAIL
    evaluate_guardian(guardian_result)

    # 6. Inspect mode
    if args.mode == "inspect":
        executable = evaluate_scope(decision)
        report_inspect(decision, executable)
        sys.exit(0)

    # 7. Execute mode
    run_execute(args.queue_state, decision)
    sys.exit(0)


if __name__ == "__main__":
    main()
