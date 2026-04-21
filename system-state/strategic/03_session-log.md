# Session Log

**Append-only log. Never delete entries. Most recent at the top.**

---

## 2026-04-21 (evening) — End-of-day close-out: Stages 1 through 3.5 shipped, MVP plumbing complete (Claude.ai chat + Claude Code)

**Duration:** Full day — approximately 8+ hours from start of execution chat through final commit.
**Mode:** Execution (primary) + strategic planning (as needed)
**Interface:** Claude.ai strategic chat + Claude Code in VS Code

### What Happened — Strategic Summary

Today was the single most productive session in the project to date. The original Week 1 plan called for scaffolding, spec, and a possibly-working backend connection. Instead we completed the equivalent of Week 1 plus most of Week 2's original scope, and arrived at a functionally end-to-end working MVP (minus the review/export UX, which is Stage 4 tomorrow).

Five build stages shipped:
- Stage 1: Next.js 16.2 scaffold + Tailwind v4 + TypeScript strict
- Stage 2: Full frontend state management layer (types, actions, reducer, context, proposal-application algorithm)
- Stage 2.5: Backend dependency manifest, fresh venv, /api URL prefix, 40/40 tests passing
- Stage 3: Frontend wired end-to-end via Next.js proxy rewrite; Input + Processing screens rendering; error path verified
- Stage 3.5: Fixed OpenAI strict Structured Outputs schema bug (narrative must be nullable + required). Full stack verified with real OpenAI API call returning 7 real proposals.

Three setup/documentation stages also shipped:
- Updated repos/resume-saas/CLAUDE.md with correct API contract and task order
- Wrote repos/resume-saas/docs/frontend-mvp-spec-v1.md (authoritative frontend spec)
- Updated workspace/CLAUDE.md with Session End Protocol trigger phrase and Working with the Strategic Chat section
- Created repos/resume-saas/docs/build-log.md and appended per-stage entries for all five stages

### Decisions Made — Strategic Level

Non-trivial cross-cutting decisions locked during today's work (all captured in 01_current-strategy.md Locked Decisions + build-log design-decisions table):

- Synchronous /api/rewrite call for MVP (async deferred)
- Client-side PDF/DOCX export via jspdf/docx (server-side is v1.1 fallback)
- Paste-text only inputs for MVP (file upload / URL scraping deferred to v1.1)
- Single-route state-machine UI (bookmarkable URLs deferred)
- /api URL prefix on all Flask blueprints
- Proposal toggle regenerates right pane with single-level undo (multi-level undo and inline popovers deferred)
- In-memory versioning kept in MVP (v1 = original, v2+ = saves; lost on refresh)
- Hybrid proposal UI: list as control surface + diff highlights as display surface (inline popovers v1.1)
- Next.js proxy rewrite pattern for local dev (avoids CORS, single-string swap for production)
- Backend dev port 8080 (5000 occupied by macOS AirPlay)
- Accept current stable versions of Next.js (16.2), React (19.2), Tailwind (v4) rather than downgrading to spec-written versions
- Python dependency manifest discipline: compatible-release pins, delete-and-recreate venv verification, single requirements.txt for MVP
- workspace/CLAUDE.md versioning: deferred (file on disk, not in any git repo; revisit when working from a second machine)
- ECS/Guardian app-build workflow extension: still premature until resume-saas and app #2 both ship (confirmed deferral)

### Key Insights

- The strategic chat + Claude Code two-surface model worked. State-delta prompts produced in chat, pasted into Claude Code, applied verbatim with diff review. Zero drift across a long session with many decisions.
- Small backend bugs get caught by live end-to-end testing, not by unit tests. The proposal_schema.py nullable-narrative bug was invisible to 40 unit tests (they mock the orchestrator) and surfaced in the first 30 seconds of real use. The error path surfacing the bug through the frontend's ErrorBanner was itself proof the frontend was correctly built.
- Reconnaissance-before-edits pattern pays off repeatedly. Every stage that started with "show me the current state first" avoided wrong assumptions. Stages that would have used blind edits (had we skipped inspection) would have hit at least two different bugs.
- The "capture design decisions as work happens" discipline in build-log is already paying off. We have 8+ rows in the design-decisions table that will become the raw material for second-brain/03_playbooks/frontend-mvp-design-decisions.md after MVP ships. Writing it retroactively would have lost most of the rationales.
- The factory-polishing-over-shipping failure mode was actively resisted multiple times today: (a) chose not to extend ECS/Guardian for app-build prematurely, (b) chose to defer workspace/CLAUDE.md versioning rather than build a superproject repo, (c) chose not to preemptively add CORS or python-dotenv until the integration actually needs them.
- Breaking stages into explicit plan-and-execute pairs (Part 1 = inspect, Part 2 = apply) caught multiple bugs before they could happen, most notably the openai 2.x version discovery during Stage 2.5 and the second schema-bug fix requirement in Stage 3.5.

### Artifacts Produced (Today, Full List)

Backend:
- repos/resume-saas/requirements.txt (new)
- repos/resume-saas/.gitignore (expanded)
- repos/resume-saas/app.py (modified — /api prefix)
- repos/resume-saas/backend/schemas/proposal_schema.py (modified — nullable narrative)
- repos/resume-saas/.venv/ (recreated clean, not committed, gitignored)

Frontend:
- repos/resume-saas/frontend/ (entire directory scaffolded via create-next-app)
- repos/resume-saas/frontend/lib/types.ts (new)
- repos/resume-saas/frontend/lib/context/actions.ts (new)
- repos/resume-saas/frontend/lib/context/reducer.ts (new)
- repos/resume-saas/frontend/lib/context/AppContext.tsx (new)
- repos/resume-saas/frontend/lib/applyProposals.ts (new)
- repos/resume-saas/frontend/lib/api.ts (new)
- repos/resume-saas/frontend/components/ErrorBanner.tsx (new)
- repos/resume-saas/frontend/components/InputScreen.tsx (new)
- repos/resume-saas/frontend/components/ProcessingScreen.tsx (new)
- repos/resume-saas/frontend/components/AppShell.tsx (new)
- repos/resume-saas/frontend/next.config.ts (modified — proxy rewrite)
- repos/resume-saas/frontend/app/layout.tsx (modified — AppProvider)
- repos/resume-saas/frontend/app/page.tsx (modified — renders AppShell)
- repos/resume-saas/frontend/app/globals.css (modified — Tailwind v4 imports)

Documentation:
- workspace/CLAUDE.md (updated, not committed — no repo)
- repos/resume-saas/CLAUDE.md (updated)
- repos/resume-saas/docs/frontend-mvp-spec-v1.md (new)
- repos/resume-saas/docs/build-log.md (new + per-stage entries)
- repos/resume-saas/README.md (dev-server instructions added)
- ai-factory/system-state/strategic/01_current-strategy.md (multiple updates)
- ai-factory/system-state/strategic/02_current-focus.md (end-of-day close-out updates)
- ai-factory/system-state/strategic/03_session-log.md (this entry + earlier-today entry)

Commits landed today (across three repos):
- resume-saas: 10+ commits covering each stage separately
- ai-factory: multiple commits on strategic files

### Next Session Should Start With

Tomorrow (2026-04-22) session-start protocol runs automatically via workspace/CLAUDE.md. It should read these strategic files and produce a summary that says:

"You're on Stage 4 of resume-saas. Yesterday Stages 1–3.5 shipped — scaffold, state layer, dependency manifest, frontend wiring, and a schema bug fix. The MVP plumbing is end-to-end verified. Today's work is the review screen: three panes, diff visualization, versioning UI, client-side PDF/DOCX export. The full Stage 4 checklist is in 02_current-focus.md under Next Up."

Action after summary: start Stage 4 planning questions. Specifically, before writing Stage 4 code, the strategic chat (me, tomorrow) should walk through:
1. jspdf vs pdf-lib vs react-pdf — which PDF library and why
2. Whether to build all three panes in one stage or split further (Stage 4a/4b)
3. Diff visualization approach — text-diff library vs simple per-op highlighting
4. Export formatting — how literally plain should the exports be

### Open Questions For Next Session

- Stage 4 library choices (see above)
- When does docker-compose.yml make sense — post-Stage-4 as originally planned, or post-deployment?
- Should the rewrite.py surface-the-real-status-code polish happen before or after MVP ships?

---

## 2026-04-21 — Week 1 Execution Session (Claude.ai chat + Claude Code)

**Duration:** ~ongoing
**Mode:** Execution — spec writing, CLAUDE.md corrections, build-log setup
**Interface:** Claude.ai web chat (strategic) + Claude Code in VS Code (execution)

### What Happened
- Read backend code (rewrite_routes.py, rewrite.py, rewrite_orchestrator_v5.py) to derive the actual /rewrite API contract.
- Identified discrepancy between CLAUDE.md and real code: endpoint was at /rewrite, not /api/rewrite; API contract section described the wrong response shape.
- Made 8 cross-cutting design decisions for the frontend MVP (captured in design decisions table of repos/resume-saas/docs/build-log.md).
- Updated repos/resume-saas/CLAUDE.md: fixed API contract section, fixed spec-location pointer, updated Week 1 task order.
- Created repos/resume-saas/docs/frontend-mvp-spec-v1.md as authoritative spec for Next.js scaffold.
- Created repos/resume-saas/docs/build-log.md with design decisions table and first session entry.
- Updated 02_current-focus.md and 01_current-strategy.md to reflect today's decisions and completions.

### Decisions Made
- Synchronous API for MVP (async deferred)
- Client-side PDF/DOCX export for MVP (server-side deferred)
- Paste-text only inputs for MVP (file upload, URL scrape deferred to v1.1)
- Single-route state-machine UI (multi-route deferred)
- /api URL prefix on all Flask blueprints
- Proposal toggle regenerates right pane from scratch with single-level undo
- Versioning kept in MVP, in-memory only
- Hybrid proposal UI: list + diff highlights (inline popovers deferred)
- ECS/Guardian extension to app-build workflow is premature; wait for 2+ data points

### Artifacts Produced
- repos/resume-saas/CLAUDE.md (edited)
- repos/resume-saas/docs/frontend-mvp-spec-v1.md (new)
- repos/resume-saas/docs/build-log.md (new)
- ai-factory/system-state/strategic/02_current-focus.md (edited)
- ai-factory/system-state/strategic/01_current-strategy.md (edited)
- ai-factory/system-state/strategic/03_session-log.md (this entry)

### Key Insights
- The "frontend spec" process surfaced backend debt (orchestrator field-name mismatch with the spec) we wouldn't have caught otherwise. Speccing the frontend forced a close read of the backend contract.
- Strategic state files drift silently during execution sessions. Need forcing function — adopted 1+3 pattern: session-end protocol asks Claude Code to drive state updates; end-of-chat deltas from strategic chat get pasted as one-shot update tasks.
- Capturing design decisions in build-log "as work happens" is lighter weight than waiting for retros and produces better raw material for future playbooks.

### Next Session Should Start With
1. Apply /api URL prefix change in app.py + update affected tests (small backend task)
2. Scaffold repos/resume-saas/frontend/ per docs/frontend-mvp-spec-v1.md (Next.js 14 App Router, TypeScript, Tailwind)
3. Wire frontend to POST /api/rewrite and verify end-to-end

### Open Questions For Next Session
- Does repos/resume-saas/app.py belong at repo root or under backend/? (Structural cleanup, separate from scaffold.)
- Orchestrator field-name mismatch with spec — audit after MVP ships.

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
