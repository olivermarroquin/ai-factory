# Strategic Context Files

These files are the persistent strategic memory for the AI operating system. They solve the problem of context loss across sessions (both Claude Code sessions and Claude.ai chat sessions).

## Files In This Directory

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `00_who-i-am.md` | Who Oliver is, principles, current capability level, tools in use | Monthly or when tools/principles change |
| `01_current-strategy.md` | Active strategy, locked decisions, open decisions, capability roadmap | Weekly or when strategy shifts |
| `02_current-focus.md` | What's in progress this week, what's next, what NOT to work on | Daily (at end of work session) |
| `03_session-log.md` | Append-only history of all work sessions | After every session (append only, never delete) |
| `04_vision-bridge.md` | Full vision, capability ladder, major features timeline, references to specs | Monthly or when vision evolves |
| `05_active-references.md` | Which detailed spec files matter for current work | When focus shifts to new phase |

## How To Use

### Starting a Claude Code session in VS Code
Tell Claude Code at the start of each session:
```
Read these files, then continue from the current objective:
- ai-factory/system-state/strategic/00_who-i-am.md
- ai-factory/system-state/strategic/01_current-strategy.md
- ai-factory/system-state/strategic/02_current-focus.md
- ai-factory/system-state/strategic/05_active-references.md
- Last entry in ai-factory/system-state/strategic/03_session-log.md
```

(Or add that instruction to `resume-saas/CLAUDE.md` so it's automatic.)

### Starting a new Claude.ai chat in the project
Files are uploaded as Claude Project knowledge. Just say:
```
Continue from current strategic context. Read the strategic files and the 
latest session-log entry, then tell me where we left off.
```

### Strategic planning session
Additionally read `04_vision-bridge.md` and any specs listed in `05_active-references.md`.

### At end of every work session (2-3 minutes)
1. Update `02_current-focus.md` — mark completed items, update next items
2. Append new entry to `03_session-log.md` — what happened, decisions, next
3. Commit to git

### Weekly review (10 minutes)
1. Review `01_current-strategy.md` — update if strategy has shifted
2. Review `05_active-references.md` — update which specs are active
3. Scan `04_vision-bridge.md` — verify current work still aligns with north star
4. Run self-awareness checkpoints from `04_vision-bridge.md`

## Design Principles

- **Plain markdown** — no tooling dependency, future-proof
- **Append-only session log** — never lose history
- **Layered context** — light daily files, deep vision file separately
- **Filter over dump** — `05_active-references.md` prevents spec overload
- **Git-versioned** — every strategic decision has a history

## Relationship to Other System State

This directory is alongside (not replacing) the existing operational state:
- `ai-factory/system-state/current-system-state.md` — Operational state (migrations)
- `ai-factory/system-state/current-objective.md` — Current migration objective
- `ai-factory/system-state/authoritative-files.md` — Source-of-truth file list
- `ai-factory/system-state/strategic/` — **This directory: strategic layer above operational**

When the operator tool is eventually expanded (after resume-saas ships), it should read from both `system-state/` (operational) and `system-state/strategic/` (strategic) to produce a unified picture of where the system is.
