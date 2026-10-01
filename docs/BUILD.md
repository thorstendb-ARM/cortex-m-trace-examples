# Build guide

## Environment and dependencies

Use CMSIS-Toolbox 2.15.0, GNU Arm Toolchain 14.3.1, CMake 3.31.5 and Ninja 1.13.2.
Arm Environment Manager and CI install these versions from
[`vcpkg-configuration.json`](../vcpkg-configuration.json); the CMSIS Solution
extension can also supply the toolbox for local builds.

For a manual installation, put those tools on `PATH`, set `CMSIS_COMPILER_ROOT`
to the toolbox's `etc` directory and `GCC_TOOLCHAIN_14_3_1` to the compiler's `bin`
directory. Check the environment from the repository root:

```sh
cbuild --version
cbuild list environment
cbuild list toolchains --verbose
cbuild list contexts Trace.csolution.yml
```

[`Trace.csolution.yml`](../Trace.csolution.yml) and the board layers pin the
CMSIS/RTX and device packs; [`Trace.cbuild-pack.yml`](../Trace.cbuild-pack.yml)
records their resolved versions. `--packs` lets cbuild/cpackget install missing
packs; `--frozen-packs` retains the recorded resolution and does not install packs
on its own.
Standalone ST CMSIS sources are included as described in the
[third-party inventory](../ThirdParty/README.md). No CubeMX, HAL/LL, BSP library
or complete STM32Cube installation is required.

## Trace toolchain

Trace Generation and automatic RAW-to-CSV conversion use the following
**development versions**. CMSIS Debugger 1.8.0 does not include the Trace
Generation view, pyTS or ctrace.

| Tool | Reference version |
| --- | --- |
| CMSIS Debugger | [1.8.1-92-g3d4de80](https://github.com/Open-CMSIS-Pack/vscode-cmsis-debugger/commit/3d4de8029f47669976b465579702fbae6ce1aa53) |
| pyOCD | [0.45.2.dev28+g3078bf177](https://github.com/pyocd/pyOCD/commit/3078bf177cb4d8afc78d4300a459f3c38c5ef238) |
| pyTS | [0.5.0](https://github.com/Open-CMSIS-Pack/pyTS/releases/tag/v0.5.0) |
| ctrace | [0.3.1](https://github.com/Open-CMSIS-Pack/devtools/releases/tag/tools/ctrace/0.3.1) |

The debugger and pyOCD links identify source revisions; pyTS and ctrace link to
releases. Together they describe the reference toolchain, not a stable debugger
release.

## Build and select a target

```sh
# First build; install missing pinned packs and generate RTE files.
cbuild Trace.csolution.yml --active MCBSTM32F400 --packs --frozen-packs --update-rte

# Select a board and named debugger set.
cbuild Trace.csolution.yml --active 'NUCLEO-F756ZG@STLink' --packs --frozen-packs

# Build all Debug contexts.
cbuild Trace.csolution.yml --context 'TraceDemo.Debug+*' --packs --frozen-packs
```

`--active <target>` selects an unnamed target set; `--active '<target>@<set>'`
selects a named debugger set. It also generates `out/Trace+<target>.cbuild-run.yml`
for that selection. `--context` selects the project/build/target context matrix.
Named sets reuse the same application image; see [debugger selection](DEBUG_PROBES.md).

In VS Code, select `Trace.csolution.yml` as the active solution and choose the
target/set in **CMSIS: Manage Solution Settings**. The `Board-Layer` variable
selects the matching local layer automatically.

## Generated files and editor setup

ELF, HEX and BIN outputs are in `out/TraceDemo/<target>/Debug/`; intermediates and
link maps are under `tmp/`. Build/run descriptions, context-specific RTE headers
and `.trace/` runtime profiles are generated. Keep the solution, CProject, layers,
pack lock, `RTX_Config.*` and their `.base@...` originals, `.cmsis/*.dbgconf*` and
source `.cmsis/*.ctrace.yml` profiles under version control.

After a build or trace-profile edit, regenerate the trace runtime configuration
from the current ELF as described in the [trace workflow](TRACE_APP.md#configure-and-generate-trace).

Enable `cmsis-csolution.generateClangSetup` with the recommended clangd extension.
CMSIS selects the active compilation database through `clangd.arguments` and
updates `Projects/TraceDemo/.clangd` with database and compiler-macro settings.
The root `.clangd` removes `-masm-syntax-unified` for editor analysis only.
These settings follow the selected project context; do not copy another
machine's generated paths.

Local editor state is not versioned: `.vscode/settings.json`, generated
`launch.json`/`tasks.json`, `.cmsis/tools-environment.yml` and
`Projects/*/.clangd` contain active-target or host-specific paths. Keep the portable
root `.clangd` and `.vscode/extensions.json`. CMSIS regenerates the active editor
setup. The [trace workflow](TRACE_APP.md#configure-and-generate-trace) covers the
Trace Generation view and automatic CSV conversion.

## Firmware baseline and limits

Start from device reset with the internal-memory and reset-clock baseline.
Bootloader handover with changed clocks/cache and external memory are outside
this setup. See [Board support](BOARD_SUPPORT.md) for layer and memory choices,
including the [L552 TrustZone requirement](../Board/NUCLEO-L552ZE-Q/README.md)
and [H7 power configuration](../Board/STM32H7B3I-DK/README.md).

A linker RAM report of 100% includes the gap below the main stack at the region's
end; it does not mean that all RAM contains application objects. RTX has its own
object pool and the C-library heap is zero.

GNU newlib-nano/libnosys warns about unimplemented `_close`, `_lseek`, `_read`
and `_write`. No STDIO transport is provided; the application makes no STDIO calls.

See [Validation](VALIDATION.md) for hardware checks and results.
