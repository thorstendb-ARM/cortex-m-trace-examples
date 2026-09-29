/* SPDX-License-Identifier: Apache-2.0 */
#ifndef TRACE_DWT_WORKLOAD_H
#define TRACE_DWT_WORKLOAD_H

#include <stdint.h>

/* Each aligned 32-bit variable has one writer and one DWT write comparator. */
extern volatile int32_t g_trace_sine;
extern volatile int32_t g_trace_noise;

/* Call each function from its own thread every 100 ms. */
void dwt_sine_update(void);
void dwt_noise_update(void);

#endif
