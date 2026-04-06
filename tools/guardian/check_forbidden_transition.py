#!/usr/bin/env python3
"""
System Guardian: Forbidden Transition Check

Detects when Immediate Next Steps contains items explicitly forbidden by
Current Constraints or Not Doing Yet.

Matching rule: a step is forbidden if any blocker text is a case-insensitive
substring of the step text. Exact substring only — no semantic reasoning.

Usage:
    python check_forbidden_transition.py
    python check_forbidden_transition.py --objective <path> --state <path> --authority <path>
"""

import argparse
import json
import os
import sys

# ---------------------------------------------------------------------------
# Default paths
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

DEFAULT_OBJECTIVE  = os.path.join(REPO_ROOT, "system-state", "current-objective.md")
DEFAULT_STATE      = os.path.join(REPO_ROOT, "system-state", "current-system-state.md")
DEFAULT_AUTHORITY  = os.path.join(REPO_ROOT, "system-state", "authoritative-files.md")

# ---------------------------------------------------------------------------
# Section definitions (same parser contract as all ECS / Guardian tools)
# ---------------------------------------------------------------------------

RECOGNIZED_SECTIONS = {
    "current phase":        "Current Phase",
    "current objective":    "Current Objective",
    "immediate next steps": "Immediate Next Steps",
    "current constraints":  "Current Constraints",
    "not doing yet":        "Not Doing Yet",
    "exit condition":       "Exit Condition",
}

# ---------------------------------------------------------------------------
# Parser (same rules as ECS tools and other Guardian checks)
# ---------------------------------------------------------------------------

def _normalize_header(line):
    stripped = line.lstrip()
    if not stripped.startswith("#"):
        return None
    level = 0
    for ch in stripped:
        if ch == "#":
            level += 1
        else:
            break
    if level == 1 or level > 3:
        return None
    if stripped[level:level + 1] != " ":
        return None
    text = stripped[level:].strip()
    return text.lower() if text else None


def parse_sections(filepath):
    """Parse a markdown file into { canonical_label: [lines] }."""
    try:
        with open(filepath, encoding="utf-8") as f:
            raw_lines = f.readlines()
    except FileNotFoundError:
        _fail(f"MISSING_FILE: {filepath}")
    except OSError as e:
        _fail(f"MISSING_FILE: {filepath} ({e})")

    filename = os.path.basename(filepath)
    sections = {}
    current_label = None

    for line in raw_lines:
        normalized = _normalize_header(line)
        if normalized is not None:
            canonical = RECOGNIZED_SECTIONS.get(normalized)
            if canonical is not None:
                if canonical in sections:
                    _fail(f"DUPLICATE_SECTION: {canonical} in {filename}")
                sections[canonical] = []
                current_label = canonical
            else:
                current_label = None
        else:
            if current_label is not None:
                sections[current_label].append(line)

    return sections


def _strip_body(lines):
    result = []
    for line in lines:
        text = line.strip()
        if not text or text == "---":
            continue
        result.append(text)
    return result


def _extract_list_items(lines):
    items = []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        if len(text) >= 3 and text[0].isdigit() and text[1] == "." and text[2] == " ":
            item = text[3:].strip()
        elif text.startswith("- ") or text.startswith("* "):
            item = text[2:].strip()
        else:
            continue
        item = item.replace("**", "")
        items.append(item)
    return items

# ---------------------------------------------------------------------------
# Failure helper
# ---------------------------------------------------------------------------

def _fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Forbidden transition check logic
# ---------------------------------------------------------------------------

def run_check(objective_path, state_path, authority_path):
    """
    Parse Immediate Next Steps, Current Constraints, and Not Doing Yet.
    For each step, check whether any blocker is a substring of the step.
    Returns the full output dict.
    """
    objective_filename = os.path.basename(objective_path)

    # Validate all three input files parse cleanly (structural check).
    parse_sections(state_path)
    parse_sections(authority_path)
    objective_sections = parse_sections(objective_path)

    # --- Extract required sections ---

    if "Immediate Next Steps" not in objective_sections:
        _fail(f"MISSING_SECTION: Immediate Next Steps in {objective_filename}")
    next_steps_body = _strip_body(objective_sections["Immediate Next Steps"])
    if not next_steps_body:
        _fail(f"EMPTY_SECTION: Immediate Next Steps in {objective_filename}")
    next_steps = _extract_list_items(next_steps_body)
    if not next_steps:
        _fail("EMPTY_SECTION: Immediate Next Steps contained no list items")

    if "Current Constraints" not in objective_sections:
        _fail(f"MISSING_SECTION: Current Constraints in {objective_filename}")
    constraints_body = _strip_body(objective_sections["Current Constraints"])
    if not constraints_body:
        _fail(f"EMPTY_SECTION: Current Constraints in {objective_filename}")
    constraint_items = _extract_list_items(constraints_body)

    # Not Doing Yet is optional.
    not_doing_items = []
    if "Not Doing Yet" in objective_sections:
        not_doing_body = _strip_body(objective_sections["Not Doing Yet"])
        not_doing_items = _extract_list_items(not_doing_body)

    # --- Evaluate each step ---

    checks = []
    failures = []

    for idx, step in enumerate(next_steps, start=1):
        check_name = f"step_{idx}_forbidden_check"
        step_lower = step.lower()

        # Check against Current Constraints first.
        blocking_constraint = None
        for item in constraint_items:
            if item.lower() in step_lower:
                blocking_constraint = item
                break

        # Then check against Not Doing Yet.
        blocking_not_doing = None
        if blocking_constraint is None:
            for item in not_doing_items:
                if item.lower() in step_lower:
                    blocking_not_doing = item
                    break

        if blocking_constraint is not None:
            status = "FAIL"
            reason = f'Blocked by Current Constraints: "{blocking_constraint}"'
            failures.append(check_name)
        elif blocking_not_doing is not None:
            status = "FAIL"
            reason = f'Blocked by Not Doing Yet: "{blocking_not_doing}"'
            failures.append(check_name)
        else:
            status = "PASS"
            reason = "No constraint or not-doing-yet item is a substring of this step."

        checks.append({
            "name":    check_name,
            "status":  status,
            "subject": step,
            "reason":  reason,
        })

    return {
        "status":     "FAIL" if failures else "PASS",
        "check_name": "forbidden_transition_check",
        "checks":     checks,
        "failures":   failures,
    }

# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="System Guardian: detect forbidden transitions in Immediate Next Steps."
    )
    parser.add_argument("--objective",  default=DEFAULT_OBJECTIVE,
                        help="Path to current-objective.md")
    parser.add_argument("--state",      default=DEFAULT_STATE,
                        help="Path to current-system-state.md")
    parser.add_argument("--authority",  default=DEFAULT_AUTHORITY,
                        help="Path to authoritative-files.md")
    args = parser.parse_args()

    result = run_check(args.objective, args.state, args.authority)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
