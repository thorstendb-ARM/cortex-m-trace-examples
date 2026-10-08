# Board support and references

All eight targets use local device-based layers in `Board/<Board>/Board.clayer.yml`.
The solution selects each through `Board-Layer`. Device names and pinned DFPs
below match the local configuration. Confirm the physical PCB revision separately
from the catalog board revision.

| Local board layer | CMSIS device (`STMicroelectronics::`) | Core | Pinned DFP (`Keil::`) |
| --- | --- | --- | --- |
| [MCBSTM32F400](../Board/MCBSTM32F400/README.md) | `STM32F407IGHx` | Cortex-M4 | `STM32F4xx_DFP@3.0.0` |
| [NUCLEO-L552ZE-Q](../Board/NUCLEO-L552ZE-Q/README.md) | `STM32L552ZETxQ` | Cortex-M33 | `STM32L5xx_DFP@2.0.0` |
| [NUCLEO-F756ZG](../Board/NUCLEO-F756ZG/README.md) | `STM32F756ZGTx` | Cortex-M7 | `STM32F7xx_DFP@3.1.1` |
| [NUCLEO-G474RE](../Board/NUCLEO-G474RE/README.md) | `STM32G474RETx` | Cortex-M4 | `STM32G4xx_DFP@2.0.0` |
| [STM32F429I-DISCO](../Board/STM32F429I-DISCO/README.md) | `STM32F429ZITx` | Cortex-M4 | `STM32F4xx_DFP@3.0.0` |
| [NUCLEO-F401RE](../Board/NUCLEO-F401RE/README.md) | `STM32F401RETx` | Cortex-M4 | `STM32F4xx_DFP@3.0.0` |
| [NUCLEO-F446RE](../Board/NUCLEO-F446RE/README.md) | `STM32F446RETx` | Cortex-M4 | `STM32F4xx_DFP@3.0.0` |
| [STM32H7B3I-DK](../Board/STM32H7B3I-DK/README.md) | `STM32H7B3LIHxQ` | Cortex-M7 | `STM32H7xx_DFP@4.1.3` |
| [STM32F4-DISCO](../Board/STM32F4-DISCO/README.md) | `STM32F407VGTx` | Cortex-M4 | `STM32F4xx_DFP@3.0.0` |

## Shared layer design

Each layer selects standalone ST CMSIS device headers, GCC startup assembly and
system sources from [ThirdParty/ST](../ThirdParty/README.md), plus the shared GCC
linker template. `regions.h` selects one internal Flash region, one SRAM region
and a 4 KiB main stack. The board `main()` calls `target_init()` and the common
`app_main()`; `target.c` updates/reports `SystemCoreClock`. The baseline uses the
vendor internal-oscillator initialization. Board READMEs record the selected
memory, clock, startup and any power/security requirements.

The project consumes CMSIS-Core and RTX5 from packs. No BSP, CubeMX, HAL, LL or
complete STM32Cube package is required. The debugger configures trace resources;
the shared application produces the test signals. See [build instructions](BUILD.md),
[trace workflow](TRACE_APP.md) and [debugger profiles](DEBUG_PROBES.md).

Hardware results and recording limitations are maintained in
[Validation](VALIDATION.md). For the 6-pin adapter, jumper
and power arrangement, use [ST board wiring](ST_BOARD_BRINGUP.md).

## Official board and device references

Match schematics to the physical PCB before using revision-specific routing.

### MCBSTM32F400

The [Keil board specification](https://www.keil.com/arm/mcbstm32f400/) identifies
STM32F407IG in a 176-pin BGA package, corresponding to `STM32F407IGHx`. Physical
PCB revision and fitted-package confirmation remain open. The local target does
not assume a current BSP `board:` identifier.

| Reference | Document |
| --- | --- |
| Board manual | [MCBSTM32F200/400 User's Guide](https://www.keil.com/support/man/docs/mcbstm32f200/default.htm) |
| Schematics | [MCBSTM32F200/F400 V1.2, 15 October 2013](https://www.keil.com/mcbstm32f200/mcbstm32f200-schematics_V1.2.pdf), sheets 1–3 for power, debug and boot jumpers |
| Datasheet | [DS8626, STM32F405/407](https://www.st.com/resource/en/datasheet/stm32f405rg.pdf) |
| Reference manual | [RM0090](https://www.st.com/resource/en/reference_manual/rm0090-stm32f405415-stm32f407417-stm32f427437-and-stm32f429439-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) |
| Errata/core programming | ES0182 and PM0214 in the [STM32F407/417 document index](https://www.st.com/en/microcontrollers-microprocessors/stm32f407-417/documentation.html) |

The [board wiring reference](../Board/MCBSTM32F400/README.md#documented-ulink-wiring)
uses the 10-pin Cortex Debug header for SWD/SWO and USB power. The V1.2 schematic
also documents 20-pin JTAG and Cortex debug/ETM connectors.

### NUCLEO-L552ZE-Q

Catalog reference: `STMicroelectronics::NUCLEO-L552ZE-Q:Rev.C`, MB1361. The local
image requires TrustZone already disabled in hardware; see the
[layer security requirement](../Board/NUCLEO-L552ZE-Q/README.md).

| Reference | Document |
| --- | --- |
| Board/manual | [NUCLEO-L552ZE-Q](https://www.st.com/en/evaluation-tools/nucleo-l552ze-q.html), [UM2581, MB1361](https://www.st.com/resource/en/user_manual/dm00615305-stm32l5-nucleo-144-board-mb1361-stmicroelectronics.pdf) |
| Schematic | [MB1361-L552ZEQ-C02](https://www.st.com/resource/en/schematic_pack/mb1361-l552zeq-c02_schematic.pdf) |
| Datasheet | [DS12737, STM32L552xx](https://www.st.com/resource/en/datasheet/stm32l552cc.pdf) |
| Reference manual | [RM0438](https://www.st.com/resource/en/reference_manual/rm0438-stm32l552xx-and-stm32l562xx-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) |
| Errata | [ES0448](https://www.st.com/resource/en/errata_sheet/es0448-stm32l552xx562xx-device-errata-stmicroelectronics.pdf) |

Use the [MB1361 wiring table](ST_BOARD_BRINGUP.md#nucleo-l552ze-q--mb1361)
for this board. Generic Nucleo-family connector descriptions do not establish a
trace connector on this model.

### NUCLEO-F756ZG

Catalog reference: `STMicroelectronics::NUCLEO-F756ZG:Rev.B`, MB1137, STM32F756ZGT6.

| Reference | Document |
| --- | --- |
| Board/manual | [NUCLEO-F756ZG](https://www.st.com/en/evaluation-tools/nucleo-f756zg.html), [UM1974, MB1137](https://www.st.com/resource/en/user_manual/um1974-stm32-nucleo144-boards-mb1137-stmicroelectronics.pdf) |
| Schematics | [Nucleo-144 schematic package](https://www.st.com/resource/en/schematic_pack/nucleo_144pins_sch.zip) |
| Datasheet | [DS10915, STM32F756xx](https://www.st.com/resource/en/datasheet/stm32f756bg.pdf) |
| Reference manual | [RM0385](https://www.st.com/resource/en/reference_manual/rm0385-stm32f75xxx-and-stm32f74xxx-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) |
| Errata | [ES0290](https://www.st.com/resource/en/errata_sheet/es0290-stm32f74xxx-and-stm32f75xxx-device-limitations-stmicroelectronics.pdf) |

The [wiring guide](ST_BOARD_BRINGUP.md#nucleo-f756zg--mb1137) records
the tested ULINK+ adapter and ST-LINK USB power arrangement.

### NUCLEO-G474RE

Catalog reference: `STMicroelectronics::NUCLEO-G474RE:Rev.C`, MB1367,
STM32G474RET6.

| Reference | Document |
| --- | --- |
| Board/manual | [NUCLEO-G474RE](https://www.st.com/en/evaluation-tools/nucleo-g474re.html), [UM2505, MB1367](https://www.st.com/resource/en/user_manual/um2505-stm32g4-nucleo64-boards-mb1367-stmicroelectronics.pdf) |
| Schematic | [MB1367-G474RE-C01](https://www.st.com/resource/en/schematic_pack/mb1367-g474re-c01_schematic.pdf) |
| Datasheet | [DS12288, STM32G474xB/C/E](https://www.st.com/resource/en/datasheet/stm32g474cb.pdf) |
| Reference manual | [RM0440](https://www.st.com/resource/en/reference_manual/rm0440-stm32g4-series-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) |
| Errata | [ES0393](https://www.st.com/resource/en/errata_sheet/es0393-stm32g4-series-device-errata-stmicroelectronics.pdf) |

See the [MB1367 wiring notes](ST_BOARD_BRINGUP.md#nucleo-g474re--mb1367).

### STM32F429I-DISCO

The physical DISCO/DISC1 variant and PCB revision remain unconfirmed. The
catalog's `STMicroelectronics::STM32F429I-DISC1:Rev.C` uses the same
`STM32F429ZITx` device support; the local target does not select a DISC1 BSP.
ST describes DISC1 as the replacement order code on its
[product page](https://www.st.com/en/evaluation-tools/32f429idiscovery.html).

| Reference | Document |
| --- | --- |
| Board manual | [UM1670](https://www.st.com/resource/en/user_manual/um1670-discovery-kit-with-stm32f429zi-mcu-stmicroelectronics.pdf) |
| Schematics | [MB1075-F429I-C01](https://www.st.com/resource/en/schematic_pack/mb1075-f429i-c01_schematic.pdf); select the physical revision from [ST's documents](https://www.st.com/en/evaluation-tools/32f429idiscovery.html#documentation) |
| Datasheet | [STM32F429ZI](https://www.st.com/resource/en/datasheet/stm32f429zi.pdf) |
| Reference manual | [RM0090](https://www.st.com/resource/en/reference_manual/rm0090-stm32f405415-stm32f407417-stm32f427437-and-stm32f429439-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) |
| Errata | [ES0206](https://www.st.com/resource/en/errata_sheet/es0206-stm32f427437-and-stm32f429439-device-errata-stmicroelectronics.pdf) |

Onboard ST-LINK descriptions and connector routing vary by board revision.
See the [MB1075 wiring notes](ST_BOARD_BRINGUP.md#stm32f429i-disco--mb1075).

### NUCLEO-F401RE

Catalog reference: `STMicroelectronics::NUCLEO-F401RE:Rev.C`, MB1136, STM32F401RET6.

| Reference | Document |
| --- | --- |
| Board/manual | [NUCLEO-F401RE](https://www.st.com/en/evaluation-tools/nucleo-f401re.html), [UM1724, MB1136](https://www.st.com/resource/en/user_manual/um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf) |
| Schematic | [MB1136-DEFAULT-C03](https://www.st.com/resource/en/schematic_pack/mb1136-default-c03_schematic.pdf) |
| Datasheet | [DS10086, STM32F401RE](https://www.st.com/resource/en/datasheet/stm32f401re.pdf) |
| Reference manual | [RM0368](https://www.st.com/resource/en/reference_manual/rm0368-stm32f401xbc-and-stm32f401xde-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) |
| Errata | [ES0299, STM32F401xD/xE](https://www.st.com/resource/en/errata_sheet/es0299-stm32f401xd-and-stm32f401xe-device-errata-stmicroelectronics.pdf) |

Use ES0299 for the fitted xE device; ES0222 covers xB/xC. Connector, jumper and
power names are in the [MB1136 wiring table](ST_BOARD_BRINGUP.md#nucleo-f401re--mb1136).

### NUCLEO-F446RE

The board is MB1136 with an STM32F446RET6 and an onboard ST-LINK/V2-1. ST lists
MB1136-F446RE-C03 and C04 main-board revisions; the physical revision of the
tested board was not visually inspected.

| Reference | Document |
| --- | --- |
| Board/manual | [NUCLEO-F446RE](https://www.st.com/en/evaluation-tools/nucleo-f446re.html), [UM1724 Rev 17, MB1136](https://www.st.com/resource/en/user_manual/um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf) |
| Schematics | [MB1136-DEFAULT-C03](https://www.st.com/resource/en/schematic_pack/mb1136-default-c03_schematic.pdf), [C04](https://www.st.com/resource/en/schematic_pack/mb1136-default-c04_schematic.pdf); match the physical revision |
| Datasheet | [DS10693, STM32F446xC/xE](https://www.st.com/resource/en/datasheet/stm32f446re.pdf) |
| Reference manual | [RM0390](https://www.st.com/resource/en/reference_manual/rm0390-stm32f446xx-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) |
| Errata | [ES0298](https://www.st.com/resource/en/errata_sheet/es0298-stm32f446xcxe-device-errata-stmicroelectronics.pdf) |

Use the [MB1136 F446 wiring table](ST_BOARD_BRINGUP.md#nucleo-f446re--mb1136)
for the onboard ST-LINK and PB3/SWO route.

### STM32H7B3I-DK

Catalog reference: `STMicroelectronics::STM32H7B3I-DK:Rev.C`, STM32H7B3LIH6Q.
ST lists MB1332 B and C revisions. The local layer selects the Q device and
requires the default direct SMPS supply configuration. The
[board wiring reference](../Board/STM32H7B3I-DK/README.md#documented-ulink-wiring)
describes CN8 SWD/SWO, VTref, USB power and ST-LINK isolation from UM2569 Rev 7.
Match the physical revision and connector population; earlier tests did not
record them.

| Reference | Document |
| --- | --- |
| Board/manual | [STM32H7B3I-DK](https://www.st.com/en/evaluation-tools/stm32h7b3i-dk.html), [UM2569](https://www.st.com/resource/en/user_manual/um2569-discovery-kit-with-stm32h7b3li-mcu-stmicroelectronics.pdf) |
| Schematics | [MB1332-H7B3I-C02](https://www.st.com/resource/en/schematic_pack/mb1332-h7b3i-c02_schematic.pdf), [C03](https://www.st.com/resource/en/schematic_pack/mb1332-h7b3i-c03-schematic.pdf); match the physical board |
| Datasheet | [DS13139, STM32H7B3](https://www.st.com/resource/en/datasheet/stm32h7b3ri.pdf) |
| Reference manual | [RM0455](https://www.st.com/resource/en/reference_manual/rm0455-stm32h7a37b3-and-stm32h7b0-value-line-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) |
| Errata | [ES0478](https://www.st.com/resource/en/errata_sheet/es0478-stm32h7a3xig-stm32h7b0xb-and-stm32h7b3xi-device-errata-stmicroelectronics.pdf) |

See [Validation](VALIDATION.md) for results and the pending onboard STLINK-V3E
validation. The device's documented 4 KiB Embedded Trace Buffer is a candidate
for later TB work; its access path and pyOCD support remain unqualified.

### STM32F4-DISCO / MB997 B-02

The original **STM32F4DISCOVERY**, PCB **MB997 B-02**, carries an
**STM32F407VGT6** and **ST-LINK/V2**. Its local layer uses device
`STMicroelectronics::STM32F407VGTx`. The later STM32F407G-DISC1 has different
onboard-probe hardware; select documentation for the physical PCB revision.

| Reference | Document |
| --- | --- |
| Board manual | [UM1472 Rev 9](https://www.st.com/resource/en/user_manual/um1472-stm32f4-discovery-stmicroelectronics.pdf), pp. 20–24 for connections, pp. 33–35 for board revisions |
| Schematic | [MB997-F407VGT6-B02](https://www.st.com/resource/en/schematic_pack/mb997-f407vgt6-b02_schematic.pdf), sheets 1–3 for PCB identity, SWD/SWO, power and fitted MCU |
| Datasheet | [DS8626, STM32F405/407](https://www.st.com/resource/en/datasheet/stm32f405rg.pdf) |
| Reference manual | [RM0090](https://www.st.com/resource/en/reference_manual/rm0090-stm32f405415-stm32f407417-stm32f427437-and-stm32f429439-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) |
| Errata | ES0182 in the [STM32F407/417 document index](https://www.st.com/en/microcontrollers-microprocessors/stm32f407-417/documentation.html) |

Use the [board README](../Board/STM32F4-DISCO/README.md) and
[MB997 wiring notes](ST_BOARD_BRINGUP.md#stm32f4-disco--mb997-b-02).
