# Current Focus

**Last Updated:** 2026-04-21
**Current Week:** Week 1 of resume-saas MVP build

## This Week's Objective

Scaffold resume-saas frontend with Claude Code in VS Code. Create CLAUDE.md conventions, frontend spec, and working Next.js scaffold that can call the existing Flask backend.

## In Progress

### Build
- [ ] Create `repos/resume-saas/frontend/` directory contents with Next.js 14 (directory exists but empty: app/, components/, lib/)
- [ ] Update repos/resume-saas/app.py to register all three blueprints with url_prefix="/api". Endpoint becomes POST /api/rewrite.
- [ ] Update repos/resume-saas/tests/backend/ tests that hit /rewrite, /resume/parse, /jobs/* at root — move to /api/rewrite, /api/resume/parse, /api/jobs/*.
- [x] Create `repos/resume-saas/docs/frontend-mvp-spec-v1.md` (3-screen spec)
- [x] Create `repos/resume-saas/docs/build-log.md` (starts empty, Claude Code appends as work happens)
- [ ] Install dependencies (Next.js, Tailwind, TypeScript) — package.json doesn't exist yet
- [ ] Verify frontend can call existing backend `/api/rewrite` endpoint
- [ ] Create `repos/resume-saas/docker-compose.yml` for local dev

### Setup
- [x] Set up strategic context files in `ai-factory/system-state/strategic/` (save all 6 files)
- [ ] Save `workspace/CLAUDE.md` at workspace root (delete the misnamed `CLAUDE .md` with a space if it exists)
- [x] Review and update `repos/resume-saas/CLAUDE.md` (already exists — compare with new version and merge)
- [x] Upload strategic context files to Claude Project as knowledge
- [ ] Test session start protocol in new execution chat

### Knowledge Capture (Ongoing Throughout Week)
- [x] Append build log entries after each significant task (see Knowledge Capture Protocol in workspace/CLAUDE.md)

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

## Blocked / Waiting On
(Nothing blocking)

## Next Up (After Current Tasks)

### Week 2
- Build Screen 1: Input form component (`ResumeForm.tsx`)
- Build Screen 2: Processing state component
- Build Screen 3: Result display + download button (`ResumePreview.tsx`, `DownloadButton.tsx`)
- Wire form → API → response flow
- **Playbook capture:** Write `second-brain/03_playbooks/frontend-nextjs-app-router-scaffold.md` after scaffold phase completes
- **Parallel (evenings):** Build VIS MVP (`ai-factory/tools/vis/process_source.py`)

### Week 3
- Frontend ↔ backend integration tests
- End-to-end flow tests (input → API → resume generation → download)
- Error handling and user feedback
- **Playbook capture:** Write `second-brain/03_playbooks/backend-flask-blueprint-integration.md` after integration works
- **Parallel:** Build `weekly_synthesis.py` for VIS
- Start daily VIS processing (2-3 sources/day)

### Week 4
- Deploy frontend to Vercel
- Deploy backend to Railway
- Configure CORS, environment variables
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

These artifacts are what will eventually become the `app-build` workflow in ai-factory (which already has an empty `ai-factory/workflows/app-build/` directory waiting for content). Capturing them during resume-saas is the foundation for automating app #2 and beyond.
