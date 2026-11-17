/* SPDX-License-Identifier: Apache-2.0 */
#include CMSIS_device_header
#include "target.h"

/* RA8P1 hardware manual Rev. 1.30: SCKSCR (p. 332), SCKDIVCR2
 * (p. 330), MOCOCR (p. 343). Recognize the reset CPU0 clock only.
 */
#define SCKSCR    (*(volatile const uint8_t *)0x4001E026UL)
#define SCKDIVCR2 (*(volatile const uint16_t *)0x4001E024UL)
#define MOCOCR    (*(volatile const uint8_t *)0x4001E038UL)
#define MOCO_HZ   8000000U

uint32_t SystemCoreClock = MOCO_HZ;

void SystemCoreClockUpdate(void)
{
    const uint32_t source = SCKSCR & 7U;
    const uint32_t divider = SCKDIVCR2 & 15U;
    SystemCoreClock = (source == 1U && divider == 0U && (MOCOCR & 1U) == 0U)
                          ? MOCO_HZ : 0U;
}

void target_init(void)
{
    SystemCoreClockUpdate();
    if (SystemCoreClock == 0U) {
        for (;;) {
            /* Reset the device; inherited clock configurations are unsupported. */
        }
    }
}

uint32_t target_core_clock_hz(void)
{
    return SystemCoreClock;
}
