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
 * Adapted from ARM::Cortex_DFP@1.1.0, Device/ARMCM85/Source/startup_ARMCM85.c.
 */

#include "ra8p1.h"

extern uint32_t __INITIAL_SP;
extern uint32_t __STACK_LIMIT;
#if defined(__ARM_FEATURE_CMSE) && (__ARM_FEATURE_CMSE == 3U)
extern uint32_t __STACK_SEAL;
#endif
extern __NO_RETURN void __PROGRAM_START(void);

__NO_RETURN void Reset_Handler(void);
__NO_RETURN void Default_Handler(void);

void NMI_Handler(void) __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
void MemManage_Handler(void) __attribute__((weak, alias("Default_Handler")));
void BusFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
void UsageFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SecureFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SVC_Handler(void) __attribute__((weak, alias("Default_Handler")));
void DebugMon_Handler(void) __attribute__((weak, alias("Default_Handler")));
void PendSV_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void) __attribute__((weak, alias("Default_Handler")));

/* 16 core exceptions and 96 ICU interrupts require 512-byte VTOR alignment.
 * See RA8P1 Hardware Manual Rev. 1.30, pp. 115-116. RTX provides the strong
 * SVC, PendSV and SysTick handlers; unused peripheral slots trap here.
 */
extern const VECTOR_TABLE_Type __VECTOR_TABLE[RA8P1_VECTOR_COUNT];
const VECTOR_TABLE_Type __VECTOR_TABLE[RA8P1_VECTOR_COUNT]
    __VECTOR_TABLE_ATTRIBUTE __ALIGNED(512) = {
    (VECTOR_TABLE_Type) (&__INITIAL_SP),
    Reset_Handler,
    NMI_Handler,
    HardFault_Handler,
    MemManage_Handler,
    BusFault_Handler,
    UsageFault_Handler,
    SecureFault_Handler,
    0,
    0,
    0,
    SVC_Handler,
    DebugMon_Handler,
    0,
    PendSV_Handler,
    SysTick_Handler,
    [16 ... RA8P1_VECTOR_COUNT - 1U] = Default_Handler
};

__NO_RETURN void Reset_Handler(void)
{
    __set_PSP((uint32_t) (uintptr_t) &__INITIAL_SP);
    __set_MSPLIM((uint32_t) (uintptr_t) &__STACK_LIMIT);
    __set_PSPLIM((uint32_t) (uintptr_t) &__STACK_LIMIT);

#if defined(__ARM_FEATURE_CMSE) && (__ARM_FEATURE_CMSE == 3U)
    __TZ_set_STACKSEAL_S((uint32_t *) &__STACK_SEAL);
#endif

    SystemInit();
    __PROGRAM_START();
}

__NO_RETURN void Default_Handler(void)
{
    for (;;) {
    }
}
