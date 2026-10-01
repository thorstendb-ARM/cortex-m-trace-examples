# Third-party sources

`ST/` contains an unmodified subset of ST's separately published CMSIS-device
components. They originate in STM32Cube; this project builds without CubeMX,
HAL/LL or a complete Cube firmware package.

| Component | Upstream tag | Retained license |
| --- | --- | --- |
| [cmsis-device-f4](https://github.com/STMicroelectronics/cmsis-device-f4/tree/v2.6.11) | v2.6.11 | [Apache-2.0](ST/cmsis-device-f4/LICENSE.md) |
| [cmsis-device-f7](https://github.com/STMicroelectronics/cmsis-device-f7/tree/v1.2.10) | v1.2.10 | [Apache-2.0](ST/cmsis-device-f7/LICENSE.md) |
| [cmsis-device-l5](https://github.com/STMicroelectronics/cmsis-device-l5/tree/v1.0.7) | v1.0.7 | [Apache-2.0](ST/cmsis-device-l5/LICENSE.md) |
| [cmsis-device-h7](https://github.com/STMicroelectronics/cmsis-device-h7/tree/v1.10.7) | v1.10.7 | [Apache-2.0](ST/cmsis-device-h7/LICENSE.md) |

[ST/sources.json](ST/sources.json) records immutable commits, selected paths,
SHA256 hashes and byte counts for all 30 files: licenses, family/device headers,
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
