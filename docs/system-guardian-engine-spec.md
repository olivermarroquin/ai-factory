# System Guardian Engine Spec

## Purpose

The System Guardian engine runs all four concrete Guardian checks in sequence and aggregates their results into a single JSON report. It does not recompute or reinterpret check logic — it delegates entirely to the individual check scripts via subprocess and combines their outputs.

---

## Version

System Guardian Engine v1.

---

## Execution Model

```
run_guardian.py
  → subprocess: check_stale_state.py        → JSON result
  → subprocess: check_ecs_consistency.py    → JSON result
  → subprocess: check_forbidden_transition.py → JSON result
  → subprocess: check_missing_artifact.py   → JSON result
  → aggregate all four results
  → emit single combined JSON to stdout
```

Each check is run to completion before the next begins. All checks are always run regardless of intermediate failures — results are aggregated, not short-circuited.

If any check subprocess exits non-zero, the engine prints an error to stderr and exits non-zero immediately. A check that cannot produce output is a hard failure; subsequent checks are not run in that case.

---

## Inputs

The engine takes no direct file inputs. All state file reading is performed by the individual check scripts. The engine only invokes the scripts and reads their stdout.

| Script | What it checks |
|---|---|
| `tools/guardian/check_stale_state.py` | Stale steps in Immediate Next Steps |
| `tools/guardian/check_ecs_consistency.py` | Agreement between ECS surfaces and written state |
| `tools/guardian/check_forbidden_transition.py` | Forbidden items in Immediate Next Steps |
| `tools/guardian/check_missing_artifact.py` | Missing artifacts for claimed-complete control layers |

---

## Aggregation Rules

1. Run each check via `subprocess.run([sys.executable, <script_path>])`.
2. If a check exits non-zero: print `ERROR: CHECK_FAILED: <script name> exited <code>: <stderr snippet>` to stderr and exit non-zero. Do not produce JSON output.
3. If a check exits zero but its stdout is not valid JSON: print `ERROR: CHECK_INVALID_JSON: <script name>` to stderr and exit non-zero.
4. If a check's JSON is missing the `status` or `check_name` fields: print `ERROR: CHECK_MISSING_FIELD: <field> in <script name>` to stderr and exit non-zero.
5. After all four checks complete successfully: aggregate into the output format below.
6. Overall `status` = `"FAIL"` if any check's `status` is `"FAIL"`; `"PASS"` if all are `"PASS"`.
7. `failures` = list of `check_name` values from checks whose `status` is `"FAIL"`.

---

## Pass / Fail Rules

| Verdict | Condition |
|---|---|
| `PASS` | All four checks return `status: "PASS"` |
| `FAIL` | One or more checks return `status: "FAIL"` |

A subprocess failure (non-zero exit) is not a `FAIL` verdict — it is a hard error that prevents the engine from producing any output.

---

## Failure Behavior

| Condition | Behavior |
|---|---|
| Check subprocess exits non-zero | `ERROR: CHECK_FAILED: <script name> exited <code>: <stderr>` to stderr; engine exits non-zero; no JSON emitted |
| Check stdout is not valid JSON | `ERROR: CHECK_INVALID_JSON: <script name>` to stderr; engine exits non-zero; no JSON emitted |
| Check JSON missing `status` or `check_name` | `ERROR: CHECK_MISSING_FIELD: <field> in <script name>` to stderr; engine exits non-zero; no JSON emitted |

---

## JSON Output Contract

A single JSON object printed to stdout on successful aggregation of all four checks.

```json
{
  "status": "PASS",
  "engine": "system_guardian_mvp",
  "checks": [
    {
      "name": "<check_name from individual check output>",
      "status": "PASS",
      "source": "<repo-relative script path>",
      "result": { "...full JSON object from that check..." }
    }
  ],
  "failures": []
}
```

Field definitions:

| Field | Always present | Value |
|---|---|---|
| `status` | Yes | `"PASS"` or `"FAIL"` |
| `engine` | Yes | Always `"system_guardian_mvp"` |
| `checks` | Yes | One entry per check script, in execution order |
| `checks[].name` | Yes | `check_name` field from the individual check's JSON output |
| `checks[].status` | Yes | `status` field from the individual check's JSON output |
| `checks[].source` | Yes | Repo-relative path of the script that produced this result |
| `checks[].result` | Yes | The full parsed JSON object returned by the check script |
| `failures` | Yes | List of `check_name` values where `status` is `"FAIL"`; empty list if none |

---

## Limitations

- The engine does not validate that individual check results are internally correct — it trusts each script's output.
- Check execution order is fixed: stale state → ECS consistency → forbidden transition → missing artifact.
- If a check subprocess cannot be launched (e.g., script file missing), the engine exits non-zero with a clear error. It does not attempt to continue.
- The engine does not retry failed subprocesses.
- Pass/fail verdict of the engine is derived solely from the `status` fields of the four check outputs. It does not inspect sub-check details.

---

## What The Engine Is NOT Allowed To Do

- Recompute or reinterpret any check's logic internally
- Skip any of the four checks
- Short-circuit on the first failure (all checks always run unless a subprocess error occurs)
- Emit a `PASS` verdict if any check returns `FAIL`
- Modify any file
- Use external libraries
- Perform semantic interpretation of check results
