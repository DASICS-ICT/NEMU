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

// The following RVC instructions are excluded
// (1) not present in RV64
//       C.LQSP  C.SQSP
//       C.LQ    C.SQ
//       C.JAL
// (2) seem not frequently present during execution
//       C.LDSP  C.LWSP  C.SDSP  C.SWSP
//       C.ADDI4SPN
// (3) only expansion without optimization
//       C.LD    C.LW    C.SD    C.SW
//       C.LUI
// (4) still not considered
//       C.FLDSP C.FLWSP C.FSDSP C.FSWSP
//       C.FLD   C.FLW   C.FSD   C.FSW
// (5) redundant from the aspect of EHelper
//       C.ADDI16SP (the same as C.ADDI)
//       C.NOP      (the same as C.ADDI)

def_EHelper(c_j) {
  IFDEF(CONFIG_RV_DASICS, rtl_dasics_jcheck(s, id_src1->imm));
  rtl_j(s, id_src1->imm);
}

def_EHelper(c_jr) {
#ifdef CONFIG_SHARE
  // See rvi/control.h:26. JALR should set the LSB to 0.
  rtl_andi(s, s0, dsrc1, ~1UL);
  IFDEF(CONFIG_RV_DASICS, rtl_dasics_jcheck(s, *(vaddr_t *)s0));

  // Zicfilp: C.JR is equivalent to JALR with rd=x0, rs1=rs1
  // Per specification (Listing 6): set ELP when (rs1 != x1) && (rs1 != x5) && (rs1 != x7)
#ifdef CONFIG_RV_ZICFILP
  if (zicfilp_lp_enabled()) {
    // Get rs1 register index from decoded operand (preg points to cpu.gpr[rs1])
    uint32_t rs1 = (id_src1->preg - &cpu.gpr[0]._64);
    // printf("[NEMU-REF-ELP] C.JR at PC=0x%016lx: rs1=x%u, mode=%lu, will_set_elp=%d\n",
    //        s->pc, rs1, cpu.mode, (rs1 != 1 && rs1 != 5 && rs1 != 7) ? 1 : 0);
    // Set ELP if rs1 is NOT x1 (ra), x5 (t0), or x7 (t2)
    if (rs1 != 1 && rs1 != 5 && rs1 != 7) {
      zicfilp_set_elp();
    }
  }
#endif  // CONFIG_RV_ZICFILP

  rtl_jr(s, s0);
#else
//  IFDEF(CONFIG_ENGINE_INTERPRETER, rtl_andi(s, s0, s0, ~0x1u));
  IFDEF(CONFIG_RV_DASICS, rtl_dasics_jcheck(s, *(vaddr_t *)dsrc1));

  // Zicfilp: C.JR is equivalent to JALR with rd=x0, rs1=rs1
  // Per specification (Listing 6): set ELP when (rs1 != x1) && (rs1 != x5) && (rs1 != x7)
#ifdef CONFIG_RV_ZICFILP
  if (zicfilp_lp_enabled()) {
    // Get rs1 register index from decoded operand (preg points to cpu.gpr[rs1])
    uint32_t rs1 = (id_src1->preg - &cpu.gpr[0]._64);
    // Set ELP if rs1 is NOT x1 (ra), x5 (t0), or x7 (t2)
    if (rs1 != 1 && rs1 != 5 && rs1 != 7) {
      zicfilp_set_elp();
    }
  }
#endif  // CONFIG_RV_ZICFILP

  IFNDEF(CONFIG_DIFFTEST_REF_NEMU, difftest_skip_dut(1, 2));
  rtl_jr(s, dsrc1);
#endif
}

def_EHelper(c_jalr) {
#ifdef CONFIG_SHARE
  // See rvi/control.h:26. JALR should set the LSB to 0.
  rtl_andi(s, s0, dsrc1, ~1UL);
  IFDEF(CONFIG_RV_DASICS, rtl_dasics_jcheck(s, *(vaddr_t *)s0));
  // Zicfilp: C.JALR is equivalent to JALR with rd=x1, rs1=rs1
  // Per specification (Listing 6): set ELP when (rs1 != x1) && (rs1 != x5) && (rs1 != x7)
#ifdef CONFIG_RV_ZICFILP
  if (zicfilp_lp_enabled()) {
    // Get rs1 register index from decoded operand (preg points to cpu.gpr[rs1])
    uint32_t rs1 = (id_src1->preg - &cpu.gpr[0]._64);
    printf("[NEMU-REF-ELP] C.JALR at PC=0x%016lx: rs1=x%u, mode=%lu, will_set_elp=%d\n",
           s->pc, rs1, cpu.mode, (rs1 != 1 && rs1 != 5 && rs1 != 7) ? 1 : 0);
    // Set ELP if rs1 is NOT x1 (ra), x5 (t0), or x7 (t2)
    if (rs1 != 1 && rs1 != 5 && rs1 != 7) {
      zicfilp_set_elp();
    }
  }
#endif  // CONFIG_RV_ZICFILP
  rtl_li(s, &cpu.gpr[1]._64, s->snpc);
  rtl_jr(s, s0);
#else
  IFDEF(CONFIG_RV_DASICS, rtl_dasics_jcheck(s, *(vaddr_t *)dsrc1));
  // Zicfilp: C.JALR is equivalent to JALR with rd=x1, rs1=rs1
  // Per specification (Listing 6): set ELP when (rs1 != x1) && (rs1 != x5) && (rs1 != x7)
#ifdef CONFIG_RV_ZICFILP
  if (zicfilp_lp_enabled()) {
    // Get rs1 register index from decoded operand (preg points to cpu.gpr[rs1])
    uint32_t rs1 = (id_src1->preg - &cpu.gpr[0]._64);
    // Set ELP if rs1 is NOT x1 (ra), x5 (t0), or x7 (t2)
    if (rs1 != 1 && rs1 != 5 && rs1 != 7) {
      zicfilp_set_elp();
    }
  }
#endif  // CONFIG_RV_ZICFILP
  rtl_li(s, &cpu.gpr[1]._64, s->snpc);
//  IFDEF(CONFIG_ENGINE_INTERPRETER, rtl_andi(s, s0, s0, ~0x1lu));
  IFNDEF(CONFIG_DIFFTEST_REF_NEMU, difftest_skip_dut(1, 2));
  rtl_jr(s, dsrc1);
#endif
}

def_EHelper(c_beqz) {
  rtl_jrelop(s, RELOP_EQ, dsrc1, rz, id_dest->imm);
}

def_EHelper(c_bnez) {
  rtl_jrelop(s, RELOP_NE, dsrc1, rz, id_dest->imm);
}

def_EHelper(c_li) {
  rtl_li(s, ddest, id_src2->imm);
}

def_EHelper(c_addi) {
  rtl_addi(s, ddest, ddest, id_src2->imm);
}

def_EHelper(c_addiw) {
  rtl_addiw(s, ddest, ddest, id_src2->imm);
}

def_EHelper(c_slli) {
  rtl_shli(s, ddest, ddest, id_src2->imm);
}

def_EHelper(c_srli) {
  rtl_shri(s, ddest, ddest, id_src2->imm);
}

def_EHelper(c_srai) {
  rtl_sari(s, ddest, ddest, id_src2->imm);
}

def_EHelper(c_andi) {
  rtl_andi(s, ddest, ddest, id_src2->imm);
}

def_EHelper(c_mv) {
  rtl_mv(s, ddest, dsrc1);
}

def_EHelper(c_add) {
  rtl_add(s, ddest, ddest, dsrc2);
}

def_EHelper(c_and) {
  rtl_and(s, ddest, ddest, dsrc2);
}

def_EHelper(c_or) {
  rtl_or(s, ddest, ddest, dsrc2);
}

def_EHelper(c_xor) {
  rtl_xor(s, ddest, ddest, dsrc2);
}

def_EHelper(c_sub) {
  rtl_sub(s, ddest, ddest, dsrc2);
}

def_EHelper(c_addw) {
  rtl_addw(s, ddest, ddest, dsrc2);
}

def_EHelper(c_subw) {
  rtl_subw(s, ddest, ddest, dsrc2);
}
