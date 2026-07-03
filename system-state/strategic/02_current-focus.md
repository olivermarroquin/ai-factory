# Current Focus

**Last Updated:** 2026-07-03
**Current Week:** "Automatable by default" sprint + client growth

## This Week's Objective

"Automatable by default" foundation sprint — fix gate friction + integrity (RGH-14/15/17), build productization-readiness system (PR-1), and run parallel tracks: IDX-1 (indexation diagnosis) + GIT-GATE (autonomous commits). Then skill batch → S&H focused page build.

## Completed 2026-06-25

### [IDX-1] Indexation diagnosis + URL-Inspection auth fix + index-status-diagnose skill
- [x] Phase 1: Fixed URL Inspection API auth scope (ADC re-auth with `webmasters` scope — A2's diagnosis was wrong, gcloud supports it). Real HTTP 200 on EV + S&H. CG-001 root cause resolved.
- [x] Phase 2: Per-page index status via URL Inspection on 55 EV + 35 S&H URLs. EV: 11 indexed / 44 not (crawl-budget, zero content rejection). S&H: 14 indexed / 21 not (12 crawled-not-indexed = authority gate).
- [x] Phase 3: Blocker verification on 5 S&H sample pages. No hard blockers (noindex/robots/sitemap/thin-content all clean). Canonical tag inconsistency flagged (CDN hypothesis). API canonical data absent for non-indexed pages (known limitation).
- [x] Phase 4: `index-status-diagnose` skill v1.0 — `gsc_url_inspection.py` engine + SKILL.md. Both clients proven from config. CG-001 resolution recorded for PR-1.

## In Progress (sprint-level)

- [ ] [RGH-14]+[RGH-15]+[RGH-17] gate friction + integrity (Wave A step 1) — in-flight, separate session
- [ ] [MCD-P4] mission-control-dashboard Phase 4 — Waves 4-5 remain (notifications, cost display)
- [ ] [A4→FOCUS] S&H focused page build — unblocked by IDX-1 (authority gate, not content issue); still needs CR-102 independent review of expansion candidates

## Next Up
- [ ] [PR-1] Productization-readiness system (Wave A step 2 — after RGH-14/15/17)
- [ ] [GIT-GATE] Autonomous commit service (parallel track after PR-1)
- [x] [client-schema-sync] skill build — SHIPPED 2026-07-03. Independent review PASS 2 rounds [2,0]. Engine + 3 profiles + SKILL.md v1.0.0.
- [ ] [G12] local-SEO growth orchestrator (Wave C, after client-schema-sync)

## In Progress

### Build
- [ ] Stage 4a Slate migration — replace ProposedPane contentEditable surface with Slate.js editor. Plan doc at `repos/resume-saas/docs/stage-4a-slate-migration-plan.md`. Estimated 2-4 hours. Read plan doc + Slate quickstart BEFORE writing execution prompt. This is the blocker for completing Stage 4a.
- [ ] Create `repos/resume-saas/docker-compose.yml` for local dev (post-Stage-4)

### Vault Orchestrator
- [x] [PROVISION-existing-project] vault-orchestrator v1.6 — existing-project decomposition (close Gap 1). SHIPPED 2026-06-19. `--existing-project <slug>` on Mode 3 PROVISION. Independent peer-review PASS (3 rounds). Unblocks Phase 5.

### Market Intelligence
- [x] [MI-8] Federal IT services niche — DONE (peer review PASS 2026-06-16). Skill v1.0→v1.1 (B2G arena variant). Output A + B produced. Reuse map + playbook pattern captured.
- [x] [MI-8] Remaining govcon niches — DONE (2026-06-17). All 4 niches (facilities/construction, staffing, management-consulting, GSA-furniture) completed from v1.1 config alone. Zero hardcoded leaks, zero skill changes. 12 analysis files + 29 raw JSON. OQL PASS-WITH-FINDINGS (4 advisories, 0 blocking). **Pending independent review.**
- [ ] [MI-8] Chrome-dependent collection for all niches (SAM.gov, GSA eLibrary, SBA DSBS) — deferred, not blocking close
- [x] [MI-8] Furniture Config B — SUPERSEDED by GSA-furniture govcon niche run (ran as B2G variant, not local-services). The duplicability proof is stronger: 5 govcon niches > original 1 govcon + 1 local-services plan.
- [ ] [MI-8] Cadence durable scheduling (monthly tool scan + quarterly re-score) — referenced in spec §6, not yet persisted as durable scheduled tasks
- [ ] [MI-8] Independent review of Chat 2 deliverables — operator to dispatch reviewer

### Setup
All items completed. Strategic context system, workspace/CLAUDE.md, repos/resume-saas/CLAUDE.md all updated and operational.

### Knowledge Capture (Ongoing)
Build-log entries captured throughout Stage 4a session 2026-04-22 including design decisions (11 rows), meta-lessons (2 entries — intake-gap + contentEditable-dead-end).

## Completed 2026-04-22 (Stage 4a full-day session)

### Stage 4a implementation
- [x] Stage 4a Section 1-6: OriginalPane, ProposedPane v1, ProposalCard, ProposalsList, ReviewScreen, AppShell review case wired
- [x] Fix 1a (data layer): multi-level undo stack, TOGGLE_ALL action, RESTORE_ORIGINAL clears selections + stack
- [x] Fix 1b (ProposedPane contentEditable rewrite) — multiple iterations, ultimately insufficient
- [x] Fix 2: applyProposals defensive normalization (synonym-aware section detection, bullet/whitespace normalization)
- [x] Fix 4: applyProposals multi-line before[0] handling + REPLACE_LINE auto-convert to phrase for sub-line edits (≥30% ratio threshold)
- [x] Fix 5.2: layout regression fix (body overflow-hidden, ReviewScreen h-full, grid-rows-1, min-h-0 on cells) — panes now scroll internally
- [x] Option A focus fix: remove hadFocus guard, always reset scroll/cursor/focus on toggle
- [x] Fix 6 Option C: contenteditable="plaintext-only" attempt (partial fix, insufficient)
- [x] Fix 6.1: line-div cursor walker (resolved Enter positioning, but backspace still broken)

### Strategic artifacts
- [x] build-log.md: 11 new design-decisions table rows covering Stage 4a decisions
- [x] build-log.md: Meta-lessons section established, 2 entries (intake-gap mid-build, contentEditable-dead-end)
- [x] frontend-mvp-spec-v1.md: revised for single-pane design + multi-level undo + Toggle All + known applyProposals limitations
- [x] second-brain/05_reference/venture-intake-checklist.md: 15-question intake checklist seeded from resume-saas lessons
- [x] second-brain/06_retros/2026-04-22_resume-saas-intake-gap-mid-build.md: mid-build retro on end-state vision gap
- [x] 01_current-strategy.md: Locked Decisions (5 new), Open Decisions (2 new), Things Not Building (4 new v1.1 items)
- [x] stage-4a-slate-migration-plan.md: full handoff document for tomorrow's Slate work

### Git hygiene
- [x] 28 commits across resume-saas repo spanning implementation, fixes, docs, and orphan-commit cleanup

## Completed This Week

### Knowledge Capture Session (2026-04-21)
- [x] Added Task Completion Checkpoint Protocol to `workspace/CLAUDE.md`
- [x] Wrote `second-brain/06_retros/2026-04-20_resume-saas-backend-migration-retro.md`
- [x] Wrote `second-brain/06_retros/2026-04-20_ai-factory-control-system-retro.md` (with operator context amendments)
- [x] Wrote `second-brain/03_playbooks/backend-flask-three-layer-structure.md`
- [x] Wrote `second-brain/03_playbooks/migration-pipeline-operator-workflow.md`
- [x] Wrote `second-brain/03_playbooks/legacy-cli-to-saas-backend-conversion.md`
- [x] Initialized `second-brain/` as git repository
- [x] Corrected test count language in `current-system-state.md` and session log

### Week 1 Build Setup (2026-04-21)
- [x] Updated repos/resume-saas/CLAUDE.md (API contract corrected, task order fixed, spec-location pointer fixed)
- [x] Created repos/resume-saas/docs/frontend-mvp-spec-v1.md (authoritative spec for Next.js scaffold)
- [x] Created repos/resume-saas/docs/build-log.md (with design decisions table + Week 1 setup session entry)

### Week 1 Build Stages (2026-04-21)
- [x] Stage 1: Next.js 16.2 scaffold, Tailwind v4, TypeScript strict, clean dev server
- [x] Stage 2: Frontend state management layer — types, actions, reducer, AppContext, applyProposals algorithm
- [x] Stage 2.5: Backend dependency manifest (requirements.txt), fresh .venv, /api url_prefix on all blueprints, 40/40 tests passing in clean venv
- [x] Stage 3: Next.js proxy rewrite, lib/api.ts, InputScreen + ProcessingScreen + ErrorBanner + AppShell, AppProvider wired into root layout, README dev-server commands documented
- [x] Stage 3.5: Fixed OpenAI strict Structured Outputs schema bug (narrative nullable + required). Full end-to-end round trip verified: real resume+JD returned 7 real proposals through the full stack.

## Blocked / Waiting On

Stage 4a completion blocked on Slate migration of ProposedPane. Execution path is clear (plan doc ready), but requires fresh session — not a same-day continuation. Next session should start with reading `repos/resume-saas/docs/stage-4a-slate-migration-plan.md` end-to-end.

Stage 4b (versioning + export) blocked on Stage 4a completion.

## Next Up (After Current Tasks)

### Stage 4a completion (Next session — still Week 1/2)

- [ ] Read `repos/resume-saas/docs/stage-4a-slate-migration-plan.md` end-to-end (~10 min)
- [ ] Read Slate's "Installing Slate" + "The Basics" walkthroughs (~20 min)
- [ ] Validate the proposed implementation approach against Slate's idioms; adjust if needed
- [ ] Install `slate` and `slate-react` dependencies
- [ ] Rewrite `components/ProposedPane.tsx` using Slate
- [ ] Adapt or remove `lib/diffPreview.ts` per migration plan
- [ ] Live end-to-end test: all 15 original Stage 4a checks PLUS 7 Enter tests PLUS 3 backspace tests (test criteria in plan doc)
- [ ] Update `docs/frontend-mvp-spec-v1.md` to reflect Slate as editor implementation
- [ ] Build-log entry: "Stage 4a Slate migration complete" with notes on Slate idiom adjustments

### Stage 4b (After Stage 4a Slate migration completes)

- [ ] Create components/VersionSidebar.tsx (saved versions UI)
- [ ] Create components/ExportMenu.tsx (PDF/DOCX/Clipboard dropdown)
- [ ] Create lib/exportPdf.ts (@react-pdf/renderer wrapper)
- [ ] Create lib/exportDocx.ts (docx library wrapper)
- [ ] Live end-to-end test: save version, export PDF, export DOCX, clipboard copy

### Week 2
- Integration tests, error handling refinement
- Preparing for deployment
- **Playbook capture:** Write `second-brain/03_playbooks/frontend-nextjs-app-router-scaffold.md` after Stage 4 ships (Stage 4 completes the scaffold-to-working-app arc and gives richer material)
- **Parallel (evenings):** Start VIS MVP (`ai-factory/tools/vis/process_source.py`) — originally Week 2-3, still on track

### Week 3
- Frontend ↔ backend integration tests
- End-to-end flow tests (input → API → resume generation → download → edit → save → re-export)
- Error handling refinement
- **Playbook capture:** Write `second-brain/03_playbooks/backend-flask-blueprint-integration.md` after integration tests land
- **Parallel:** Build `weekly_synthesis.py` for VIS
- Start daily VIS processing (2-3 sources/day)

### Week 4
- Deploy frontend to Vercel
- Deploy backend to Railway
- Configure environment variables
- Basic production smoke tests
- Use resume-saas for 5 real job applications
- **Playbook capture:** Write `second-brain/03_playbooks/deployment-vercel-railway.md` after first successful deploy
- **Retro:** Write `second-brain/06_retros/2026-MM-DD_resume-saas-mvp-retro.md` after MVP is live

## DO NOT Work On Right Now

- Operator tool expansion
- ECA implementation
- PM Agent layer
- Full VIS 6-stage pipeline (MVP is enough)
- Video Intelligence automation beyond Week 3 MVP
- Client outreach
- Second portfolio app (wait for Week 5+)
- Multi-agent coordination setup
- Managed Agents configuration
- OpenClaw setup
- Cowork setup (revisit after MVP ships)

## Key Reminders

- When a cross-cutting design decision is made during a build session, capture it in repos/<venture>/docs/build-log.md under "Design decisions" immediately. These accumulate into playbooks after the venture ships.
- When in doubt between "polish the factory" and "ship the product" — ship
- When in doubt between "capture knowledge" and "skip it" — capture
- Do not route frontend work through the migration pipeline
- Use Claude Code in VS Code for 80%+ of implementation
- Update `02_current-focus.md` and `03_session-log.md` at end of each work session
- Write build log entries as work happens, not after the fact
- The migration API spec lives in `ai-factory/docs/rewrite-api-spec-v1.md`, NOT in resume-saas

## Knowledge Capture Expected This Week

By end of Week 4, the following artifacts should exist in `second-brain/`:

1. `03_playbooks/frontend-nextjs-app-router-scaffold.md`
2. `03_playbooks/backend-flask-blueprint-integration.md`
3. `03_playbooks/deployment-vercel-railway.md`
4. `06_retros/2026-MM-DD_resume-saas-mvp-retro.md`

Plus ongoing entries in `repos/resume-saas/docs/build-log.md`.

Note: At current pace (Stages 1 through 3.5 all completed in one day of Week 1), the scaffold playbook is writable after Stage 4 ships tomorrow. Integration and deployment playbooks still map to their respective weeks. Retro still post-MVP-deployment.

These artifacts are what will eventually become the `app-build` workflow in ai-factory (which already has an empty `ai-factory/workflows/app-build/` directory waiting for content). Capturing them during resume-saas is the foundation for automating app #2 and beyond.
