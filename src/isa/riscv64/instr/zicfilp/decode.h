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

// Zicfilp: Landing Pad instruction decoder

#ifndef __RISCV64_ZICFILP_DECODE_H__
#define __RISCV64_ZICFILP_DECODE_H__

// LPAD instruction decoder
// Encoding: auipc x0, label (opcode=0010111, rd=0)
// 
// Label checking behavior:
//   - If label == 0: No label check, only ELP verification
//   - If label != 0: Check x7[19:0] == label
static inline def_DHelper(lpad) {
  // Extract 20-bit label from imm[31:12]
  uint32_t label = (uint32_t)s->isa.instr.u.simm31_12;
  
  // Operand 1: x7 register (conditional source)
  // Only read x7 if label != 0 (runtime label checking needed)
  if (label != 0) {
    // Label check enabled: read x7
    decode_op_r(s, id_src1, 7, true);  // x7 is GPR[7]
  } else {
    // No label check: x7 not needed
    static word_t dummy = 0;
    id_src1->preg = &dummy;
  }
  
  // Operand 2: 20-bit label as immediate
  decode_op_i(s, id_src2, label, false);
  
  // Print assembly
  if (label != 0) {
    print_asm_template2(lpad);
  } else {
    print_asm("lpad");  // LPAD 0 - simplified output
  }
}

#endif  // __RISCV64_ZICFILP_DECODE_H__