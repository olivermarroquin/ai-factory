# Session Log

**Append-only log. Never delete entries. Most recent at the top.**

---

## 2026-07-06 — SEP-v2 arc completion + workflow conventions + queue staging (Cowork, same chat as 07-05 entry)

**Duration:** ~6 hours across two days
**Mode:** implementation + orchestration
**Interface:** Cowork (chat `session-end-protocol-v2-202607052100` — continuation of the 07-05 v2 build entry below)

### What Happened
- Shepherded [SEP-FU3] (independent review, PASS-WITH-FINDINGS, all findings fixed + re-verified) and [SEP-FU2] (13 door cards, aggregator lit, QC PASS) through spawn → relay → close
- Shipped the manual-workflow conventions: relay files (+ machine-output rule, FINAL signal, two-line tell-block, bare-line commands, reviewer gate-clearing duty), pair-spawn launcher (slug mode, one command → two prompted tabs), gate-skip script convention, terminal-copy commit rule, tidy.sh clipboard cleaner
- Queued the permanent-fix pipeline: [RGH-CR219] (gate plumbing whitelist + compact 8-line hook message + dedupe/recursion fix, Parts A-C), [GIT-GATE-LIVE] (staged shadow-mode rollout), [FLEET-DECOMP] (executed same day by its own chat — FLEET-1..6 authored + registered, pass 376)
- All 3 git-less repos onto GitHub (dad-businesses, keelworks new; hire-relay rebased onto its existing v0.7 history, case-c, no force); `project-git-init.sh` promoted as the reusable engine (collision branch validated live)

### Decisions Made
- Gate never auto-trusts model "plumbing" claims — automation = deterministic gate-side classification (CR219 Part A), interim = operator-run skips with the discrimination rule
- Reviewer owns gate-clearing (log-review-pass) on verified deliverables; operator relays pointers only
- Repo bootstrap: .kos-only initial commits, WIP never swept; skill path = fold into app-factory/init-project-vault (spec item 8)

### Artifacts Produced
- Conventions in CLAUDE.md (relay/pair-spawn/skip/commit-surface rules); spawn-pair.sh + project-git-init.sh + tidy.sh; handoffs RGH-CR219 + GIT-GATE-LIVE + FLEET-DECOMP; spec v2.1 improvement queue items 1-8; spawn pairs staged (rgh-cr219, git-gate-live, fleet-1 via FLEET-DECOMP)

### Key Insights
- Every operator friction traced to one root: text traveling through clipboards/terminals instead of files — the relay/script/launcher conventions are all the same fix, and all retire into FLEET
- Drift-sweep-at-close caught a live opening-gate gap at this very close (rgh-cr219 spawned but still status: queued) — spec item 1 justified by its own close

### Next Session Should Start With
- Verify rgh-cr219 producer ran its Opening Protocol (flip queued→active); then GIT-GATE-LIVE after CR219 closes; then spawn-pair.sh fleet-1 (FLEET-3 before OP-2)

### Open Questions For Next Session
- GIT-GATE-LIVE AC-5: operator push-behavior decision (auto-push vs operator-push) — Oliver decides during that run

---

## 2026-07-05 — Session End Protocol v2 redesign + build (Cowork)

**Duration:** ~2 hours
**Mode:** planning + implementation
**Interface:** Cowork

### What Happened
- Investigated the April-era Session End Protocol vs. the handoff Closing Protocol — confirmed two overlapping close-out systems and a two-thirds-stale `02_current-focus.md` as the cause of every run's close-out stall
- Designed + shipped v2: canonical close definition at `second-brain/_meta/session-close-protocol.md` (single source of truth), CLAUDE.md rewritten as dispatcher (Path A handoff / Path B ad-hoc), design spec at `_meta/specs/session-end-protocol-v2-spec.md`
- Added three mandatory close steps everywhere (template + tracker how-to): 1b quality + tier verification (PR-1 DoD, output-quality-loop Mode-4 eval on every deliverable, capability-gap surfacing), 3c project door-card (`_chat-status.md`) update feeding the aggregator → operations-planner → MCD roll-up chain, 6b drift sweep
- Slimmed `02_current-focus.md` to a current-only sprint card; archived the April resume-saas plan verbatim to `repos/resume-saas/.kos/specs/archived-2026-04-mvp-current-focus-plan.md`; corrected stale statuses (PR-1/GIT-GATE/RGH shipped 07-02)

### Decisions Made
- Dispatcher pattern over merged mega-protocol; canonical-doc-wins precedence over verbatim-rendered copies
- `03_session-log.md` kept (only cross-project narrative); `02_current-focus.md` touched only on sprint-level change
- Every close step is a vault-file write — Hermes/fleet forward-compatibility by construction; v2 doc seeds FLEET-2

### Artifacts Produced
- `second-brain/_meta/session-close-protocol.md` (NEW), `second-brain/_meta/specs/session-end-protocol-v2-spec.md` (NEW), CLAUDE.md rewrite, closing-protocol-template v2 steps, tracker how-to (pass 365), slim 02_current-focus, resume-saas archive, execution log

### Key Insights
- `02_current-focus.md` and `03_session-log.md` were both edited by parallel sessions mid-build — live proof that chat state belongs in the tracker/door-card layer, not strategic files
- The roll-up chain (door cards → aggregator → planner → dashboard) was already built but had no write-side guarantee; step 3c closes that

### Next Session Should Start With
- Optional: independent review of the v2 protocol docs; door-card backfill sweep (FU-2 in execution log)

### Open Questions For Next Session
- FU-2 door-card backfill: one-time sweep or lazily on first close per project?

---

## 2026-07-05 — [HERMES-P3-W1] Phase 3 Wave 1: Hooks + Telegram Home Channel (Claude Code in VS Code)

**Duration:** ~2h
**Mode:** implementation
**Interface:** Claude Code in VS Code

### What Happened
- Verified v0.18.0 substrate reality against upstream source (CR-163 class): `cron:complete` event DOES NOT EXIST (cron delivery is built-in via `deliver:` param); `/sethome` is the home-channel mechanism (env var, not config.yaml); FETCH_HEAD mtime replaces commit-date freshness per operator design input
- Built 1 hook (boot-health-check: `gateway:startup`, 3 health checks — cron failures, FETCH_HEAD staleness, systemd units — Telegram alert on issues, silent on all-clear)
- Did NOT build cron-delivery hook (substrate handles it natively)
- Wrote operator steps document (6-step paste-safe guide)
- Filed CR-178 (gh-api read-only gate friction — recurring false-positive class)
- All 5 ACs verified with raw on-box evidence
- Independent peer-review PASS, 0 blocking findings

### Decisions Made
- `/sethome` over config.yaml — substrate reality: config.yaml has no Telegram home channel key; `/sethome` persists to `.env` and updates live config
- FETCH_HEAD mtime over commit date — operator caught that commit date measures vault activity, not sync health; false-alarms on quiet days
- urllib.request over httpx for Telegram API — stdlib-only dependency for hook sandbox compatibility
- No cron-delivery hook — `cron:complete` event doesn't exist in v0.18.0; delivery is a built-in primitive
- Sync handler (not async) — all operations are fast (stat, subprocess, urllib)

### Artifacts Produced
- `skills/hermes-hooks/boot-health-check/HOOK.yaml` + `handler.py` — gateway:startup hook
- `skills/hermes-hooks/OPERATOR-STEPS.md` — operator placement + verification guide
- `second-brain/_meta/execution-logs/exec-log-2026-07-05-hermes-p3-w1-hooks-telegram.md`
- CR-178 in catch register (gh-api read-only gate friction)
- Event-log rows (code-complete + shipped)

### Key Insights
- Substrate-reality verification (CR-163 class) is load-bearing: 2 of 3 handoff assumptions were wrong (no `cron:complete` event, home channel is env var not config.yaml). Building without verification would have produced dead code.
- FETCH_HEAD mtime is a better sync-health signal than commit date — quiet repos false-alarm on commit-date freshness. Operator caught this during VERIFY-AT-SPAWN.
- v0.18.0 hooks are lightweight (plain Python in-process, fire-and-forget) — no need for external dependencies. stdlib urllib.request is sufficient for Telegram Bot API.

### Next Session Should Start With
- [HERMES-P3-W2] Curator fix + Errno-13 ownership + RGH-3 on-box deployment + Phase 3b handoff draft

### Open Questions For Next Session
- Cron output directory structure assumption in handler.py (`~/.hermes/cron/output/<job>/<timestamp>/result.json`) — verify against v0.18.0 during W2
- Box needs reboot (system restart required + 12 pending updates) — fold into W2's apt/security-updates operator task

---

## 2026-07-03 — EV-FU2 + EV-FU3: Review shortcodes + hours 24/7 (Claude Code in VS Code)

**Duration:** ~45 min
**Mode:** implementation
**Interface:** Claude Code in VS Code

### What Happened
- Converted hardcoded review counts (87/148) → `[ev_review_count]`/`[ev_review_rating]` shortcodes on 43 WP pages (25 Core-30 + 7 hubs + 6 A3 + 5 Wave-1) via REST API
- Replaced `openingHoursSpecification` in JSON-LD on all 43 pages from Mon-Fri 08:00-18:00 + Sat 09:00-16:00 → 7-day 00:00-23:59
- Updated `contact/page.tsx` and `client-ev-electric-services.json` hours to 24/7
- Produced operator Elementor guide for homepage/About page hours (operator executed + verified same session)
- Filed EV-FU5 (Yoast meta-description stale review count sweep — reviewer catch)
- Full 43/43 verification sweep PASS

### Decisions Made
- Scope expanded from "~25 Core-30" to 43 pages after auditing all page types (hubs, A3, Wave-1 all had same issues)
- Schema `reviewCount`/`ratingValue` NOT edited per-page (FU1 Snippet 2 content filter handles at render time)
- Homepage NOT REST-written per CR-146 precedent — operator Elementor guide instead

### Artifacts Produced
- `outputs/ev-fu2-fu3-convert.py` — conversion script (credentials redacted post-review)
- `outputs/ev-fu2-fu3-results.json` — per-page results
- `outputs/ev-fu3-homepage-hours-operator-guide.md` — operator Elementor guide
- `repos/ev-electric-services/.kos/execution-logs/execution-log-2026-07-03-ev-fu2-fu3-review-shortcodes-hours-24-7.md`
- Register rows EV-FU2, EV-FU3 → applied; EV-FU5 filed (new)
- Wave-status updated

### Key Insights
- Regex patterns for HTML content must account for inline tags (`<strong>`, `<em>`) wrapping target text — C30-08 missed on first pass, caught by verification sweep
- Always audit ALL page types when the task names a subset — 18 additional pages (hubs, A3, Wave-1) had the same issues
- The full-sweep verification step is load-bearing — it caught the C30-08 miss that the conversion script's patterns didn't

### Next Session Should Start With
- EV-FU5 (Yoast meta-description sweep) if prioritized
- Wave 2 differentiation planning if operator directs

### Open Questions For Next Session
- None — FU1-FU4 all closed, FU5 queued

---

## 2026-07-03 — CR-146 Golden Services cross-client leak fix (Claude Code in VS Code)

**Duration:** ~45 min
**Mode:** implementation
**Interface:** Claude Code in VS Code

### What Happened
- Verified live leak state on evelectric.pro: 56 `goldenservices.us` references per page (36 Manrope + 18 Syne @font-face filesystem paths + 2 `Golden-Services-02.png` logo refs returning 404)
- Exhaustively explored all REST API paths for programmatic fix — `elementskit-template`, `/elementor/v1/documents`, Customizer theme_mods — all dead ends (template `_elementor_data` not `show_in_rest`, no Elementor edit endpoint, BSR wp-admin only)
- Diagnosed why operator's prior BSR attempt failed: Elementor JSON uses escaped forward slashes (`https:\/\/`); prior search used unescaped URLs → 0 matches
- Produced 3-option remediation guide (Hostinger file copy / BSR with JSON-escaped strings / Elementor editor) + Customizer Typography font fix
- Operator executed fixes in wp-admin: logo via Elementor editor (header Nav Menu widget Mobile Menu Logo + footer broken Image widget deleted), fonts switched to Inter across ~12 Customizer typography locations
- Independent reviewer (session 484e159f) verified: 0 goldenservices refs on all 8 pages curled (homepage + 3 Wave-1 + 3 Core-30 + 1 hub). CR-146 closed.

### Decisions Made
- **All fixes operator-manual.** No REST/programmatic path exists for ElementsKit templates or Customizer theme_mods — confirmed by enumerating every WP REST route.
- **Fonts switched to Inter** (not re-selecting Manrope/Syne from Google Fonts) because Kirki's font-download cache would have re-served the stale goldenservices.us paths.
- **Footer logo deleted, not replaced.** The footer's broken Image widget was redundant — removing it was cleaner than re-pointing it.

### Artifacts Produced
- Updated `CR-146-golden-services-leak-fix.md` (status: resolved, with as-executed deltas)
- `execution-log-2026-07-03-cr146-golden-services-leak-fix.md`
- `pattern-wordpress-cloned-site-cross-client-leak-remediation.md` (SOP pattern, operator-authored)
- `_deployment-status.md` annotated with CR-146 + font leak status
- Catch register CR-146 row updated (Open → Resolved with LU-Q4 evidence)

### Key Insights
- BSR on Elementor data requires JSON-escaped search strings — the escaped-slash mismatch is a silent failure that looks like "BSR didn't find it" when really the search string was wrong.
- The font leak wasn't just 2 font families — it was ~12 separate Customizer typography locations (body, headings, buttons, nav, etc.) all pointing at the cloned site's paths. A checklist that says "fix body + heading fonts" undercounts.
- Kirki caches downloaded font files — even after fixing the Customizer source setting, re-selecting the same font family can re-serve the cached broken files. Switching to a different family (Inter) avoids this.

### Next Session Should Start With
- Execute remaining EV follow-up items (EV-FU2: ~25 older Core-30 pages with hardcoded review count, EV-FU4 completion)
- CR-147: llms.txt + robots.txt AI-crawler allowlist (one-time, operator file manager)
- Wave-1 content rebuild execution (CR-145 — the actual brief-driven page rebuilds)

### Open Questions For Next Session
- Does Kirki's font cache clear on its own after Customizer changes, or is there a manual purge step? (Relevant if Manrope/Syne are ever re-added.)

---

## 2026-07-03 — [client-schema-sync] Skill Build (Claude Code in VS Code)

**Duration:** ~3 hours
**Mode:** implementation
**Interface:** Claude Code in VS Code

### What Happened
- Surveyed `client-seo-onboarding` (11-step one-time pipeline), Core-30 scaffold/publish scripts, `gate-peer-reviewer` (21 gate types). Decided: NEW separate skill (different trigger cadence, data sources, execution model vs. onboarding). Operator confirmed.
- Built agnostic engine `schema_sync_engine.py` (~580L) with 5 CLI commands: `audit`, `verify`, `sync-rating`, `inject` (HowTo+Speakable), `inject-lb` (LocalBusiness via keelworks plugin). Zero hardcoded client values.
- Created 3 per-client profiles: EV (41 pages, all WP IDs), S&H (30 pages, WP IDs pending), Asian Delight (4 pages, Restaurant type — 2nd-client proof).
- Wrote SKILL.md v1.0.0 with config schema, safety rules, human-in-loop steps, gate integration.
- Independent review Round 1 caught 2 BLOCKING: (1) `safe_json_for_script` not implemented (Python json.dumps does NOT escape `</script>`), (2) `skip_widget_patterns` unenforced in engine. Both fixed and verified.
- Independent review Round 2: PASS (0 blocking). 17 unit tests + 8 adversarial reviewer tests all PASS.
- Full Productize-tier DoD B1-B6 completed in execution log.

### Decisions Made
- **Separate skill, not extension of client-seo-onboarding.** Different trigger cadence (recurring vs one-time), data sources (live WP vs intake forms), execution model.
- **Profile per client, not per business type.** Page lists, selectors, WP IDs are per-client; business-type differences come from the client config's `business_type` field.
- **`safe_json_for_script()` replaces `</` with `<\/`** — the standard web-safe JSON-in-HTML approach, applied to all 7 serialization paths (script tags + _kw_jsonld meta).
- **`filter_skip_widgets()` is nesting-aware** — tracks open/close tag depth to avoid eating sibling elements.

### Artifacts Produced
- `repos/ai-agency-core/scripts/schema_sync_engine.py` — agnostic engine (~580L)
- `skills/client-schema-sync/SKILL.md` — skill definition v1.0.0
- `skills/client-schema-sync/references/profiles/ev-electric-services.json` — 41 pages
- `skills/client-schema-sync/references/profiles/s-and-h-contracting.json` — 30 pages
- `skills/client-schema-sync/references/profiles/asian-delight.json` — 2nd-client proof (Restaurant)
- `skills/client-schema-sync/execution-logs/execution-log-2026-07-03-client-schema-sync-skill-build.md` — B1-B6 DoD

### Key Insights
- Python's `json.dumps` does NOT escape `</script>` — a common false assumption. The `safe_json_for_script` post-processing is mandatory for any JSON placed in `<script>` tags.
- `fnmatch.translate()` produces `(?s:...)` which makes `.*` match across quote boundaries in HTML attributes — manual glob-to-regex conversion is safer for HTML class matching.
- The independent review caught both safety defects that the producer missed — validates the separate-session reviewer model.

### Next Session Should Start With
- [G12] local-SEO growth orchestrator scoping/build (composes client-schema-sync + other G-series skills)
- G-schema gate type registration in `gate-type-registry.md` (tracked follow-up)
- S&H WP page ID population (human-in-loop step)

### Open Questions For Next Session
- Should G-schema be a registered gate type or handled by G-default?
- S&H profile needs WP IDs populated before sync-rating/inject can run

---

## 2026-06-23 — [BTF-3] Full Pipeline Generalization — Wave 3 (Claude Code in VS Code)

**Duration:** ~4 hours
**Mode:** implementation
**Interface:** Claude Code in VS Code

### What Happened
- Executed BTF-3 Wave 3: made the entire onboarding pipeline business-type-agnostic (not just scaffolding)
- **Slice 1 (Script Parameterization):** 6 scripts parameterized — scaffold-service-data.py (owner_title), scaffold-city-data.py (href-prefix + optional EV fields), scaffold-client-data.py (credentials checklist filtering), generate-imagery-prompts.py + generate-and-distribute-heroes.py (external prompt files), scaffold-page.py + electrician profile (CR-072 matrix_section_sequence from profile)
- **Slice 2 (Internal Links + OQL):** Defined restaurant internal-link axis model (Axis N — flat cross-page navigation); adapted insert-internal-links.py with --business-type dispatch; added "Restaurant fixed-list page" entry to OQL spec-routing-table
- **Slice 3 (Capstone Orchestrator):** Extended client-seo-onboarding SKILL.md v1.8→v1.9 with business-type routing table — ONE path routes electrician or restaurant by reading business_type from client config
- **Carried-forward items closed:** CR-072 (section sequence from profile), CR-082-lesson (CREDENTIALS_CHECKLIST parameterization)
- Independent review: 4 rounds total (S1: 2 rounds [BLOCKING on missing tests, then PASS], S2: 1 round [PASS], S3: 1 round [PASS])

### Decisions Made
- **Restaurant link model = Axis N (flat cross-page)** — restaurants have no service×city matrix, so Axes A/B/C don't map. Axis N iterates page-model.json's pages[] list for cross-page navigation proposals.
- **"Flag + filter" pattern for type-specific constants** — `applies_to` tags on shared lists (CREDENTIALS_CHECKLIST), filtered by `get_X_for_type(business_type)`.
- **Profile-declared section sequence (CR-072)** — `matrix_section_sequence` array in content-sections.json, engine reads with `.get()` + fallback. New matrix types reorder by editing JSON alone.
- **Orchestrator routing via SKILL.md table, not code fork** — per-step routing table maps each step to the correct flags for each business_type. No separate restaurant orchestrator needed.

### Artifacts Produced
- `scripts/scaffold-service-data.py` — owner_title parameterization
- `scripts/scaffold-city-data.py` — --href-prefix, --business-type
- `scripts/scaffold-client-data.py` — CREDENTIALS_CHECKLIST applies_to + get_credentials_for_type()
- `scripts/generate-imagery-prompts.py` — --service-prompts-file
- `scripts/generate-and-distribute-heroes.py` — --service-prompts-file
- `scripts/scaffold-page.py` — _render_matrix_section() dispatch, profile-driven sequence
- `scripts/profiles/electrician/content-sections.json` — matrix_section_sequence array
- `scripts/insert-internal-links.py` — check_axis_n(), detect_fixed_list_context(), --business-type dispatch
- `skills/output-quality-loop/references/spec-routing-table.md` — Restaurant fixed-list page entry
- `skills/client-seo-onboarding/SKILL.md` — v1.9 business-type routing
- `scripts/tests/test_btf3_slice1_generalization.py` — 6 tests
- `scripts/tests/test_btf3_slice2_internal_links.py` — 6 tests
- `scripts/tests/test_btf3_slice3_orchestrator.py` — 6 tests
- `second-brain/05_shared-intelligence/lessons/lesson-btf-wave3-retro.md` — Wave 3 retro

### Key Insights
- Wave 3 was mechanical parameterization on a well-structured codebase — the payoff of Waves 1-2 doing the architectural heavy lifting
- The "add a new type" procedure is now clear: create profiles/<type>/ + client config → scaffold-page.py produces pages with zero engine changes
- Every script followed the same parameterization shape: rename constant → add flag → thread through callers → backward-compat fallback

### Next Session Should Start With
- Wave 4 planning: select a third business type (plumber, HVAC, or another local service) to validate that the pattern generalizes beyond 2 types
- Author the "add a new type" playbook in second-brain/05_shared-intelligence/patterns/

### Open Questions For Next Session
- Should restaurant brief templates be operator-authored content or auto-generated from a discovery call transcript? (Honest limit from Wave 3)
- Which third type best tests the profile schema's flexibility? (A matrix-type like plumber would test CR-072's section reordering; a fixed-list type like dentist would test the restaurant path)

---

## 2026-06-23 — [RGH-12] Auto-infer reviewer role from gate-clearing (Claude Code in VS Code)

**Duration:** ~1.5h
**Mode:** implementation
**Interface:** Claude Code in VS Code

### What Happened
- Extended `classify_session_role()` with signal (b): auto-infer reviewer role from gate-clearing records — a session is classified `reviewer` if any other session's reviewed ledger contains an entry with `reviewer_session == self`
- Extracted `_check_marker_signal()` (signal a, RGH-11) and added `_check_gate_clearing_signal()` (signal b, RGH-12) with early-exit glob + process-lifetime cache
- Built `is_bash_reviewer_doc_write()` (RGH12-6): exempts reviewer Bash whose only write targets are known reviewer-working-doc paths (firing tracker, catch register, verdict files, reviewer execution logs) — strict B3 guard ensures compound commands with any non-doc write still gate
- Updated `check_gate()` session-level exemption to cover both `is_bash_entry_write_safe()` (RGH-11) and `is_bash_reviewer_doc_write()` (RGH12-6)
- Added 38 new tests: auto-inference unit (6), adversarial no-bypass (6), real-runner replay of BTF-W3/MCD-CR-075 scenarios (3), reviewer-doc-write unit (13), integration (4), compound-bypass guard (6)
- Independent review PASS (1 round, 2 advisories: test count discrepancy in summary + negative cache re-scan design note)

### Decisions Made
- **Glob approach** for signal (b) — scan `*-reviewed.jsonl` excluding own session's ledger. Bounded: `iglob` + line-by-line + early exit on first match + process-lifetime positive cache
- **Positive-only cache** — confirmed reviewer status cached forever (can't un-clear a gate); negative results re-scanned (reviewer may not have cleared yet). ADV-2 noted this as a design tradeoff vs efficiency
- **Reviewer-doc Bash write as separate function** (not folded into `is_bash_entry_write_safe`) — cleaner separation: write-safe = no writes at all; doc-write = writes only to known reviewer paths. Both checked in `check_gate()` for verified reviewer sessions only
- **B3 guard strict**: every compound segment must be either read-only or a reviewer-doc write. One non-doc write anywhere → entire command gates

### Artifacts Produced
- `repos/ai-agency-core/scripts/mandatory-review-gate/engine.py` — `_check_marker_signal()`, `_check_gate_clearing_signal()`, `_gate_clearing_signal_cache`, updated `classify_session_role()`, `_REVIEWER_DOC_WRITE_PATTERNS`, `_extract_write_target()`, `_is_segment_reviewer_doc_write()`, `is_bash_reviewer_doc_write()`, updated `check_gate()`
- `repos/ai-agency-core/scripts/mandatory-review-gate/test_session_tagging.py` — +38 tests (95 total, 156/156 with RGH-10 regression)

### Key Insights
- The auto-inference is truly forget-proof: the reviewer self-qualifies by doing its actual job (logging the producer's PASS). The BTF-W3 and MCD CR-075 scenarios that needed manual gate-skips would now resolve automatically
- Honest limit documented: a producer that can write arbitrary files into `.review-gate/state/` could forge a reviewed-ledger entry, but the write itself is dirty-ledger-tracked and the scoped exemption still only covers Bash
- RGH12-6 (reviewer-doc Bash writes) was a scope addition mid-build — the live BTF-W3 `cat >>` case showed the gap between RGH-10's tool-path exemption (Write/Edit only) and Bash redirect writes to the same paths

### Next Session Should Start With
- Update CR-010/044/054 notes in catch register to reference RGH-12
- Update independent-reviewer-mandate §0 to note registration becomes optional once RGH-12 is live
- Commit + push

### Open Questions For Next Session
- None — clean build, clean review

---

## 2026-06-22 — [RGH-11] Session-level reviewer tagging (Claude Code in VS Code)

**Duration:** ~2h
**Mode:** implementation
**Interface:** Claude Code in VS Code

### What Happened
- Built session-level reviewer detection and scoped Bash exemption for the mandatory review gate
- Created `classify_session_role()` in engine.py — reads structural marker files, returns `'reviewer'` only on valid evidence (fail-closed on all invalid cases)
- Created `is_bash_entry_write_safe()` in engine.py — scoped Bash exemption that passes commands without positive write indicators (redirects, file-mutating commands, Python inline writes) while still gating state-changing Bash
- Updated `check_gate()` with session-level exemption after RGH-10 source filter + RGH-5 independent-review filter alignment
- Created `register-reviewer-session.py` — session marker registration script with self-review rejection
- Updated `dirty-ledger-track.py` — added `bash_cmd` field for reliable write-indicator detection + `register-reviewer-session` to SELF_PATTERNS
- Created `test_session_tagging.py` — 60 tests (unit + adversarial + acceptance + real-runner replay)
- Updated CR-010, CR-054, CR-073 resolved notes in catch register
- Independent review PASS (2 rounds: R1 1 MAJOR [type validation gap], R2 0 catches, convergence)

### Decisions Made
- **Marker file approach** for session detection (vs evidence-based inference from reviewed ledger) — avoids timing problem where reviewer gets blocked before it can clear any gates
- **Scoped Bash exemption** (Option B from reviewer feedback) — only Bash without positive write indicators, not blanket. Caught the BLOCKING-1 bypass vector from plan review Round 1
- **Write-indicator detection at gate-check time** (in engine.py check_gate), not at tracking time (dirty-ledger-track.py) — separates concerns: tracker tracks faithfully, gate decides exemptions
- **Full bash_cmd field in dirty entries** — needed for reliable write-indicator detection since `display` is truncated to 80 chars

### Artifacts Produced
- `repos/ai-agency-core/scripts/mandatory-review-gate/engine.py` — `classify_session_role()`, `is_bash_entry_write_safe()`, `check_gate()` session exemption
- `repos/ai-agency-core/scripts/mandatory-review-gate/register-reviewer-session.py` (NEW)
- `repos/ai-agency-core/scripts/mandatory-review-gate/dirty-ledger-track.py` — SELF_PATTERNS + bash_cmd field
- `repos/ai-agency-core/scripts/mandatory-review-gate/test_session_tagging.py` (NEW, 60 tests)
- `second-brain/_meta/handoffs/_review-gate-catch-register.md` — CR-010/054/073 updates
- `second-brain/_meta/handoffs/_active-chats-tracker.md` — Active row added

### Key Insights
- Plan review with adversarial probing (2 rounds before build) caught a real bypass vector (blanket Bash exemption) that would have shipped if built from the original plan
- The `isinstance` + `.strip()` validation gap (MAJOR-1 from independent review) shows that JSON deserialization types need explicit validation — Python truthiness is too loose for security-critical code
- Session-level exemption composes cleanly with RGH-10 per-entry tagging — three-layer defense (per-entry source → session role → write-indicator detection)

### Next Session Should Start With
- Closing protocol: move tracker row to recently-closed, flip handoff status to consumed
- Verify the reviewer-orchestrator (RGH-9-P2) integrates `register-reviewer-session.py` into its dispatch flow

### Open Questions For Next Session
- Should `register-reviewer-session.py` validate that the `reviewing_session` dirty ledger actually exists? (Currently not required — acknowledged as honest limit that forgery requires multi-step attack with no deliverable bypass)

---

## 2026-06-22 — [RGH-9-P2] reviewer-orchestrator Phase 2 auto-watch event-log (Claude Code in VS Code)

**Duration:** ~1 hour
**Mode:** implementation
**Interface:** Claude Code in VS Code

### What Happened
- Extended reviewer-orchestrator skill v1.0 → v2.0 with Phase 2: auto-watch event-log polling loop
- Added Steps W1–W6: enter watch mode, tick scan, report, dispatch flow (reuses Phase 1 Steps 2–8), sleep-and-loop, exit
- Designed per-tick sleep model: conversational turns with operator intervention points between every cycle (not a monolithic Bash loop)
- Operator dispatch-plan gate (Step 4) preserved — no silent auto-dispatch
- Added honest limits 7 (session-scoped, not daemon) and 8 (per-session deduplication gap + mitigation)
- Acceptance proved on a real throwaway event-log row: watcher correctly identified it as the only unreviewed item among ~15+ rows, produced dispatch manifest, cleaned up test row
- Independent peer-review PASS (2 rounds [3,0], reviewer session 26201e56 ≠ producer b9138162)
- 3 advisory findings fixed post-review: tab-delimited grep (false-positive fix), abort-then-re-detect nagging (aborted sessions suppressed), last_seen_line_count wired

### Decisions Made
- **Per-tick sleep, not monolithic loop.** Each tick is a discrete conversational turn: grep → cross-check → report → sleep. Operator has natural intervention points. Fits Claude Code's turn-based model.
- **Session-scoped, not daemon.** Watcher only runs while the Claude Code session is active. Background/unattended watching is RGH-3/Hermes territory.
- **Aborted items suppressed.** Items the operator explicitly aborts at Step 4 are added to `dispatched_sessions` so they don't nag on the next tick.

### Artifacts Produced
- `skills/reviewer-orchestrator/SKILL.md` (v1.0 → v2.0)
- `_active-chats-tracker.md` pass 303 (Active row)
- `_active-chats-tracker-changelog.md` pass 303 entry
- Event-log rows (ready-for-review + reviewer PASS)

### Key Insights
- The per-tick sleep model is the right abstraction for Claude Code polling — it preserves operator control without fighting the execution model
- Phase 2's value is highest when multiple producers are in flight simultaneously (the current state: BTF-1, MCD-P4, G4 all active)

### Next Session Should Start With
- Phase 3 (bind to Mode 6 wave-close) is DEFERRED with named trigger: Phase 2 stable for ≥1 week of real use

### Open Questions For Next Session
- None — Phase 2 is self-contained

---

## 2026-06-19 — [PROVISION-existing-project] vault-orchestrator v1.6 existing-project decomposition (Claude Code in VS Code)

**Duration:** ~3 hours
**Mode:** implementation
**Interface:** Claude Code in VS Code

### What Happened
- Extended vault-orchestrator Mode 3 PROVISION with `--existing-project <slug>` flag
- Built 3-state phase classifier (done / partial / not-started) that reuses RESUME's 6-source state-read
- Created classification rules reference doc (`references/existing-project-classification-rules.md`)
- Added collision awareness against existing handoffs, in-flight chats, and spawn-queue rows
- Validated against website-factory program (17 phases: 7 done skipped, 3 partial scoped, 7 not-started identified)
- Bumped skill v1.5 → v1.6 with full changelog, trigger phrases, flags, step-by-step (E1-E10), verification checks (12-18)
- Underwent 3 rounds of independent peer review (operator-directed): converged [2,1,0]

### Decisions Made
- **Flag-based branch, not a separate mode.** Chose `--existing-project` flag on Mode 3 rather than "Mode 3b" because the output shape is identical to greenfield PROVISION.
- **Reuse RESUME's read, not reimplementation.** Steps E1-E2 invoke RESUME's 6-source read directly — no new read logic.
- **Three-state classifier, not binary.** Partial is distinct from done and not-started. WF-4's rejection case proved this is essential.
- **Collision-first, not draft-first.** Collision check (Step E5) runs before DECOMPOSE (E6) to prevent duplicate handoffs.

### Artifacts Produced
- `skills/vault-orchestrator/SKILL.md` (v1.6)
- `skills/vault-orchestrator/references/existing-project-classification-rules.md` (new)
- `second-brain/_meta/handoffs/vault-orchestrator/execution-log-2026-06-19-provision-existing-project.md`
- Event-log rows (build + close)
- Tracker pass 265 (open) + pass 271 (close)
- _recently-closed closure record + one-liner

### Key Insights
- Almost all real work is mid-stream, not greenfield — this was the single most-requested PROVISION capability
- The classifier's signal hierarchy (recently-closed > execution log > handoff frontmatter > artifacts) handles real vault messiness well
- Vault status values are more varied than expected (`ready` vs `ready-to-spawn`, `completed` vs `consumed` vs `closed`) — the classifier needed to cover all of them

### Next Session Should Start With
- vault-orchestrator Phase 5 (per-project orchestrator decomposition) is now unblocked — this was the gating prereq

### Open Questions For Next Session
- Should Phase 5 decompose the monolith into sub-skills, or is the current single-SKILL.md approach still serviceable given the existing-project path?

---

## 2026-06-17 — [MI-8] Chat 2: Replicate 4 govcon niches + MI-8 close-out (Claude Code in VS Code)

**Duration:** ~2.5 hours
**Mode:** implementation (data collection + analysis + close-out)
**Interface:** Claude Code in VS Code (host-side execution)

### What Happened
- Ran `market-intelligence-engine` v1.1 on 4 remaining govcon niches from config alone: facilities/construction (NAICS 236220/561210), staffing (561320/561311), management-consulting (541611/541612/541618), GSA-furniture/office (337214/337127)
- Pulled 29 USASpending API queries across all niches (all-firms, SB, 8(a), SDVOSB, WOSB, HUBZone, agency breakdowns)
- Produced 12 analysis files (analysis + Output A + Output B per niche)
- Discovered correct USASpending API set-aside filter parameter (`set_aside_type_codes`, not `set_asides`)
- Updated reuse map with cross-niche confirmation table (5 niches, zero leaks, zero skill changes)
- Added 21 new data gaps (DG-27..DG-47) to the central register
- Updated _README with all niche data folders, flipped MI-8 status to "pending independent review"
- Ran OQL across all 15 deliverable files: PASS-WITH-FINDINGS (4 advisories, 0 blocking)
- Applied all OQL fixes (README date, ground-truth verification)
- Wrote execution log for Chat 2

### Decisions Made
- **Scoring honesty:** Keelworks G4=0 for construction/staffing/furniture (no relevant capability) vs G4=1 for IT/consulting (real AI capability, zero govcon framing)
- **DG renumbering:** Furniture DG-33-37 → DG-43-47 to avoid collision with staffing
- **Furniture Config B superseded:** GSA-furniture govcon niche run replaces the original lighter local-services furniture test — 5 govcon niches is a stronger duplicability proof
- **Cross-niche verdict:** Pursue IT services (primary) + management consulting (additive); do not pursue construction/staffing/furniture as prime

### Artifacts Produced
- 12 new analysis files (4 × {analysis, Output A, Output B})
- 29 raw USASpending JSON files across 4 niche subfolders
- Updated: mi8-reuse-map.md, _README.md, _data-gap-register.md, 02_current-focus.md
- mi8-chat2-execution-log-2026-06-17.md
- This session log entry

### Key Insights
- **Zero skill changes for 4 additional niches confirms v1.1 is production-ready.** The B2G arena variant, provisioning preflight, and gap-discovery mechanism all transferred without modification across physical products (furniture), construction, healthcare staffing, and knowledge-work consulting.
- **Zero hardcoded leaks is the strongest reproducibility evidence.** No electrician-origin terminology leaked into any of the 5 govcon analyses.
- **Management consulting (541611) is the second viable niche for Keelworks** — AI transformation consulting under the same cert/vehicle path as IT services. Dual NAICS registration recommended.
- **The SB set-aside pool varies enormously by niche:** IT services ($315M top), consulting ($97M), construction ($86M), furniture ($22M), staffing ($19M). This determines competitive pressure and opportunity size.

### Next Session Should Start With
- Dispatch independent reviewer on Chat 2 deliverables (operator action)
- On reviewer PASS: move [MI-8] Active→_recently-closed on tracker
- Chrome-dependent collection remains a deferred residual (not blocking MI-8 close)
- Cadence scheduling (monthly tool scan + quarterly re-score) remains session-only, not yet durable

### Open Questions For Next Session
- Is Oliver eligible for 8(a)? (personal financial assessment — not determinable by the engine)
- Should cadence scheduling be set up as durable scheduled tasks now, or after MI-8 fully closes?
- Should the management consulting pursuit be actioned immediately (add 541611 to SAM.gov registration) or wait for the IT services path to be further along?

---

## 2026-06-16 — [MI-8] Govcon duplicability proof: federal IT services (Claude Code in VS Code)

**Duration:** ~3 hours
**Mode:** implementation (data collection + analysis + skill extension)
**Interface:** Claude Code in VS Code (host-side execution)

### What Happened
- Moved [MI-8] Ready→Active on tracker (pass 230)
- Ran `market-intelligence-engine` on government contracting (B2G) — a far field from the electrician origin — from config alone
- Pulled USASpending API data: 8 queries across NAICS 541512/541511/518210, all-firms + SB + 8(a) + SDVOSB + WOSB + HUBZone + agency breakdown
- Consolidated 86-entity SB competitor set, scored top 15 light / 5 deep across 14 arenas
- Produced Output A (perfect company profile) + Output B (Keelworks govcon gap-to-action plan)
- Updated skill v1.0→v1.1: B2G arena variant (G1-G6), per-client provisioning preflight, geo-grid anchor fallback
- Updated spec with B2G arena variant section
- Added 7 new data gaps (DG-20..DG-26) to register
- Wrote reuse map, govcon playbook pattern, gate-label re-audit
- Completed independent peer review (PASS-WITH-FIXES, 6 findings, all applied)

### Decisions Made
- Score SB tier against SB tier (not large primes) — Keelworks' actual competitive frame
- 14-arena model for B2G (8 standard + 6 G-arenas) rather than forcing govcon into local-services arenas
- Relabel (not re-run) 4 pre-registration G-market-intel verdicts — data sound, labels corrected
- Federal IT services as priority-1 niche; other 4 niches deferred to follow-up chat

### Artifacts Produced
- `mi8-govcon-data/` — 8 USASpending JSON files, consolidated competitor set, analysis, Output A, Output B, reuse map, execution log, gate-label re-audit
- `skills/market-intelligence-engine/SKILL.md` v1.1
- `spec-market-intelligence-engine.md` B2G variant section
- `05_shared-intelligence/patterns/pattern-govcon-market-intelligence-playbook.md`
- `_data-gap-register.md` updated with DG-20..DG-26
- Tracker pass 230 + changelog + event-log row

### Key Insights
- **The engine's config-driven architecture worked on a far B2G field.** 47% of components ran as-is; 29% needed skill extension (the B2G arenas), not instance hacks. Done bar for `feedback_no_half_finished_build_for_reuse` met.
- **B2G competition is structurally different from local-services.** Awards, certifications, vehicles, agency incumbency, and teaming partnerships are the decision-drivers — not SEO, local pack, or Google reviews. The arena model had to extend, not just parameterize.
- **8(a) eligibility is the single highest-leverage finding for Keelworks.** If Oliver qualifies (Hispanic/Latino heritage = presumed socially disadvantaged), sole-source contracts up to $4.5M open immediately. This changes the entire entry strategy.
- **Chrome is essential for B2G collection completeness.** SAM.gov, GSA eLibrary, SBA DSBS are all JS-rendered — WebFetch returns empty. G2/G3/G4/G6 precision requires Chrome.

### Next Session Should Start With
- Confirm Chrome (Work profile) connectivity
- Run Chrome-dependent collection for federal IT services (SAM.gov, GSA eLibrary, SBA DSBS)
- Pull remaining 4 govcon niches (facilities/construction, staffing, management-consulting, GSA-furniture)
- Set up durable cadence scheduling (monthly tool scan + quarterly re-score)
- Furniture Config B (lighter second-instance confirmation)

### Open Questions For Next Session
- Is Oliver eligible for 8(a)? (requires personal financial disclosure — not determinable by the engine)
- Is Keelworks registered on SAM.gov? (Chrome needed to verify)
- Should the remaining 4 niches be full runs or lighter confirmation passes?

---

## 2026-06-13 → 06-14 — [WF-14] Full current-state capture: EV + S&H + AJ Long (Claude Code in VS Code)

**Duration:** ~7 hours
**Mode:** implementation (capture + archive)
**Interface:** Claude Code in VS Code (execution) + parallel Cowork reviewer (independent verification throughout)

### What Happened

**Setup + opening protocol:**
- Read WF-14 handoff, WF-4 postmortem, pre-build-due-diligence-gate pattern
- Moved WF-14 Ready→Active in tracker (pass 181)
- Discovered all live page URLs via sitemaps: EV 41, S&H 58, AJ Long 24 representative
- HTTP precheck: 123/123 URLs returned 200 (C-01 resolved by visual confirmation on AJ Long PNGs)

**Folder reorg (operator-approved option b):**
- Created 3-state model for both clients: old/pre-core-30, old/post-core-30, new/custom-site
- EV: moved 6 HTML + _files/ + 2 TODOs → pre-core-30. S&H: moved 2 HTML + _files/ + 2 TODOs
- Updated all 6 _README.md files (2 top-level + 2 old/ + 2 new/)
- new/core-30/ and new/existing-pages/ untouched throughout

**EV Electric capture (41/41 pages, 519MB):**
- 164 screenshots (desktop 1440 + mobile 375, full + ATF per page)
- 41 HTML, 41 CSS, 41 computed-styles JSON, 41 meta/schema/OG JSON
- 143 assets (22 images, 90 fonts/7 Google Fonts families, 28 JS, 3 favicons)
- Full sitemap diff on disk: 41/43 content pages captured, 2 Elementor template fragments excluded

**S&H Contracting capture (58/58 pages, 634MB):**
- 232 screenshots, 58 HTML, 35 CSS, 58 computed-styles, 58 meta
- 151 assets (119 images, 25 Roboto fonts, 4 JS, 3 favicons)
- Server throttled after ~35 pages; retry with 3s delays captured remaining 23
- Full sitemap diff: 58/60 captured, 2 taxonomy archives excluded

**AJ Long Electric benchmark (24/24 pages, ~50MB):**
- 96 screenshots covering all 18 distinct page types (template-complete)
- 24 HTML, 2 CSS (Tailwind v4), 24 computed-styles, 24 meta
- 41 assets (5 images, 1 Inter font, 33 JS bundles, 2 favicons)
- Design tokens extracted: dark theme, Inter font, 60px h1, Next.js stack

**Wayback Machine recovery (handoff task 6):**
- EV: No Wayback snapshots exist (archive never crawled evelectric.pro). May 2026 HTML is the only pre-Core-30 record.
- S&H: 4 pages recovered from Jan-Feb 2026 (homepage, about, expert-electrical-repairs, electrical-installations) with 8 screenshots + 4 HTML

**Read-only proof closed (C-11):**
- Both sites' sitemap lastmods unchanged after ~4-hour capture window
- EV: page-sitemap 2026-06-10T01:10:51, elementskit 2026-05-25T20:41:16 — unchanged
- S&H: all 4 sitemaps unchanged

### Decisions Made
- AJ Long capture = 24 representative pages (template coverage), not all 1,018 — reviewer-approved as "acceptable for design benchmark"
- S&H taxonomy archives (category/author) deliberately excluded with justification — not authored content
- EV Elementor template fragments excluded — not visitor-facing pages
- Wayback recovery best-effort: EV has zero archive history, documented as the fallback record

### Artifacts Produced
- EV `website-archive/old/post-core-30/` — complete capture (screenshots, HTML, CSS, computed-styles, meta, assets, manifest)
- S&H `website-archive/old/post-core-30/` — complete capture (same structure)
- AJ Long `aj-long-teardown/raw/` — benchmark capture (screenshots, HTML, CSS, computed-styles, meta, assets, manifest)
- S&H `old/pre-core-30/wayback-screenshots/` + `wayback-html/` — 4 recovered pages
- S&H `old/pre-core-30/_wayback-recovery.md` — recovery manifest
- Both clients' `website-archive/` folder reorg (3-state model) with 6 updated READMEs
- `ev-sitemap-diff.md`, `sh-sitemap-diff.md` + JSON dumps — sitemap completeness proof
- `url-status-precheck.txt` — 123-URL HTTP status baseline
- `full-site-capture.mjs` + `asset-computed-styles-pass.mjs` — reusable capture scripts

### Key Insights
- **WordPress servers throttle rapid Playwright requests.** S&H's Hostinger server started dropping connections after ~35 pages in quick succession. Fix: 3s inter-page delay + 90s timeout. Pattern candidate for future captures.
- **Google Fonts aren't captured by @font-face CSS reading** — Elementor loads them via `<link>` to fonts.googleapis.com, and cross-origin protection blocks reading the CSS rules. Separate download pass needed (fetch the CSS, parse woff2 URLs, download).
- **Next.js assets need different handling** — AJ Long's images are served via `/_next/image` (optimized), fonts via `/_next/static/media`, JS via `/_next/static/chunks`. The generic asset collector finds fewer because URLs are dynamically constructed. Captured via the supplemental pass.
- **Sitemap diff is essential** — the reviewer caught that the initial "41/41 zero skips" was circular (measured against our own URL list, not the live sitemap). The full sitemap dump + diff proved completeness against the real denominator.
- **The review gate caught real gaps** — assets empty (C-04), computed-styles missing (C-05), manifest naming wrong (C-06), sitemap labels mislabeled (C-09). Without the reviewer, the capture would have shipped incomplete.

### Next Session Should Start With
- [WF-4-R2] is now unblocked — the full EV + AJ Long capture exists as the design target
- Read the WF-4-R2 handoff + run the pre-build-due-diligence-gate checklist with the capture data

### Open Questions For Next Session
- Should the `full-site-capture.mjs` + `asset-computed-styles-pass.mjs` scripts be promoted to a reusable skill? (Pattern candidate noted)
- Should a Wayback recovery step be a standard part of the client onboarding flow? (EV has zero history — early clients may have the same gap)

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
