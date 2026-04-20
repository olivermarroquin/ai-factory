# Current Strategy

**Last Updated:** 2026-04-20

## Active Strategy: Portfolio-First Build Approach

Build a portfolio of proven apps and automations, then offer clients fast deployment of things I've already built. Higher margin than bespoke consulting. Each app teaches patterns for the next.

## Build Sequence

1. **resume-saas MVP** (Weeks 1-4) — First portfolio piece
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
| Frontend framework | Next.js 14+ App Router | Already have experience, dominant React meta-framework, zero-config Vercel deploy |
| Backend framework | Flask (Python) | Already built for resume-saas |
| Styling | Tailwind CSS | Standard, fast, reusable across apps |
| Frontend deployment | Vercel | Zero-config Next.js deploys |
| Backend deployment | Railway | Simple Flask hosting |
| Auth for resume-saas MVP | None | Adds 2-4 weeks; add later when multi-user matters |
| VIS code location | `ai-factory/tools/vis/` | It's a tool in the factory, not a separate project |
| VIS seed channels | @nicksaraev, @nateherk, @NetworkChuck, @danmartell, @LiamOttley | Starting intelligence sources |
| Frontend state management | React Context + hooks for MVP | Add Zustand/Redux only if complexity demands |

## Open Decisions (To Resolve As They Come Up)

- CI/CD tool: GitHub Actions vs. Vercel built-in (decide at deploy time)
- Whether to expand operator tool after resume-saas ships (reassess Week 5)
- Second portfolio app: wait for VIS output in Week 4 before deciding
- Client outreach strategy: decide after 3 portfolio pieces exist

## Capability Level Roadmap

| Level | Capability | Target | Status |
|-------|-----------|--------|--------|
| 1 | Human orchestrator + Claude Code executor | Now | ACTIVE |
| 2 | Single-purpose autonomous agents (VIS processor, weekly synthesis) | Month 2 | Starting Week 5 |
| 3 | Multiple narrow agents, human-coordinated (deployment, testing, VIS) | Month 3-4 | Not started |
| 4 | Orchestration layer routes to specialized agents | Month 6-9 | Not started |
| 5 | Executive assistant agent — natural language in, automation out | Year 2+ | Not started |

## Things I Am Deliberately NOT Building Right Now

- ECA (Executive Command Assistant) — Level 4 work, too early
- PM Agent Layer — Level 4 work, too early
- Agent Capability Engine — needs real agents running first
- Autonomous Debugging System — needs CI/CD first
- Full Context Engine automation — manual handoffs work fine at current scale
- Semantic Retrieval Layer — no knowledge corpus large enough to need it
- Full Video Intelligence pipeline (6-stage) — MVP version is enough
- Operator tool expansion — wait until resume-saas teaches workflow patterns
- Multi-agent coordination — not useful until Level 3 is real

## Revenue Path
- **Month 3-6:** First clients via portfolio demos
- **Month 6-12:** Productized services using portfolio apps as templates
- **Year 2+:** Agency operating semi-autonomously, content-driven inbound leads
