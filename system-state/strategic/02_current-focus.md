# Current Focus

**Last Updated:** 2026-04-20
**Current Week:** Week 1 of resume-saas MVP build

## This Week's Objective

Scaffold resume-saas frontend with Claude Code in VS Code. Create CLAUDE.md conventions, frontend spec, and working Next.js scaffold that can call the existing Flask backend.

## In Progress

- [ ] Set up strategic context files in `ai-factory/system-state/strategic/`
- [ ] Upload strategic context files to Claude Project as knowledge
- [ ] Create `resume-saas/frontend/` directory with Next.js 14 (App Router, TypeScript, Tailwind)
- [ ] Create `resume-saas/CLAUDE.md` with repo conventions
- [ ] Create `resume-saas/docs/frontend-mvp-spec-v1.md` (3-screen spec)
- [ ] Install dependencies (Next.js, Tailwind, TypeScript)
- [ ] Verify frontend can call existing backend `/api/rewrite` endpoint
- [ ] Create `resume-saas/docker-compose.yml` for local dev

## Completed This Week
(Starting fresh — no completions yet)

## Blocked / Waiting On
(Nothing blocking)

## Next Up (After Current Tasks)

### Week 2
- Build Screen 1: Input form component (`ResumeForm.tsx`)
- Build Screen 2: Processing state component
- Build Screen 3: Result display + download button (`ResumePreview.tsx`, `DownloadButton.tsx`)
- Wire form → API → response flow
- **Parallel (evenings):** Build VIS MVP (`ai-factory/tools/vis/process_source.py`)

### Week 3
- Frontend ↔ backend integration tests
- End-to-end flow tests (input → API → resume generation → download)
- Error handling and user feedback
- **Parallel:** Build `weekly_synthesis.py` for VIS
- Start daily VIS processing (2-3 sources/day)

### Week 4
- Deploy frontend to Vercel
- Deploy backend to Railway
- Configure CORS, environment variables
- Basic production smoke tests
- Use resume-saas for 5 real job applications
- Write first retro in `second-brain/07_lessons/`

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

## Key Reminders

- When in doubt between "polish the factory" and "ship the product" — ship
- Do not route frontend work through the migration pipeline
- Use Claude Code in VS Code for 80%+ of implementation
- Update `02_current-focus.md` and `03_session-log.md` at end of each work session
