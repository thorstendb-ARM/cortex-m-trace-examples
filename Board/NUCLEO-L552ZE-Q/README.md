# NUCLEO-L552ZE-Q

Local layer for `STMicroelectronics::STM32L552ZETxQ`, Cortex-M33, using one image
with `trustzone: off`.

| Setting | Local configuration |
| --- | --- |
| DFP | `Keil::STM32L5xx_DFP@2.0.0` |
| ST startup/system | `startup_stm32l552xx.s`, `system_stm32l5xx.c` |
| Linked Flash | 512 KiB at `0x08000000` |
| Linked SRAM | 256 KiB at `0x20000000` |
| Main stack | 4 KiB |
| Nominal reset clock | 4 MHz MSI |
| Debugger sets | `ULINKplus`, `STLink` (shared `Debug` image); `ULINKplus StackCorruption` (separate build); SWD / 1 Mbaud SWO |

The layer follows the [shared board design](../../docs/BOARD_SUPPORT.md#shared-layer-design).
DFP sequences provide the PB3 SWO pin/clock setup; no local override is used.

**TrustZone must already be disabled in hardware.** Building `trustzone: off`
does not change option bytes or provision the device. There is no secure
companion image.

MB1361 uses different connector/jumper names from F756; follow the
[L552 wiring table](../../docs/ST_BOARD_BRINGUP.md#nucleo-l552ze-q--mb1361).
See [Validation](../../docs/VALIDATION.md) for hardware results and recording
limits, and [debugger profiles](../../docs/DEBUG_PROBES.md) for capture setup.

`ULINKplus StackCorruption` adds a `StackCorruption` thread with a 256-byte stack.
After two seconds it deliberately overwrites the first stack word, RTX's
`0xE25A2EA5` magic, with `0xDEADC0DE`. Its trace profile watches only writes to
that word and emits the writing PC; the normal demo trace sources are disabled.
RTX stack checking then enters its stack-overflow error handler. Select this set,
build and regenerate its trace profile before capture; see the
[stack-corruption workflow](../../docs/TRACE_APP.md#stack-corruption-watch-nucleo-l552ze-q).
