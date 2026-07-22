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
#include <generated/autoconf.h>

def_EHelper(jal) {
  IFDEF(CONFIG_RV_DASICS, riscv64_dasics_jump_target_permit_check(s->pc, id_src1->imm));
  rtl_li(s, ddest, id_src2->imm);
  IFDEF(CONFIG_BR_LOG, br_log_commit(s->pc, id_src1->imm, 1, BR_JUMP));
  rtl_j(s, id_src1->imm);
}

def_EHelper(jalr) {
  // Described at 2.5 Control Transter Instructions
  // The target address is obtained by adding the sign-extended 12-bit I-immediate to the register rs1
  rtl_addi(s, s0, dsrc1, id_src2->imm);
  // then setting the least-significant bit of the result to zero.
  rtl_andi(s, s0, s0, ~1UL);
//  IFDEF(CONFIG_ENGINE_INTERPRETER, rtl_andi(s, s0, s0, ~0x1lu));
  IFDEF(CONFIG_RV_DASICS, riscv64_dasics_jump_target_permit_check(s->pc, *s0));
#ifdef CONFIG_GUIDED_EXEC
  if(cpu.guided_exec && cpu.execution_guide.force_set_jump_target) {
    rtl_li(s, ddest, cpu.execution_guide.jump_target);
  } else {
    rtl_li(s, ddest, s->snpc);
  }
#else
  rtl_li(s, ddest, s->snpc);
#endif
  IFNDEF(CONFIG_DIFFTEST_REF_NEMU, difftest_skip_dut(1, 3));
  rtl_jr(s, s0);
}

#ifdef CONFIG_RV_DASICS
def_EHelper(dasicscall_j) {
  riscv64_dasics_call_permit_check(s->pc);
  riscv64_dasics_write_return_pc(id_src2->imm);
  rtl_li(s, ddest, id_src2->imm);
  IFDEF(CONFIG_BR_LOG, br_log_commit(s->pc, id_src1->imm, 1, BR_JUMP));
  rtl_j(s, id_src1->imm);
}

def_EHelper(dasicscall_jr) {
  riscv64_dasics_call_permit_check(s->pc);
  rtl_addi(s, s0, dsrc1, id_src2->imm);
  rtl_andi(s, s0, s0, ~1UL);
  rtl_li(s, ddest, s->snpc);
  riscv64_dasics_write_return_pc(s->snpc);
  IFNDEF(CONFIG_DIFFTEST_REF_NEMU, difftest_skip_dut(1, 3));
  rtl_jr(s, s0);
}
#endif // CONFIG_RV_DASICS

def_EHelper(beq) {
  riscv64_dasics_jrelop(s, RELOP_EQ, dsrc1, dsrc2, id_dest->imm);
}

def_EHelper(bne) {
  riscv64_dasics_jrelop(s, RELOP_NE, dsrc1, dsrc2, id_dest->imm);
}

def_EHelper(blt) {
  riscv64_dasics_jrelop(s, RELOP_LT, dsrc1, dsrc2, id_dest->imm);
}

def_EHelper(bge) {
  riscv64_dasics_jrelop(s, RELOP_GE, dsrc1, dsrc2, id_dest->imm);
}

def_EHelper(bltu) {
  riscv64_dasics_jrelop(s, RELOP_LTU, dsrc1, dsrc2, id_dest->imm);
}

def_EHelper(bgeu) {
  riscv64_dasics_jrelop(s, RELOP_GEU, dsrc1, dsrc2, id_dest->imm);
}
