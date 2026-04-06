#!/usr/bin/env python3
"""
ECS Gate-Check: Deterministic action allow/block resolver.

Given a proposed action string, determines whether it is allowed to execute
based only on authoritative system state. Does not perform semantic interpretation.

Usage:
    python check_action_allowed.py --action "proposed action text"
    python check_action_allowed.py --action "..." --state <path> --objective <path> --authority <path>
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

# ---------------------------------------------------------------------------
# Section definitions (identical to resolve_next_action.py)
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
# Parser (same rules as resolve_next_action.py)
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
    Strips markdown bold markers (**).
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
# Gate-check logic
# ---------------------------------------------------------------------------

def check(all_sections, proposed_action):
    """
    Determine whether proposed_action is allowed.

    Rules:
    - allowed = true only if the proposed action matches a next step AND is not blocked.
    - Matching: case-insensitive exact equality against each Immediate Next Steps item.
    - Blocking: case-insensitive substring — a blocker item blocks if it is found
      literally within the proposed action string.
    """
    # Validate required sections are present and non-empty.
    for canonical, filename in REQUIRED_SECTIONS.items():
        if canonical not in all_sections:
            _fail(f"MISSING_SECTION: {canonical} in {filename}")
        body = _strip_body(all_sections[canonical])
        if not body:
            _fail(f"EMPTY_SECTION: {canonical} in {filename}")

    # Extract next steps.
    next_steps_body = _strip_body(all_sections["Immediate Next Steps"])
    next_steps = _extract_list_items(next_steps_body)
    if not next_steps:
        _fail("EMPTY_SECTION: Immediate Next Steps contained no list items")

    # Extract blockers.
    constraints_body = _strip_body(all_sections["Current Constraints"])
    constraint_items = _extract_list_items(constraints_body)

    not_doing_items = []
    if "Not Doing Yet" in all_sections:
        not_doing_body = _strip_body(all_sections["Not Doing Yet"])
        not_doing_items = _extract_list_items(not_doing_body)

    all_blockers = constraint_items + not_doing_items

    # Step 1: find an exact case-insensitive match in Immediate Next Steps.
    proposed_lower = proposed_action.strip().lower()
    matched_step = None
    for step in next_steps:
        if step.strip().lower() == proposed_lower:
            matched_step = step
            break

    # Step 2: check whether any blocker is a substring of the proposed action.
    blocked_by = []
    for blocker in all_blockers:
        if blocker.lower() in proposed_lower:
            blocked_by.append(blocker)

    # Determine verdict.
    if matched_step is None:
        reason = "Proposed action does not exactly match any item in Immediate Next Steps."
        allowed = False
    elif blocked_by:
        reason = "Proposed action matches a next step but is explicitly blocked."
        allowed = False
    else:
        reason = "Proposed action matches an item in Immediate Next Steps and is not blocked."
        allowed = True

    return {
        "proposed_action": proposed_action,
        "allowed": allowed,
        "reason": reason,
        "matched_next_step": matched_step,
        "blocked_by": blocked_by,
    }

# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="ECS Gate-Check: determine whether a proposed action is allowed by current state."
    )
    parser.add_argument(
        "--action",
        required=True,
        help="Proposed action string to check against authoritative state.",
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
    _                  = parse_sections(args.authority)  # validated; not used in gate logic
    objective_sections = parse_sections(args.objective)

    # Merge; detect cross-file duplicate recognized sections.
    all_sections = {}
    for label, body in state_sections.items():
        all_sections[label] = body
    for label, body in objective_sections.items():
        if label in all_sections:
            _fail(f"DUPLICATE_SECTION: {label} found in both state and objective files")
        all_sections[label] = body

    result = check(all_sections, args.action)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
