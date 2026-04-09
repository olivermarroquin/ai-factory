#!/usr/bin/env python3
"""
System Guardian Engine

Runs all four Guardian checks in sequence via subprocess and aggregates
their results into a single combined JSON report.

Does not recompute check logic. Delegates entirely to individual scripts.

Usage:
    python run_guardian.py
"""

import json
import os
import subprocess
import sys

# ---------------------------------------------------------------------------
# Repo root and check script definitions (in execution order)
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# (repo-relative path, script name for error messages)
CHECKS = [
    ("tools/guardian/check_stale_state.py",          "check_stale_state.py"),
    ("tools/guardian/check_ecs_consistency.py",      "check_ecs_consistency.py"),
    ("tools/guardian/check_forbidden_transition.py", "check_forbidden_transition.py"),
    ("tools/guardian/check_missing_artifact.py",     "check_missing_artifact.py"),
    ("tools/guardian/check_policy_integrity.py",     "check_policy_integrity.py"),
    ("tools/guardian/check_objective_alignment.py",  "check_objective_alignment.py"),
]

# ---------------------------------------------------------------------------
# Failure helper
# ---------------------------------------------------------------------------

def _fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

def run_engine():
    """
    Run each check script via subprocess. Aggregate results.
    Exits non-zero (no JSON) if any subprocess fails or returns invalid output.
    """
    check_entries = []
    failures = []

    for rel_path, script_name in CHECKS:
        abs_path = os.path.join(REPO_ROOT, rel_path)

        try:
            proc = subprocess.run(
                [sys.executable, abs_path],
                capture_output=True,
                text=True,
            )
        except OSError as e:
            _fail(f"CHECK_FAILED: {script_name} could not be launched: {e}")

        if proc.returncode != 0:
            stderr_snippet = proc.stderr.strip()[:300]
            _fail(f"CHECK_FAILED: {script_name} exited {proc.returncode}: {stderr_snippet}")

        try:
            result = json.loads(proc.stdout)
        except json.JSONDecodeError:
            _fail(f"CHECK_INVALID_JSON: {script_name}")

        for required_field in ("status", "check_name"):
            if required_field not in result:
                _fail(f"CHECK_MISSING_FIELD: {required_field} in {script_name}")

        check_name   = result["check_name"]
        check_status = result["status"]

        check_entries.append({
            "name":   check_name,
            "status": check_status,
            "source": rel_path,
            "result": result,
        })

        if check_status == "FAIL":
            failures.append(check_name)

    overall_status = "FAIL" if failures else "PASS"

    return {
        "status":   overall_status,
        "engine":   "system_guardian_mvp",
        "checks":   check_entries,
        "failures": failures,
    }


def main():
    result = run_engine()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
