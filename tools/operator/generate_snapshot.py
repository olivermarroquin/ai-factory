#!/usr/bin/env python3
"""
Operator Snapshot Generator — v1

Produces a single JSON snapshot describing the current control state of the
ai-factory system. Reads only from authoritative sources. No file writes,
no execution, no external model calls.

Usage:
    python tools/operator/generate_snapshot.py
"""

import json
import os
import re
import subprocess
import sys

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

OBJECTIVE_FILE    = os.path.join(REPO_ROOT, "system-state", "current-objective.md")
SYSTEM_STATE_FILE = os.path.join(REPO_ROOT, "system-state", "current-system-state.md")
BATCH_REPORTS_DIR = os.path.join(REPO_ROOT, "batch-reports")
QUEUE_RUNS_DIR    = os.path.join(REPO_ROOT, "queue-runs")
OUTCOME_RECORDS_DIR = os.path.join(REPO_ROOT, "outcome-records")
TRANSITION_RECORDS_DIR = os.path.join(REPO_ROOT, "transition-records")

RESOLVER_TOOL  = os.path.join(REPO_ROOT, "tools", "ecs", "resolve_next_action.py")
GUARDIAN_TOOL  = os.path.join(REPO_ROOT, "tools", "guardian", "run_guardian.py")

# ---------------------------------------------------------------------------
# Markdown parser (identical contract to ECS / Guardian tools)
# ---------------------------------------------------------------------------

RECOGNIZED_SECTIONS = {
    "current phase":        "Current Phase",
    "current objective":    "Current Objective",
    "immediate next steps": "Immediate Next Steps",
    "current constraints":  "Current Constraints",
    "not doing yet":        "Not Doing Yet",
    "exit condition":       "Exit Condition",
}


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
    try:
        with open(filepath, encoding="utf-8") as f:
            raw_lines = f.readlines()
    except FileNotFoundError:
        _abort(f"MISSING_FILE: {filepath}")
    except OSError as e:
        _abort(f"MISSING_FILE: {filepath} ({e})")

    sections = {}
    current_label = None

    for line in raw_lines:
        normalized = _normalize_header(line)
        if normalized is not None:
            canonical = RECOGNIZED_SECTIONS.get(normalized)
            if canonical is not None:
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
# Abort helper
# ---------------------------------------------------------------------------

def _abort(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Mode extraction from current-objective.md
# ---------------------------------------------------------------------------

SYSTEM_BUILDING_KEYWORDS = ["guardian", "enforcement", "system", "control"]


def extract_mode(objective_path):
    """
    Derive mode from first Immediate Next Step.
    Returns "system-building" or "migration-execution".
    """
    sections = parse_sections(objective_path)
    if "Immediate Next Steps" not in sections:
        return None
    body = _strip_body(sections["Immediate Next Steps"])
    items = _extract_list_items(body)
    if not items:
        return None

    first_lower = items[0].lower()
    first_words = set(first_lower.split())

    for keyword in SYSTEM_BUILDING_KEYWORDS:
        kw_words = keyword.split()
        if len(kw_words) == 1:
            matched = kw_words[0] in first_words
        else:
            matched = keyword in first_lower
        if matched:
            return "system-building"

    return "migration-execution"


# ---------------------------------------------------------------------------
# Objective step extraction
# ---------------------------------------------------------------------------

def extract_objective_step_raw(objective_path):
    sections = parse_sections(objective_path)
    if "Immediate Next Steps" not in sections:
        return None
    body = _strip_body(sections["Immediate Next Steps"])
    items = _extract_list_items(body)
    return items[0] if items else None


# ---------------------------------------------------------------------------
# ECS resolver
# ---------------------------------------------------------------------------

def run_resolver():
    """Call resolve_next_action.py. Returns (decision, placement) or (None, None)."""
    try:
        result = subprocess.run(
            [sys.executable, RESOLVER_TOOL],
            capture_output=True,
            text=True,
        )
    except OSError as e:
        _abort(f"RESOLVER_LAUNCH_FAILED: {e}")

    if result.returncode != 0:
        _abort(f"RESOLVER_FAILED: exit {result.returncode}: {result.stderr.strip()[:200]}")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        _abort("RESOLVER_INVALID_JSON")

    decision  = data.get("decision")
    placement = data.get("placement")
    return decision, placement


# ---------------------------------------------------------------------------
# Guardian
# ---------------------------------------------------------------------------

def run_guardian():
    """Call run_guardian.py. Returns (status_str, blockers_list)."""
    try:
        result = subprocess.run(
            [sys.executable, GUARDIAN_TOOL],
            capture_output=True,
            text=True,
        )
    except OSError as e:
        _abort(f"GUARDIAN_LAUNCH_FAILED: {e}")

    if result.returncode != 0:
        _abort(f"GUARDIAN_FAILED: exit {result.returncode}: {result.stderr.strip()[:200]}")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        _abort("GUARDIAN_INVALID_JSON")

    status = data.get("status", "FAIL")

    blockers = []
    for check in data.get("checks", []):
        if check.get("status") == "FAIL":
            blockers.append(check.get("name", "unknown_check"))

    return status, blockers


# ---------------------------------------------------------------------------
# Execution cycle records from system-state
# ---------------------------------------------------------------------------

BLOCK_START = "<!-- EXECUTION_CYCLE_STATUS_START -->"
BLOCK_END   = "<!-- EXECUTION_CYCLE_STATUS_END -->"


def extract_execution_block(system_state_path):
    """
    Parse the EXECUTION_CYCLE_STATUS block from current-system-state.md.
    Returns dict with keys: queue_state, queue_run_record, outcome_record.
    All values are raw strings or None.
    """
    try:
        with open(system_state_path, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        _abort(f"MISSING_FILE: {system_state_path}")
    except OSError as e:
        _abort(f"MISSING_FILE: {system_state_path} ({e})")

    start = content.find(BLOCK_START)
    end   = content.find(BLOCK_END)

    if start == -1 or end == -1 or end <= start:
        return {"queue_state": None, "queue_run_record": None, "outcome_record": None}

    block = content[start + len(BLOCK_START):end]

    def _field(key):
        pattern = rf"^- {re.escape(key)}:\s*(.+)$"
        m = re.search(pattern, block, re.MULTILINE)
        if not m:
            return None
        val = m.group(1).strip()
        return val if val else None

    return {
        "queue_state":    _field("queue_state"),
        "queue_run_record": _field("queue_run_record"),
        "outcome_record": None,  # not written in block directly; resolved separately
    }


# ---------------------------------------------------------------------------
# Active record resolution
# ---------------------------------------------------------------------------

def _latest_file(directory, suffix):
    """Return path of the lexicographically latest file matching suffix, or None."""
    if not os.path.isdir(directory):
        return None
    matches = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(suffix)
    ]
    if not matches:
        return None
    return max(matches)


def resolve_active_records(block, queue_state_path):
    """
    Resolve active_queue_run and active_outcome_record.

    Primary: paths from execution block / queue-state job fields.
    Fallback: latest file by timestamp from respective directories.
    Same cycle only — verify source_queue_state_path matches.
    """
    # Queue run
    active_queue_run = block.get("queue_run_record")
    if active_queue_run and not os.path.isfile(active_queue_run):
        active_queue_run = None

    if not active_queue_run and queue_state_path:
        # Try to find the queue-run that references this queue-state
        active_queue_run = _find_queue_run_for_state(queue_state_path)

    if not active_queue_run:
        active_queue_run = _latest_file(QUEUE_RUNS_DIR, "_queue-run.json")

    # Outcome record — find one that references the active queue-state
    active_outcome_record = None
    if queue_state_path:
        active_outcome_record = _find_outcome_for_state(queue_state_path)

    if not active_outcome_record:
        active_outcome_record = _latest_file(OUTCOME_RECORDS_DIR, "_outcome.json")

    return active_queue_run, active_outcome_record


def _find_queue_run_for_state(queue_state_path):
    """Scan queue-runs/ for a record whose source_queue_state_path matches."""
    if not os.path.isdir(QUEUE_RUNS_DIR):
        return None
    qs_real = os.path.realpath(queue_state_path)
    candidates = sorted(
        [f for f in os.listdir(QUEUE_RUNS_DIR) if f.endswith("_queue-run.json")],
        reverse=True,
    )
    for fname in candidates:
        fpath = os.path.join(QUEUE_RUNS_DIR, fname)
        try:
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        src = data.get("source_queue_state_path")
        if src and os.path.realpath(src) == qs_real:
            return fpath
    return None


def _find_outcome_for_state(queue_state_path):
    """Scan outcome-records/ for a record whose queue_state_path matches."""
    if not os.path.isdir(OUTCOME_RECORDS_DIR):
        return None
    qs_real = os.path.realpath(queue_state_path)
    candidates = sorted(
        [f for f in os.listdir(OUTCOME_RECORDS_DIR) if f.endswith("_outcome.json")],
        reverse=True,
    )
    for fname in candidates:
        fpath = os.path.join(OUTCOME_RECORDS_DIR, fname)
        try:
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        src = data.get("queue_state_path")
        if src and os.path.realpath(src) == qs_real:
            return fpath
    return None


# ---------------------------------------------------------------------------
# Active transition record
# ---------------------------------------------------------------------------

def resolve_active_transition_record():
    """Return latest transition record path, or None."""
    return _latest_file(TRANSITION_RECORDS_DIR, "_transition.json")


# ---------------------------------------------------------------------------
# execution_phase derivation
# ---------------------------------------------------------------------------

def derive_execution_phase(active_queue_state, active_queue_run, active_outcome_record):
    """
    Priority order (spec):
    1. active_outcome_record exists          → "recorded"
    2. active_queue_run.status in completed  → "executed"
    3. active_queue_run exists               → "executing"
    4. active_queue_state exists             → "ready"
    5. else                                  → "idle"
    """
    TERMINAL_QUEUE_RUN_STATUSES = {"success", "failed"}

    if active_outcome_record and os.path.isfile(active_outcome_record):
        return "recorded"

    if active_queue_run and os.path.isfile(active_queue_run):
        try:
            with open(active_queue_run, encoding="utf-8") as f:
                qr_data = json.load(f)
            run_status = qr_data.get("status", "")
            if run_status in TERMINAL_QUEUE_RUN_STATUSES:
                return "executed"
        except (OSError, json.JSONDecodeError):
            pass
        return "executing"

    if active_queue_state and os.path.isfile(active_queue_state):
        return "ready"

    return "idle"


# ---------------------------------------------------------------------------
# next_action_type + next_command derivation
# ---------------------------------------------------------------------------

def derive_outcome_label(active_queue_run):
    """Best-guess outcome label from queue-run record for record_outcome command."""
    if not active_queue_run or not os.path.isfile(active_queue_run):
        return "<outcome>"
    try:
        with open(active_queue_run, encoding="utf-8") as f:
            data = json.load(f)
        status = data.get("status", "")
        if status == "success":
            return "succeeded"
        if status == "failed":
            return "failed"
    except (OSError, json.JSONDecodeError):
        pass
    return "<outcome>"


def derive_next_action(guardian_status, execution_phase, active_queue_state, active_queue_run):
    if guardian_status == "FAIL":
        return "none", None

    if execution_phase == "ready":
        cmd = f"./ai-factory-run --mode execute-allowed-step --queue-state {active_queue_state}"
        return "execute", cmd

    if execution_phase == "executed":
        outcome_label = derive_outcome_label(active_queue_run)
        cmd = (
            f"./ai-factory-record-outcome"
            f" --queue-state {active_queue_state}"
            f" --outcome {outcome_label}"
        )
        return "record_outcome", cmd

    if execution_phase == "recorded":
        return "transition", None

    return "none", None


# ---------------------------------------------------------------------------
# blocked_commands derivation
# ---------------------------------------------------------------------------

def derive_blocked_commands(guardian_status):
    if guardian_status == "FAIL":
        return ["execute", "transition", "record_outcome"]
    return []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # --- Required file existence checks ---
    for path in [OBJECTIVE_FILE, SYSTEM_STATE_FILE]:
        if not os.path.isfile(path):
            _abort(f"MISSING_REQUIRED_FILE: {path}")

    # --- Mode ---
    mode = extract_mode(OBJECTIVE_FILE)

    # --- Objective step ---
    objective_step_raw = extract_objective_step_raw(OBJECTIVE_FILE)

    # --- ECS resolver ---
    ecs_decision_resolved, ecs_placement = run_resolver()

    # --- Guardian ---
    guardian_status, guardian_blockers = run_guardian()

    # --- Active records from state file ---
    block = extract_execution_block(SYSTEM_STATE_FILE)
    active_queue_state = block.get("queue_state")

    # Validate queue-state path exists; fall back to latest
    if active_queue_state and not os.path.isfile(active_queue_state):
        active_queue_state = None
    if not active_queue_state:
        active_queue_state = _latest_file(BATCH_REPORTS_DIR, "_queue-state.json")

    active_queue_run, active_outcome_record = resolve_active_records(block, active_queue_state)
    active_transition_record = resolve_active_transition_record()

    # --- execution_phase ---
    execution_phase = derive_execution_phase(
        active_queue_state, active_queue_run, active_outcome_record
    )

    # --- next_action_type + next_command ---
    next_action_type, next_command = derive_next_action(
        guardian_status, execution_phase, active_queue_state, active_queue_run
    )

    # --- blocked_commands ---
    blocked_commands = derive_blocked_commands(guardian_status)

    # --- context_bundle_refs ---
    context_bundle_refs = [
        "system-state/current-system-state.md",
        "system-state/current-objective.md",
    ]
    if active_queue_state:
        # Make relative to repo root for portability
        try:
            rel = os.path.relpath(active_queue_state, REPO_ROOT)
        except ValueError:
            rel = active_queue_state
        context_bundle_refs.append(rel)

    # --- Assemble snapshot ---
    snapshot = {
        "mode":                    mode,
        "execution_phase":         execution_phase,
        "objective_step_raw":      objective_step_raw,
        "ecs_decision_resolved":   ecs_decision_resolved,
        "ecs_placement":           ecs_placement,
        "guardian_status":         guardian_status,
        "guardian_blockers":       guardian_blockers,
        "active_queue_state":      active_queue_state,
        "active_queue_run":        active_queue_run,
        "active_outcome_record":   active_outcome_record,
        "active_transition_record": active_transition_record,
        "next_action_type":        next_action_type,
        "next_command":            next_command,
        "blocked_commands":        blocked_commands,
        "context_bundle_refs":     context_bundle_refs,
    }

    print(json.dumps(snapshot, indent=2))


if __name__ == "__main__":
    main()
