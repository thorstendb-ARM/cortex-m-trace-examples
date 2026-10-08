# ST boards: ULINK+ and ST-LINK USB power

Connect the ULINK+ adapter to the board's 6-pin SWD/SWO header with the
adapter PCB pointing **inwards towards the board, not outwards**. Connect its
separate **VCC/VTref lead to the board 3V3/3V reference**, including when using
ST-LINK USB for power.
Use only one active debugger session when both probes are connected.

Keep the SWD jumpers closed for these adapter connections; they do not isolate
the onboard ST-LINK. See [Board support](BOARD_SUPPORT.md) for manuals and
schematics, and [Keil AN321, p. 17](https://www.keil.com/appnotes/files/apnt_321_v1.1.pdf#page=17)
for the adapter and separate voltage-reference lead.

## Connections and jumper settings

### NUCLEO-F756ZG / MB1137

- **CN6:** adapter PCB points towards the two **CN4** jumpers.
- **CN4:** both jumpers **closed**.
- **CN1:** ST-LINK USB power; **JP3 = U5V, pins 3–4 (middle position)**.

### NUCLEO-G474RE / MB1367

- **CN4:** SWD/SWO adapter connection.
- **CN2:** both jumpers **closed**.
- **CN1:** ST-LINK USB power; **JP5 pins 1–2 (U5V)** and **JP6 closed**.
- Solder bridge **SB22 closed** routes PB3/SWO.

### NUCLEO-L552ZE-Q / MB1361

- **CN5:** SWD/SWO adapter connection.
- **CN4:** jumpers **1–2 and 3–4 closed**.
- **CN1:** ST-LINK USB power; **JP6 pins 1–2**.
- **JP3 closed** for reset; solder bridge **SB140 closed** for SWO.

### STM32F429I-DISCO / MB1075

- **CN2:** SWD/SWO adapter connection.
- **CN4:** both jumpers **closed**.
- **CN1:** ST-LINK USB power; **JP3 (IDD) closed** for MCU power.
- Solder bridges **SB12 closed** for reset and **SB9 closed** for SWO.

See [UM1670 Rev 6, pp. 18–23](https://www.st.com/resource/en/user_manual/um1670-discovery-kit-with-stm32f429zi-mcu-stmicroelectronics.pdf#page=18);
match the designators to the physical board revision.

### NUCLEO-F401RE / MB1136

- **CN4:** SWD/SWO adapter connection.
- **CN2:** both jumpers **closed**.
- **CN1:** ST-LINK USB power; **JP5 pins 1–2 (U5V)** and **JP6 closed**.
- Solder bridges **SB12 closed** for reset and **SB15 closed** for SWO.

### NUCLEO-F446RE / MB1136

- Use the onboard **ST-LINK/V2-1** through **CN1** USB.
- **CN2:** both jumpers **closed** for the onboard STM32 target.
- **JP5:** pins **1–2 (U5V)**; **JP6 closed** for USB power.
- Solder bridges **SB12 closed** for reset and **SB15 closed** for PB3/SWO.

See [UM1724 Rev 17, pp. 16–26](https://www.st.com/resource/en/user_manual/um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf#page=16).

### STM32F4-DISCO / MB997 B-02

- **CN2:** 6-pin SWD/SWO adapter connection; pins 1–6 are VDD_TARGET, SWCLK,
  GND, SWDIO, NRST and SWO.
- **CN3:** both jumpers **closed** (1–2 and 3–4).
- **CN1:** onboard ST-LINK/V2 Mini-B USB connection and board power;
  **JP1 (IDD) closed** for MCU power.
- **VCC/VTref:** connect the adapter's separate lead to **P2 pin 5 or 6 (3V)**.
  CN2 pin 1 does not provide the board's supply voltage.
- Solder bridges **SB11 closed** for reset and **SB12 closed** for PB3/SWO.

See [UM1472 Rev 9, pp. 20–24](https://www.st.com/resource/en/user_manual/um1472-stm32f4-discovery-stmicroelectronics.pdf#page=20)
and the [MB997 B.2 schematic, sheets 1–2](https://www.st.com/resource/en/schematic_pack/mb997-f407vgt6-b02_schematic.pdf).
