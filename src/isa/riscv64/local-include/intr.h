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

#ifndef __INTR_H__
#define __INTR_H__

#include <cpu/decode.h>
#include "csr.h"

enum {
  EX_IAM, // instruction address misaligned
  EX_IAF, // instruction address fault
  EX_II,  // illegal instruction
  EX_BP,  // breakpoint
  EX_LAM, // load address misaligned
  EX_LAF, // load address fault
  EX_SAM, // store/amo address misaligned
  EX_SAF, // store/amo address fault
  EX_ECU, // ecall from U-mode
  EX_ECS, // ecall from S-mode
  EX_RS0, // reserved
  EX_ECM, // ecall from M-mode
  EX_IPF, // instruction page fault
  EX_LPF, // load page fault
  EX_RS1, // reserved
  EX_SPF, // store/amo page fault
#ifdef CONFIG_RV_DASICS
  EX_DUIAF=24,  // DASICS user instruction access fault
  EX_DSIAF,     // DASICS supervisor instruction access fault
  EX_DULAF,     // DASICS user load access fault
  EX_DSLAF,     // DASICS supervisor load access fault
  EX_DUSAF,     // DASICS user store access fault
  EX_DSSAF,     // DASICS supervisor store access fault
  EX_DUEF,      // DASICS user ecall fault
  EX_DSEF,      // DASICS supervisor ecall fault
#endif  // CONFIG_RV_DASICS
#ifdef CONFIG_RV_MPK
  EX_PKULPF = 32, // protection key user load page fault
  EX_PKUSPF, // protection key user store page fault
  EX_PKSLPF, // protection key supervisor load page fault
  EX_PKSSPF, // protection key supervisor store page fault
#endif  // CONFIG_RV_MPK
};

// now NEMU does not support EX_IAM,
// so it may ok to use EX_IAM to indicate a successful memory access
#define MEM_OK 0

word_t raise_intr(word_t NO, vaddr_t epc);
#define return_on_mem_ex() do { if (cpu.mem_exception != MEM_OK) return; } while (0)
bool intr_deleg_S(word_t exceptionNO);
#ifdef CONFIG_RVN
bool intr_deleg_U(word_t exceptionNO);
#define INTR_TVAL_REG(ex) (*((intr_deleg_U(ex)) ? (word_t *)utval : \
                            ((intr_deleg_S(ex)) ? (word_t *)stval : \
                                                  (word_t *)mtval)))
#else
#define INTR_TVAL_REG(ex) (*((intr_deleg_S(ex)) ? (word_t *)stval : (word_t *)mtval))
#endif  // CONFIG_RVN

#endif
