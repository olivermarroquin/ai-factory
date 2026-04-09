#!/usr/bin/env python3
"""
System Guardian: Objective Alignment Check

Ensures the current objective defines a clear, actionable next step.

Blocks execution if:
- ## Immediate Next Steps section is missing
- section has no list items
- first list item is empty
- first list item is vague (matches a known vague keyword)

Usage:
    python check_objective_alignment.py
    python check_objective_alignment.py --objective <path>
"""

import argparse
import json
import os
import sys

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

DEFAULT_OBJECTIVE = os.path.join(REPO_ROOT, "system-state", "current-objective.md")

# ---------------------------------------------------------------------------
# Vague keyword detection
# ---------------------------------------------------------------------------

VAGUE_KEYWORDS = ["continue", "improve", "work more"]

# ---------------------------------------------------------------------------
# System-building objective detection
#
# If the first Immediate Next Step is system-building work, migration
# execution should be blocked — execution context is misaligned with objective.
# ---------------------------------------------------------------------------

SYSTEM_BUILDING_KEYWORDS = ["guardian", "enforcement", "system", "control"]

# ---------------------------------------------------------------------------
# Failure helper
# ---------------------------------------------------------------------------

def _fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def _parse_immediate_next_steps(filepath):
    """
    Extract lines from the ## Immediate Next Steps section.
    Returns None if section is not found.
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        _fail(f"MISSING_FILE: {filepath}")
    except OSError as e:
        _fail(f"MISSING_FILE: {filepath} ({e})")

    in_section = False
    section_lines = []

    for line in lines:
        stripped = line.strip()

        # Detect ## Immediate Next Steps (level-2 header, case-insensitive)
        if stripped.startswith("##") and not stripped.startswith("###"):
            header_text = stripped.lstrip("#").strip().lower()
            if header_text == "immediate next steps":
                in_section = True
                continue
            elif in_section:
                # Hit the next section — stop collecting
                break
        elif in_section:
            section_lines.append(stripped)

    if not in_section:
        return None

    return section_lines

# ---------------------------------------------------------------------------
# Check
# ---------------------------------------------------------------------------

def run_check(objective_path):
    section_lines = _parse_immediate_next_steps(objective_path)

    # 1. Section must exist
    if section_lines is None:
        return {
            "status":     "FAIL",
            "check_name": "objective_alignment",
            "failures":   ["objective_not_actionable"],
            "reason":     "Immediate Next Steps section is missing",
        }

    # 2. Must contain at least one list item
    def _extract_item(line):
        """Return item text if line is a list item, else None."""
        if line.startswith("- ") or line.startswith("* "):
            return line[2:].strip()
        if line.startswith("-") or line.startswith("*"):
            return line[1:].strip()
        # Ordered: one or more digits followed by ". "
        i = 0
        while i < len(line) and line[i].isdigit():
            i += 1
        if i > 0 and i < len(line) and line[i] == "." and i + 1 < len(line) and line[i + 1] == " ":
            return line[i + 2:].strip()
        return None

    list_items = [
        text for text in (_extract_item(line) for line in section_lines)
        if text is not None
    ]

    if not list_items:
        return {
            "status":     "FAIL",
            "check_name": "objective_alignment",
            "failures":   ["objective_not_actionable"],
            "reason":     "Immediate Next Steps section has no list items",
        }

    # 3. First item must be non-empty
    first_item = list_items[0]
    if not first_item:
        return {
            "status":     "FAIL",
            "check_name": "objective_alignment",
            "failures":   ["objective_not_actionable"],
            "reason":     "First item in Immediate Next Steps is empty",
        }

    # 4. First item must not be vague
    first_item_lower = first_item.lower()
    for keyword in VAGUE_KEYWORDS:
        if keyword in first_item_lower:
            return {
                "status":     "FAIL",
                "check_name": "objective_alignment",
                "failures":   ["objective_not_actionable"],
                "reason":     f"First item in Immediate Next Steps is too vague (matched: '{keyword}')",
                "first_item": first_item,
            }

    # 5. Objective must not be system-building while migration execution is attempted
    # Match on whole words only — substring matching would incorrectly match
    # "controlled" for "control", "controller" for "control", etc.
    first_item_words = set(first_item_lower.split())
    for keyword in SYSTEM_BUILDING_KEYWORDS:
        keyword_words = keyword.split()
        if len(keyword_words) == 1:
            matched = keyword_words[0] in first_item_words
        else:
            # Multi-word phrase: require all words to appear as a contiguous sequence
            matched = keyword_words[0] in first_item_lower and keyword in first_item_lower
        if matched:
            return {
                "status":     "FAIL",
                "check_name": "objective_alignment",
                "failures":   ["objective_mismatch_execution"],
                "reason":     f"Objective is system-building (matched: '{keyword}') — migration execution is not aligned with current objective",
                "first_item": first_item,
            }

    return {
        "status":     "PASS",
        "check_name": "objective_alignment",
        "failures":   [],
        "first_item": first_item,
    }


def main():
    parser = argparse.ArgumentParser(
        description="System Guardian: verify current objective has an actionable next step."
    )
    parser.add_argument("--objective", default=DEFAULT_OBJECTIVE,
                        help="Path to current-objective.md")
    args = parser.parse_args()

    result = run_check(args.objective)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
