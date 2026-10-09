/* The production translation units are included to inject faults into their
 * private storage without adding an architectural import or debug setter. */
#define FDI_BANK_TEST
#include "fdi-stubs/trap-isolation.h"
#include "../../src/isa/riscv64/system/dasics.c"
#include "../../src/isa/riscv64/difftest/fdi.c"

struct FdiTestCpu cpu = { .pc = UINT64_C(0x10000000), .mode = MODE_M };

static void rejected(uint32_t phase) {
  struct { uint64_t before; DifftestFdiState state; uint64_t after; } buffer;
  memset(&buffer, 0xa5, sizeof(buffer));
  unsigned char saved[sizeof(buffer)];
  memcpy(saved, &buffer, sizeof(buffer));
  int32_t rc = phase == DIFFTEST_FDI_PHASE_RESET ?
    difftest_fdi_capture_reset(0, &buffer.state, sizeof(buffer.state)) :
    difftest_fdi_get_state(0, &buffer.state, sizeof(buffer.state));
  assert(rc == DIFFTEST_FDI_E_INVARIANT);
  assert(memcmp(saved, &buffer, sizeof(buffer)) == 0);
}

int main(void) {
  fdi_note_reset();
  dasics_reset();
  dasics_bank.main_call_entry = 1;
  rejected(DIFFTEST_FDI_PHASE_RESET);
  dasics_bank.main_call_entry = 0;
  DifftestFdiState state;
  assert(difftest_fdi_capture_reset(0, &state, sizeof(state)) == DIFFTEST_FDI_OK);
  DifftestFdiInit init = { DIFFTEST_FDI_VERSION, sizeof(init), 0, 0, 17, DIFFTEST_FDI_FEATURES };
  dasics_bank.return_pc = 1;
  assert(difftest_fdi_init(&init, sizeof(init)) == DIFFTEST_FDI_E_INVARIANT);
  assert(dasics_bank.return_pc == 1);
  dasics_bank.return_pc = 0;
  assert(difftest_fdi_init(&init, sizeof(init)) == DIFFTEST_FDI_OK);

  struct { uint64_t *word; uint64_t invalid; } faults[48];
  size_t count = 0;
#define FAULT(word, bit) faults[count++] = (typeof(faults[0])){ &(word), (bit) }
  FAULT(dasics_bank.main_cfg, UINT64_C(1) << 63);
  FAULT(dasics_bank.lib_cfg, UINT64_C(1) << 2);
  FAULT(dasics_bank.jump_cfg, UINT64_C(1) << 1);
  FAULT(dasics_bank.freason, UINT64_C(1) << 3);
  for (size_t i = 0; i < 2; i++) {
    FAULT(dasics_bank.s_main_bound[i], 1);
    FAULT(dasics_bank.u_main_bound[i], 1);
  }
  for (size_t i = 0; i < 32; i++) FAULT(dasics_bank.lib_bound[i], 1);
  for (size_t i = 0; i < 8; i++) FAULT(dasics_bank.jump_bound[i], 1);
#undef FAULT
  assert(count == 48);
  for (size_t i = 0; i < count; i++) {
    *faults[i].word = faults[i].invalid;
    rejected(DIFFTEST_FDI_PHASE_CURRENT);
    assert(*faults[i].word == faults[i].invalid);
    *faults[i].word = 0;
  }
  dasics_bank.main_cfg = 0x7ff;
  dasics_bank.main_call_entry = UINT64_C(0xfedcba987654321f);
  dasics_bank.return_pc = UINT64_MAX;
  dasics_bank.active_zone_return_pc = UINT64_C(0x8000000000000001);
  for (uint64_t reason = 0; reason < 8; reason++) {
    dasics_bank.freason = reason;
    assert(difftest_fdi_get_state(0, &state, sizeof(state)) == DIFFTEST_FDI_OK);
    assert(state.words[0] == 0x7ff && state.words[1] == 0x7c2);
    assert(state.words[39] == UINT64_C(0xfedcba987654321f));
    assert(state.words[40] == UINT64_MAX);
    assert(state.words[41] == UINT64_C(0x8000000000000001));
    assert(state.words[42] == reason);
  }
  puts("FDI_BANK_TEST PASS: 48 raw invariant faults, reset pollution, all FReason values, full PC bits");
  return 0;
}
