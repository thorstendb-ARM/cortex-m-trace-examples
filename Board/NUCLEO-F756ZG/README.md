# NUCLEO-F756ZG

Local layer for `STMicroelectronics::STM32F756ZGTx`, Cortex-M7.

| Setting | Local configuration |
| --- | --- |
| DFP | `Keil::STM32F7xx_DFP@3.1.1` |
| ST startup/system | `startup_stm32f756xx.s`, `system_stm32f7xx.c` |
| Linked Flash | 1 MiB at `0x08000000` |
| Linked SRAM | 240 KiB at `0x20010000` |
| Main stack | 4 KiB |
| Nominal reset clock | 16 MHz HSI |
| Debugger sets | `ULINKplus`, `STLink`; same firmware, SWD / 1 Mbaud SWO |

The layer follows the [shared board design](../../docs/BOARD_SUPPORT.md#shared-layer-design).
The layer does not configure caches, the MPU or board peripherals.

Follow the [ST board wiring guide](../../docs/ST_BOARD_BRINGUP.md#nucleo-f756zg--mb1137)
for the adapter direction, **both CN4 jumpers closed**, the separate **3V3/VTref
lead**, and **CN1 USB / JP3 U5V** power selection.

See [Validation](../../docs/VALIDATION.md) for controlled and IDE capture results,
and [debugger profiles](../../docs/DEBUG_PROBES.md) for capture setup.
