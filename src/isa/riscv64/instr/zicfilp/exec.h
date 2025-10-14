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

// Zicfilp: Landing Pad instruction execution

#ifndef __RISCV64_ZICFILP_EXEC_H__
#define __RISCV64_ZICFILP_EXEC_H__

// LPAD instruction execution
// 
// Behavior:
//   1. If cpu.elp is not set: acts as NOP
//   2. If cpu.elp is set:
//      a. If label == 0: clear ELP (no label check)
//      b. If label != 0: verify x7[19:0] == label, then clear ELP
//         - If mismatch: trigger Software Check Exception (cause=18)
//
// Operands:
//   - id_src1: x7 register value (only valid when label != 0)
//   - id_src2: 20-bit label immediate
def_EHelper(lpad) {
  uint32_t label = id_src2->imm;  // 20-bit label from instruction
  
  // Placeholder for Task 6 implementation
  // For now, just print the instruction
  // Actual logic will be:
  //
  // if (cpu.elp) {
  //   if (label != 0) {
  //     uint32_t x7_label = *id_src1->preg & 0xFFFFF;  // x7[19:0]
  //     if (x7_label != label) {
  //       // Trigger Software Check Exception
  //       // Will be implemented in Task 8
  //     }
  //   }
  //   cpu.elp = false;
  // }
  // // else: LPAD acts as NOP when ELP is not set
  
  // Debug output
  if (label != 0) {
    print_asm("lpad x7, 0x%x", label);
  } else {
    print_asm("lpad");
  }
}

#endif  // __RISCV64_ZICFILP_EXEC_H__