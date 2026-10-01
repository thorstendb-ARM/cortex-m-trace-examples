# Validation

Status: **2026-10-01**. Build, Flash loading/readback and RTX5 execution passed
on all eight boards: the original six on 2026-09-28, STM32F4-DISCO on 2026-09-29,
and NUCLEO-F446RE on 2026-10-01.
Both debuggers use the same image where tested. Board prerequisites
and configuration are in [Board support](BOARD_SUPPORT.md); capture settings and
commands are in [Debugger profiles](DEBUG_PROBES.md) and [Trace workflow](TRACE_APP.md).
An additional L552 board passed the ST-LINK retest below after TrustZone/RDP recovery.

## Results

**PASS** means the measured capture passed DWT/ITM sequence and timing checks,
PC range checks, and decoder error/overflow checks. **FAIL** means a capture check
failed; **OPEN** means a finding remains unresolved; **—** means untested.
A PASS does not establish complete capture from reset or repeatable start/pause/end behavior.

| Board | Controlled SWO: ULINK+ | Controlled SWO: ST-LINK | IDE pause / debug end |
| --- | --- | --- | --- |
| MCBSTM32F400 | PASS | — | ULINK+: automatic CSV at pause/end verified; initial-sync loss and incomplete end packet |
| NUCLEO-L552ZE-Q | OPEN | PASS | ULINK+: automatic CSV verified; packet-integrity checks pending. ST-LINK: IDE test pending |
| NUCLEO-F756ZG | PASS | PASS | ULINK+: incomplete pause packet, corrupted PC at end despite decoder exit 0. ST-LINK: pause passes, end incomplete |
| STM32F429I-DISCO | FAIL | PASS | ULINK+: initial-sync and final-packet errors. ST-LINK: one pause → end sequence passes |
| NUCLEO-F401RE | PASS | PASS | ULINK+: incomplete pause packet; full end-packet checks pending. ST-LINK: one pause → end sequence passes |
| NUCLEO-F446RE | — | PASS | IDE test pending; command-line server shutdown reported an SWV-reader assertion after the valid capture was flushed |
| STM32H7B3I-DK | FAIL | — | ULINK+: incomplete/malformed packets at pause/end |
| STM32F4-DISCO (MB997 B-02) | PASS | PASS | ULINK+: unexpected ITM26 records at pause/resume boundaries; incomplete pause/end packets. ST-LINK: pause passes, end incomplete |

Controlled ULINK+ findings:

- **L552 — OPEN:** DWT/ITM pass; 113 PC values `0xFFFFFFBC` remain unexplained.
- **F756 — PASS:** applies to the controlled repeat; initial-sync failure was also observed.
- **F429/H7 — FAIL:** signal sequences are correct after synchronization, but initial data is lost.

Automatic CSV conversion and recording integrity are separate checks: a CSV file
or decoder exit 0 alone is insufficient. On F429, opening the RAW file before trace
setup passes a diagnostic ULINK+ capture; this is not an installed IDE fix. The
same ordering still fails initial synchronization on MCB and H7.

## Test scope

- Controlled captures run for 30 s, then halt the core and drain for 50 ms before
  stopping. A fixed drain delay does not prove an empty probe queue.
- Checks cover Flash readback, RTX threads and fault state, DWT sine/noise at
  100 ms, ITM1 counter at 200 ms, decoder errors/overflows and PC ranges. Startup
  BSS zero stores are separated from application values. Timing uses the configured
  clock; PC range checks do not prove instruction-boundary validity.
- STM32F4-DISCO also passed hardware-breakpoint and single-step checks with both probes.
- L552 was tested with hardware TrustZone disabled. Tests use the internal-memory
  and reset-clock baseline; they do not qualify external memory or other clock setups.

## NUCLEO-L552ZE-Q recovery and ST-LINK retest — 2026-09-30

**Build, Flash readback, RTX5 execution and controlled SWO: PASS.** This retest
used ST-LINK `066DFF393132534E43041740`, firmware `V2J46M33`, on another board
with `CPUID=0x410FD212` and `DBGMCU_IDCODE=0x10006472` (MCU Rev A).

Initially, `DAUTHSTATUS=0xAF`, the core could not be halted, and `TraceStart`
failed reading `RCC_AHB2ENR` at `0x4002104C`. FLASH option registers were also
inaccessible, including under reset. With CN11 pins 5–7 connected (BOOT0 high)
and a power cycle, STM32CubeProgrammer 2.19.0 Hotplug readback established
`RDP=0x55` (level 0.5), `TZEN=1`, `BOOT_LOCK=0`, `nSWBOOT0=1`, and
`NSBOOTADD1=0x17F200`. After explicit authorization, regression to `RDP=0xAA`,
`TZEN=0` succeeded. Independent option-byte readback and a full 512 KiB Flash
blank check verified the recovery. The temporary BOOT0 jumper was removed
before programming the unchanged trace example.

The image matched its BIN readback. The IDE reached `main`, all five RTX tasks
were present, and a conditional breakpoint at ITM counter 5 was hit with no
fault flags. A subsequent 30.006 s controlled capture at 4 MHz core clock /
1 Mbaud SWO produced 65,290 bytes: 299 samples each of sine and deterministic
noise, 150 consecutive ITM1 values (1–150), and 7,320 PC samples within executable
ELF sections. Median DWT intervals were 99.99325 ms; ITM intervals were
199.9865 ms. Runtime reported `g_app_state=1`, `g_trace_itm_dropped=0`, and
`CFSR=HFSR=0`. Decoder exit was 0 with no error or overflow records.

The startup boundary remains incomplete: both DWT streams begin at application
index 2 and ITM begins at 1. No rows were discarded for the passing checks.
This result validates the captured steady sequence and timing, not complete
delivery from reset or IDE pause/end recording integrity.

Local evidence (ignored by Git): recovery logs and option-byte readbacks under
`.trace/captures/NUCLEO-L552ZE-Q-20260930-access/`; ELF/profile snapshots,
RAW/CSV, runtime and analysis reports under
`.trace/captures/NUCLEO-L552ZE-Q-20260930-test/`. No firmware or Pack changes
were required.

## NUCLEO-F446RE ST-LINK validation — 2026-10-01

**Build, Flash readback, RTX5 execution and controlled SWO: PASS.** The connected
NUCLEO-F446RE used its onboard ST-LINK/V2-1 with firmware `V2J43M28`. pyOCD
identified `STM32F446RETx`, Cortex-M4 r0p1, four DWT watchpoints, ITM, TPIU and
ETM. The linked image used 15,008 bytes of Flash; all loadable sections matched
the target readback.

Runtime inspection reported `g_app_state=1`, a 16 MHz core clock,
`g_trace_itm_dropped=0`, and `CFSR=HFSR=0`. An approximately 18 s command-line
capture at 16 MHz core clock / 1 Mbaud SWO produced 147,677 bytes: 180 valid
samples each of the sine and deterministic-noise sequences, 90 consecutive ITM1
values (3–92), and 17,582 PC samples within executable ELF text. Median DWT
intervals were 99.926 ms and the ITM median was 199.988 ms. ctrace reported no
decoder diagnostic or overflow records.

The capture began after the first application updates, so it does not establish
complete delivery from reset. IDE pause/end conversion remains untested. Stopping
the command-line GDB server with Ctrl-C logged an SWV-reader assertion after the
RAW file was flushed; the resulting RAW decoded successfully and passed the
checks above.

## Open work

- [ ] Resolve the capture-start and pause/end failures listed above, and the
  L552 ULINK+ PC values; their exception-return interpretation is unconfirmed.
- [ ] Extend pause/resume/end and stop/restart tests for both probes, plus endurance
  and Trace Buffer tests. On H7, Pack `TraceStop` disables clocks/routing that
  `TraceStart` alone does not re-enable; validate restart within the same session.
- [ ] Configure and validate the H7 `STLink` set/profile: Flash loading, RTX5
  execution, SWO and automatic pause/end CSV conversion.
- [ ] Confirm physical board revisions and unresolved connector/variant details
  listed in the [board references](BOARD_SUPPORT.md).
