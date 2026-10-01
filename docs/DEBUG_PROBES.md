# Debugger selection

Debugger target sets in [`Trace.csolution.yml`](../Trace.csolution.yml) select the
probe and trace profile. Both probes use the same board layer and application
image. Build commands are in [BUILD.md](BUILD.md); measured results are in
[Validation](VALIDATION.md).

## Configured probes and profiles

All sets use SWD and SWO UART/NRZ file capture at **1 Mbaud**.

| Probe | Debugger name | Selection | SWD clock | PC period |
| --- | --- | --- | --- | --- |
| ULINK+ | `ULINKplus@pyOCD` | Automatic | 10 MHz; MCB uses the tool default | 8192 cycles |
| ST-LINK | `ST-Link@pyOCD` | Automatic | 4 MHz | 16384 cycles |

Both probe types use automatic selection without a fixed `probe-id`.
`pyocd list --probes` lists connected probes. When multiple probes of the same
type are connected, select the intended probe before loading an image.

| Target | Available target sets | Core / timestamp clock |
| --- | --- | --- |
| MCBSTM32F400 | `ULINKplus` (unnamed set) | 16 MHz |
| NUCLEO-L552ZE-Q | `ULINKplus`, `STLink` | 4 MHz |
| NUCLEO-F756ZG | `ULINKplus`, `STLink` | 16 MHz |
| STM32F429I-DISCO | `ULINKplus`, `STLink` | 16 MHz |
| NUCLEO-F401RE | `ULINKplus`, `STLink` | 16 MHz |
| NUCLEO-F446RE | `STLink` | 16 MHz |
| STM32H7B3I-DK | `ULINKplus` (unnamed set) | 64 MHz |
| STM32F4-DISCO (MB997 B-02) | `ULINKplus`, `STLink` | 16 MHz |

For the two unnamed sets, select `--active MCBSTM32F400` or
`--active STM32H7B3I-DK`, without an `@ULINKplus` suffix. The other boards
use named sets, for example `--active NUCLEO-F756ZG@ULINKplus`.

Only the PC-sampling period differs between a board's two trace profiles;
ST-LINK uses half the PC sample rate. The common sources and timestamp/sync
settings are described in [Trace application](TRACE_APP.md#configuration-ownership).

## Switch sets

1. Stop the active debug/capture session.
2. In **CMSIS: Manage Solution Settings**, select the target and available set,
   then save. Check probe selection and [board wiring](ST_BOARD_BRINGUP.md).
3. Build as needed and [regenerate the trace profile](TRACE_APP.md#configure-and-generate-trace)
   after an ELF/profile change. Use the profile matching the selected set.
4. Start the generated debugger configuration.

From an activated command-line environment, for example:

```sh
cbuild Trace.csolution.yml --active 'NUCLEO-F756ZG@STLink' --packs --frozen-packs
/path/to/pyTS out/Trace+NUCLEO-F756ZG.cbuild-run.yml --format json
```

The generated `.cbuild-run.yml` represents the active set and is replaced when
switching. Source and generated trace profiles include `@<set>` for named sets;
see the [file naming table](TRACE_APP.md#configuration-ownership).
