/* SPDX-License-Identifier: Apache-2.0 */
#ifndef TRACE_STACK_CORRUPTION_H
#define TRACE_STACK_CORRUPTION_H

#include <stdbool.h>
#include <stdint.h>

/* Create the fault-injection thread before starting the RTX kernel. */
bool stack_corruption_start(uint32_t delay_ticks);

#endif
