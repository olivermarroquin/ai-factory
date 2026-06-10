# Session Log

**Append-only log. Never delete entries. Most recent at the top.**

---

## 2026-06-09 → 06-10 — EV + S&H Core 30 completion, hub pages, nav architecture (Claude Code in VS Code)

**Duration:** ~12 hours (split across two calendar days)
**Mode:** implementation + debugging
**Interface:** Claude Code in VS Code (execution) + Claude.ai meta-review chat (peer review, skill authoring, render verification)

### What Happened

**EV Electric — Core 30 completion + hub architecture:**
- Fixed 3 live pages (03/04/05) with customer-visible placeholder content (hero, portrait, map) — replaced with real assets via WP REST API
- Fixed homepage Favicon-04.png (5 refs in `_elementor_data` replaced with cropped-Favicon.png)
- Built and published 7 hub pages: 6 per-service hubs (electrical-troubleshooting, panel-upgrade, ev-charger-installation, light-fixture-installation, smoke-alarm-installation, outlet-installation) + 1 master Service Areas page with full service×city matrix
- Rewired header nav (WP menu 55): swapped 3 arbitrary city sub-items → 6 service hub items + "Service Areas" top-level
- Wired /services/ page (ID 97) with 6 hub-card links
- Added breadcrumb backlinks to all 30 leaf pages (Home › Hub › This page)
- Set crafted AIOSEO meta descriptions on all 7 hubs (were auto-generated CSS text)
- Fixed hub CSS structure: wp:html wrapping, consolidated style blocks, hub-specific additions (city-grid, matrix, check-list)
- **EV result: 37 pages live (30 leaves + 7 hubs), all in-nav, max crawl depth 3 clicks**

**S&H Contracting — leaf fix + hub architecture:**
- Fixed S&H homepage Elementor rendering (corrupted `_elementor_data` JSON — unescaped quotes in CF7 shortcode from prior string-replace)
- Meta-review chat: fixed 28 S&H leaves missing `<!-- wp:html -->` wrapper (wpautop injected `<p>` into `<style>`, breaking hero gradient on 27/28 leaves)
- Meta-review chat: built and published 5 S&H hubs + rewired header/footer nav + added 29 leaf breadcrumbs + fixed hub hero images + footer "Areas We Serve" column
- **S&H result: 29 leaves + 5 hubs live, all in-nav**

**Tooling + skills:**
- New skill: `hub-and-nav-build` v1.0 → v1.1 (authored by meta-review chat): hub page template, nav-wiring SOP, CSS contract, verification gate, failure guardrails
- Render gate hardened to 3-state PASS/FAIL/BLOCKED with hero-image-fill assertion and connectivity preflight
- Guard 4 added to `publish-core-30-page.py`: re-reads content.raw post-publish, re-posts if wp:html wrapper lost

### Decisions Made
- **Footer: Option C** (Service Areas hub as crawlable link surface) — no Elementor footer template edit needed; fully automatic
- **Hub content: rich** (~800–1200 words per hub, house-voice quality bar)
- **Title banner: accepted** — CSS injection into page content broke hub rendering twice; operator accepted the theme title banner rather than risk further regressions; future fix must be via page-level template/meta only
- **S&H footer: Option D** (client-side WPCode JS snippet) — Elementor footer not REST-writable, JS snippet wires links without touching template data

### Artifacts Produced
- 7 EV hub pages (WP 6347–6353) + 5 S&H hub pages (WP 5004–5008)
- `plan-hub-pages-nav-architecture-2026-06-09.md` (approved + executed)
- `lesson-ev-sh-run-failure-retrospective-2026-06-09.md` (ISSUE-01 through ISSUE-13)
- `lesson-sh-leaf-wpautop-wrapper-defect-2026-06-09.md`
- `lesson-elementor-footer-clientside-link-fix-2026-06-09.md`
- `pattern-elementor-clientside-snippet-nav-footer-fix.md` (2 validated instances)
- `skills/hub-and-nav-build/` v1.1 (full skill with CSS contract, verification gate, failure guardrails)
- Guard 4 in `publish-core-30-page.py` (wp:html wrapper preservation)

### Key Insights
- **CSS injection into WP page content is fragile and destructive.** Three rounds of inject/remove for the title-hide CSS stripped 17K chars of base CSS; structural checks (balanced braces) passed while pages rendered unstyled. The render gate (getComputedStyle) was the only check that caught it. Standing rule: never modify the `<style>` block to add layout/visibility overrides; use page-level template/meta or accept the cosmetic issue.
- **String-replacing serialized data breaks it.** The S&H homepage `_elementor_data` corruption (ISSUE-12) was caused by a string-replace on the JSON blob. Parse → edit node → re-serialize is the only safe path.
- **"Verified" off an HTML-string check is not verified.** CSS rule presence ≠ CSS applying ≠ page rendering styled. This session produced 3+ false "verified" claims. The rendered visual output is the only ground truth.
- **wp:html wrapper is mandatory for HTML-in-WP-content pages.** Without it, wpautop and wptexturize corrupt `<style>` blocks and inline CSS. 27 of 28 S&H leaves shipped without it; the publish script now has Guard 4 to enforce it.

### Next Session Should Start With
- Verify EV hub rendering is stable (operator screenshot-confirmed before close)
- 2 S&H legacy page redirects (expert-electrical-repairs, specialized-electrical-services) — needs Redirection plugin
- Rotate the exposed S&H WP application password (credentials.md value appeared in a tool output)
- GSC indexing recheck ~2026-06-22 (2 weeks from publish) for both clients
- Golden-Services-02.png file copy (operator Hostinger action, documented in EV deployment status)

### Open Questions For Next Session
- S&H /services/ page (ID 873): Elementor page, ignores post_content — hub links block doesn't render. Needs Elementor editor edit or client-side JS injection (Option D pattern). Low priority — hubs are reachable via header+footer nav.
- Whether to build city-level hub pages (e.g., /vienna-va/) — deferred until Core 60+ when cities have 3+ services each

---

## 2026-06-06 — S&H Core 30 Wave 2 Complete (Stafford→Springfield→Burke→Lorton) (Claude Code in VS Code)

**Duration:** ~5 hours
**Mode:** implementation
**Interface:** Claude Code in VS Code

### What Happened
- Resumed wave-2 from handoff at Stafford (positions 28-29), completed all 4 remaining cities
- Published 10 pages total: Stafford (2), Springfield (3), Burke (2), Lorton (3)
- Full pipeline per page: author Q&A bodies → house-voice-rewrite → output-quality-loop EVALUATE → imagery (faceless/topic reuse + cached about portrait) → publish via publish-core-30-page.py
- Gate-peer-reviewer v2.1 execution evidence at every gate (placeholder counts + JSON-loaded foreign-client identity strings)
- 4 source-level defects found and fixed mid-run (D-10 through D-13)
- S&H Core 30 now at 29/30 pages live (slot 30 reserved for GSC-driven demand)

### Decisions Made
- Dispatch times parameterized per city: Lorton=15–20min, Springfield/Burke=20–30min, Stafford=35–50min (distance from Woodbridge HQ)
- areaServed in JSON-LD parameterized from city JSON (no more client-level HQ-county default)
- Utility coordination language parameterized (Stafford gets "Dominion, NOVEC, or REC"; Fairfax County cities get "Dominion Energy")
- D-13 three-check spec written for dispatch-time verification (body-internal + meta-inclusion + ground-truth cross-check) — logged, not yet built into gate-peer-reviewer SKILL.md

### Artifacts Produced
- 10 live pages (WP post IDs 4918-4939)
- scaffold-core-30-page.py: 3 new template variables (area_served_schema, utility_coordination_phrase, dispatch_time_phrase/short)
- emergency-electrician.json: fully parameterized (0 literal "45" dispatch references)
- s-and-h-contracting/panel-upgrade.json: utility phrase parameterized
- 4 city JSONs updated (stafford, springfield, burke, lorton): area_served_schema + electric_utilities + dispatch_time_phrase
- D-10/D-11/D-12/D-13 added to lesson-gate-peer-reviewer-build-wave-2-calibration-2026-06-06.md
- feedback memory: gate-reviewer must show execution evidence not narrative
- Handoff flipped to closed

### Key Insights
- The meta description is the recurring failure point for dispatch-time consistency — it's baked at scaffold time into draft-v1.md and not re-checked by body-editing passes
- Operator live-verification catches value-correctness errors the reviewer doesn't yet (D-13 spec written but not automated)
- Per-service hero reuse across cities works cleanly — zero new image generation needed for 10 pages, $0 credit cost
- Pipeline velocity increased through the session as trust built: Stafford got full gate-by-gate review, Springfield got G-data + G-publish only, Burke/Lorton ran straight through

### Next Session Should Start With
- Slot 30: check GSC data for demand signal to assign the final page
- S&H Phase 2 hubs (C1-C4): 29 live pages across 4+ services × 4+ cities triggers hub buildability
- GSC ADC re-auth: `gcloud auth application-default login` for indexing API
- D-13 implementation: build the 3-check spec into gate-peer-reviewer SKILL.md

### Open Questions For Next Session
- Slot 30 service/city assignment — pending GSC impression data
- AIOSEO bridge plugin installation on shcontractingunlimited.com — meta descriptions currently require manual wp-admin paste
- Whether to re-scaffold the 10 pages with the parameterized scaffolder (they work fine as-is with manual fixes applied; re-scaffolding would only matter if the scaffolder output is the canonical source-of-truth for future edits)

---

## 2026-06-06 — S&H Core 30 Wave 2 Build (Alexandria validation) (Claude Code in VS Code)

**Duration:** ~6 hours
**Mode:** implementation
**Interface:** Claude Code in VS Code

### What Happened
- Spawned wave-2 build from handoff-2026-06-05-s-and-h-core-30-wave-2-build.md
- Wave R: Produced 13 intersection briefs for 5 new cities (Alexandria ×3, Stafford ×2, Springfield ×3, Burke ×2, Lorton ×3) with live SERP research per cell
- Wave S: Scaffolded 5 city JSONs + 13 page drafts (positions 17-29) via scaffold-city-data.py + bulk-scaffold-pages.py
- Wave P1: Published Alexandria's 3 pages (positions 23-25) as the live wave-4 validation — first production run of autonomous gate-peer-reviewer
- 9 calibration defects (D-01 through D-09) captured as the gate-peer-reviewer Build wave 2 calibration corpus
- Fixed containedInPlace schema bug (Alexandria listed as Fairfax County), county→city text, response-time meta desync

### Decisions Made
- Demand-ranked publish order: Alexandria first (vol 260), then Stafford→Springfield→Burke→Lorton
- Faceless/generic heroes (not owner-face), per-service reuse across cities
- House-voice-rewrite mandatory before publish (caught as gap D-08, retroactively applied)
- Quality-loop EVALUATE mandatory before publish (caught as gap D-07, retroactively run)

### Artifacts Produced
- 13 intersection briefs in second-brain/05_shared-intelligence/research-briefs/intersections/
- 5 city JSONs in repos/ai-agency-core/scripts/data/cities/
- 13 page draft folders in core-30/ (positions 17-29)
- 3 published pages: panel-upgrade/emergency-electrician/ev-charger-installation × Alexandria
- Lesson: lesson-gate-peer-reviewer-build-wave-2-calibration-2026-06-06.md (9 D-rows)
- Execution log: execution-log-2026-06-06-core-30-wave-2-build.md

### Key Insights
- The gate-peer-reviewer v2.0 has 9 calibration fixes needed before next production run — the D-rows are the highest-value output of this session
- House-voice-rewrite is load-bearing — without it, content reads as competent-generic not contractor-authentic
- The publish script's quality gate (refusing without last-verdict: PASS) is a genuine safety net that caught real bugs
- Stafford has the weakest competitor SERP in the service area — a Minnesota spam page on page 1

### Next Session Should Start With
- Resume wave-2 at Stafford (2 pages, positions 28-29) — drafts scaffolded, pipeline: author Q&As → house-voice → imagery → quality-loop → publish
- Then Springfield (3) → Burke (2) → Lorton (3) — 10 pages total remaining

### Open Questions For Next Session
- Stafford/Burke Q&A bodies: reference EV charger installation or keep strictly to panel + emergency?
- Emergency-electrician hero library: generate a 4th variant for variety across 5 cities?
- Word count ~4,800 on Alexandria pages vs 2,500 target: trim for other cities or accept?

---

## 2026-06-06 — Website-factory Phase 0 intel complete (Claude Code)

**Duration:** ~2.5 hours
**Mode:** Research + data collection + analysis
**Interface:** Claude Code

### What Happened
- Spawned [F1] website-factory Phase 0 intel chat from handoff
- Executed Opening Protocol (tracker pass 133) + all 6 tasks + Closing Protocol (pass 134)
- Task 2 (priority): EV + S&H Core-30 per-city keyword-difficulty pass via DataForSEO Labs — per-city `location_name`, search volume + KD + local-pack spot-checks. Built demand-ranked build-order tables for both clients (EV 17 unbuilt, S&H 13 unbuilt)
- Task 1: Core Web Vitals for AJ Long — desktop 96-98, mobile 75-92 (beatable target)
- Task 3: Ranking monitor — 37 new AJ Long URLs now ranking (all page 3+); window narrowing
- Task 4: Redirect map — 22 old→new 308 entries across 3 redirect patterns
- Task 5: HousecallPro embed — static org-level token, `openModalWithParams()` API exists but unused = pre-fill opportunity
- Task 6: Blog taxonomy — 254 posts categorized into 13 topic clusters
- Peer-review caught stale live-baseline in build-order tables (S&H 16 live not 1, EV 12 live) — corrected
- Program handoff data-to-verify: 5/6 checked off

### Decisions Made
- Build-order for both clients now ranked by city head-term demand (not original sequential order)
- KD 0-4 across all cities = green-light signal for local SEO
- Recommend monthly AJ Long ranking monitor as scheduled task
- S&H Phase 2 hubs C1-C4 all triggered (16 live pages = 4 services × 4 cities)

### Artifacts Produced
- `aj-long-teardown/data/ev-sh-keyword-priority.md` — prioritized build-order tables
- `aj-long-teardown/data/dfs-ev-sh-kw-raw.json` — raw search volume + KD data
- `aj-long-teardown/data/dfs-kw-difficulty.json` — keyword difficulty scores
- `aj-long-teardown/data/dfs-pagespeed-ajlong.json` — Lighthouse CWV data
- `aj-long-teardown/data/dfs-ranked-keywords-2026-06-05.json` — ranking monitor snapshot
- `aj-long-teardown/data/redirect-map.tsv` — 22-entry old→new map
- `aj-long-teardown/data/blog-topic-taxonomy.md` — 13-cluster blog taxonomy
- Teardown §26-§29 appended
- Program handoff data-to-verify list updated
- Tracker pass 134, handoff consumed, event-log rows appended

### Key Insights
- All service×city long-tails below Google Ads reporting threshold — normal for hyperlocal; city head-term volume is the proxy for demand
- AJ Long's mobile CWV (75-92) is the beatable benchmark; their CLS=0 is the bar to match
- 37 new AJ Long URLs ranking in under a month = indexation transition is real but still page 3+
- HousecallPro has `openModalWithParams()` for per-page pre-fill that AJ Long doesn't use — free conversion advantage

### Next Session Should Start With
- [F2] gate-peer-reviewer Build wave 4 (autonomous page-build review) or [F3] page-factory reusability hardening — whichever operator prioritizes
- Wire AJ Long ranking monitor as monthly scheduled task
- S&H wave 2 research (5 city briefs for Alexandria/Stafford/Springfield/Burke/Lorton)

### Open Questions For Next Session
- Should the AJ Long ranking monitor fire as a Claude Code scheduled task or a manual monthly re-run?
- S&H Phase 2 category hubs (C1-C4) are all triggered — build them before or after wave 2 city pages?

---

## 2026-04-22 — Stage 4a full-day session: review screen shipped, Slate migration decided (Claude.ai chat + Claude Code)

**Duration:** ~14 hours
**Mode:** Execution (heavy) + strategic redesign mid-session + knowledge capture
**Interface:** Claude.ai strategic chat + Claude Code in VS Code

### What Happened — Strategic Summary

Today was the longest session to date and the first with a major mid-session architectural pivot. Stage 4a started with a clean plan (three-pane review screen, per-op diff highlighting, single-level undo, client-side export deferred to 4b) and ended with Stage 4a substantially complete but blocked on a full component rewrite via Slate.js for the freeform editor in ProposedPane.

Three narrative arcs:

**Arc 1 — Stage 4a planning and implementation.** Stage 4 split into 4a (three panes + toggles + diff) and 4b (versioning + export). PDF library decision finalized as @react-pdf/renderer. Stage 4a built in sections 1-6 (OriginalPane, ProposedPane, ProposalCard, ProposalsList, ReviewScreen, AppShell wiring). Initial live test passed 12 of 15 checks.

**Arc 2 — Bug triage and review-screen redesign.** Three bug classes surfaced during live test: REPLACE_LINE indentation loss, applyProposals heuristic failures on real resume headers, and UX confusion with two stacked text surfaces. Redesigned review screen mid-session: single contentEditable pane with inline highlighting, multi-level undo with TOGGLE_ALL action, "Clear all edits and selections" replacing "Restore original." Spec revised (10 edits). Five fix rounds landed: Fix 1a (data layer), Fix 1b (contentEditable pane), Fix 2 (applyProposals normalization), Fix 4 (multi-line before + REPLACE_LINE-to-phrase conversion), Fix 5/5.1/5.2 (layout regression), Option A (focus fix).

**Arc 3 — contentEditable dead end and Slate decision.** Fix 6 (plaintext-only contentEditable) and Fix 6.1 (line-div cursor walker) each resolved one bug and surfaced another. Diagnostic instrumentation added, revealed root cause: React and Chrome's contentEditable cannot co-own the DOM. Every fix patches a symptom of the divergence; none addresses the divergence itself. Slate.js chosen as replacement (over Lexical, TipTap, CodeMirror) for bundle size, React-native API, element-type styling fit, v1.1 inline-popover roadmap compatibility. Decision made to stop for the night and execute Slate migration with fresh eyes rather than push through.

### Decisions Made — Strategic Level

Non-trivial cross-cutting decisions locked today (all captured in 01_current-strategy.md Locked Decisions + build-log design-decisions table):

- Stage 4 split into 4a (three-pane review) and 4b (versioning + export)
- PDF library: @react-pdf/renderer, not jspdf or pdf-lib (quality over bundle size)
- PDF template: minimal single-column Helvetica for MVP, richer templates v1.1
- Product framing Path C: v1 = AI proposal-review tool, v2 = format-preserving resume editor
- Diff visualization: per-op highlighting, not text-diff library
- Review-screen redesign: single contentEditable pane with multi-level undo, TOGGLE_ALL action, Clear all edits and selections
- Toggle UX: scroll stays, cursor to start of text, focus preserved
- Fix 4 threshold: REPLACE_LINE auto-converts to phrase when before[0] is ≥30% of line length (captures sub-line edits without breaking short-substring cases)
- Slate.js migration for ProposedPane (structural replacement, not a patch)

Deferrals captured in 01_current-strategy.md under "Things Not Building":
- Format-preserving resume export (v2 vision)
- Pane scroll alignment in review screen
- Synchronized three-pane review experience (cross-pane anchor highlights)
- Orchestrator prompt improvements for op-type accuracy
- Schema validator strictness for proposal.before entries (reject embedded \n)

### Key Insights

- The strategic chat + Claude Code two-surface model remained the right fit under 14 hours of load with major architectural decisions. State-delta prompts produced cleanly, Claude Code executed verbatim, operator approved each diff. Zero drift on strategic state files.
- Live testing is the primary bug-surfacing mechanism for anything user-facing. Today reinforced yesterday's insight: the three critical bugs (REPLACE_LINE indentation, applyProposals heuristic failures, contentEditable Enter/backspace) were all invisible to unit tests and surfaced in the first minutes of real usage with a real resume. Test suites aren't wrong — they're just operating at a different abstraction level than user interaction bugs live at.
- The intake checklist gap surfaced mid-session: the frontend MVP spec did not capture "user will paste resumes that came from DOCX/PDF and expect format-preserving output" as an intake requirement. Captured as `venture-intake-checklist.md` in second-brain/05_reference/ for future ventures. Gap cost no time today but would have cost major time if caught later. Intake checklist discipline pays off.
- The contentEditable dead end is a meta-lesson more valuable than the specific fixes. Any product requirement mixing user-editable text AND per-character/per-line visual styling in the same rendered surface requires a real editor framework (Slate, Lexical, TipTap, ProseMirror, CodeMirror). "Simple contentEditable + React children" is a well-known trap that looks fine for demos and fails under real use. Added to venture-intake-checklist as editor-framework-decision question for future ventures.
- Stopping for the night when push-through-to-finish was tempting was the correct call. The Slate migration is a 2-4 hour focused task with a clear plan. Starting it at midnight after 14 hours of debugging would have introduced regressions beyond the scope of the migration itself and required rollback in the morning. The plan doc is a much better handoff than a half-finished implementation.
- Mid-session design changes are expensive but sometimes correct. Today's review-screen redesign (two-pane → single-pane + multi-level undo + Toggle All) happened around hour 6 and required reworking Fix 1a and building Fix 1b. Looking back, the redesign was right — the original two-pane split was the wrong UX. The cost of catching it live-test-late instead of spec-review-early was about 2 hours. Catching the contentEditable issue spec-review-early would have saved 4+ hours. Intake checklist captures this so future ventures don't repeat.
- The strategic chat was worth its weight in pushing back on tired decisions near the end of the session. Twice tonight the chat pushed Oliver to stop instead of push through; both were the correct call. The value of having a separate strategic surface (not just an execution interface) is amplified during long sessions.

### Artifacts Produced (Today, Full List)

resume-saas repo (28 commits today):
- frontend/components/OriginalPane.tsx (new)
- frontend/components/ProposedPane.tsx (new, rewritten 3x over the day)
- frontend/components/ProposalCard.tsx (new)
- frontend/components/ProposalsList.tsx (new)
- frontend/components/ReviewScreen.tsx (new)
- frontend/components/AppShell.tsx (modified — review case wired)
- frontend/lib/types.ts (modified — UndoEntry type, undoStack)
- frontend/lib/context/actions.ts (modified — TOGGLE_ALL added)
- frontend/lib/context/reducer.ts (modified — multi-level undo semantics)
- frontend/lib/applyProposals.ts (modified — Fix 2 + Fix 4 defensive fallbacks)
- frontend/lib/diffPreview.ts (new — per-op diff line computation)
- frontend/scripts/ (new — diagnostic scripts from Fix 4 reconnaissance)
- docs/frontend-mvp-spec-v1.md (modified — Revision History, single-pane design, multi-level undo, Toggle All, known applyProposals limitations)
- docs/build-log.md (11 new design-decisions rows, 2 Meta-lessons entries, multiple per-fix session entries)
- docs/stage-4a-slate-migration-plan.md (new — full handoff document for next session)

Strategic state:
- ai-factory/system-state/strategic/01_current-strategy.md (5 new Locked Decisions, 2 new Open Decisions, 4 new Things Not Building entries)
- ai-factory/system-state/strategic/02_current-focus.md (Stage 4a progress, Stage 4b dependencies, Slate migration task queue)
- ai-factory/system-state/strategic/03_session-log.md (this entry)

Knowledge OS:
- second-brain/05_reference/venture-intake-checklist.md (new — 15-question intake checklist seeded from resume-saas lessons)
- second-brain/06_retros/2026-04-22_resume-saas-intake-gap-mid-build.md (new — mid-build retro on format-preservation vision gap)

### Next Session Should Start With

The session-start protocol in workspace/CLAUDE.md will run automatically. It should produce a summary ending with:

"Stage 4a is substantially complete. The blocker for completion is a Slate.js migration of ProposedPane. Read `repos/resume-saas/docs/stage-4a-slate-migration-plan.md` end-to-end before writing any prompts. Then read Slate's quickstart. Validate the plan's proposed implementation approach against Slate's idioms, adjust if needed, then execute."

First action after summary: read the migration plan doc. Do NOT start writing Claude Code prompts until that plan has been read and Slate's basics have been skimmed. The plan doc estimates 2-4 hours total for the migration (including test and close-out).

### Open Questions For Next Session

- Will Slate's idioms for programmatic document replacement (Transforms.delete + Transforms.insertNodes at root) work cleanly, or does Slate prefer a different pattern for full-value replacement on structural changes?
- Does `lib/diffPreview.ts` survive the migration or become obsolete? Decide during implementation.
- After Slate migration lands, revisit Stage 4b sequencing: versioning + export, or start with export first?
- Post-Stage-4b: when does docker-compose.yml become worth building vs. continuing with parallel dev server commands?

---

## 2026-04-21 (evening) — End-of-day close-out: Stages 1 through 3.5 shipped, MVP plumbing complete (Claude.ai chat + Claude Code)

**Duration:** Full day — approximately 8+ hours from start of execution chat through final commit.
**Mode:** Execution (primary) + strategic planning (as needed)
**Interface:** Claude.ai strategic chat + Claude Code in VS Code

### What Happened — Strategic Summary

Today was the single most productive session in the project to date. The original Week 1 plan called for scaffolding, spec, and a possibly-working backend connection. Instead we completed the equivalent of Week 1 plus most of Week 2's original scope, and arrived at a functionally end-to-end working MVP (minus the review/export UX, which is Stage 4 tomorrow).

Five build stages shipped:
- Stage 1: Next.js 16.2 scaffold + Tailwind v4 + TypeScript strict
- Stage 2: Full frontend state management layer (types, actions, reducer, context, proposal-application algorithm)
- Stage 2.5: Backend dependency manifest, fresh venv, /api URL prefix, 40/40 tests passing
- Stage 3: Frontend wired end-to-end via Next.js proxy rewrite; Input + Processing screens rendering; error path verified
- Stage 3.5: Fixed OpenAI strict Structured Outputs schema bug (narrative must be nullable + required). Full stack verified with real OpenAI API call returning 7 real proposals.

Three setup/documentation stages also shipped:
- Updated repos/resume-saas/CLAUDE.md with correct API contract and task order
- Wrote repos/resume-saas/docs/frontend-mvp-spec-v1.md (authoritative frontend spec)
- Updated workspace/CLAUDE.md with Session End Protocol trigger phrase and Working with the Strategic Chat section
- Created repos/resume-saas/docs/build-log.md and appended per-stage entries for all five stages

### Decisions Made — Strategic Level

Non-trivial cross-cutting decisions locked during today's work (all captured in 01_current-strategy.md Locked Decisions + build-log design-decisions table):

- Synchronous /api/rewrite call for MVP (async deferred)
- Client-side PDF/DOCX export via jspdf/docx (server-side is v1.1 fallback)
- Paste-text only inputs for MVP (file upload / URL scraping deferred to v1.1)
- Single-route state-machine UI (bookmarkable URLs deferred)
- /api URL prefix on all Flask blueprints
- Proposal toggle regenerates right pane with single-level undo (multi-level undo and inline popovers deferred)
- In-memory versioning kept in MVP (v1 = original, v2+ = saves; lost on refresh)
- Hybrid proposal UI: list as control surface + diff highlights as display surface (inline popovers v1.1)
- Next.js proxy rewrite pattern for local dev (avoids CORS, single-string swap for production)
- Backend dev port 8080 (5000 occupied by macOS AirPlay)
- Accept current stable versions of Next.js (16.2), React (19.2), Tailwind (v4) rather than downgrading to spec-written versions
- Python dependency manifest discipline: compatible-release pins, delete-and-recreate venv verification, single requirements.txt for MVP
- workspace/CLAUDE.md versioning: deferred (file on disk, not in any git repo; revisit when working from a second machine)
- ECS/Guardian app-build workflow extension: still premature until resume-saas and app #2 both ship (confirmed deferral)

### Key Insights

- The strategic chat + Claude Code two-surface model worked. State-delta prompts produced in chat, pasted into Claude Code, applied verbatim with diff review. Zero drift across a long session with many decisions.
- Small backend bugs get caught by live end-to-end testing, not by unit tests. The proposal_schema.py nullable-narrative bug was invisible to 40 unit tests (they mock the orchestrator) and surfaced in the first 30 seconds of real use. The error path surfacing the bug through the frontend's ErrorBanner was itself proof the frontend was correctly built.
- Reconnaissance-before-edits pattern pays off repeatedly. Every stage that started with "show me the current state first" avoided wrong assumptions. Stages that would have used blind edits (had we skipped inspection) would have hit at least two different bugs.
- The "capture design decisions as work happens" discipline in build-log is already paying off. We have 8+ rows in the design-decisions table that will become the raw material for second-brain/03_playbooks/frontend-mvp-design-decisions.md after MVP ships. Writing it retroactively would have lost most of the rationales.
- The factory-polishing-over-shipping failure mode was actively resisted multiple times today: (a) chose not to extend ECS/Guardian for app-build prematurely, (b) chose to defer workspace/CLAUDE.md versioning rather than build a superproject repo, (c) chose not to preemptively add CORS or python-dotenv until the integration actually needs them.
- Breaking stages into explicit plan-and-execute pairs (Part 1 = inspect, Part 2 = apply) caught multiple bugs before they could happen, most notably the openai 2.x version discovery during Stage 2.5 and the second schema-bug fix requirement in Stage 3.5.

### Artifacts Produced (Today, Full List)

Backend:
- repos/resume-saas/requirements.txt (new)
- repos/resume-saas/.gitignore (expanded)
- repos/resume-saas/app.py (modified — /api prefix)
- repos/resume-saas/backend/schemas/proposal_schema.py (modified — nullable narrative)
- repos/resume-saas/.venv/ (recreated clean, not committed, gitignored)

Frontend:
- repos/resume-saas/frontend/ (entire directory scaffolded via create-next-app)
- repos/resume-saas/frontend/lib/types.ts (new)
- repos/resume-saas/frontend/lib/context/actions.ts (new)
- repos/resume-saas/frontend/lib/context/reducer.ts (new)
- repos/resume-saas/frontend/lib/context/AppContext.tsx (new)
- repos/resume-saas/frontend/lib/applyProposals.ts (new)
- repos/resume-saas/frontend/lib/api.ts (new)
- repos/resume-saas/frontend/components/ErrorBanner.tsx (new)
- repos/resume-saas/frontend/components/InputScreen.tsx (new)
- repos/resume-saas/frontend/components/ProcessingScreen.tsx (new)
- repos/resume-saas/frontend/components/AppShell.tsx (new)
- repos/resume-saas/frontend/next.config.ts (modified — proxy rewrite)
- repos/resume-saas/frontend/app/layout.tsx (modified — AppProvider)
- repos/resume-saas/frontend/app/page.tsx (modified — renders AppShell)
- repos/resume-saas/frontend/app/globals.css (modified — Tailwind v4 imports)

Documentation:
- workspace/CLAUDE.md (updated, not committed — no repo)
- repos/resume-saas/CLAUDE.md (updated)
- repos/resume-saas/docs/frontend-mvp-spec-v1.md (new)
- repos/resume-saas/docs/build-log.md (new + per-stage entries)
- repos/resume-saas/README.md (dev-server instructions added)
- ai-factory/system-state/strategic/01_current-strategy.md (multiple updates)
- ai-factory/system-state/strategic/02_current-focus.md (end-of-day close-out updates)
- ai-factory/system-state/strategic/03_session-log.md (this entry + earlier-today entry)

Commits landed today (across three repos):
- resume-saas: 10+ commits covering each stage separately
- ai-factory: multiple commits on strategic files

### Next Session Should Start With

Tomorrow (2026-04-22) session-start protocol runs automatically via workspace/CLAUDE.md. It should read these strategic files and produce a summary that says:

"You're on Stage 4 of resume-saas. Yesterday Stages 1–3.5 shipped — scaffold, state layer, dependency manifest, frontend wiring, and a schema bug fix. The MVP plumbing is end-to-end verified. Today's work is the review screen: three panes, diff visualization, versioning UI, client-side PDF/DOCX export. The full Stage 4 checklist is in 02_current-focus.md under Next Up."

Action after summary: start Stage 4 planning questions. Specifically, before writing Stage 4 code, the strategic chat (me, tomorrow) should walk through:
1. jspdf vs pdf-lib vs react-pdf — which PDF library and why
2. Whether to build all three panes in one stage or split further (Stage 4a/4b)
3. Diff visualization approach — text-diff library vs simple per-op highlighting
4. Export formatting — how literally plain should the exports be

### Open Questions For Next Session

- Stage 4 library choices (see above)
- When does docker-compose.yml make sense — post-Stage-4 as originally planned, or post-deployment?
- Should the rewrite.py surface-the-real-status-code polish happen before or after MVP ships?

---

## 2026-04-21 — Week 1 Execution Session (Claude.ai chat + Claude Code)

**Duration:** ~ongoing
**Mode:** Execution — spec writing, CLAUDE.md corrections, build-log setup
**Interface:** Claude.ai web chat (strategic) + Claude Code in VS Code (execution)

### What Happened
- Read backend code (rewrite_routes.py, rewrite.py, rewrite_orchestrator_v5.py) to derive the actual /rewrite API contract.
- Identified discrepancy between CLAUDE.md and real code: endpoint was at /rewrite, not /api/rewrite; API contract section described the wrong response shape.
- Made 8 cross-cutting design decisions for the frontend MVP (captured in design decisions table of repos/resume-saas/docs/build-log.md).
- Updated repos/resume-saas/CLAUDE.md: fixed API contract section, fixed spec-location pointer, updated Week 1 task order.
- Created repos/resume-saas/docs/frontend-mvp-spec-v1.md as authoritative spec for Next.js scaffold.
- Created repos/resume-saas/docs/build-log.md with design decisions table and first session entry.
- Updated 02_current-focus.md and 01_current-strategy.md to reflect today's decisions and completions.

### Decisions Made
- Synchronous API for MVP (async deferred)
- Client-side PDF/DOCX export for MVP (server-side deferred)
- Paste-text only inputs for MVP (file upload, URL scrape deferred to v1.1)
- Single-route state-machine UI (multi-route deferred)
- /api URL prefix on all Flask blueprints
- Proposal toggle regenerates right pane from scratch with single-level undo
- Versioning kept in MVP, in-memory only
- Hybrid proposal UI: list + diff highlights (inline popovers deferred)
- ECS/Guardian extension to app-build workflow is premature; wait for 2+ data points

### Artifacts Produced
- repos/resume-saas/CLAUDE.md (edited)
- repos/resume-saas/docs/frontend-mvp-spec-v1.md (new)
- repos/resume-saas/docs/build-log.md (new)
- ai-factory/system-state/strategic/02_current-focus.md (edited)
- ai-factory/system-state/strategic/01_current-strategy.md (edited)
- ai-factory/system-state/strategic/03_session-log.md (this entry)

### Key Insights
- The "frontend spec" process surfaced backend debt (orchestrator field-name mismatch with the spec) we wouldn't have caught otherwise. Speccing the frontend forced a close read of the backend contract.
- Strategic state files drift silently during execution sessions. Need forcing function — adopted 1+3 pattern: session-end protocol asks Claude Code to drive state updates; end-of-chat deltas from strategic chat get pasted as one-shot update tasks.
- Capturing design decisions in build-log "as work happens" is lighter weight than waiting for retros and produces better raw material for future playbooks.

### Next Session Should Start With
1. Apply /api URL prefix change in app.py + update affected tests (small backend task)
2. Scaffold repos/resume-saas/frontend/ per docs/frontend-mvp-spec-v1.md (Next.js 14 App Router, TypeScript, Tailwind)
3. Wire frontend to POST /api/rewrite and verify end-to-end

### Open Questions For Next Session
- Does repos/resume-saas/app.py belong at repo root or under backend/? (Structural cleanup, separate from scaffold.)
- Orchestrator field-name mismatch with spec — audit after MVP ships.

---

## 2026-04-21 — Knowledge capture session (Claude Code in VS Code)

**Duration:** ~2 hours (estimate)
**Mode:** Documentation + state correction
**Interface:** Claude Code in VS Code

### What Happened
- Drafted and committed retrospective state capture (2026-04-19 entry) to 03_session-log.md
- Drafted and committed resume-saas backend migration retro to second-brain
- Drafted, committed, and amended ai-factory control system retro with operator context
- Initialized second-brain/ as git repository with .gitignore for Obsidian files
- Identified and corrected test-count ambiguity in current-system-state.md
- Added Task Completion Checkpoint Protocol to workspace/CLAUDE.md

### Decisions Made
- second-brain/ gets its own git repo, to be backed up to GitHub separately
- State files will use explicit language ('defined'/'passing'/'failing'/'blocked') rather than bare counts
- python-docx dependency blocker is noted as debt, not fixed this session (install when frontend work needs it)
- Task Completion Checkpoint Protocol is mandatory, not optional — enforces knowledge capture between tasks

### Artifacts Produced
- `second-brain/06_retros/2026-04-20_resume-saas-backend-migration-retro.md`
- `second-brain/06_retros/2026-04-20_ai-factory-control-system-retro.md`
- `second-brain/.gitignore`
- `workspace/CLAUDE.md` (updated with Task Completion Checkpoint Protocol)
- `ai-factory/system-state/current-system-state.md` (corrected test count)

### Key Insights
- Retrospective capture reveals hidden state drift: writing the retros exposed that current-system-state.md had language ambiguity
- The inability to remember the specific Guardian expansion bug after two weeks proved the need for build-time capture vs. retroactive retros
- ai-factory control system retro showed 38 docs for 2 formal production uses — the workspace audit's "factory polishing" pattern playing out in data
- Scope evaluation got more honest after operator provided context: Guardian expansion was legitimately reactive, advisor layer had dual motivation (one product-driven, one speculative), workflow stubs were intentional schema reservations
- Knowledge capture infrastructure already existed; what was missing was an enforcement gate between tasks
- Step 14 pipeline failures (6/15 runs) were distributed across multiple stages (coder, planner, apply, reviewer, classification) — model output inconsistency under same input, not a code-under-test issue
- Step 15's 14 successive successful re-runs were deliberate iterative refinement, not error recovery — the pipeline has no mechanism to distinguish these, a real artifact trail gap

### Next Session Should Start With
- Prompts 4-6 from the retrospective knowledge capture plan if knowledge capture isn't finished, OR
- Begin resume-saas frontend scaffold (Week 1 build tasks in 02_current-focus.md) if knowledge capture is complete
- First action: scaffold `repos/resume-saas/frontend/` with Next.js 14 (App Router, TypeScript, Tailwind)

### Open Questions For Next Session
- Should python-docx be installed to unblock the 12 tests? (Likely defer until frontend integration touches resume parsing.)
- Should the workspace root become a git repo so workspace/CLAUDE.md is version-controlled? (Deferred decision — not critical this session.)

---

## 2026-04-19 — Retrospective state capture (Claude Code in VS Code)

**Duration:** N/A (retrospective summary)
**Mode:** Documentation
**Interface:** Claude Code in VS Code

### Purpose
Capture the state of the workspace as of the start of the strategic context
system. Establishes a baseline for future session entries.

### State of ai-factory
- **Latest tag:** v43-current-system-docs
- **Phase:** Controlled Execution — Full Lifecycle Control Implemented
- **Objective mode:** migration-execution (set via ai-factory-transition)
- **Latest execution cycle:** 2026-04-10, outcome: succeeded (proving_pass_cycle_B)
- **What works:** Full control loop enforced — ECS resolution, Guardian (6 checks), operator entrypoint (ai-factory-run), objective transition (ai-factory-transition), post-execution outcome recording (ai-factory-record-outcome), operator advisory layer (ai-factory-operator + ai-factory-advisor)
- **Only executable workflow:** `code_migration` (class A, reason codes A_EXACT_PORT / A_SCHEMA_PORT). `app_build`, `automation_build`, `ui_conversion` defined but NOT executable.
- **Two transition records exist** in transition-records/
- **Context Engine:** NOT IMPLEMENTED — relies on manual operator discipline
- **Knowledge OS:** NOT IMPLEMENTED

### State of resume-saas backend
- **Status:** Phase 1 and Phase 2 complete (tags v40, v42)
- **Tests:** 40 defined; 28 passing, 12 blocked by missing `python-docx` dependency (test_resume_api.py)
- **API blueprints:** rewrite (POST /api/rewrite), resume, jobs — all wired into app.py
- **Services:** jd_parser, resume_parser, proposal_validator, rewrite_formatter, rewrite_orchestrators v1–v5 (v5 is current; v1–v4 preserved as migration history)
- **Schemas:** proposal_schema
- **Empty dirs:** backend/models/, backend/utils/ — not populated
- **Note:** resume-saas backend served as the migration validation harness during ai-factory build, not as a product priority

### State of resume-saas frontend
- Directory `repos/resume-saas/frontend/` exists with subdirectories `app/`, `components/`, `lib/` — all empty
- No package.json, no Next.js scaffold, no components
- Not started

### State of second-brain
- 18 spec/reference files across `01_ai-operating-system/`, `02_ventures/`, and `05_reference/`
- Knowledge OS: structure present, no content captured yet — no patterns, no retros, no playbooks
- Used as reference input during ai-factory build; not yet used as an active learning system

### What's Active / Not Active
- **Active:** ai-factory migration pipeline (code_migration only), resume-saas backend (stable, not being modified)
- **Paused / not started:** resume-saas frontend build, VIS tool build, second-brain knowledge capture workflow, app-factory workflows (app_build, automation_build), operator tool expansion

### Known Issues / Debt
- Guardian stale-state check has incomplete artifact mapping for some current step language
- Operator advisor requires `claude` binary on PATH — not portable without Claude Code session credentials
- `python3` interpreter resolution inconsistency between bash wrappers and shell alias (ai-factory-advisor uses python3.12 explicitly as workaround)
- Mode-derivation keyword matching (whole-word) must stay consistent across snapshot, guardian, and transition — fragile if objective language drifts
- No docker-compose.yml for local dev (frontend + backend together)
- No frontend MVP spec document yet
- No workspace/CLAUDE.md with session protocol yet (a misnamed `CLAUDE .md` with a space exists)
- No build-log.md in resume-saas/docs/ yet
- Missing `python-docx` dependency blocks 12 resume API tests
- `ai-factory/system-state/current-system-state.md` contains the string "40 tests" which was interpreted as "40 passing" when the reality is 40 defined with 12 blocked. This ambiguity suggests the state file needs stricter language conventions — state files should distinguish 'defined', 'passing', 'failing', and 'blocked' explicitly.

---

## 2026-04-20 — Strategic Planning Session (Claude.ai chat)

**Duration:** ~3 hours
**Mode:** Strategy, architecture review, planning
**Interface:** Claude.ai web chat (Opus 4.7)

### What Happened
- Reviewed WORKSPACE_AUDIT.md and all 17 system specs
- Identified the "factory polishing over product shipping" pattern as primary risk
- Decided against using migration pipeline for frontend work (wrong tool)
- Decided against multi-agent build teams for MVP (OpenClaw and Managed Agents premature)
- Locked 5 architecture decisions for resume-saas
- Defined portfolio strategy (build apps → accumulate → offer to clients)
- Defined agent capability ladder (Levels 1-5) with realistic timeline
- Designed strategic context system (6 files, this directory)

### Decisions Made
- Skip custom VIS build for 2 weeks, use NotebookLM + structured prompt template as interim
- Build VIS as 1-2 day tool in Week 2-3 evenings (not a multi-week project)
- Do NOT expand operator tool before resume-saas ships
- Use Claude Code in VS Code as primary development tool (not Managed Agents, not OpenClaw)
- Architecture stack: Next.js 14+ / Flask / Tailwind / Vercel / Railway
- No auth for resume-saas MVP
- VIS lives in `ai-factory/tools/vis/`
- Strategic context lives in `ai-factory/system-state/strategic/`

### Artifacts Produced (In Claude.ai outputs)
- `system-build-strategy-report.md`
- `accelerated-build-plan.md`
- `revised-build-plan-portfolio-strategy.md`
- `strategic-context-system.md`
- `complete-context-system-structure.md`
- This set of 6 strategic context files (00-05)

### Key Insights
- Claude Code already does what a multi-agent dev team would do for MVP work, with human-in-the-loop
- The end-state vision (Level 5 executive assistant) doesn't fully work for anyone yet, even Anthropic
- Portfolio strategy is smarter than bespoke consulting — higher margin, lower risk per project
- Manual VIS using NotebookLM gives 80% of value with 0% of build time for the first 2 weeks

### Next Session Should Start With
1. Read `00_who-i-am.md`
2. Read `01_current-strategy.md`
3. Read `02_current-focus.md`
4. Read latest entry in `03_session-log.md` (this one)
5. Read `05_active-references.md`
6. Then execute what's in "In Progress" in `02_current-focus.md`

### Open Questions For Next Session
- None — strategy is clear, execution starts

---

<!-- NEW ENTRIES APPENDED ABOVE THIS LINE -->
<!-- Template for new entries:

## YYYY-MM-DD — [Session Name] ([Interface])

**Duration:** 
**Mode:** 
**Interface:** 

### What Happened

### Decisions Made

### Artifacts Produced

### Key Insights

### Next Session Should Start With

### Open Questions For Next Session

---
-->
