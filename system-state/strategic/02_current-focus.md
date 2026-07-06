# Current Focus

**Last Updated:** 2026-07-05
**Current Week:** "Automatable by default" sprint + client growth

> **How to use this file (v2, 2026-07-05):** this is a slim, current-only sprint card — objective, sprint items, next up, blocked. Live chat state belongs in `second-brain/_meta/handoffs/_active-chats-tracker.md` (the source of truth for in-flight work); project detail belongs in each repo's `.kos/`. Update this file only when sprint-level state changes (something shipped, a new blocker, a priority shift) — per `second-brain/_meta/session-close-protocol.md`. Do not append per-project or per-chat detail here.

## This Week's Objective

"Automatable by default" foundation sprint + client growth. Gate machinery landed (RGH-14/15/17/18/19, PR-1, GIT-GATE all shipped 07-02) — focus shifts to pending independent reviews, client differentiation follow-ups, and the S&H focused page build.

## In Progress (sprint-level)

- [ ] [MCD-P4] mission-control-dashboard Phase 4 — Waves 4-5 remain (notification multiplexing, cost display)
- [ ] [A4→FOCUS] S&H focused page build — needs CR-102 independent review of expansion candidates (open since 06-24)
- [ ] [RGH-16/RO-FIX] reviewer-orchestrator v3.0 — ready for independent review since 07-03
- [ ] [EV-DIFF] Wave-2/Wave-3 build phase — briefs PASS (pass 360), build next

## Recently Shipped (this sprint)

- [x] [SH-G1] sitewide-similarity-audit tool — SHIPPED + CLOSED 07-05 (pass 364); S&H 29/29 pages mean 73.5%, EV 2nd-instance PASS
- [x] [HERMES-P3-W1] Hooks + Telegram home channel — SHIPPED 07-05, peer-review PASS 0 blocking (AC-1..AC-5)
- [x] [PR-1] Productization-readiness system — SHIPPED + CLOSED 07-02 (pass 345)
- [x] [GIT-GATE] Autonomous commit service — SHIPPED + CLOSED 07-02 (pass 348); review PASS 41/41 + 12 adversarial
- [x] [RGH-14/15/17] + [RGH-18/19] gate friction/integrity + deterministic checks — SHIPPED
- [x] [client-schema-sync] skill v1.0.0 — SHIPPED 07-03 (pass 354); 2nd-client proof PASS
- [x] [IDX-1] Indexation diagnosis + index-status-diagnose skill v1.0 — SHIPPED 06-25
- [x] [EV-DIFF] Wave-1 published 07-01; turnkey T1-T5 complete 07-03; EV-FU1–FU4 done 07-03 (FU5 queued)
- [x] Session End Protocol v2 ARC COMPLETE — canonical close + dispatcher + FU3 independent review PASS + FU2 door-card backfill (14/14, aggregator lit) + workflow conventions (relay/pair-spawn/gate-skip/commit-surface) + all repos git-tracked on GitHub (07-05/06)
- [x] [FLEET-DECOMP] — FLEET-1..6 authored + registered (pass 376); Fleet program ACTIVE (07-06)

## Next Up

- [ ] Dispatch pending independent reviews: RGH-16/RO-FIX, EV-DIFF T3, MI-8 Chat 2 (highest-leverage per execution-plan-2026-07-03)
- [ ] [RGH-CR219] gate plumbing exemption — pair spawned 07-06 (verify Opening Protocol ran: handoff still queued at SEP close) → then [GIT-GATE-LIVE] (sequential) → then [FLEET-1] (pair staged; FLEET-3 before OP-2 spawns)
- [ ] [HERMES-P3] W2 — ready to spawn (W1 shipped 07-05)
- [ ] [G12] local-SEO growth orchestrator (Wave C — unblocked by client-schema-sync)
- [ ] [EV-FU5] Yoast meta-description stale review-count sweep

## Open Follow-ups (non-sprint)

- [ ] [MI-8] Chrome-dependent collection (SAM.gov, GSA eLibrary, SBA DSBS) — deferred, not blocking
- [ ] [MI-8] Cadence durable scheduling (monthly tool scan + quarterly re-score)
- [ ] Operator decisions flagged expired 07-03: GBP-API application outcome (case 4-8814000041505), WF-14 git storage (open since 06-14)

## Blocked / Waiting On

- [A4→FOCUS] blocked on CR-102 independent review
- resume-saas Stage 4a/4b (Slate migration, versioning/export) — PARKED since April; full resume-point plan archived at `repos/resume-saas/.kos/specs/archived-2026-04-mvp-current-focus-plan.md`

## Key Reminders

- When in doubt between "polish the factory" and "ship the product" — ship
- When in doubt between "capture knowledge" and "skip it" — capture
- Session close runs per `second-brain/_meta/session-close-protocol.md` (canonical); this file gets touched only on sprint-level change
- Write execution-log entries as work happens, not after the fact
