---
name: prepare-ra8p1-trace
description: Prepare this repository's EK-RA8P1 CPU0 debug description and SWO file runtime after the final build or CMSIS refresh, using the pinned debug template and installed pyTS. Does not patch a PDSC or start hardware.
---

# Prepare RA8P1 trace

Apply the temporary CPU0/AP0 and SWO configuration for `EK-RA8P1@ULINKplus`
in the repository containing `Trace.csolution.yml`. Read the
[board procedure](../../../Board/EK-RA8P1/README.md#debug-and-trace-preparation)
for the DFP gap and the [trace workflow](../../../docs/TRACE_APP.md#configure-and-generate-trace)
for normal profile generation. Use file tools; no custom helper or build hook.

## Preflight before changing files

1. Verify this workspace's selected solution/target is `EK-RA8P1@ULINKplus`,
   device `Renesas::R7KA8P1KF:CPU0`, pack `Renesas::RA_DFP@6.6.0` and the normal
   Debug context. Stop on a mismatch; do not switch another target silently.
2. Complete any required build/refresh first through `cmsis_action build` for
   this workspace/target, or the documented `cbuild` command. Require the current
   `out/TraceDemo/EK-RA8P1/Debug/TraceDemo.elf` and generated
   `out/Trace+EK-RA8P1.cbuild-run.yml`. Check the template's pack/image paths and
   resources against that output; report unexpected drift before replacing it.
3. Inspect `.cmsis/Trace+EK-RA8P1@ULINKplus.ctrace.yml` before editing the run
   description. Preserve CPU0 source choices, including custom watches/channels.
   The normal demo uses `g_trace_sine`, `g_trace_noise`, ITM1, PC samples,
   8 MHz timestamps and DWT synchronization. Stop on an active CPU1 setup or an
   incompatible timestamp clock. Plan to remove only disabled CPU1 placeholders:
   pyTS can otherwise emit CPU1 disable register accesses.
   If a matching `~` preview profile could redirect generation, report the
   conflict and stop without changing either profile. Do not replace user
   settings with defaults.

## Prepare and validate

1. Apply the preflighted profile changes: back up before removing disabled CPU1
   placeholders, and preserve every CPU0 setting. If no placeholders exist,
   leave the profile unchanged. Back up the generated run description outside
   the pack and build inputs.
   Apply the versioned [debug template](../../../Board/EK-RA8P1/debug-run.yml)
   with the agent's file tools only if its contents differ. The equivalent
   POSIX command from the repository root is:

   ```sh
   cp Board/EK-RA8P1/debug-run.yml out/Trace+EK-RA8P1.cbuild-run.yml
   ```

   This replaces a generated description, not a pack file. Preserve the vendor
   pack; this skill does not patch a PDSC. Do not add interpreter helpers,
   CMake/Make preparation steps or automatic build hooks.
2. Generate the trace runtime with the installed CMSIS Debugger's bundled pyTS.
   Resolve its executable from the extension or tools configuration; quote it,
   and do not install a separate package or hardcode a host-specific path:

   ```sh
   "$trace_pyts" out/Trace+EK-RA8P1.cbuild-run.yml --format json
   ```

   The UI **Convert *.ctrace.yml to *.ctrace-run.yml** command uses the same
   generator with `--allow-missing`. For either route inspect errors and missing
   symbols explicitly; a successful exit alone is insufficient.
3. Parse the run description through the installed pyOCD `TraceConfig` consumer
   without creating a session/probe. Require one enabled SWO source in `file`
   mode with 1000000 Hz input and 1000000 bit/s output, without ignored-source
   warnings. `mode` and clocks are siblings of the null `swo-uart` key; nesting
   them inside it passes basic YAML/pyTS checks but is ignored by pyOCD.
4. Inspect `.trace/Trace+EK-RA8P1@ULINKplus.ctrace-run.yml` against the selected
   production profile and current ELF: resolve all enabled watches, preserve
   requested ITM/PC/timestamp/sync sources, and require CPU0-only register
   operations including `ctrace-disable`. Disabled CPU1 metadata does not make
   CPU1 register accesses safe. Use the CMSIS structural validator when available;
   its checks cover common structure rather than device behavior.
5. Re-read the files after extension watchers settle. A repeat without another
   build or profile change must preserve the resulting configuration. Compare
   before writing the template again and retain existing backups.

Report preparation and hardware reception separately. Do not flash, reset,
start/stop debugging or open a live trace TCP service. A separately requested
hardware run uses CMSIS tools and normal file capture → automatic CSV conversion
on pause/end. The sequence rejects a conflicting running trace clock before
register writes; end trace and reset the device before changing its clock mode.

Build, refresh or target changes can overwrite the generated description.
Repeat preparation after the last such operation and before Enter Debug. Remove
this skill and template once the native DFP/tool flow has been validated.
