#!/usr/bin/env python3
"""
ECS MVP: Deterministic parser + rule-based resolver.

Reads authoritative system-state markdown files and emits the single next
allowed action as JSON. Does not perform semantic interpretation.

Usage:
    python resolve_next_action.py
    python resolve_next_action.py --state <path> --objective <path> --authority <path>
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
# Section definitions
# ---------------------------------------------------------------------------

# Sections the parser recognizes (normalized: lowercase, stripped).
# Maps normalized name -> canonical label used internally.
RECOGNIZED_SECTIONS = {
    "current phase":       "Current Phase",
    "current objective":   "Current Objective",
    "immediate next steps": "Immediate Next Steps",
    "current constraints": "Current Constraints",
    "not doing yet":       "Not Doing Yet",
    "exit condition":      "Exit Condition",
}

# Required sections and which file each is expected in (for clear error messages).
REQUIRED_SECTIONS = {
    "Current Phase":          "current-system-state.md",
    "Current Objective":      "current-objective.md",
    "Immediate Next Steps":   "current-objective.md",
    "Current Constraints":    "current-objective.md",
}


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def _normalize_header(line):
    """
    Strip leading '#' markers and whitespace; lowercase.
    Returns None if not a header or if H1 (document title, not a section).
    H1 lines (single '#') are document titles and are skipped.
    """
    stripped = line.lstrip()
    if not stripped.startswith("#"):
        return None
    # Count leading '#' characters to determine heading level.
    level = 0
    for ch in stripped:
        if ch == "#":
            level += 1
        else:
            break
    if level == 1:
        # H1 is the document title — not a parseable section.
        return None
    if level > 3:
        # H4 and deeper are not recognized section headers.
        return None
    # Require a space immediately after the '#' markers (e.g. "## Section Name").
    # A '#' sequence not followed by a space is not a valid section header.
    if not stripped[level:level + 1] == " ":
        return None
    text = stripped[level:].strip()
    return text.lower() if text else None


def parse_sections(filepath):
    """
    Parse a markdown file into a dict of { canonical_label: [lines] }.

    Raises SystemExit on:
      - file not found / unreadable
      - duplicate recognized section
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            raw_lines = f.readlines()
    except FileNotFoundError:
        _fail(f"MISSING_FILE: {filepath}")
    except OSError as e:
        _fail(f"MISSING_FILE: {filepath} ({e})")

    filename = os.path.basename(filepath)
    sections = {}       # canonical_label -> list of content lines
    current_label = None

    for line in raw_lines:
        normalized = _normalize_header(line)
        if normalized is not None:
            # Is this a recognized section?
            canonical = RECOGNIZED_SECTIONS.get(normalized)
            if canonical is not None:
                if canonical in sections:
                    _fail(f"DUPLICATE_SECTION: {canonical} in {filename}")
                sections[canonical] = []
                current_label = canonical
            else:
                # Unrecognized header: stop accumulating into previous section.
                current_label = None
        else:
            if current_label is not None:
                sections[current_label].append(line)

    return sections


def _strip_body(lines):
    """
    Remove horizontal rules, blank lines, and markdown bold/formatting markers.
    Returns a list of non-empty stripped strings.
    """
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
    Accepts lines beginning with: '- ', '* ', or '<digit>. '.
    Returns plain text of each item (stripped of marker and bold markers).
    """
    items = []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        # Ordered list: "1. ", "2. ", etc.
        if len(text) >= 3 and text[0].isdigit() and text[1] == "." and text[2] == " ":
            item = text[3:].strip()
        elif text.startswith("- ") or text.startswith("* "):
            item = text[2:].strip()
        else:
            # Non-list line: skip (we only want list items for step extraction)
            continue
        # Strip markdown bold markers (**text**)
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
# Resolver
# ---------------------------------------------------------------------------

def resolve(all_sections):
    """
    Apply rule-based resolution. Returns the output dict on success.
    Calls _fail() on any failure condition.
    """
    # Validate required sections are present and non-empty.
    for canonical, filename in REQUIRED_SECTIONS.items():
        if canonical not in all_sections:
            _fail(f"MISSING_SECTION: {canonical} in {filename}")
        body = _strip_body(all_sections[canonical])
        if not body:
            _fail(f"EMPTY_SECTION: {canonical} in {filename}")

    # Extract candidate actions from Immediate Next Steps (ordered).
    next_steps_body = _strip_body(all_sections["Immediate Next Steps"])
    candidates = _extract_list_items(next_steps_body)
    if not candidates:
        _fail("EMPTY_SECTION: Immediate Next Steps contained no list items")

    # Extract blockers from Current Constraints.
    constraints_body = _strip_body(all_sections["Current Constraints"])
    constraint_items = _extract_list_items(constraints_body)

    # Extract blockers from Not Doing Yet (optional).
    not_doing_items = []
    if "Not Doing Yet" in all_sections:
        not_doing_body = _strip_body(all_sections["Not Doing Yet"])
        not_doing_items = _extract_list_items(not_doing_body)

    all_blockers = constraint_items + not_doing_items

    # Filter candidates: remove any whose text is explicitly blocked.
    # A candidate is blocked if any blocker phrase appears in it (case-insensitive substring).
    # This is exact substring matching, not semantic inference.
    blocked_actions = []
    valid_candidates = []

    for candidate in candidates:
        candidate_lower = candidate.lower()
        blocked = False
        for blocker in all_blockers:
            # Check for meaningful overlap: blocker key phrases in candidate.
            # We use the blocker text itself as the match signal (substring).
            if _candidate_blocked_by(candidate_lower, blocker.lower()):
                blocked = True
                if blocker not in blocked_actions:
                    blocked_actions.append(blocker)
                break
        if not blocked:
            valid_candidates.append(candidate)

    if not valid_candidates:
        _fail("NO_VALID_ACTION: all actions excluded by constraints or not-doing-yet")

    # The first valid candidate in original order is the decision.
    # If there is exactly one, it is unambiguous.
    # If there are multiple, the first (by explicit numbering) is the decision
    # only if the list was explicitly ordered (numbered). Otherwise fail.
    decision = valid_candidates[0]

    # Determine if steps were numbered (ordered list) — if so, first is deterministic.
    # Check if the raw Immediate Next Steps lines contained numbered items.
    raw_steps = _strip_body(all_sections["Immediate Next Steps"])
    is_ordered = any(
        line.strip() and line.strip()[0].isdigit() and len(line.strip()) >= 3
        and line.strip()[1] == "." and line.strip()[2] == " "
        for line in raw_steps
    )

    if len(valid_candidates) > 1 and not is_ordered:
        _fail(
            "AMBIGUOUS_ACTION: cannot determine single next action from explicit state"
            f" — {len(valid_candidates)} candidates remain and list is unordered"
        )

    # why: reference explicit state only; do not assume ordering within Current Objective.
    why = "Derived from Current Objective and Immediate Next Steps (explicit state)."

    # state_impact: full stripped content of Current Phase, joined deterministically.
    # No first-line selection; no interpretation added.
    phase_body = _strip_body(all_sections["Current Phase"])
    phase_text = " | ".join(phase_body) if phase_body else "NOT_EXPLICIT_IN_STATE"
    state_impact = f"Current Phase: {phase_text}"

    # placement: full stripped content of Exit Condition if present, joined deterministically.
    # No first-line selection.
    placement = "NOT_EXPLICIT_IN_STATE"
    if "Exit Condition" in all_sections:
        ec_body = _strip_body(all_sections["Exit Condition"])
        if ec_body:
            placement = " | ".join(ec_body)

    output = {
        "decision": decision,
        "why": why,
        # Full original ordered list from Immediate Next Steps, unfiltered.
        "exact_next_steps": candidates,
        "placement": placement,
        "state_impact": state_impact,
        "delegation_opportunity": "NONE_IN_MVP",
        "blocked_actions": blocked_actions,
    }

    return output


def _candidate_blocked_by(candidate_lower, blocker_lower):
    """
    Return True if the blocker text is an exact substring of the candidate.

    Strictly text-based substring matching only. No word-overlap heuristics,
    no semantic inference. If the blocker phrase does not appear literally
    inside the candidate, the candidate is not considered blocked.
    """
    return blocker_lower in candidate_lower


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="ECS MVP: emit the single next allowed action from authoritative state files."
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

    # Parse all three files. Sections accumulate into one dict keyed by canonical label.
    # If the same recognized section appears in multiple files, the duplicate rule fires.
    # Each file is parsed independently; we merge after.
    state_sections     = parse_sections(args.state)
    _                  = parse_sections(args.authority)   # parsed for structure validation; not used in resolution
    objective_sections = parse_sections(args.objective)

    # Merge: check for cross-file duplicate recognized sections.
    all_sections = {}
    for label, body in state_sections.items():
        all_sections[label] = body
    for label, body in objective_sections.items():
        if label in all_sections:
            _fail(f"DUPLICATE_SECTION: {label} found in both state and objective files")
        all_sections[label] = body

    result = resolve(all_sections)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
