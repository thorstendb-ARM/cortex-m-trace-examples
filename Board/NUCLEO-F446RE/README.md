# NUCLEO-F446RE

Local layer for `STMicroelectronics::STM32F446RETx`, Cortex-M4.

| Setting | Local configuration |
| --- | --- |
| Fitted MCU | STM32F446RET6 |
| DFP | `Keil::STM32F4xx_DFP@3.0.0` |
| ST startup/system | `startup_stm32f446xx.s`, `system_stm32f4xx.c` |
| Linked Flash | 512 KiB at `0x08000000` |
| Linked SRAM | 128 KiB at `0x20000000` |
| Main stack | 4 KiB |
| Nominal reset clock | 16 MHz HSI |
| Debugger set | `STLink`; SWD / 1 Mbaud SWO |

The layer follows the [shared board design](../../docs/BOARD_SUPPORT.md#shared-layer-design).
DFP sequences supply the SWO pin/clock setup for PB3; no local sequence override
is used. Keep both CN2 jumpers closed for the onboard ST-LINK/V2-1 and SB15
closed for SWO. Use the [F446 wiring table](../../docs/ST_BOARD_BRINGUP.md#nucleo-f446re--mb1136).

See [Validation](../../docs/VALIDATION.md) for hardware results and open capture
issues, and [debugger profiles](../../docs/DEBUG_PROBES.md) for probe selection
and capture settings.
