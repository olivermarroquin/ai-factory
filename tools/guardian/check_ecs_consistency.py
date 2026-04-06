#!/usr/bin/env python3
"""
System Guardian: ECS Consistency Check

Detects contradictions between ECS tool surfaces and authoritative state.
Compares exact string values only — no semantic matching, no fuzzy comparison.

Three comparisons (all must pass):
  1. resolve_next_action.decision == read_state.immediate_next_steps[0]
  2. read_state.immediate_next_steps[0] == first parsed step from current-objective.md
  3. read_state.current_objective == full stripped Current Objective joined with " | "

Usage:
    python check_ecs_consistency.py
    python check_ecs_consistency.py --objective <path>
"""

import argparse
import json
import os
import subprocess
import sys

# ---------------------------------------------------------------------------
# Default paths
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

DEFAULT_OBJECTIVE  = os.path.join(REPO_ROOT, "system-state", "current-objective.md")
RESOLVER_TOOL      = os.path.join(REPO_ROOT, "tools", "ecs", "resolve_next_action.py")
READ_STATE_TOOL    = os.path.join(REPO_ROOT, "tools", "ecs", "read_state.py")

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

REQUIRED_SECTIONS = ["Current Objective", "Immediate Next Steps"]

# ---------------------------------------------------------------------------
# Parser
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
# ECS tool runner
# ---------------------------------------------------------------------------

def _run_ecs_tool(tool_path):
    """
    Run an ECS tool as a subprocess. Returns parsed JSON dict.
    Calls _fail() on non-zero exit, malformed JSON, or missing required fields.
    """
    tool_name = os.path.basename(tool_path)
    try:
        result = subprocess.run(
            [sys.executable, tool_path],
            capture_output=True,
            text=True,
        )
    except OSError as e:
        _fail(f"ECS_TOOL_FAILED: {tool_path} could not be launched: {e}")

    if result.returncode != 0:
        stderr_snippet = result.stderr.strip()[:200]
        _fail(f"ECS_TOOL_FAILED: {tool_name} exited {result.returncode}: {stderr_snippet}")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        _fail(f"ECS_TOOL_INVALID_JSON: {tool_name}")

    return data


def _require_field(data, field_path, tool_name):
    """
    Extract a nested field from a dict using dot/bracket notation description.
    Supports simple keys and index 0 (immediate_next_steps[0]).
    Calls _fail() if the field is absent or the list is empty.
    """
    if field_path == "immediate_next_steps[0]":
        lst = data.get("immediate_next_steps")
        if lst is None:
            _fail(f"ECS_TOOL_MISSING_FIELD: immediate_next_steps in {tool_name} output")
        if not lst:
            _fail(f"ECS_TOOL_MISSING_FIELD: immediate_next_steps[0] in {tool_name} output")
        return lst[0]
    value = data.get(field_path)
    if value is None:
        _fail(f"ECS_TOOL_MISSING_FIELD: {field_path} in {tool_name} output")
    return value

# ---------------------------------------------------------------------------
# Consistency check logic
# ---------------------------------------------------------------------------

def run_check(objective_path):
    """
    Run all three consistency comparisons. Returns the output dict.
    All comparisons are evaluated regardless of individual results.
    """
    filename = os.path.basename(objective_path)

    # --- Parse current-objective.md ---
    sections = parse_sections(objective_path)

    for section in REQUIRED_SECTIONS:
        if section not in sections:
            _fail(f"MISSING_SECTION: {section} in {filename}")
        body = _strip_body(sections[section])
        if not body:
            _fail(f"EMPTY_SECTION: {section} in {filename}")

    # First item from Immediate Next Steps.
    next_steps_body = _strip_body(sections["Immediate Next Steps"])
    next_steps = _extract_list_items(next_steps_body)
    if not next_steps:
        _fail(f"EMPTY_SECTION: Immediate Next Steps contained no list items")
    parsed_first_step = next_steps[0]

    # Full stripped Current Objective joined with " | " (same rule as read_state.py).
    objective_body = _strip_body(sections["Current Objective"])
    parsed_objective = " | ".join(objective_body)

    # --- Run ECS tools ---
    resolver_data    = _run_ecs_tool(RESOLVER_TOOL)
    read_state_data  = _run_ecs_tool(READ_STATE_TOOL)

    resolver_decision      = _require_field(resolver_data,   "decision",               "resolve_next_action.py")
    read_state_step_0      = _require_field(read_state_data, "immediate_next_steps[0]","read_state.py")
    read_state_objective   = _require_field(read_state_data, "current_objective",      "read_state.py")

    # --- Run comparisons ---
    comparisons = [
        {
            "name":     "resolver_decision_vs_read_state_step_0",
            "expected": resolver_decision,
            "actual":   read_state_step_0,
        },
        {
            "name":     "read_state_step_0_vs_parsed_objective",
            "expected": parsed_first_step,
            "actual":   read_state_step_0,
        },
        {
            "name":     "read_state_objective_vs_parsed_objective",
            "expected": parsed_objective,
            "actual":   read_state_objective,
        },
    ]

    checks = []
    failures = []

    for comp in comparisons:
        passed = comp["expected"] == comp["actual"]
        status = "PASS" if passed else "FAIL"
        checks.append({
            "name":     comp["name"],
            "status":   status,
            "expected": comp["expected"],
            "actual":   comp["actual"],
        })
        if not passed:
            failures.append(comp["name"])

    return {
        "status":     "FAIL" if failures else "PASS",
        "check_name": "ecs_consistency_check",
        "checks":     checks,
        "failures":   failures,
    }

# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="System Guardian: detect contradictions between ECS surfaces and authoritative state."
    )
    parser.add_argument(
        "--objective",
        default=DEFAULT_OBJECTIVE,
        help="Path to current-objective.md",
    )
    args = parser.parse_args()

    result = run_check(args.objective)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
