# STM32F429I-DISCO

Local layer for `STMicroelectronics::STM32F429ZITx`, Cortex-M4.

| Setting | Local configuration |
| --- | --- |
| DFP | `Keil::STM32F4xx_DFP@3.0.0` |
| ST startup/system | `startup_stm32f429xx.s`, `system_stm32f4xx.c` |
| Linked Flash | 2 MiB at `0x08000000` |
| Linked SRAM | 192 KiB at `0x20000000` |
| Main stack | 4 KiB |
| Nominal reset clock | 16 MHz HSI |
| Debugger sets | `ULINKplus`, `STLink`; same firmware, SWD / 1 Mbaud SWO |

The layer follows the [shared board design](../../docs/BOARD_SUPPORT.md#shared-layer-design).
CCM RAM and external SDRAM are not linked. Existing DFP sequences provide SWO
pin/clock configuration; no local override is used.

The physical DISCO/DISC1 variant and PCB revision remain unresolved. The layer
uses common STM32F429ZITx device support without selecting the DISC1 BSP. Match
connector routing and onboard probe details to the actual board before rewiring;
see the [board references](../../docs/BOARD_SUPPORT.md#stm32f429i-disco).

See [Validation](../../docs/VALIDATION.md) for ST-LINK and ULINK+ capture results,
and [debugger profiles](../../docs/DEBUG_PROBES.md) for capture setup.
