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
#include "../local-include/dasics_treg_zero.h"

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
  (void)pc;
  return false;
}

bool dasics_treg_zero_int_src_is_init(int rs) {
  (void)rs;
  return true;
}

bool dasics_treg_zero_fp_src_is_init(int rs) {
  (void)rs;
  return true;
}

void dasics_treg_zero_mark_pending_clear(void) {
}

void dasics_treg_zero_commit_hook(const struct Decode *s) {
  (void)s;
}

rtlreg_t *dasics_treg_zero_fp_src_addr(const struct Decode *s, int idx) {
  (void)s;
  return &fpreg_l(idx);
}

#endif
