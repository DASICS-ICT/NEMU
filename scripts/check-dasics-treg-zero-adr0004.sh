#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

mkdir -p "$tmpdir/include/cpu"

cat > "$tmpdir/include/common.h" <<'EOF'
#ifndef __COMMON_H__
#define __COMMON_H__

#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#define CONFIG_ISA64 1
#define CONFIG_RV_DASICS 1
#define CONFIG_RV_DASICS_TREG_ZERO 1
#define CONFIG_RVN 1
#define CONFIG_RV_PMP_CSR 1

#include "macro.h"

typedef uint64_t word_t;
typedef int64_t sword_t;
typedef uint64_t rtlreg_t;
typedef uint64_t vaddr_t;

#endif
EOF

cat > "$tmpdir/include/isa.h" <<'EOF'
#ifndef __ISA_H__
#define __ISA_H__

#include <common.h>

enum { MODE_U = 0, MODE_S, MODE_H, MODE_M };

typedef struct {
  union { uint64_t _64; } gpr[32];
  union { uint64_t _64; } fpr[32];
  uint64_t mode;
  uint32_t dasics_treg_zero_int_init_bits;
  uint32_t dasics_treg_zero_fp_init_bits;
  bool dasics_treg_zero_pending_clear;
  bool dasics_treg_zero_treg_not_cleaned;
} CPU_state;

extern CPU_state cpu;

#endif
EOF

cat > "$tmpdir/include/cpu/decode.h" <<'EOF'
#ifndef __CPU_DECODE_H__
#define __CPU_DECODE_H__

#include <isa.h>

typedef struct {
  rtlreg_t *preg;
  int8_t reg_idx;
  uint8_t reg_is_fp;
} Operand;

typedef struct Decode {
  vaddr_t pc;
  Operand dest;
} Decode;

#endif
EOF

cat > "$tmpdir/adr0004_test.c" <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <isa.h>
#include "src/isa/riscv64/local-include/csr.h"

CPU_state cpu;
rtlreg_t csr_array[4096];

#define DEFINE_CSR(name, addr) name##_t * const name = (name##_t *)&csr_array[addr];
MAP(CSRS, DEFINE_CSR)
MAP(NCSRS, DEFINE_CSR)
MAP(DASICS_CSRS, DEFINE_CSR)
MAP(MPK_CSRS, DEFINE_CSR)

bool dasics_in_trusted_zone(uint64_t pc) {
  bool is_smain_enable = dsmcfg->mcfg_sena;
  bool is_umain_enable = dsmcfg->mcfg_uena;
  bool in_smain_zone = pc >= dsmbound0->val && pc < dsmbound1->val && cpu.mode == MODE_S && is_smain_enable;
  bool in_umain_zone = pc >= dumbound0->val && pc < dumbound1->val && cpu.mode == MODE_U && is_umain_enable;
  bool in_s_trusted_zone = in_smain_zone || (cpu.mode == MODE_S && !is_smain_enable);
  bool in_u_trusted_zone = in_umain_zone || (cpu.mode == MODE_U && !is_umain_enable);
  return cpu.mode == MODE_M || in_s_trusted_zone || in_u_trusted_zone;
}

#include "src/isa/riscv64/system/dasics_treg_zero.c"

static void require_true(bool condition, const char *message) {
  if (!condition) {
    fprintf(stderr, "FAIL: %s\n", message);
    exit(1);
  }
}

static void reset_case(void) {
  for (int i = 0; i < 4096; i++) csr_array[i] = 0;
  cpu.mode = MODE_M;
  dasics_treg_zero_reset();
}

static void set_u_trusted_range(uint64_t lo, uint64_t hi) {
  dsmcfg->mcfg_uena = 1;
  dumbound0->val = lo;
  dumbound1->val = hi;
}

int main(void) {
  Decode s = { .pc = 0x1000, .dest = { .reg_idx = 5, .reg_is_fp = 0 } };

  reset_case();
  set_u_trusted_range(0x2000, 0x3000);
  cpu.mode = MODE_U;
  dasics_treg_zero_trap_entry(0x1000);
  require_true(dasics_treg_zero_treg_not_cleaned(), "U untrusted trap sets state");

  reset_case();
  set_u_trusted_range(0x2000, 0x3000);
  cpu.mode = MODE_S;
  dasics_treg_zero_trap_entry(0x1000);
  require_true(!dasics_treg_zero_treg_not_cleaned(), "S trap does not set state");

  reset_case();
  set_u_trusted_range(0x2000, 0x3000);
  cpu.mode = MODE_M;
  dasics_treg_zero_trap_entry(0x1000);
  require_true(!dasics_treg_zero_treg_not_cleaned(), "M trap does not set state");

  reset_case();
  dsmcfg->mcfg_uena = 0;
  cpu.mode = MODE_U;
  dasics_treg_zero_trap_entry(0x1000);
  require_true(!dasics_treg_zero_treg_not_cleaned(), "DASICS U disable prevents set");

  reset_case();
  set_u_trusted_range(0x2000, 0x3000);
  cpu.mode = MODE_U;
  dasics_treg_zero_trap_entry(0x1000);
  dasics_treg_zero_xret(true, MODE_S, 0x2100);
  require_true(dasics_treg_zero_treg_not_cleaned(), "MRET/SRET to S keeps state");
  cpu.mode = MODE_S;
  dasics_treg_zero_trap_entry(0x2000);
  require_true(dasics_treg_zero_treg_not_cleaned(), "nested S trap keeps state");
  dasics_treg_zero_xret(false, MODE_U, 0x1000);
  require_true(dasics_treg_zero_treg_not_cleaned(), "illegal xRET does not clear");
  dasics_treg_zero_xret(true, MODE_U, 0x2100);
  require_true(dasics_treg_zero_treg_not_cleaned(), "legal xRET to U trusted stub keeps state");
  dasics_treg_zero_xret(true, MODE_U, 0x1000);
  require_true(!dasics_treg_zero_treg_not_cleaned(), "legal xRET to U untrusted clears state");

  reset_case();
  set_u_trusted_range(0x2000, 0x3000);
  cpu.dasics_treg_zero_treg_not_cleaned = true;
  cpu.dasics_treg_zero_int_init_bits &= ~(1u << 5);
  cpu.mode = MODE_U;
  require_true(dasics_treg_zero_rewrite_context(0x2100), "treg window is rewrite context in trusted handler");
  require_true(!dasics_treg_zero_int_src_is_init(5), "t0 init bit is clear");
  dasics_treg_zero_commit_hook(&s);
  require_true(dasics_treg_zero_int_src_is_init(5), "handler write sets init bit in treg window");
  cpu.dasics_treg_zero_int_init_bits &= ~(1u << 8);
  cpu.dasics_treg_zero_fp_init_bits &= ~(1u << 8);
  require_true(dasics_treg_zero_int_src_is_init(8), "non-protected integer source is never rewritten");
  require_true(dasics_treg_zero_fp_src_is_init(8), "non-protected FP source is never rewritten");

  reset_case();
  dsmcfg->mcfg_uena = 0;
  cpu.dasics_treg_zero_treg_not_cleaned = true;
  cpu.mode = MODE_U;
  require_true(!dasics_treg_zero_rewrite_context(0x4000), "DASICS U disable gates rewrite context");

  return 0;
}
EOF

gcc -std=c11 -Wall -Wextra -Wno-unused-parameter -Werror=implicit-function-declaration \
  -I"$tmpdir/include" \
  -I"$repo_root/include" \
  -I"$repo_root" \
  -o "$tmpdir/adr0004_test" "$tmpdir/adr0004_test.c"

"$tmpdir/adr0004_test"
echo "dasics-treg-zero ADR 0004 focused checks passed"
