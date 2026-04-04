# AI Factory

## Purpose

AI Factory is the execution layer of my workspace.

It holds:

- workflows
- venture execution wrappers
- agent definitions
- runtime state
- logs and temporary execution artifacts

## Role in System

- second-brain = thinking and documentation
- repos = source code
- ai-agency-core = reusable standards, prompts, templates
- ai-factory = execution and orchestration

## Rules

- product source code does not live here
- reusable standards do not originate here
- this layer wraps, runs, and coordinates work
- each venture should have a clear execution folder

---

## Code Migration System

Automates multi-stage code migration across repos using a structured pipeline:
**analyzer → planner → coder → apply → reviewer**

Each stage produces a logged artifact. The only stage that writes to the target repo is **apply**.

### Repo-root entrypoints

```
./run-migration-start    # Create migration artifacts for a new step
./run-migration-execute  # Execute a migration step (auto or manual)
./show-latest-manifest   # Print the newest run manifest for a venture + step
```

All scripts resolve the repo root from their own location and forward all arguments unchanged.

To inspect the latest run manifest:

```bash
./show-latest-manifest resume-saas 14
```

### Basic workflow

1. Run `./run-migration-start` to scaffold all prompt and artifact files for a step.
2. Run `./run-migration-execute --mode auto-openai` to run the full pipeline automatically, or use a `manual-capture` mode to paste stage outputs interactively.
3. Review the logged artifacts under `ventures/<venture>/migration-logs/`.

### Known-good example: run-migration-start

```bash
./run-migration-start \
  --venture resume-saas \
  --step 15 \
  --date 2026-04-04 \
  --source backend/services/rewrite_orchestrator_v3.py \
  --target backend/services/rewrite_orchestrator_v4.py \
  --goal "Port rewrite orchestrator to v4 with same deterministic behavior"
```

- `--source` and `--target` are resolved relative to `~/workspace/repos/<venture>/` if not absolute.
- Creates all prompt and artifact files under `ventures/<venture>/migration-logs/`.

### Known-good example: run-migration-execute

```bash
./run-migration-execute \
  --venture resume-saas \
  --date 2026-04-04 \
  --step 15 \
  --mode auto-openai
```

Supported modes:

| Mode | Description |
|---|---|
| `stub` | Dry run, prints paths only |
| `manual-capture` | Paste analyzer and planner output interactively |
| `manual-capture-coder-reviewer` | Paste coder and reviewer output interactively |
| `manual-capture-coder-apply-reviewer` | Paste coder output, auto-apply, paste reviewer |
| `auto-stub` | Runs analyzer and planner with stub model |
| `auto-openai` | Full pipeline via OpenAI API |

`auto-openai` requires `OPENAI_API_KEY`. Override the model with `CODE_MIGRATION_MODEL` (default: `gpt-4.1-mini`).

### Artifact locations

All artifacts are written to:

```
ventures/<venture>/migration-logs/<date>_step-<NN>_<artifact>.md
```

Examples:
```
ventures/resume-saas/migration-logs/2026-04-04_step-15_analyzer-prompt.md
ventures/resume-saas/migration-logs/2026-04-04_step-15_planner-output.md
ventures/resume-saas/migration-logs/2026-04-04_step-15_coder-output.md
ventures/resume-saas/migration-logs/2026-04-04_step-15_reviewer.md
```

The target file written during apply is resolved from the planner output:
- Absolute paths are used as-is.
- Relative paths are resolved against `~/workspace/repos/<venture>/`.

### Safety rules

- **apply is the only stage that writes to the target repo.** All other stages write only to migration-logs.
- **Reviewer output is validated** before it is saved. The reviewer artifact is not written if validation fails.
- **Coder output is validated** (syntax, required imports, required function signatures) before apply runs.
- **Planner output is validated** for structure and drift terms before coder runs.
- Use `--force` to overwrite existing artifacts intentionally. Without it, the scripts refuse to overwrite non-empty files.
- Planner, coder, and reviewer outputs are each validated before the next stage runs. The pipeline stops and exits non-zero on any validation failure.
