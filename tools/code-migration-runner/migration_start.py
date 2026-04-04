from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys


WORKSPACE = Path.home() / "workspace"
AI_FACTORY = WORKSPACE / "ai-factory"
AI_AGENCY_CORE = WORKSPACE / "repos" / "ai-agency-core"
MAX_SOURCE_CHARS = 12000


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Start a code migration step by creating artifacts and prompt files."
    )
    parser.add_argument("--venture", required=True, help="Venture name, e.g. resume-saas")
    parser.add_argument("--step", required=True, help="Step number, e.g. 04")
    parser.add_argument("--source", required=True, help="Absolute path to source file")
    parser.add_argument("--target", required=True, help="Absolute path to target file")
    parser.add_argument("--goal", required=True, help="Migration goal")
    parser.add_argument(
        "--date",
        dest="run_date",
        default=str(date.today()),
        help="Date in YYYY-MM-DD format",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    return parser


def validate_inputs(args: argparse.Namespace) -> None:
    source_path = Path(args.source)
    target_path = Path(args.target)

    if not source_path.exists():
        raise FileNotFoundError(f"source file not found: {source_path}")

    if not target_path.parent.exists():
        raise FileNotFoundError(f"target parent folder not found: {target_path.parent}")

    venture_logs = AI_FACTORY / "ventures" / args.venture / "migration-logs"
    if not venture_logs.exists():
        raise FileNotFoundError(f"venture migration log folder not found: {venture_logs}")

    prompt_dir = AI_AGENCY_CORE / "prompts" / "code-migration"
    required_prompt_files = [
        prompt_dir / "analyzer-prompt.md",
        prompt_dir / "planner-prompt.md",
        prompt_dir / "coder-prompt.md",
        prompt_dir / "reviewer-prompt.md",
    ]
    for prompt_file in required_prompt_files:
        if not prompt_file.exists():
            raise FileNotFoundError(f"prompt template not found: {prompt_file}")


def write_file(path: Path, content: str, force: bool = False) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"file already exists: {path}")
    path.write_text(content, encoding="utf-8")


def read_prompt_template(name: str) -> str:
    path = AI_AGENCY_CORE / "prompts" / "code-migration" / name
    return path.read_text(encoding="utf-8")


def read_source_text(path_str: str, max_chars: int = MAX_SOURCE_CHARS) -> str:
    path = Path(path_str)
    text = path.read_text(encoding="utf-8")
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    return truncated + "\n\n# ... TRUNCATED ...\n"

def read_target_text(path_str: str, max_chars: int = MAX_SOURCE_CHARS) -> str:
    path = Path(path_str)
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    return truncated + "\n\n# ... TRUNCATED ...\n"


def try_rel_to_workspace_repos(path_str: str) -> str:
    path = Path(path_str)
    repos_root = WORKSPACE / "repos"
    try:
        return str(path.relative_to(repos_root))
    except ValueError:
        return str(path)


def planner_content(source: str, target: str, goal: str) -> str:
    target_rel = try_rel_to_workspace_repos(target)
    source_rel = try_rel_to_workspace_repos(source)
    return f"""# Planner Output

## Target File
{target_rel}

## Target Scope
-

## Goal
{goal}

## Constraints
- deterministic only
- no CLI behavior
- no filesystem assumptions
- keep scope narrow
- keep it service-oriented

## Do Not Touch
- unrelated files
- architecture outside current scope

## Source Context Required
yes

## Source File
{source_rel}

## Implementation Prompt
-
"""


def reviewer_content(target: str) -> str:
    target_rel = try_rel_to_workspace_repos(target)
    return f"""# Reviewer Output

## Target File
{target_rel}

## Status
- pass
- revise

## What Is Correct
-

## Issues
-

## Drift Detected
- yes / no

## Next Safe Step
-

## Notes
-
"""


def analyzer_output_content() -> str:
    return """# Analyzer Output

## Classification
-

## Role
-

## Preserve
-

## Leave Behind
-

## Recommended Next Scope
-

## Notes
-
"""


def next_action_content(
    analyzer_prompt_path: Path,
    analyzer_output_path: Path,
    planner_prompt_path: Path,
) -> str:
    return f"""# Next Action

## Step 1 — Run Analyzer
Open this file:
{analyzer_prompt_path}

Paste its full contents into Claude Code.

Then append:
Analyze the source file and return the result in the analyzer-output format.

Copy Claude's response into:
{analyzer_output_path}

## Step 2 — Run Planner
Open this file:
{planner_prompt_path}

Paste its full contents into Claude Code.

Then append:
Use the analyzer output file referenced above.

Return only the completed planner output.

## Step 3 — Continue
Use the completed planner output to drive the coder step.
"""


def summary_content(source: str, target: str, goal: str, step: str, run_date: str) -> str:
    return f"""# Step Summary

## Step
step-{step}

## Date
{run_date}

## Source File
{source}

## Target File
{target}

## Goal
{goal}

## What Changed
-

## Result
- accepted
- revised
- blocked

## Blockers
-

## Commit
-

## Next Step
-
"""


def planner_followup_instructions(analyzer_output_path: Path) -> str:
    return f"""## Planner Execution Note

Use the analyzer output stored here:

{analyzer_output_path}

After the analyzer output is filled in, use it to produce a completed planner output.

Return only the completed planner output.
"""


def implementation_brief(source: str, target: str, goal: str) -> str:
    target_name = Path(target).name

    return f"""## Suggested Implementation Brief

Implement the next migration step in:

{target}

Goal:
{goal}

Requirements:
- modify only this target file
- keep scope narrow
- preserve deterministic logic where applicable
- do not introduce CLI behavior
- do not introduce filesystem workflow assumptions
- do not refactor unrelated code
- do not redesign architecture
- stop and explain if another function must change

Output:
- return the full updated target file only

Notes:
- use the source code below as migration context
- align with the current target file state
- prefer a minimal V1 implementation over overengineering

Suggested target file:
{target_name}
"""


def wrap_prompt(
    template: str,
    role: str,
    venture: str,
    step: str,
    source: str,
    target: str,
    goal: str,
    source_text: str | None = None,
    target_text: str | None = None,
    include_impl_brief: bool = False,
    analyzer_output_path: Path | None = None,
) -> str:
    parts = [
        f"# {role} Prompt Packet",
        "",
        "## Venture",
        venture,
        "",
        "## Step",
        step,
        "",
        "## Source File",
        source,
        "",
        "## Target File",
        target,
        "",
        "## Goal",
        goal,
        "",
        "## Instructions",
        "Use the reusable prompt below together with the migration context above.",
        "",
        "## Scope Rules",
        "- modify only the requested target file",
        "- keep scope narrow",
        "- do not refactor unrelated code",
        "- preserve architecture boundaries",
        "",
        "---",
        "",
        template.strip(),
    ]

    if include_impl_brief:
        parts.extend([
            "",
            implementation_brief(source, target, goal).rstrip(),
        ])

    if analyzer_output_path is not None:
        parts.extend([
            "",
            planner_followup_instructions(analyzer_output_path).rstrip(),
        ])

    if target_text is not None:
        parts.extend([
            "",
            "## Current Target File",
            "```python",
            target_text.rstrip(),
            "```",
        ])

    if source_text is not None:
        parts.extend([
            "",
            "## Source Code",
            "```python",
            source_text.rstrip(),
            "```",
        ])

    return "\n".join(parts) + "\n"

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        validate_inputs(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    venture_logs = AI_FACTORY / "ventures" / args.venture / "migration-logs"
    step = str(args.step).zfill(2)
    prefix = f"{args.run_date}_step-{step}"

    files = {
        "planner": venture_logs / f"{prefix}_planner.md",
        "reviewer": venture_logs / f"{prefix}_reviewer.md",
        "summary": venture_logs / f"{prefix}_summary.md",
        "analyzer_prompt": venture_logs / f"{prefix}_analyzer-prompt.md",
        "analyzer_output": venture_logs / f"{prefix}_analyzer-output.md",
        "planner_prompt": venture_logs / f"{prefix}_planner-prompt.md",
        "coder_prompt": venture_logs / f"{prefix}_coder-prompt.md",
        "reviewer_prompt": venture_logs / f"{prefix}_reviewer-prompt.md",
        "next_action": venture_logs / f"{prefix}_next-action.md",
    }

    try:
        analyzer_template = read_prompt_template("analyzer-prompt.md")
        planner_template = read_prompt_template("planner-prompt.md")
        coder_template = read_prompt_template("coder-prompt.md")
        reviewer_template = read_prompt_template("reviewer-prompt.md")
        source_text = read_source_text(args.source)
        target_text = read_target_text(args.target)

        write_file(
            files["analyzer_output"],
            analyzer_output_content(),
            force=args.force,
        )
        write_file(
            files["next_action"],
            next_action_content(
                files["analyzer_prompt"],
                files["analyzer_output"],
                files["planner_prompt"],
            ),
            force=args.force,
        )
        write_file(
            files["planner"],
            planner_content(args.source, args.target, args.goal),
            force=args.force,
        )
        write_file(
            files["reviewer"],
            reviewer_content(args.target),
            force=args.force,
        )
        write_file(
            files["summary"],
            summary_content(args.source, args.target, args.goal, step, args.run_date),
            force=args.force,
        )

        write_file(
            files["analyzer_prompt"],
            wrap_prompt(
                analyzer_template,
                "Analyzer",
                args.venture,
                step,
                args.source,
                args.target,
                args.goal,
                source_text=source_text,
                target_text=target_text,
                include_impl_brief=False,
            ),
            force=args.force,
        )
        write_file(
            files["planner_prompt"],
            wrap_prompt(
                planner_template,
                "Planner",
                args.venture,
                step,
                args.source,
                args.target,
                args.goal,
                source_text=None,
                target_text=target_text,
                include_impl_brief=False,
                analyzer_output_path=files["analyzer_output"],
            ),
            force=args.force,
        )
        write_file(
            files["coder_prompt"],
            wrap_prompt(
                coder_template,
                "Coder",
                args.venture,
                step,
                args.source,
                args.target,
                args.goal,
                source_text=source_text,
                target_text=target_text,
                include_impl_brief=True,
            ),
            force=args.force,
        )
        write_file(
            files["reviewer_prompt"],
            wrap_prompt(
                reviewer_template,
                "Reviewer",
                args.venture,
                step,
                args.source,
                args.target,
                args.goal,
                source_text=None,
                target_text=target_text,
                include_impl_brief=False,
            ),
            force=args.force,
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print("created:")
    for path in files.values():
        print(path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())