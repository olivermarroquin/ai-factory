#!/usr/bin/env python3
"""
Operator Advisor — v1

Consumes combined operator JSON and returns Advisor Output Schema JSON.
Advisory layer only — no execution, no state mutation, no ECS/Guardian calls.

Usage:
    <operator-json> | python tools/operator/run_advisor.py
    python tools/operator/run_advisor.py --file <path>
"""

import argparse
import json
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
# Grounded advisor logic (v1 deterministic stub — model-call shape)
# ---------------------------------------------------------------------------

def _generate_advisor_response(payload):
    """
    v1 grounded advisor. Deterministic — derives output from operator inputs only.
    No external calls. This is the model-call boundary for future replacement.

    Returns validated Advisor Output Schema dict.
    """
    snapshot              = payload["snapshot"]
    router                = payload["router"]
    instruction           = payload["instruction"]
    required_input_manifest = payload.get("required_input_manifest")
    validation_summaries  = payload.get("validation_summaries") or []

    guardian_status   = snapshot.get("guardian_status", "")
    router_allowed    = router.get("allowed", False)
    router_reason     = router.get("reason", "")
    router_action     = router.get("next_action_type", "none")
    next_command      = router.get("next_command")
    execution_phase   = snapshot.get("execution_phase", "")
    mode              = snapshot.get("mode", "")
    instruction_block = instruction.get("instruction_block", "")

    risk_flags              = []
    missing_inputs_guidance = None
    state_consistency_notes = None
    continue_allowed        = False
    recommended_next_step   = ""
    reasoning_summary       = ""

    # --- state_consistency_notes from validation_summaries ---
    consistency_items = []
    for entry in validation_summaries:
        if isinstance(entry, dict):
            note = entry.get("note") or entry.get("message")
            if note and isinstance(note, str):
                consistency_items.append(note)
        elif isinstance(entry, str) and entry.strip():
            consistency_items.append(entry.strip())
    if consistency_items:
        state_consistency_notes = consistency_items

    # --- Case A: Guardian block ---
    if guardian_status != "PASS" or (not router_allowed and router_reason == "guardian_block"):
        risk_flags.append("guardian_block")
        continue_allowed = False
        recommended_next_step = (
            "Do not proceed with execution. "
            "Guardian validation is failing — resolve the failing check(s) before taking any action. "
            "Run './ai-factory-run --mode inspect' to see current Guardian output."
        )
        failing_checks = snapshot.get("guardian_blockers") or []
        if failing_checks:
            check_list = ", ".join(str(c) for c in failing_checks)
            reasoning_summary = (
                f"Guardian status is {guardian_status!r}. "
                f"Failing check(s): {check_list}. "
                "Execution is blocked until Guardian passes. "
                "Align objective, control state, and system state with policy before continuing."
            )
        else:
            reasoning_summary = (
                f"Guardian status is {guardian_status!r}. "
                "Execution is blocked. Investigate Guardian output and align system state before continuing."
            )
        return _build_output(
            recommended_next_step, reasoning_summary, risk_flags,
            missing_inputs_guidance, state_consistency_notes, continue_allowed
        )

    # --- Case B: Missing required input (transition needs target_mode) ---
    if not router_allowed and router_reason == "missing_command" and required_input_manifest:
        continue_allowed = True
        fields_guidance = []
        for inp in required_input_manifest.get("required_inputs", []):
            name = inp.get("name", "")
            allowed_values = inp.get("allowed_values")
            hint = "Provide via operator CLI input."
            if allowed_values:
                hint = f"Allowed values: {', '.join(str(v) for v in allowed_values)}. Provide via --transition-to <mode>."
            fields_guidance.append({"name": name, "usage_hint": hint})

        missing_inputs_guidance = {"fields": fields_guidance} if fields_guidance else None

        action_type = required_input_manifest.get("action_type", router_action)
        recommended_next_step = (
            f"Provide the required input to proceed with '{action_type}'. "
            f"Run './ai-factory-operator --transition-to <mode>' with your chosen mode."
        )
        reasoning_summary = (
            f"The operator has identified a '{action_type}' action is needed "
            f"(execution_phase={execution_phase!r}, mode={mode!r}) "
            "but cannot proceed without human-provided input. "
            "The required input manifest is populated above. No execution has occurred."
        )
        return _build_output(
            recommended_next_step, reasoning_summary, risk_flags,
            missing_inputs_guidance, state_consistency_notes, continue_allowed
        )

    # --- Case C: Allowed action ---
    if router_allowed:
        continue_allowed = True
        recommended_next_step = (
            f"Run the command provided in the instruction block to execute the '{router_action}' action."
        )
        if next_command:
            recommended_next_step = (
                f"Run: {next_command}"
            )
        reasoning_summary = (
            f"Guardian passed. Router approved action '{router_action}' "
            f"for execution_phase={execution_phase!r}, mode={mode!r}. "
            "The instruction block is ready. Proceed when operator is satisfied the state is correct."
        )
        return _build_output(
            recommended_next_step, reasoning_summary, risk_flags,
            missing_inputs_guidance, state_consistency_notes, continue_allowed
        )

    # --- Case D: Blocked none / no_action (non-guardian) ---
    continue_allowed = False
    recommended_next_step = (
        "No executable action is available in the current state. "
        f"Reason: {router_reason!r}. "
        "Review the operator output and system state before proceeding."
    )
    reasoning_summary = (
        f"Router returned next_action_type={router_action!r} with allowed=false "
        f"and reason={router_reason!r}. "
        f"Current execution_phase={execution_phase!r}, mode={mode!r}. "
        "No action can be taken until the blocking condition is resolved."
    )
    return _build_output(
        recommended_next_step, reasoning_summary, risk_flags,
        missing_inputs_guidance, state_consistency_notes, continue_allowed
    )


def _build_output(recommended_next_step, reasoning_summary, risk_flags,
                  missing_inputs_guidance, state_consistency_notes, continue_allowed):
    return {
        "recommended_next_step":  recommended_next_step,
        "reasoning_summary":      reasoning_summary,
        "risk_flags":             risk_flags,
        "missing_inputs_guidance": missing_inputs_guidance,
        "state_consistency_notes": state_consistency_notes,
        "continue_allowed":        continue_allowed,
    }


# ---------------------------------------------------------------------------
# Input loading and validation
# ---------------------------------------------------------------------------

REQUIRED_INPUT_SECTIONS = ["snapshot", "router", "context", "instruction"]


def _load_input(raw):
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        _abort(f"Invalid JSON input: {e}")

    for section in REQUIRED_INPUT_SECTIONS:
        if section not in payload:
            _abort(f"Missing required input section: {section!r}")
        if not isinstance(payload[section], dict):
            _abort(f"Input section {section!r} must be an object")

    return payload


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

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
    output  = _generate_advisor_response(payload)

    _validate_advisor_output(output)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
