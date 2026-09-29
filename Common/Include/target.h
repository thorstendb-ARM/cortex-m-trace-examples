/* SPDX-License-Identifier: Apache-2.0 */
#ifndef TRACE_TARGET_H
#define TRACE_TARGET_H

#include <stdint.h>

/* Called after the vendor startup/SystemInit and before starting RTX5. */
void target_init(void);
uint32_t target_core_clock_hz(void);

#endif
