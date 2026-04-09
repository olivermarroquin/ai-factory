#!/usr/bin/env python3
"""
System Guardian: Policy File Integrity Check

Verifies that config/migration-execution-policy.json:
- exists
- is valid JSON
- contains all required keys

Does not enforce values — only presence.

Usage:
    python check_policy_integrity.py
"""

import json
import os
import sys

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

POLICY_FILE = os.path.join(REPO_ROOT, "config", "migration-execution-policy.json")

REQUIRED_KEYS = [
    ("batch_execution", "allowed_workflow_types"),
    ("batch_execution", "allowed_workflow_spec_versions"),
    ("batch_execution", "allowed_job_types"),
    ("batch_execution", "allowed_classes"),
    ("batch_execution", "allowed_reason_codes"),
]

# ---------------------------------------------------------------------------
# Check
# ---------------------------------------------------------------------------

def run_check(policy_path):
    failures = []

    # 1. File must exist
    if not os.path.exists(policy_path):
        return {
            "status":     "FAIL",
            "check_name": "policy_file_integrity",
            "failures":   ["policy_file_missing"],
            "detail":     f"not found: {policy_path}",
        }

    # 2. Must be valid JSON
    try:
        with open(policy_path, encoding="utf-8") as f:
            policy = json.load(f)
    except json.JSONDecodeError as e:
        return {
            "status":     "FAIL",
            "check_name": "policy_file_integrity",
            "failures":   ["policy_file_invalid_json"],
            "detail":     str(e),
        }
    except OSError as e:
        return {
            "status":     "FAIL",
            "check_name": "policy_file_integrity",
            "failures":   ["policy_file_unreadable"],
            "detail":     str(e),
        }

    # 3. Required keys must be present
    missing_keys = []
    for parent_key, child_key in REQUIRED_KEYS:
        parent = policy.get(parent_key)
        if not isinstance(parent, dict) or child_key not in parent:
            missing_keys.append(f"{parent_key}.{child_key}")

    if missing_keys:
        failures.extend(missing_keys)
        return {
            "status":       "FAIL",
            "check_name":   "policy_file_integrity",
            "failures":     failures,
            "missing_keys": missing_keys,
        }

    return {
        "status":     "PASS",
        "check_name": "policy_file_integrity",
        "failures":   [],
    }


def main():
    result = run_check(POLICY_FILE)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
