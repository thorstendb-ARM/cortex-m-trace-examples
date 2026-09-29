/* SPDX-License-Identifier: Apache-2.0 */
#include CMSIS_device_header
#include "trace.h"

bool trace_itm1_try_write_u32(uint32_t value)
{
    /* The debugger/ctrace configuration owns DEMCR, TCR, TER and the trace path.
     * Check each gate before accessing the stimulus port; do not block an RTX
     * thread when a capture is stopped or the port FIFO is full.
     */
    if (((DCB->DEMCR & DCB_DEMCR_TRCENA_Msk) == 0U) ||
        ((ITM->TCR & ITM_TCR_ITMENA_Msk) == 0U) ||
        ((ITM->TER & (1UL << 1)) == 0U) ||
        (ITM->PORT[1].u32 == 0U)) {
        return false;
    }

    ITM->PORT[1].u32 = value;
    return true;
}
