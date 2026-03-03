/***************************************************************************************
* Copyright (c) 2014-2021 Zihao Yu, Nanjing University
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

#define def_ldst_load_template(name, rtl_instr, width, mmu_mode) \
  def_EHelper(name) { \
    word_t addr = *dsrc1 + id_src2->imm; \
    concat(rtl_, rtl_instr) (s, ddest, dsrc1, id_src2->imm, width, mmu_mode); \
    IFDEF(CONFIG_RV_DASICS, \
      *ddest = dasics_sreg_load_gate(s->pc, s->isa.instr.i.rd, \
          s->isa.instr.i.rs1, addr, *ddest); \
    ); \
  }

#define def_ldst_store_template(name, width, mmu_mode) \
  def_EHelper(name) { \
    word_t addr = *dsrc1 + id_src2->imm; \
    word_t data = *ddest; \
    IFDEF(CONFIG_RV_DASICS, \
      data = dasics_sreg_store_gate(s->pc, s->isa.instr.s.rs2, \
          s->isa.instr.s.rs1, addr, data); \
    ); \
    rtl_sm(s, &data, dsrc1, id_src2->imm, width, mmu_mode); \
  }

#define def_all_ldst(suffix, mmu_mode) \
  def_ldst_load_template(concat(ld , suffix), lms, 8, mmu_mode) \
  def_ldst_load_template(concat(lw , suffix), lms, 4, mmu_mode) \
  def_ldst_load_template(concat(lh , suffix), lms, 2, mmu_mode) \
  def_ldst_load_template(concat(lb , suffix), lms, 1, mmu_mode) \
  def_ldst_load_template(concat(lwu, suffix), lm , 4, mmu_mode) \
  def_ldst_load_template(concat(lhu, suffix), lm , 2, mmu_mode) \
  def_ldst_load_template(concat(lbu, suffix), lm , 1, mmu_mode) \
  def_ldst_store_template(concat(sd , suffix), 8, mmu_mode) \
  def_ldst_store_template(concat(sw , suffix), 4, mmu_mode) \
  def_ldst_store_template(concat(sh , suffix), 2, mmu_mode) \
  def_ldst_store_template(concat(sb , suffix), 1, mmu_mode)

def_all_ldst(, MMU_DIRECT)
def_all_ldst(_mmu, MMU_TRANSLATE)
