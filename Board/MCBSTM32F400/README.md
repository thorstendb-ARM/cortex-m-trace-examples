# MCBSTM32F400

Local layer for `STMicroelectronics::STM32F407IGHx`, Cortex-M4.

| Setting | Local configuration |
| --- | --- |
| DFP | `Keil::STM32F4xx_DFP@3.0.0` |
| ST startup/system | `startup_stm32f407xx.s`, `system_stm32f4xx.c` |
| Linked Flash | 1 MiB at `0x08000000` |
| Linked SRAM | 128 KiB at `0x20000000` |
| Main stack | 4 KiB |
| Nominal reset clock | 16 MHz HSI |
| Debugger | ULINK+ (unnamed set), SWD / 1 Mbaud SWO |

The layer follows the [shared board design](../../docs/BOARD_SUPPORT.md#shared-layer-design).
It uses internal memory and leaves trace setup to the debugger.

## Documented ULINK+ wiring

For base-board **V1.2**, use a 10-pin, 1.27 mm Cortex debug cable between ULINK+
and the header marked **Cortex Debug**, aligned at pin 1. Its wiring is:

| Pin | Signal |
| --- | --- |
| 1 | 3V3 / VTref |
| 2 | SWDIO / PA13 |
| 4 | SWCLK / PA14 |
| 6 | SWO / PB3 |
| 10 | nRESET |
| 3, 5, 9 | Ground |

Power the board through its **USB FS or USB HS Micro-USB connector**. Keep
**J19 and J20 closed** for MCU power, **J1 pins 1–2** for VBAT from 3V3, and
**J4 (BOOT0) pins 1–2** for Flash boot. The debug cable carries VTref; there is
no onboard ST-LINK to isolate. Leave the other debug connectors unused.

Source: [MCBSTM32F200/F400 schematic V1.2, 15 October 2013, sheets 1–3](https://www.keil.com/mcbstm32f200/mcbstm32f200-schematics_V1.2.pdf#page=1).
Match the PCB revision and connector markings before using this reference wiring.

See [Validation](../../docs/VALIDATION.md) for runtime/trace results and recording
limits, and [debugger profiles](../../docs/DEBUG_PROBES.md) for capture setup.
