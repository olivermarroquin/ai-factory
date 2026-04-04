# Resume SaaS Build Sequence

## Phase 1 — Understand the Source

- inspect resume-factory structure
- identify entrypoints
- identify core logic vs shell glue
- identify outputs and dependencies

## Phase 2 — Define the Web App Shape

- decide target stack
- define UI entry flow
- define backend/API flow
- define output/download flow

## Phase 3 — Scaffold the New App

- use app-factory to create resume-saas repo
- apply standards from ai-agency-core
- create initial docs and structure

## Phase 4 — Port the Logic

- move or adapt reusable logic
- replace CLI interaction with app interaction
- test smallest working flow first

## Phase 5 — Stabilize

- verify one complete end-to-end flow
- clean up structure
- document what was reused and what changed

## Rule

Build the smallest functional end-to-end version first.
Do not optimize for scale, billing, or full automation yet.
