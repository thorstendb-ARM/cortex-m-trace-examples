# STM32H7B3I-DK

Local layer for `STMicroelectronics::STM32H7B3LIHxQ`, Cortex-M7.

| Setting | Local configuration |
| --- | --- |
| DFP | `Keil::STM32H7xx_DFP@4.1.3` |
| ST startup/system | `startup_stm32h7b3xxq.s`, `system_stm32h7xx_singlecore.c` |
| Linked Flash | Bank 1: 1 MiB at `0x08000000` |
| Linked AXI SRAM | 1 MiB at `0x24000000` |
| Main stack | 4 KiB |
| Core / SWO clock | 64 MHz HSI / 1 Mbaud SWO |
| Debugger | ULINK+ (unnamed set), automatic probe selection without a fixed UID, 10 MHz SWD |
| PC sampling period | 8192 cycles |

The layer follows the [shared board design](../../docs/BOARD_SUPPORT.md#shared-layer-design).
`STM32H7B3xxQ` selects the Q device variant. Vendor startup calls `ExitRun0Mode()`
before `SystemInit()`. `USE_PWR_DIRECT_SMPS_SUPPLY` follows the
[official ST board template](https://github.com/STMicroelectronics/STM32CubeH7/blob/master/Projects/STM32H7B3I-DK/Templates/STM32CubeIDE/.cproject);
no HAL is used.
The local layer requires the board's default **direct SMPS** supply arrangement
and links only the internal memory listed above.

## Documented ULINK+ wiring

Use a **10-pin, 1.27 mm Cortex debug cable at CN8**. On the STDC14 footprint,
MIPI10 pins 1–10 correspond to STDC14 pins 3–12; align the cable accordingly.

| MIPI10 pin | STDC14 pin | Signal |
| --- | --- | --- |
| 1 | 3 | Target VCC / VTref |
| 2 | 4 | SWDIO |
| 4 | 6 | SWCLK |
| 6 | 8 | SWO |
| 10 | 12 | nRESET |
| 3, 5, 9 | 5, 7, 11 | Ground / ground detect |

Choose one power/debug arrangement:

- **CN14 ST-LINK USB; JP1 pins 1–2 (STLK):** leave **CN13 open**, wait for the
  ST-LINK COM LED to turn red, then connect ULINK+. Keep ST-LINK idle.
- **CN15 USB OTG HS; JP1 pins 5–6 (U5V):** close **CN13 (STLK_RST)** to hold
  ST-LINK in reset with its pins in high impedance, then connect ULINK+.
  This arrangement does not require the ST-LINK USB connector.

The powered board supplies VTref through the cable. Source:
[UM2569 Rev 7, sections 7.1.4–7.2.4, pp. 12–14](https://www.st.com/resource/en/user_manual/um2569-discovery-kit-with-stm32h7b3li-mcu-stmicroelectronics.pdf#page=12).
Match the physical PCB revision and CN8 population to the
[board references](../../docs/BOARD_SUPPORT.md#stm32h7b3i-dk).

See [Validation](../../docs/VALIDATION.md) for hardware results and the pending
ST-LINK validation, and [debugger profiles](../../docs/DEBUG_PROBES.md)
for capture setup.
