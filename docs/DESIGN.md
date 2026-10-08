# Project design and implementation baseline

This document records the agreed requirements and how the project was assembled.
Usage is in [README.md](../README.md);
hardware results and capture limitations are in [Validation](VALIDATION.md).

## Agreed requirements

- Reuse one compact application across Cortex-M4, Cortex-M7 and Cortex-M33 boards.
  Keep device startup, memory layout and hardware adaptation in local board layers.
- Use CMSIS csolution/cproject/clayer, CMSIS-Core and RTX5. Use device Packs for
  device descriptions, SVDs, Flash algorithms and debug/trace sequences.
- Build without CubeMX, HAL/LL, BSP libraries or a complete STM32Cube installation.
  Obtain startup, system and device headers from the standalone ST CMSIS-device
  repositories; retain their provenance and licenses. These sources originate in
  STM32Cube, so the requirement concerns build dependencies, not their origin.
- Run separate sine and deterministic-noise threads at 100 ms and an ITM channel 1
  counter thread at 200 ms. Configure two DWT sources, PC sampling and timestamps
  through the Trace Generation view and `.ctrace.yml`.
- Keep trace initialization in the debugger. Firmware writes the watched variables
  and makes nonblocking ITM writes; it does not enable or configure the trace path.
- Use ULINK+ through pyOCD as the baseline. Provide ST-LINK profiles with a lower
  PC-sampling rate and the same image for that board. Both probe types use
  automatic selection without fixed probe IDs.
- Capture SWO through pyOCD and convert RAW to CSV automatically on debug pause
  or session end in VS Code. Add trace-buffer (TB) scenarios after the required
  target paths and pyOCD functionality are established; TB is not implemented here.
- Use internal Flash/SRAM and the vendor reset-clock baseline. L552 uses one image
  with TrustZone disabled; option-byte provisioning is outside this project.
- Prepare for open-source release: preserve source provenance and license notices;
  exclude build outputs, `.trace/` and machine-specific settings from Git.

The board order is MCBSTM32F400, NUCLEO-L552ZE-Q, NUCLEO-F756ZG,
STM32F429I-DISCO, NUCLEO-F401RE, STM32H7B3I-DK, STM32F4-DISCO (MB997 B-02),
then NUCLEO-F446RE.

## Architecture and ownership

| Element | Responsibility |
| --- | --- |
| `Trace.csolution.yml` | Device-based targets, Debug build, layer selection and debugger sets |
| `Projects/TraceDemo/TraceDemo.cproject.yml` | One application image per selected board; shared sources and CMSIS/RTX components |
| `Board/<board>/Board.clayer.yml` | Device header/startup/system selection, board `main()`, target adaptation and linker regions |
| `Common/App`, `Common/Workloads`, `Common/Trace` | RTX startup, periodic signal generation and nonblocking ITM output |
| `Projects/TraceDemo/RTE/CMSIS` | Shared RTX5 component configuration |
| `ThirdParty/ST`, `Board/Support` | Pinned ST CMSIS sources and shared linker template |
| `.cmsis/*.ctrace.yml` | Editable, symbol-based trace sources; pyTS resolves them against the built ELF |
| `.cmsis/*.dbgconf` | Pack debug/trace variable configuration |
| `out/*.cbuild-run.yml`, `.trace/` | Generated debug/trace runtime files and RAW/CSV captures; excluded from Git |
| `Trace.cbuild-pack.yml`, `vcpkg-configuration.json` | Resolved Pack versions and selected build tools |

Each target sets the `Board-Layer` variable. The CProject includes that layer with
its common sources, producing one linked image with exactly one startup and
`main()`. Layers group reusable implementation and configuration; targets select
hardware. A board layer is not a separately built project and needs no published
Pack or additional BSP connector layer.

The handover is an ordinary C call:

```text
Reset → device SystemInit / C runtime → board main()
      → target_init() → shared app_main() → RTX5 and the three signal threads
```

`target_init()` retains the vendor clock baseline and updates `SystemCoreClock`.
RTX5/CMSIS OS Tick supply SVC, PendSV and SysTick handling. The Trace application
is currently a CProject, not an application clayer. Explicit layer selection and
`target.h`/`app.h` provide the interface; `connections:` metadata is not required
and would not generate the call to `app_main()`.

## How the baseline was assembled

1. Established one solution, one CProject and a `Debug` build with optimization
   disabled. Dependencies are pinned in the [Pack lock](../Trace.cbuild-pack.yml);
   tool versions and setup are in [BUILD.md](BUILD.md).
2. Authored eight local board layers using standalone ST CMSIS startup, system and
   header sources, keeping the build independent of CubeMX generator paths.
   Included source commit IDs and hashes in
   [ThirdParty/ST/sources.json](../ThirdParty/ST/sources.json).
3. Connected each board `main()` to the shared application. Kept one Flash region,
   one SRAM region and a 4 KiB main stack per context; RTX5 uses a shared 32 KiB
   object pool, 1 kHz tick and 1024-byte stacks for the three signal threads.
4. Added symbol-based trace profiles, regenerated against each rebuilt ELF.
   Pack sequences configure device routing/clocks, pyOCD initializes ITM/TPIU, and
   `.ctrace-run.yml` configures trace sources. See
   [trace setup](TRACE_APP.md#configuration-ownership).
5. Separated probe selection and trace traffic settings from the firmware build
   through [debugger target sets](DEBUG_PROBES.md).

The [board inventory](BOARD_SUPPORT.md) records exact devices and Pack choices;
[ThirdParty/README.md](../ThirdParty/README.md) records the imported source subset.

## Rules for extension and validation

A new board should reuse the common CProject and application, adding only its
layer, target and trace profile. Add a new CProject for a separate image
or application. Introduce an application layer when several projects need that
shared implementation; a second solution is warranted by independent dependencies
or workflows, not merely another board.

Address missing trace sequences through the documented, target-specific
[debugger override workflow](TRACE_APP.md#temporary-run-description-overrides).
Record hardware results and limitations against the checks in
[Validation](VALIDATION.md); a successful build or automatic CSV conversion alone
does not establish recording integrity.

## TODO

- [ ] **Trace Buffer (TB):** add and validate buffered trace capture through pyOCD.
- [ ] **Trace / break triggers:** define and test configurable triggers, for example
  stopping trace capture or halting the target when a condition is met ("stop on condition").
