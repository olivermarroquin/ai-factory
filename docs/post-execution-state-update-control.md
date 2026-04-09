# Post-Execution State Update Control

## Purpose

Post-execution state update control closes the gap between what happened during execution and what the state surface says is true.

Without it, the system can successfully execute work and then silently drift — the objective still points to completed work, the state surface reflects an in-progress or stale phase, and no auditable record exists of what outcome was observed.

Post-execution state update control ensures every execution outcome is acknowledged, recorded, and reflected in state before the system considers an execution cycle closed. It is not a retry mechanism, not an orchestration layer, and not a replacement for Guardian or ECS. It is the discipline that prevents silent drift after execution.

The separation of responsibilities is preserved:

- **Guardian** = validation
- **ECS** = decision
- **policy** = permission
- **entrypoint** = coordination
- **transition command** = phase change
- **post-execution command** = outcome acknowledgment and state surface update

---

## Execution Outcome Types

**Type 1: Execution fully succeeded**
All approved jobs completed. Queue status is `succeeded`. Manifests are written. No partial state exists.

**Type 2: Execution partially succeeded — queue blocked**
One or more jobs completed, then a job was blocked by policy, Guardian, or manifest failure. Queue status is `failed`. Some jobs have `succeeded`, at least one has `failed` or `blocked`. Partial work happened and must be explicitly acknowledged.

**Type 3: Execution failed before work began**
Guardian blocked, ECS failed, or queue-state validation failed before any job ran. No migration work was performed. Queue status was never set to `executing`. The system is in the same state as before execution was attempted.

**Type 4: Execution failed after work began**
At least one job ran. The queue halted mid-run. Queue status is `failed`. Some manifests exist. The system is in a partially-advanced state relative to before execution.

Types 1 and 3 are clean transitions. Types 2 and 4 leave partial state that must be explicitly acknowledged before the system proceeds.

---

## Update Authority

**One authority: explicit operator command.**

The operator invokes the post-execution command after reviewing execution outcomes. No automatic state mutation happens as a side effect of execution completing. Execution records outcomes in artifacts — it does not update the state surface.

The rationale: the system cannot determine whether a partial success is acceptable or requires re-queueing, whether a failure reveals a control gap or was a transient error, or whether the next correct step is another migration run or a return to system-building mode. These judgments require operator context. The post-execution command structures the operator's assertion — it does not replace it.

---

## Post-Execution Preconditions

Before any post-execution state update is allowed, all of the following must be true:

1. **Queue run record exists** — the `queue-runs/<timestamp>_queue-run.json` file referenced in the queue-state must exist and be readable.

2. **Queue-state file is readable and valid JSON** — the same file used during execution.

3. **Queue-state `batch_status` is terminal** — must be `succeeded` or `failed`. Not `approved`, `executing`, or any non-terminal value. No post-execution update is allowed while execution is still in progress or in an ambiguous intermediate state.

4. **Outcome is known and declared** — the operator provides an explicit `--outcome` argument that matches the observed queue-state terminal status. The command validates the two agree before any write occurs.

5. **Guardian passes** — run against the current state before any write. If the system is already in a broken state, post-execution updates must not compound it.

6. **No duplicate outcome record exists for the same queue-state** — before writing anything, the command must check that no outcome record already references the same queue-state file path. If a duplicate is detected, the transition is blocked. Outcome records are write-once per queue-state.

All six preconditions must be satisfied. Failure of any one blocks the update with no file changes.

---

## Update Mechanism

The post-execution command is `ai-factory-record-outcome`, implemented as a Python script (`ai_factory_record_outcome.py`) with a thin bash wrapper. It follows the same pattern as `ai_factory_run.py` and `ai_factory_transition.py`.

**Invocation:**

```
ai-factory-record-outcome --queue-state <path> --outcome succeeded --notes "<text>"
ai-factory-record-outcome --queue-state <path> --outcome failed --notes "<text>"
```

`--outcome` is required. `--notes` is optional operator context recorded in the outcome record.

**Execution sequence:**

1. Read and validate the queue-state file
2. Read and validate the queue run record
3. Verify `batch_status` is terminal and matches declared `--outcome`
4. Verify declared `--outcome` against actual job statuses (see Validation section)
5. Check for existing outcome record for the same queue-state — block if found
6. Run Guardian against current state — block if FAIL
7. Write outcome record to `outcome-records/<timestamp>_outcome.json`
8. Atomically update `system-state/current-system-state.md`:
   - Write new content to a temporary file: `system-state/.current-system-state.md.tmp`
   - Validate the temporary file is non-empty and contains required sections
   - Replace `current-system-state.md` using `os.replace` only after validation passes
   - If validation fails: delete temp file, abort, exit non-zero — `current-system-state.md` is unchanged
9. Re-run Guardian after the write to confirm no inconsistency was introduced
10. Print outcome summary and advisory

The command does not automatically trigger a transition. It records what happened and surfaces the appropriate next step. The operator decides and acts.

**Atomic write is a non-negotiable rule.** The command must never write directly to `system-state/current-system-state.md`. Partial writes to that file are not permitted under any condition.

---

## State Surface Impact

**Files that MAY change:**

- `system-state/current-system-state.md` — updated atomically to reflect the completed execution cycle. Only the execution cycle status section is modified. Overall phase and objective language is not changed by this command.
- `outcome-records/<timestamp>_outcome.json` — new write-once outcome record.

**Files that must NOT be changed by this command:**

- `system-state/current-objective.md` — owned exclusively by `ai-factory-transition`
- `system-state/authoritative-files.md` — not affected by execution outcomes
- Any execution artifact (batch reports, queue runs, manifests) — write-once historical records; this command reads them, never modifies them
- `config/migration-execution-policy.json` — not affected by execution outcomes

**Two-file rule:** the command touches at most two files — `current-system-state.md` (updated) and the outcome record (new). Nothing else.

---

## Validation

Post-execution updates are validated at two points: before the write and after.

**Before the write:**

1. **Declared outcome vs. queue-state terminal status** — `--outcome succeeded` is only accepted if `batch_status == "succeeded"`. `--outcome failed` is only accepted if `batch_status == "failed"`. Any mismatch blocks the update.

2. **Declared outcome vs. actual job statuses** — the declared outcome must be verified against individual job statuses in the queue-state:
   - `--outcome succeeded` requires every job in the `jobs` array to have `status == "succeeded"`. If any job has any other status, the declared outcome is rejected.
   - `--outcome failed` requires at least one job with `status != "succeeded"`. If all jobs show `succeeded` but the batch is declared failed, the declared outcome is rejected.

3. **Duplicate check** — `outcome-records/` is scanned for any existing record referencing the same queue-state file path. If found, the update is blocked.

4. **Pre-write Guardian pass** — full Guardian must pass before any file is written.

**After the write:**

5. **Outcome record exists and is readable** — the written JSON file is confirmed present and parseable after write.

6. **Post-write Guardian pass** — full Guardian is re-run after `current-system-state.md` is replaced. If Guardian fails, the command exits non-zero and explicitly identifies the inconsistency. No rollback is attempted — the operator must inspect and correct.

7. **Temp file cleanup** — if the atomic write succeeded, the temp file was consumed by `os.replace`. If validation failed before replace, the temp file must be deleted before exit.

---

## Failure / Block Conditions

A post-execution update is blocked (no file changes, non-zero exit) if:

- Queue-state file is missing, unreadable, or not valid JSON
- Queue run record is missing or unreadable
- `batch_status` is not terminal (`approved`, `executing`, or absent)
- Declared `--outcome` does not match the observed `batch_status`
- Declared `--outcome` does not match actual job statuses (see Validation)
- Duplicate outcome record detected for the same queue-state path
- Pre-write Guardian fails
- Temp file for `current-system-state.md` cannot be written or validated
- Atomic replace of `current-system-state.md` fails
- Outcome record cannot be written or verified after write
- Post-write Guardian fails — command exits non-zero and instructs operator to inspect

Post-write Guardian failure does not trigger automatic rollback. The command reports the inconsistency and exits. The operator inspects and corrects manually.

---

## Relationship to Transitions

Post-execution state updates and objective transitions are deliberately separated. Neither triggers the other automatically.

**After `succeeded` outcome:**
The command records the outcome and prints an advisory. The operator decides whether to run another migration batch (remaining in migration-execution mode) or transition back to system-building mode. If a transition is wanted, the operator runs `ai-factory-transition --to system-building --reason "..."`. The outcome record is the factual basis for that transition decision.

**After `failed` outcome:**
The command records the outcome and prints an advisory recommending `ai-factory-transition --to system-building`. This is a recommendation, not an automatic action. The operator may choose to investigate and re-run instead. The transition remains explicit and operator-owned.

**No automatic objective switching.** The outcome record is evidence. The transition command is the gate. The two are not wired together in v1 because the system cannot determine whether a failed outcome warrants a mode change or a re-run without operator judgment.

**Transition precondition independence.** `ai-factory-transition` has its own preconditions (Guardian pass, approved jobs in queue-state, declared reason). A clean outcome record provides the operator the factual basis to satisfy those preconditions, but does not unlock or bypass any of them.

---

## Boundaries

In v1, post-execution state update control must NOT:

- Automatically trigger `ai-factory-transition` based on execution outcome
- Re-queue failed jobs or generate new preflight reports
- Modify any execution artifact — batch reports, queue runs, and manifests are read-only historical records
- Evaluate whether the execution outcome was "good enough" — it records what happened, not whether it was acceptable
- Accept a `--force` flag or bypass any precondition
- Modify `current-objective.md` — that file is owned by `ai-factory-transition`
- Accept multiple queue-state files in one invocation
- Produce structured JSON output — plain text only in v1
- Infer the outcome from artifacts without an explicit operator declaration — `--outcome` is always required
- Attempt rollback of any execution artifact or state file
- Automatically advance to a next migration batch
- Interact with Context Engine or Knowledge OS (neither is implemented)
- Support multi-agent delegation

---

## Final Recommendation

Implement `ai-factory-record-outcome` as a Python script (`ai_factory_record_outcome.py`) with a bash wrapper following the exact pattern of the other entrypoint commands.

The script has two required arguments (`--queue-state`, `--outcome`) and one optional argument (`--notes`). No other arguments.

The `current-system-state.md` update is surgical — the command replaces only a clearly delimited execution cycle status block within the file, not the whole file. This minimizes write risk and makes the change reviewable in a diff. The atomic write sequence (temp file → validate → `os.replace`) is mandatory and identical in structure to the atomic write in `ai_factory_transition.py`.

The outcome record in `outcome-records/` is the durable audit trail. Over time it becomes a chronological record of every acknowledged execution cycle — what ran, what the outcome was, what the operator declared, what Guardian said at that moment. This is the minimum viable execution history without a database or external system.

The duplicate-detection rule (no second outcome record for the same queue-state) is what prevents re-acknowledgment of the same batch. Combined with the write-once nature of execution artifacts, this ensures that each queue-state file maps to exactly one acknowledged outcome.

The single governing principle: **execution records its artifacts; the operator acknowledges the outcome; the command records that acknowledgment and updates the state surface to match reality.** No step in that chain is skipped or automated away in v1.
