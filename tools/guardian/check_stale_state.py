#!/usr/bin/env python3
"""
System Guardian: Stale State Check

Detects when Immediate Next Steps lists work that is already complete,
based only on whether required artifacts exist as non-empty files.

A step is stale only if its text exactly matches a mapping key (case-insensitive)
AND every required artifact for that step exists and is non-empty.

Usage:
    python check_stale_state.py
    python check_stale_state.py --objective <path>
"""

import argparse
import json
import os
import sys

# ---------------------------------------------------------------------------
# Default input file paths (repo-relative from this script's location)
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

DEFAULT_OBJECTIVE = os.path.join(REPO_ROOT, "system-state", "current-objective.md")

# ---------------------------------------------------------------------------
# Explicit artifact mapping (v1)
#
# Keys are normalized step texts (lowercase, stripped, bold markers removed).
# Values are lists of repo-relative artifact paths.
#
# A step is stale only if its normalized text exactly matches a key here
# AND every artifact in the value list exists and is non-empty.
# ---------------------------------------------------------------------------

STEP_ARTIFACT_MAP = {
    # System State Surface
    "complete system state surface (this conversation) \u2014 write `current-system-state.md`, `authoritative-files.md`, `current-objective.md`.": [
        "system-state/current-system-state.md",
        "system-state/authoritative-files.md",
        "system-state/current-objective.md",
    ],
    # ECS resolver validation
    "validate resolver output against updated state \u2014 run `tools/ecs/resolve_next_action.py` and confirm the decision reflects the correct current next step.": [
        "tools/ecs/resolve_next_action.py",
    ],
    # ECS gate-check
    "define ecs gate-check \u2014 specify and implement the rule that determines whether a proposed action is allowed to execute given the current state. this is the core gate mechanism of ecs mvp.": [
        "docs/ecs-gate-check-spec.md",
        "tools/ecs/check_action_allowed.py",
    ],
    # ECS read-state interface
    "define ecs read-state interface \u2014 specify and implement how the ecs surfaces current system state to an operator or agent in a structured, queryable form.": [
        "docs/ecs-read-state-spec.md",
        "tools/ecs/read_state.py",
    ],
    # ECS MVP exit review
    "ecs mvp exit review \u2014 confirm all exit condition criteria are met before proceeding to system guardian.": [
        "docs/ecs-mvp-exit-review.md",
    ],
    # System Guardian spec
    "system guardian mvp \u2014 define scope, specify invariant checks, drift detection, and health reporting for the controlled pipeline.": [
        "docs/system-guardian-mvp-spec.md",
    ],
}

# ---------------------------------------------------------------------------
# Section definitions (same parser contract as ECS tools)
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
# Parser (same rules as ECS tools)
# ---------------------------------------------------------------------------

def _normalize_header(line):
    """
    Returns normalized header text for ## and ### only.
    H1 skipped. H4 and deeper ignored.
    Lines without a space after # markers are not headers.
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
    """Remove horizontal rules and blank lines. Return non-empty stripped strings."""
    result = []
    for line in lines:
        text = line.strip()
        if not text or text == "---":
            continue
        result.append(text)
    return result


def _extract_list_items(lines):
    """Extract ordered/unordered list items. Strip bold markers. Preserve order."""
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
# Artifact checks
# ---------------------------------------------------------------------------

def _check_artifacts(artifact_rel_paths):
    """
    Check each artifact path for existence and non-emptiness.
    Returns (missing, empty) — lists of repo-relative paths.
    """
    missing = []
    empty = []
    for rel_path in artifact_rel_paths:
        abs_path = os.path.join(REPO_ROOT, rel_path)
        if not os.path.exists(abs_path):
            missing.append(rel_path)
        elif os.path.getsize(abs_path) == 0:
            empty.append(rel_path)
    return missing, empty

# ---------------------------------------------------------------------------
# Stale state check logic
# ---------------------------------------------------------------------------

def run_check(objective_path):
    """
    Parse Immediate Next Steps from current-objective.md and classify each step.
    Returns the full output dict.
    """
    sections = parse_sections(objective_path)
    filename = os.path.basename(objective_path)

    if "Immediate Next Steps" not in sections:
        _fail(f"MISSING_SECTION: Immediate Next Steps in {filename}")

    body = _strip_body(sections["Immediate Next Steps"])
    if not body:
        _fail(f"EMPTY_SECTION: Immediate Next Steps in {filename}")

    steps = _extract_list_items(body)
    if not steps:
        _fail("EMPTY_SECTION: Immediate Next Steps contained no list items")

    results = []
    failures = []

    for step in steps:
        step_key = step.strip().lower()
        artifacts = STEP_ARTIFACT_MAP.get(step_key)

        if artifacts is None:
            # No mapping exists for this step — cannot determine staleness.
            results.append({
                "step": step,
                "classification": "UNMAPPED",
                "required_artifacts": [],
                "missing_artifacts": [],
                "empty_artifacts": [],
            })
            continue

        missing, empty = _check_artifacts(artifacts)

        if not missing and not empty:
            # All artifacts present and non-empty — step is stale.
            classification = "STALE"
            failures.append(step)
        else:
            # At least one artifact is absent or empty — step is current.
            classification = "CURRENT"

        results.append({
            "step": step,
            "classification": classification,
            "required_artifacts": list(artifacts),
            "missing_artifacts": missing,
            "empty_artifacts": empty,
        })

    status = "FAIL" if failures else "PASS"

    return {
        "status": status,
        "check_name": "stale_state_check",
        "results": results,
        "failures": failures,
    }

# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="System Guardian: detect stale steps in Immediate Next Steps."
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
