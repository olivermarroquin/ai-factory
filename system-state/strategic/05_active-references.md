# Active References

**Last Updated:** 2026-04-20
**Current Focus:** Building resume-saas frontend MVP (Week 1-4)

---

## Purpose Of This File

You have 17+ spec documents in the workspace. If Claude reads all of them every session, it wastes context and gets distracted by systems that don't matter for current work. This file is the filter — it says "for this week's work, THESE specific files are what matters."

Update this file whenever current focus shifts to a new phase.

---

## Relevant To Current Work (Read These When Active)

### For building resume-saas frontend:
- `repos/resume-saas/docs/rewrite-api-spec-v1.md` — API contract for the rewrite endpoint
- `repos/resume-saas/docs/frontend-mvp-spec-v1.md` — Frontend architecture (once created in Week 1)
- `repos/resume-saas/CLAUDE.md` — Repo conventions for Claude Code (once created in Week 1)
- `repos/resume-saas/backend/` — Existing Flask backend to integrate with

### For building VIS MVP (Week 2-3):
- `ai-factory/tools/vis/README.md` — Tool documentation (to be created)
- Partial reference: `second-brain/01_ai-operating-system/video-intelligence-system.md` — Read Sections 1-3, 6-8, and 19 only (MVP-relevant parts)

### For strategic decisions this week:
- `ai-factory/system-state/strategic/04_vision-bridge.md` — North star check
- `WORKSPACE_AUDIT.md` — Current workspace state reminder

---

## NOT Relevant Right Now (Skip Unless Strategy Shifts)

These are important long-term documents but do NOT affect current work. Reading them now wastes context and creates pressure to build things that aren't the priority:

- `executive-command-assistant_(eca)_system.md` — Level 4 work, months away
- `ai-project-manager-agent-layer.md` — Level 4 work
- `ai-agent_capability-engine.md` — Needs real agents first
- `human-ai-skill-development_capability-engine.md` — Not a build task
- `continuous-testing_qa-automation-system.md` — Post-MVP work
- `context-engine_handoff-system-builder.md` — Manual process works fine at current scale
- Full `video-intelligence-system.md` — Using MVP subset only; full spec is end-state
- `knowledge-os_architecture-and-expansion-system.md` — Start using it, stop designing it
- `app-factory-system.md` — Not actively using for resume-saas

---

## When To Update This File

Update `05_active-references.md` when:
- A new phase of work starts (e.g., after resume-saas ships, when starting app #2)
- Focus shifts to a different subsystem (e.g., moving from frontend to VIS build)
- A previously irrelevant spec becomes relevant (e.g., starting to build testing system)

Update takes ~2 minutes. Doing it saves much more time in wasted context.

---

## How Claude Uses This File

At session start, after reading 00-03, Claude reads this file to understand:
- Which detailed specs are worth loading for the current task
- Which specs to explicitly NOT load (to avoid premature optimization)

When user asks about an unrelated system, Claude can answer: "That's in [spec file], but it's not currently active work. Current focus is [X]. Want to add it to the active list, or keep focus where it is?"
