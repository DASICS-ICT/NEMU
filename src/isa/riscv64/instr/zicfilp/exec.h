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
  uint32_t label = (uint32_t)id_src2->imm;  // 20-bit landing-pad-label (LPL)

  // LPAD execution logic per Zicfilp specification
  if (cpu.elp) {
    // ELP is LP_EXPECTED: perform landing pad verification

    // Check 1: Instruction must be 4-byte aligned
    if ((s->pc & 0x3) != 0) {
      // Not 4-byte aligned: trigger Software Check Exception
      save_globals(s);
      INTR_TVAL_REG(EX_SCE) = 2;  // Landing pad fault (code=2)
      longjmp_exception(EX_SCE);
      return;
    }

    // Check 2: Label verification (if label != 0)
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

    // All checks passed: clear ELP to NO_LP_EXPECTED
    cpu.elp = false;
  }
  // else: ELP is NO_LP_EXPECTED, LPAD acts as NOP

  // Debug output
  if (label != 0) {
    print_asm("lpad x7, 0x%x", label);
  } else {
    print_asm("lpad");
  }
}

#endif  // __RISCV64_ZICFILP_EXEC_H__