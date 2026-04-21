# Current Focus

**Last Updated:** 2026-04-21
**Current Week:** Week 1 of resume-saas MVP build

## This Week's Objective

Scaffold resume-saas frontend and wire it end-to-end to the Flask backend. All core screens except the review/export UX are complete. Stage 4 (review screen + export) starts tomorrow and completes Week 1's core scope.

## In Progress

### Build
- [ ] Create `repos/resume-saas/docker-compose.yml` for local dev (post-Stage-4)

### Setup
- [x] Set up strategic context files in `ai-factory/system-state/strategic/` (save all 6 files)
- [x] workspace/CLAUDE.md at workspace root — updated with Session End Protocol trigger phrase and "Working with the Strategic Chat" section. The misnamed `CLAUDE .md` with a space was renamed. Note: workspace/CLAUDE.md versioning is deferred — file is on disk but not in any git repo. See 01_current-strategy.md open decisions and build-log Stage 1 deferral entry.
- [x] Review and update `repos/resume-saas/CLAUDE.md` (already exists — compare with new version and merge)
- [x] Upload strategic context files to Claude Project as knowledge
- [x] Test session start protocol in new execution chat

### Knowledge Capture (Ongoing)
Append build log entries after each significant task (see Knowledge Capture Protocol in workspace/CLAUDE.md). All per-stage entries captured for Stages 1–3.5 today.

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

Nothing blocking. Ready to start Stage 4 tomorrow. No blockers.

## Next Up (After Current Tasks)

### Stage 4 (Tomorrow — still Week 1)

Stage 4: Implement real review screen. Completes the originally-planned Week 2 screen work, one week early.

- [ ] Install jspdf and docx libraries
- [ ] Create components/ReviewScreen.tsx (composes sub-panes)
- [ ] Create components/OriginalPane.tsx (read-only left pane)
- [ ] Create components/ProposedPane.tsx (editable center pane with diff highlighting)
- [ ] Create components/ProposalsList.tsx + ProposalCard.tsx (right pane, toggles)
- [ ] Create components/VersionSidebar.tsx (saved versions UI)
- [ ] Create components/ExportMenu.tsx (PDF/DOCX/Clipboard)
- [ ] Create lib/exportPdf.ts and lib/exportDocx.ts wrappers
- [ ] Wire AppShell's "review" case to render ReviewScreen instead of the Stage 3 placeholder
- [ ] Live end-to-end test: submit, toggle proposals, save version, export each format

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
