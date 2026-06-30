/***************************************************************************************
* Copyright (c) 2014-2021 Zihao Yu, Nanjing University
* Copyright (c) 2020-2022 Institute of Computing Technology, Chinese Academy of Sciences
*
* NEMU is licensed under Mulan PSL v2.
* You can use this software according to the terms and conditions of the Mulan PSL v2.
* You may obtain a copy of Mulan PSL v2 at:
*          http://license.coscl.org.cn/MulanPSL2
*
* THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
* EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
* MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
*
* See the Mulan PSL v2 for more details.
***************************************************************************************/

#ifndef __DASICS_CONFIG_H__
#define __DASICS_CONFIG_H__

#define DASICS_LIB_ENTRY_NUM 16
#define DASICS_JUMP_ENTRY_NUM 4

#define DASICS_CSR_LIB_CFG 0x880
#define DASICS_CSR_LIB_BOUND_LO_BASE 0x890
#define DASICS_CSR_LIB_BOUND_HI_BASE 0x891
#define DASICS_CSR_LIB_BOUND_STRIDE 2
#define DASICS_CSR_LIB_BOUND_LO(index) (DASICS_CSR_LIB_BOUND_LO_BASE + ((index) * DASICS_CSR_LIB_BOUND_STRIDE))
#define DASICS_CSR_LIB_BOUND_HI(index) (DASICS_CSR_LIB_BOUND_HI_BASE + ((index) * DASICS_CSR_LIB_BOUND_STRIDE))

#define DASICS_CSR_MAIN_CALL 0x8b0
#define DASICS_CSR_RETURN_PC 0x8b1
#define DASICS_CSR_ACTIVE_ZONE_RETURN_PC 0x8b2
#define DASICS_CSR_FREASON 0x8b3

#define DASICS_CSR_JUMP_BOUND_LO_BASE 0x8c0
#define DASICS_CSR_JUMP_BOUND_HI_BASE 0x8c1
#define DASICS_CSR_JUMP_BOUND_STRIDE 2
#define DASICS_CSR_JUMP_BOUND_LO(index) (DASICS_CSR_JUMP_BOUND_LO_BASE + ((index) * DASICS_CSR_JUMP_BOUND_STRIDE))
#define DASICS_CSR_JUMP_BOUND_HI(index) (DASICS_CSR_JUMP_BOUND_HI_BASE + ((index) * DASICS_CSR_JUMP_BOUND_STRIDE))
#define DASICS_CSR_JUMP_CFG 0x8c8

#define DASICS_CSR_SFETCHCTL_FORBIDDEN_ALIAS 0x9e0
#define DASICS_CSR_UMAIN_CFG 0x9e1
#define DASICS_CSR_UMAIN_BOUND_LO 0x9e2
#define DASICS_CSR_UMAIN_BOUND_HI 0x9e3

#define DASICS_CSR_SMAIN_CFG 0xbc0
#define DASICS_CSR_SMAIN_BOUND_LO 0xbc2
#define DASICS_CSR_SMAIN_BOUND_HI 0xbc3

#define DASICS_CSR_FULL_MASK 0xffffffffffffffffULL
#define DASICS_MAIN_CFG_SMAIN_MASK 0x3ff
#define DASICS_MAIN_CFG_UMAIN_MASK 0x3e
#define DASICS_FREASON_MASK 0x7

#define DASICS_FREASON_NONE 0
#define DASICS_FREASON_ECALL 1
#define DASICS_FREASON_LOAD 2
#define DASICS_FREASON_STORE 3
#define DASICS_FREASON_JUMP 4
#define DASICS_FREASON_LOAD_MPK 5
#define DASICS_FREASON_STORE_MPK 6
#define DASICS_FREASON_RESERVED 7

#if DASICS_CSR_UMAIN_CFG == DASICS_CSR_SFETCHCTL_FORBIDDEN_ALIAS
#error "DasicsUMainCfg must not alias Sfetchctl at CSR 0x9e0"
#endif

#if defined(CONFIG_RV_DASICS) && defined(CONFIG_RV_MBMC)
#error "CONFIG_RV_DASICS conflicts with CONFIG_RV_MBMC at CSR 0xbc2"
#endif

#endif
