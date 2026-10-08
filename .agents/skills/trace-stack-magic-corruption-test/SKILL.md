---
name: trace-stack-magic-corruption-test
description: Capture the stack-magic write trace for this project's active CMSIS target set, or analyze an existing CSV without a build or debug session. Resolve recorded PCs with arm-none-eabi-addr2line, and create a separate Markdown report with source text, project-relative locations and source-based explanations, one section per CSV record. Keep the CSV unchanged, create no capture archives or sidecar files, and open the completed report in VS Code. Use to automate the existing StackCorruption experiment; it does not add targets or invent a missing trace watch.
---

# Trace Stack Magic corruption test

Run this repository's existing stack-corruption experiment for the **currently
selected target and set**, or create a report from an existing CSV. Deliver a
separate Markdown report with one section per CSV record, including legitimate
initialization writes and records without a PC. Never add columns to or rewrite
the CSV.

The **only additional output file** is the Markdown report beside the selected
CSV (normally `.trace/<stem>.SWO.md`). Use existing build/debug outputs in place.
Do not create capture directories, ELF/profile copies, manifests, JSON result files or diagnostic logs. Keep verification state
and tool diagnostics in memory/tool output. Leave existing archives untouched.

The repository root contains `Trace.csolution.yml`. Read the
[stack experiment](../../../docs/TRACE_APP.md#stack-corruption-watch-nucleo-l552ze-q)
and its [validation limits](../../../docs/VALIDATION.md#nucleo-l552ze-q-stackcorruption--2026-10-05)
when preparing a capture. Do not encode the board, probe ID, ELF address or source
line number from a previous run into the workflow.

## Choose the mode

For "only create the MD", "use the existing CSV", "report only" or equivalent,
use **report-only mode** below. An unspecified mode runs the full capture workflow.
Both modes explain and automatically open the report.

## Report only from an existing CSV

1. Use the CSV named by the user; otherwise select the existing CSV for the active
   target/set. Read local solution/runtime metadata to identify it. Require a
   completed, stable CSV; do not change a running debug session to obtain one.
2. Find the ELF associated with that CSV, preferably supplied by the user or
   referenced by its existing runtime profile. Use the source tree and
   `arm-none-eabi-addr2line` as in the full workflow. Do not choose an arbitrary
   newer build; if the association is ambiguous, ask which ELF belongs to the CSV.
   Successful address resolution alone does not prove the ELF matches the capture.
3. Set `trace_report` to the CSV path with its `.csv` suffix replaced by `.md`.
   Run the helper on these existing files:

   ```sh
   python3 .agents/skills/trace-stack-magic-corruption-test/scripts/report_trace.py \
     --report-only --csv "$trace_csv" --elf "$trace_elf" \
     --addr2line "$trace_addr2line" --source-root "$trace_workspace" \
     --output "$trace_report"
   ```

   If verified state from that exact capture is still available in memory, pass
   it with `--capture-state "$trace_state"`. Otherwise the report identifies its
   ELF/source association as unverified and displays current source with that
   limitation. Never manufacture capture-time verification from current hashes.
4. Continue at **Report content and explanation** below. Retain the provenance
   note when adding code context and explanations. Only summarize findings in
   the supplied capture; do not claim a new successful hardware test.

This mode does not build, flash, start/stop debugging, generate trace profiles,
convert RAW, or run `capture_state.py`. It needs no connected board and does not
require the current trace profile still to have the original watch enabled.
Only the Markdown report is written; the CSV, ELF and source remain unchanged.

## Bind the active target and verify its trace (full capture)

Use `cmsis-debug-live` for hardware operations and the CMSIS Developer Assistant
MCP tools for build/load/debug. Select this repository's VS Code window with
`list_debug_windows` / `select_debug_window`; leave other projects' sessions alone.
Apply the user's physical probe-selection rules. Allow up to **10 attempts**
per failing CMSIS operation, correcting the cause between attempts. After ten
failures, call `get_session_status` and `get_recent_problems`, then stop and
explain the required VS Code action; do not substitute shell board access.
Shell helpers below operate on local files only. This workflow intentionally
uses the user-requested `arm-none-eabi-addr2line` for offline PC resolution.

1. Read `.vscode/cmsis.json` (`activeSolution`, `activeTarget`) and
   `Trace.cbuild-idx.yml` (`build-idx.target`, `cbuild-run`). The selected target
   includes `@<set>` for a named set. Build **that selection** with
   `cmsis_action build`, using `check-cmsis-environment` when a build environment
   check is needed. If this project already has a debug session, check its state
   and end it before rebuilding/starting a fresh capture. Do not switch to the
   example L552 set merely because another selected set has no magic watch.
2. From the indexed `.cbuild-run.yml`, read `solution`, `target-type`, `target-set`,
   `output` and `debugger.trace`. Require agreement with the active selection.
   Resolve the one symbol-bearing ELF from its `output` entry, relative to the
   run file. For multiple images/cores, require an unambiguous association with
   the watch before continuing. Require SWO file capture.
3. Form the profile stem from the solution name, target and optional set:
   `Trace+<target>[@<set>]`. Read `.cmsis/<stem>.ctrace.yml`. It must contain a data
   watch for `g_stack_corruption_stack` (or its first element), with a write access,
   **four-byte size** and **PC output**. Check this against the workload's actual
   RTX stack storage, not a similarly named spare canary. If missing or incompatible,
   report the exact active set and deficiency; do not enable a different demo.
4. Regenerate with the installed CMSIS Debugger's pyTS against the indexed run
   file. Check its missing-symbol list and `.trace/<stem>.ctrace-run.yml`: the
   magic watch resolves to the first stack word, has size four and PC output, and
   its `symbol-file` is the selected ELF. Resolve the corresponding DWT index for
   later CSV checks. Retain protocol synchronization; this experiment needs
   `sync-on-run` to decode its short capture. Other demo sources should remain
   disabled in the StackCorruption profile. Do not change Pack/pyOCD sources.
5. Find `arm-none-eabi-addr2line` beside the selected GCC compiler (the active
   `compile_commands.json` records its path), from the tools environment, or on
   the activated PATH. Do not install a compiler. Missing tools are a setup issue.

## Prepare and record

The helpers require Python 3 and only its standard library. Use arguments, not
shell interpolation of untrusted YAML/CSV contents. Quote paths containing spaces.

Run `scripts/capture_state.py prepare` with the resolved values:

```sh
python3 .agents/skills/trace-stack-magic-corruption-test/scripts/capture_state.py prepare \
  --workspace "$trace_workspace" --target "$trace_target" \
  --elf "$trace_elf" --compile-commands "$trace_compile_commands" \
  --run-description "$trace_run" --source-profile "$trace_profile" \
  --runtime-profile "$trace_runtime_profile" \
  --raw "$trace_raw" --csv "$trace_csv"
```

Keep the returned JSON as `trace_state` in memory across tool calls. It records
the selected ELF path, input/source hashes and capture start time without writing
files. Pass that JSON directly to the following helpers; never save it to disk.
Prepare again after any build, profile or target change. Keep sources unchanged
between the build, capture and report; if they change, rebuild and capture again.

- Check `get_session_status` and `list_breakpoints`. A clean capture must pass the
  corruption store without breakpoints or single stepping. Remove only this
  workflow's own breakpoints; if user breakpoints interrupt the path, arrange for
  them to be disabled/restored rather than silently clearing all breakpoints.
- Use `cmsis_action load_and_debug` with the exact active target/set. Confirm the
  image/probe match. From the initial halt at `main`, use `continue_execution`
  with a **4500 ms** wait for the current two-second workload. A `running` result
  is expected. If the workload delay changes, use its delay plus sufficient drain
  time instead. If execution stops early, investigate before calling it a capture.
- Pause after the uninterrupted run, then **end the debug session** with
  `stop_debugging`. The pause lets the existing IDE workflow convert the drained
  RAW; ending the session fixes the final input for the report.
  This experiment normally ends in `osRtxErrorNotify` after the deliberate error.
- Run `capture_state.py verify --state-json "$trace_state"`. It waits up to
  15 seconds for a fresh, nonempty, stable RAW/CSV pair and rechecks the inputs.
  Replace the in-memory `trace_state` with its returned JSON, which includes the
  final RAW/CSV hashes. Do not accept a previous CSV because it exists. Inspect
  decoder diagnostics in tool output. If automatic conversion is missing or
  stale, run the installed `ctrace` offline on this exact stem and final RAW/profile,
  then verify again; report that manual fallback was used. Do not save check logs.

## Resolve PCs and write the Markdown report

After the session and final conversion have ended, run:

```sh
python3 .agents/skills/trace-stack-magic-corruption-test/scripts/report_trace.py \
  --csv "$trace_csv" --elf "$trace_elf" \
  --addr2line "$trace_addr2line" --source-root "$trace_workspace" \
  --capture-state "$trace_state" --output "$trace_report"
```

Set `trace_report` to `.trace/<stem>.SWO.md`; by default the helper replaces the
input CSV's `.csv` suffix with `.md`. Use the ELF selected before this capture.
The helper checks its hash and the final CSV hash against the in-memory state,
batches distinct PCs through `addr2line`, and writes only the Markdown file.
**Leave CSV bytes, columns, cells and row order unchanged.** Use trace PCs exactly
as recorded; do not subtract a Thumb or return-address offset. If the matching
ELF or source is no longer available, report that limitation instead of guessing.

## Report content and explanation

Create exactly one `## Entry N` section per CSV data record, in original order,
including duplicates, decoder diagnostics and records without a PC. The header
is not an entry. For a resolved PC, show the source code first and the location
next, for example:

````markdown
## Entry 2

```c
*bad_destination = 0xDEADC0DEU;
```

Location: `Common/Workloads/stack_corruption.c:39`
````

Follow this with the record's trace fields, including its PC and any original
notes. Make all source paths project-relative, including `../` for external
Pack files. Pair each inline frame's source and location within the same entry.
For missing/invalid PCs or unavailable/changed source text, state the actual
status and retain the original CSV information; never invent a source line.
Use capture-time source hashes when available; an uncaptured inline header can
have a valid DWARF location without verified source text. In report-only mode,
current source may be shown with an explicit unverified-source note; known hash
mismatches must still be reported and their text omitted. Repeating the helper
with unchanged inputs must produce identical base Markdown.

After the helper finishes, **explain what happened** in the report. Use its
`addr2line` results (or call that tool again with the selected ELF) to locate the
actual functions, then read the surrounding source, relevant callers and symbol
or constant definitions. Check available source hashes against the capture.
Add a compact context excerpt when needed to explain the resolved store, retaining
the exact recorded source line and its location. Use the matching code-fence
language, including `asm` for assembly. Add one to three explanatory sentences to
each entry and a brief overall interpretation before the entries. Preserve the
entry count/order and original trace fields; leave the CSV untouched.

Distinguish normal startup/RTX initialization from deliberate corruption using
the source context, never fixed PC addresses, row numbers or a matching literal
alone. Separate recorded evidence from source-based interpretation: PC-only
trace identifies writes but does not directly record their stored values or
elapsed time. Explain subsequent stack checking from its actual code; claim an
observed error-handler stop only when this run has corresponding debugger
inspection. Mark missing evidence or unresolved entries explicitly. Do not
rerun the helper after adding explanations, because it replaces the report;
open the explained report as the final artifact.

Check that the report section count equals the CSV record count, and that the
CSV hash is unchanged. Report-only mode retains unresolved/incomplete entries
and explains their limitations; it does not start a capture to fill missing data.
For a successful full capture test, the magic-watch DWT index must contain a PC
resolving to the corruption store, without decoder errors. An initialization
write remains a separate entry and is not evidence of corruption by itself.
Do not treat cycle fields as elapsed time when timestamps are disabled.

**Automatically open the newly generated report in VS Code before the
final response**, including reports that document unresolved entries. Use a
workspace-targeted editor tool if available; otherwise use the installed VS Code
CLI with both absolute paths:

```sh
code "$trace_workspace" "$trace_report"
```

Passing the project folder lets VS Code select its existing workspace window.
Respect its Markdown editor/preview association. Do not force a new/reused window
or use `--wait`, which would block until the user closes the report. Open only the
report generated and checked in this invocation, never a stale file after generation
failed. If no GUI/editor is available (for example in CI), keep the report and
state that it could not be opened; do not rerun the capture for this reason.

Finish with the mode, identified target/set or ELF, report result, resolved store
location when present, and links to the report and original CSV. Include material
decoder/capture limitations. Do not restart debugging after reporting. Later captures replace
the current files; this skill keeps no archive.
