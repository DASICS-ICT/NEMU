  .equ CSR_MSTATEEN0, 0x30c
  .equ CSR_SSTATEEN0, 0x10c
  .equ CSR_USTATUS, 0x000
  .equ CSR_UTVEC, 0x005
  .equ CSR_USCRATCH, 0x040
  .equ CSR_UEPC, 0x041
  .equ CSR_UCAUSE, 0x042
  .equ CSR_UTVAL, 0x043
  .equ CSR_SEDELEG, 0x102
  .equ CSR_LIB_CFG, 0x880
  .equ CSR_LIB_BOUND0_LO, 0x890
  .equ CSR_LIB_BOUND0_HI, 0x891
  .equ CSR_LIB_BOUND1_LO, 0x892
  .equ CSR_LIB_BOUND1_HI, 0x893
  .equ CSR_LIB_BOUND15_LO, 0x8ae
  .equ CSR_LIB_BOUND15_HI, 0x8af
  .equ CSR_MAIN_CALL_ENTRY, 0x8b0
  .equ CSR_RETURN_PC, 0x8b1
  .equ CSR_ACTIVE_ZONE_RETURN_PC, 0x8b2
  .equ CSR_FREASON, 0x8b3
  .equ CSR_JUMP_BOUND0_LO, 0x8c0
  .equ CSR_JUMP_BOUND0_HI, 0x8c1
  .equ CSR_JUMP_BOUND1_LO, 0x8c2
  .equ CSR_JUMP_BOUND1_HI, 0x8c3
  .equ CSR_JUMP_BOUND2_LO, 0x8c4
  .equ CSR_JUMP_BOUND2_HI, 0x8c5
  .equ CSR_JUMP_BOUND3_LO, 0x8c6
  .equ CSR_JUMP_BOUND3_HI, 0x8c7
  .equ CSR_JUMP_CFG, 0x8c8
  .equ CSR_UMAIN_CFG, 0x9e1
  .equ CSR_UMAIN_BOUND_LO, 0x9e2
  .equ CSR_UMAIN_BOUND_HI, 0x9e3
  .equ CSR_SMAIN_CFG, 0xbc0
  .equ CSR_SMAIN_BOUND_LO, 0xbc2
  .equ CSR_SMAIN_BOUND_HI, 0xbc3

  .equ MSTATUS_MPP_MASK, (3 << 11)
  .equ MSTATUS_UIE, (1 << 0)
  .equ MSTATUS_UPIE, (1 << 4)
  .equ STATEEN_CUSTOM, 1
  .equ PMP_TOR_RWX, 0x0f
  .equ UCFG_JUMP_ONLY, 0x1e
  .equ UCFG_LOAD_ONLY, 0x2e
  .equ UCFG_STORE_ONLY, 0x36
  .equ UCFG_ECALL_OPEN, 0x3a
  .equ UCFG_ECALL_CLOSED, 0x3e
  .equ SCFG_ECALL_OPEN, 0x381
  .equ SCFG_ECALL_CLOSED, 0x3c1
  .equ SCFG_LOAD_OPEN, 0x2c1
  .equ SCFG_STORE_OPEN, 0x341
  .equ SCFG_JUMP_OPEN, 0x1c1
  .equ SCFG_ALL_CLOSED, 0x3c1
  .equ LIB_CFG_TWO_READ, 0xaa
  .equ LIB_CFG_TWO_WRITE, 0x99
  .equ LIB_CFG_ONE_READ, 0x0a
  .equ LIB_CFG_ONE_WRITE, 0x09
  .equ CAUSE_LOAD_MISALIGNED, 4
  .equ CAUSE_STORE_MISALIGNED, 6
  .equ CAUSE_ILLEGAL_INSTRUCTION, 2
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
  .equ CASE_CALL_J_TRUSTED, 24
  .equ CASE_CALL_JR_TRUSTED, 25
  .equ CASE_CALL_J_DISABLED, 26
  .equ CASE_CALL_JR_DISABLED, 27
  .equ CASE_CALL_J_UNTRUSTED, 28
  .equ CASE_CALL_JR_UNTRUSTED, 29
  .equ CASE_S_LOAD_OPEN, 30
  .equ CASE_S_LOAD_CLOSED, 31
  .equ CASE_S_STORE_OPEN, 32
  .equ CASE_S_STORE_CLOSED, 33
  .equ CASE_S_JUMP_OPEN, 34
  .equ CASE_S_JUMP_CLOSED, 35
  .equ CASE_LB_ALLOW, 36
  .equ CASE_LB_DENY, 37
  .equ CASE_LBU_ALLOW, 38
  .equ CASE_LBU_DENY, 39
  .equ CASE_LH_ALLOW, 40
  .equ CASE_LH_DENY, 41
  .equ CASE_LHU_ALLOW, 42
  .equ CASE_LHU_DENY, 43
  .equ CASE_LW_ALLOW, 44
  .equ CASE_LW_DENY, 45
  .equ CASE_LWU_ALLOW, 46
  .equ CASE_LWU_DENY, 47
  .equ CASE_SB_ALLOW, 48
  .equ CASE_SB_DENY, 49
  .equ CASE_SH_ALLOW, 50
  .equ CASE_SH_DENY, 51
  .equ CASE_SW_ALLOW, 52
  .equ CASE_SW_DENY, 53
  .equ CASE_BRANCH_JUMP_BOUND0, 54
  .equ CASE_JAL_JUMP_BOUND0, 55
  .equ CASE_JALR_JUMP_BOUND3, 56
  .equ CASE_JUMP_BOUND_HI, 57
  .equ CASE_JUMP_BOUND_INVALID_CFG, 58
  .equ CASE_JUMP_BOUND_EMPTY, 59
  .equ CASE_JUMP_BOUND_REVERSED, 60
  .equ CASE_JALR_MAIN_CALL, 61
  .equ CASE_JALR_ILLEGAL, 62
  .equ CASE_U_LOAD_TRUSTED, 63
  .equ CASE_U_LOAD_DISABLED, 64
  .equ CASE_U_LOAD_CLOSED, 65
  .equ CASE_U_STORE_TRUSTED, 66
  .equ CASE_U_STORE_DISABLED, 67
  .equ CASE_U_STORE_CLOSED, 68
  .equ CASE_U_JUMP_TRUSTED, 69
  .equ CASE_U_JUMP_DISABLED, 70
  .equ CASE_U_JUMP_CLOSED, 71
  .equ CASE_LIB_WRITE_ONLY_LOAD, 72
  .equ CASE_LIB_READ_ONLY_STORE, 73
  .equ CASE_LIB_NO_VALID_LOAD, 74
  .equ CASE_LIB_SLOT15_LOAD, 75
  .equ CASE_LIB_EMPTY_LOAD, 76
  .equ CASE_LIB_REVERSED_STORE, 77
  .equ CASE_S_CSR_TRUSTED_READ, 78
  .equ CASE_S_CSR_UNTRUSTED_READ, 79
  .equ CASE_S_CSR_UNTRUSTED_WRITE, 80
  .equ CASE_S_CALL_J_TRUSTED, 81
  .equ CASE_S_CALL_JR_TRUSTED, 82
  .equ CASE_S_CALL_J_DISABLED, 83
  .equ CASE_S_CALL_JR_DISABLED, 84
  .equ CASE_S_CALL_J_UNTRUSTED, 85
  .equ CASE_S_CALL_JR_UNTRUSTED, 86
  .equ CASE_U_MAIN_HI, 87
  .equ CASE_U_MAIN_EMPTY, 88
  .equ CASE_U_MAIN_REVERSED, 89
  .equ CASE_U_MAIN_BELOW_LO, 90
  .equ CASE_S_MAIN_HI, 91
  .equ CASE_S_MAIN_EMPTY, 92
  .equ CASE_S_MAIN_REVERSED, 93
  .equ CASE_S_MAIN_BELOW_LO, 94
  .equ CASE_CALL_JR_NON_RA_TRUSTED, 95
  .equ CASE_CALL_JR_NON_RA_ILLEGAL, 96
  .equ CASE_CALL_J_POSITIVE, 97
  .equ CASE_CALL_J_NEGATIVE, 98
  .equ CASE_BNE_ILLEGAL, 99
  .equ CASE_BLT_ILLEGAL, 100
  .equ CASE_BGE_ILLEGAL, 101
  .equ CASE_BLTU_ILLEGAL, 102
  .equ CASE_BGEU_ILLEGAL, 103
  .equ CASE_JUMP_BOUND1, 104
  .equ CASE_JUMP_BOUND2, 105
  .equ CASE_C_J_ILLEGAL, 106
  .equ CASE_C_JR_ILLEGAL, 107
  .equ CASE_C_JALR_ILLEGAL, 108
  .equ CASE_C_BEQZ_ILLEGAL, 109
  .equ CASE_C_BNEZ_ILLEGAL, 110
  .equ CASE_C_BRANCH_NOT_TAKEN, 111
  .equ CASE_C_J_MAIN_CALL, 112
  .equ CASE_S_LOAD_TRUSTED, 113
  .equ CASE_S_LOAD_DISABLED, 114
  .equ CASE_S_STORE_TRUSTED, 115
  .equ CASE_S_STORE_DISABLED, 116
  .equ CASE_S_JUMP_TRUSTED, 117
  .equ CASE_S_JUMP_DISABLED, 118
  .equ CASE_S_LOAD_BOUND_ALLOW, 119
  .equ CASE_S_STORE_BOUND_ALLOW, 120
  .equ CASE_S_JUMP_BOUND_ALLOW, 121
  .equ CASE_S_JUMP_SPECIAL_ALLOW, 122
  .equ CASE_N_HU_LOAD_TRAP_URET, 123
  .equ CASE_N_HU_STORE_TRAP_URET, 124
  .equ CASE_SCALAR_LOAD_FIRST, CASE_LB_ALLOW
  .equ CASE_SCALAR_STORE_FIRST, CASE_SB_ALLOW
  .equ CASE_SCALAR_LAST, CASE_SW_DENY
  .equ CASE_DIAG_LOAD_ADJACENT, 125
  .equ CASE_DIAG_LOAD_OVERLAP, 126
  .equ CASE_DIAG_STORE_ADJACENT, 127
  .equ CASE_DIAG_LOAD_TVAL, 128
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

  .macro SET_EXPECTED_AUX value0, value1
    la t0, expected_aux0
    li t1, \value0
    sd t1, 0(t0)
    la t0, expected_aux1
    li t1, \value1
    sd t1, 0(t0)
  .endm

  .macro SET_EXPECTED_SCALAR_TRAP epc_label, addr_offset, reason
    SET_EXPECTED CAUSE_CHECK_U, \epc_label, \reason
    la t0, expected_tval
    la t1, scalar_data
    addi t1, t1, \addr_offset
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
  li t0, CASE_CALL_J_TRUSTED
  beq s0, t0, case_call_j_trusted
  li t0, CASE_CALL_JR_TRUSTED
  beq s0, t0, case_call_jr_trusted
  li t0, CASE_CALL_J_DISABLED
  beq s0, t0, case_call_j_disabled
  li t0, CASE_CALL_JR_DISABLED
  beq s0, t0, case_call_jr_disabled
  li t0, CASE_CALL_J_UNTRUSTED
  beq s0, t0, case_call_j_untrusted
  li t0, CASE_CALL_JR_UNTRUSTED
  beq s0, t0, case_call_jr_untrusted
  li t0, CASE_S_LOAD_OPEN
  beq s0, t0, case_s_load_open
  li t0, CASE_S_LOAD_CLOSED
  beq s0, t0, case_s_load_closed
  li t0, CASE_S_STORE_OPEN
  beq s0, t0, case_s_store_open
  li t0, CASE_S_STORE_CLOSED
  beq s0, t0, case_s_store_closed
  li t0, CASE_S_JUMP_OPEN
  beq s0, t0, case_s_jump_open
  li t0, CASE_S_JUMP_CLOSED
  beq s0, t0, case_s_jump_closed
  li t0, CASE_LB_ALLOW
  beq s0, t0, case_lb_allow
  li t0, CASE_LB_DENY
  beq s0, t0, case_lb_deny
  li t0, CASE_LBU_ALLOW
  beq s0, t0, case_lbu_allow
  li t0, CASE_LBU_DENY
  beq s0, t0, case_lbu_deny
  li t0, CASE_LH_ALLOW
  beq s0, t0, case_lh_allow
  li t0, CASE_LH_DENY
  beq s0, t0, case_lh_deny
  li t0, CASE_LHU_ALLOW
  beq s0, t0, case_lhu_allow
  li t0, CASE_LHU_DENY
  beq s0, t0, case_lhu_deny
  li t0, CASE_LW_ALLOW
  beq s0, t0, case_lw_allow
  li t0, CASE_LW_DENY
  beq s0, t0, case_lw_deny
  li t0, CASE_LWU_ALLOW
  beq s0, t0, case_lwu_allow
  li t0, CASE_LWU_DENY
  beq s0, t0, case_lwu_deny
  li t0, CASE_SB_ALLOW
  beq s0, t0, case_sb_allow
  li t0, CASE_SB_DENY
  beq s0, t0, case_sb_deny
  li t0, CASE_SH_ALLOW
  beq s0, t0, case_sh_allow
  li t0, CASE_SH_DENY
  beq s0, t0, case_sh_deny
  li t0, CASE_SW_ALLOW
  beq s0, t0, case_sw_allow
  li t0, CASE_SW_DENY
  beq s0, t0, case_sw_deny
  li t0, CASE_BRANCH_JUMP_BOUND0
  beq s0, t0, case_branch_jump_bound0
  li t0, CASE_JAL_JUMP_BOUND0
  beq s0, t0, case_jal_jump_bound0
  li t0, CASE_JALR_JUMP_BOUND3
  beq s0, t0, case_jalr_jump_bound3
  li t0, CASE_JUMP_BOUND_HI
  beq s0, t0, case_jump_bound_hi
  li t0, CASE_JUMP_BOUND_INVALID_CFG
  beq s0, t0, case_jump_bound_invalid_cfg
  li t0, CASE_JUMP_BOUND_EMPTY
  beq s0, t0, case_jump_bound_empty
  li t0, CASE_JUMP_BOUND_REVERSED
  beq s0, t0, case_jump_bound_reversed
  li t0, CASE_JALR_MAIN_CALL
  beq s0, t0, case_jalr_main_call
  li t0, CASE_JALR_ILLEGAL
  beq s0, t0, case_jalr_illegal
  li t0, CASE_U_LOAD_TRUSTED
  beq s0, t0, case_u_load_trusted
  li t0, CASE_U_LOAD_DISABLED
  beq s0, t0, case_u_load_disabled
  li t0, CASE_U_LOAD_CLOSED
  beq s0, t0, case_u_load_closed
  li t0, CASE_U_STORE_TRUSTED
  beq s0, t0, case_u_store_trusted
  li t0, CASE_U_STORE_DISABLED
  beq s0, t0, case_u_store_disabled
  li t0, CASE_U_STORE_CLOSED
  beq s0, t0, case_u_store_closed
  li t0, CASE_U_JUMP_TRUSTED
  beq s0, t0, case_u_jump_trusted
  li t0, CASE_U_JUMP_DISABLED
  beq s0, t0, case_u_jump_disabled
  li t0, CASE_U_JUMP_CLOSED
  beq s0, t0, case_u_jump_closed
  li t0, CASE_LIB_WRITE_ONLY_LOAD
  beq s0, t0, case_lib_write_only_load
  li t0, CASE_LIB_READ_ONLY_STORE
  beq s0, t0, case_lib_read_only_store
  li t0, CASE_LIB_NO_VALID_LOAD
  beq s0, t0, case_lib_no_valid_load
  li t0, CASE_LIB_SLOT15_LOAD
  beq s0, t0, case_lib_slot15_load
  li t0, CASE_LIB_EMPTY_LOAD
  beq s0, t0, case_lib_empty_load
  li t0, CASE_LIB_REVERSED_STORE
  beq s0, t0, case_lib_reversed_store
  li t0, CASE_S_CSR_TRUSTED_READ
  beq s0, t0, case_s_csr_trusted_read
  li t0, CASE_S_CSR_UNTRUSTED_READ
  beq s0, t0, case_s_csr_untrusted_read
  li t0, CASE_S_CSR_UNTRUSTED_WRITE
  beq s0, t0, case_s_csr_untrusted_write
  li t0, CASE_S_CALL_J_TRUSTED
  beq s0, t0, case_s_call_j_trusted
  li t0, CASE_S_CALL_JR_TRUSTED
  beq s0, t0, case_s_call_jr_trusted
  li t0, CASE_S_CALL_J_DISABLED
  beq s0, t0, case_s_call_j_disabled
  li t0, CASE_S_CALL_JR_DISABLED
  beq s0, t0, case_s_call_jr_disabled
  li t0, CASE_S_CALL_J_UNTRUSTED
  beq s0, t0, case_s_call_j_untrusted
  li t0, CASE_S_CALL_JR_UNTRUSTED
  beq s0, t0, case_s_call_jr_untrusted
  li t0, CASE_U_MAIN_HI
  beq s0, t0, case_u_main_hi
  li t0, CASE_U_MAIN_EMPTY
  beq s0, t0, case_u_main_empty
  li t0, CASE_U_MAIN_REVERSED
  beq s0, t0, case_u_main_reversed
  li t0, CASE_U_MAIN_BELOW_LO
  beq s0, t0, case_u_main_below_lo
  li t0, CASE_S_MAIN_HI
  beq s0, t0, case_s_main_hi
  li t0, CASE_S_MAIN_EMPTY
  beq s0, t0, case_s_main_empty
  li t0, CASE_S_MAIN_REVERSED
  beq s0, t0, case_s_main_reversed
  li t0, CASE_S_MAIN_BELOW_LO
  beq s0, t0, case_s_main_below_lo
  li t0, CASE_CALL_JR_NON_RA_TRUSTED
  beq s0, t0, case_call_jr_non_ra_trusted
  li t0, CASE_CALL_JR_NON_RA_ILLEGAL
  beq s0, t0, case_call_jr_non_ra_illegal
  li t0, CASE_CALL_J_POSITIVE
  beq s0, t0, case_call_j_positive
  li t0, CASE_CALL_J_NEGATIVE
  beq s0, t0, case_call_j_negative
  li t0, CASE_BNE_ILLEGAL
  beq s0, t0, case_bne_illegal
  li t0, CASE_BLT_ILLEGAL
  beq s0, t0, case_blt_illegal
  li t0, CASE_BGE_ILLEGAL
  beq s0, t0, case_bge_illegal
  li t0, CASE_BLTU_ILLEGAL
  beq s0, t0, case_bltu_illegal
  li t0, CASE_BGEU_ILLEGAL
  beq s0, t0, case_bgeu_illegal
  li t0, CASE_JUMP_BOUND1
  beq s0, t0, case_jump_bound1
  li t0, CASE_JUMP_BOUND2
  beq s0, t0, case_jump_bound2
  li t0, CASE_C_J_ILLEGAL
  beq s0, t0, case_c_j_illegal
  li t0, CASE_C_JR_ILLEGAL
  beq s0, t0, case_c_jr_illegal
  li t0, CASE_C_JALR_ILLEGAL
  beq s0, t0, case_c_jalr_illegal
  li t0, CASE_C_BEQZ_ILLEGAL
  beq s0, t0, case_c_beqz_illegal
  li t0, CASE_C_BNEZ_ILLEGAL
  beq s0, t0, case_c_bnez_illegal
  li t0, CASE_C_BRANCH_NOT_TAKEN
  beq s0, t0, case_c_branch_not_taken
  li t0, CASE_C_J_MAIN_CALL
  beq s0, t0, case_c_j_main_call
  li t0, CASE_S_LOAD_TRUSTED
  beq s0, t0, case_s_load_trusted
  li t0, CASE_S_LOAD_DISABLED
  beq s0, t0, case_s_load_disabled
  li t0, CASE_S_STORE_TRUSTED
  beq s0, t0, case_s_store_trusted
  li t0, CASE_S_STORE_DISABLED
  beq s0, t0, case_s_store_disabled
  li t0, CASE_S_JUMP_TRUSTED
  beq s0, t0, case_s_jump_trusted
  li t0, CASE_S_JUMP_DISABLED
  beq s0, t0, case_s_jump_disabled
  li t0, CASE_S_LOAD_BOUND_ALLOW
  beq s0, t0, case_s_load_bound_allow
  li t0, CASE_S_STORE_BOUND_ALLOW
  beq s0, t0, case_s_store_bound_allow
  li t0, CASE_S_JUMP_BOUND_ALLOW
  beq s0, t0, case_s_jump_bound_allow
  li t0, CASE_S_JUMP_SPECIAL_ALLOW
  beq s0, t0, case_s_jump_special_allow
  li t0, CASE_N_HU_LOAD_TRAP_URET
  beq s0, t0, case_n_hu_load_trap_uret
  li t0, CASE_N_HU_STORE_TRAP_URET
  beq s0, t0, case_n_hu_store_trap_uret
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
  SET_EXPECTED_AUX 0x5a5a5a5a5a5a5a5a, 0
  la t0, illegal_jump_entry
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
  SET_EXPECTED_AUX 0x5a5a5a5a5a5a5a5a, 0
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

case_call_j_trusted:
  CLEAR_CASE_STATE
  li t0, UCFG_JUMP_ONLY
  csrw CSR_UMAIN_CFG, t0
  la t0, call_j_trusted_site
  csrw CSR_UMAIN_BOUND_LO, t0
  addi t1, t0, 8
  csrw CSR_UMAIN_BOUND_HI, t1
  SET_EXPECTED CAUSE_ECALL_U, call_j_trusted_target_ecall, 0
  la t0, call_j_trusted_site
  j enter_umode

case_call_jr_trusted:
  CLEAR_CASE_STATE
  li t0, UCFG_JUMP_ONLY
  csrw CSR_UMAIN_CFG, t0
  la t0, call_jr_trusted_site
  csrw CSR_UMAIN_BOUND_LO, t0
  addi t1, t0, 8
  csrw CSR_UMAIN_BOUND_HI, t1
  SET_EXPECTED CAUSE_ECALL_U, call_jr_trusted_target_ecall, 0
  la t0, call_jr_trusted_entry
  j enter_umode

case_call_j_disabled:
  CLEAR_CASE_STATE
  li t0, 5
  csrw CSR_FREASON, t0
  li t0, 0x5555555555555555
  csrw CSR_RETURN_PC, t0
  SET_EXPECTED CAUSE_ILLEGAL_INSTRUCTION, call_j_disabled_site, 5
  la t0, call_j_disabled_entry
  j enter_umode

case_call_jr_disabled:
  CLEAR_CASE_STATE
  li t0, 5
  csrw CSR_FREASON, t0
  li t0, 0x5555555555555555
  csrw CSR_RETURN_PC, t0
  SET_EXPECTED CAUSE_ILLEGAL_INSTRUCTION, call_jr_disabled_site, 5
  la t0, call_jr_disabled_entry
  j enter_umode

case_call_j_untrusted:
  CLEAR_CASE_STATE
  li t0, UCFG_JUMP_ONLY
  csrw CSR_UMAIN_CFG, t0
  li t0, 5
  csrw CSR_FREASON, t0
  li t0, 0x5555555555555555
  csrw CSR_RETURN_PC, t0
  SET_EXPECTED CAUSE_ILLEGAL_INSTRUCTION, call_j_untrusted_site, 5
  la t0, call_j_untrusted_entry
  j enter_umode

case_call_jr_untrusted:
  CLEAR_CASE_STATE
  li t0, UCFG_JUMP_ONLY
  csrw CSR_UMAIN_CFG, t0
  li t0, 5
  csrw CSR_FREASON, t0
  li t0, 0x5555555555555555
  csrw CSR_RETURN_PC, t0
  SET_EXPECTED CAUSE_ILLEGAL_INSTRUCTION, call_jr_untrusted_site, 5
  la t0, call_jr_untrusted_entry
  j enter_umode

case_s_load_open:
  CLEAR_CASE_STATE
  li t0, SCFG_LOAD_OPEN
  csrw CSR_SMAIN_CFG, t0
  SET_EXPECTED_TRAP CAUSE_CHECK_S, s_load_open_site, 0, FREASON_LOAD
  SET_EXPECTED_AUX 0x5a5a5a5a5a5a5a5a, 0
  la t0, s_load_open_entry
  j enter_smode

case_s_load_closed:
  CLEAR_CASE_STATE
  li t0, SCFG_ALL_CLOSED
  csrw CSR_SMAIN_CFG, t0
  SET_EXPECTED CAUSE_ECALL_S, s_load_closed_ecall, 0
  la t0, s_load_closed_entry
  j enter_smode

case_s_store_open:
  CLEAR_CASE_STATE
  li t0, SCFG_STORE_OPEN
  csrw CSR_SMAIN_CFG, t0
  SET_EXPECTED_TRAP CAUSE_CHECK_S, s_store_open_site, 0, FREASON_STORE
  la t0, s_store_open_entry
  j enter_smode

case_s_store_closed:
  CLEAR_CASE_STATE
  li t0, SCFG_ALL_CLOSED
  csrw CSR_SMAIN_CFG, t0
  SET_EXPECTED CAUSE_ECALL_S, s_store_closed_ecall, 0
  la t0, s_store_closed_entry
  j enter_smode

case_s_jump_open:
  CLEAR_CASE_STATE
  li t0, SCFG_JUMP_OPEN
  csrw CSR_SMAIN_CFG, t0
  SET_EXPECTED_TARGET s_jump_open_site, s_jump_open_target
  la t0, expected_cause
  li t1, CAUSE_CHECK_S
  sd t1, 0(t0)
  SET_EXPECTED_AUX 0x5a5a5a5a5a5a5a5a, 0
  la t0, s_jump_open_entry
  j enter_smode

case_s_jump_closed:
  CLEAR_CASE_STATE
  li t0, SCFG_ALL_CLOSED
  csrw CSR_SMAIN_CFG, t0
  SET_EXPECTED CAUSE_ECALL_S, s_jump_closed_ecall, 0
  la t0, s_jump_closed_site
  j enter_smode

  .macro SCALAR_LOAD_ALLOW_CASE case_name, site_name, expected
\case_name:
  call prepare_load_case
  li t0, LIB_CFG_ONE_READ
  csrw CSR_LIB_CFG, t0
  la t0, scalar_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  SET_EXPECTED CAUSE_ECALL_U, \site_name\()_ecall, 0
  SET_EXPECTED_AUX \expected, 0
  la t0, \site_name\()_entry
  j enter_umode
  .endm

  .macro SCALAR_LOAD_DENY_CASE case_name, site_name
\case_name:
  call prepare_load_case
  li t0, LIB_CFG_ONE_READ
  csrw CSR_LIB_CFG, t0
  la t0, scalar_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  SET_EXPECTED_SCALAR_TRAP \site_name\()_site, 8, FREASON_LOAD
  SET_EXPECTED_AUX 0x5a5a5a5a5a5a5a5a, 0
  la t0, \site_name\()_entry
  j enter_umode
  .endm

  .macro SCALAR_STORE_ALLOW_CASE case_name, site_name, expected
\case_name:
  call prepare_store_case
  li t0, LIB_CFG_ONE_WRITE
  csrw CSR_LIB_CFG, t0
  la t0, scalar_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  SET_EXPECTED CAUSE_ECALL_U, \site_name\()_ecall, 0
  SET_EXPECTED_AUX \expected, 0x99aabbccddeeff00
  la t0, \site_name\()_entry
  j enter_umode
  .endm

  .macro SCALAR_STORE_DENY_CASE case_name, site_name
\case_name:
  call prepare_store_case
  li t0, LIB_CFG_ONE_WRITE
  csrw CSR_LIB_CFG, t0
  la t0, scalar_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  SET_EXPECTED_SCALAR_TRAP \site_name\()_site, 8, FREASON_STORE
  SET_EXPECTED_AUX 0x88776655f4e3d2c1, 0x99aabbccddeeff00
  la t0, \site_name\()_entry
  j enter_umode
  .endm

  SCALAR_LOAD_ALLOW_CASE case_lb_allow, scalar_lb_allow, 0xffffffffffffffc1
  SCALAR_LOAD_DENY_CASE case_lb_deny, scalar_lb_deny
  SCALAR_LOAD_ALLOW_CASE case_lbu_allow, scalar_lbu_allow, 0xc1
  SCALAR_LOAD_DENY_CASE case_lbu_deny, scalar_lbu_deny
  SCALAR_LOAD_ALLOW_CASE case_lh_allow, scalar_lh_allow, 0xffffffffffffd2c1
  SCALAR_LOAD_DENY_CASE case_lh_deny, scalar_lh_deny
  SCALAR_LOAD_ALLOW_CASE case_lhu_allow, scalar_lhu_allow, 0xd2c1
  SCALAR_LOAD_DENY_CASE case_lhu_deny, scalar_lhu_deny
  SCALAR_LOAD_ALLOW_CASE case_lw_allow, scalar_lw_allow, 0xfffffffff4e3d2c1
  SCALAR_LOAD_DENY_CASE case_lw_deny, scalar_lw_deny
  SCALAR_LOAD_ALLOW_CASE case_lwu_allow, scalar_lwu_allow, 0xf4e3d2c1
  SCALAR_LOAD_DENY_CASE case_lwu_deny, scalar_lwu_deny
  SCALAR_STORE_ALLOW_CASE case_sb_allow, scalar_sb_allow, 0x88776655f4e3d218
  SCALAR_STORE_DENY_CASE case_sb_deny, scalar_sb_deny
  SCALAR_STORE_ALLOW_CASE case_sh_allow, scalar_sh_allow, 0x88776655f4e30718
  SCALAR_STORE_DENY_CASE case_sh_deny, scalar_sh_deny
  SCALAR_STORE_ALLOW_CASE case_sw_allow, scalar_sw_allow, 0x88776655e5f60718
  SCALAR_STORE_DENY_CASE case_sw_deny, scalar_sw_deny

case_branch_jump_bound0:
  call prepare_jump_case
  li t0, 1
  csrw CSR_JUMP_CFG, t0
  la t0, branch_jump_bound0_target
  csrw CSR_JUMP_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_JUMP_BOUND0_HI, t1
  SET_EXPECTED CAUSE_ECALL_U, branch_jump_bound0_target, 0
  la t0, branch_jump_bound0_source
  j enter_umode

case_jal_jump_bound0:
  call prepare_jump_case
  li t0, 0xf
  csrw CSR_JUMP_CFG, t0
  la t0, jal_jump_bound0_target
  csrw CSR_JUMP_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_JUMP_BOUND0_HI, t1
  SET_EXPECTED CAUSE_ECALL_U, jal_jump_bound0_target, 0
  la t0, jal_jump_bound0_source
  j enter_umode

case_jalr_jump_bound3:
  call prepare_jump_case
  li t0, (1 << 48)
  csrw CSR_JUMP_CFG, t0
  la t0, jalr_jump_bound3_target
  csrw CSR_JUMP_BOUND3_LO, t0
  addi t1, t0, 8
  csrw CSR_JUMP_BOUND3_HI, t1
  SET_EXPECTED CAUSE_ECALL_U, jalr_jump_bound3_target, 0
  la t0, jalr_jump_bound3_entry
  j enter_umode

case_jump_bound_hi:
  call prepare_jump_case
  li t0, 1
  csrw CSR_JUMP_CFG, t0
  la t0, jump_bound_hi_target
  addi t1, t0, -8
  csrw CSR_JUMP_BOUND0_LO, t1
  csrw CSR_JUMP_BOUND0_HI, t0
  SET_EXPECTED_TARGET jump_bound_hi_source, jump_bound_hi_target
  la t0, jump_bound_hi_source
  j enter_umode

case_jump_bound_invalid_cfg:
  call prepare_jump_case
  li t0, 2
  csrw CSR_JUMP_CFG, t0
  la t0, jump_bound_invalid_cfg_target
  csrw CSR_JUMP_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_JUMP_BOUND0_HI, t1
  SET_EXPECTED_TARGET jump_bound_invalid_cfg_source, jump_bound_invalid_cfg_target
  la t0, jump_bound_invalid_cfg_source
  j enter_umode

case_jump_bound_empty:
  call prepare_jump_case
  li t0, 1
  csrw CSR_JUMP_CFG, t0
  la t0, jump_bound_empty_target
  csrw CSR_JUMP_BOUND0_LO, t0
  csrw CSR_JUMP_BOUND0_HI, t0
  SET_EXPECTED_TARGET jump_bound_empty_source, jump_bound_empty_target
  la t0, jump_bound_empty_source
  j enter_umode

case_jump_bound_reversed:
  call prepare_jump_case
  li t0, 1
  csrw CSR_JUMP_CFG, t0
  la t0, jump_bound_reversed_target
  addi t1, t0, 8
  csrw CSR_JUMP_BOUND0_LO, t1
  csrw CSR_JUMP_BOUND0_HI, t0
  SET_EXPECTED_TARGET jump_bound_reversed_source, jump_bound_reversed_target
  la t0, jump_bound_reversed_source
  j enter_umode

case_jalr_main_call:
  call prepare_jump_case
  la t0, jalr_main_call_target
  csrw CSR_MAIN_CALL_ENTRY, t0
  SET_EXPECTED CAUSE_ECALL_U, jalr_main_call_target, 0
  la t0, jalr_main_call_entry
  j enter_umode

case_jalr_illegal:
  call prepare_jump_case
  SET_EXPECTED_TARGET jalr_illegal_source, jalr_illegal_target
  SET_EXPECTED_AUX 0x5a5a5a5a5a5a5a5a, 0
  la t0, jalr_illegal_entry
  j enter_umode

  .macro U_LOAD_BYPASS_CASE case_name, site_name, cfg, trusted
\case_name:
  CLEAR_CASE_STATE
  li t0, \cfg
  csrw CSR_UMAIN_CFG, t0
  .if \trusted
  la t0, \site_name\()_site
  csrw CSR_UMAIN_BOUND_LO, t0
  addi t1, t0, 8
  csrw CSR_UMAIN_BOUND_HI, t1
  .endif
  SET_EXPECTED CAUSE_ECALL_U, \site_name\()_ecall, 0
  SET_EXPECTED_AUX 0x99aabbccddeeff00, 0
  la t0, \site_name\()_entry
  j enter_umode
  .endm

  .macro U_STORE_BYPASS_CASE case_name, site_name, cfg, trusted
\case_name:
  CLEAR_CASE_STATE
  li t0, \cfg
  csrw CSR_UMAIN_CFG, t0
  .if \trusted
  la t0, \site_name\()_site
  csrw CSR_UMAIN_BOUND_LO, t0
  addi t1, t0, 8
  csrw CSR_UMAIN_BOUND_HI, t1
  .endif
  SET_EXPECTED CAUSE_ECALL_U, \site_name\()_ecall, 0
  SET_EXPECTED_AUX 0x123456789abcdef0, 0x99aabbccddeeff00
  la t0, \site_name\()_entry
  j enter_umode
  .endm

  .macro U_JUMP_BYPASS_CASE case_name, site_name, cfg, trusted
\case_name:
  CLEAR_CASE_STATE
  li t0, \cfg
  csrw CSR_UMAIN_CFG, t0
  .if \trusted
  la t0, \site_name\()_site
  csrw CSR_UMAIN_BOUND_LO, t0
  addi t1, t0, 8
  csrw CSR_UMAIN_BOUND_HI, t1
  .endif
  SET_EXPECTED CAUSE_ECALL_U, \site_name\()_ecall, 0
  SET_EXPECTED_AUX 0x6a, 0
  la t0, \site_name\()_site
  j enter_umode
  .endm

  U_LOAD_BYPASS_CASE case_u_load_trusted, u_load_trusted, UCFG_LOAD_ONLY, 1
  U_LOAD_BYPASS_CASE case_u_load_disabled, u_load_disabled, 0, 0
  U_LOAD_BYPASS_CASE case_u_load_closed, u_load_closed, UCFG_ECALL_CLOSED, 0
  U_STORE_BYPASS_CASE case_u_store_trusted, u_store_trusted, UCFG_STORE_ONLY, 1
  U_STORE_BYPASS_CASE case_u_store_disabled, u_store_disabled, 0, 0
  U_STORE_BYPASS_CASE case_u_store_closed, u_store_closed, UCFG_ECALL_CLOSED, 0
  U_JUMP_BYPASS_CASE case_u_jump_trusted, u_jump_trusted, UCFG_JUMP_ONLY, 1
  U_JUMP_BYPASS_CASE case_u_jump_disabled, u_jump_disabled, 0, 0
  U_JUMP_BYPASS_CASE case_u_jump_closed, u_jump_closed, UCFG_ECALL_CLOSED, 0

case_lib_write_only_load:
  call prepare_load_case
  li t0, LIB_CFG_ONE_WRITE
  csrw CSR_LIB_CFG, t0
  la t0, scalar_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  SET_EXPECTED_SCALAR_TRAP lib_write_only_load_site, 0, FREASON_LOAD
  SET_EXPECTED_AUX 0x5a5a5a5a5a5a5a5a, 0
  la t0, lib_write_only_load_entry
  j enter_umode

case_lib_read_only_store:
  call prepare_store_case
  li t0, LIB_CFG_ONE_READ
  csrw CSR_LIB_CFG, t0
  la t0, scalar_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  SET_EXPECTED_SCALAR_TRAP lib_read_only_store_site, 0, FREASON_STORE
  SET_EXPECTED_AUX 0x88776655f4e3d2c1, 0x99aabbccddeeff00
  la t0, lib_read_only_store_entry
  j enter_umode

case_lib_no_valid_load:
  call prepare_load_case
  li t0, 2
  csrw CSR_LIB_CFG, t0
  la t0, scalar_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  SET_EXPECTED_SCALAR_TRAP lib_no_valid_load_site, 0, FREASON_LOAD
  SET_EXPECTED_AUX 0x5a5a5a5a5a5a5a5a, 0
  la t0, lib_no_valid_load_entry
  j enter_umode

case_lib_slot15_load:
  call prepare_load_case
  li t0, 0xa000000000000000
  csrw CSR_LIB_CFG, t0
  la t0, scalar_data
  csrw CSR_LIB_BOUND15_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND15_HI, t1
  SET_EXPECTED CAUSE_ECALL_U, lib_slot15_load_ecall, 0
  SET_EXPECTED_AUX 0x88776655f4e3d2c1, 0
  la t0, lib_slot15_load_entry
  j enter_umode

case_lib_empty_load:
  call prepare_load_case
  li t0, LIB_CFG_ONE_READ
  csrw CSR_LIB_CFG, t0
  la t0, scalar_data
  csrw CSR_LIB_BOUND0_LO, t0
  csrw CSR_LIB_BOUND0_HI, t0
  SET_EXPECTED_SCALAR_TRAP lib_empty_load_site, 0, FREASON_LOAD
  SET_EXPECTED_AUX 0x5a5a5a5a5a5a5a5a, 0
  la t0, lib_empty_load_entry
  j enter_umode

case_lib_reversed_store:
  call prepare_store_case
  li t0, LIB_CFG_ONE_WRITE
  csrw CSR_LIB_CFG, t0
  la t0, scalar_data
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_LO, t1
  csrw CSR_LIB_BOUND0_HI, t0
  SET_EXPECTED_SCALAR_TRAP lib_reversed_store_site, 0, FREASON_STORE
  SET_EXPECTED_AUX 0x88776655f4e3d2c1, 0x99aabbccddeeff00
  la t0, lib_reversed_store_entry
  j enter_umode

case_s_csr_trusted_read:
  CLEAR_CASE_STATE
  li t0, SCFG_ALL_CLOSED
  csrw CSR_SMAIN_CFG, t0
  li t0, 5
  csrw CSR_FREASON, t0
  la t0, s_csr_trusted_read_site
  csrw CSR_SMAIN_BOUND_LO, t0
  addi t1, t0, 8
  csrw CSR_SMAIN_BOUND_HI, t1
  SET_EXPECTED CAUSE_ECALL_S, s_csr_trusted_read_ecall, 5
  SET_EXPECTED_AUX 5, 0
  la t0, s_csr_trusted_read_site
  j enter_smode

case_s_csr_untrusted_read:
  CLEAR_CASE_STATE
  li t0, SCFG_ALL_CLOSED
  csrw CSR_SMAIN_CFG, t0
  li t0, 5
  csrw CSR_FREASON, t0
  SET_EXPECTED CAUSE_ILLEGAL_INSTRUCTION, s_csr_untrusted_read_site, 5
  SET_EXPECTED_AUX 0x5a5a5a5a5a5a5a5a, 0
  la t0, s_csr_untrusted_read_entry
  j enter_smode

case_s_csr_untrusted_write:
  CLEAR_CASE_STATE
  li t0, SCFG_ALL_CLOSED
  csrw CSR_SMAIN_CFG, t0
  li t0, 5
  csrw CSR_FREASON, t0
  li t0, 0xa
  csrw CSR_LIB_CFG, t0
  SET_EXPECTED CAUSE_ILLEGAL_INSTRUCTION, s_csr_untrusted_write_site, 5
  SET_EXPECTED_AUX 0xa, 0
  la t0, s_csr_untrusted_write_entry
  j enter_smode

  .macro S_CALL_TRUSTED_CASE case_name, site_name, entry_name, marker
\case_name:
  CLEAR_CASE_STATE
  li t0, SCFG_JUMP_OPEN
  csrw CSR_SMAIN_CFG, t0
  la t0, \site_name\()_site
  csrw CSR_SMAIN_BOUND_LO, t0
  addi t1, t0, 8
  csrw CSR_SMAIN_BOUND_HI, t1
  SET_EXPECTED CAUSE_ECALL_S, \site_name\()_target_ecall, 0
  SET_EXPECTED_AUX \marker, 0
  la t0, \entry_name
  j enter_smode
  .endm

  .macro S_CALL_ILLEGAL_CASE case_name, entry_name, site_name, cfg
\case_name:
  CLEAR_CASE_STATE
  li t0, \cfg
  csrw CSR_SMAIN_CFG, t0
  li t0, 5
  csrw CSR_FREASON, t0
  li t0, 0x5555555555555555
  csrw CSR_RETURN_PC, t0
  SET_EXPECTED CAUSE_ILLEGAL_INSTRUCTION, \site_name, 5
  la t0, \entry_name
  j enter_smode
  .endm

  S_CALL_TRUSTED_CASE case_s_call_j_trusted, s_call_j_trusted, s_call_j_trusted_site, 0x7a
  S_CALL_TRUSTED_CASE case_s_call_jr_trusted, s_call_jr_trusted, s_call_jr_trusted_entry, 0x7b
  S_CALL_ILLEGAL_CASE case_s_call_j_disabled, s_call_j_disabled_entry, s_call_j_disabled_site, 0
  S_CALL_ILLEGAL_CASE case_s_call_jr_disabled, s_call_jr_disabled_entry, s_call_jr_disabled_site, 0
  S_CALL_ILLEGAL_CASE case_s_call_j_untrusted, s_call_j_untrusted_entry, s_call_j_untrusted_site, SCFG_JUMP_OPEN
  S_CALL_ILLEGAL_CASE case_s_call_jr_untrusted, s_call_jr_untrusted_entry, s_call_jr_untrusted_site, SCFG_JUMP_OPEN

  .macro MAIN_BOUNDARY_CASE case_name, site_name, cfg, cause, lo_delta, hi_delta, csr_lo, csr_hi, enter_mode
\case_name:
  CLEAR_CASE_STATE
  li t0, \cfg
  csrw CSR_SMAIN_CFG, t0
  la t0, \site_name
  addi t1, t0, \lo_delta
  csrw \csr_lo, t1
  addi t1, t0, \hi_delta
  csrw \csr_hi, t1
  SET_EXPECTED \cause, \site_name, FREASON_ECALL
  la t0, \site_name
  j \enter_mode
  .endm

  MAIN_BOUNDARY_CASE case_u_main_hi, u_main_hi_site, UCFG_ECALL_OPEN, CAUSE_CHECK_U, -8, 0, CSR_UMAIN_BOUND_LO, CSR_UMAIN_BOUND_HI, enter_umode
  MAIN_BOUNDARY_CASE case_u_main_empty, u_main_empty_site, UCFG_ECALL_OPEN, CAUSE_CHECK_U, 0, 0, CSR_UMAIN_BOUND_LO, CSR_UMAIN_BOUND_HI, enter_umode
  MAIN_BOUNDARY_CASE case_u_main_reversed, u_main_reversed_site, UCFG_ECALL_OPEN, CAUSE_CHECK_U, 8, 0, CSR_UMAIN_BOUND_LO, CSR_UMAIN_BOUND_HI, enter_umode
  MAIN_BOUNDARY_CASE case_u_main_below_lo, u_main_below_lo_site, UCFG_ECALL_OPEN, CAUSE_CHECK_U, 8, 16, CSR_UMAIN_BOUND_LO, CSR_UMAIN_BOUND_HI, enter_umode
  MAIN_BOUNDARY_CASE case_s_main_hi, s_main_hi_site, SCFG_ECALL_OPEN, CAUSE_CHECK_S, -8, 0, CSR_SMAIN_BOUND_LO, CSR_SMAIN_BOUND_HI, enter_smode
  MAIN_BOUNDARY_CASE case_s_main_empty, s_main_empty_site, SCFG_ECALL_OPEN, CAUSE_CHECK_S, 0, 0, CSR_SMAIN_BOUND_LO, CSR_SMAIN_BOUND_HI, enter_smode
  MAIN_BOUNDARY_CASE case_s_main_reversed, s_main_reversed_site, SCFG_ECALL_OPEN, CAUSE_CHECK_S, 8, 0, CSR_SMAIN_BOUND_LO, CSR_SMAIN_BOUND_HI, enter_smode
  MAIN_BOUNDARY_CASE case_s_main_below_lo, s_main_below_lo_site, SCFG_ECALL_OPEN, CAUSE_CHECK_S, 8, 16, CSR_SMAIN_BOUND_LO, CSR_SMAIN_BOUND_HI, enter_smode

case_call_jr_non_ra_trusted:
  CLEAR_CASE_STATE
  li t0, UCFG_JUMP_ONLY
  csrw CSR_UMAIN_CFG, t0
  la t0, call_jr_non_ra_trusted_site
  csrw CSR_UMAIN_BOUND_LO, t0
  addi t1, t0, 8
  csrw CSR_UMAIN_BOUND_HI, t1
  SET_EXPECTED CAUSE_ECALL_U, call_jr_non_ra_trusted_target_ecall, 0
  la t0, call_jr_non_ra_trusted_entry
  j enter_umode

case_call_jr_non_ra_illegal:
  CLEAR_CASE_STATE
  li t0, UCFG_JUMP_ONLY
  csrw CSR_UMAIN_CFG, t0
  li t0, 5
  csrw CSR_FREASON, t0
  li t0, 0x5555555555555555
  csrw CSR_RETURN_PC, t0
  SET_EXPECTED CAUSE_ILLEGAL_INSTRUCTION, call_jr_non_ra_illegal_site, 5
  la t0, call_jr_non_ra_illegal_entry
  j enter_umode

  .macro CALL_J_OFFSET_CASE case_name, site_name, target_ecall
\case_name:
  CLEAR_CASE_STATE
  li t0, UCFG_JUMP_ONLY
  csrw CSR_UMAIN_CFG, t0
  la t0, \site_name
  csrw CSR_UMAIN_BOUND_LO, t0
  addi t1, t0, 8
  csrw CSR_UMAIN_BOUND_HI, t1
  SET_EXPECTED CAUSE_ECALL_U, \target_ecall, 0
  la t0, \site_name
  j enter_umode
  .endm

  CALL_J_OFFSET_CASE case_call_j_positive, call_j_positive_site, call_j_positive_target_ecall
  CALL_J_OFFSET_CASE case_call_j_negative, call_j_negative_site, call_j_negative_target_ecall

  .macro ILLEGAL_BRANCH_CASE case_name, entry_name, site_name, target_name
\case_name:
  call prepare_jump_case
  SET_EXPECTED_TARGET \site_name, \target_name
  la t0, \entry_name
  j enter_umode
  .endm

  ILLEGAL_BRANCH_CASE case_bne_illegal, bne_illegal_entry, bne_illegal_site, bne_illegal_target
  ILLEGAL_BRANCH_CASE case_blt_illegal, blt_illegal_entry, blt_illegal_site, blt_illegal_target
  ILLEGAL_BRANCH_CASE case_bge_illegal, bge_illegal_entry, bge_illegal_site, bge_illegal_target
  ILLEGAL_BRANCH_CASE case_bltu_illegal, bltu_illegal_entry, bltu_illegal_site, bltu_illegal_target
  ILLEGAL_BRANCH_CASE case_bgeu_illegal, bgeu_illegal_entry, bgeu_illegal_site, bgeu_illegal_target

  .macro JUMP_BOUND_CASE case_name, source_name, target_name, cfg, csr_lo, csr_hi
\case_name:
  call prepare_jump_case
  li t0, \cfg
  csrw CSR_JUMP_CFG, t0
  la t0, \target_name
  csrw \csr_lo, t0
  addi t1, t0, 8
  csrw \csr_hi, t1
  SET_EXPECTED CAUSE_ECALL_U, \target_name, 0
  la t0, \source_name
  j enter_umode
  .endm

  JUMP_BOUND_CASE case_jump_bound1, jump_bound1_source, jump_bound1_target, (1 << 16), CSR_JUMP_BOUND1_LO, CSR_JUMP_BOUND1_HI
  JUMP_BOUND_CASE case_jump_bound2, jump_bound2_source, jump_bound2_target, (1 << 32), CSR_JUMP_BOUND2_LO, CSR_JUMP_BOUND2_HI

  .macro COMPRESSED_ILLEGAL_CASE case_name, entry_name, site_name, target_name
\case_name:
  call prepare_jump_case
  SET_EXPECTED_TARGET \site_name, \target_name
  la t0, \entry_name
  j enter_umode
  .endm

  COMPRESSED_ILLEGAL_CASE case_c_j_illegal, c_j_illegal_site, c_j_illegal_site, c_j_illegal_target
  COMPRESSED_ILLEGAL_CASE case_c_jr_illegal, c_jr_illegal_entry, c_jr_illegal_site, c_jr_illegal_target
  COMPRESSED_ILLEGAL_CASE case_c_jalr_illegal, c_jalr_illegal_entry, c_jalr_illegal_site, c_jalr_illegal_target
  COMPRESSED_ILLEGAL_CASE case_c_beqz_illegal, c_beqz_illegal_entry, c_beqz_illegal_site, c_beqz_illegal_target
  COMPRESSED_ILLEGAL_CASE case_c_bnez_illegal, c_bnez_illegal_entry, c_bnez_illegal_site, c_bnez_illegal_target

case_c_branch_not_taken:
  call prepare_jump_case
  SET_EXPECTED CAUSE_ECALL_U, c_branch_not_taken_ecall, 0
  la t0, c_branch_not_taken_entry
  j enter_umode

case_c_j_main_call:
  call prepare_jump_case
  la t0, c_j_main_call_target
  csrw CSR_MAIN_CALL_ENTRY, t0
  SET_EXPECTED CAUSE_ECALL_U, c_j_main_call_target, 0
  la t0, c_j_main_call_site
  j enter_umode

  .macro S_BYPASS_CASE case_name, site_name, cfg, trusted, expected
\case_name:
  CLEAR_CASE_STATE
  li t0, \cfg
  csrw CSR_SMAIN_CFG, t0
  .if \trusted
  la t0, \site_name\()_site
  csrw CSR_SMAIN_BOUND_LO, t0
  addi t1, t0, 8
  csrw CSR_SMAIN_BOUND_HI, t1
  .endif
  SET_EXPECTED CAUSE_ECALL_S, \site_name\()_ecall, 0
  SET_EXPECTED_AUX \expected, 0x99aabbccddeeff00
  la t0, \site_name\()_entry
  j enter_smode
  .endm

  S_BYPASS_CASE case_s_load_trusted, s_load_trusted, SCFG_LOAD_OPEN, 1, 0x99aabbccddeeff00
  S_BYPASS_CASE case_s_load_disabled, s_load_disabled, 0, 0, 0x99aabbccddeeff00
  S_BYPASS_CASE case_s_store_trusted, s_store_trusted, SCFG_STORE_OPEN, 1, 0x123456789abcdef0
  S_BYPASS_CASE case_s_store_disabled, s_store_disabled, 0, 0, 0x123456789abcdef0
  S_BYPASS_CASE case_s_jump_trusted, s_jump_trusted, SCFG_JUMP_OPEN, 1, 0x8a
  S_BYPASS_CASE case_s_jump_disabled, s_jump_disabled, 0, 0, 0x8a

case_s_load_bound_allow:
  CLEAR_CASE_STATE
  li t0, SCFG_LOAD_OPEN
  csrw CSR_SMAIN_CFG, t0
  li t0, LIB_CFG_ONE_READ
  csrw CSR_LIB_CFG, t0
  la t0, scalar_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  SET_EXPECTED CAUSE_ECALL_S, s_load_bound_allow_ecall, 0
  SET_EXPECTED_AUX 0x88776655f4e3d2c1, 0
  la t0, s_load_bound_allow_entry
  j enter_smode

case_s_store_bound_allow:
  CLEAR_CASE_STATE
  li t0, SCFG_STORE_OPEN
  csrw CSR_SMAIN_CFG, t0
  li t0, LIB_CFG_ONE_WRITE
  csrw CSR_LIB_CFG, t0
  la t0, scalar_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  SET_EXPECTED CAUSE_ECALL_S, s_store_bound_allow_ecall, 0
  SET_EXPECTED_AUX 0x123456789abcdef0, 0x99aabbccddeeff00
  la t0, s_store_bound_allow_entry
  j enter_smode

case_s_jump_bound_allow:
  CLEAR_CASE_STATE
  li t0, SCFG_JUMP_OPEN
  csrw CSR_SMAIN_CFG, t0
  li t0, 1
  csrw CSR_JUMP_CFG, t0
  la t0, s_jump_bound_allow_target
  csrw CSR_JUMP_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_JUMP_BOUND0_HI, t1
  SET_EXPECTED CAUSE_ECALL_S, s_jump_bound_allow_ecall, 0
  SET_EXPECTED_AUX 0x8b, 0
  la t0, s_jump_bound_allow_site
  j enter_smode

case_s_jump_special_allow:
  CLEAR_CASE_STATE
  li t0, SCFG_JUMP_OPEN
  csrw CSR_SMAIN_CFG, t0
  la t0, s_jump_special_allow_target
  csrw CSR_MAIN_CALL_ENTRY, t0
  SET_EXPECTED CAUSE_ECALL_S, s_jump_special_allow_ecall, 0
  SET_EXPECTED_AUX 0x8c, 0
  la t0, s_jump_special_allow_site
  j enter_smode

prepare_n_hu_case:
  csrr t0, misa
  srli t0, t0, 13
  andi t0, t0, 1
  beqz t0, test_fail
  li t0, (1 << CAUSE_CHECK_U)
  csrs medeleg, t0
  csrr t1, medeleg
  and t1, t1, t0
  beqz t1, test_fail
  csrw CSR_SEDELEG, t0
  csrr t1, CSR_SEDELEG
  and t1, t1, t0
  beqz t1, test_fail
  la t0, n_hu_trap_handler
  csrw CSR_UTVEC, t0
  csrw CSR_UMAIN_BOUND_LO, t0
  la t0, n_hu_handler_fail
  csrw CSR_UMAIN_BOUND_HI, t0
  li t0, 0x4e2d68752d747261
  csrw CSR_USCRATCH, t0
  li t0, MSTATUS_UIE
  csrw CSR_USTATUS, t0
  li a1, 0
  ret

case_n_hu_load_trap_uret:
  call prepare_load_case
  li t0, LIB_CFG_ONE_READ
  csrw CSR_LIB_CFG, t0
  la t0, test_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  call prepare_n_hu_case
  li a2, 0x5a5a5a5a5a5a5a5a
  la t0, n_hu_load_entry
  j enter_umode

case_n_hu_store_trap_uret:
  call prepare_store_case
  li t0, LIB_CFG_ONE_WRITE
  csrw CSR_LIB_CFG, t0
  la t0, test_data
  csrw CSR_LIB_BOUND0_LO, t0
  addi t1, t0, 8
  csrw CSR_LIB_BOUND0_HI, t1
  call prepare_n_hu_case
  la t0, n_hu_store_entry
  j enter_umode

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
illegal_jump_entry:
  li a2, 0x5a5a5a5a5a5a5a5a
illegal_jump_source:
  jal a2, illegal_jump_target
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
  li a2, 0x5a5a5a5a5a5a5a5a
aligned_illegal_load_site:
  ld a2, 8(t0)
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

  .balign 8
call_j_trusted_site:
  .word 0x0080000b
call_j_trusted_return_site:
  ecall
call_j_trusted_target:
  li a2, 0x4a
call_j_trusted_target_ecall:
  ecall

  .balign 8
call_jr_trusted_entry:
  la a0, call_jr_trusted_target
  addi a0, a0, -3
call_jr_trusted_site:
  .word 0x0045108b
call_jr_trusted_return_site:
  ecall
  .balign 8
call_jr_trusted_target:
  li a2, 0x4b
call_jr_trusted_target_ecall:
  ecall

  .balign 8
call_j_disabled_entry:
  li ra, 0x6666666666666666
  li a2, 0
call_j_disabled_site:
  .word 0x0080000b
  ecall
call_j_disabled_target:
  li a2, 0x4c
  ecall

  .balign 8
call_jr_disabled_entry:
  la a0, call_jr_disabled_target
  addi a0, a0, -3
  li ra, 0x6666666666666666
  li a2, 0
call_jr_disabled_site:
  .word 0x0045108b
  ecall
  .balign 8
call_jr_disabled_target:
  li a2, 0x4d
  ecall

  .balign 8
call_j_untrusted_entry:
  li ra, 0x6666666666666666
  li a2, 0
call_j_untrusted_site:
  .word 0x0080000b
  ecall
call_j_untrusted_target:
  li a2, 0x4e
  ecall

  .balign 8
call_jr_untrusted_entry:
  la a0, call_jr_untrusted_target
  addi a0, a0, -3
  li ra, 0x6666666666666666
  li a2, 0
call_jr_untrusted_site:
  .word 0x0045108b
  ecall
  .balign 8
call_jr_untrusted_target:
  li a2, 0x4f
  ecall

s_load_open_entry:
  la t0, test_data
  li a2, 0x5a5a5a5a5a5a5a5a
s_load_open_site:
  ld a2, 0(t0)
  ecall

s_load_closed_entry:
  la t0, test_data
  ld a2, 0(t0)
s_load_closed_ecall:
  ecall

s_store_open_entry:
  la t0, test_data
  li t1, -1
s_store_open_site:
  sd t1, 0(t0)
  ecall

s_store_closed_entry:
  la t0, test_data
  li t1, 0x7777777777777777
  sd t1, 0(t0)
s_store_closed_ecall:
  ecall

  .balign 8
s_jump_open_entry:
  li a2, 0x5a5a5a5a5a5a5a5a
s_jump_open_site:
  jal zero, s_jump_open_target
  ecall
s_jump_open_target:
  li a2, 0x5a
  ecall

  .balign 8
s_jump_closed_site:
  jal zero, s_jump_closed_target
  ecall
s_jump_closed_target:
  li a2, 0x5b
s_jump_closed_ecall:
  ecall

  .macro SCALAR_LOAD_SITE name, op, offset
\name\()_entry:
  la t0, scalar_data
  addi t0, t0, \offset
  li a2, 0x5a5a5a5a5a5a5a5a
\name\()_site:
  \op a2, 0(t0)
\name\()_ecall:
  ecall
  .endm

  .macro SCALAR_STORE_SITE name, op, offset
\name\()_entry:
  la t0, scalar_data
  addi t0, t0, \offset
  li t1, 0xa1b2c3d4e5f60718
\name\()_site:
  \op t1, 0(t0)
\name\()_ecall:
  ecall
  .endm

  SCALAR_LOAD_SITE scalar_lb_allow, lb, 0
  SCALAR_LOAD_SITE scalar_lb_deny, lb, 8
  SCALAR_LOAD_SITE scalar_lbu_allow, lbu, 0
  SCALAR_LOAD_SITE scalar_lbu_deny, lbu, 8
  SCALAR_LOAD_SITE scalar_lh_allow, lh, 0
  SCALAR_LOAD_SITE scalar_lh_deny, lh, 8
  SCALAR_LOAD_SITE scalar_lhu_allow, lhu, 0
  SCALAR_LOAD_SITE scalar_lhu_deny, lhu, 8
  SCALAR_LOAD_SITE scalar_lw_allow, lw, 0
  SCALAR_LOAD_SITE scalar_lw_deny, lw, 8
  SCALAR_LOAD_SITE scalar_lwu_allow, lwu, 0
  SCALAR_LOAD_SITE scalar_lwu_deny, lwu, 8
  SCALAR_STORE_SITE scalar_sb_allow, sb, 0
  SCALAR_STORE_SITE scalar_sb_deny, sb, 8
  SCALAR_STORE_SITE scalar_sh_allow, sh, 0
  SCALAR_STORE_SITE scalar_sh_deny, sh, 8
  SCALAR_STORE_SITE scalar_sw_allow, sw, 0
  SCALAR_STORE_SITE scalar_sw_deny, sw, 8

  .balign 8
branch_jump_bound0_source:
  beq zero, zero, branch_jump_bound0_target
  ecall
  .balign 8
branch_jump_bound0_target:
  ecall

  .balign 8
jal_jump_bound0_source:
  jal zero, jal_jump_bound0_target
  ecall
  .balign 8
jal_jump_bound0_target:
  ecall

  .balign 8
jalr_jump_bound3_entry:
  la t0, jalr_jump_bound3_target
jalr_jump_bound3_source:
  jalr zero, 0(t0)
  ecall
  .balign 8
jalr_jump_bound3_target:
  ecall

  .balign 8
jump_bound_hi_source:
  jal zero, jump_bound_hi_target
  ecall
  .balign 8
jump_bound_hi_target:
  ecall

  .balign 8
jump_bound_invalid_cfg_source:
  jal zero, jump_bound_invalid_cfg_target
  ecall
  .balign 8
jump_bound_invalid_cfg_target:
  ecall

  .balign 8
jump_bound_empty_source:
  jal zero, jump_bound_empty_target
  ecall
  .balign 8
jump_bound_empty_target:
  ecall

  .balign 8
jump_bound_reversed_source:
  jal zero, jump_bound_reversed_target
  ecall
  .balign 8
jump_bound_reversed_target:
  ecall

  .balign 8
jalr_main_call_entry:
  la t0, jalr_main_call_target
jalr_main_call_source:
  jalr zero, 0(t0)
  ecall
  .balign 8
jalr_main_call_target:
  ecall

  .balign 8
jalr_illegal_entry:
  la t0, jalr_illegal_target
  li a2, 0x5a5a5a5a5a5a5a5a
jalr_illegal_source:
  jalr a2, 0(t0)
  ecall
  .balign 8
jalr_illegal_target:
  ecall

  .macro U_LOAD_BYPASS_SITE name
\name\()_entry:
  la t0, scalar_data
  addi t0, t0, 8
  li a2, 0x5a5a5a5a5a5a5a5a
  .balign 8
\name\()_site:
  ld a2, 0(t0)
\name\()_ecall:
  ecall
  .endm

  .macro U_STORE_BYPASS_SITE name
\name\()_entry:
  la t0, scalar_data
  li t1, 0x123456789abcdef0
  .balign 8
\name\()_site:
  sd t1, 0(t0)
\name\()_ecall:
  ecall
  .endm

  .macro U_JUMP_BYPASS_SITE name
  .balign 8
\name\()_site:
  jal zero, \name\()_target
  ecall
\name\()_target:
  li a2, 0x6a
\name\()_ecall:
  ecall
  .endm

  U_LOAD_BYPASS_SITE u_load_trusted
  U_LOAD_BYPASS_SITE u_load_disabled
  U_LOAD_BYPASS_SITE u_load_closed
  U_STORE_BYPASS_SITE u_store_trusted
  U_STORE_BYPASS_SITE u_store_disabled
  U_STORE_BYPASS_SITE u_store_closed
  U_JUMP_BYPASS_SITE u_jump_trusted
  U_JUMP_BYPASS_SITE u_jump_disabled
  U_JUMP_BYPASS_SITE u_jump_closed

  .macro LIB_LOAD_SITE name
\name\()_entry:
  la t0, scalar_data
  li a2, 0x5a5a5a5a5a5a5a5a
\name\()_site:
  ld a2, 0(t0)
\name\()_ecall:
  ecall
  .endm

  .macro LIB_STORE_SITE name
\name\()_entry:
  la t0, scalar_data
  li t1, 0x123456789abcdef0
\name\()_site:
  sd t1, 0(t0)
\name\()_ecall:
  ecall
  .endm

  LIB_LOAD_SITE lib_write_only_load
  LIB_STORE_SITE lib_read_only_store
  LIB_LOAD_SITE lib_no_valid_load
  LIB_LOAD_SITE lib_slot15_load
  LIB_LOAD_SITE lib_empty_load
  LIB_STORE_SITE lib_reversed_store

  .balign 8
s_csr_trusted_read_site:
  csrr a2, CSR_FREASON
s_csr_trusted_read_ecall:
  ecall

  .balign 8
s_csr_untrusted_read_entry:
  li a2, 0x5a5a5a5a5a5a5a5a
s_csr_untrusted_read_site:
  csrr a2, CSR_FREASON
  ecall

  .balign 8
s_csr_untrusted_write_entry:
  li a2, -1
s_csr_untrusted_write_site:
  csrw CSR_LIB_CFG, a2
  ecall

  .macro S_CALL_J_SITE name, marker
  .balign 8
\name\()_site:
  .word 0x0080000b
\name\()_return_site:
  ecall
\name\()_target:
  li a2, \marker
\name\()_target_ecall:
  ecall
  .endm

  .macro S_CALL_JR_SITE name, marker
  .balign 8
\name\()_entry:
  la a0, \name\()_target
  addi a0, a0, -3
\name\()_site:
  .word 0x0045108b
\name\()_return_site:
  ecall
  .balign 8
\name\()_target:
  li a2, \marker
\name\()_target_ecall:
  ecall
  .endm

  S_CALL_J_SITE s_call_j_trusted, 0x7a
  S_CALL_JR_SITE s_call_jr_trusted, 0x7b

  .macro S_CALL_J_ILLEGAL_SITE name
  .balign 8
\name\()_entry:
  li ra, 0x6666666666666666
  li a2, 0
\name\()_site:
  .word 0x0080000b
  ecall
\name\()_target:
  li a2, 0x7c
  ecall
  .endm

  .macro S_CALL_JR_ILLEGAL_SITE name
  .balign 8
\name\()_entry:
  la a0, \name\()_target
  addi a0, a0, -3
  li ra, 0x6666666666666666
  li a2, 0
\name\()_site:
  .word 0x0045108b
  ecall
  .balign 8
\name\()_target:
  li a2, 0x7d
  ecall
  .endm

  S_CALL_J_ILLEGAL_SITE s_call_j_disabled
  S_CALL_JR_ILLEGAL_SITE s_call_jr_disabled
  S_CALL_J_ILLEGAL_SITE s_call_j_untrusted
  S_CALL_JR_ILLEGAL_SITE s_call_jr_untrusted

  .macro MAIN_BOUNDARY_SITE name
  .balign 8
\name\()_site:
  ecall
  .endm

  MAIN_BOUNDARY_SITE u_main_hi
  MAIN_BOUNDARY_SITE u_main_empty
  MAIN_BOUNDARY_SITE u_main_reversed
  MAIN_BOUNDARY_SITE u_main_below_lo
  MAIN_BOUNDARY_SITE s_main_hi
  MAIN_BOUNDARY_SITE s_main_empty
  MAIN_BOUNDARY_SITE s_main_reversed
  MAIN_BOUNDARY_SITE s_main_below_lo

  .balign 8
call_jr_non_ra_trusted_entry:
  la a0, call_jr_non_ra_trusted_target
  addi a0, a0, -3
  li ra, 0x6666666666666666
  li a2, 0x5a5a5a5a5a5a5a5a
  li a3, 0
call_jr_non_ra_trusted_site:
  .word 0x0045160b
call_jr_non_ra_trusted_return_site:
  ecall
  .balign 8
call_jr_non_ra_trusted_target:
  li a3, 0x7e
call_jr_non_ra_trusted_target_ecall:
  ecall

  .balign 8
call_jr_non_ra_illegal_entry:
  la a0, call_jr_non_ra_illegal_target
  addi a0, a0, -3
  li ra, 0x6666666666666666
  li a2, 0x5a5a5a5a5a5a5a5a
  li a3, 0
call_jr_non_ra_illegal_site:
  .word 0x0045160b
  ecall
  .balign 8
call_jr_non_ra_illegal_target:
  li a3, 0x7f
  ecall

  .balign 8
call_j_positive_site:
  .word 0x4000000b
call_j_positive_return_site:
  .space 1020, 0
call_j_positive_target:
  li a2, 0x80
call_j_positive_target_ecall:
  ecall

  .balign 8
call_j_negative_target:
  li a2, 0x81
call_j_negative_target_ecall:
  ecall
  .space 248, 0
call_j_negative_site:
  .word 0xf01f8f8b
call_j_negative_return_site:
  ecall

  .macro BRANCH_SITE name, setup0, setup1, op
  .balign 8
\name\()_entry:
  li t0, \setup0
  li t1, \setup1
\name\()_site:
  \op t0, t1, \name\()_target
  ecall
\name\()_target:
  ecall
  .endm

  BRANCH_SITE bne_illegal, 1, 0, bne
  BRANCH_SITE blt_illegal, -1, 0, blt
  BRANCH_SITE bge_illegal, 0, -1, bge
  BRANCH_SITE bltu_illegal, 0, 1, bltu
  BRANCH_SITE bgeu_illegal, 1, 0, bgeu

  .balign 8
jump_bound1_source:
  jal zero, jump_bound1_target
  ecall
  .balign 8
jump_bound1_target:
  ecall

  .balign 8
jump_bound2_source:
  jal zero, jump_bound2_target
  ecall
  .balign 8
jump_bound2_target:
  ecall

  .option push
  .option rvc
  .balign 8
c_j_illegal_site:
  c.j c_j_illegal_target
  c.nop
c_j_illegal_target:
  ecall

  .balign 8
c_jr_illegal_entry:
  la t0, c_jr_illegal_target
  addi t0, t0, 1
c_jr_illegal_site:
  c.jr t0
  c.nop
c_jr_illegal_target:
  ecall

  .balign 8
c_jalr_illegal_entry:
  la t0, c_jalr_illegal_target
  addi t0, t0, 1
  li ra, 0x6666666666666666
c_jalr_illegal_site:
  c.jalr t0
  c.nop
c_jalr_illegal_target:
  ecall

  .balign 8
c_beqz_illegal_entry:
  li s1, 0
c_beqz_illegal_site:
  c.beqz s1, c_beqz_illegal_target
  c.nop
c_beqz_illegal_target:
  ecall

  .balign 8
c_bnez_illegal_entry:
  li s1, 1
c_bnez_illegal_site:
  c.bnez s1, c_bnez_illegal_target
  c.nop
c_bnez_illegal_target:
  ecall

  .balign 8
c_branch_not_taken_entry:
  li s1, 1
  c.beqz s1, c_branch_not_taken_target
c_branch_not_taken_ecall:
  ecall
c_branch_not_taken_target:
  ecall

  .balign 8
c_j_main_call_site:
  c.j c_j_main_call_target
  c.nop
c_j_main_call_target:
  ecall
  .option pop

  .macro S_LOAD_BYPASS_SITE name
\name\()_entry:
  la t0, scalar_data
  addi t0, t0, 8
  li a2, 0x5a5a5a5a5a5a5a5a
  .balign 8
\name\()_site:
  ld a2, 0(t0)
\name\()_ecall:
  ecall
  .endm

  .macro S_STORE_BYPASS_SITE name
\name\()_entry:
  la t0, scalar_data
  li t1, 0x123456789abcdef0
  .balign 8
\name\()_site:
  sd t1, 0(t0)
\name\()_ecall:
  ecall
  .endm

  .macro S_JUMP_BYPASS_SITE name
  .balign 8
\name\()_entry:
  li a2, 0
\name\()_site:
  jal zero, \name\()_target
  ecall
\name\()_target:
  li a2, 0x8a
\name\()_ecall:
  ecall
  .endm

  S_LOAD_BYPASS_SITE s_load_trusted
  S_LOAD_BYPASS_SITE s_load_disabled
  S_STORE_BYPASS_SITE s_store_trusted
  S_STORE_BYPASS_SITE s_store_disabled
  S_JUMP_BYPASS_SITE s_jump_trusted
  S_JUMP_BYPASS_SITE s_jump_disabled

s_load_bound_allow_entry:
  la t0, scalar_data
s_load_bound_allow_site:
  ld a2, 0(t0)
s_load_bound_allow_ecall:
  ecall

s_store_bound_allow_entry:
  la t0, scalar_data
  li t1, 0x123456789abcdef0
s_store_bound_allow_site:
  sd t1, 0(t0)
s_store_bound_allow_ecall:
  ecall

  .balign 8
s_jump_bound_allow_site:
  jal zero, s_jump_bound_allow_target
  ecall
  .balign 8
s_jump_bound_allow_target:
  li a2, 0x8b
s_jump_bound_allow_ecall:
  ecall

  .balign 8
s_jump_special_allow_site:
  jal zero, s_jump_special_allow_target
  ecall
  .balign 8
s_jump_special_allow_target:
  li a2, 0x8c
s_jump_special_allow_ecall:
  ecall

  .align 2
n_hu_load_entry:
  la t0, test_data
n_hu_load_fault:
  ld a2, 8(t0)
  j test_fail

n_hu_load_recovery:
  csrr t0, CSR_USTATUS
  li t1, (MSTATUS_UIE | MSTATUS_UPIE)
  bne t0, t1, test_fail
  li t0, 0x4e
  bne a1, t0, test_fail
  li t0, 0x5a5a5a5a5a5a5a5a
  bne a2, t0, test_fail
  li a0, 0
  j test_done

n_hu_store_entry:
  la t0, test_data
  li t1, -1
n_hu_store_fault:
  sd t1, 8(t0)
  j test_fail

n_hu_store_recovery:
  csrr t0, CSR_USTATUS
  li t1, (MSTATUS_UIE | MSTATUS_UPIE)
  bne t0, t1, test_fail
  li t0, 0x4e
  bne a1, t0, test_fail
  la t0, test_data
  ld t1, 8(t0)
  li t2, 0x2222222222222222
  bne t1, t2, test_fail
  li a0, 0
  j test_done

  .align 2
n_hu_trap_handler:
  csrr t0, CSR_UCAUSE
  li t1, CAUSE_CHECK_U
  bne t0, t1, n_hu_handler_fail
  csrr t0, CSR_USTATUS
  li t1, MSTATUS_UPIE
  bne t0, t1, n_hu_handler_fail
  csrr t0, CSR_USCRATCH
  li t1, 0x4e2d68752d747261
  bne t0, t1, n_hu_handler_fail
  csrr t0, CSR_UTVAL
  la t1, test_data
  addi t1, t1, 8
  bne t0, t1, n_hu_handler_fail
  csrr t0, CSR_UEPC
  li t1, CASE_N_HU_LOAD_TRAP_URET
  beq s0, t1, n_hu_check_load
  li t1, CASE_N_HU_STORE_TRAP_URET
  beq s0, t1, n_hu_check_store
  j n_hu_handler_fail

n_hu_check_load:
  la t1, n_hu_load_fault
  bne t0, t1, n_hu_handler_fail
  csrr t0, CSR_FREASON
  li t1, FREASON_LOAD
  bne t0, t1, n_hu_handler_fail
  la t0, n_hu_load_recovery
  j n_hu_handler_return

n_hu_check_store:
  la t1, n_hu_store_fault
  bne t0, t1, n_hu_handler_fail
  csrr t0, CSR_FREASON
  li t1, FREASON_STORE
  bne t0, t1, n_hu_handler_fail
  la t0, n_hu_store_recovery

n_hu_handler_return:
  csrw CSR_UEPC, t0
  li a1, 0x4e
  .word 0x00200073
  j n_hu_handler_fail

n_hu_handler_fail:
  li a1, 0xdead
  j test_fail

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
  li t2, CAUSE_ILLEGAL_INSTRUCTION
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
  li t0, CASE_ALIGNED_ILLEGAL_LOAD
  beq s0, t0, check_expected_a2
  li t0, CASE_ALIGNED_ILLEGAL_STORE
  beq s0, t0, check_no_store_effect
  li t0, CASE_MISALIGNED_STORE
  beq s0, t0, check_no_store_effect
  li t0, CASE_ILLEGAL_JUMP
  beq s0, t0, check_expected_a2
  li t0, CASE_CALL_J_TRUSTED
  beq s0, t0, check_call_j_trusted_effect
  li t0, CASE_CALL_JR_TRUSTED
  beq s0, t0, check_call_jr_trusted_effect
  li t0, CASE_CALL_J_DISABLED
  bltu s0, t0, trap_pass
  li t0, CASE_S_LOAD_OPEN
  bltu s0, t0, check_call_illegal_effect
  beq s0, t0, check_expected_a2
  li t0, CASE_S_LOAD_CLOSED
  beq s0, t0, check_s_load_closed_effect
  li t0, CASE_S_STORE_OPEN
  beq s0, t0, check_no_store_effect
  li t0, CASE_S_STORE_CLOSED
  beq s0, t0, check_s_store_closed_effect
  li t0, CASE_S_JUMP_CLOSED
  beq s0, t0, check_s_jump_closed_effect
  li t0, CASE_S_JUMP_OPEN
  beq s0, t0, check_expected_a2
  li t0, CASE_SCALAR_LOAD_FIRST
  bltu s0, t0, trap_pass
  li t0, CASE_SCALAR_STORE_FIRST
  bltu s0, t0, check_scalar_load_effect
  li t0, CASE_SCALAR_LAST
  bgeu t0, s0, check_scalar_store_effect
  li t0, CASE_U_LOAD_TRUSTED
  li t1, CASE_JALR_ILLEGAL
  beq s0, t1, check_expected_a2
  bltu s0, t0, trap_pass
  li t0, CASE_U_STORE_TRUSTED
  bltu s0, t0, check_scalar_load_effect
  li t0, CASE_U_JUMP_TRUSTED
  bltu s0, t0, check_scalar_store_effect
  li t0, CASE_LIB_WRITE_ONLY_LOAD
  bltu s0, t0, check_expected_a2
  li t0, CASE_LIB_READ_ONLY_STORE
  beq s0, t0, check_scalar_store_effect
  li t0, CASE_LIB_SLOT15_LOAD
  beq s0, t0, check_scalar_load_effect
  li t0, CASE_LIB_REVERSED_STORE
  beq s0, t0, check_scalar_store_effect
  li t0, CASE_S_CSR_TRUSTED_READ
  bltu s0, t0, check_scalar_load_effect
  beq s0, t0, check_expected_a2
  li t0, CASE_S_CSR_UNTRUSTED_READ
  beq s0, t0, check_expected_a2
  li t0, CASE_S_CSR_UNTRUSTED_WRITE
  beq s0, t0, check_s_csr_write_effect
  li t0, CASE_S_CALL_J_TRUSTED
  beq s0, t0, check_s_call_j_trusted_effect
  li t0, CASE_S_CALL_JR_TRUSTED
  beq s0, t0, check_s_call_jr_trusted_effect
  li t0, CASE_U_MAIN_HI
  bltu s0, t0, check_call_illegal_effect
  li t0, CASE_CALL_JR_NON_RA_TRUSTED
  beq s0, t0, check_call_jr_non_ra_trusted_effect
  li t0, CASE_CALL_JR_NON_RA_ILLEGAL
  beq s0, t0, check_call_jr_non_ra_illegal_effect
  li t0, CASE_CALL_J_POSITIVE
  beq s0, t0, check_call_j_positive_effect
  li t0, CASE_CALL_J_NEGATIVE
  beq s0, t0, check_call_j_negative_effect
  li t0, CASE_C_JALR_ILLEGAL
  beq s0, t0, check_c_jalr_illegal_effect
  li t0, CASE_S_LOAD_TRUSTED
  beq s0, t0, check_scalar_load_effect
  li t0, CASE_S_LOAD_DISABLED
  beq s0, t0, check_scalar_load_effect
  li t0, CASE_S_STORE_TRUSTED
  beq s0, t0, check_scalar_store_effect
  li t0, CASE_S_STORE_DISABLED
  beq s0, t0, check_scalar_store_effect
  li t0, CASE_S_JUMP_TRUSTED
  beq s0, t0, check_expected_a2
  li t0, CASE_S_JUMP_DISABLED
  beq s0, t0, check_expected_a2
  li t0, CASE_S_LOAD_BOUND_ALLOW
  beq s0, t0, check_scalar_load_effect
  li t0, CASE_S_STORE_BOUND_ALLOW
  beq s0, t0, check_scalar_store_effect
  li t0, CASE_S_JUMP_BOUND_ALLOW
  beq s0, t0, check_expected_a2
  li t0, CASE_S_JUMP_SPECIAL_ALLOW
  beq s0, t0, check_expected_a2
  j trap_pass
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

check_call_j_trusted_effect:
  li t0, 0x4a
  bne a2, t0, side_effect_fail
  la t0, call_j_trusted_return_site
  bne ra, t0, side_effect_fail
  csrr t1, CSR_RETURN_PC
  bne t1, t0, side_effect_fail
  j trap_pass

check_call_jr_trusted_effect:
  li t0, 0x4b
  bne a2, t0, side_effect_fail
  la t0, call_jr_trusted_return_site
  bne ra, t0, side_effect_fail
  csrr t1, CSR_RETURN_PC
  bne t1, t0, side_effect_fail
  j trap_pass

check_call_illegal_effect:
  li t0, 0x6666666666666666
  bne ra, t0, side_effect_fail
  bnez a2, side_effect_fail
  csrr t1, CSR_RETURN_PC
  li t0, 0x5555555555555555
  bne t1, t0, side_effect_fail
  j trap_pass

check_s_load_closed_effect:
  li t0, 0x1111111111111111
  bne a2, t0, side_effect_fail
  j trap_pass

check_s_store_closed_effect:
  la t0, test_data
  ld t1, 0(t0)
  li t2, 0x7777777777777777
  bne t1, t2, side_effect_fail
  j trap_pass

check_s_jump_closed_effect:
  li t0, 0x5b
  bne a2, t0, side_effect_fail
  j trap_pass

check_expected_a2:
  la t0, expected_aux0
  ld t0, 0(t0)
  bne a2, t0, side_effect_fail
  j trap_pass

check_s_csr_write_effect:
  csrr t1, CSR_LIB_CFG
  la t0, expected_aux0
  ld t0, 0(t0)
  bne t1, t0, side_effect_fail
  j trap_pass

check_s_call_j_trusted_effect:
  li t0, 0x7a
  bne a2, t0, side_effect_fail
  la t0, s_call_j_trusted_return_site
  bne ra, t0, side_effect_fail
  csrr t1, CSR_RETURN_PC
  bne t1, t0, side_effect_fail
  j trap_pass

check_s_call_jr_trusted_effect:
  li t0, 0x7b
  bne a2, t0, side_effect_fail
  la t0, s_call_jr_trusted_return_site
  bne ra, t0, side_effect_fail
  csrr t1, CSR_RETURN_PC
  bne t1, t0, side_effect_fail
  j trap_pass

check_call_jr_non_ra_trusted_effect:
  la t0, call_jr_non_ra_trusted_return_site
  bne a2, t0, side_effect_fail
  li t1, 0x6666666666666666
  bne ra, t1, side_effect_fail
  csrr t1, CSR_RETURN_PC
  bne t1, t0, side_effect_fail
  li t0, 0x7e
  bne a3, t0, side_effect_fail
  j trap_pass

check_call_jr_non_ra_illegal_effect:
  li t0, 0x5a5a5a5a5a5a5a5a
  bne a2, t0, side_effect_fail
  li t0, 0x6666666666666666
  bne ra, t0, side_effect_fail
  bnez a3, side_effect_fail
  csrr t1, CSR_RETURN_PC
  li t0, 0x5555555555555555
  bne t1, t0, side_effect_fail
  j trap_pass

check_call_j_positive_effect:
  li t0, 0x80
  bne a2, t0, side_effect_fail
  la t0, call_j_positive_return_site
  bne ra, t0, side_effect_fail
  csrr t1, CSR_RETURN_PC
  bne t1, t0, side_effect_fail
  j trap_pass

check_call_j_negative_effect:
  li t0, 0x81
  bne a2, t0, side_effect_fail
  la t0, call_j_negative_return_site
  bne ra, t0, side_effect_fail
  csrr t1, CSR_RETURN_PC
  bne t1, t0, side_effect_fail
  j trap_pass

check_c_jalr_illegal_effect:
  li t0, 0x6666666666666666
  bne ra, t0, side_effect_fail
  j trap_pass

check_scalar_load_effect:
  la t0, expected_aux0
  ld t0, 0(t0)
  bne a2, t0, side_effect_fail
  j trap_pass

check_scalar_store_effect:
  la t0, scalar_data
  ld t1, 0(t0)
  la t2, expected_aux0
  ld t2, 0(t2)
  bne t1, t2, side_effect_fail
  ld t1, 8(t0)
  la t2, expected_aux1
  ld t2, 0(t2)
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
expected_aux0:
  .quad 0
expected_aux1:
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

  .balign 8
scalar_data:
  .quad 0x88776655f4e3d2c1
  .quad 0x99aabbccddeeff00
