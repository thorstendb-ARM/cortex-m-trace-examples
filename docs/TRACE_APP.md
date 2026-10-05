# Trace application and workflow

All targets use the shared RTX5 workload. L552's `ULINKplus StackCorruption`
adds one fault-injection thread and selects a dedicated trace profile.
See [Validation](VALIDATION.md)
for measured results and remaining limits; [BUILD.md](BUILD.md) covers build and
board prerequisites, and [DEBUG_PROBES.md](DEBUG_PROBES.md) covers probe selection.

## Signals

| Thread / source | Output | Requested interval | Expected values |
| --- | --- | --- | --- |
| `Sine100ms` / DWT | `g_trace_sine`, signed 32-bit | 100 ms | 20 samples per 2 s sine period, amplitude 1000. |
| `Noise100ms` / DWT | `g_trace_noise`, signed 32-bit | 100 ms | Deterministic xorshift32 noise, -1000 through +1000. |
| `ITM1_200ms` / ITM channel 1 | Binary unsigned 32-bit counter | 200 ms | 0, 1, 2, ...; wraps at `UINT32_MAX`. |

The [DWT workload](../Common/Workloads/dwt_workload.c) uses a sine table beginning
`0, 309, 588, 809, 951, 1000` and noise seed `0x6D2B79F5`; reset repeats both
sequences. Each variable is four-byte aligned with one store per update. A capture
from reset can also contain BSS zero stores before those application updates.

Threads update immediately, then use absolute RTX deadlines with a 1000 Hz tick.
After a missed deadline or debug halt, scheduling restarts without catch-up bursts.
These intervals are application requests; decoded timing must be checked separately.
The privileged ITM thread never waits for a disabled or full port:
`g_trace_itm_counter` advances on every attempt, and `g_trace_itm_dropped` counts
failed attempts. Successful writes do not prove host delivery. ITM1 is binary data,
not console text; `g_app_state` and `g_app_core_clock_hz` support runtime inspection.

The RTX idle thread spins without `WFE`/`WFI`, so most PC samples can be in idle.
PC sampling observes locations periodically; it need not catch each short update function.

## Stack-corruption watch (NUCLEO-L552ZE-Q)

The `ULINKplus StackCorruption` set selects the `StackCorruption` build with
`TRACE_STACK_CORRUPTION=1`. Only this context includes and creates the fourth
thread, `StackCorruption`, from
[`stack_corruption.c`](../Common/Workloads/stack_corruption.c).
Its 256-byte stack is the aligned `g_stack_corruption_stack[64]` array; RTX writes
its `0xE25A2EA5` magic to the first word at the lowest stack address.

After a two-second delay the thread fills a small local array, then uses a
deliberately invalid offset from that array to write `0xDEADC0DE` into the magic
word. The injected store uses integer address arithmetic and a volatile pointer
to target that one word while keeping the live stack pointer within its limits.
The next RTX context switch detects the changed magic and enters the existing
`osRtxErrorNotify` stack-overflow loop. This is an intentional terminal error;
restart the session to repeat it.

The matching
[`ULINKplus StackCorruption` profile](<../.cmsis/Trace+NUCLEO-L552ZE-Q@ULINKplus StackCorruption.ctrace.yml>)
configures a single watch at `g_stack_corruption_stack`, `access: W`, `size: 4`,
`output: PC`. It disables ITM channels and periodic PC sampling, and requests no
timestamps or exception events. DWT synchronization (`16M`, `sync-on-run: true`)
provides the protocol framing needed to decode the short capture. The three
normal workload threads remain present, but their outputs are not selected for
capture.

1. Select `NUCLEO-L552ZE-Q` / `ULINKplus StackCorruption`, build, and regenerate
   the matching trace runtime profile against the `StackCorruption` ELF.
2. Check that the watch resolves to the first stack word and retains `output: PC`.
   Start debugging with ULINK+ and run continuously from `main` for at least
   three seconds, through the two-second injection delay and into the error
   handler. Avoid breakpoints around the store: short breakpoint-to-breakpoint
   runs have lost its PC packet at the capture boundary.
3. Pause to convert the pyOCD SWO recording with ctrace. Inspect
   `.trace/Trace+NUCLEO-L552ZE-Q@ULINKplus StackCorruption.SWO.csv` for the PC of
   the store in `stack_corruption_thread`.

The watch reports every write to that address. A capture from reset can also
contain PCs from BSS initialization and RTX stack initialization; these are not
corruption events. The profile reports writing PCs rather than stored values;
without timestamps, CSV cycle fields do not measure elapsed time.
The verified continuous run captured both the RTX initialization PC and the
corruption-store PC. See [Validation](VALIDATION.md#nucleo-l552ze-q-stackcorruption--2026-10-05)
for the measured result and remaining pause-boundary limitation.

## Stack-magic agent workflow

Invoke `Use $trace-stack-magic-corruption-test` to use the project
[trace-stack-magic-corruption-test skill](../.agents/skills/trace-stack-magic-corruption-test/SKILL.md).
It derives the profile and ELF from the active target set and keeps that
selection. Before running, it checks that the stack-magic watch uses `access: W`,
`size: 4` and `output: PC` and resolves to the intended stack word.

The skill starts debugging, lets the application run, ends the debug session and
waits for final CSV conversion. Its `report_trace.py` helper uses `addr2line`
with the matching ELF to create `.trace/<stem>.SWO.md`, leaving the CSV unchanged.
Every CSV entry gets a section, including entries without a PC. Resolved source
code appears first, followed by `project-relative/file:line`, the original trace
fields and any resolution diagnostics. External Pack paths use `../` relative
to the project root. The agent then reads the surrounding source at the resolved
locations and adds a short explanation per entry, with relevant code context.
It distinguishes initialization from corruption and separates recorded PCs from
values or behavior inferred from the source.

Original RAW/CSV, an ELF snapshot, a manifest and the Markdown report are retained
under `.trace/captures/stack-magic-*`. At the end, the skill automatically opens
the completed report in VS Code. In a headless environment it keeps the report
and reports that opening was unavailable. Later captures replace the current `.trace/`
CSV, so keep the archived result for comparison. The capture-boundary limitations
above still apply.

## Configuration ownership

In filenames below, `[@<set>]` is omitted for an unnamed target set.

| Owner / file | Responsibility |
| --- | --- |
| Shared firmware | Periodic variable updates, nonblocking ITM writes and the optional stack-corruption thread. |
| `Trace.csolution.yml` | Target set, probe, SWD and SWO transport, input/output clocks. |
| `.cmsis/Trace+<target>[@<set>].ctrace.yml` | Editable DWT symbols, ITM channels, PC sampling, timestamps and synchronization. |
| `out/Trace+<target>.cbuild-run.yml` | Generated active-set description: image, debugger and Pack sequences. |
| `.trace/Trace+<target>[@<set>].ctrace-run.yml` | pyTS output: resolved ELF addresses and trace-register settings. |
| `.trace/Trace+<target>[@<set>].SWO.raw` / `.SWO.csv` | Captured bytes and decoded records. |

The debugger owns trace initialization: Pack sequences supply device routing and
clocks, pyOCD supplies standard ITM/TPIU setup in legacy mode, and the generated
profile configures sources. Firmware does not configure comparators, enable ITM,
or initialize trace pins/path.

The regular demo profiles select both DWT variables with `access: W`, `size: 4`, and
`output: value`; ITM mask `0x00000002`; timestamp prescaler 1; and DWT sync `16M`.
Board clocks, SWO rate and per-probe PC periods are listed in
[Debugger profiles](DEBUG_PROBES.md#configured-probes-and-profiles). A clock change
requires matching solution transport and profile timestamp settings, then regeneration.

## Configure and generate trace

This workflow uses the [reference trace-tool versions](BUILD.md#trace-toolchain).
Their development status and source/release links are recorded there.

1. Select the target and available set (`ULINKplus`, `STLink`, or L552's
   `ULINKplus StackCorruption`) in CMSIS
   **Manage Solution**; [build](BUILD.md) the selected image.
2. Enable `vscode-cmsis-debugger.enableTraceGenerationView` in local VS Code
   settings. Open **Trace Generation** and review the matching source `.ctrace.yml`.
   Keep DWT locations as symbol names.
3. Run **CMSIS Debugger: Convert *.ctrace.yml to *.ctrace-run.yml** after every
   build and source-profile change. pyTS uses the active `.cbuild-run.yml` and
   current ELF; relinking can move variables without changing their names.
4. For the regular demo, check the generated profile resolves both symbols as
   signed 32-bit values and includes the intended DWT, ITM, PC, timestamp and
   synchronization settings. For StackCorruption, check the single stack-word
   watch and its writing-PC output as described above.
   Start the matching debugger configuration and inspect the resulting capture.

Equivalent offline generation with the bundled pyTS executable, for example:

```sh
/path/to/pyTS out/Trace+MCBSTM32F400.cbuild-run.yml --format json
```

The `.cbuild-run.yml` filename has no set suffix and represents the active set;
source/generated trace profiles retain `@<set>`. Regenerate each set before its
next capture after an ELF/profile change; see [Switch sets](DEBUG_PROBES.md#switch-sets).

## Automatic CSV conversion in VS Code

With the trace view enabled, pausing, hitting a breakpoint or ending a debug
session triggers CSV conversion when new trace data is available. SWO output is
`.trace/Trace+<target>[@<set>].SWO.csv`; later conversions replace it. CTF export
is not automatic. Manual decoding uses the matching profile beside the RAW:

```sh
/path/to/ctrace .trace -t Trace+MCBSTM32F400 --csv
```

Inspect decoder errors as well as the CSV; apply the checks in
[Validation](VALIDATION.md#stm32-capture-test-scope). Keep RAW/CSV together for diagnosis.
The [stack-magic agent workflow](#stack-magic-agent-workflow) provides a reusable
capture and Markdown source-report workflow for stack-word PC watches.

## Temporary run-description overrides

For a demonstrated missing behavior, use a minimal target-specific override while
retaining the shared firmware and installed Packs as the baseline.

| Correction | Runtime location |
| --- | --- |
| Named CMSIS sequences: `TraceStart`, `TraceCapture`, `TraceFlush`, `TraceStop` | `.cbuild-run.yml` under `debug-sequences`. |
| Resolved register settings | `.ctrace-run.yml` under `ctrace-refs[].regs`. |

Select a fixed `.cbuild-run.yml` explicitly with pyOCD `--cbuild-run` and preserve
or adjust its relative paths. The `.ctrace-run.yml` reader does not execute named
sequences; register corrections must reach the active
`.trace/Trace+<target>[@<set>].ctrace-run.yml`. A separate `fixed.ctrace-run.yml`
is not automatically selected. Keep corrections and rationale under version
control outside `out/` and `.trace/`; regenerate after builds and reapply them to
current ELF addresses. Record tool/Pack versions and hardware results.

The project uses legacy setup: Pack device sequences plus pyOCD ITM/TPIU setup.
`TraceCapture` and `TraceFlush` sequences execute only with
`debug-sequences-conf.trace-setup: full`. Full mode bypasses pyOCD's legacy
ITM/TPIU initialization, so `TraceStart` must supply complete trace setup;
enabling full mode solely to invoke those two sequences is insufficient.
