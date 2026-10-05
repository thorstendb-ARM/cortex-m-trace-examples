/* SPDX-License-Identifier: Apache-2.0 */
#include "cmsis_os2.h"
#include "app.h"
#include "target.h"
#include "dwt_workload.h"
#include "trace.h"
#if defined(TRACE_STACK_CORRUPTION)
#include "stack_corruption.h"
#endif

enum app_state {
    APP_STARTING,
    APP_RUNNING,
    APP_ERROR
};

/* Debugger-visible application state. A running app does not prove capture. */
volatile enum app_state g_app_state = APP_STARTING;
volatile uint32_t g_app_core_clock_hz;
volatile uint32_t g_trace_itm_counter;
volatile uint32_t g_trace_itm_dropped;

static uint32_t signal_period_ticks;
static uint32_t counter_period_ticks;

static bool wait_for_next_period(uint32_t *deadline, uint32_t period)
{
    *deadline += period;
    osStatus_t status = osDelayUntil(*deadline);
    if (status == osErrorParameter) {
        /* An overrun or debug halt must not cause a burst of catch-up samples.
         * Normal operation uses absolute deadlines; resume from now when late.
         */
        *deadline = osKernelGetTickCount() + period;
        status = osDelayUntil(*deadline);
    }
    if (status != osOK) {
        g_app_state = APP_ERROR;
        return false;
    }
    return true;
}

static void sine_thread(void *argument)
{
    (void)argument;
    uint32_t deadline = osKernelGetTickCount();
    do {
        dwt_sine_update();
    } while (wait_for_next_period(&deadline, signal_period_ticks));
    osThreadExit();
}

static void noise_thread(void *argument)
{
    (void)argument;
    uint32_t deadline = osKernelGetTickCount();
    do {
        dwt_noise_update();
    } while (wait_for_next_period(&deadline, signal_period_ticks));
    osThreadExit();
}

static void counter_thread(void *argument)
{
    (void)argument;
    uint32_t deadline = osKernelGetTickCount();
    do {
        /* Emit raw uint32 values 0, 1, 2, ...; gaps reveal unavailable output.
         * Unsigned wrap at UINT32_MAX is intentional for a long-running test.
         */
        if (!trace_itm1_try_write_u32(g_trace_itm_counter)) {
            ++g_trace_itm_dropped;
        }
        ++g_trace_itm_counter;
    } while (wait_for_next_period(&deadline, counter_period_ticks));
    osThreadExit();
}

int app_main(void)
{
    static const osThreadAttr_t sine_attributes = {
        .name = "Sine100ms",
        .stack_size = 1024U,
        .priority = osPriorityNormal
    };
    static const osThreadAttr_t noise_attributes = {
        .name = "Noise100ms",
        .stack_size = 1024U,
        .priority = osPriorityNormal
    };
    static const osThreadAttr_t counter_attributes = {
        .name = "ITM1_200ms",
        /* RTX defaults to unprivileged threads. ITM/DCB accesses require this. */
        .attr_bits = osThreadPrivileged,
        .stack_size = 1024U,
        .priority = osPriorityNormal
    };

    g_app_core_clock_hz = target_core_clock_hz();
    if (osKernelInitialize() != osOK) {
        g_app_state = APP_ERROR;
        return -1;
    }

    const uint32_t tick_hz = osKernelGetTickFreq();
    if ((tick_hz < 10U) || ((tick_hz % 10U) != 0U)) {
        /* Both 100 ms and 200 ms must be exactly representable in RTX ticks. */
        g_app_state = APP_ERROR;
        return -1;
    }
    signal_period_ticks = tick_hz / 10U;
    counter_period_ticks = tick_hz / 5U;

    if ((osThreadNew(sine_thread, NULL, &sine_attributes) == NULL) ||
        (osThreadNew(noise_thread, NULL, &noise_attributes) == NULL) ||
        (osThreadNew(counter_thread, NULL, &counter_attributes) == NULL)) {
        g_app_state = APP_ERROR;
        return -1;
    }

#if defined(TRACE_STACK_CORRUPTION)
    if (!stack_corruption_start(2U * tick_hz)) {
        g_app_state = APP_ERROR;
        return -1;
    }
#endif

    g_app_state = APP_RUNNING;
    (void)osKernelStart();
    g_app_state = APP_ERROR;
    return -1;
}
