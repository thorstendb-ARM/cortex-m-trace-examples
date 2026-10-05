---
name: trace-stack-magic-corruption-test
description: Capture the stack-magic write trace for this project's active CMSIS target set, resolve recorded PCs with arm-none-eabi-addr2line, and create a separate Markdown report with source text, project-relative locations and source-based explanations, one section per CSV record. Keep the CSV unchanged and open the completed report in VS Code. Use to automate the existing StackCorruption experiment; it does not add targets or invent a missing trace watch.
---

# Trace Stack Magic corruption test

Run this repository's existing stack-corruption experiment for the **currently
selected target and set**. Deliver the original SWO CSV and a separate Markdown
report with one section per CSV record, including legitimate initialization writes
and records without a PC. Never add columns to or rewrite the CSV.

The repository root contains `Trace.csolution.yml`. Read the
[stack experiment](../../../docs/TRACE_APP.md#stack-corruption-watch-nucleo-l552ze-q)
and its [validation limits](../../../docs/VALIDATION.md#nucleo-l552ze-q-stackcorruption--2026-10-05)
when preparing a capture. Do not encode the board, probe ID, ELF address or source
line number from a previous run into the workflow.

## Bind the active target and verify its trace

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

Run `scripts/capture_manifest.py prepare` with the resolved values:

```sh
python3 .agents/skills/trace-stack-magic-corruption-test/scripts/capture_manifest.py prepare \
  --workspace "$trace_workspace" --target "$trace_target" \
  --elf "$trace_elf" --compile-commands "$trace_compile_commands" \
  --run-description "$trace_run" --source-profile "$trace_profile" \
  --runtime-profile "$trace_runtime_profile" \
  --raw "$trace_raw" --csv "$trace_csv"
```

The returned manifest is in a unique `.trace/captures/stack-magic-*` directory.
It records the exact ELF snapshot, profile hashes, compilation-source hashes and
capture start time. Keep this manifest path for verification and the report.
Prepare again after any build, profile or target change.

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
- Run `capture_manifest.py verify --manifest "$trace_manifest"`. It waits up to
  15 seconds for a fresh, nonempty, stable RAW/CSV pair and saves the unannotated
  capture beside the manifest. Do not accept a previous CSV because it exists.
  Inspect decoder diagnostics. If automatic conversion is missing or stale,
  run the installed `ctrace` offline on this exact stem and final RAW/profile,
  then verify again; report that manual fallback was used.

## Resolve PCs and write the Markdown report

After the session and final conversion have ended, run:

```sh
python3 .agents/skills/trace-stack-magic-corruption-test/scripts/report_trace.py \
  --csv "$trace_csv" --elf "$trace_snapshot_elf" \
  --addr2line "$trace_addr2line" --source-root "$trace_workspace" \
  --source-manifest "$trace_manifest" --output "$trace_report"
```

Set `trace_report` to `.trace/<stem>.SWO.md`; by default the helper replaces the
input CSV's `.csv` suffix with `.md`. Take `trace_snapshot_elf` from the manifest's
`elf`, not whichever build is now newest. The helper checks ELF and captured CSV
hashes, batches distinct PCs through `addr2line`, and writes only the Markdown
file atomically. **Leave CSV bytes, columns, cells and row order unchanged.**
Use trace PCs exactly as recorded; do not subtract a Thumb or return-address
offset. If an old capture was enriched by the previous skill version, use its
archived original CSV and matching manifest, without rewriting the current CSV.

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
Verify source text against the captured compilation inputs; an uncaptured inline
header can have a valid DWARF location without verified source text. Repeating
the helper with unchanged inputs must produce identical base Markdown.

After the helper finishes, **explain what happened** in the report. Use its
`addr2line` results (or call that tool again with the captured ELF) to locate the
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
archive and open the explained report as the final artifact.

Check that the report section count equals the CSV record count, and that the
CSV hash is unchanged. The magic-watch DWT index must contain a PC resolving to
the corruption store. An initialization write is expected and remains a separate
entry; it is not evidence of corruption by itself. A missing corruption PC,
decoder errors or unresolved corruption location prevents a successful end-to-end
result. Do not treat cycle fields as elapsed time when timestamps are disabled.

Copy the Markdown report beside the manifest; retain original RAW/CSV and ELF
there. **Automatically open the newly generated report in VS Code before the
final response**, including reports that document unresolved entries. Use a
workspace-targeted editor tool if available; otherwise use the installed VS Code
CLI with both absolute paths:

```sh
code "$trace_workspace" "$trace_report"
```

Passing the project folder lets VS Code select its existing workspace window.
Respect its Markdown editor/preview association. Do not force a new/reused window
or use `--wait`, which would block until the user closes the report. Open only the
report generated and verified by this run, never a stale file after generation
failed. If no GUI/editor is available (for example in CI), keep the report and
state that it could not be opened; do not rerun the capture for this reason.

Finish with the active target/set, capture/report result, resolved store location,
and links to the report, original CSV and capture directory. Include material
decoder/capture limitations. Do not restart debugging after reporting; a later
capture replaces current files but the archived report remains available.
