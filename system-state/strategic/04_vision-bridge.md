# Vision Bridge — Full System Direction

**Purpose:** This file connects daily operational work to the larger vision. Read during strategic sessions, not daily coding sessions.

---

## The North Star

I am building an **AI-governed venture factory** — a system that:
- Builds apps and automations faster than I could alone
- Accumulates a portfolio of proven, deployable solutions
- Eventually runs autonomously with a master orchestrator agent
- Learns and improves through structured knowledge capture
- Scales from solo operator → agent-assisted → fully autonomous

**End-state:** I describe a need in natural language to an executive assistant agent. It asks clarifying questions, produces specs, invokes specialized agents, builds the thing, deploys it, and schedules it as a cron job if needed. I supervise; I don't micromanage.

Example end-state request: "Hey, I need you to build me an automation system that looks for parts for this vehicle I found on an auction site, uses my notes on what parts I need, compares prices and delivery timelines, gives me a report of where to buy from, and automates the purchasing." The system asks clarifying questions, generates the spec, invokes the appropriate agents, builds the automation, and schedules it.

---

## Capability Level Ladder

| Level | Capability | Status | Target |
|-------|-----------|--------|--------|
| 1 | Human orchestrator + Claude Code executor | **ACTIVE** | Now |
| 2 | Single-purpose autonomous agents (VIS processor, weekly synthesis, deployment) | Starting | Month 2 |
| 3 | Multiple narrow agents, human-coordinated | Not started | Month 3-4 |
| 4 | Orchestration layer routes to specialized agents | Not started | Month 6-9 |
| 5 | Executive assistant — natural language in, working automation out | Not started | Year 2+ |

**Rule: Do not skip levels.** Each level's infrastructure requires real usage data from the previous level to build correctly.

---

## The Five Subsystems (Full Architecture)

Per `master-system-map.md`, the AI Operating System has 5 layers:

### Layer 1: Executive Layer (ECA)
Top-level command, goals, priorities.
- **Status:** Spec only (`executive-command-assistant_(eca)_system.md`)
- **Build when:** Level 3 is real and there are multiple active projects to coordinate

### Layer 2: Coordination Layer (PM Agents)
Per-project management.
- **Status:** Spec only (`ai-project-manager-agent-layer.md`)
- **Build when:** Level 3 is real and at least 3 concurrent ventures exist

### Layer 3: Control Layer (ECS + Guardian)
What executes next, is it allowed.
- **Status:** Real, working, proven on migration workflows
- **Current action:** Keep using for migration. Expand to app-build workflows after resume-saas ships.

### Layer 4: Execution Layer (AI Factory + Workers)
Does the actual work.
- **Status:** Migration workflows work. App-build workflows don't exist yet.
- **Current action:** Build resume-saas manually first. Use that to define what an app-build workflow needs.

### Layer 5: Intelligence Layer (Knowledge OS + Capability Engine)
Learning and compounding.
- **Status:** Architecture exists, content doesn't. Start populating now.
- **Current action:** Write retros after each phase. Build VIS MVP. Stop designing, start using.

---

## Major Features — Timeline and Status

### Near-term (Weeks 1-8) — ACTIVE NOW
- **resume-saas** — First portfolio piece (Weeks 1-4)
- **Video Intelligence System MVP** — Automated source processing (Weeks 2-3)
- **Vault structure** — apps/, clients/, intelligence/, lessons/, shared-intelligence/
- **First retro** — Populate Knowledge OS with real lessons (Week 4)
- **App #2** — Chosen from VIS recommendations (Weeks 5-8)

### Mid-term (Month 2-4)
- **Deployment agent** — Level 2 capability (Month 2)
- **Weekly synthesis agent** — Level 2 capability (Month 2)
- **Testing/QA system** — Adjacent repos, CI/CD pipelines (Month 2-3)
- **App-build workflow in ai-factory** — Operator tool expansion (Month 2-3, after resume-saas teaches the pattern)
- **Apps #3 and #4** — Portfolio growth
- **First client conversations** — Starting Month 3

### Longer-term (Month 4-12)
- **Full operator tool expansion** — Handles all workflow types
- **PM Agent for active ventures** — Level 3 capability
- **Context Engine automation** — Auto-updating state across sessions
- **Multi-agent coordination** — Managed Agents when stable
- **ECA MVP** — Level 4 capability
- **First client deliveries** — Using portfolio patterns as templates

### End-state (Year 2+)
- Full autonomous agent orchestration
- Natural language → shipped automation pipeline
- Self-improving Agent Capability Engine
- Video Intelligence on full autopilot
- Agency running with minimal human intervention

---

## Revenue Path

- **Month 3-6:** First clients via portfolio demos. Pitch: "I build AI-powered web apps that automate X. Here's an example of what I've built."
- **Month 6-12:** Productized services using portfolio apps as templates. Deploy proven patterns quickly for new clients.
- **Year 2+:** Agency operating semi-autonomously. Content-driven inbound leads. Multiple concurrent client projects managed by PM agents with ECA oversight.

---

## Critical Constraints (Non-Negotiable)

- Do not skip capability levels
- Do not build systems without a product to validate them
- Do not expand the operator tool before resume-saas ships
- Do not build ECA / PM agents before Level 3 is real
- Do not confuse "factory polish" for "product progress"
- Every spec without a shipping product attached = deferred work, not completed work
- Do not use the migration pipeline for new app building
- Do not set up multi-agent teams before workflow patterns are proven manually

---

## Full Reference Documents (Read Only When Relevant)

**Architecture:**
- `second-brain/01_ai-operating-system/master-system-map.md` — Full architecture overview
- `second-brain/01_ai-operating-system/execution-optimizer_execution-control-system.md` — ECS details
- `second-brain/01_ai-operating-system/system-guardian_validation-engine.md` — Guardian details
- `second-brain/01_ai-operating-system/context-engine_handoff-system-builder.md` — Context handoffs

**Knowledge & Intelligence:**
- `second-brain/01_ai-operating-system/knowledge-os_architecture-and-expansion-system.md` — Knowledge OS
- `second-brain/01_ai-operating-system/knowledge-os_obsidian-system-builder.md` — Obsidian specifics
- `second-brain/01_ai-operating-system/video-intelligence-system.md` — Full VIS spec (end-state)

**Future Systems (Don't Implement Yet):**
- `second-brain/01_ai-operating-system/executive-command-assistant_(eca)_system.md` — ECA
- `second-brain/01_ai-operating-system/ai-project-manager-agent-layer.md` — PM Agents
- `second-brain/01_ai-operating-system/ai-agent_capability-engine.md` — Agent capability
- `second-brain/01_ai-operating-system/human-ai-skill-development_capability-engine.md` — Human skill dev
- `second-brain/01_ai-operating-system/continuous-testing_qa-automation-system.md` — Testing
- `second-brain/01_ai-operating-system/app-factory-system.md` — App Factory

**Business Context:**
- `second-brain/05_reference/ai-agency.md` — Agency vision
- `second-brain/02_ventures/resume-saas/overview.md` — Resume SaaS overview
- `WORKSPACE_AUDIT.md` — Current workspace state and risks

**Rule:** Do not read all of these every session. Use this file for orientation. Read specific specs only when they're relevant to current work (use `05_active-references.md` to track what's relevant now).

---

## Self-Awareness Checkpoints

Ask these questions weekly during strategic review:

1. Am I polishing the factory instead of shipping the product?
2. Am I building infrastructure for capability levels I haven't reached yet?
3. Am I writing specs for systems I can't validate with real usage?
4. Is my current work producing something a user can touch within 2-4 weeks?
5. Am I accumulating real knowledge (retros, patterns) or just adding more architecture docs?

If answers to 1-3 are "yes" or answers to 4-5 are "no" — course correct immediately.
