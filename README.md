# Cortex-M Trace Examples

One shared **RTX5 trace demo** for six Cortex-M boards, built with CMSIS-Toolbox.
Two threads update sine and deterministic-noise variables every 100 ms for DWT;
a third emits a 32-bit counter on ITM channel 1 every 200 ms. Trace profiles add
PC sampling and timestamps. pyOCD captures SWO; ctrace converts recordings to CSV.

**Status: experimental SWO demo.** Trace Generation and automatic CSV conversion
require the [listed development tool versions](docs/BUILD.md#trace-toolchain).
Capture-start and pause/end recording issues remain; see [Validation](docs/VALIDATION.md).

## Boards

| Target | Core | Configured probes |
| --- | --- | --- |
| [MCBSTM32F400](Board/MCBSTM32F400/README.md) | Cortex-M4 | ULINK+ |
| [NUCLEO-L552ZE-Q](Board/NUCLEO-L552ZE-Q/README.md) | Cortex-M33, TrustZone off | ULINK+, ST-LINK |
| [NUCLEO-F756ZG](Board/NUCLEO-F756ZG/README.md) | Cortex-M7 | ULINK+, ST-LINK |
| [STM32F429I-DISCO](Board/STM32F429I-DISCO/README.md) | Cortex-M4 | ULINK+, ST-LINK |
| [NUCLEO-F401RE](Board/NUCLEO-F401RE/README.md) | Cortex-M4 | ULINK+, ST-LINK |
| [STM32H7B3I-DK](Board/STM32H7B3I-DK/README.md) | Cortex-M7 | ULINK+ |

Hardware results and open capture issues are listed in
[Validation](docs/VALIDATION.md). This project currently implements SWO;
Trace Buffer (TB) support is planned.

## Use the demo

1. Open this folder in VS Code and install its recommended build and clangd
   extensions. Activate the tools from `vcpkg-configuration.json`; see
   [build tools and setup](docs/BUILD.md). For Trace Generation, use the
   [specified CMSIS Debugger and trace-tool versions](docs/BUILD.md#trace-toolchain).
2. Select `Trace.csolution.yml` as the active solution. Open **CMSIS: Manage Solution
   Settings**, choose a board and, where available, the `ULINKplus` or `STLink` set.
   Both use automatic probe selection. Check the
   board README linked above and the [ST board wiring notes](docs/ST_BOARD_BRINGUP.md).
3. Build the selected target. Enable `vscode-cmsis-debugger.enableTraceGenerationView`
   in local VS Code settings. In the CMSIS Debugger **Trace Generation** view,
   review its `.ctrace.yml` profile and run **Convert *.ctrace.yml to *.ctrace-run.yml**.
   Repeat conversion after rebuilding or changing the profile so DWT addresses
   match the current ELF.
4. Start debugging. SWO is recorded under `.trace/`; pause or end the session to
   trigger CSV conversion when new trace data is available. Inspect decoder errors
   as well as the CSV. See the [trace workflow](docs/TRACE_APP.md).

Command-line build from an activated tool environment:

```sh
cbuild Trace.csolution.yml --active 'STM32F429I-DISCO@STLink' --packs --update-rte
```

Changing the debugger set keeps the same application image for that board. Changing
boards selects another local board layer. Firmware produces the signals; Pack
sequences, pyOCD and ctrace configuration own trace initialization.

## Add a board with an agent

Use the project skill [add-trace-board](.agents/skills/add-trace-board/SKILL.md),
for example: `Use $add-trace-board to add NUCLEO-G474RE with STLink.`
Without a board name or debugger, the skill asks for the missing information.
It follows [DESIGN.md](docs/DESIGN.md) and adds the target, board layer, startup,
trace profiles and build checks. Hardware validation is reported separately.

Codex discovers the repository's `.agents/skills/` directory
([skill discovery](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)).
For an agent without skill discovery, explicitly ask it to read the linked
`SKILL.md` and follow its workflow.

## Project files and documentation

| File or directory | Purpose |
| --- | --- |
| `Trace.csolution.yml`, `Projects/TraceDemo/TraceDemo.cproject.yml` | Targets, debugger sets, common application and RTX5 components |
| `Common/`, `Board/` | Shared application and six local board layers |
| `.cmsis/`, `Trace.cbuild-pack.yml`, `vcpkg-configuration.json` | Trace/debug profiles and pinned dependencies |
| [DESIGN.md](docs/DESIGN.md) | Agreed requirements, architecture and how the baseline was assembled |
| [BUILD.md](docs/BUILD.md), [DEBUG_PROBES.md](docs/DEBUG_PROBES.md) | Tool setup, builds and switching probes |
| [TRACE_APP.md](docs/TRACE_APP.md) | Signal definitions, capture/CSV workflow and host-tool scope |
| [BOARD_SUPPORT.md](docs/BOARD_SUPPORT.md), [ST_BOARD_BRINGUP.md](docs/ST_BOARD_BRINGUP.md) | Devices, packs, manuals, connectors, jumpers and power |
| [Validation](docs/VALIDATION.md) | Hardware results, recording limits and open work |
| [ThirdParty](ThirdParty/README.md) | Standalone ST CMSIS sources, provenance and licenses |

Build output (`out/`, `tmp/`) and local captures (`.trace/`) are ignored by Git
and are not included in a fresh checkout.

[Apache License 2.0](LICENSE). Third-party sources retain their own notices.
