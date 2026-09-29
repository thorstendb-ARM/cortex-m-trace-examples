/* SPDX-License-Identifier: Apache-2.0 */
/* Memory selected from Keil::STM32H7xx_DFP@4.1.3, STM32H7B3LIHxQ.
 * Use one internal Flash region and one SRAM region for this baseline.
 * Additional banks and external memory are deliberately not linked yet.
 */
#ifndef TRACE_MEMORY_REGIONS_H
#define TRACE_MEMORY_REGIONS_H

#define __ROM0_BASE  0x08000000
#define __ROM0_SIZE  0x00100000
#define __RAM0_BASE  0x24000000
#define __RAM0_SIZE  0x00100000
#define __STACK_SIZE 0x00001000
#define __HEAP_SIZE  0x00000000

#endif
