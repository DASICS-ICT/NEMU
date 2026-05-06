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

#include <isa.h>
#include <cpu/decode.h>
#include "../local-include/dasics_treg_zero.h"
#include "../local-include/csr.h"

#ifdef CONFIG_RV_DASICS_TREG_ZERO

#include "../local-include/reg.h"

const rtlreg_t dasics_treg_zero_int_zero = 0;
const rtlreg_t dasics_treg_zero_fp_zero = 0;

static bool dasics_treg_zero_int_is_protected(int idx) {
  return (DASICS_TREG_ZERO_INT_CLEAR_MASK & (1u << idx)) != 0;
}

static bool dasics_treg_zero_fp_is_protected(int idx) {
  return (DASICS_TREG_ZERO_FP_CLEAR_MASK & (1u << idx)) != 0;
}

void dasics_treg_zero_reset(void) {
  cpu.dasics_treg_zero_int_init_bits = DASICS_TREG_ZERO_INIT_ALL;
  cpu.dasics_treg_zero_fp_init_bits = DASICS_TREG_ZERO_INIT_ALL;
  cpu.dasics_treg_zero_pending_clear = false;
  cpu.dasics_treg_zero_sreg_not_cleaned = false;
}

bool dasics_treg_zero_is_untrusted_now(vaddr_t pc) {
  return !dasics_in_trusted_zone(pc);
}

bool dasics_treg_zero_rewrite_context(vaddr_t pc) {
  return dsmcfg->mcfg_uena &&
    (dasics_treg_zero_is_untrusted_now(pc) ||
     cpu.dasics_treg_zero_sreg_not_cleaned);
}

void dasics_treg_zero_trap_entry(vaddr_t epc) {
  if (cpu.mode == MODE_U &&
      dsmcfg->mcfg_uena &&
      dasics_treg_zero_is_untrusted_now(epc)) {
    cpu.dasics_treg_zero_sreg_not_cleaned = true;
  }
}

static bool dasics_treg_zero_xret_target_is_untrusted(uint64_t return_mode, vaddr_t target_pc) {
  uint64_t old_mode = cpu.mode;
  cpu.mode = return_mode;
  bool untrusted = dasics_treg_zero_is_untrusted_now(target_pc);
  cpu.mode = old_mode;
  return untrusted;
}

void dasics_treg_zero_xret(bool legal, uint64_t return_mode, vaddr_t target_pc) {
  if (legal &&
      return_mode == MODE_U &&
      dsmcfg->mcfg_uena &&
      dasics_treg_zero_xret_target_is_untrusted(return_mode, target_pc)) {
    cpu.dasics_treg_zero_sreg_not_cleaned = false;
  }
}

bool dasics_treg_zero_sreg_not_cleaned(void) {
  return cpu.dasics_treg_zero_sreg_not_cleaned;
}

bool dasics_treg_zero_int_src_is_init(int rs) {
  int idx = check_reg_index(rs);
  return idx == 0 ||
    !dasics_treg_zero_int_is_protected(idx) ||
    (cpu.dasics_treg_zero_int_init_bits & (1u << idx));
}

bool dasics_treg_zero_fp_src_is_init(int rs) {
  int idx = check_reg_index(rs);
  return !dasics_treg_zero_fp_is_protected(idx) ||
    (cpu.dasics_treg_zero_fp_init_bits & (1u << idx));
}

void dasics_treg_zero_mark_pending_clear(void) {
  cpu.dasics_treg_zero_pending_clear = true;
}

void dasics_treg_zero_commit_hook(const struct Decode *s) {
  if (cpu.dasics_treg_zero_pending_clear) {
    cpu.dasics_treg_zero_int_init_bits &= ~DASICS_TREG_ZERO_INT_CLEAR_MASK;
    cpu.dasics_treg_zero_fp_init_bits &= ~DASICS_TREG_ZERO_FP_CLEAR_MASK;
    cpu.dasics_treg_zero_pending_clear = false;
  }

  if (!dasics_treg_zero_rewrite_context(s->pc)) return;

  if (s->dest.reg_idx >= 1 && s->dest.reg_idx < 32) {
    if (s->dest.reg_is_fp) {
      cpu.dasics_treg_zero_fp_init_bits |= (1u << s->dest.reg_idx);
    } else {
      cpu.dasics_treg_zero_int_init_bits |= (1u << s->dest.reg_idx);
    }
  }
}

rtlreg_t *dasics_treg_zero_fp_src_addr(const struct Decode *s, int idx) {
  if (dasics_treg_zero_rewrite_context(s->pc) && !dasics_treg_zero_fp_src_is_init(idx)) {
    return (rtlreg_t *)&dasics_treg_zero_fp_zero;
  }
  return &fpreg_l(idx);
}

#endif
