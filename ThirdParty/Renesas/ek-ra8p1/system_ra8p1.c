/*
 * Copyright (c) 2022 Arm Limited. All rights reserved.
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
 * Adapted from ARM::Cortex_DFP@1.1.0, Device/ARMCM85/Source/system_ARMCM85.c.
 */

#include "ra8p1.h"

extern const VECTOR_TABLE_Type __VECTOR_TABLE[RA8P1_VECTOR_COUNT];

void SystemInit(void)
{
    SCB->VTOR = (uint32_t) (uintptr_t) &__VECTOR_TABLE[0];

    /* Cortex-M85 template setup for low-overhead loops and branch prediction.
     * Instruction/data caches, SAU partitioning and vendor registers retain
     * their reset settings. The project disables FPU, MVE and PAC/BTI use.
     */
    SCB->CCR |= SCB_CCR_LOB_Msk | SCB_CCR_BP_Msk;
    __DSB();
    __ISB();
}
