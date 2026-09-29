# STM32F4-DISCO

Local layer for the original **STM32F4DISCOVERY, MB997 B-02**, fitted with
`STM32F407VGT6` (U4); CMSIS device `STMicroelectronics::STM32F407VGTx`, Cortex-M4.
This revision has an onboard ST-LINK/V2; use supported probe firmware for pyOCD
and SWO. An older probe may need a vendor firmware update before first use.
The later STM32F407G-DISC1 has different
probe hardware; its BSP is not selected here. See [UM1472 Rev 9, pp. 33–35](https://www.st.com/resource/en/user_manual/um1472-stm32f4-discovery-stmicroelectronics.pdf#page=33)
and the [MB997 B.2 schematic, sheets 1–3](https://www.st.com/resource/en/schematic_pack/mb997-f407vgt6-b02_schematic.pdf).

| Setting | Local configuration |
| --- | --- |
| DFP | `Keil::STM32F4xx_DFP@3.0.0` |
| ST startup/system | `startup_stm32f407xx.s`, `system_stm32f4xx.c` |
| Linked Flash | 1 MiB at `0x08000000` |
| Linked SRAM | 128 KiB at `0x20000000` |
| Main stack | 4 KiB |
| Nominal reset clock | 16 MHz HSI |
| Debugger sets | `ULINKplus`, `STLink`; same firmware, SWD / 1 Mbaud SWO |

The layer follows the [shared board design](../../docs/BOARD_SUPPORT.md#shared-layer-design).
The separate 64 KiB CCM RAM is not linked. Clock and memory references are
[DS8626 Rev 12, pp. 25 and 73](https://www.st.com/resource/en/datasheet/stm32f407vg.pdf#page=25).
Existing DFP sequences configure SWO routing and clocks; no local override is used.

Select target `STM32F4-DISCO` in **CSolution: Manage Solution**, then choose
`ULINKplus` or `STLink`. Both use automatic probe selection. See
[ST board bring-up](../../docs/ST_BOARD_BRINGUP.md#stm32f4-disco--mb997-b-02) for
CN2/CN3 wiring, USB power and the separate voltage-reference lead, and
[Validation](../../docs/VALIDATION.md) for hardware-test status.
