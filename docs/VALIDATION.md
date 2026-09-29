# Validation

Status: **2026-09-28**. Build, Flash loading/readback and RTX5 execution passed on
all six boards. Both debuggers use the same image where tested. Board prerequisites
and configuration are in [Board support](BOARD_SUPPORT.md); capture settings and
commands are in [Debugger profiles](DEBUG_PROBES.md) and [Trace workflow](TRACE_APP.md).

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
| STM32H7B3I-DK | FAIL | — | ULINK+: incomplete/malformed packets at pause/end |

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
- L552 was tested with hardware TrustZone disabled. Tests use the internal-memory
  and reset-clock baseline; they do not qualify external memory or other clock setups.

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
