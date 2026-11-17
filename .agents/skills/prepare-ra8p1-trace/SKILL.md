---
name: prepare-ra8p1-trace
description: Prepare this repository's EK-RA8P1 CPU0 debug description and normal SWO trace runtime after a build or CMSIS refresh. Applies the temporary RA_DFP 6.6.0 configuration with CMake and the installed pyTS; does not start a hardware session.
---

# Prepare RA8P1 trace

Apply the temporary CPU0/AP0 and SWO configuration for `EK-RA8P1@ULINKplus`
in the repository containing `Trace.csolution.yml`. Read the
[board procedure](../../../Board/EK-RA8P1/README.md#debug-and-trace-preparation)
for the DFP gap and the [trace workflow](../../../docs/TRACE_APP.md#configure-and-generate-trace)
for normal profile generation. Other targets use their existing setup.

1. Check that the selected solution/target is this repository's
   `EK-RA8P1@ULINKplus`, with `Renesas::R7KA8P1KF:CPU0` and
   `Renesas::RA_DFP@6.6.0`. Do not switch a different active target silently or
   apply this pinned description to another DFP version.
2. Complete any required build/refresh first. Use `cmsis_action build` when
   available, or the documented `cbuild` command in the board procedure.
   Require the current `out/TraceDemo/EK-RA8P1/Debug/TraceDemo.elf` and generated
   `out/Trace+EK-RA8P1.cbuild-run.yml`. Preserve existing source trace settings.
3. From the repository root, apply the versioned description with the existing
   build tool; no custom script or YAML rewrite is needed:

   ```sh
   cmake -E copy_if_different Board/EK-RA8P1/debug-run.yml out/Trace+EK-RA8P1.cbuild-run.yml
   ```

4. Generate the trace runtime from that run description and current ELF using
   the installed CMSIS Debugger's pyTS. Resolve its executable from the installed
   extension or the host's tool configuration; never hardcode a host path or
   install a separate Python package. Quote the resolved executable path:

   ```sh
   "$trace_pyts" out/Trace+EK-RA8P1.cbuild-run.yml --format json
   ```

   The normal **Trace Generation → Convert *.ctrace.yml to *.ctrace-run.yml**
   command is equivalent. If neither route is available, report the missing
   trace tool and stop before claiming preparation succeeded.
5. Check the generated
   `.trace/Trace+EK-RA8P1@ULINKplus.ctrace-run.yml` against the selected source
   profile and current ELF: resolve enabled watches without missing symbols,
   retain the requested ITM/PC/timestamp/sync sources, and require CPU0-only
   register operations. Disabled CPU1 metadata alone is not a register access.
   The standard demo enables `g_trace_sine`, `g_trace_noise`, ITM1, PC samples,
   8 MHz timestamps and DWT synchronization. Require SWO `mode: file` at 1 Mbaud.

Report the prepared target, ELF/profile and generation result. Preparation
does not flash, reset, start/stop debugging or open a live trace TCP service.
For a separately requested hardware run, use the CMSIS tools and the normal
file capture → automatic CSV conversion on pause/end workflow.

A subsequent build, refresh or target change can replace the prepared run
description. Repeat the copy and trace generation after the last such operation
and before Enter Debug. Remove this skill and the template once the DFP/tool
flow supplies the required behavior natively and has been validated.
