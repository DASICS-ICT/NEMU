#ifndef RISCV_USER_TIMER_H
#define RISCV_USER_TIMER_H

#include <common.h>
#include <difftest-user-timer.h>

bool uit_is_csr(uint32_t address);
void uit_reset(void);
void uit_note_execution(void);
void uit_note_retirement(void);
void uit_validate_fetched(uint64_t pc, uint32_t instruction);
void uit_note_exception(uint32_t cause);
void uit_validate_csr_access(uint32_t address, bool reads);
uint64_t uit_read_sample(uint32_t address);
void uit_note_csr_write(uint64_t value);
void uit_check_import(void);
void uit_check_mmio(uint64_t address, int len, bool is_write);
void uit_record_tx(uint64_t pc, uint64_t address, uint64_t data, int len);
bool uit_csr_permitted(void);
uint64_t uit_return(void);
int32_t uit_enter_hu(void);

#endif
