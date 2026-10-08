/* SPDX-License-Identifier: Apache-2.0 */
#include "cmsis_compiler.h"
#include "cmsis_os2.h"
#include "rtx_os.h"
#include "stack_corruption.h"

/* RTX initializes word 0 to osRtxStackMagicWord (0xE25A2EA5). The trace watch
 * resolves this symbol to the actual thread stack, not a separate test canary.
 */
__ALIGNED(8) uint32_t g_stack_corruption_stack[64];

static osRtxThread_t thread_control_block;
static uint32_t corruption_delay_ticks;

static void stack_corruption_thread(void *argument)
{
    volatile uint32_t local_words[8];
    (void)argument;

    /* Leave time to inspect the intact RTX stack before the deliberate fault. */
    if (osDelay(corruption_delay_ticks) != osOK) {
        osThreadExit();
    }
    for (uint32_t i = 0U; i < 8U; ++i) {
        local_words[i] = i;
    }

    /* Inject an array-underflow write with a deliberately invalid byte offset.
     * Integer address arithmetic confines the injected error to the magic word:
     * no intermediate writes damage the live frame, saved registers or returns.
     * PSP stays within the 256-byte stack, so Cortex-M33 PSPLIM does not fault
     * before the watched STR instruction can emit its PC through DWT/SWO.
     */
    const uintptr_t local_address = (uintptr_t)&local_words[0];
    const uintptr_t invalid_offset =
        local_address - (uintptr_t)&g_stack_corruption_stack[0];
    volatile uint32_t *bad_destination =
        (volatile uint32_t *)(local_address - invalid_offset);
    *bad_destination = 0xDEADC0DEU;

    /* Keep RTX stack checking enabled. This switch detects the overwritten
     * magic and enters the standard osRtxErrorNotify stack-overflow handler.
     */
    (void)osDelay(1U);
    osThreadExit();
}

bool stack_corruption_start(uint32_t delay_ticks)
{
    static const osThreadAttr_t attributes = {
        .name = "StackCorruption",
        .cb_mem = &thread_control_block,
        .cb_size = sizeof(thread_control_block),
        .stack_mem = g_stack_corruption_stack,
        .stack_size = sizeof(g_stack_corruption_stack),
        .priority = osPriorityNormal
    };

    corruption_delay_ticks = delay_ticks;
    return osThreadNew(stack_corruption_thread, NULL, &attributes) != NULL;
}
