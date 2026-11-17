/*
 * Copyright (c) 2022-2023 Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the License); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an AS IS BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Adapted from ARM::Cortex_DFP@1.1.0, Device/ARMCM85/Include/ARMCM85.h.
 */

#ifndef RA8P1_H
#define RA8P1_H

#ifdef __cplusplus
extern "C" {
#endif

/* RA8P1 Hardware Manual Rev. 1.30, Cortex-M85 processor, pp. 115-116:
 * docs/renesas/ra8p1-group-users-manual-hardware.pdf.
 * Peripheral interrupt routing is outside this core-only board layer.
 */
#define RA8P1_DEVICE_IRQ_COUNT 96U
#define RA8P1_VECTOR_COUNT     (16U + RA8P1_DEVICE_IRQ_COUNT)

typedef enum IRQn {
    NonMaskableInt_IRQn   = -14,
    HardFault_IRQn        = -13,
    MemoryManagement_IRQn = -12,
    BusFault_IRQn         = -11,
    UsageFault_IRQn       = -10,
    SecureFault_IRQn      = -9,
    SVCall_IRQn           = -5,
    DebugMonitor_IRQn     = -4,
    PendSV_IRQn           = -2,
    SysTick_IRQn          = -1,
    IRQ0_IRQn             = 0,
    IRQ95_IRQn            = 95
} IRQn_Type;

#define __CM85_REV             0x0101U
#define __NVIC_PRIO_BITS       4U
#define __Vendor_SysTickConfig 0U
#define __VTOR_PRESENT         1U
#define __MPU_PRESENT          1U
#define __FPU_PRESENT          1U
#define __FPU_DP               1U
#define __DSP_PRESENT          1U
#define __SAUREGION_PRESENT    1U
#define __PMU_PRESENT          1U
#define __PMU_NUM_EVENTCNT     8U
#define __ICACHE_PRESENT       1U
#define __DCACHE_PRESENT       1U

#include "core_cm85.h"
#include "system_ra8p1.h"

#ifdef __cplusplus
}
#endif

#endif
