# NUCLEO-G474RE

Local layer for `STMicroelectronics::STM32G474RETx`, Cortex-M4.

| Setting | Local configuration |
| --- | --- |
| DFP | `Keil::STM32G4xx_DFP@2.0.0` |
| ST startup/system | `startup_stm32g474xx.s`, `system_stm32g4xx.c` |
| Linked Flash | 512 KiB at `0x08000000` |
| Linked SRAM | 128 KiB at `0x20000000` |
| Main stack | 4 KiB |
| Nominal reset clock | 16 MHz HSI |
| Debugger sets | `ULINKplus`, `STLink`; same firmware, SWD / 1 Mbaud SWO |

The layer follows the [shared board design](../../docs/BOARD_SUPPORT.md#shared-layer-design).
DFP sequences provide the PB3 SWO pin/clock setup; no local sequence override
is used. Follow the [G474 wiring table](../../docs/ST_BOARD_BRINGUP.md#nucleo-g474re--mb1367)
for connector, jumper and power settings.

Hardware trace validation is pending; see [Validation](../../docs/VALIDATION.md)
and [debugger profiles](../../docs/DEBUG_PROBES.md) for capture setup.