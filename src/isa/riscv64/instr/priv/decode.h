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

static inline def_DHelper(csr) {
  decode_op_r(s, id_src1, s->isa.instr.i.rs1, true);
  decode_op_i(s, id_src2, s->isa.instr.csr.csr, true);
  decode_op_r(s, id_dest, s->isa.instr.i.rd, false);
}

#if defined(CONFIG_DEBUG) || defined(CONFIG_SHARE)
#ifdef CONFIG_RVH
def_THelper(system) {
  def_INSTR_IDTAB("000000000000 00000 000 00000 ????? ??", csr, ecall);
#if defined(CONFIG_RV_DEBUG) || defined(CONFIG_EBREAK_AS_TRAP)
  def_INSTR_IDTAB("000000000001 00000 000 00000 ????? ??", csr, ebreak);
#endif
  def_INSTR_IDTAB("000100000010 00000 000 00000 ????? ??", csr, sret);
  def_INSTR_IDTAB("000100000101 00000 000 00000 ????? ??", csr, wfi);
  def_INSTR_IDTAB("0001001????? ????? 000 00000 11100 11", csr, sfence_vma);
#ifdef CONFIG_RV_SVINVAL
  def_INSTR_IDTAB("0001011????? ????? 000 00000 11100 11", csr, sinval_vma);
  def_INSTR_IDTAB("000110000000 00000 000 00000 11100 11", csr, sfence_w_inval);
  def_INSTR_IDTAB("000110000001 00000 000 00000 11100 11", csr, sfence_inval_ir);
  def_INSTR_IDTAB("0010011????? ????? 000 00000 11100 11", csr, hinval_vvma);
  def_INSTR_IDTAB("0110011????? ????? 000 00000 11100 11", csr, hinval_gvma);
#endif
  def_INSTR_IDTAB("001100000010 00000 000 00000 ????? ??", csr, mret);
  def_INSTR_IDTAB("???????????? ????? 001 ????? ????? ??", csr, csrrw);
  def_INSTR_IDTAB("???????????? ????? 010 ????? ????? ??", csr, csrrs);
  def_INSTR_IDTAB("???????????? ????? 011 ????? ????? ??", csr, csrrc);
  def_INSTR_IDTAB("???????????? ????? 101 ????? ????? ??", csr, csrrwi);
  def_INSTR_IDTAB("???????????? ????? 110 ????? ????? ??", csr, csrrsi);
  def_INSTR_IDTAB("???????????? ????? 111 ????? ????? ??", csr, csrrci);
  def_INSTR_IDTAB("0010001????? ????? 000 00000 11100 11", csr, hfence_vvma);
  def_INSTR_IDTAB("0110001????? ????? 000 00000 11100 11", csr, hfence_gvma);
  def_INSTR_IDTAB("011000000000 ????? 100 ????? 11100 11", I  , hlv_b);
  def_INSTR_IDTAB("011000000001 ????? 100 ????? 11100 11", I  , hlv_bu);
  def_INSTR_IDTAB("011001000000 ????? 100 ????? 11100 11", I  , hlv_h);
  def_INSTR_IDTAB("011001000001 ????? 100 ????? 11100 11", I  , hlv_hu);
  def_INSTR_IDTAB("011001000011 ????? 100 ????? 11100 11", I  , hlvx_hu);
  def_INSTR_IDTAB("011010000000 ????? 100 ????? 11100 11", I  , hlv_w);
  def_INSTR_IDTAB("011010000011 ????? 100 ????? 11100 11", I  , hlvx_wu);
  def_INSTR_IDTAB("0110001????? ????? 100 00000 11100 11", R  , hsv_b);
  def_INSTR_IDTAB("0110011????? ????? 100 00000 11100 11", R  , hsv_h);
  def_INSTR_IDTAB("0110101????? ????? 100 00000 11100 11", R  , hsv_w);
  def_INSTR_IDTAB("011010000001 ????? 100 ????? 11100 11", I  , hlv_wu);
  def_INSTR_IDTAB("011011000000 ????? 100 ????? 11100 11", I  , hlv_d);
  def_INSTR_IDTAB("0110111????? ????? 100 00000 11100 11", R  , hsv_w);
  return EXEC_ID_inv;
};
#else
def_THelper(system) {
  def_INSTR_TAB("000000000000 00000 000 00000 ????? ??", ecall);
#if defined(CONFIG_RV_DEBUG) || defined(CONFIG_EBREAK_AS_TRAP)
  def_INSTR_TAB("000000000001 00000 000 00000 ????? ??", ebreak);
#endif //CONFIG_RV_DEBUG
#ifdef CONFIG_RVN
  def_INSTR_TAB("000000000010 00000 000 00000 ????? ??", uret);
#endif  // CONFIG_RVN
  def_INSTR_TAB("000100000010 00000 000 00000 ????? ??", sret);
  def_INSTR_TAB("000100000101 00000 000 00000 ????? ??", wfi);
  def_INSTR_TAB("0001001????? ????? 000 00000 11100 11", sfence_vma);
#ifdef CONFIG_RV_SVINVAL
  def_INSTR_TAB("0001011????? ????? 000 00000 11100 11", sinval_vma);
  def_INSTR_TAB("000110000000 00000 000 00000 11100 11", sfence_w_inval);
  def_INSTR_TAB("000110000001 00000 000 00000 11100 11", sfence_inval_ir);
#endif //CONFIG_RV_SVINVAL
  def_INSTR_TAB("001100000010 00000 000 00000 ????? ??", mret);
  def_INSTR_TAB("???????????? ????? 001 ????? ????? ??", csrrw);
  def_INSTR_TAB("???????????? ????? 010 ????? ????? ??", csrrs);
  def_INSTR_TAB("???????????? ????? 011 ????? ????? ??", csrrc);
  def_INSTR_TAB("???????????? ????? 101 ????? ????? ??", csrrwi);
  def_INSTR_TAB("???????????? ????? 110 ????? ????? ??", csrrsi);
  def_INSTR_TAB("???????????? ????? 111 ????? ????? ??", csrrci);
  return EXEC_ID_inv;
};
#endif //CONFIG_RVH
#endif

#if defined(CONFIG_RVH) && !defined(CONFIG_DEBUG) && !defined(CONFIG_SHARE)
def_THelper(system) {
  def_INSTR_IDTAB("0110??0 ????? ????? 100 ????? 11100 ??", I     , hload);
  def_INSTR_IDTAB("0110??1 ????? ????? 100 00000 11100 ??", R     , hstore);
  def_INSTR_IDTAB("??????? ????? ????? ??? ????? 11100 ??", csr   , priv);
  return EXEC_ID_inv;
}
#endif
