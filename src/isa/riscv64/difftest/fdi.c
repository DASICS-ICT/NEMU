#include <isa.h>
#include <difftest-fdi.h>
#include "../local-include/dasics.h"

#define FDI_ENABLED_FEATURES MUXDEF(CONFIG_RV_DASICS, DIFFTEST_FDI_FEATURES, 0)

int32_t difftest_fdi_query_caps(void *out, uint32_t out_bytes) {
  if (!out || out_bytes != sizeof(DifftestFdiCaps)) return DIFFTEST_FDI_E_ABI;
  DifftestFdiCaps caps = {
    .version = DIFFTEST_FDI_VERSION, .bytes = sizeof(caps),
    .state_bytes = sizeof(DifftestFdiState), .projection_words = DIFFTEST_FDI_PROJECTION_WORDS,
    .supported_features = DIFFTEST_FDI_FEATURES, .enabled_features = FDI_ENABLED_FEATURES,
    .xlen = DIFFTEST_FDI_XLEN, .max_harts = DIFFTEST_FDI_MAX_HARTS,
    .init_bytes = sizeof(DifftestFdiInit), .projection_version = DIFFTEST_FDI_PROJECTION_VERSION,
    .machine_abi_major = DIFFTEST_FDI_MACHINE_ABI_MAJOR
  };
  memcpy(out, &caps, sizeof(caps));
  return DIFFTEST_FDI_OK;
}

#ifdef CONFIG_RV_DASICS
/* Imports are allowed between reset capture and session binding, but guest
 * instructions and accepted trap events are not. This boolean observation
 * remains passive for clients that do not start FDI export. */
static struct {
  bool cold_reset, imported, executed, captured, initialized;
  uint64_t epoch;
} fdi;

/* Reinitialization remains available to ordinary clients, but a reused model
 * instance cannot supply the first natural reset required by FDI cold start. */
static bool model_initialized;

void fdi_check_reset(void) {
  Assert(!fdi.captured && !fdi.initialized, "FDI reference forbids warm reset after reset capture");
}

void fdi_note_reset(void) {
  fdi_check_reset();
  memset(&fdi, 0, sizeof(fdi));
  fdi.cold_reset = !model_initialized;
  model_initialized = true;
}

void fdi_note_execution(void) {
  fdi.executed = true;
}

void fdi_check_import(void) {
  Assert(!fdi.initialized, "FDI reference forbids imports after protocol initialization");
  fdi.imported = true;
}

static int32_t snapshot(DifftestFdiState *state, bool reset) {
  *state = (DifftestFdiState){
    .version = DIFFTEST_FDI_VERSION, .bytes = sizeof(*state), .hart = 0,
    .phase = reset ? DIFFTEST_FDI_PHASE_RESET : DIFFTEST_FDI_PHASE_CURRENT,
    .epoch = reset ? 0 : fdi.epoch, .model_pc = cpu.pc
  };
  if (!dasics_export_state(state->words)) return DIFFTEST_FDI_E_INVARIANT;
  if (reset) {
    for (size_t i = 0; i < DIFFTEST_FDI_PROJECTION_WORDS; i++) {
      if (state->words[i]) return DIFFTEST_FDI_E_INVARIANT;
    }
  }
  return DIFFTEST_FDI_OK;
}
#endif

int32_t difftest_fdi_capture_reset(uint32_t hart, void *out, uint32_t out_bytes) {
  if (!out || out_bytes != sizeof(DifftestFdiState)) return DIFFTEST_FDI_E_ABI;
#ifndef CONFIG_RV_DASICS
  return DIFFTEST_FDI_E_FEATURE;
#else
  if (hart) return DIFFTEST_FDI_E_HART;
  if (!fdi.cold_reset || fdi.imported || fdi.executed || fdi.captured || fdi.initialized)
    return DIFFTEST_FDI_E_STATE;
  DifftestFdiState state;
  int32_t rc = snapshot(&state, true);
  if (rc) return rc;
  memcpy(out, &state, sizeof(state));
  fdi.captured = true;
  return DIFFTEST_FDI_OK;
#endif
}

int32_t difftest_fdi_init(const void *input, uint32_t input_bytes) {
  if (!input || input_bytes != sizeof(DifftestFdiInit)) return DIFFTEST_FDI_E_ABI;
  DifftestFdiInit init;
  memcpy(&init, input, sizeof(init));
  if (init.version != DIFFTEST_FDI_VERSION || init.bytes != sizeof(init) || init.reserved)
    return DIFFTEST_FDI_E_ABI;
#ifndef CONFIG_RV_DASICS
  return DIFFTEST_FDI_E_FEATURE;
#else
  if (init.required_features != FDI_ENABLED_FEATURES) return DIFFTEST_FDI_E_FEATURE;
  if (init.hart) return DIFFTEST_FDI_E_HART;
  if (!init.epoch || !fdi.captured || fdi.initialized || fdi.executed) return DIFFTEST_FDI_E_STATE;
  DifftestFdiState state;
  int32_t rc = snapshot(&state, true);
  if (rc) return rc;
  fdi.epoch = init.epoch;
  fdi.initialized = true;
  return DIFFTEST_FDI_OK;
#endif
}

int32_t difftest_fdi_get_state(uint32_t hart, void *out, uint32_t out_bytes) {
  if (!out || out_bytes != sizeof(DifftestFdiState)) return DIFFTEST_FDI_E_ABI;
#ifndef CONFIG_RV_DASICS
  return DIFFTEST_FDI_E_FEATURE;
#else
  if (hart) return DIFFTEST_FDI_E_HART;
  if (!fdi.initialized) return DIFFTEST_FDI_E_STATE;
  DifftestFdiState state;
  int32_t rc = snapshot(&state, false);
  if (rc) return rc;
  memcpy(out, &state, sizeof(state));
  return DIFFTEST_FDI_OK;
#endif
}
