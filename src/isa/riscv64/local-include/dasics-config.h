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

#include <stdbool.h>
#include <stdint.h>

#define DASICS_LIB_ENTRY_NUM 16
#define DASICS_LIB_CFG_SLOT_BITS 4
#define DASICS_LIB_CFG_WRITE 0x1
#define DASICS_LIB_CFG_READ 0x2
#define DASICS_LIB_CFG_VALID 0x8
#define DASICS_LIB_CFG_MASK 0xfULL
#define DASICS_JUMP_ENTRY_NUM 4
#define DASICS_JUMP_CFG_SLOT_BITS 16
#define DASICS_JUMP_CFG_VALID 0x1
#define DASICS_JUMP_CFG_MASK 0xffffULL

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
#define DASICS_MAIN_CFG_SENA (1ULL << 0)
#define DASICS_MAIN_CFG_UENA (1ULL << 1)
#define DASICS_MAIN_CFG_CUET (1ULL << 2)
#define DASICS_MAIN_CFG_CUST (1ULL << 3)
#define DASICS_MAIN_CFG_CULT (1ULL << 4)
#define DASICS_MAIN_CFG_CUFT (1ULL << 5)
#define DASICS_MAIN_CFG_CSET (1ULL << 6)
#define DASICS_MAIN_CFG_CSST (1ULL << 7)
#define DASICS_MAIN_CFG_CSLT (1ULL << 8)
#define DASICS_MAIN_CFG_CSFT (1ULL << 9)
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

static inline bool dasics_is_protected_csr(uint32_t addr) {
  return addr == DASICS_CSR_LIB_CFG ||
         (addr >= DASICS_CSR_LIB_BOUND_LO(0) && addr <= DASICS_CSR_LIB_BOUND_HI(DASICS_LIB_ENTRY_NUM - 1)) ||
         (addr >= DASICS_CSR_MAIN_CALL && addr <= DASICS_CSR_FREASON) ||
         (addr >= DASICS_CSR_JUMP_BOUND_LO(0) && addr <= DASICS_CSR_JUMP_BOUND_HI(DASICS_JUMP_ENTRY_NUM - 1)) ||
         addr == DASICS_CSR_JUMP_CFG ||
         (addr >= DASICS_CSR_UMAIN_CFG && addr <= DASICS_CSR_UMAIN_BOUND_HI) ||
         addr == DASICS_CSR_SMAIN_CFG ||
         addr == DASICS_CSR_SMAIN_BOUND_LO ||
         addr == DASICS_CSR_SMAIN_BOUND_HI;
}

#endif
