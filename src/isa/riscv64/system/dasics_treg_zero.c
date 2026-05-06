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

void dasics_treg_zero_reset(void) {
  cpu.dasics_treg_zero_int_init_bits = DASICS_TREG_ZERO_INIT_ALL;
  cpu.dasics_treg_zero_fp_init_bits = DASICS_TREG_ZERO_INIT_ALL;
  cpu.dasics_treg_zero_pending_clear = false;
}

bool dasics_treg_zero_is_untrusted_now(vaddr_t pc) {
  return !dasics_in_trusted_zone(pc);
}

bool dasics_treg_zero_int_src_is_init(int rs) {
  int idx = check_reg_index(rs);
  return idx == 0 || (cpu.dasics_treg_zero_int_init_bits & (1u << idx));
}

bool dasics_treg_zero_fp_src_is_init(int rs) {
  int idx = check_reg_index(rs);
  return cpu.dasics_treg_zero_fp_init_bits & (1u << idx);
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

  if (!dasics_treg_zero_is_untrusted_now(s->pc)) return;

  if (s->dest.reg_idx >= 1 && s->dest.reg_idx < 32) {
    if (s->dest.reg_is_fp) {
      cpu.dasics_treg_zero_fp_init_bits |= (1u << s->dest.reg_idx);
    } else {
      cpu.dasics_treg_zero_int_init_bits |= (1u << s->dest.reg_idx);
    }
  }
}

rtlreg_t *dasics_treg_zero_fp_src_addr(const struct Decode *s, int idx) {
  if (dasics_treg_zero_is_untrusted_now(s->pc) && !dasics_treg_zero_fp_src_is_init(idx)) {
    return (rtlreg_t *)&dasics_treg_zero_fp_zero;
  }
  return &fpreg_l(idx);
}

#endif
