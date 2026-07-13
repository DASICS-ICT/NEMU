  .equ CSR_MSTATEEN0, 0x30c
  .equ CSR_SSTATEEN0, 0x10c
  .equ CSR_LIB_CFG, 0x880
  .equ CSR_LIB_BOUND0_LO, 0x890
  .equ CSR_LIB_BOUND0_HI, 0x891
  .equ CSR_LIB_BOUND1_LO, 0x892
  .equ CSR_LIB_BOUND1_HI, 0x893
  .equ CSR_MAIN_CALL_ENTRY, 0x8b0
  .equ CSR_RETURN_PC, 0x8b1
  .equ CSR_ACTIVE_ZONE_RETURN_PC, 0x8b2
  .equ CSR_FREASON, 0x8b3
  .equ CSR_JUMP_CFG, 0x8c8
  .equ CSR_UMAIN_CFG, 0x9e1
  .equ CSR_UMAIN_BOUND_LO, 0x9e2
  .equ CSR_UMAIN_BOUND_HI, 0x9e3
  .equ CSR_SMAIN_CFG, 0xbc0
  .equ CSR_SMAIN_BOUND_LO, 0xbc2
  .equ CSR_SMAIN_BOUND_HI, 0xbc3

  .equ MSTATUS_MPP_MASK, (3 << 11)
  .equ STATEEN_CUSTOM, 1
  .equ PMP_TOR_RWX, 0x0f
  .equ UCFG_JUMP_ONLY, 0x1e
  .equ UCFG_LOAD_ONLY, 0x2e
  .equ UCFG_STORE_ONLY, 0x36
  .equ UCFG_ECALL_OPEN, 0x3a
  .equ UCFG_ECALL_CLOSED, 0x3e
  .equ SCFG_ECALL_OPEN, 0x381
  .equ SCFG_ECALL_CLOSED, 0x3c1
  .equ LIB_CFG_TWO_READ, 0xaa
  .equ LIB_CFG_TWO_WRITE, 0x99
  .equ LIB_CFG_ONE_READ, 0x0a
  .equ LIB_CFG_ONE_WRITE, 0x09
  .equ CAUSE_LOAD_MISALIGNED, 4
  .equ CAUSE_STORE_MISALIGNED, 6
  .equ CAUSE_ECALL_U, 8
  .equ CAUSE_ECALL_S, 9
  .equ CAUSE_CHECK_U, 0x18
  .equ CAUSE_CHECK_S, 0x19
  .equ FREASON_ECALL, 1
  .equ FREASON_LOAD, 2
  .equ FREASON_STORE, 3
  .equ FREASON_JUMP, 4
  .equ CASE_ILLEGAL_BRANCH, 7
  .equ CASE_ILLEGAL_JUMP, 8
  .equ CASE_SINGLE_LOAD, 9
  .equ CASE_SINGLE_STORE, 10
  .equ CASE_ALIGNED_ILLEGAL_LOAD, 11
  .equ CASE_ALIGNED_ILLEGAL_STORE, 12
  .equ CASE_MISALIGNED_LOAD, 13
  .equ CASE_MISALIGNED_STORE, 14
  .equ CASE_BOUND_WARL, 15
  .equ CASE_U_ECALL_OPEN, 16
  .equ CASE_U_ECALL_CLOSED, 17
  .equ CASE_U_ECALL_TRUSTED, 18
  .equ CASE_U_ECALL_DISABLED, 19
  .equ CASE_S_ECALL_OPEN, 20
  .equ CASE_S_ECALL_CLOSED, 21
  .equ CASE_S_ECALL_TRUSTED, 22
  .equ CASE_S_ECALL_DISABLED, 23
  .equ CASE_DIAG_LOAD_ADJACENT, 24
  .equ CASE_DIAG_LOAD_OVERLAP, 25
  .equ CASE_DIAG_STORE_ADJACENT, 26
  .equ CASE_DIAG_LOAD_TVAL, 27
  .equ CASE_DIAG_FIRST, CASE_DIAG_LOAD_ADJACENT

  .macro CLEAR_CASE_STATE
    csrw CSR_LIB_CFG, zero
    csrw CSR_LIB_BOUND0_LO, zero
    csrw CSR_LIB_BOUND0_HI, zero
    csrw CSR_LIB_BOUND1_LO, zero
    csrw CSR_LIB_BOUND1_HI, zero
    csrw CSR_JUMP_CFG, zero
    csrw CSR_MAIN_CALL_ENTRY, zero
    csrw CSR_RETURN_PC, zero
    csrw CSR_ACTIVE_ZONE_RETURN_PC, zero
    csrw CSR_UMAIN_CFG, zero
    csrw CSR_UMAIN_BOUND_LO, zero
    csrw CSR_UMAIN_BOUND_HI, zero
    csrw CSR_SMAIN_CFG, zero
    csrw CSR_SMAIN_BOUND_LO, zero
    csrw CSR_SMAIN_BOUND_HI, zero
  .endm

  .macro SET_EXPECTED cause, epc_label, reason
    la t0, expected_cause
    li t1, \cause
    sd t1, 0(t0)
    la t0, expected_epc
    la t1, \epc_label
    sd t1, 0(t0)
    la t0, expected_tval
    sd zero, 0(t0)
    la t0, expected_reason
    li t1, \reason
    sd t1, 0(t0)
  .endm

  .macro SET_EXPECTED_TRAP cause, epc_label, addr_offset, reason
    SET_EXPECTED \cause, \epc_label, \reason
    la t0, expected_tval
    la t1, test_data
    addi t1, t1, \addr_offset
    sd t1, 0(t0)
  .endm

  .macro SET_EXPECTED_TARGET epc_label, target_label
    SET_EXPECTED CAUSE_CHECK_U, \epc_label, FREASON_JUMP
    la t0, expected_tval
    la t1, \target_label
    sd t1, 0(t0)
  .endm

  .macro SET_DIAGNOSTIC access_label, ecall_label, addr_offset, ordinary_cause, reason
    la t0, diagnostic_access_epc
    la t1, \access_label
    sd t1, 0(t0)
    la t0, diagnostic_ecall_epc
    la t1, \ecall_label
    sd t1, 0(t0)
    la t0, diagnostic_vaddr
    la t1, test_data
    addi t1, t1, \addr_offset
    sd t1, 0(t0)
    la t0, diagnostic_ordinary_cause
    li t1, \ordinary_cause
    sd t1, 0(t0)
    la t0, diagnostic_fdi_reason
    li t1, \reason
    sd t1, 0(t0)
  .endm

  .macro CHECK_BOUND csr
    li a2, \csr
    li t0, 0x80000127
    csrw \csr, t0
    csrr t1, \csr
    li t2, 0x80000120
    bne t1, t2, bound_warl_fail
  .endm

  .section .text.init, "ax"
  .option push
  .option norvc

  .globl _start
  .align 3
_start:
  mv s0, a0
  la t0, trap_handler
  csrw mtvec, t0
  li t0, -1
  csrw pmpaddr0, t0
  li t0, PMP_TOR_RWX
  csrw pmpcfg0, t0
  li t0, STATEEN_CUSTOM
  csrs CSR_MSTATEEN0, t0
  csrs CSR_SSTATEEN0, t0

  li t0, CASE_BOUND_WARL
  beq s0, t0, case_bound_warl
  li t0, 0
  beq s0, t0, case_branch_main_call
  li t0, 1
  beq s0, t0, case_branch_return_pc
  li t0, 2
  beq s0, t0, case_branch_active_return
  li t0, 3
  beq s0, t0, case_jump_main_call
  li t0, 4
  beq s0, t0, case_jump_return_pc
  li t0, 5
  beq s0, t0, case_jump_active_return
  li t0, 6
  beq s0, t0, case_branch_not_taken
  li t0, CASE_ILLEGAL_BRANCH
  beq s0, t0, case_illegal_branch
  li t0, CASE_ILLEGAL_JUMP
  beq s0, t0, case_illegal_jump
  li t0, CASE_SINGLE_LOAD
  beq s0, t0, case_single_bound_load
  li t0, CASE_SINGLE_STORE
  beq s0, t0, case_single_bound_store
  li t0, CASE_ALIGNED_ILLEGAL_LOAD
  beq s0, t0, case_aligned_illegal_load
  li t0, CASE_ALIGNED_ILLEGAL_STORE
  beq s0, t0, case_aligned_illegal_store
  li t0, CASE_MISALIGNED_LOAD
  beq s0, t0, case_misaligned_contained_load
  li t0, CASE_MISALIGNED_STORE
  beq s0, t0, case_misaligned_contained_store
  li t0, CASE_U_ECALL_OPEN
  beq s0, t0, case_u_ecall_open
  li t0, CASE_U_ECALL_CLOSED
  beq s0, t0, case_u_ecall_closed
  li t0, CASE_U_ECALL_TRUSTED
  beq s0, t0, case_u_ecall_trusted
  li t0, CASE_U_ECALL_DISABLED
  beq s0, t0, case_u_ecall_disabled
  li t0, CASE_S_ECALL_OPEN
  beq s0, t0, case_s_ecall_open
  li t0, CASE_S_ECALL_CLOSED
  beq s0, t0, case_s_ecall_closed
  li t0, CASE_S_ECALL_TRUSTED
  beq s0, t0, case_s_ecall_trusted
  li t0, CASE_S_ECALL_DISABLED
  beq s0, t0, case_s_ecall_disabled
  li t0, CASE_DIAG_LOAD_ADJACENT
  beq s0, t0, case_load_adjacent_bounds
  li t0, CASE_DIAG_LOAD_OVERLAP
  beq s0, t0, case_load_overlapping_bounds
  li t0, CASE_DIAG_STORE_ADJACENT
  beq s0, t0, case_store_adjacent_bounds
  li t0, CASE_DIAG_LOAD_TVAL
  beq s0, t0, case_load_fault_tval
  j test_fail

prepare_jump_case:
  CLEAR_CASE_STATE
  li t0, UCFG_JUMP_ONLY
  csrw CSR_UMAIN_CFG, t0
  csrw CSR_UMAIN_BOUND_LO, zero
  csrw CSR_UMAIN_BOUND_HI, zero
  ret

prepare_load_case:
  CLEAR_CASE_STATE
  li t0, UCFG_LOAD_ONLY
  csrw CSR_UMAIN_CFG, t0
  csrw CSR_UMAIN_BOUND_LO, zero
  csrw CSR_UMAIN_BOUND_HI, zero
  ret

prepare_store_case:
  CLEAR_CASE_STATE
  li t0, UCFG_STORE_ONLY
  csrw CSR_UMAIN_CFG, t0
  csrw CSR_UMAIN_BOUND_LO, zero
  csrw CSR_UMAIN_BOUND_HI, zero
  ret

enter_umode:
  csrw mepc, t0
  csrr t1, mstatus
  li t2, MSTATUS_MPP_MASK
  not t2, t2
  and t1, t1, t2
  csrw mstatus, t1
  mret

enter_smode:
  csrw mepc, t0
  csrr t1, mstatus
  li t2, MSTATUS_MPP_MASK
  not t2, t2
  and t1, t1, t2
  li t2, (1 << 11)
  or t1, t1, t2
  csrw mstatus, t1
  mret

case_branch_main_call:
  call prepare_jump_case
  SET_EXPECTED CAUSE_ECALL_U, branch_main_call_target, 0
  la t0, branch_main_call_target
  csrw CSR_MAIN_CALL_ENTRY, t0
  la t0, branch_main_call_source
  j enter_umode

case_branch_return_pc:
  call prepare_jump_case
  SET_EXPECTED CAUSE_ECALL_U, branch_return_pc_target, 0
  la t0, branch_return_pc_target
  csrw CSR_RETURN_PC, t0
  la t0, branch_return_pc_source
  j enter_umode

case_branch_active_return:
  call prepare_jump_case
  SET_EXPECTED CAUSE_ECALL_U, branch_active_return_target, 0
  la t0, branch_active_return_target
  csrw CSR_ACTIVE_ZONE_RETURN_PC, t0
  la t0, branch_active_return_source
  j enter_umode

case_jump_main_call:
  call prepare_jump_case
  SET_EXPECTED CAUSE_ECALL_U, jump_main_call_target, 0
  la t0, jump_main_call_target
  csrw CSR_MAIN_CALL_ENTRY, t0
  la t0, jump_main_call_source
  j enter_umode

case_jump_return_pc:
  call prepare_jump_case
  SET_EXPECTED CAUSE_ECALL_U, jump_return_pc_target, 0
  la t0, jump_return_pc_target
  csrw CSR_RETURN_PC, t0
  la t0, jump_return_pc_source
  j enter_umode

case_jump_active_return:
  call prepare_jump_case
  SET_EXPECTED CAUSE_ECALL_U, jump_active_return_target, 0
  la t0, jump_active_return_target
  csrw CSR_ACTIVE_ZONE_RETURN_PC, t0
  la t0, jump_active_return_source
  j enter_umode

case_branch_not_taken:
  call prepare_jump_case
  SET_EXPECTED CAUSE_ECALL_U, branch_not_taken_ecall, 0
  la t0, branch_not_taken_source
  j enter_umode

case_illegal_branch:
  call prepare_jump_case
  SET_EXPECTED_TARGET illegal_branch_source, illegal_branch_target
  la t0, illegal_branch_source
  j enter_umode

case_illegal_jump:
  call prepare_jump_case
  SET_EXPECTED_TARGET illegal_jump_source, illegal_jump_target
  la t0, illegal_jump_source
  j enter_umode

case_load_adjacent_bounds:
  call prepare_load_case
  li t0, LIB_CFG_TWO_READ
  csrw CSR_LIB_CFG, t0
  la t0, test_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  csrw CSR_LIB_BOUND1_LO, t1
  addi t1, t0, 16
  csrw CSR_LIB_BOUND1_HI, t1
  SET_DIAGNOSTIC load_adjacent_site, load_adjacent_ecall, 4, CAUSE_LOAD_MISALIGNED, FREASON_LOAD
  la t0, load_adjacent_entry
  j enter_umode

case_load_overlapping_bounds:
  call prepare_load_case
  li t0, LIB_CFG_TWO_READ
  csrw CSR_LIB_CFG, t0
  la t0, test_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 16
  csrw CSR_LIB_BOUND0_HI, t1
  addi t1, t0, 8
  csrw CSR_LIB_BOUND1_LO, t1
  addi t1, t0, 24
  csrw CSR_LIB_BOUND1_HI, t1
  SET_DIAGNOSTIC load_overlap_site, load_overlap_ecall, 12, CAUSE_LOAD_MISALIGNED, FREASON_LOAD
  la t0, load_overlap_entry
  j enter_umode

case_store_adjacent_bounds:
  call prepare_store_case
  li t0, LIB_CFG_TWO_WRITE
  csrw CSR_LIB_CFG, t0
  la t0, test_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  csrw CSR_LIB_BOUND1_LO, t1
  addi t1, t0, 16
  csrw CSR_LIB_BOUND1_HI, t1
  SET_DIAGNOSTIC store_adjacent_site, store_adjacent_ecall, 4, CAUSE_STORE_MISALIGNED, FREASON_STORE
  la t0, store_adjacent_entry
  j enter_umode

case_load_fault_tval:
  call prepare_load_case
  li t0, LIB_CFG_ONE_READ
  csrw CSR_LIB_CFG, t0
  la t0, test_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  csrw CSR_LIB_BOUND1_LO, zero
  csrw CSR_LIB_BOUND1_HI, zero
  SET_DIAGNOSTIC load_tval_site, load_tval_ecall, 4, CAUSE_LOAD_MISALIGNED, FREASON_LOAD
  la t0, load_tval_entry
  j enter_umode

case_single_bound_load:
  call prepare_load_case
  li t0, LIB_CFG_ONE_READ
  csrw CSR_LIB_CFG, t0
  la t0, test_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  SET_EXPECTED CAUSE_ECALL_U, single_load_ecall, 0
  la t0, single_load_entry
  j enter_umode

case_single_bound_store:
  call prepare_store_case
  li t0, LIB_CFG_ONE_WRITE
  csrw CSR_LIB_CFG, t0
  la t0, test_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  SET_EXPECTED CAUSE_ECALL_U, single_store_ecall, 0
  la t0, single_store_entry
  j enter_umode

case_aligned_illegal_load:
  call prepare_load_case
  li t0, LIB_CFG_ONE_READ
  csrw CSR_LIB_CFG, t0
  la t0, test_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  SET_EXPECTED_TRAP CAUSE_CHECK_U, aligned_illegal_load_site, 8, FREASON_LOAD
  la t0, aligned_illegal_load_entry
  j enter_umode

case_aligned_illegal_store:
  call prepare_store_case
  li t0, LIB_CFG_ONE_WRITE
  csrw CSR_LIB_CFG, t0
  la t0, test_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  SET_EXPECTED_TRAP CAUSE_CHECK_U, aligned_illegal_store_site, 8, FREASON_STORE
  la t0, aligned_illegal_store_entry
  j enter_umode

case_misaligned_contained_load:
  call prepare_load_case
  li t0, LIB_CFG_ONE_READ
  csrw CSR_LIB_CFG, t0
  la t0, test_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 16
  csrw CSR_LIB_BOUND0_HI, t1
  SET_EXPECTED_TRAP CAUSE_LOAD_MISALIGNED, contained_load_site, 4, 0
  la t0, contained_load_entry
  j enter_umode

case_misaligned_contained_store:
  call prepare_store_case
  li t0, LIB_CFG_ONE_WRITE
  csrw CSR_LIB_CFG, t0
  la t0, test_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 16
  csrw CSR_LIB_BOUND0_HI, t1
  SET_EXPECTED_TRAP CAUSE_STORE_MISALIGNED, contained_store_site, 4, 0
  la t0, contained_store_entry
  j enter_umode

case_u_ecall_open:
  CLEAR_CASE_STATE
  li t0, UCFG_ECALL_OPEN
  csrw CSR_UMAIN_CFG, t0
  SET_EXPECTED CAUSE_CHECK_U, u_ecall_open_site, FREASON_ECALL
  la t0, u_ecall_open_site
  j enter_umode

case_u_ecall_closed:
  CLEAR_CASE_STATE
  li t0, UCFG_ECALL_CLOSED
  csrw CSR_UMAIN_CFG, t0
  SET_EXPECTED CAUSE_ECALL_U, u_ecall_closed_site, 0
  la t0, u_ecall_closed_site
  j enter_umode

case_u_ecall_trusted:
  CLEAR_CASE_STATE
  li t0, UCFG_ECALL_OPEN
  csrw CSR_UMAIN_CFG, t0
  la t0, u_ecall_trusted_site
  csrw CSR_UMAIN_BOUND_LO, t0
  addi t1, t0, 8
  csrw CSR_UMAIN_BOUND_HI, t1
  SET_EXPECTED CAUSE_ECALL_U, u_ecall_trusted_site, 0
  la t0, u_ecall_trusted_site
  j enter_umode

case_u_ecall_disabled:
  CLEAR_CASE_STATE
  SET_EXPECTED CAUSE_ECALL_U, u_ecall_disabled_site, 0
  la t0, u_ecall_disabled_site
  j enter_umode

case_s_ecall_open:
  CLEAR_CASE_STATE
  li t0, SCFG_ECALL_OPEN
  csrw CSR_SMAIN_CFG, t0
  SET_EXPECTED CAUSE_CHECK_S, s_ecall_open_site, FREASON_ECALL
  la t0, s_ecall_open_site
  j enter_smode

case_s_ecall_closed:
  CLEAR_CASE_STATE
  li t0, SCFG_ECALL_CLOSED
  csrw CSR_SMAIN_CFG, t0
  SET_EXPECTED CAUSE_ECALL_S, s_ecall_closed_site, 0
  la t0, s_ecall_closed_site
  j enter_smode

case_s_ecall_trusted:
  CLEAR_CASE_STATE
  li t0, SCFG_ECALL_OPEN
  csrw CSR_SMAIN_CFG, t0
  la t0, s_ecall_trusted_site
  csrw CSR_SMAIN_BOUND_LO, t0
  addi t1, t0, 8
  csrw CSR_SMAIN_BOUND_HI, t1
  SET_EXPECTED CAUSE_ECALL_S, s_ecall_trusted_site, 0
  la t0, s_ecall_trusted_site
  j enter_smode

case_s_ecall_disabled:
  CLEAR_CASE_STATE
  SET_EXPECTED CAUSE_ECALL_S, s_ecall_disabled_site, 0
  la t0, s_ecall_disabled_site
  j enter_smode

case_bound_warl:
  CHECK_BOUND CSR_UMAIN_BOUND_LO
  CHECK_BOUND CSR_UMAIN_BOUND_HI
  CHECK_BOUND CSR_SMAIN_BOUND_LO
  CHECK_BOUND CSR_SMAIN_BOUND_HI
  CHECK_BOUND 0x890
  CHECK_BOUND 0x891
  CHECK_BOUND 0x892
  CHECK_BOUND 0x893
  CHECK_BOUND 0x894
  CHECK_BOUND 0x895
  CHECK_BOUND 0x896
  CHECK_BOUND 0x897
  CHECK_BOUND 0x898
  CHECK_BOUND 0x899
  CHECK_BOUND 0x89a
  CHECK_BOUND 0x89b
  CHECK_BOUND 0x89c
  CHECK_BOUND 0x89d
  CHECK_BOUND 0x89e
  CHECK_BOUND 0x89f
  CHECK_BOUND 0x8a0
  CHECK_BOUND 0x8a1
  CHECK_BOUND 0x8a2
  CHECK_BOUND 0x8a3
  CHECK_BOUND 0x8a4
  CHECK_BOUND 0x8a5
  CHECK_BOUND 0x8a6
  CHECK_BOUND 0x8a7
  CHECK_BOUND 0x8a8
  CHECK_BOUND 0x8a9
  CHECK_BOUND 0x8aa
  CHECK_BOUND 0x8ab
  CHECK_BOUND 0x8ac
  CHECK_BOUND 0x8ad
  CHECK_BOUND 0x8ae
  CHECK_BOUND 0x8af
  CHECK_BOUND 0x8c0
  CHECK_BOUND 0x8c1
  CHECK_BOUND 0x8c2
  CHECK_BOUND 0x8c3
  CHECK_BOUND 0x8c4
  CHECK_BOUND 0x8c5
  CHECK_BOUND 0x8c6
  CHECK_BOUND 0x8c7
  li a0, 0
  j test_done

bound_warl_fail:
  mv a1, t1
  addi a0, s0, 1
  j test_done

  .balign 8
branch_main_call_source:
  beq zero, zero, branch_main_call_target
  ecall
branch_main_call_target:
  ecall

  .balign 8
branch_return_pc_source:
  beq zero, zero, branch_return_pc_target
  ecall
branch_return_pc_target:
  ecall

  .balign 8
branch_active_return_source:
  beq zero, zero, branch_active_return_target
  ecall
branch_active_return_target:
  ecall

  .balign 8
jump_main_call_source:
  jal zero, jump_main_call_target
  ecall
jump_main_call_target:
  ecall

  .balign 8
jump_return_pc_source:
  jal zero, jump_return_pc_target
  ecall
jump_return_pc_target:
  ecall

  .balign 8
jump_active_return_source:
  jal zero, jump_active_return_target
  ecall
jump_active_return_target:
  ecall

  .balign 8
branch_not_taken_source:
  li t0, 1
  beq t0, zero, branch_not_taken_target
branch_not_taken_ecall:
  ecall
branch_not_taken_target:
  ecall

  .balign 8
illegal_branch_source:
  beq zero, zero, illegal_branch_target
  ecall
illegal_branch_target:
  ecall

  .balign 8
illegal_jump_source:
  jal zero, illegal_jump_target
  ecall
illegal_jump_target:
  ecall

load_adjacent_entry:
  la t0, test_data
load_adjacent_site:
  ld a3, 4(t0)
load_adjacent_ecall:
  ecall

load_overlap_entry:
  la t0, test_data
load_overlap_site:
  ld a3, 12(t0)
load_overlap_ecall:
  ecall

store_adjacent_entry:
  la t0, test_data
  li t1, -1
store_adjacent_site:
  sd t1, 4(t0)
store_adjacent_ecall:
  ecall

load_tval_entry:
  la t0, test_data
load_tval_site:
  ld a3, 4(t0)
load_tval_ecall:
  ecall

single_load_entry:
  la t0, test_data
  ld a2, 0(t0)
single_load_ecall:
  ecall

single_store_entry:
  la t0, test_data
  li t1, 0x5555555555555555
  sd t1, 0(t0)
single_store_ecall:
  ecall

aligned_illegal_load_entry:
  la t0, test_data
aligned_illegal_load_site:
  ld t1, 8(t0)
  ecall

aligned_illegal_store_entry:
  la t0, test_data
  li t1, -1
aligned_illegal_store_site:
  sd t1, 8(t0)
  ecall

contained_load_entry:
  la t0, test_data
contained_load_site:
  ld t1, 4(t0)
  ecall

contained_store_entry:
  la t0, test_data
  li t1, -1
contained_store_site:
  sd t1, 4(t0)
  ecall

  .balign 8
u_ecall_open_site:
  ecall

  .balign 8
u_ecall_closed_site:
  ecall

  .balign 8
u_ecall_trusted_site:
  ecall

  .balign 8
u_ecall_disabled_site:
  ecall

  .balign 8
s_ecall_open_site:
  ecall

  .balign 8
s_ecall_closed_site:
  ecall

  .balign 8
s_ecall_trusted_site:
  ecall

  .balign 8
s_ecall_disabled_site:
  ecall

  .align 2
trap_handler:
  csrr a1, CSR_FREASON
  li t0, CASE_DIAG_FIRST
  bgeu s0, t0, diagnostic_observe
  csrr t0, mcause
  la t1, expected_cause
  ld t1, 0(t1)
  bne t0, t1, test_fail
  csrr t0, mepc
  la t1, expected_epc
  ld t1, 0(t1)
  bne t0, t1, test_fail
  la t1, expected_reason
  ld t1, 0(t1)
  mv t0, a1
  bne t0, t1, test_fail
  csrr t0, mcause
  li t2, CAUSE_ECALL_U
  beq t0, t2, 1f
  csrr t0, mtval
  la t1, expected_tval
  ld t1, 0(t1)
  bne t0, t1, test_fail
1:
  li t0, CASE_SINGLE_LOAD
  beq s0, t0, check_single_load_value
  li t0, CASE_SINGLE_STORE
  beq s0, t0, check_single_store_value
  li t0, CASE_ALIGNED_ILLEGAL_STORE
  beq s0, t0, check_no_store_effect
  li t0, CASE_MISALIGNED_STORE
  beq s0, t0, check_no_store_effect
trap_pass:
  li a0, 0
  j test_done

check_no_store_effect:
  la t0, test_data
  ld t1, 0(t0)
  li t2, 0x1111111111111111
  bne t1, t2, side_effect_fail
  ld t1, 8(t0)
  li t2, 0x2222222222222222
  bne t1, t2, side_effect_fail
  j trap_pass

diagnostic_observe:
  li a2, 0
  csrr t0, mepc
  la t1, diagnostic_access_epc
  ld t1, 0(t1)
  beq t0, t1, diagnostic_access_trap
  la t1, diagnostic_ecall_epc
  ld t1, 0(t1)
  bne t0, t1, test_fail

  csrr t0, mcause
  li t1, CAUSE_ECALL_U
  bne t0, t1, test_fail
  bnez a1, test_fail
  li t0, CASE_DIAG_STORE_ADJACENT
  beq s0, t0, diagnostic_store_completed
  li t0, CASE_DIAG_LOAD_OVERLAP
  beq s0, t0, diagnostic_overlap_load_completed
  li t0, 0x2222222211111111
  bne a3, t0, test_fail
  j diagnostic_done

diagnostic_overlap_load_completed:
  li t0, 0x3333333322222222
  bne a3, t0, test_fail
  j diagnostic_done

diagnostic_access_trap:
  csrr t0, mcause
  la t1, diagnostic_ordinary_cause
  ld t1, 0(t1)
  beq t0, t1, diagnostic_ordinary_trap
  li t1, CAUSE_CHECK_U
  bne t0, t1, test_fail
  la t0, diagnostic_fdi_reason
  ld t0, 0(t0)
  bne a1, t0, test_fail
  j diagnostic_access_trap_effect

diagnostic_ordinary_trap:
  bnez a1, test_fail
  csrr t0, mtval
  la t1, diagnostic_vaddr
  ld t1, 0(t1)
  bne t0, t1, test_fail

diagnostic_access_trap_effect:
  li t0, CASE_DIAG_STORE_ADJACENT
  bne s0, t0, diagnostic_done
diagnostic_store_unchanged:
  la t0, test_data
  ld t1, 0(t0)
  li t2, 0x1111111111111111
  bne t1, t2, test_fail
  ld t1, 8(t0)
  li t2, 0x2222222222222222
  bne t1, t2, test_fail
  j diagnostic_done

diagnostic_store_completed:
  la t0, test_data
  ld t1, 0(t0)
  li t2, 0xffffffff11111111
  bne t1, t2, test_fail
  ld t1, 8(t0)
  li t2, 0x22222222ffffffff
  bne t1, t2, test_fail
  li a2, 1
diagnostic_done:
  li a0, 0
  j test_done

check_single_load_value:
  li t0, 0x1111111111111111
  mv t1, a2
  bne t1, t0, side_effect_fail
  j trap_pass

check_single_store_value:
  la t0, test_data
  ld t1, 0(t0)
  li t2, 0x5555555555555555
  bne t1, t2, side_effect_fail
  j trap_pass

side_effect_fail:
  mv a1, t1
  j test_fail

test_fail:
  addi a0, s0, 1

  .globl test_done
  .align 2
test_done:
  .word 0x0000006b
2:
  j 2b

  .option pop

  .section .data, "aw"
  .balign 8
expected_cause:
  .quad 0
expected_epc:
  .quad 0
expected_tval:
  .quad 0
expected_reason:
  .quad 0
diagnostic_access_epc:
  .quad 0
diagnostic_ecall_epc:
  .quad 0
diagnostic_vaddr:
  .quad 0
diagnostic_ordinary_cause:
  .quad 0
diagnostic_fdi_reason:
  .quad 0

  .balign 32
test_data:
  .quad 0x1111111111111111
  .quad 0x2222222222222222
  .quad 0x3333333333333333
  .quad 0x4444444444444444
