#!/usr/bin/env python3
"""
Operator Advisor — v1 (model-backed)

Consumes combined operator JSON and returns Advisor Output Schema JSON
via a real model invocation. Advisory layer only — no execution, no state
mutation, no ECS/Guardian calls.

Usage:
    <operator-json> | python tools/operator/run_advisor.py
    python tools/operator/run_advisor.py --file <path>
"""

import argparse
import json
import os
import shutil
import subprocess
import sys

# ---------------------------------------------------------------------------
# Advisor Output Schema — locked field set
# ---------------------------------------------------------------------------

ADVISOR_OUTPUT_FIELDS = {
    "recommended_next_step",
    "reasoning_summary",
    "risk_flags",
    "missing_inputs_guidance",
    "state_consistency_notes",
    "continue_allowed",
}

MODEL_ID = "claude-sonnet-4-6"

# Claude binary — located relative to CLAUDE_CODE_EXECPATH env var if set,
# otherwise searched on PATH.
def _find_claude_binary():
    execpath = os.environ.get("CLAUDE_CODE_EXECPATH")
    if execpath:
        candidate = os.path.join(os.path.dirname(execpath), "claude")
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    found = shutil.which("claude")
    if found:
        return found
    return None

# ---------------------------------------------------------------------------
# Abort helper
# ---------------------------------------------------------------------------

def _abort(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Output validation
# ---------------------------------------------------------------------------

def _validate_advisor_output(output):
    """
    Validate advisor output against locked schema before printing.
    Aborts on any violation.
    """
    if not isinstance(output, dict):
        _abort("Advisor output is not a JSON object")

    for field in ADVISOR_OUTPUT_FIELDS:
        if field not in output:
            _abort(f"Advisor output missing required field: {field!r}")

    extra = set(output.keys()) - ADVISOR_OUTPUT_FIELDS
    if extra:
        _abort(f"Advisor output contains unexpected fields: {sorted(extra)}")

    if not isinstance(output["recommended_next_step"], str) or not output["recommended_next_step"].strip():
        _abort("Advisor output: 'recommended_next_step' must be a non-empty string")

    if not isinstance(output["reasoning_summary"], str) or not output["reasoning_summary"].strip():
        _abort("Advisor output: 'reasoning_summary' must be a non-empty string")

    if not isinstance(output["risk_flags"], list):
        _abort("Advisor output: 'risk_flags' must be an array")

    if not isinstance(output["continue_allowed"], bool):
        _abort("Advisor output: 'continue_allowed' must be a boolean")

    if output["missing_inputs_guidance"] is not None and not isinstance(output["missing_inputs_guidance"], dict):
        _abort("Advisor output: 'missing_inputs_guidance' must be an object or null")

    state_notes = output["state_consistency_notes"]
    if state_notes is not None and not isinstance(state_notes, (str, list)):
        _abort("Advisor output: 'state_consistency_notes' must be a string, array, or null")


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are an Operator Advisor for ai-factory, a controlled execution and orchestration system.

Your role is strictly advisory. You:
- interpret operator outputs only
- recommend the next human step only
- never execute commands
- never mutate state
- never call ECS or Guardian
- never invent commands not present in the operator inputs
- never assert state not present in the provided inputs

You must return ONLY a JSON object matching this exact schema — no other text:

{
  "recommended_next_step": "<non-empty string>",
  "reasoning_summary": "<non-empty string>",
  "risk_flags": [],
  "missing_inputs_guidance": null,
  "state_consistency_notes": null,
  "continue_allowed": false
}

Schema rules:
- recommended_next_step: required, non-empty string
- reasoning_summary: required, non-empty string
- risk_flags: required, array of strings (may be empty)
- missing_inputs_guidance: object with "fields" array, or null
- state_consistency_notes: string, array of strings, or null
- continue_allowed: required, boolean

If the operator state is blocked or unclear, set continue_allowed = false.
Do not output anything except the JSON object.
"""


def _build_user_prompt(payload):
    """
    Build a grounded advisory prompt from the operator payload.
    Only includes data present in the input — no invented state.
    """
    snapshot              = payload["snapshot"]
    router                = payload["router"]
    instruction           = payload["instruction"]
    required_input_manifest = payload.get("required_input_manifest")
    recent_operator_runs  = payload.get("recent_operator_runs") or []
    validation_summaries  = payload.get("validation_summaries") or []

    lines = [
        "CURRENT OPERATOR STATE",
        "======================",
        "",
        "SNAPSHOT:",
        json.dumps(snapshot, indent=2),
        "",
        "ROUTER OUTPUT:",
        json.dumps(router, indent=2),
        "",
        "INSTRUCTION BLOCK:",
        instruction.get("instruction_block", "(none)"),
        "",
    ]

    if required_input_manifest is not None:
        lines += [
            "REQUIRED INPUT MANIFEST:",
            json.dumps(required_input_manifest, indent=2),
            "",
        ]
    else:
        lines += ["REQUIRED INPUT MANIFEST: null", ""]

    if recent_operator_runs:
        lines += [
            "RECENT OPERATOR RUNS (most recent first):",
            json.dumps(recent_operator_runs[:5], indent=2),
            "",
        ]

    if validation_summaries:
        lines += [
            "VALIDATION SUMMARIES:",
            json.dumps(validation_summaries, indent=2),
            "",
        ]

    lines += [
        "ADVISORY RULES:",
        "- If guardian_status != PASS OR router reason == guardian_block: set continue_allowed=false, add 'guardian_block' to risk_flags",
        "- If router reason == missing_command AND required_input_manifest present: set continue_allowed=true, populate missing_inputs_guidance",
        "- If router.allowed == true: set continue_allowed=true, recommend running the command in the instruction block",
        "- Otherwise: set continue_allowed=false",
        "- missing_inputs_guidance must use this shape when applicable: {\"fields\": [{\"name\": \"<name>\", \"usage_hint\": \"<hint>\"}]}",
        "- state_consistency_notes: populate only from validation_summaries or recent_operator_runs if they indicate drift or inconsistency; otherwise null",
        "- Do not invent any commands, state, or risk flags not grounded in the inputs above",
        "",
        "Return only the JSON object. No explanation, no preamble, no trailing text.",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Model invocation
# ---------------------------------------------------------------------------

def _strip_code_fences(text):
    """Strip markdown code fences from model output if present."""
    text = text.strip()
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    inner = []
    in_block = False
    for line in lines:
        if line.startswith("```") and not in_block:
            in_block = True
            continue
        if line.startswith("```") and in_block:
            break
        inner.append(line)
    return "\n".join(inner).strip()


def _call_model(payload):
    """
    Send the operator payload to the model via the claude CLI binary and return
    the parsed advisor output. Fails closed on any error — no fallback heuristics.

    Uses the claude binary (found via CLAUDE_CODE_EXECPATH) which carries the
    session credentials. This avoids requiring ANTHROPIC_API_KEY in the environment.
    """
    claude_bin = _find_claude_binary()
    if not claude_bin:
        _abort(
            "Cannot locate claude binary. "
            "Ensure CLAUDE_CODE_EXECPATH is set or 'claude' is on PATH."
        )

    # Build full prompt: system context + user payload as a single message
    user_prompt = _build_user_prompt(payload)
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

    try:
        result = subprocess.run(
            [claude_bin, "--model", MODEL_ID, "-p", full_prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        _abort("Model call timed out after 120 seconds")
    except OSError as e:
        _abort(f"Failed to launch claude binary: {e}")

    if result.returncode != 0:
        stderr_snippet = result.stderr.strip()[:400]
        _abort(
            f"claude binary exited {result.returncode}. "
            + (f"stderr: {stderr_snippet}" if stderr_snippet else "")
        )

    raw_text = _strip_code_fences(result.stdout)

    if not raw_text:
        _abort("Model returned empty output")

    try:
        output = json.loads(raw_text)
    except json.JSONDecodeError as e:
        _abort(
            f"Model returned invalid JSON: {e}\n"
            f"Raw output (first 400 chars): {raw_text[:400]}"
        )

    return output


# ---------------------------------------------------------------------------
# Public API — callable directly from run_operator.py
# ---------------------------------------------------------------------------

REQUIRED_INPUT_SECTIONS = ["snapshot", "router", "context", "instruction"]


def _validate_input(payload):
    """Validate required sections are present and are dicts. Aborts on failure."""
    for section in REQUIRED_INPUT_SECTIONS:
        if section not in payload:
            _abort(f"Missing required input section: {section!r}")
        if not isinstance(payload[section], dict):
            _abort(f"Input section {section!r} must be an object")


def run_advisor_core(input_dict):
    """
    Core advisor entry point. Accepts a pre-assembled input dict, calls the
    model, validates output, and returns the Advisor Output Schema dict.

    Aborts (stderr + exit non-zero) on any failure — no partial output.
    This function is the callable API for run_operator.py integration.
    """
    _validate_input(input_dict)
    output = _call_model(input_dict)
    _validate_advisor_output(output)
    return output


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _load_input(raw):
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        _abort(f"Invalid JSON input: {e}")
    _validate_input(payload)
    return payload


def main():
    parser = argparse.ArgumentParser(
        description="Operator Advisor: consume operator outputs and return advisor JSON."
    )
    parser.add_argument(
        "--file",
        default=None,
        metavar="PATH",
        help="Path to combined operator JSON file (default: read from stdin)",
    )
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, encoding="utf-8") as f:
                raw = f.read()
        except FileNotFoundError:
            _abort(f"File not found: {args.file}")
        except OSError as e:
            _abort(f"Cannot read file: {e}")
    else:
        raw = sys.stdin.read()

    payload = _load_input(raw)
    output  = run_advisor_core(payload)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
