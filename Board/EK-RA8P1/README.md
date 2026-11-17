# Renesas EK-RA8P1

Target `EK-RA8P1`, debugger set `ULINKplus`, device
`Renesas::R7KA8P1KF:CPU0` (Cortex-M85). The board is fitted with
`R7KA8P1KFLCAC`; CPU1, the Cortex-M33, is outside this target.

## Firmware and dependencies

The layer uses `Renesas::RA_DFP@6.6.0`, CMSIS-Core 6.3.0 and RTX5 5.9.0.
Startup, core header and `SystemInit()` are adapted from the supplied
`Renesas_EK-RA8P1/RTOSDemo.csolution.yml` project, originally based on
`ARM::Cortex_DFP@1.1.0`. [The source manifest](../../ThirdParty/Renesas/sources.json)
records provenance, source hashes and local changes. The DFP's FSP-dependent
startup is not selected. No FSP generator, BSP or full SDK is required.

The image uses 1 MiB code MRAM at `0x02000000` and 512 KiB SRAM0 at
`0x22000000`, with a 4 KiB main stack and no C-library heap. TCM and external
memory are unused. The 112-entry `.vectors` table is aligned to 512 bytes.
The shared GCC linker template retains it at the MRAM origin and provides
`__StackTop`/`__StackLimit` and the CMSIS C-runtime copy table; newlib startup
clears `.bss`. RTX supplies SVC, PendSV and SysTick handlers.

CPU0 retains the **8 MHz MOCO reset clock**, with its divider at one.
`target_init()` checks the source, divider and oscillator state and stops
before RTX if that clock is not recognized (`SystemCoreClock == 0`). Start
from a device reset. The reference project's 1-GHz PLL/voltage/cache setup
is intentionally not imported: the reset-clock baseline also leaves adequate
SWO bandwidth for periodic PC sampling. The common RTX idle thread spins.

`trustzone: off`, FPU/MVE off and branch protection off are compiler settings.
They do not provision device security. The MRAM/SRAM and system/debug registers
must already be accessible to CPU0 and the external debugger. This project
changes no lifecycle, OTP, option or security configuration.

## Debug and trace preparation

Select **EK-RA8P1 → ULINKplus** in CMSIS Manage Solution Settings and build:

```sh
cbuild Trace.csolution.yml --active 'EK-RA8P1@ULINKplus' --packs --frozen-packs --update-rte
```

The firmware build has no custom preparation step. After the final build or
refresh, invoke `Use $prepare-ra8p1-trace` with an agent that can read this
repository's [skill](../../.agents/skills/prepare-ra8p1-trace/SKILL.md). It copies
the temporary [debug-run.yml](debug-run.yml) using the existing CMake executable
and generates the normal trace runtime with the installed pyTS.

Without an agent, run the same copy from the repository root:

```sh
cmake -E copy_if_different Board/EK-RA8P1/debug-run.yml out/Trace+EK-RA8P1.cbuild-run.yml
```

Then generate the trace runtime from the current ELF through the normal **Trace
Generation** view (or the bundled pyTS), as for the other targets. Use
**Enter Debug / Load & Debug** after generation. The debugger uses GDB port 3333.
A subsequent build, refresh or target change can replace the prepared description;
repeat preparation after that operation. No additional interpreter, YAML library
or CMSIS tools export is required. The skill is optional automation; the commands
also work for a fresh clone with the documented build/debug tools installed.

Trace uses the normal **file capture → automatic CSV conversion** workflow.
Pausing or ending debugging converts the RAW file to
`.trace/Trace+EK-RA8P1@ULINKplus.SWO.csv`. There is no live trace TCP service.

The unmodified DFP supplies no RA8P1 SWO sequences, processor/AP mapping or
`.dbgconf` defaults. The temporary debug description supplies:

- CPU0 on AP0, with CPU0-only processor resources and trace configuration.
- P209 SWO routing and the trace clock before CoreSight discovery and after reset.
  PRCR access enables are preserved while setting TRCKCR to MOCO `/8`.
- Legacy pyOCD ITM/TPIU setup; full trace setup is not enabled.
- The pinned DFP's programming algorithms and system descriptions, referenced
  through `${CMSIS_PACK_ROOT}`. Solution and ELF paths are relative to `out/`.

This is a maintained description for **RA_DFP 6.6.0**, not a general YAML patcher.
Keep its DFP paths, image paths, transport settings and resources consistent with
the layer and solution. Once the DFP/tool flow provides this behavior natively,
remove the template and preparation skill together and verify the generated
description.
Installed packs and the reference project remain unchanged.

SWD is 10 MHz. MOCO `/8` gives a **1 MHz trace input**, serialized at **1 Mbaud**;
CPU0 timestamps use **8 MHz**. The profile watches `g_trace_sine` and
`g_trace_noise`, enables ITM1, samples the PC every 8192 core cycles and requests
DWT synchronization every 16M cycles. RA8P1 CPU0 implements eight DWT comparators,
ITM and a dedicated SWO TPIU. pyTS allocates the watch comparators.

## Power and Debug In wiring

The board manual Rev. 1.04, section 5.2.2 (PDF p. 27), specifies:

| Setting | Debug In position |
| --- | --- |
| J6 | 2–3 |
| J8 | 1–2 |
| J9 | 1–2; holds the onboard debug MCU in reset |
| J29 | All four shunts: 1–2, 3–4, 5–6, 7–8 |
| External debugger | J13 (10-pin) or J20 (20-pin), correct pin-1 orientation |

P209/SWO is pin 6 on J13/J20. Supply board power separately through J10, J11
or J7 as described in section 5.1; VTref is a voltage reference. Change jumpers
with power disconnected. Confirm the physical board revision and probe locally
before loading. The solution retains automatic probe selection.

## References and validation

- [EK-RA8P1 v1 User's Manual](https://www.renesas.com/en/document/mat/ek-ra8p1-v1-users-manual), Rev. 1.04: power and Debug In, PDF pp. 23–28.
- [RA8P1 hardware manual](https://www.renesas.com/en/document/mah/ra8p1-group-users-manual-hardware), Rev. 1.30: CPU0 features pp. 115–116; debug/trace pp. 134–145; MRAM map pp. 238–239; clock registers pp. 330, 332, 343, 375–376; SRAM0 pp. 3537–3543.
- [Cortex-M85 TRM](https://developer.arm.com/documentation/101924/latest): DWT, ITM and TPIU.

Build, Load & Debug to `main`, RTX runtime at 8 MHz and automatic CSV creation
on pause passed on 2026-11-17 through ULINKplus. The capture contains both DWT
sources, ITM1 and PC samples. Capture integrity remains open: one invalid ITM
packet near startup and one incomplete packet at pause/EOF were reported.
The supplied reference project's 1-GHz ITM0 results do not validate this image.
See the single [validation record](../../docs/VALIDATION.md).
