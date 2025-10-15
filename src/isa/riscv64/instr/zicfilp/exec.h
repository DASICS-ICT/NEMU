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
// Specification (RISC-V Zicfilp Extension):
// When ELP is set to LP_EXPECTED:
//   1. Check if instruction is 4-byte aligned
//   2. Check if it's a valid LPAD instruction
//   3. If label != 0: verify x7[31:12] == label
//   4. If any check fails: raise Software Check Exception (cause=18, tval=2)
//   5. If all checks pass: clear ELP to NO_LP_EXPECTED
//
// When ELP is NO_LP_EXPECTED: LPAD acts as NOP
//
// Operands:
//   - id_src1: x7 register value (only valid when label != 0)
//   - id_src2: 20-bit label immediate (landing-pad-label, LPL)
def_EHelper(lpad) {
  uint32_t label = (uint32_t)id_src2->imm & 0xFFFFF;

  // LPAD execution logic per Zicfilp specification
  // Per spec §3.2: LPAD only performs checks when both LPE=1 AND ELP=1
  // When ELP=0, LPAD acts as a NOP regardless of LPE
  if (zicfilp_lp_enabled() && cpu.elp) {
    // Both Zicfilp is enabled (LPE=1) AND ELP is set - perform label check if needed and clear ELP
    if (label != 0) {
      // Label check required: verify x7[31:12] == label
      // Note: Label is stored in upper 20 bits of x7 (bits 31:12)
      uint32_t x7_label = (uint32_t)((*id_src1->preg) >> 12) & 0xFFFFF;

      if (x7_label != label) {
        // Label mismatch: trigger Software Check Exception
        save_globals(s);
        INTR_TVAL_REG(EX_SCE) = 2;  // Landing pad fault (code=2)
        longjmp_exception(EX_SCE);
        return;
      }
      // Label matches: proceed to clear ELP
    }

    // Clear ELP for both label=0 and label!=0 cases
    cpu.elp = false;
  }
  // else: ELP=0 or LPE=0: LPAD acts as NOP

  // Debug output
  if (label != 0) {
    print_asm("lpad x7, 0x%x", label);
  } else {
    print_asm("lpad");
  }
}

#endif  // __RISCV64_ZICFILP_EXEC_H__