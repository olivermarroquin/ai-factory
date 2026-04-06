#!/usr/bin/env python3
"""
System Guardian: Missing Control Artifact Check

Detects when state claims a control layer is complete but required artifacts
are missing or empty on the filesystem.

Each claim entry in the mapping table defines a trigger substring and the
artifact paths that must exist and be non-empty for that claim to be valid.
A claim is only evaluated if its trigger is found in the combined Current Phase
+ Current Objective text (case-insensitive substring match).

Usage:
    python check_missing_artifact.py
    python check_missing_artifact.py --state <path> --objective <path> --authority <path>
"""

import argparse
import json
import os
import sys

# ---------------------------------------------------------------------------
# Default paths
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

DEFAULT_STATE     = os.path.join(REPO_ROOT, "system-state", "current-system-state.md")
DEFAULT_OBJECTIVE = os.path.join(REPO_ROOT, "system-state", "current-objective.md")
DEFAULT_AUTHORITY = os.path.join(REPO_ROOT, "system-state", "authoritative-files.md")

# ---------------------------------------------------------------------------
# Explicit claim-to-artifact mapping table (v1)
#
# Each entry:
#   "name":     identifier used in output
#   "trigger":  case-insensitive substring searched in combined state text
#   "artifacts": repo-relative paths that must exist and be non-empty
#
# Add new entries here when new control layers are completed and claimed.
# ---------------------------------------------------------------------------

CLAIM_MAP = [
    {
        "name":    "system_state_surface_complete",
        "trigger": "system state surface complete",
        "artifacts": [
            "system-state/current-system-state.md",
            "system-state/current-objective.md",
            "system-state/authoritative-files.md",
        ],
    },
    {
        "name":    "ecs_mvp_complete",
        "trigger": "ecs mvp complete",
        "artifacts": [
            "docs/ecs-mvp-spec.md",
            "tools/ecs/resolve_next_action.py",
            "docs/ecs-gate-check-spec.md",
            "tools/ecs/check_action_allowed.py",
            "docs/ecs-read-state-spec.md",
            "tools/ecs/read_state.py",
            "docs/ecs-mvp-exit-review.md",
        ],
    },
]

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

# ---------------------------------------------------------------------------
# Failure helper
# ---------------------------------------------------------------------------

def _fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Artifact presence checks
# ---------------------------------------------------------------------------

def _check_artifacts(artifact_rel_paths):
    """Return (missing, empty) lists of repo-relative paths."""
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
# Missing artifact check logic
# ---------------------------------------------------------------------------

def run_check(state_path, objective_path, authority_path):
    """
    Parse Current Phase and Current Objective from state files.
    For each entry in CLAIM_MAP, check whether the trigger is present in the
    combined text. If present, verify all required artifacts exist and are non-empty.
    """
    state_filename     = os.path.basename(state_path)
    objective_filename = os.path.basename(objective_path)

    # Validate authority file parses cleanly.
    parse_sections(authority_path)

    # Parse state file — require Current Phase.
    state_sections = parse_sections(state_path)
    if "Current Phase" not in state_sections:
        _fail(f"MISSING_SECTION: Current Phase in {state_filename}")
    phase_body = _strip_body(state_sections["Current Phase"])
    if not phase_body:
        _fail(f"EMPTY_SECTION: Current Phase in {state_filename}")
    phase_text = " | ".join(phase_body)

    # Parse objective file — require Current Objective.
    objective_sections = parse_sections(objective_path)
    if "Current Objective" not in objective_sections:
        _fail(f"MISSING_SECTION: Current Objective in {objective_filename}")
    objective_body = _strip_body(objective_sections["Current Objective"])
    if not objective_body:
        _fail(f"EMPTY_SECTION: Current Objective in {objective_filename}")
    objective_text = " | ".join(objective_body)

    # Combined lowercased text used for trigger matching.
    combined_text = (phase_text + " | " + objective_text).lower()

    # --- Evaluate each claim entry ---

    checks = []
    failures = []

    for entry in CLAIM_MAP:
        name      = entry["name"]
        trigger   = entry["trigger"]
        artifacts = entry["artifacts"]

        if trigger.lower() not in combined_text:
            # Trigger not found in state — claim not active; skip artifact check.
            checks.append({
                "name":               name,
                "status":             "NOT_APPLICABLE",
                "claim_text":         trigger,
                "required_artifacts": list(artifacts),
                "missing_artifacts":  [],
                "empty_artifacts":    [],
            })
            continue

        # Trigger found — verify all artifacts.
        missing, empty = _check_artifacts(artifacts)

        if missing or empty:
            status = "FAIL"
            failures.append(name)
        else:
            status = "PASS"

        checks.append({
            "name":               name,
            "status":             status,
            "claim_text":         trigger,
            "required_artifacts": list(artifacts),
            "missing_artifacts":  missing,
            "empty_artifacts":    empty,
        })

    return {
        "status":     "FAIL" if failures else "PASS",
        "check_name": "missing_control_artifact_check",
        "checks":     checks,
        "failures":   failures,
    }

# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="System Guardian: detect missing artifacts for claimed-complete control layers."
    )
    parser.add_argument("--state",     default=DEFAULT_STATE,
                        help="Path to current-system-state.md")
    parser.add_argument("--objective", default=DEFAULT_OBJECTIVE,
                        help="Path to current-objective.md")
    parser.add_argument("--authority", default=DEFAULT_AUTHORITY,
                        help="Path to authoritative-files.md")
    args = parser.parse_args()

    result = run_check(args.state, args.objective, args.authority)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
