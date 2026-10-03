#ifndef RISCV_DASICS_H
#define RISCV_DASICS_H

#include <common.h>

#define CSR_FDI_SMAINCFG 0xbc4
#define CSR_FDI_UMAINCFG 0x9e1
#define CSR_FDI_SMAINBOUNDLO 0xbc5
#define CSR_FDI_SMAINBOUNDHI 0xbc6
#define CSR_FDI_UMAINBOUNDLO 0x9e2
#define CSR_FDI_UMAINBOUNDHI 0x9e3
#define CSR_FDI_LIBCFG 0x880
#define CSR_FDI_LIBBOUNDLO0 0x890
#define CSR_FDI_LIBBOUNDHI0 0x891
#define CSR_FDI_LIBBOUNDLO1 0x892
#define CSR_FDI_LIBBOUNDHI1 0x893
#define CSR_FDI_LIBBOUNDLO2 0x894
#define CSR_FDI_LIBBOUNDHI2 0x895
#define CSR_FDI_LIBBOUNDLO3 0x896
#define CSR_FDI_LIBBOUNDHI3 0x897
#define CSR_FDI_LIBBOUNDLO4 0x898
#define CSR_FDI_LIBBOUNDHI4 0x899
#define CSR_FDI_LIBBOUNDLO5 0x89a
#define CSR_FDI_LIBBOUNDHI5 0x89b
#define CSR_FDI_LIBBOUNDLO6 0x89c
#define CSR_FDI_LIBBOUNDHI6 0x89d
#define CSR_FDI_LIBBOUNDLO7 0x89e
#define CSR_FDI_LIBBOUNDHI7 0x89f
#define CSR_FDI_LIBBOUNDLO8 0x8a0
#define CSR_FDI_LIBBOUNDHI8 0x8a1
#define CSR_FDI_LIBBOUNDLO9 0x8a2
#define CSR_FDI_LIBBOUNDHI9 0x8a3
#define CSR_FDI_LIBBOUNDLO10 0x8a4
#define CSR_FDI_LIBBOUNDHI10 0x8a5
#define CSR_FDI_LIBBOUNDLO11 0x8a6
#define CSR_FDI_LIBBOUNDHI11 0x8a7
#define CSR_FDI_LIBBOUNDLO12 0x8a8
#define CSR_FDI_LIBBOUNDHI12 0x8a9
#define CSR_FDI_LIBBOUNDLO13 0x8aa
#define CSR_FDI_LIBBOUNDHI13 0x8ab
#define CSR_FDI_LIBBOUNDLO14 0x8ac
#define CSR_FDI_LIBBOUNDHI14 0x8ad
#define CSR_FDI_LIBBOUNDLO15 0x8ae
#define CSR_FDI_LIBBOUNDHI15 0x8af
#define CSR_FDI_MAINCALLENTRY 0x8b0
#define CSR_FDI_RETURNPC 0x8b1
#define CSR_FDI_ACTIVEZONERETURNPC 0x8b2
#define CSR_FDI_FREASON 0x8b3
#define CSR_FDI_JUMPCFG 0x8c8
#define CSR_FDI_JUMPBOUNDLO0 0x8c0
#define CSR_FDI_JUMPBOUNDHI0 0x8c1
#define CSR_FDI_JUMPBOUNDLO1 0x8c2
#define CSR_FDI_JUMPBOUNDHI1 0x8c3
#define CSR_FDI_JUMPBOUNDLO2 0x8c4
#define CSR_FDI_JUMPBOUNDHI2 0x8c5
#define CSR_FDI_JUMPBOUNDLO3 0x8c6
#define CSR_FDI_JUMPBOUNDHI3 0x8c7

#define DASICS_SMAINCFG_MASK UINT64_C(0x7ff)
#define DASICS_UMAINCFG_MASK UINT64_C(0x7c2)
#define DASICS_BOUND_MASK UINT64_C(0xfffffffffffffff8)
#define DASICS_LIBCFG_MASK UINT64_C(0xbbbbbbbbbbbbbbbb)
#define DASICS_JUMPCFG_MASK UINT64_C(0x0001000100010001)
#define DASICS_PC_MASK UINT64_C(0xffffffffffffffff)
#define DASICS_FREASON_MASK UINT64_C(0x7)

#ifdef CONFIG_RV_DASICS
void dasics_reset(void);
bool dasics_export_state(uint64_t words[52]);
void fdi_check_reset(void);
void fdi_note_reset(void);
void fdi_note_execution(void);
void fdi_check_import(void);
bool dasics_is_csr(uint32_t address);
word_t dasics_csr_read(uint32_t address);
void dasics_csr_write(uint32_t address, word_t value);
bool dasics_csr_source_permitted(vaddr_t source_pc);
#endif

#endif
