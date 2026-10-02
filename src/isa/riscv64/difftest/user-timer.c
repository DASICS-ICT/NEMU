#include <isa.h>
#include <cpu/cpu.h>
#include <cpu/exec.h>
#include <difftest.h>
#include "../local-include/csr.h"
#include "../local-include/user-timer.h"

#define UIT_ENABLED_FEATURES MUXDEF(CONFIG_RV_DASICS, DIFFTEST_UIT_FEATURES, 0)

int32_t difftest_uit_query_caps(void *out, uint32_t out_bytes) {
  if (!out || out_bytes != sizeof(DifftestUitCaps)) return DIFFTEST_UIT_E_ABI;
  DifftestUitCaps caps = {
    .version = DIFFTEST_UIT_VERSION, .bytes = sizeof(caps),
    .enabled_features = UIT_ENABLED_FEATURES,
    .supported_features = DIFFTEST_UIT_FEATURES,
    .xlen = 64, .vlen = MUXDEF(CONFIG_RVV, VLEN, 0),
    .legacy_regcpy_bytes = DIFFTEST_REG_SIZE,
    .legacy_csrcpy_bytes = 4096 * sizeof(rtlreg_t),
    .legacy_regcpy_arity = MUXDEF(CONFIG_LIGHTQS, 4, 2), .max_harts = 1,
    .exec_request_bytes = sizeof(DifftestUitExecRequest),
    .event_request_bytes = sizeof(DifftestUitHUEvent),
    .state_bytes = sizeof(DifftestUitState), .exec_result_bytes = sizeof(DifftestUitExecResult)
  };
  memcpy(out, &caps, sizeof(caps));
  return DIFFTEST_UIT_OK;
}

#ifdef CONFIG_RV_DASICS
#if !defined(CONFIG_HAS_UARTLITE) || CONFIG_UARTLITE_MMIO != 0x40600000
#error "Controlled user timer reference requires UARTLite TX at 0x40600004"
#endif
_Static_assert(offsetof(CPU_state, amo) == DIFFTEST_REG_SIZE, "Legacy regcpy prefix must remain contiguous");

#define UIT_TX_CAPACITY 4096

/* One descriptor is armed only for one normal cpu_exec(1). Retirement and
 * cancellation queues belong to the DUT bridge, not to this reference model. */
static struct {
  bool initialized, started, active, fetched, faulted;
  uint64_t epoch, sequence, last_uid, last_event_uid, instruction_count, tx_sequence;
  int32_t error;
  DifftestUitExecRequest request;
  DifftestUitExecResult result;
  DifftestUitTx tx[UIT_TX_CAPACITY];
  uint32_t tx_head, tx_count;
} uit;

bool uit_is_csr(uint32_t address) {
  switch (address) {
    case CSR_USTATUS: case CSR_UIE: case CSR_UTVEC: case CSR_USCRATCH:
    case CSR_UEPC: case CSR_UCAUSE: case CSR_UTVAL: case CSR_UIP: case CSR_UTIMER:
      return true;
    default: return false;
  }
}

static void reset_user_bank(void) {
  const uint16_t addresses[] = { CSR_USTATUS, CSR_UIE, CSR_UTVEC, CSR_USCRATCH,
    CSR_UEPC, CSR_UCAUSE, CSR_UTVAL, CSR_UIP, CSR_UTIMER };
  for (size_t i = 0; i < sizeof(addresses) / sizeof(addresses[0]); i++) csr_array[addresses[i]] = 0;
  IFDEF(CONFIG_RV_DASICS, cpu.uit_in_handler = false);
}

void uit_reset(void) {
  memset(&uit, 0, sizeof(uit));
  reset_user_bank();
}

void uit_note_execution(void) {
  uit.started = true;
  uit.faulted = false;
}

void uit_note_retirement(void) {
  // Faulting instructions do not advance the boundary carried by HU events.
  if (uit.initialized && !uit.faulted) uit.instruction_count++;
}

void uit_check_import(void) {
  Assert(!uit.initialized && !uit.started, "User timer reference forbids imports after protocol initialization");
}

static _Noreturn void protocol_abort(int32_t error) {
  uit.error = error;
  fprintf(stderr, "UIT protocol error %d at reference PC 0x%016lx\n", error, cpu.pc);
  nemu_state.state = NEMU_ABORT;
  nemu_state.halt_pc = cpu.pc;
  nemu_state.halt_ret = 1;
  longjmp_context(NEMU_EXEC_END);
}

void uit_validate_fetched(uint64_t pc, uint32_t instruction) {
  uint32_t funct3 = (instruction >> 12) & 7;
  bool controlled = (ISDEF(CONFIG_RV_DASICS) && instruction == UINT32_C(0x00200073)) ||
    ((instruction & 0x7f) == 0x73 && funct3 != 0 && uit_is_csr(instruction >> 20));
  if (!uit.active) {
    if (controlled) protocol_abort(uit.initialized ? DIFFTEST_UIT_E_STATE : DIFFTEST_UIT_E_UNSUPPORTED);
    return;
  }
  if (uit.fetched) protocol_abort(DIFFTEST_UIT_E_SAMPLE_DUPLICATE);
  if (pc != uit.request.diagnostic_pc) protocol_abort(DIFFTEST_UIT_E_PC);
  if (instruction != uit.request.instruction) protocol_abort(DIFFTEST_UIT_E_INSTRUCTION);
  uit.fetched = true;
}

void uit_note_exception(uint32_t cause) {
  uit.faulted = true;
  if (uit.active) {
    uit.result.outcome = DIFFTEST_UIT_ISA_EXCEPTION;
    uit.result.exception_cause = cause;
  }
}

void uit_validate_csr_access(uint32_t address, bool reads) {
  if (!uit.active || !uit.fetched) protocol_abort(DIFFTEST_UIT_E_STATE);
  if (address != uit.request.csr) protocol_abort(DIFFTEST_UIT_E_CSR);
  uint8_t expected = !reads ? DIFFTEST_UIT_NO_SAMPLE :
    address == CSR_UTIMER ? DIFFTEST_UIT_TIMER_SAMPLE :
    address == CSR_UIP ? DIFFTEST_UIT_PENDING_SAMPLE : DIFFTEST_UIT_NO_SAMPLE;
  if (expected && !uit.request.sample_kind) protocol_abort(DIFFTEST_UIT_E_SAMPLE_MISSING);
  if (uit.request.sample_kind != expected) protocol_abort(DIFFTEST_UIT_E_SAMPLE_UNEXPECTED);
}

uint64_t uit_read_sample(uint32_t address) {
  if (!uit.active || !uit.request.sample_kind) protocol_abort(DIFFTEST_UIT_E_SAMPLE_MISSING);
  if (uit.result.sample_consumed) protocol_abort(DIFFTEST_UIT_E_SAMPLE_DUPLICATE);
  if (address != uit.request.csr) protocol_abort(DIFFTEST_UIT_E_CSR);
  uit.result.sample_consumed = 1;
  return address == CSR_UIP ? uit.request.sample_payload << 4 : uit.request.sample_payload;
}

void uit_note_csr_write(uint64_t value) {
  uit.result.csr_write_valid = 1;
  uit.result.csr_write_value = value;
}

static int32_t ready(void) {
  if (!uit.initialized || uit.active) return DIFFTEST_UIT_E_STATE;
  return uit.error;
}

static int32_t identity(uint32_t version, uint32_t bytes, uint32_t expected_bytes,
                        uint32_t hart, uint64_t epoch, uint64_t sequence) {
  if (version != DIFFTEST_UIT_VERSION || bytes != expected_bytes) return DIFFTEST_UIT_E_ABI;
  if (hart != 0) return DIFFTEST_UIT_E_ID;
  if (epoch != uit.epoch) return DIFFTEST_UIT_E_EPOCH;
  if (!sequence || sequence != uit.sequence + 1) return DIFFTEST_UIT_E_ORDER;
  return DIFFTEST_UIT_OK;
}

int32_t difftest_uit_init(const void *input, uint32_t input_bytes) {
  if (!input || input_bytes != sizeof(DifftestUitInit)) return DIFFTEST_UIT_E_ABI;
  DifftestUitInit init;
  memcpy(&init, input, sizeof(init));
  if (init.version != DIFFTEST_UIT_VERSION || init.bytes != sizeof(init) || init.reserved)
    return DIFFTEST_UIT_E_ABI;
  if (init.required_features != UIT_ENABLED_FEATURES) return DIFFTEST_UIT_E_FEATURE;
  if (init.hart != 0) return DIFFTEST_UIT_E_ID;
  if (!init.epoch) return DIFFTEST_UIT_E_EPOCH;
  if (uit.initialized || uit.started) return DIFFTEST_UIT_E_STATE;
  reset_user_bank();
  uit.epoch = init.epoch;
  uit.initialized = true;
  return DIFFTEST_UIT_OK;
}

int32_t difftest_uit_exec(const void *input, uint32_t input_bytes, void *out, uint32_t out_bytes) {
  if (!input || !out || input_bytes != sizeof(DifftestUitExecRequest) ||
      out_bytes != sizeof(DifftestUitExecResult)) return DIFFTEST_UIT_E_ABI;
  int32_t rc = ready();
  if (rc) return rc;
  DifftestUitExecRequest request;
  memcpy(&request, input, sizeof(request));
  rc = identity(request.version, request.bytes, sizeof(request), request.hart,
                request.epoch, request.control_seq);
  if (rc) return rc;
  if (!request.transaction_uid || request.transaction_uid <= uit.last_uid) return DIFFTEST_UIT_E_ID;
  if (cpu.pc != request.diagnostic_pc) return DIFFTEST_UIT_E_PC;
  if (request.sample_kind > DIFFTEST_UIT_PENDING_SAMPLE ||
      (!request.sample_kind && request.sample_payload) ||
      (request.sample_kind == DIFFTEST_UIT_PENDING_SAMPLE && request.sample_payload > 1))
    return DIFFTEST_UIT_E_PAYLOAD;
  if (request.kind == DIFFTEST_UIT_CSR) {
    uint32_t funct3 = (request.instruction >> 12) & 7;
    if ((request.instruction & 0x7f) != 0x73 || funct3 == 0 || funct3 == 4)
      return DIFFTEST_UIT_E_INSTRUCTION;
    if (!uit_is_csr(request.csr) || request.csr != (request.instruction >> 20) ||
        request.funct3 != funct3) return DIFFTEST_UIT_E_CSR;
    if ((request.sample_kind == DIFFTEST_UIT_TIMER_SAMPLE && request.csr != CSR_UTIMER) ||
        (request.sample_kind == DIFFTEST_UIT_PENDING_SAMPLE && request.csr != CSR_UIP))
      return DIFFTEST_UIT_E_SAMPLE_UNEXPECTED;
  } else if (request.kind == DIFFTEST_UIT_URET) {
    if (request.instruction != UINT32_C(0x00200073)) return DIFFTEST_UIT_E_INSTRUCTION;
    if (request.csr != UINT16_MAX || request.funct3) return DIFFTEST_UIT_E_CSR;
    if (request.sample_kind) return DIFFTEST_UIT_E_SAMPLE_UNEXPECTED;
  } else return DIFFTEST_UIT_E_INSTRUCTION;

  uit.request = request;
  uit.result = (DifftestUitExecResult){
    .version = DIFFTEST_UIT_VERSION, .bytes = sizeof(uit.result), .hart = 0,
    .epoch = uit.epoch, .transaction_uid = request.transaction_uid,
    .control_seq = request.control_seq
  };
  uit.active = true;
  uit.fetched = false;
  cpu_exec(1);
  uit.active = false;
  memcpy(out, &uit.result, sizeof(uit.result));
  memset(&uit.request, 0, sizeof(uit.request));
  if (uit.error) return uit.error;
  if (nemu_state.state == NEMU_ABORT || nemu_state.state == NEMU_END) return DIFFTEST_UIT_E_EXECUTION;
  if (!uit.fetched && uit.result.outcome != DIFFTEST_UIT_ISA_EXCEPTION) return DIFFTEST_UIT_E_INSTRUCTION;
  uit.sequence = request.control_seq;
  uit.last_uid = request.transaction_uid;
  return DIFFTEST_UIT_OK;
}

int32_t difftest_uit_raise_event(const void *input, uint32_t input_bytes) {
#ifndef CONFIG_RV_DASICS
  return DIFFTEST_UIT_E_FEATURE;
#else
  if (!input || input_bytes != sizeof(DifftestUitHUEvent)) return DIFFTEST_UIT_E_ABI;
  int32_t rc = ready();
  if (rc) return rc;
  DifftestUitHUEvent event;
  memcpy(&event, input, sizeof(event));
  rc = identity(event.version, event.bytes, sizeof(event), event.hart, event.epoch, event.control_seq);
  if (rc) return rc;
  if (event.event_kind != DIFFTEST_UIT_HU_TIMER) return DIFFTEST_UIT_E_UNSUPPORTED;
  if (!event.event_uid || event.event_uid <= uit.last_event_uid) return DIFFTEST_UIT_E_ID;
  if (event.prior_instruction_count != uit.instruction_count) return DIFFTEST_UIT_E_ORDER;
  if (event.boundary_pc != cpu.pc) return DIFFTEST_UIT_E_PC;
  if (event.diagnostic_target != utvec->val) return DIFFTEST_UIT_E_PC;
  rc = uit_enter_hu();
  if (rc) return rc;
  uit.sequence = event.control_seq;
  uit.last_event_uid = event.event_uid;
  return DIFFTEST_UIT_OK;
#endif
}

int32_t difftest_uit_get_state(void *out, uint32_t out_bytes) {
  if (!out || out_bytes != sizeof(DifftestUitState)) return DIFFTEST_UIT_E_ABI;
  int32_t rc = ready();
  if (rc) return rc;
  DifftestUitState state = {
    .version = DIFFTEST_UIT_VERSION, .bytes = sizeof(state), .hart = 0,
    .flags = MUXDEF(CONFIG_RV_SDEXT, cpu.debug_mode, 0),
    .epoch = uit.epoch, .last_control_seq = uit.sequence,
    .ustatus = csr_array[CSR_USTATUS], .uie = csr_array[CSR_UIE], .utvec = csr_array[CSR_UTVEC],
    .uscratch = csr_array[CSR_USCRATCH], .uepc = csr_array[CSR_UEPC],
    .ucause = csr_array[CSR_UCAUSE], .utval = csr_array[CSR_UTVAL],
    .pc = cpu.pc, .mode = cpu.mode, .v = cpu.v,
    .in_handler = MUXDEF(CONFIG_RV_DASICS, cpu.uit_in_handler, 0)
  };
  memcpy(out, &state, sizeof(state));
  return DIFFTEST_UIT_OK;
}

void uit_check_mmio(uint64_t address, int len, bool is_write) {
  if (!uit.initialized) return;
  if (address != DIFFTEST_UIT_UART_TX || len != 1 || !is_write)
    protocol_abort(DIFFTEST_UIT_E_UNSUPPORTED);
}

void uit_record_tx(uint64_t pc, uint64_t address, uint64_t data, int len) {
  if (!uit.initialized) protocol_abort(DIFFTEST_UIT_E_STATE);
  uit_check_mmio(address, len, true);
  if (uit.tx_count == UIT_TX_CAPACITY) protocol_abort(DIFFTEST_UIT_E_OVERFLOW);
  uint32_t index = (uit.tx_head + uit.tx_count) % UIT_TX_CAPACITY;
  uit.tx[index] = (DifftestUitTx){
    .version = DIFFTEST_UIT_VERSION, .bytes = sizeof(DifftestUitTx), .hart = 0,
    .epoch = uit.epoch, .tx_seq = ++uit.tx_sequence, .pc = pc,
    .address = address, .data = data & 0xff, .len = len
  };
  uit.tx_count++;
}

int32_t difftest_uit_read_tx(void *out, uint32_t out_bytes) {
  if (!out || out_bytes != sizeof(DifftestUitTx)) return DIFFTEST_UIT_E_ABI;
  int32_t rc = ready();
  if (rc) return rc;
  if (!uit.tx_count) return DIFFTEST_UIT_EMPTY;
  memcpy(out, &uit.tx[uit.tx_head], sizeof(DifftestUitTx));
  uit.tx_head = (uit.tx_head + 1) % UIT_TX_CAPACITY;
  uit.tx_count--;
  return DIFFTEST_UIT_OK;
}

#else
int32_t difftest_uit_init(const void *input, uint32_t bytes) { return DIFFTEST_UIT_E_FEATURE; }
int32_t difftest_uit_exec(const void *input, uint32_t bytes, void *out, uint32_t out_bytes) {
  return DIFFTEST_UIT_E_FEATURE;
}
int32_t difftest_uit_raise_event(const void *input, uint32_t bytes) { return DIFFTEST_UIT_E_FEATURE; }
int32_t difftest_uit_get_state(void *out, uint32_t bytes) { return DIFFTEST_UIT_E_FEATURE; }
int32_t difftest_uit_read_tx(void *out, uint32_t bytes) { return DIFFTEST_UIT_E_FEATURE; }
#endif
