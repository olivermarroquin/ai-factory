from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI


@dataclass(frozen=True)
class ModelRunResult:
    raw_text: str
    backend_name: str
    model_name: str
    status: str  # success | empty | backend_error
    error_message: Optional[str] = None
    duration_ms: int = 0


def run_model(stage: str, prompt_text: str, backend_name: str = "stub") -> ModelRunResult:
    """
    Minimal transport seam for model execution (stub only).

    - No API calls
    - No parsing
    - No file writes
    - Deterministic outputs
    """

    if backend_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return ModelRunResult(
                raw_text="",
                backend_name="openai",
                model_name="none",
                status="backend_error",
                error_message="OPENAI_API_KEY not set",
            )

        try:
            client = OpenAI(api_key=api_key)

            model_name = os.getenv("CODE_MIGRATION_MODEL", "gpt-4.1-mini")

            if stage == "planner":
                system_instruction = (
                    "You are a strict code migration planner.\n"
                    "Your job is to plan the NEXT SMALLEST SAFE MIGRATION STEP only.\n"
                    "You MUST preserve the current migration system design.\n"
                    "Do NOT redesign architecture.\n"
                    "Do NOT invent new abstractions.\n"
                    "Do NOT introduce classes, methods, entry points, interfaces, or orchestration unless they are explicitly present in the source code.\n"
                    "If source code is present in the prompt, you must plan only a faithful port of the exact top-level imports, helpers, and functions that appear there.\n"
                    "Use the exact function names from the source when defining scope.\n"
                    "Do NOT generalize source functions into 'service', 'module', 'entry function', or 'class' language.\n"
                    "If the target file is empty, plan only the minimum exact source-backed content needed.\n"
                    "Return output in this exact format:\n\n"
                    "Target File\n"
                    "<value>\n\n"
                    "Target Scope\n"
                    "<value>\n\n"
                    "Goal\n"
                    "<value>\n\n"
                    "Constraints\n"
                    "- <item>\n"
                    "- <item>\n\n"
                    "Do Not Touch\n"
                    "- <item>\n"
                    "- <item>\n\n"
                    "Source Context Required\n"
                    "Yes or No\n\n"
                    "Implementation Prompt\n"
                    "<value>\n\n"
                    "Rules:\n"
                    "- No bullet prefixes like '- target_file:'\n"
                    "- No commentary before or after\n"
                    "- No classes unless explicitly present in the source\n"
                    "- No orchestration logic unless explicitly present in the source\n"
                    "- No future extension language\n"
                    "- No documentation requirements unless present in the source\n"
                    "- If the source contains helper functions, include them explicitly\n"
                    "- If the source contains exactly named functions, the implementation prompt must name those functions exactly\n"
                )
            elif stage == "analyzer":
                system_instruction = (
                    "You are a strict code migration analyzer.\n"
                    "Return output in this exact format:\n\n"
                    "Classification\n"
                    "<value>\n\n"
                    "Role\n"
                    "<value>\n\n"
                    "Preserve\n"
                    "- <item>\n"
                    "- <item>\n\n"
                    "Leave Behind\n"
                    "- <item>\n"
                    "- <item>\n\n"
                    "Recommended Next Scope\n"
                    "<value>\n\n"
                    "Notes\n"
                    "- <item>\n"
                    "- <item>\n"
                )
            elif stage == "coder":
                system_instruction = (
                    "You are a strict code implementer.\n"
                    "You MUST follow the implementation prompt exactly.\n"
                    "You MUST return the FULL target file contents.\n"
                    "The FIRST LINE of the output file MUST be: from __future__ import annotations\n"
                    "Do NOT return explanations.\n"
                    "Do NOT return diffs.\n"
                    "Do NOT return partial code.\n"
                    "Do NOT include markdown fences.\n"
                    "Do NOT include commentary.\n"
                    "The output must be valid Python file content only.\n"
                    "If you are unsure, prefer copying source code exactly.\n"
                )
            else:
                system_instruction = "Return plain text only."

            resp = client.responses.create(
                model=model_name,
                input=[
                    {
                        "role": "system",
                        "content": system_instruction,
                    },
                    {
                        "role": "user",
                        "content": prompt_text,
                    },
                ],
            )

            raw = resp.output_text

            if not raw or not raw.strip():
                return ModelRunResult(
                    raw_text="",
                    backend_name="openai",
                    model_name=model_name,
                    status="empty",
                    error_message="model returned empty output",
                )

            return ModelRunResult(
                raw_text=raw,
                backend_name="openai",
                model_name=model_name,
                status="success",
            )

        except Exception as e:
            return ModelRunResult(
                raw_text="",
                backend_name="openai",
                model_name="unknown",
                status="backend_error",
                error_message=str(e),
            )

    if backend_name != "stub":
        return ModelRunResult(
            raw_text="",
            backend_name=backend_name,
            model_name="none",
            status="backend_error",
            error_message=f"unsupported backend: {backend_name}",
        )

    text = prompt_text.strip()
    if not text:
        return ModelRunResult(
            raw_text="",
            backend_name="stub",
            model_name="stub-model",
            status="empty",
            error_message="prompt text is empty",
        )

    if stage == "analyzer":
        return ModelRunResult(
            raw_text=(
                "# Analyzer Output\n\n"
                "## Classification\n"
                "stub\n\n"
                "## Role\n"
                "stub analyzer result\n\n"
                "## Preserve\n"
                "- stub preserve item\n\n"
                "## Leave Behind\n"
                "- stub leave-behind item\n\n"
                "## Recommended Next Scope\n"
                "stub next scope\n\n"
                "## Notes\n"
                "- generated by auto-stub\n"
            ),
            backend_name="stub",
            model_name="stub-model",
            status="success",
        )

    if stage == "planner":
        return ModelRunResult(
            raw_text=(
                "# Planner Output\n\n"
                "## Target File\n"
                "stub/target.py\n\n"
                "## Target Scope\n"
                "stub planner scope\n\n"
                "## Goal\n"
                "stub planner goal\n\n"
                "## Constraints\n"
                "- generated by auto-stub\n\n"
                "## Do Not Touch\n"
                "- unrelated files\n\n"
                "## Source Context Required\n"
                "no\n\n"
                "## Implementation Prompt\n"
                "stub implementation prompt\n"
            ),
            backend_name="stub",
            model_name="stub-model",
            status="success",
        )

    return ModelRunResult(
        raw_text="",
        backend_name="stub",
        model_name="stub-model",
        status="backend_error",
        error_message=f"unsupported stage: {stage}",
    )