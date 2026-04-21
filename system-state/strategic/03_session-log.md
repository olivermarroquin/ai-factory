# Session Log

**Append-only log. Never delete entries. Most recent at the top.**

---

## 2026-04-21 — Knowledge capture session (Claude Code in VS Code)

**Duration:** ~2 hours (estimate)
**Mode:** Documentation + state correction
**Interface:** Claude Code in VS Code

### What Happened
- Drafted and committed retrospective state capture (2026-04-19 entry) to 03_session-log.md
- Drafted and committed resume-saas backend migration retro to second-brain
- Drafted, committed, and amended ai-factory control system retro with operator context
- Initialized second-brain/ as git repository with .gitignore for Obsidian files
- Identified and corrected test-count ambiguity in current-system-state.md
- Added Task Completion Checkpoint Protocol to workspace/CLAUDE.md

### Decisions Made
- second-brain/ gets its own git repo, to be backed up to GitHub separately
- State files will use explicit language ('defined'/'passing'/'failing'/'blocked') rather than bare counts
- python-docx dependency blocker is noted as debt, not fixed this session (install when frontend work needs it)
- Task Completion Checkpoint Protocol is mandatory, not optional — enforces knowledge capture between tasks

### Artifacts Produced
- `second-brain/06_retros/2026-04-20_resume-saas-backend-migration-retro.md`
- `second-brain/06_retros/2026-04-20_ai-factory-control-system-retro.md`
- `second-brain/.gitignore`
- `workspace/CLAUDE.md` (updated with Task Completion Checkpoint Protocol)
- `ai-factory/system-state/current-system-state.md` (corrected test count)

### Key Insights
- Retrospective capture reveals hidden state drift: writing the retros exposed that current-system-state.md had language ambiguity
- The inability to remember the specific Guardian expansion bug after two weeks proved the need for build-time capture vs. retroactive retros
- ai-factory control system retro showed 38 docs for 2 formal production uses — the workspace audit's "factory polishing" pattern playing out in data
- Scope evaluation got more honest after operator provided context: Guardian expansion was legitimately reactive, advisor layer had dual motivation (one product-driven, one speculative), workflow stubs were intentional schema reservations
- Knowledge capture infrastructure already existed; what was missing was an enforcement gate between tasks
- Step 14 pipeline failures (6/15 runs) were distributed across multiple stages (coder, planner, apply, reviewer, classification) — model output inconsistency under same input, not a code-under-test issue
- Step 15's 14 successive successful re-runs were deliberate iterative refinement, not error recovery — the pipeline has no mechanism to distinguish these, a real artifact trail gap

### Next Session Should Start With
- Prompts 4-6 from the retrospective knowledge capture plan if knowledge capture isn't finished, OR
- Begin resume-saas frontend scaffold (Week 1 build tasks in 02_current-focus.md) if knowledge capture is complete
- First action: scaffold `repos/resume-saas/frontend/` with Next.js 14 (App Router, TypeScript, Tailwind)

### Open Questions For Next Session
- Should python-docx be installed to unblock the 12 tests? (Likely defer until frontend integration touches resume parsing.)
- Should the workspace root become a git repo so workspace/CLAUDE.md is version-controlled? (Deferred decision — not critical this session.)

---

## 2026-04-19 — Retrospective state capture (Claude Code in VS Code)

**Duration:** N/A (retrospective summary)
**Mode:** Documentation
**Interface:** Claude Code in VS Code

### Purpose
Capture the state of the workspace as of the start of the strategic context
system. Establishes a baseline for future session entries.

### State of ai-factory
- **Latest tag:** v43-current-system-docs
- **Phase:** Controlled Execution — Full Lifecycle Control Implemented
- **Objective mode:** migration-execution (set via ai-factory-transition)
- **Latest execution cycle:** 2026-04-10, outcome: succeeded (proving_pass_cycle_B)
- **What works:** Full control loop enforced — ECS resolution, Guardian (6 checks), operator entrypoint (ai-factory-run), objective transition (ai-factory-transition), post-execution outcome recording (ai-factory-record-outcome), operator advisory layer (ai-factory-operator + ai-factory-advisor)
- **Only executable workflow:** `code_migration` (class A, reason codes A_EXACT_PORT / A_SCHEMA_PORT). `app_build`, `automation_build`, `ui_conversion` defined but NOT executable.
- **Two transition records exist** in transition-records/
- **Context Engine:** NOT IMPLEMENTED — relies on manual operator discipline
- **Knowledge OS:** NOT IMPLEMENTED

### State of resume-saas backend
- **Status:** Phase 1 and Phase 2 complete (tags v40, v42)
- **Tests:** 40 defined; 28 passing, 12 blocked by missing `python-docx` dependency (test_resume_api.py)
- **API blueprints:** rewrite (POST /api/rewrite), resume, jobs — all wired into app.py
- **Services:** jd_parser, resume_parser, proposal_validator, rewrite_formatter, rewrite_orchestrators v1–v5 (v5 is current; v1–v4 preserved as migration history)
- **Schemas:** proposal_schema
- **Empty dirs:** backend/models/, backend/utils/ — not populated
- **Note:** resume-saas backend served as the migration validation harness during ai-factory build, not as a product priority

### State of resume-saas frontend
- Directory `repos/resume-saas/frontend/` exists with subdirectories `app/`, `components/`, `lib/` — all empty
- No package.json, no Next.js scaffold, no components
- Not started

### State of second-brain
- 18 spec/reference files across `01_ai-operating-system/`, `02_ventures/`, and `05_reference/`
- Knowledge OS: structure present, no content captured yet — no patterns, no retros, no playbooks
- Used as reference input during ai-factory build; not yet used as an active learning system

### What's Active / Not Active
- **Active:** ai-factory migration pipeline (code_migration only), resume-saas backend (stable, not being modified)
- **Paused / not started:** resume-saas frontend build, VIS tool build, second-brain knowledge capture workflow, app-factory workflows (app_build, automation_build), operator tool expansion

### Known Issues / Debt
- Guardian stale-state check has incomplete artifact mapping for some current step language
- Operator advisor requires `claude` binary on PATH — not portable without Claude Code session credentials
- `python3` interpreter resolution inconsistency between bash wrappers and shell alias (ai-factory-advisor uses python3.12 explicitly as workaround)
- Mode-derivation keyword matching (whole-word) must stay consistent across snapshot, guardian, and transition — fragile if objective language drifts
- No docker-compose.yml for local dev (frontend + backend together)
- No frontend MVP spec document yet
- No workspace/CLAUDE.md with session protocol yet (a misnamed `CLAUDE .md` with a space exists)
- No build-log.md in resume-saas/docs/ yet
- Missing `python-docx` dependency blocks 12 resume API tests
- `ai-factory/system-state/current-system-state.md` contains the string "40 tests" which was interpreted as "40 passing" when the reality is 40 defined with 12 blocked. This ambiguity suggests the state file needs stricter language conventions — state files should distinguish 'defined', 'passing', 'failing', and 'blocked' explicitly.

---

## 2026-04-20 — Strategic Planning Session (Claude.ai chat)

**Duration:** ~3 hours
**Mode:** Strategy, architecture review, planning
**Interface:** Claude.ai web chat (Opus 4.7)

### What Happened
- Reviewed WORKSPACE_AUDIT.md and all 17 system specs
- Identified the "factory polishing over product shipping" pattern as primary risk
- Decided against using migration pipeline for frontend work (wrong tool)
- Decided against multi-agent build teams for MVP (OpenClaw and Managed Agents premature)
- Locked 5 architecture decisions for resume-saas
- Defined portfolio strategy (build apps → accumulate → offer to clients)
- Defined agent capability ladder (Levels 1-5) with realistic timeline
- Designed strategic context system (6 files, this directory)

### Decisions Made
- Skip custom VIS build for 2 weeks, use NotebookLM + structured prompt template as interim
- Build VIS as 1-2 day tool in Week 2-3 evenings (not a multi-week project)
- Do NOT expand operator tool before resume-saas ships
- Use Claude Code in VS Code as primary development tool (not Managed Agents, not OpenClaw)
- Architecture stack: Next.js 14+ / Flask / Tailwind / Vercel / Railway
- No auth for resume-saas MVP
- VIS lives in `ai-factory/tools/vis/`
- Strategic context lives in `ai-factory/system-state/strategic/`

### Artifacts Produced (In Claude.ai outputs)
- `system-build-strategy-report.md`
- `accelerated-build-plan.md`
- `revised-build-plan-portfolio-strategy.md`
- `strategic-context-system.md`
- `complete-context-system-structure.md`
- This set of 6 strategic context files (00-05)

### Key Insights
- Claude Code already does what a multi-agent dev team would do for MVP work, with human-in-the-loop
- The end-state vision (Level 5 executive assistant) doesn't fully work for anyone yet, even Anthropic
- Portfolio strategy is smarter than bespoke consulting — higher margin, lower risk per project
- Manual VIS using NotebookLM gives 80% of value with 0% of build time for the first 2 weeks

### Next Session Should Start With
1. Read `00_who-i-am.md`
2. Read `01_current-strategy.md`
3. Read `02_current-focus.md`
4. Read latest entry in `03_session-log.md` (this one)
5. Read `05_active-references.md`
6. Then execute what's in "In Progress" in `02_current-focus.md`

### Open Questions For Next Session
- None — strategy is clear, execution starts

---

<!-- NEW ENTRIES APPENDED ABOVE THIS LINE -->
<!-- Template for new entries:

## YYYY-MM-DD — [Session Name] ([Interface])

**Duration:** 
**Mode:** 
**Interface:** 

### What Happened

### Decisions Made

### Artifacts Produced

### Key Insights

### Next Session Should Start With

### Open Questions For Next Session

---
-->
