---
name: add-trace-board
description: Add a board to this repository's Cortex-M trace demo, including its CMSIS target, local board layer, startup and debugger/trace profiles. Use when a user asks to add a board; obtain its name and debugger from the request or ask for missing inputs, then follow docs/DESIGN.md.
---

# Add a trace board

Extend the existing trace demo with a working board target. Read
[DESIGN.md](../../../docs/DESIGN.md) first: it is the project design reference.
Keep the common CProject, RTX5 application and workload; place hardware-specific
changes in the new board layer. Explicit user requirements take precedence;
explain any necessary departure from the design before changing that design.

Paths below are relative to the repository root containing `Trace.csolution.yml`.
Read the solution, the CProject and a suitable existing `Board/*/Board.clayer.yml`
before editing. Use [BUILD.md](../../../docs/BUILD.md),
[DEBUG_PROBES.md](../../../docs/DEBUG_PROBES.md) and
[TRACE_APP.md](../../../docs/TRACE_APP.md) for current commands and conventions.
CMSIS assistant tools and skills can help when available; this workflow also
works with CMSIS-Toolbox, vendor documentation and the repository files alone.

## Establish the board and debugger

- Take the board name and requested debugger(s) from the current request and
  conversation. Ask only for missing inputs, together if both are missing:
  "Which board should be added, and which debugger will you use?"
  Accept ULINK+ / ULINKplus and ST-Link / STLink as equivalent input names.
- Derive compiler, RTOS, layer strategy and trace workload from the project.
  Ask further questions only when evidence cannot resolve an important choice,
  such as an ambiguous MCU variant, selected core or physical connection.
- If the board or debugger set already exists, reuse or complete it instead of
  creating a duplicate target. Add only the requested debugger profiles.
- Resolve the exact fitted MCU, CMSIS device/processor identifier and support
  pack from vendor board documentation and the CMSIS catalog/PDSC. Check the
  physical revision when it affects wiring or initialization. A missing BSP
  does not prevent the project's device-based local layer.
- Verify internal Flash/SRAM, startup/reset clock, power/security prerequisites,
  SWD access, SWO routing and pyOCD support for the requested probe/device.
  Confirm the two DWT data sources, ITM channel 1 and PC sampling are supported;
  coupled DWT comparators can require more than two hardware units.
  Use pack documentation tools when available, otherwise official vendor/Arm
  documentation. Record relevant source links in the board documentation.
- If essential support or hardware facts are missing, state the specific gap,
  continue independent work, and ask only for the unresolved information or
  scope decision. Do not invent support, silently substitute a debugger or
  reduce the trace workload to make a target appear complete.

## Add the target and board layer

Verify the installed build environment against `vcpkg-configuration.json` and
BUILD.md. Use the existing compiler and pinned dependencies. Install missing
required packs through the normal CMSIS workflow; do not upgrade unrelated packs.

Create `Board/<board>/` following the closest compatible local layer:

| File | Required content |
| --- | --- |
| `Board.clayer.yml` | Board layer type, exact device applicability, pinned DFP, device defines/header, startup/system sources and linker configuration |
| `main.c` | `target_init()` followed by the shared `app_main()` |
| `target.c` | Required board adaptation, `SystemCoreClockUpdate()` and `target_core_clock_hz()`; no trace initialization |
| `regions.h` | Verified internal Flash/SRAM and stack/heap settings matching DESIGN.md |
| `README.md` | Device, dependencies, memory/clock choices and essential power/security/wiring prerequisites |

Select exactly one device startup and system implementation. Reuse compatible
vendor CMSIS sources already present. For STM32, import missing files from the
recorded standalone CMSIS-device commit; update
[ThirdParty/ST/sources.json](../../../ThirdParty/ST/sources.json) with paths,
hashes and sizes and retain licenses. Follow the
[third-party source policy](../../../ThirdParty/README.md) for new families;
for other vendors use suitable pack or standalone CMSIS sources and equivalent
provenance. Do not add CubeMX, HAL/LL, BSP libraries or a full vendor SDK dependency.
A DFP need not contain startup/headers: inspect its contents instead of selecting
a generator-backed `Device:Startup` component by assumption.

Check vector placement, C runtime initialization and the startup/linker symbol
contract before reusing `Board/Support/gcc_linker_script.ld.src`; it currently
adapts ST GNU startup. Keep RTX exception handlers and the shared application
intact. Verify available RAM against the shared RTX configuration. Document
required TrustZone/option-byte or power-supply state; do not provision option
bytes or copy another board's power settings as part of ordinary target creation.

Append a target to `Trace.csolution.yml` with its exact `device:` and
`Board-Layer: $SolutionDir()$/Board/<board>/Board.clayer.yml`. Reuse
`TraceDemo.Debug` and the existing CProject layer selection. Keep DFP dependencies
in the layer and update `Trace.cbuild-pack.yml` through CMSIS tooling.

## Add debugger and trace configuration

Use named `ULINKplus` and/or `STLink` target sets for the requested probes, with
`ULINKplus@pyOCD` and `ST-Link@pyOCD` respectively. For another requested probe,
verify its tool identifier and SWO support first. Omit `probe-id` for automatic
selection. Each set references the same `TraceDemo.Debug` image.

Configure SWD and SWO clocks from the verified hardware and probe capabilities;
keep solution transport clocks and profile timestamps consistent. Existing
profiles are a starting point, not evidence that an unknown board supports those
rates. Obtain the Pack's `.dbgconf` defaults and retain their base files when
CMSIS generates them.

Create `.cmsis/Trace+<target>@<set>.ctrace.yml` for each named set, following
TRACE_APP.md. Use `g_trace_sine` and `g_trace_noise` symbol names, ITM channel 1,
PC sampling, timestamps and synchronization. Keep source symbols independent of
DWT comparator allocation; pyTS resolves ELF addresses and hardware assignments.
Use the supported installed schema; do not rename trace keys during board work.

Trace initialization remains in Pack sequences, pyOCD and generated runtime
configuration. For missing behavior, follow the
[override workflow](../../../docs/TRACE_APP.md#temporary-run-description-overrides).
Do not patch installed Packs or add firmware trace setup as a board workaround.

## Validate and document

- Build each new target/set using the BUILD.md workflow, including Pack resolution
  and RTE generation as needed. Check one linked startup/main, memory fit and
  both watched symbols. A template or successful YAML parse is not a build result.
- Generate trace runtime configuration from the current ELF with the installed
  pyTS workflow. `out/Trace+<target>.cbuild-run.yml` has no set suffix and describes
  the active set. Source profiles and generated `.trace/` files for named sets
  include `@<set>`; regenerate each requested set before its capture.
- Rebuild affected existing targets if shared sources, linker code or dependencies
  changed. Preserve unrelated target settings and active debug sessions.
- Hardware connection is not required to finish implementation/build checks.
  If live testing is requested and the board is available, identify the intended
  board/probe before loading or debugging and use the checks in
  [VALIDATION.md](../../../docs/VALIDATION.md). Inspect recording integrity as
  well as automatic CSV creation at pause/end. Never infer a hardware PASS from
  a build or a CSV file alone.
- Update README board counts/tables, [BOARD_SUPPORT.md](../../../docs/BOARD_SUPPORT.md)
  and DEBUG_PROBES.md. Add only applicable connector/jumper information to
  [ST_BOARD_BRINGUP.md](../../../docs/ST_BOARD_BRINGUP.md). Keep hardware results
  in the single VALIDATION.md; mark untested entries as such and do not extend
  historical PASS claims to the new board. Keep DESIGN.md as the reference,
  updating current inventory statements only where needed.
- Keep generated output, all `.trace/` content, probe serials and host-specific
  paths out of versioned files. Do not create additional validation documents.

Report the board/device, debugger sets, implemented files, build and trace-profile
checks, and any missing prerequisites. Distinguish implementation complete,
build verified and hardware/trace verified. State how to select the new target
and set in CMSIS Manage Solution. If hardware was unavailable, name the remaining
live checks without claiming the board has passed them.
