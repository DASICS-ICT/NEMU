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

#include <isa.h>
#include <cpu/cpu.h>
#include <cpu/exec.h>
#include <difftest.h>
#include "../local-include/intr.h"
#include "../local-include/csr.h"
#include <generated/autoconf.h>
#include <stdlib.h>

void ramcmp() {
  printf("ram cmp called\n");
  uint64_t *ahead_ram = (uint64_t *)(0x1100000000ul);
  uint64_t *normal_ram = (uint64_t *)(0x100000000ul);
  for (int i = 0; i < CONFIG_MSIZE / 8; i++) {
    if (ahead_ram[i] != normal_ram[i]) {
      printf("Memory diff at 0x%x\n", i);
      exit(1);
    }
  }
}

// csr_prepare() & csr_writeback() are used to maintain
// a compact mirror of critical CSRs
// For processor difftest only
#ifdef CONFIG_RVH
#define MIDELEG_FORCED_MASK ((1 << 12) | (1 << 10) | (1 << 6) | (1 << 2))
#endif //CONFIG_RVH

void csr_prepare() {
  cpu.mstatus = mstatus->val;
  cpu.mcause  = mcause->val;
  cpu.mepc    = mepc->val;

  cpu.sstatus = mstatus->val & SSTATUS_RMASK; // sstatus
  cpu.scause  = scause->val;
  cpu.sepc    = sepc->val;

  cpu.satp     = satp->val;
  cpu.mip      = mip->val;
  cpu.mie      = mie->val;
  cpu.mscratch = mscratch->val;
  cpu.sscratch = sscratch->val;
  cpu.mideleg  = mideleg->val;
  cpu.medeleg  = medeleg->val;
  cpu.mtval    = mtval->val;
  cpu.stval    = stval->val;
  cpu.mtvec    = mtvec->val;
  cpu.stvec    = stvec->val;

#ifdef CONFIG_RVN
  cpu.ustatus  = csrid_read(0x000);  // ustatus
  cpu.ucause   = ucause->val;
  cpu.uepc     = uepc->val;
  cpu.uscratch = uscratch->val;
  cpu.sedeleg  = sedeleg->val;
  cpu.sideleg  = sideleg->val;
  cpu.utval    = utval->val;
  cpu.utvec    = utvec->val;
  cpu.utimer   = utimer->val;
#endif  // CONFIG_RVN

#ifdef CONFIG_RV_DASICS
  cpu.dsmcfg    = dsmcfg->val;
  cpu.dsmbound0 = dsmbound0->val;
  cpu.dsmbound1 = dsmbound1->val;
  // cpu.dumcfg    = csrid_read(0x9e0);   // dumcfg
  cpu.dumbound0 = dumbound0->val;
  cpu.dumbound1 = dumbound1->val;

  cpu.dlcfg0    = dlcfg0->val;
  cpu.dlbound0  = dlbound0->val;
  cpu.dlbound1  = dlbound1->val;
  cpu.dlbound2  = dlbound2->val;
  cpu.dlbound3  = dlbound3->val;
  cpu.dlbound4  = dlbound4->val;
  cpu.dlbound5  = dlbound5->val;
  cpu.dlbound6  = dlbound6->val;
  cpu.dlbound7  = dlbound7->val;
  cpu.dlbound8  = dlbound8->val;
  cpu.dlbound9  = dlbound9->val;
  cpu.dlbound10 = dlbound10->val;
  cpu.dlbound11 = dlbound11->val;
  cpu.dlbound12 = dlbound12->val;
  cpu.dlbound13 = dlbound13->val;
  cpu.dlbound14 = dlbound14->val;
  cpu.dlbound15 = dlbound15->val;
  cpu.dlbound16 = dlbound16->val;
  cpu.dlbound17 = dlbound17->val;
  cpu.dlbound18 = dlbound18->val;
  cpu.dlbound19 = dlbound19->val;
  cpu.dlbound20 = dlbound20->val;
  cpu.dlbound21 = dlbound21->val;
  cpu.dlbound22 = dlbound22->val;
  cpu.dlbound23 = dlbound23->val;
  cpu.dlbound24 = dlbound24->val;
  cpu.dlbound25 = dlbound25->val;
  cpu.dlbound26 = dlbound26->val;
  cpu.dlbound27 = dlbound27->val;
  cpu.dlbound28 = dlbound28->val;
  cpu.dlbound29 = dlbound29->val;
  cpu.dlbound30 = dlbound30->val;
  cpu.dlbound31 = dlbound31->val;

  cpu.djcfg     = djcfg->val;
  cpu.djbound0lo= djbound0lo->val;
  cpu.djbound0hi= djbound0hi->val;
  cpu.djbound1lo= djbound1lo->val;
  cpu.djbound1hi= djbound1hi->val;
  cpu.djbound2lo= djbound2lo->val;
  cpu.djbound2hi= djbound2hi->val;
  cpu.djbound3lo= djbound3lo->val;
  cpu.djbound3hi= djbound3hi->val;

  cpu.dmaincall = dmaincall->val;
  cpu.dretpc    = dretpc->val;
  cpu.dretpcfz  = dretpcfz->val;
#endif  // CONFIG_RV_DASICS

#ifdef CONFIG_RV_MPK
  cpu.upkru    = upkru->val;
  cpu.spkrs    = spkrs->val;
  cpu.spkctl   = spkctl->val;
#endif

#if defined (CONFIG_RV_DASICS) || defined (CONFIG_RV_MPK)
  cpu.dfreason  = dfreason->val;
#endif

#ifdef CONFIG_RVV
  cpu.vstart  = vstart->val;
  cpu.vxsat   = vxsat->val;
  cpu.vxrm    = vxrm->val;
  cpu.vcsr    = vcsr->val;
  cpu.vl      = vl->val;
  cpu.vtype   = vtype->val;
  cpu.vlenb   = vlenb->val;
#endif // CONFIG_RVV
#ifdef CONFIG_RVH
  cpu.mtval2  = mtval2->val;
  cpu.mtinst  = mtinst->val;
  cpu.hstatus = hstatus->val;
  cpu.hideleg = hideleg->val;
  cpu.hedeleg = hedeleg->val;
  cpu.hcounteren = hcounteren->val;
  cpu.htval   = htval->val;
  cpu.htinst  = htinst->val;
  cpu.hgatp   = hgatp->val;
  cpu.vsstatus= vsstatus->val;
  cpu.vstvec  = vstvec->val;
  cpu.vsepc   = vsepc->val;
  cpu.vscause = vscause->val;
  cpu.vstval  = vstval->val;
  cpu.vsatp   = vsatp->val;
  cpu.vsscratch = vsscratch->val;
#endif
}

void csr_writeback() {
  mstatus->val = cpu.mstatus;
  mcause ->val = cpu.mcause ;
  mepc   ->val = cpu.mepc   ;
  //sstatus->val = cpu.sstatus;  // sstatus is a shadow of mstatus
  scause ->val = cpu.scause ;
  sepc   ->val = cpu.sepc   ;
#ifdef CONFIG_RVN
  //ustatus->val = cpu.ustatus;  // ustatus is a shadow of mstatus
  ucause->val  = cpu.ucause;
  uepc->val    = cpu.uepc;
#endif  // CONFIG_RVN

  satp->val     = cpu.satp;
  mip->val      = cpu.mip;
  mie->val      = cpu.mie;
  mscratch->val = cpu.mscratch;
  sscratch->val = cpu.sscratch;
  mideleg->val  = cpu.mideleg;
  medeleg->val  = cpu.medeleg;
  mtval->val    = cpu.mtval;
  stval->val    = cpu.stval;
  mtvec->val    = cpu.mtvec;
  stvec->val    = cpu.stvec;

#ifdef CONFIG_RVN
  uscratch->val = cpu.uscratch;
  sideleg->val  = cpu.sideleg;
  sedeleg->val  = cpu.sedeleg;
  utval->val    = cpu.utval;
  utvec->val    = cpu.utvec;
  utimer->val   = cpu.utimer;
#endif  // CONFIG_RVN

#ifdef CONFIG_RV_DASICS
  dsmcfg->val    = cpu.dsmcfg;
  dsmbound0->val = cpu.dsmbound0;
  dsmbound1->val = cpu.dsmbound1;
  // dumcfg->val    = cpu.dumcfg; // dumcfg is a shadow of dsmcfg
  dumbound0->val = cpu.dumbound0;
  dumbound1->val = cpu.dumbound1;

  dlcfg0->val    = cpu.dlcfg0;
  dlbound0->val  = cpu.dlbound0;
  dlbound1->val  = cpu.dlbound1;
  dlbound2->val  = cpu.dlbound2;
  dlbound3->val  = cpu.dlbound3;
  dlbound4->val  = cpu.dlbound4;
  dlbound5->val  = cpu.dlbound5;
  dlbound6->val  = cpu.dlbound6;
  dlbound7->val  = cpu.dlbound7;
  dlbound8->val  = cpu.dlbound8;
  dlbound9->val  = cpu.dlbound9;
  dlbound10->val = cpu.dlbound10;
  dlbound11->val = cpu.dlbound11;
  dlbound12->val = cpu.dlbound12;
  dlbound13->val = cpu.dlbound13;
  dlbound14->val = cpu.dlbound14;
  dlbound15->val = cpu.dlbound15;
  dlbound16->val = cpu.dlbound16;
  dlbound17->val = cpu.dlbound17;
  dlbound18->val = cpu.dlbound18;
  dlbound19->val = cpu.dlbound19;
  dlbound20->val = cpu.dlbound20;
  dlbound21->val = cpu.dlbound21;
  dlbound22->val = cpu.dlbound22;
  dlbound23->val = cpu.dlbound23;
  dlbound24->val = cpu.dlbound24;
  dlbound25->val = cpu.dlbound25;
  dlbound26->val = cpu.dlbound26;
  dlbound27->val = cpu.dlbound27;
  dlbound28->val = cpu.dlbound28;
  dlbound29->val = cpu.dlbound29;
  dlbound30->val = cpu.dlbound30;
  dlbound31->val = cpu.dlbound31;

  djcfg->val     = cpu.djcfg;
  djbound0lo->val= cpu.djbound0lo;
  djbound0hi->val= cpu.djbound0hi;
  djbound1lo->val= cpu.djbound1lo;
  djbound1hi->val= cpu.djbound1hi;
  djbound2lo->val= cpu.djbound2lo;
  djbound2hi->val= cpu.djbound2hi;
  djbound3lo->val= cpu.djbound3lo;
  djbound3hi->val= cpu.djbound3hi;

  dmaincall->val = cpu.dmaincall;
  dretpc->val    = cpu.dretpc;
  dretpcfz->val  = cpu.dretpcfz;
#endif  // CONFIG_RV_DASICS

#ifdef CONFIG_RV_MPK
  upkru->val    = cpu.upkru;
  spkrs->val    = cpu.spkrs;
  spkctl->val   = cpu.spkctl;
#endif

#if defined (CONFIG_RV_DASICS) || defined (CONFIG_RV_MPK)
  dfreason->val = cpu.dfreason;
#endif

#ifdef CONFIG_RVV
  vstart->val  = cpu.vstart;
  vxsat->val   = cpu.vxsat;
  vxrm->val    = cpu.vxrm;
  vcsr->val    = cpu.vcsr;
  vl->val      = cpu.vl;
  vtype->val   = cpu.vtype;
  vlenb->val   = cpu.vlenb;
#endif //CONFIG_RVV
#ifdef CONFIG_RVH
  mtval2->val  = cpu.mtval2;
  mtinst->val  = cpu.mtinst;
  hstatus->val = cpu.hstatus;
  hideleg->val = cpu.hideleg;
  hedeleg->val = cpu.hedeleg;
  hcounteren->val = cpu.hcounteren;
  htval->val   = cpu.htval;
  htinst->val  = cpu.htinst;
  hgatp->val   = cpu.hgatp;
  vsstatus->val= cpu.vsstatus;
  vstvec->val  = cpu.vstvec;
  vsepc->val   = cpu.vsepc;
  vscause->val = cpu.vscause;
  vstval->val  = cpu.vstval;
  vsatp->val   = cpu.vsatp;
  vsscratch->val = cpu.vsscratch;
#endif
}
#ifdef CONFIG_LIGHTQS
extern uint64_t stable_log_begin, spec_log_begin;

extern struct lightqs_reg_ss reg_ss;
extern uint64_t g_nr_guest_instr;
void isa_difftest_regcpy(void *dut, bool direction, bool restore, uint64_t restore_count) {
  if (restore) {
    uint64_t left_exec = lightqs_restore_reg_snapshot(restore_count);
    #ifdef CONFIG_LIGHTQS_DEBUG
    printf("restore count %lu\n", restore_count);
    printf("left exec = %lx\n", left_exec);
    #endif // CONFIG_LIGHTQS_DEBUG
    pmem_record_restore(reg_ss.inst_cnt);
    // clint_restore_snapshot(restore_count);

    if (spec_log_begin <= restore_count) {
      // must have restored using spec snapshot
      stable_log_begin = spec_log_begin;
    }
    cpu_exec(left_exec);
  }
#else
void isa_difftest_regcpy(void *dut, bool direction) {
#endif // CONFIG_LIGHTQS
  //ramcmp();
  if (direction == DIFFTEST_TO_REF) {
    memcpy(&cpu, dut, DIFFTEST_REG_SIZE);
    csr_writeback();
    // need to clear the cached mmu states as well
    extern void update_mmu_state();
    update_mmu_state();
  } else {
    csr_prepare();
    memcpy(dut, &cpu, DIFFTEST_REG_SIZE);
  }
#ifdef CONFIG_LIGHTQS
  // after processing, take another snapshot
  // FIXME: update spec_log_begin
  if (restore) {
    ++g_nr_guest_instr; // must sync with RTL
    lightqs_take_reg_snapshot();
    // clint_take_snapshot();
    // pmem ops are logged automatically
    stable_log_begin = restore_count + 1;
    spec_log_begin = restore_count + AHEAD_LENGTH + 1;
    cpu_exec(AHEAD_LENGTH);
    lightqs_take_spec_reg_snapshot();
    // clint_take_spec_snapshot();
  }
#endif // CO
}

void isa_difftest_csrcpy(void *dut, bool direction) {
  if (direction == DIFFTEST_TO_REF) {
    memcpy(csr_array, dut, 4096 * sizeof(rtlreg_t));
  } else {
    memcpy(dut, csr_array, 4096 * sizeof(rtlreg_t));
  }
}
#ifdef CONFIG_LIGHTQS
void isa_difftest_uarchstatus_cpy(void *dut, bool direction, uint64_t restore_count) {
  uint64_t left_exec = lightqs_restore_reg_snapshot(restore_count);
  pmem_record_restore(reg_ss.inst_cnt);
  // clint_restore_snapshot(restore_count);

  if (spec_log_begin <= restore_count) {
    // must have restored using spec snapshot
    stable_log_begin = spec_log_begin;
  }
  cpu_exec(left_exec);
#else
void isa_difftest_uarchstatus_cpy(void *dut, bool direction) {
#endif // CONFIG_LIGHTQS
  //ramcmp();

  if (direction == DIFFTEST_TO_REF) {
    struct SyncState* ms = (struct SyncState*)dut;
#if CONFIG_DIFFTEST_REF_FOR_GEM5
    cpu.lr_valid = ms->lrscValid;
#else
    if (ms->lrscValid) { // this is actually sc_failed
      cpu.lr_valid = 0;
    }
#endif
  } else {
    struct SyncState ms;
    ms.lrscValid = cpu.lr_valid;
    ms.lrscAddr = cpu.lr_addr;
    memcpy(dut, &ms, sizeof(struct SyncState));
  }

#ifdef CONFIG_LIGHTQS
  // after processing, take another snapshot
  lightqs_take_reg_snapshot();
  // clint_take_snapshot();
  // pmem ops are logged automatically
  stable_log_begin = restore_count;
  spec_log_begin = restore_count + AHEAD_LENGTH;
  cpu_exec(AHEAD_LENGTH);

  lightqs_take_spec_reg_snapshot();
  // clint_take_spec_snapshot();
#endif // CONFIG_LIGHTQS
}
#ifdef CONFIG_LIGHTQS
void isa_difftest_raise_intr(word_t NO, uint64_t restore_count) {

  uint64_t left_exec = lightqs_restore_reg_snapshot(restore_count);
  pmem_record_restore(reg_ss.inst_cnt);
  // clint_restore_snapshot(restore_count);

  if (spec_log_begin <= restore_count) {
    // must have restored using spec snapshot
    stable_log_begin = spec_log_begin;
  }
  cpu_exec(left_exec);
#else
void isa_difftest_raise_intr(word_t NO) {
#endif // CONFIG_LIGHTQS
  //ramcmp();
  cpu.pc = raise_intr(NO, cpu.pc);

#ifdef CONFIG_LIGHTQS
  // after processing, take another snapshot
  // FIXME: update spec_log_begin
  lightqs_take_reg_snapshot();
  // clint_take_snapshot();
  // pmem ops are logged automatically
  stable_log_begin = restore_count;
  spec_log_begin = restore_count + AHEAD_LENGTH;
  cpu_exec(AHEAD_LENGTH);

  lightqs_take_spec_reg_snapshot();
  // clint_take_spec_snapshot();
#endif // CONFIG_LIGHTQS
}

#ifdef CONFIG_GUIDED_EXEC

#ifdef CONFIG_LIGHTQS
void isa_difftest_guided_exec(void * guide, uint64_t restore_count) {

  uint64_t left_exec = lightqs_restore_reg_snapshot(restore_count);
  pmem_record_restore(reg_ss.inst_cnt);
  // clint_restore_snapshot(restore_count);

  if (spec_log_begin <= restore_count) {
    // must have restored using spec snapshot
    stable_log_begin = spec_log_begin;
  }
  cpu_exec(left_exec);
#else
void isa_difftest_guided_exec(void * guide) {
#endif // CONFIG_LIGHTQS
  memcpy(&cpu.execution_guide, guide, sizeof(struct ExecutionGuide));

  cpu.guided_exec = true;
  cpu_exec(1);
  cpu.guided_exec = false;

  // guided exec may affect ram content, in this case, normal so have finished guided exec
  //ramcmp();

#ifdef CONFIG_LIGHTQS
  // after processing, take another snapshot
  // FIXME: update spec_log_begin
  lightqs_take_reg_snapshot();
  // clint_take_snapshot();
  // pmem ops are logged automatically
  stable_log_begin = restore_count + 1;
  spec_log_begin = restore_count + 1 + AHEAD_LENGTH;
  cpu_exec(AHEAD_LENGTH);
  lightqs_take_spec_reg_snapshot();
  // clint_take_spec_snapshot();
#endif // CONFIG_LIGHTQS
}
#endif

#ifdef CONFIG_BR_LOG
extern struct br_info br_log[];
void * isa_difftest_query_br_log() {
  return (void *)br_log;
}
#endif // CONFIG_BR_LOG

#ifdef CONFIG_QUERY_REF
void isa_difftest_query_ref(void *result_buffer, uint64_t type) {
  size_t size;
  switch(type) {
    case REF_QUERY_MEM_EVENT:
      cpu.query_mem_event.pc = cpu.debug.current_pc; // update pc
      size = sizeof(cpu.query_mem_event);
      memcpy(result_buffer, &cpu.query_mem_event, size);
      // nemu result buffer will be flushed after query
      // printf_with_pid("mem_access %x\n", cpu.query_mem_event.mem_access);
      // printf_with_pid("mem_access_is_load %x\n", cpu.query_mem_event.mem_access_is_load);
      // printf_with_pid("mem_access_vaddr %lx\n", cpu.query_mem_event.mem_access_vaddr);
      memset(&cpu.query_mem_event, 0, size);
      break;
    default:
      panic("Invalid ref query type");
  }
}
#endif

char *reg_dump_file = NULL;

void dump_regs() {
  if (reg_dump_file == NULL) {
    printf("No register dump file is specified, register dump skipped.\n");
    return ;
  }
  FILE *fp = fopen(reg_dump_file, "w");
  if (fp == NULL) {
    printf("Cannot open file %s, register dump skipped.\n", reg_dump_file);
    return ;
  }
  fprintf(fp, "mstatus %lx\n", cpu.mstatus);
  fprintf(fp, "mcause %lx\n", cpu.mcause);
  fprintf(fp, "mepc %lx\n", cpu.mepc);
  fprintf(fp, "sstatus %lx\n", cpu.sstatus);
  fprintf(fp, "scause %lx\n", cpu.scause);
  fprintf(fp, "sepc %lx\n", cpu.sepc);
  fprintf(fp, "satp %lx\n", cpu.satp);
  fprintf(fp, "mip %lx\n", cpu.mip);
  fprintf(fp, "mie %lx\n", cpu.mie);
  fprintf(fp, "mscratch %lx\n", cpu.mscratch);
  fprintf(fp, "sscratch %lx\n", cpu.sscratch);
  fprintf(fp, "mideleg %lx\n", cpu.mideleg);
  fprintf(fp, "medeleg %lx\n", cpu.medeleg);
  fprintf(fp, "mtval %lx\n", cpu.mtval);
  fprintf(fp, "stval %lx\n", cpu.stval);
  fprintf(fp, "mtvec %lx\n", cpu.mtvec);
  fprintf(fp, "stvec %lx\n", cpu.stvec);
#ifdef CONFIG_RVV
  fprintf(fp, "vtype %lx\n", vtype->val);
  fprintf(fp, "vstart %lx\n", vstart->val);
  fprintf(fp, "vxsat %lx\n", vxsat->val);
  fprintf(fp, "vxrm %lx\n", vxrm->val);
  fprintf(fp, "vl %lx\n", vl->val);
#endif // CONFIG_RVV
  for (int i = 0; i < 32; i++) {
    fprintf(fp, "gpr %d %lx\n", i, cpu.gpr[i]._64);
  }
#ifndef CONFIG_FPU_NONE
  for (int i = 0; i < 32; i++) {
    fprintf(fp, "fpr %d %lx\n", i, cpu.fpr[i]._64);
  }
#endif // CONFIG_FPU_NONE
}

#ifdef CONFIG_MULTICORE_DIFF
void isa_difftest_set_mhartid(int n) {
  mhartid->val = n;
}
#endif
