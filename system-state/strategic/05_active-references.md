# Active References

**Last Updated:** 2026-04-20
**Current Focus:** Building resume-saas frontend MVP (Week 1-4)

---

## Purpose Of This File

You have 17+ spec documents in the workspace. If Claude reads all of them every session, it wastes context and gets distracted by systems that don't matter for current work. This file is the filter — it says "for this week's work, THESE specific files are what matters."

Update this file whenever current focus shifts to a new phase.

---

## Relevant To Current Work (Read These When Active)

All paths are relative to workspace root.

### For building resume-saas frontend:
- `ai-factory/docs/rewrite-api-spec-v1.md` — API contract for the rewrite endpoint (note: lives in ai-factory/docs/, not resume-saas)
- `repos/resume-saas/docs/overview.md` — Existing overview document
- `repos/resume-saas/docs/mvp-scope.md` — Existing scope document
- `repos/resume-saas/docs/frontend-mvp-spec-v1.md` — Frontend architecture (to be created in Week 1)
- `repos/resume-saas/CLAUDE.md` — Repo conventions for Claude Code (already exists — review/update in Week 1)
- `repos/resume-saas/backend/` — Existing Flask backend to integrate with
- `second-brain/02_ventures/resume-saas/resume-saas-overview.md` — Venture overview

### For building VIS MVP (Week 2-3):
- `ai-factory/tools/vis/README.md` — Tool documentation (to be created)
- Partial reference: `second-brain/01_ai-operating-system/intelligence-layer/knowledge-os/video-intelligence-system.md` — Read Sections 1-3, 6-8, and 19 only (MVP-relevant parts)

### For strategic decisions this week:
- `ai-factory/system-state/strategic/04_vision-bridge.md` — North star check
- `second-brain/01_ai-operating-system/WORKSPACE_AUDIT.md` — Current workspace state reminder

---

## NOT Relevant Right Now (Skip Unless Strategy Shifts)

These are important long-term documents but do NOT affect current work. Reading them now wastes context and creates pressure to build things that aren't the priority:

- `second-brain/01_ai-operating-system/coordination-layer/executive-command-assistant_(eca)_system.md` — Level 4 work, months away
- `second-brain/01_ai-operating-system/coordination-layer/ai-project-manager-agent-layer.md` — Level 4 work
- `second-brain/01_ai-operating-system/intelligence-layer/capability/ai-agent_capability-engine.md` — Needs real agents first
- `second-brain/01_ai-operating-system/intelligence-layer/capability/human-ai-skill-development_capability-engine.md` — Not a build task
- `second-brain/01_ai-operating-system/quality-layer/continuous-testing_qa-automation-system.md` — Post-MVP work
- `second-brain/01_ai-operating-system/control-layer/context-engine_handoff-system-builder.md` — Manual process works fine at current scale
- Full `second-brain/01_ai-operating-system/intelligence-layer/knowledge-os/video-intelligence-system.md` — Using MVP subset only
- `second-brain/01_ai-operating-system/intelligence-layer/knowledge-os/knowledge-os_architecture-and-expansion-system.md` — Start using it, stop designing it
- `second-brain/01_ai-operating-system/execution-layer/app-factory-system.md` — Not actively using for resume-saas

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
