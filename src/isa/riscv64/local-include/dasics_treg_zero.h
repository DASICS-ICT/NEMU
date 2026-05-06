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

#ifndef __RISCV64_DASICS_TREG_ZERO_H__
#define __RISCV64_DASICS_TREG_ZERO_H__

#include <common.h>
#include "reg.h"

struct Decode;

#ifdef CONFIG_RV_DASICS_TREG_ZERO

#define DASICS_TREG_ZERO_INT_CLEAR_MASK 0xF00000E0u
#define DASICS_TREG_ZERO_FP_CLEAR_MASK  0xF00000FFu
#define DASICS_TREG_ZERO_INIT_ALL       0xFFFFFFFFu

extern const rtlreg_t dasics_treg_zero_int_zero;
extern const rtlreg_t dasics_treg_zero_fp_zero;

// Reset private treg-zero init-bit state before guest execution starts.
void dasics_treg_zero_reset(void);

// Return true when PC belongs to a DASICS untrusted domain whose source reads
// must observe init-bit masking.
bool dasics_treg_zero_is_untrusted_now(vaddr_t pc);

// Return true when source reads should observe init-bit masking. ADR 0004
// extends the original untrusted-domain context with the trap cleanup window.
bool dasics_treg_zero_rewrite_context(vaddr_t pc);

// Maintain the ADR 0004 trap cleanup window state. trap_entry must be called
// before raise_intr() changes cpu.mode; xret is called only on decoded xRET.
void dasics_treg_zero_trap_entry(vaddr_t epc);
void dasics_treg_zero_xret(bool legal, uint64_t return_mode, vaddr_t target_pc);

// Expose the private state for focused checks and diagnostics.
bool dasics_treg_zero_sreg_not_cleaned(void);

// Query source init state for a logical GPR. x0 is always treated initialized.
bool dasics_treg_zero_int_src_is_init(int rs);

// Query source init state for a logical FPR.
bool dasics_treg_zero_fp_src_is_init(int rs);

// Record that a committed dasicscall.j/jr must clear caller-saved init bits.
// dasics_treg_zero_commit_hook() consumes this flag exactly once.
void dasics_treg_zero_mark_pending_clear(void);

// Run after an instruction commits: apply pending dasicscall clear first, then
// mark any untrusted destination register initialized.
void dasics_treg_zero_commit_hook(const struct Decode *s);

// Return the storage address used for an FPR source read, redirecting to the
// static zero word when the source is untrusted and uninitialized.
rtlreg_t *dasics_treg_zero_fp_src_addr(const struct Decode *s, int idx);

#define DASICS_TREG_ZERO_FP_SRC_ADDR(s, idx) dasics_treg_zero_fp_src_addr((s), (idx))

#else

#define DASICS_TREG_ZERO_FP_SRC_ADDR(s, idx) (&fpreg_l(idx))

#endif

#endif
