# Cortex-M Trace Examples

**Project scope:** This project is used to test and bring up the new trace
architecture across a selection of boards and trace use cases. It is not a board
bring-up project or a reference example, and is currently not intended as a
starting point for customer projects.

 A common firmware baseline for testing trace across Cortex-M boards and debug
 probes. One **CMSIS solution** builds a shared **RTX5 application** through eight
local board layers, covering Cortex-M4, Cortex-M7 and Cortex-M33.

The workload updates sine and deterministic-noise variables every 100 ms for DWT
and emits an ITM channel 1 counter every 200 ms. Debugger profiles add PC sampling
and timestamps. pyOCD captures SWO; ctrace converts recordings to CSV.
NUCLEO-L552ZE-Q also provides `ULINKplus StackCorruption`: a fourth thread
deliberately overwrites its RTX stack magic word, and a single DWT watch reports
the writing PC over SWO. See the [stack-corruption workflow](docs/TRACE_APP.md#stack-corruption-watch-nucleo-l552ze-q).

**Status: experimental SWO demo.** Trace Generation and automatic CSV conversion
require the [listed development tool versions](docs/BUILD.md#trace-toolchain).
Capture-start and pause/end recording issues remain; see [Validation](docs/VALIDATION.md).

## Boards

| Target | Core | Configured probes |
| --- | --- | --- |
| [MCBSTM32F400](Board/MCBSTM32F400/README.md) | Cortex-M4 | `ULINKplus` |
| [NUCLEO-L552ZE-Q](Board/NUCLEO-L552ZE-Q/README.md) | Cortex-M33, TrustZone off | `ULINKplus`, `STLink` |
| [NUCLEO-F756ZG](Board/NUCLEO-F756ZG/README.md) | Cortex-M7 | `ULINKplus`, `STLink` |
| [NUCLEO-G474RE](Board/NUCLEO-G474RE/README.md) | Cortex-M4 | `ULINKplus`, `STLink` |
| [STM32F429I-DISCO](Board/STM32F429I-DISCO/README.md) | Cortex-M4 | `ULINKplus`, `STLink` |
| [NUCLEO-F401RE](Board/NUCLEO-F401RE/README.md) | Cortex-M4 | `ULINKplus`, `STLink` |
| [NUCLEO-F446RE](Board/NUCLEO-F446RE/README.md) | Cortex-M4 | `STLink` |
| [STM32H7B3I-DK](Board/STM32H7B3I-DK/README.md) | Cortex-M7 | `ULINKplus` |
| [STM32F4-DISCO](Board/STM32F4-DISCO/README.md), MB997 B-02 | Cortex-M4 | `ULINKplus`, `STLink` |

Hardware results and open capture issues are listed in
[Validation](docs/VALIDATION.md). This project currently implements SWO;
Trace Buffer (TB) support is planned.

## Prerequisites

Use one of the boards and configured probes above. The [build guide](docs/BUILD.md)
lists the build tools and editor setup; `vcpkg-configuration.json` records the
build-tool versions. Trace Generation and CSV conversion additionally require
the [reference debugger and trace-tool versions](docs/BUILD.md#trace-toolchain).
Missing CMSIS packs are installed by `cbuild --packs` using the pinned dependencies.

## Quick start

1. Open this folder in VS Code and activate the build environment described in
   the [build guide](docs/BUILD.md).
2. Select `Trace.csolution.yml` as the active solution. Open **CMSIS: Manage Solution
   Settings**, choose a board and its target set (`ULINKplus`, `STLink`, or the
   L552-only `ULINKplus StackCorruption`). Sets use automatic probe selection;
   select the intended probe locally when several are connected. Check the
   board README linked above and the [ST board wiring notes](docs/ST_BOARD_BRINGUP.md).
3. Build the selected target. Enable `vscode-cmsis-debugger.enableTraceGenerationView`
   in local VS Code settings. In the CMSIS Debugger **Trace Generation** view,
   review its `.ctrace.yml` profile and run **Convert *.ctrace.yml to *.ctrace-run.yml**.
   Repeat conversion after rebuilding or changing the profile so DWT addresses
   match the current ELF.
4. Start debugging. SWO is recorded under `.trace/`; pause or end the session to
   trigger CSV conversion when new trace data is available. Inspect decoder errors
   as well as the CSV. See the [trace workflow](docs/TRACE_APP.md).

For an agent-driven stack-magic capture, invoke `Use $trace-stack-magic-corruption-test` with the
intended target set active. The project
[trace-stack-magic-corruption-test skill](.agents/skills/trace-stack-magic-corruption-test/SKILL.md) checks its
trace watch, runs and ends debugging, then creates a Markdown report with one
section per CSV entry, source text and project-relative locations. The CSV remains
unchanged. See the [workflow](docs/TRACE_APP.md#stack-magic-agent-workflow).

Command-line build from an activated tool environment:

```sh
cbuild Trace.csolution.yml --active 'STM32F429I-DISCO@STLink' --packs --frozen-packs --update-rte
```

The regular `ULINKplus` and `STLink` sets share the board's `Debug` image.
`ULINKplus StackCorruption` selects the separate `StackCorruption` build.
Changing boards selects another local board layer. Firmware produces the signals; Pack
sequences, pyOCD and ctrace configuration own trace initialization.

## Add a board

Follow the [project design](docs/DESIGN.md) to add a local board layer, target and
trace profiles while reusing the shared application. The optional
[add-trace-board agent skill](.agents/skills/add-trace-board/SKILL.md) guides this
workflow, including build checks and hardware validation when a board is available.
For example: `Use $add-trace-board to add NUCLEO-G474RE with STLink.`
If your agent does not discover repository skills, ask it to read the linked
`SKILL.md` first.

## Project files and documentation

| File or directory | Purpose |
| --- | --- |
| `Trace.csolution.yml`, `Projects/TraceDemo/TraceDemo.cproject.yml` | Targets, debugger sets, common application and RTX5 components |
| `Common/`, `Board/` | Shared application and eight local board layers |
| `.cmsis/`, `Trace.cbuild-pack.yml`, `vcpkg-configuration.json` | Trace/debug profiles and pinned dependencies |
| [DESIGN.md](docs/DESIGN.md) | Agreed requirements, architecture and how the baseline was assembled |
| [BUILD.md](docs/BUILD.md), [DEBUG_PROBES.md](docs/DEBUG_PROBES.md) | Tool setup, builds and switching probes |
| [TRACE_APP.md](docs/TRACE_APP.md) | Signal definitions, capture/CSV workflow and host-tool scope |
| [BOARD_SUPPORT.md](docs/BOARD_SUPPORT.md), [ST_BOARD_BRINGUP.md](docs/ST_BOARD_BRINGUP.md) | Devices, packs, manuals, connectors, jumpers and power |
| [Validation](docs/VALIDATION.md) | Hardware results, recording limits and open work |
| [ThirdParty](ThirdParty/README.md) | Standalone ST CMSIS sources, provenance and licenses |

Build output (`out/`, `tmp/`) and local captures (`.trace/`) are ignored by Git
and are not included in a fresh checkout.

## License

Project code is licensed under [Apache License 2.0](LICENSE). Third-party sources
retain their own licenses and notices; see the [source inventory](ThirdParty/README.md).
