/* SPDX-License-Identifier: Apache-2.0 */
#include CMSIS_device_header
#include "target.h"

void target_init(void)
{
    /* Vendor SystemInit has run. Retain the internal-oscillator baseline. */
    SystemCoreClockUpdate();
}

uint32_t target_core_clock_hz(void)
{
    return SystemCoreClock;
}
