/* SPDX-License-Identifier: Apache-2.0 */
#ifndef TRACE_OUTPUT_H
#define TRACE_OUTPUT_H

#include <stdbool.h>
#include <stdint.h>

/* Call from privileged Thread mode. Never waits or changes trace configuration.
 * Returns false when capture is disabled or the stimulus port is not ready.
 */
bool trace_itm1_try_write_u32(uint32_t value);

#endif
