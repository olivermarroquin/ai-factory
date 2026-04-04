from __future__ import annotations

import argparse
import ast
from pathlib import Path
import re
import sys

from model_backend import run_model


AI_FACTORY = Path(__file__).resolve().parent.parent.parent
WORKSPACE = AI_FACTORY.parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Execute analyzer and planner stages for a migration step."
    )
    parser.add_argument("--venture", required=True, help="Venture name, e.g. resume-saas")
    parser.add_argument("--step", required=True, help="Step number, e.g. 10")
    parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD format")
    parser.add_argument("--model", default="stub", help="Execution backend")
    parser.add_argument(
        "--mode",
        choices=["stub", "manual-capture", "manual-capture-coder-reviewer", "manual-capture-coder-apply-reviewer", "auto-stub", "auto-openai"],
        default="stub",
        help="Execution mode",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing analyzer/planner output files",
    )
    return parser


def migration_logs_dir(venture: str) -> Path:
    return AI_FACTORY / "ventures" / venture / "migration-logs"


def step_prefix(run_date: str, step: str) -> str:
    return f"{run_date}_step-{str(step).zfill(2)}"


def required_paths(venture: str, run_date: str, step: str) -> dict[str, Path]:
    logs = migration_logs_dir(venture)
    prefix = step_prefix(run_date, step)
    return {
        "logs_dir": logs,
        "analyzer_prompt": logs / f"{prefix}_analyzer-prompt.md",
        "planner_prompt": logs / f"{prefix}_planner-prompt.md",
        "analyzer_output": logs / f"{prefix}_analyzer-output.md",
        "planner_output": logs / f"{prefix}_planner-output.md",
        "next_action": logs / f"{prefix}_next-action.md",
        "coder_prompt": logs / f"{prefix}_coder-prompt.md",
        "coder_output": logs / f"{prefix}_coder-output.md",
        "reviewer_prompt": logs / f"{prefix}_reviewer-prompt.md",
        "reviewer": logs / f"{prefix}_reviewer.md",
    }


def validate_inputs(paths: dict[str, Path], mode: str) -> None:
    if not paths["logs_dir"].exists():
        raise FileNotFoundError(f"migration log folder not found: {paths['logs_dir']}")

    common_required = {
        "analyzer_prompt": paths["analyzer_prompt"],
        "planner_prompt": paths["planner_prompt"],
        "analyzer_output": paths["analyzer_output"],
    }

    coder_reviewer_required = {
        "planner_output": paths["planner_output"],
        "coder_prompt": paths["coder_prompt"],
        "reviewer_prompt": paths["reviewer_prompt"],
    }

    required = dict(common_required)

    if mode in ("manual-capture-coder-reviewer", "manual-capture-coder-apply-reviewer"):
        required.update(coder_reviewer_required)

    for path in required.values():
        if not path.exists():
            raise FileNotFoundError(f"required file not found: {path}")


def safe_write(path: Path, content: str, force: bool = False) -> None:
    if path.exists() and path.read_text(encoding="utf-8").strip() and not force:
        raise FileExistsError(f"refusing to overwrite non-empty file: {path}")
    path.write_text(content, encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def detect_markdown_artifacts(text: str) -> bool:
    bad_markers = [
        "```",
        "```python",
        "\\_",
    ]
    return any(marker in text for marker in bad_markers)


def coder_output_requires_future_import(planner_text: str, coder_output: str) -> bool:
    low = planner_text.lower()
    if "preserve from __future__ import annotations" in low:
        return "from __future__ import annotations" in coder_output
    return True


def validate_coder_output(planner_text: str, coder_output: str) -> None:
    if not coder_output.strip():
        raise ValueError("coder output is empty")

    prose_markers = [
        "Here is",
        "Explanation",
        "Output:",
        "```",
        "\\_",
    ]
    for marker in prose_markers:
        if marker in coder_output:
            raise ValueError(f"coder output contains disallowed content: {marker!r}")

    try:
        ast.parse(coder_output)
    except SyntaxError as exc:
        raise ValueError(f"coder output is not valid Python: {exc}") from exc

    if not coder_output_requires_future_import(planner_text, coder_output):
        raise ValueError("coder output is missing required future import")

    planner_low = planner_text.lower()
    if "source context required\nyes" in planner_low:
        required_imports = [
            "from __future__ import annotations",
            "from typing import Any, Dict, List",
        ]
        for imp in required_imports:
            if imp not in coder_output:
                raise ValueError(f"coder output missing required import for exact port: {imp!r}")

        required_signatures = [
            "_lines(",
            "render_rewrite_packet_md(",
        ]
        for sig in required_signatures:
            if sig not in coder_output:
                raise ValueError(f"coder output missing required function for exact port: {sig!r}")


def validate_reviewer_output(reviewer_output: str) -> None:
    if not reviewer_output.strip():
        raise ValueError("reviewer output is empty")

    required_markers = ["status:", "correct:", "issues:", "drift_detected:", "next_safe_step:"]
    for marker in required_markers:
        if marker.lower() not in reviewer_output.lower():
            raise ValueError(f"reviewer output missing required field: {marker!r}")


def validate_planner_output(planner_output: str, source_text: str = "") -> tuple[bool, str]:
    if not planner_output.strip():
        return False, "planner output is empty"

    required_sections = [
        "Target File",
        "Target Scope",
        "Goal",
        "Constraints",
        "Do Not Touch",
        "Source Context Required",
        "Implementation Prompt",
    ]

    lines = planner_output.splitlines()
    stripped_lines = [ln.strip() for ln in lines]

    last_index = -1
    for section in required_sections:
        try:
            idx = stripped_lines.index(section, last_index + 1)
            last_index = idx
        except ValueError:
            return False, f"missing required section: {section}"

    bad_prefixes = [
        "target_file:",
        "target scope:",
        "goal:",
        "constraints:",
        "do not touch:",
        "source context required:",
        "implementation prompt:",
    ]
    for ln in stripped_lines:
        ln_low = ln.lower()
        for prefix in bad_prefixes:
            if ln_low.startswith(prefix):
                return False, f"unexpected key-value style line: {ln!r}"

    drift_terms = ["class", "service", "orchestrator", "entry function"]
    source_low = source_text.lower()
    planner_low = planner_output.lower()
    for term in drift_terms:
        if term in planner_low and term not in source_low:
            return False, f"planner output contains drift term not present in source: {term!r}"

    return True, ""


def planner_requires_coder(planner_text: str) -> bool:
    text = planner_text.lower()

    # Explicit no-op cases
    if "no code changes required" in text:
        return False
    if "no changes required" in text:
        return False
    if "verification pass only" in text:
        return False
    if "do not modify" in text and "verify" in text:
        return False

    # Positive detection of real work
    trigger_phrases = [
        "create the file",
        "implement",
        "add",
        "modify",
        "update",
        "port",
        "write",
        "append",
        "insert",
    ]

    for phrase in trigger_phrases:
        if phrase in text:
            return True

    # Default to requiring coder (safer than skipping work)
    return True


def extract_target_file_from_planner(planner_text: str) -> str:
    lines = planner_text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().lower() == "target file" and i + 1 < len(lines):
            value = lines[i + 1].strip()
            if value:
                return value
        if line.strip().startswith("## Target File") and i + 1 < len(lines):
            value = lines[i + 1].strip()
            if value:
                return value
    raise ValueError("could not determine target file from planner output")


def resolve_target_path(target_value: str) -> Path:
    target_value = target_value.strip()
    if target_value.startswith("/"):
        return Path(target_value)
    repos_root = WORKSPACE / "repos"
    return repos_root / target_value


def apply_coder_output_to_target(target_path: Path, coder_output: str, force: bool = False) -> None:
    if not coder_output.strip():
        raise ValueError("coder output is empty")
    if not target_path.parent.exists():
        raise FileNotFoundError(f"target parent folder not found: {target_path.parent}")
    if target_path.exists() and target_path.read_text(encoding="utf-8").strip() and not force:
        raise FileExistsError(f"refusing to overwrite non-empty target file without --force: {target_path}")
    target_path.write_text(coder_output, encoding="utf-8")


def verify_target_matches(target_path: Path, coder_output: str) -> None:
    actual = target_path.read_text(encoding="utf-8")
    if actual != coder_output:
        raise ValueError("post-apply verification failed: target file does not match coder output")
    if not actual.strip():
        raise ValueError("post-apply verification failed: target file is empty")


def capture_multiline_input(end_marker: str = "EOF") -> str:
    print(f"Paste content below. End with a line containing only {end_marker}")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == end_marker:
            break
        lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def apply_and_review(
    planner_output: str,
    coder_output: str,
    paths: dict,
    args: argparse.Namespace,
) -> int:
    # --- Apply ---
    try:
        target_value = extract_target_file_from_planner(planner_output)
        target_path = resolve_target_path(target_value)
        apply_coder_output_to_target(target_path, coder_output, force=args.force)
        verify_target_matches(target_path, coder_output)
    except Exception as exc:
        print(f"error applying coder output: {exc}", file=sys.stderr)
        return 1

    if args.mode == "auto-openai":
        print(f"applied target file -> {target_path}")

    # --- Reviewer ---
    if args.mode == "auto-openai":
        reviewer_prompt = read_text(paths["reviewer_prompt"])

        result = run_model("reviewer", reviewer_prompt, backend_name="openai")

        if result.status != "success":
            print(f"reviewer failed: {result.error_message}", file=sys.stderr)
            return 1

        if not result.raw_text.strip():
            print("reviewer returned empty output", file=sys.stderr)
            return 1

        try:
            validate_reviewer_output(result.raw_text)
        except Exception as exc:
            print(f"[FAIL] Reviewer validation failed: {exc}", file=sys.stderr)
            return 1

        try:
            safe_write(paths["reviewer"], result.raw_text, force=args.force)
        except Exception as exc:
            print(f"error writing reviewer output: {exc}", file=sys.stderr)
            return 1

        print(f"saved reviewer output -> {paths['reviewer']}")

    else:
        reviewer_prompt = read_text(paths["reviewer_prompt"])
        print("\n=== REVIEWER PROMPT ===\n")
        print(reviewer_prompt)
        print("\n=== END REVIEWER PROMPT ===\n")
        print("Run the reviewer in your model, then paste the reviewer output here.")
        reviewer_output = capture_multiline_input()

        try:
            validate_reviewer_output(reviewer_output)
        except Exception as exc:
            print(f"[FAIL] Reviewer validation failed: {exc}", file=sys.stderr)
            return 1

        try:
            safe_write(paths["reviewer"], reviewer_output, force=args.force)
        except Exception as exc:
            print(f"error writing reviewer output: {exc}", file=sys.stderr)
            return 1

        print("")
        print("status: coder output captured, applied, verified, and reviewer output saved")
        print(f"saved coder output -> {paths['coder_output']}")
        print(f"applied target file -> {target_path}")
        print(f"saved reviewer output -> {paths['reviewer']}")

    return 0


def run_stub(paths: dict[str, Path], args: argparse.Namespace) -> int:
    print("migration_execute.py stub")
    print("")
    print(f"venture: {args.venture}")
    print(f"step: {str(args.step).zfill(2)}")
    print(f"date: {args.date}")
    print(f"model: {args.model}")
    print("")
    print("would execute:")
    print(f"1. analyzer prompt -> {paths['analyzer_prompt']}")
    print(f"2. save analyzer output -> {paths['analyzer_output']}")
    print(f"3. planner prompt -> {paths['planner_prompt']}")
    print(f"4. save planner output -> {paths['planner_output']}")
    print("")
    print("status: validation passed, execution not yet implemented")
    return 0


def run_manual_capture(paths: dict[str, Path], args: argparse.Namespace) -> int:
    analyzer_prompt = read_text(paths["analyzer_prompt"])
    print("\n=== ANALYZER PROMPT ===\n")
    print(analyzer_prompt)
    print("\n=== END ANALYZER PROMPT ===\n")
    print("Run the analyzer in your model, then paste the analyzer output here.")
    analyzer_output = capture_multiline_input()

    try:
        safe_write(paths["analyzer_output"], analyzer_output, force=args.force)
    except Exception as exc:
        print(f"error writing analyzer output: {exc}", file=sys.stderr)
        return 1

    planner_prompt = read_text(paths["planner_prompt"])
    print("\n=== PLANNER PROMPT ===\n")
    print(planner_prompt)
    print("\n=== END PLANNER PROMPT ===\n")
    print("Run the planner in your model, then paste the planner output here.")
    planner_output = capture_multiline_input()

    try:
        safe_write(paths["planner_output"], planner_output, force=args.force)
    except Exception as exc:
        print(f"error writing planner output: {exc}", file=sys.stderr)
        return 1

    print("")
    print("status: analyzer and planner outputs captured successfully")
    print(f"saved analyzer output -> {paths['analyzer_output']}")
    print(f"saved planner output -> {paths['planner_output']}")
    return 0


def run_auto_stub(paths: dict[str, Path], args: argparse.Namespace) -> int:
    # --- Analyzer ---
    analyzer_prompt = read_text(paths["analyzer_prompt"])

    result = run_model("analyzer", analyzer_prompt)

    if result.status != "success":
        print(f"analyzer failed: {result.error_message}", file=sys.stderr)
        return 1

    if not result.raw_text.strip():
        print("analyzer returned empty output", file=sys.stderr)
        return 1

    try:
        safe_write(paths["analyzer_output"], result.raw_text, force=args.force)
    except Exception as exc:
        print(f"error writing analyzer output: {exc}", file=sys.stderr)
        return 1

    print(f"saved analyzer output -> {paths['analyzer_output']}")

    # --- Planner ---
    planner_prompt = read_text(paths["planner_prompt"])

    result = run_model("planner", planner_prompt)

    if result.status != "success":
        print(f"planner failed: {result.error_message}", file=sys.stderr)
        return 1

    if not result.raw_text.strip():
        print("planner returned empty output", file=sys.stderr)
        return 1

    try:
        safe_write(paths["planner_output"], result.raw_text, force=args.force)
    except Exception as exc:
        print(f"error writing planner output: {exc}", file=sys.stderr)
        return 1

    print(f"saved planner output -> {paths['planner_output']}")

    print("")
    print("status: auto-stub analyzer and planner completed")
    return 0


def run_auto_openai(paths: dict[str, Path], args: argparse.Namespace) -> int:
    # --- Analyzer ---
    analyzer_prompt = read_text(paths["analyzer_prompt"])

    result = run_model("analyzer", analyzer_prompt, backend_name="openai")

    if result.status != "success":
        print(f"analyzer failed: {result.error_message}", file=sys.stderr)
        return 1

    if not result.raw_text.strip():
        print("analyzer returned empty output", file=sys.stderr)
        return 1

    try:
        safe_write(paths["analyzer_output"], result.raw_text, force=args.force)
    except Exception as exc:
        print(f"error writing analyzer output: {exc}", file=sys.stderr)
        return 1

    print(f"saved analyzer output -> {paths['analyzer_output']}")

    # --- Planner ---
    planner_prompt = read_text(paths["planner_prompt"])

    result = run_model("planner", planner_prompt, backend_name="openai")

    if result.status != "success":
        print(f"planner failed: {result.error_message}", file=sys.stderr)
        return 1

    if not result.raw_text.strip():
        print("planner returned empty output", file=sys.stderr)
        return 1

    try:
        safe_write(paths["planner_output"], result.raw_text, force=args.force)
    except Exception as exc:
        print(f"error writing planner output: {exc}", file=sys.stderr)
        return 1

    print(f"saved planner output -> {paths['planner_output']}")

    planner_valid, planner_reason = validate_planner_output(result.raw_text, source_text=analyzer_prompt)
    if not planner_valid:
        print(f"[FAIL] Planner validation failed: {planner_reason}", file=sys.stderr)
        return 1

    # --- Coder ---
    coder_prompt = read_text(paths["coder_prompt"])

    result = run_model("coder", coder_prompt, backend_name="openai")

    if result.status != "success":
        print(f"coder failed: {result.error_message}", file=sys.stderr)
        return 1

    if not result.raw_text.strip():
        print("coder returned empty output", file=sys.stderr)
        return 1

    try:
        safe_write(paths["coder_output"], result.raw_text, force=args.force)
    except Exception as exc:
        print(f"error writing coder output: {exc}", file=sys.stderr)
        return 1

    print(f"saved coder output -> {paths['coder_output']}")

    try:
        validate_coder_output(read_text(paths["planner_output"]), result.raw_text)
    except Exception as exc:
        print(f"[FAIL] Coder validation failed: {exc}", file=sys.stderr)
        return 1

    # --- Apply + Reviewer ---
    coder_output = result.raw_text
    planner_output = read_text(paths["planner_output"])

    rc = apply_and_review(planner_output, coder_output, paths, args)
    if rc != 0:
        return rc

    print("")
    print("status: auto-openai analyzer, planner, coder, apply, reviewer completed")
    return 0


def run_manual_capture_coder_reviewer(paths: dict[str, Path], args: argparse.Namespace) -> int:
    planner_output = read_text(paths["planner_output"])

    if not planner_requires_coder(planner_output):
        print("")
        print("status: planner indicates no coder action is required")
        print(f"planner output -> {paths['planner_output']}")
        print("coder/reviewer execution skipped")
        return 0

    coder_prompt = read_text(paths["coder_prompt"])
    print("\n=== CODER PROMPT ===\n")
    print(coder_prompt)
    print("\n=== END CODER PROMPT ===\n")
    print("Run the coder in your model, then paste the coder output here.")
    coder_output = capture_multiline_input()

    try:
        safe_write(paths["coder_output"], coder_output, force=args.force)
    except Exception as exc:
        print(f"error writing coder output: {exc}", file=sys.stderr)
        return 1

    reviewer_prompt = read_text(paths["reviewer_prompt"])
    print("\n=== REVIEWER PROMPT ===\n")
    print(reviewer_prompt)
    print("\n=== END REVIEWER PROMPT ===\n")
    print("Run the reviewer in your model, then paste the reviewer output here.")
    reviewer_output = capture_multiline_input()

    try:
        safe_write(paths["reviewer"], reviewer_output, force=args.force)
    except Exception as exc:
        print(f"error writing reviewer output: {exc}", file=sys.stderr)
        return 1

    print("")
    print("status: coder and reviewer outputs captured successfully")
    print(f"saved coder output -> {paths['coder_output']}")
    print(f"saved reviewer output -> {paths['reviewer']}")
    return 0


def run_manual_capture_coder_apply_reviewer(paths: dict[str, Path], args: argparse.Namespace) -> int:
    planner_output = read_text(paths["planner_output"])

    if not planner_requires_coder(planner_output):
        print("")
        print("status: planner indicates no coder action is required")
        print(f"planner output -> {paths['planner_output']}")
        print("coder/apply/reviewer execution skipped")
        return 0

    coder_prompt = read_text(paths["coder_prompt"])
    print("\n=== CODER PROMPT ===\n")
    print(coder_prompt)
    print("\n=== END CODER PROMPT ===\n")
    print("Run the coder in your model, then paste the coder output here.")
    coder_output = capture_multiline_input()

    try:
        safe_write(paths["coder_output"], coder_output, force=args.force)
    except Exception as exc:
        print(f"error writing coder output: {exc}", file=sys.stderr)
        return 1

    try:
        validate_coder_output(planner_output, coder_output)
    except Exception as exc:
        print(f"error validating coder output: {exc}", file=sys.stderr)
        return 1

    return apply_and_review(planner_output, coder_output, paths, args)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    paths = required_paths(args.venture, args.date, args.step)

    try:
        validate_inputs(paths, args.mode)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.mode == "stub":
        return run_stub(paths, args)

    if args.mode == "manual-capture":
        return run_manual_capture(paths, args)

    if args.mode == "manual-capture-coder-reviewer":
        return run_manual_capture_coder_reviewer(paths, args)

    if args.mode == "manual-capture-coder-apply-reviewer":
        return run_manual_capture_coder_apply_reviewer(paths, args)

    if args.mode == "auto-stub":
        return run_auto_stub(paths, args)

    if args.mode == "auto-openai":
        return run_auto_openai(paths, args)

    print(f"error: unsupported mode {args.mode}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())