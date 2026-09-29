# Trace application and workflow

All targets use the shared RTX5 workload. See [Validation](VALIDATION.md)
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

## Configuration ownership

In filenames below, `[@<set>]` is omitted for an unnamed target set.

| Owner / file | Responsibility |
| --- | --- |
| Shared firmware | Periodic variable updates and nonblocking ITM writes. |
| `Trace.csolution.yml` | Target set, probe, SWD and SWO transport, input/output clocks. |
| `.cmsis/Trace+<target>[@<set>].ctrace.yml` | Editable DWT symbols, ITM channels, PC sampling, timestamps and synchronization. |
| `out/Trace+<target>.cbuild-run.yml` | Generated active-set description: image, debugger and Pack sequences. |
| `.trace/Trace+<target>[@<set>].ctrace-run.yml` | pyTS output: resolved ELF addresses and trace-register settings. |
| `.trace/Trace+<target>[@<set>].SWO.raw` / `.SWO.csv` | Captured bytes and decoded records. |

The debugger owns trace initialization: Pack sequences supply device routing and
clocks, pyOCD supplies standard ITM/TPIU setup in legacy mode, and the generated
profile configures sources. Firmware does not configure comparators, enable ITM,
or initialize trace pins/path.

Current profiles select both DWT variables with `access: W`, `size: 4`, and
`output: value`; ITM mask `0x00000002`; timestamp prescaler 1; and DWT sync `16M`.
Board clocks, SWO rate and per-probe PC periods are listed in
[Debugger profiles](DEBUG_PROBES.md#configured-probes-and-profiles). A clock change
requires matching solution transport and profile timestamp settings, then regeneration.

## Configure and generate trace

This workflow uses the [reference trace-tool versions](BUILD.md#trace-toolchain).
Their development status and source/release links are recorded there.

1. Select the target and, where available, `ULINKplus` or `STLink` in CMSIS
   **Manage Solution**; [build](BUILD.md) the selected image.
2. Enable `vscode-cmsis-debugger.enableTraceGenerationView` in local VS Code
   settings. Open **Trace Generation** and review the matching source `.ctrace.yml`.
   Keep DWT locations as symbol names.
3. Run **CMSIS Debugger: Convert *.ctrace.yml to *.ctrace-run.yml** after every
   build and source-profile change. pyTS uses the active `.cbuild-run.yml` and
   current ELF; relinking can move variables without changing their names.
4. Check the generated profile resolves both symbols as signed 32-bit values and
   includes the intended DWT, ITM, PC, timestamp and synchronization settings.
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
[Validation](VALIDATION.md#test-scope). Keep RAW/CSV together for diagnosis.
The project currently has no reusable automated capture/check runner.

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
