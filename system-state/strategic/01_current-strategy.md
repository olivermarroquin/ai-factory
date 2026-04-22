# Current Strategy

**Last Updated:** 2026-04-22

## Active Strategy: Portfolio-First Build Approach

Build a portfolio of proven apps and automations, then offer clients fast deployment of things I've already built. Higher margin than bespoke consulting. Each app teaches patterns for the next.

## Build Sequence

1. **resume-saas MVP** (Weeks 1-4) — First portfolio piece. Stages 1–3.5 shipped 2026-04-21. MVP end-to-end plumbing verified. Stage 4 (review screen + export) is next; then deploy. Ahead of original week-by-week plan.
2. **Video Intelligence System automated tool** (Weeks 2-3, parallel) — Intelligence intake for future app ideas
3. **App #2** (Weeks 5-8) — Chosen from VIS-ranked recommendations
4. **App #3** (Weeks 9-12) — Continued portfolio growth
5. **Client outreach** (Month 3+) — Begin with 3+ portfolio pieces to show

## Why This Strategy
- Cannot sell automation services without proof of work
- Portfolio model has higher margin and lower risk than bespoke consulting
- Each app teaches patterns (CLAUDE.md, stack decisions, deployment) for the next
- VIS surfaces what to build and how to build it best
- resume-saas validates entire pipeline (factory → product → revenue)

## Locked Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend framework | Next.js 16.2+ App Router (React 19.2) | Current stable as of April 2026. create-next-app defaults. Major changes from 14: Turbopack default, async params, new routing/caching APIs. Core App Router patterns still apply. |
| Backend framework | Flask (Python) | Already built for resume-saas |
| Styling | Tailwind CSS v4 | Current stable. Config-in-CSS via @theme blocks (no tailwind.config.ts file). Utility classes unchanged from v3. @import "tailwindcss" replaces @tailwind directives. |
| Frontend deployment | Vercel | Zero-config Next.js deploys |
| Backend deployment | Railway | Simple Flask hosting |
| Auth for resume-saas MVP | None | Adds 2-4 weeks; add later when multi-user matters |
| VIS code location | `ai-factory/tools/vis/` | It's a tool in the factory, not a separate project |
| VIS seed channels | @nicksaraev, @nateherk, @NetworkChuck, @danmartell, @LiamOttley | Starting intelligence sources |
| Frontend state management | React Context + hooks for MVP | Add Zustand/Redux only if complexity demands |
| API call pattern (MVP) | Synchronous POST /api/rewrite, no job polling | LLM returns in 10-30s; within browser/proxy timeout. Async adds infrastructure that's reversible if needed later. |
| PDF/DOCX export (MVP) | Client-side via jspdf and docx libraries | Lighter infrastructure. Server-side is v1.1 fallback if output quality insufficient. |
| Input format (MVP) | Paste-text only for resume and JD | File parsing (PDF, DOCX) and URL scraping are multi-day scope expansions. Backend already accepts strings. v1.1 work. |
| Frontend routing | Single route at /, state-machine phase field drives screen transitions | Persisting in-memory state across route changes adds complexity without user benefit. Bookmarkable URLs are non-goal. |
| Backend URL prefix | All Flask blueprints registered with url_prefix="/api" | Namespaces API routes from future frontend/static/health routes. One-line change. Matches convention in docs. |
| Proposal toggle behavior | Regenerate right pane from scratch on toggle; discard freeform edits with single-level undo | Simplest to implement and reason about. One-level undo covers realistic "oops" case. Multi-level undo is scope creep. |
| Versioning (MVP) | In-memory only; v1 = original, v2+ = user saves; lost on refresh | Lightweight without persistence. Useful for tailor-to-multiple-jobs workflow. |
| Proposal UI pattern | Hybrid: list in right pane as control surface, diff highlights in center pane as display surface | Pure list obscures effect on text. Inline popovers handle ADD_LINE poorly. Inline popovers deferred to v1.1. |
| PDF export library (MVP) | @react-pdf/renderer (client-side) | Prioritizes export quality without forcing a library rewrite when pushing quality later. Declarative model handles pagination/typography/spacing. Bundle cost (~600kb over jspdf) acceptable given priority. pdf-lib rejected (optimized for modifying existing PDFs, not generating). |
| PDF template (MVP) | Minimal — single column, Helvetica, heading + body hierarchy, no structured header block | Frontend holds resume as one string; richer template requires parsing section boundaries, which is data-model scope creep. Minimal renders plain text cleanly. Richer template is v1.1, gated on introducing structured resume data. |
| Product framing (v1 vs v2) | v1 = AI proposal-review tool for resume tailoring. v2 = format-preserving resume editor (DOCX/PDF upload, format-intact export). | End-state vision is format preservation (upload own resume → apply proposals → download with original formatting). MVP cannot deliver this (paste-text discards formatting at input). Path C: ship MVP with honest framing; validate proposal-flow usefulness; invest in format preservation post-launch with real data. |

## Open Decisions (To Resolve As They Come Up)

- CI/CD tool: GitHub Actions vs. Vercel built-in (decide at deploy time)
- Whether to expand operator tool after resume-saas ships (reassess Week 5)
- Second portfolio app: wait for VIS output in Week 4 before deciding
- Client outreach strategy: decide after 3 portfolio pieces exist
- Orchestrator field-name audit: partial — the strict-mode required/nullable issue was resolved in Stage 3.5. A separate question remains: the orchestrator's model prompt uses the words target/action/new_line in plain text while the spec uses section/op. Since OpenAI Structured Outputs enforces the schema regardless of prompt wording, this is cosmetic/clarity debt, not a bug. Revisit post-MVP.
- Stage 4 PDF library choice: jspdf vs pdf-lib vs react-pdf. jspdf was named in the spec and build-log design-decisions as the MVP choice, but a quick comparison of output quality and API ergonomics should happen at Stage 4 start before committing.
- Stage 4 diff visualization approach: text-diff library (e.g., diff-match-patch) for line/word-level diff, vs. per-op highlighting driven by the proposal op types (REPLACE_LINE, ADD_LINE, DELETE_LINE, REPLACE_PHRASE). Per-op is simpler; text-diff is more general. Decide at Stage 4 start.
- backend/app.py location: currently at repos/resume-saas/app.py (repo root). Consider moving under backend/ for structural consistency. Decide during or after backend /api prefix change.
- Workspace-level git tracking: workspace/CLAUDE.md lives outside any git repo. Deferred 2026-04-21. Revisit when working from a second machine, collaborating, or when more workspace-level files need tracking.
- Product copy / landing-page framing: when the MVP ships, the public framing needs to match Path C — "AI proposal generator for resume tailoring" rather than implying format-preserving editing. Decide at deploy time (Week 4). Not a code decision; a positioning decision.

## Capability Level Roadmap

| Level | Capability | Target | Status |
|-------|-----------|--------|--------|
| 1 | Human orchestrator + Claude Code executor | Now | ACTIVE |
| 2 | Single-purpose autonomous agents (VIS processor, weekly synthesis) | Month 2 | Starting Week 5 |
| 3 | Multiple narrow agents, human-coordinated (deployment, testing, VIS) | Month 3-4 | Not started |
| 4 | Orchestration layer routes to specialized agents | Month 6-9 | Not started |
| 5 | Executive assistant agent — natural language in, automation out | Year 2+ | Not started |

## Things I Am Deliberately NOT Building Right Now

- Format-preserving resume export (DOCX/PDF upload → proposal application → format-intact output) — this is the v2 product vision but building it now would defer MVP ship 3-4 weeks before proposal-review-flow usefulness has been validated. Revisit after MVP ships and real usage data exists. Trigger to revisit: (a) consistent user feedback that plain-text export is unusable, OR (b) you've used the MVP for 5+ real job applications and the missing format preservation is the top pain point.
- Pane scroll alignment in review screen (locked scroll between Original and Proposed panes, top-aligned line-by-line for side-by-side comparison) — real UX polish opportunity surfaced during Stage 4a live test, but not a correctness issue. Current implementation uses independent scrolling. Revisit when real usage shows operators or users hitting pane-comparison friction, or when working on review-screen UX polish pass post-MVP.
- Orchestrator prompt improvements for op-type accuracy — Stage 4a live test revealed the model sometimes picks REPLACE_LINE for sub-line edits that should be REPLACE_PHRASE, and sometimes packs multi-line content into a single before[0] string. Frontend has defensive fallback logic (Strategy B from Fix 4 triage, 2026-04-22 build-log). Backend orchestrator prompt fix is the proper long-term solution. Revisit trigger: real usage across 10+ different resumes showing a pattern of which ops the model gets wrong. Fix in one prioritized pass rather than chasing individual cases. Paired with the schema validator strictness item below.
- Schema validator strictness for proposal.before entries — current proposal_validator.py does not reject before[0] values containing embedded newlines for line-oriented ops (REPLACE_LINE, DELETE_LINE). This lets backend-quirky proposals through that the frontend must then defensively handle. Tighten the validator to reject multi-line before[0] for line-oriented ops, forcing the orchestrator to produce cleaner output. Revisit alongside the orchestrator prompt fix above — they're one coherent backend improvement pass.
- ECS/Guardian extension to app-build workflow — premature until resume-saas and app #2 provide real data points on app-build patterns. Current ECS/Guardian focus stays on migration workflow.
- ECA (Executive Command Assistant) — Level 4 work, too early
- PM Agent Layer — Level 4 work, too early
- Agent Capability Engine — needs real agents running first
- Autonomous Debugging System — needs CI/CD first
- Full Context Engine automation — manual handoffs work fine at current scale
- Semantic Retrieval Layer — no knowledge corpus large enough to need it
- Full Video Intelligence pipeline (6-stage) — MVP version is enough
- Operator tool expansion — wait until resume-saas teaches workflow patterns. Confirmed deferred 2026-04-21 during strategic review. Reassess Week 5.
- Multi-agent coordination — not useful until Level 3 is real

## Revenue Path
- **Month 3-6:** First clients via portfolio demos
- **Month 6-12:** Productized services using portfolio apps as templates
- **Year 2+:** Agency operating semi-autonomously, content-driven inbound leads
