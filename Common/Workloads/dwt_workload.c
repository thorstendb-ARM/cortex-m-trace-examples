/* SPDX-License-Identifier: Apache-2.0 */
#include "dwt_workload.h"

_Alignas(4) volatile int32_t g_trace_sine;
_Alignas(4) volatile int32_t g_trace_noise;

void dwt_sine_update(void)
{
    /* Amplitude 1000, 20 samples per 2-second period at a 100-ms interval. */
    static const int32_t samples[] = {
           0,  309,  588,  809,  951, 1000,  951,  809,  588,  309,
           0, -309, -588, -809, -951,-1000, -951, -809, -588, -309
    };
    static uint32_t index;

    /* Exactly one store to the watched variable per update. */
    g_trace_sine = samples[index];
    index = (index + 1U) % (sizeof(samples) / sizeof(samples[0]));
}

void dwt_noise_update(void)
{
    /* Deterministic xorshift32 with a nonzero seed; not a random entropy source. */
    static uint32_t state = 0x6D2B79F5U;
    state ^= state << 13;
    state ^= state >> 17;
    state ^= state << 5;

    g_trace_noise = (int32_t)(state % 2001U) - 1000;
}
