#include <isa.h>
#include "../local-include/dasics.h"

#ifdef CONFIG_RV_DASICS

/* FDI state is private to the model, outside both legacy copy interfaces.
 * The two MainCfg views share one backing; all modes share Lib/Jump state.
 * Each bound array stores consecutive Lo/Hi pairs in CSR address order. */
static struct {
  word_t main_cfg;
  word_t s_main_bound[2];
  word_t u_main_bound[2];
  word_t lib_cfg;
  word_t lib_bound[32];
  word_t main_call_entry;
  word_t return_pc;
  word_t active_zone_return_pc;
  word_t freason;
  word_t jump_cfg;
  word_t jump_bound[8];
} dasics_bank;

_Static_assert(sizeof(dasics_bank) == 51 * sizeof(uint64_t), "FDI requires 51 RV64 backing words");

typedef struct {
  word_t *backing;
  word_t mask;
} DasicsCsrView;

static DasicsCsrView dasics_csr_view(uint32_t address) {
  if (address >= CSR_FDI_SMAINBOUNDLO && address <= CSR_FDI_SMAINBOUNDHI) {
    return (DasicsCsrView){ &dasics_bank.s_main_bound[address - CSR_FDI_SMAINBOUNDLO], DASICS_BOUND_MASK };
  }
  if (address >= CSR_FDI_UMAINBOUNDLO && address <= CSR_FDI_UMAINBOUNDHI) {
    return (DasicsCsrView){ &dasics_bank.u_main_bound[address - CSR_FDI_UMAINBOUNDLO], DASICS_BOUND_MASK };
  }
  if (address >= CSR_FDI_LIBBOUNDLO0 && address <= CSR_FDI_LIBBOUNDHI15) {
    return (DasicsCsrView){ &dasics_bank.lib_bound[address - CSR_FDI_LIBBOUNDLO0], DASICS_BOUND_MASK };
  }
  if (address >= CSR_FDI_JUMPBOUNDLO0 && address <= CSR_FDI_JUMPBOUNDHI3) {
    return (DasicsCsrView){ &dasics_bank.jump_bound[address - CSR_FDI_JUMPBOUNDLO0], DASICS_BOUND_MASK };
  }
  switch (address) {
    case CSR_FDI_SMAINCFG: return (DasicsCsrView){ &dasics_bank.main_cfg, DASICS_SMAINCFG_MASK };
    case CSR_FDI_UMAINCFG: return (DasicsCsrView){ &dasics_bank.main_cfg, DASICS_UMAINCFG_MASK };
    case CSR_FDI_LIBCFG: return (DasicsCsrView){ &dasics_bank.lib_cfg, DASICS_LIBCFG_MASK };
    case CSR_FDI_MAINCALLENTRY: return (DasicsCsrView){ &dasics_bank.main_call_entry, DASICS_PC_MASK };
    case CSR_FDI_RETURNPC: return (DasicsCsrView){ &dasics_bank.return_pc, DASICS_PC_MASK };
    case CSR_FDI_ACTIVEZONERETURNPC: return (DasicsCsrView){ &dasics_bank.active_zone_return_pc, DASICS_PC_MASK };
    case CSR_FDI_FREASON: return (DasicsCsrView){ &dasics_bank.freason, DASICS_FREASON_MASK };
    case CSR_FDI_JUMPCFG: return (DasicsCsrView){ &dasics_bank.jump_cfg, DASICS_JUMPCFG_MASK };
    default: return (DasicsCsrView){ NULL, 0 };
  }
}

void dasics_reset(void) {
  memset(&dasics_bank, 0, sizeof(dasics_bank));
}

/* Check raw storage before deriving the U alias. CSR reads alone would hide
 * reserved-bit corruption and therefore cannot establish export canonicality. */
bool dasics_export_state(uint64_t words[52]) {
  if ((dasics_bank.main_cfg & ~DASICS_SMAINCFG_MASK) ||
      (dasics_bank.lib_cfg & ~DASICS_LIBCFG_MASK) ||
      (dasics_bank.jump_cfg & ~DASICS_JUMPCFG_MASK) ||
      (dasics_bank.freason & ~DASICS_FREASON_MASK)) return false;
  for (size_t i = 0; i < 2; i++) {
    if ((dasics_bank.s_main_bound[i] | dasics_bank.u_main_bound[i]) & ~DASICS_BOUND_MASK)
      return false;
  }
  for (size_t i = 0; i < 32; i++) {
    if (dasics_bank.lib_bound[i] & ~DASICS_BOUND_MASK) return false;
  }
  for (size_t i = 0; i < 8; i++) {
    if (dasics_bank.jump_bound[i] & ~DASICS_BOUND_MASK) return false;
  }
  words[0] = dasics_bank.main_cfg;
  words[1] = dasics_bank.main_cfg & DASICS_UMAINCFG_MASK;
  memcpy(words + 2, dasics_bank.s_main_bound, sizeof(dasics_bank.s_main_bound));
  memcpy(words + 4, dasics_bank.u_main_bound, sizeof(dasics_bank.u_main_bound));
  words[6] = dasics_bank.lib_cfg;
  memcpy(words + 7, dasics_bank.lib_bound, sizeof(dasics_bank.lib_bound));
  words[39] = dasics_bank.main_call_entry;
  words[40] = dasics_bank.return_pc;
  words[41] = dasics_bank.active_zone_return_pc;
  words[42] = dasics_bank.freason;
  words[43] = dasics_bank.jump_cfg;
  memcpy(words + 44, dasics_bank.jump_bound, sizeof(dasics_bank.jump_bound));
  return true;
}

bool dasics_is_csr(uint32_t address) {
  return dasics_csr_view(address).backing != NULL;
}

word_t dasics_csr_read(uint32_t address) {
  DasicsCsrView view = dasics_csr_view(address);
  assert(view.backing != NULL);
  return *view.backing & view.mask;
}

void dasics_csr_write(uint32_t address, word_t value) {
  DasicsCsrView view = dasics_csr_view(address);
  assert(view.backing != NULL);
  /* The operand is a view value; UMainCfg writes must retain hidden S bits.
   * Bounds only clear bits 2:0, without truncating or ordering the endpoints. */
  *view.backing = (*view.backing & ~view.mask) | (value & view.mask);
}

bool dasics_csr_source_permitted(vaddr_t source_pc) {
  if (MUXDEF(CONFIG_RVH, cpu.v, false)) return false;
  if (cpu.mode == MODE_M) return true;
  word_t *bound;
  word_t enable;
  if (cpu.mode == MODE_S) {
    bound = dasics_bank.s_main_bound;
    enable = UINT64_C(1);
  } else if (cpu.mode == MODE_U) {
    bound = dasics_bank.u_main_bound;
    enable = UINT64_C(2);
  } else {
    return false;
  }
  /* This check runs before any write. Close bits do not authorize CSR access,
   * and an empty interval remains empty even when its upper bound is zero. */
  return !(dasics_bank.main_cfg & enable) ||
    (source_pc >= bound[0] && source_pc < bound[1]);
}

#endif
