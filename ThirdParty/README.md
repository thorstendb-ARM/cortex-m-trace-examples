# Third-party sources

`ST/` contains an unmodified subset of ST's separately published CMSIS-device
components. They originate in STM32Cube; this project builds without CubeMX,
HAL/LL or a complete Cube firmware package.

| Component | Upstream tag | Retained license |
| --- | --- | --- |
| [cmsis-device-f4](https://github.com/STMicroelectronics/cmsis-device-f4/tree/v2.6.11) | v2.6.11 | [Apache-2.0](ST/cmsis-device-f4/LICENSE.md) |
| [cmsis-device-f7](https://github.com/STMicroelectronics/cmsis-device-f7/tree/v1.2.10) | v1.2.10 | [Apache-2.0](ST/cmsis-device-f7/LICENSE.md) |
| [cmsis-device-g4](https://github.com/STMicroelectronics/cmsis-device-g4/tree/v1.2.6) | v1.2.6 | [Apache-2.0](ST/cmsis-device-g4/LICENSE.md) |
| [cmsis-device-l5](https://github.com/STMicroelectronics/cmsis-device-l5/tree/v1.0.7) | v1.0.7 | [Apache-2.0](ST/cmsis-device-l5/LICENSE.md) |
| [cmsis-device-h7](https://github.com/STMicroelectronics/cmsis-device-h7/tree/v1.10.7) | v1.10.7 | [Apache-2.0](ST/cmsis-device-h7/LICENSE.md) |

[ST/sources.json](ST/sources.json) records immutable commits, selected paths,
SHA256 hashes and byte counts for all 34 files: licenses, family/device headers,
GNU startup assembly and system templates. Other devices referenced by the
umbrella headers are intentionally absent.

For an update, select a reviewed upstream commit, preserve notices, update the
manifest and rebuild all contexts. Update headers together with startup/system
files. Review changes to clock and power initialization, particularly H7
`ExitRun0Mode()`, before hardware tests.

[The shared GCC linker script](../Board/Support/gcc_linker_script.ld.src) derives
from the Apache-2.0 [CMSIS-Toolbox 2.15.0 GCC linker template](https://open-cmsis-pack.github.io/cmsis-toolbox/build-overview/#linker-script-management).
Local changes retain ST's `.isr_vector` at the Flash origin and provide the six
symbols used by ST GNU startup. That startup initializes only the primary
`.data`/`.bss`; additional memory banks need explicit integration.

CMSIS-Core and RTX5 are consumed from packs. CMSIS tools copy application
configuration and DFP debugger defaults into `RTE/` and `.cmsis/`; their original
notices remain intact.

## Renesas EK-RA8P1 core support

[Renesas/sources.json](Renesas/sources.json) records the startup, system source
and core headers imported from the supplied `Renesas_EK-RA8P1` project, with the
source revision, original byte hashes and retained-file hashes. They adapt
`ARM::Cortex_DFP@1.1.0` Cortex-M85 templates and retain their Apache-2.0 notices.
The local system header removes the reference project's 1-GHz clock API; that
clock implementation and its FSP dependency are not imported. Board clock
recognition is project code in `Board/EK-RA8P1/target.c`.

The CMSIS C startup places `.vectors` at MRAM origin using the shared linker
script, initializes data through the CMSIS copy table and lets newlib initialize
BSS. The DFP's FSP-generated startup is not selected. Renesas::RA_DFP@6.6.0
supplies device metadata, SVD and programming algorithms from the installed pack;
its contents are unchanged. The board-local trace override adapts the supplied
project's historical CPU0 SWO sequence, with the reset-clock frequency and
explicit AP preservation. See the [board documentation](../Board/EK-RA8P1/README.md).
