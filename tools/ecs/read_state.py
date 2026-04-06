#!/usr/bin/env python3
"""
ECS Read-State: Deterministic system state snapshot emitter.

Reads authoritative system-state markdown files and emits a structured JSON
snapshot of current ECS-readable state. Does not resolve actions or apply
gate logic.

Usage:
    python read_state.py
    python read_state.py --state <path> --objective <path> --authority <path>
"""

import argparse
import json
import os
import sys

# ---------------------------------------------------------------------------
# Default input file paths (repo-relative from this script's location)
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

DEFAULT_FILES = {
    "state":     os.path.join(REPO_ROOT, "system-state", "current-system-state.md"),
    "authority": os.path.join(REPO_ROOT, "system-state", "authoritative-files.md"),
    "objective": os.path.join(REPO_ROOT, "system-state", "current-objective.md"),
}

# Repo-relative paths surfaced in output (fixed; not derived from args).
AUTHORITATIVE_INPUT_PATHS = [
    "system-state/current-system-state.md",
    "system-state/authoritative-files.md",
    "system-state/current-objective.md",
]

# ---------------------------------------------------------------------------
# Section definitions (identical to resolve_next_action.py / check_action_allowed.py)
# ---------------------------------------------------------------------------

RECOGNIZED_SECTIONS = {
    "current phase":        "Current Phase",
    "current objective":    "Current Objective",
    "immediate next steps": "Immediate Next Steps",
    "current constraints":  "Current Constraints",
    "not doing yet":        "Not Doing Yet",
    "exit condition":       "Exit Condition",
}

REQUIRED_SECTIONS = {
    "Current Phase":        "current-system-state.md",
    "Current Objective":    "current-objective.md",
    "Immediate Next Steps": "current-objective.md",
    "Current Constraints":  "current-objective.md",
}

# ---------------------------------------------------------------------------
# Parser (same rules as resolve_next_action.py / check_action_allowed.py)
# ---------------------------------------------------------------------------

def _normalize_header(line):
    """
    Returns normalized header text for ## and ### only.
    H1 (single #) is skipped as document title.
    H4 and deeper are ignored.
    Lines where # sequences are not followed by a space are not headers.
    """
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
    """Remove horizontal rules and blank lines. Return list of non-empty stripped strings."""
    result = []
    for line in lines:
        text = line.strip()
        if not text or text == "---":
            continue
        result.append(text)
    return result


def _extract_list_items(lines):
    """
    Extract ordered or unordered list items from body lines.
    Strips markdown bold markers (**). Preserves original order.
    """
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
# Read-state logic
# ---------------------------------------------------------------------------

def build_snapshot(all_sections):
    """
    Build the state snapshot dict from parsed sections.
    Validates required sections, then surfaces all recognized sections.
    No interpretation. No summaries. No inferred fields.
    """
    # Validate required sections are present and non-empty.
    for canonical, filename in REQUIRED_SECTIONS.items():
        if canonical not in all_sections:
            _fail(f"MISSING_SECTION: {canonical} in {filename}")
        body = _strip_body(all_sections[canonical])
        if not body:
            _fail(f"EMPTY_SECTION: {canonical} in {filename}")

    # current_phase: full stripped content, joined with " | " if multi-line.
    phase_body = _strip_body(all_sections["Current Phase"])
    current_phase = " | ".join(phase_body)

    # current_objective: full stripped content, joined with " | " if multi-line.
    objective_body = _strip_body(all_sections["Current Objective"])
    current_objective = " | ".join(objective_body)

    # immediate_next_steps: ordered list items, original order preserved.
    next_steps_body = _strip_body(all_sections["Immediate Next Steps"])
    immediate_next_steps = _extract_list_items(next_steps_body)
    if not immediate_next_steps:
        _fail("EMPTY_SECTION: Immediate Next Steps contained no list items")

    # current_constraints: list items only.
    constraints_body = _strip_body(all_sections["Current Constraints"])
    current_constraints = _extract_list_items(constraints_body)

    # not_doing_yet: list items, or [] if section absent.
    not_doing_yet = []
    if "Not Doing Yet" in all_sections:
        not_doing_body = _strip_body(all_sections["Not Doing Yet"])
        not_doing_yet = _extract_list_items(not_doing_body)

    # exit_condition: full stripped content joined with " | ", or NOT_EXPLICIT_IN_STATE.
    exit_condition = "NOT_EXPLICIT_IN_STATE"
    if "Exit Condition" in all_sections:
        ec_body = _strip_body(all_sections["Exit Condition"])
        if ec_body:
            exit_condition = " | ".join(ec_body)

    return {
        "current_phase":         current_phase,
        "current_objective":     current_objective,
        "immediate_next_steps":  immediate_next_steps,
        "current_constraints":   current_constraints,
        "not_doing_yet":         not_doing_yet,
        "exit_condition":        exit_condition,
        "authoritative_inputs":  AUTHORITATIVE_INPUT_PATHS,
    }

# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="ECS Read-State: emit a structured JSON snapshot of current authoritative system state."
    )
    parser.add_argument(
        "--state",
        default=DEFAULT_FILES["state"],
        help="Path to current-system-state.md",
    )
    parser.add_argument(
        "--authority",
        default=DEFAULT_FILES["authority"],
        help="Path to authoritative-files.md",
    )
    parser.add_argument(
        "--objective",
        default=DEFAULT_FILES["objective"],
        help="Path to current-objective.md",
    )
    args = parser.parse_args()

    state_sections     = parse_sections(args.state)
    _                  = parse_sections(args.authority)  # validated; content not surfaced
    objective_sections = parse_sections(args.objective)

    # Merge; detect cross-file duplicate recognized sections.
    all_sections = {}
    for label, body in state_sections.items():
        all_sections[label] = body
    for label, body in objective_sections.items():
        if label in all_sections:
            _fail(f"DUPLICATE_SECTION: {label} found in both state and objective files")
        all_sections[label] = body

    result = build_snapshot(all_sections)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
