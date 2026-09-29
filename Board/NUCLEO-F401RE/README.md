# NUCLEO-F401RE

Local layer for `STMicroelectronics::STM32F401RETx`, Cortex-M4.

| Setting | Local configuration |
| --- | --- |
| DFP | `Keil::STM32F4xx_DFP@3.0.0` |
| ST startup/system | `startup_stm32f401xe.s`, `system_stm32f4xx.c` |
| Linked Flash | 512 KiB at `0x08000000` |
| Linked SRAM | 96 KiB at `0x20000000` |
| Main stack | 4 KiB |
| Nominal reset clock | 16 MHz HSI |
| Debugger sets | `ULINKplus`, `STLink`; same firmware, SWD / 1 Mbaud SWO |

The layer follows the [shared board design](../../docs/BOARD_SUPPORT.md#shared-layer-design).
DFP sequences supply the SWO pin/clock setup for PB3; no local sequence override
is used. MB1136 connector, jumper and power names differ from the larger Nucleo
boards; use the [F401 wiring table](../../docs/ST_BOARD_BRINGUP.md#nucleo-f401re--mb1136).

See [Validation](../../docs/VALIDATION.md) for ULINK+/ST-LINK
results and open capture issues, and [debugger profiles](../../docs/DEBUG_PROBES.md)
for probe selection and capture settings.
