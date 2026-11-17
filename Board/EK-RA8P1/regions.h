/* SPDX-License-Identifier: Apache-2.0 */
#ifndef EK_RA8P1_REGIONS_H
#define EK_RA8P1_REGIONS_H

/* RA8P1 hardware manual Rev. 1.30, pp. 238-239 and 3537-3543.
 * CPU0 code MRAM and SRAM0 only; no TCM or external memory.
 */
#define __ROM0_BASE  0x02000000
#define __ROM0_SIZE  0x00100000
#define __RAM0_BASE  0x22000000
#define __RAM0_SIZE  0x00080000
#define __STACK_SIZE 0x00001000
#define __HEAP_SIZE  0x00000000

#endif
