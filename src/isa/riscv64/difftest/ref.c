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
#include <difftest.h>
#include "../local-include/intr.h"
#include "../local-include/csr.h"

// csr_prepare() & csr_writeback() are used to maintain 
// a compact mirror of critical CSRs
// For processor difftest only 
static void csr_prepare() {
  cpu.mstatus = mstatus->val;
  cpu.mcause  = mcause->val;
  cpu.mepc    = mepc->val;

  cpu.sstatus = csrid_read(0x100); // sstatus
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
  // cpu.utimer   = utimer->val;
#endif  // CONFIG_RVN

#ifdef CONFIG_RV_DASICS
  cpu.dsmbound = dsmbound->val;
  cpu.dumbound = dumbound->val;

  cpu.dmbound0  = dmbound0->val;
  cpu.dmbound1  = dmbound1->val;
  cpu.dmbound2  = dmbound2->val;
  cpu.dmbound3  = dmbound3->val;
  cpu.dmbound4  = dmbound4->val;
  cpu.dmbound5  = dmbound5->val;
  cpu.dmbound6  = dmbound6->val;
  cpu.dmbound7  = dmbound7->val;
  cpu.dmbound8  = dmbound8->val;
  cpu.dmbound9  = dmbound9->val;
  cpu.dmbound10 = dmbound10->val;
  cpu.dmbound11 = dmbound11->val;
  cpu.dmbound12 = dmbound12->val;
  cpu.dmbound13 = dmbound13->val;
  cpu.dmbound14 = dmbound14->val;
  cpu.dmbound15 = dmbound15->val;
  cpu.dmbound16 = dmbound16->val;
  cpu.dmbound17 = dmbound17->val;
  cpu.dmbound18 = dmbound18->val;
  cpu.dmbound19 = dmbound19->val;
  cpu.dmbound20 = dmbound20->val;
  cpu.dmbound21 = dmbound21->val;
  cpu.dmbound22 = dmbound22->val;
  cpu.dmbound23 = dmbound23->val;
  cpu.dmbound24 = dmbound24->val;
  cpu.dmbound25 = dmbound25->val;
  cpu.dmbound26 = dmbound26->val;
  cpu.dmbound27 = dmbound27->val;
  cpu.dmbound28 = dmbound28->val;
  cpu.dmbound29 = dmbound29->val;
  cpu.dmbound30 = dmbound30->val;
  cpu.dmbound31 = dmbound31->val;

  cpu.djbound0= djbound0->val;
  cpu.djbound1= djbound1->val;
  cpu.djbound2= djbound2->val;
  cpu.djbound3= djbound3->val;
  cpu.djbound4= djbound4->val;
  cpu.djbound5= djbound5->val;
  cpu.djbound6= djbound6->val;
  cpu.djbound7= djbound7->val;

  cpu.dmaincall = dmaincall->val;
  cpu.dretpc    = dretpc->val;
  cpu.dretpcfz  = dretpcfz->val;
  cpu.dfreason  = dfreason->val;
#endif  // CONFIG_RV_DASICS

#ifdef CONFIG_RV_DASICS
  cpu.upkru    = upkru->val;
  cpu.spkrs    = spkrs->val;
  cpu.spkctl   = spkctl->val;
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
}

static void csr_writeback() {
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
  // utimer->val   = cpu.utimer;
#endif  // CONFIG_RVN

#ifdef CONFIG_RV_DASICS

  dsmbound->val = cpu.dsmbound;
  dumbound->val = cpu.dumbound;

  dmbound0->val  = cpu.dmbound0;
  dmbound1->val  = cpu.dmbound1;
  dmbound2->val  = cpu.dmbound2;
  dmbound3->val  = cpu.dmbound3;
  dmbound4->val  = cpu.dmbound4;
  dmbound5->val  = cpu.dmbound5;
  dmbound6->val  = cpu.dmbound6;
  dmbound7->val  = cpu.dmbound7;
  dmbound8->val  = cpu.dmbound8;
  dmbound9->val  = cpu.dmbound9;
  dmbound10->val = cpu.dmbound10;
  dmbound11->val = cpu.dmbound11;
  dmbound12->val = cpu.dmbound12;
  dmbound13->val = cpu.dmbound13;
  dmbound14->val = cpu.dmbound14;
  dmbound15->val = cpu.dmbound15;
  dmbound16->val = cpu.dmbound16;
  dmbound17->val = cpu.dmbound17;
  dmbound18->val = cpu.dmbound18;
  dmbound19->val = cpu.dmbound19;
  dmbound20->val = cpu.dmbound20;
  dmbound21->val = cpu.dmbound21;
  dmbound22->val = cpu.dmbound22;
  dmbound23->val = cpu.dmbound23;
  dmbound24->val = cpu.dmbound24;
  dmbound25->val = cpu.dmbound25;
  dmbound26->val = cpu.dmbound26;
  dmbound27->val = cpu.dmbound27;
  dmbound28->val = cpu.dmbound28;
  dmbound29->val = cpu.dmbound29;
  dmbound30->val = cpu.dmbound30;
  dmbound31->val = cpu.dmbound31;

  djbound0->val= cpu.djbound0;
  djbound1->val= cpu.djbound1;
  djbound2->val= cpu.djbound2;
  djbound3->val= cpu.djbound3;
  djbound4->val= cpu.djbound4;
  djbound5->val= cpu.djbound5;
  djbound6->val= cpu.djbound6;
  djbound7->val= cpu.djbound7;

  dmaincall->val = cpu.dmaincall;
  dretpc->val    = cpu.dretpc;
  dretpcfz->val  = cpu.dretpcfz;
  dfreason->val  = cpu.dfreason;
#endif  // CONFIG_RV_DASICS

#ifdef CONFIG_RV_DASICS
  upkru->val    = cpu.upkru;
  spkrs->val    = cpu.spkrs;
  spkctl->val   = cpu.spkctl;
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
}

void isa_difftest_regcpy(void *dut, bool direction) {
  if (direction == DIFFTEST_TO_REF) {
    memcpy(&cpu, dut, DIFFTEST_REG_SIZE);
    csr_writeback();
  } else {
    csr_prepare();
    memcpy(dut, &cpu, DIFFTEST_REG_SIZE);
  }
}

void isa_difftest_csrcpy(void *dut, bool direction) {
  if (direction == DIFFTEST_TO_REF) {
    memcpy(csr_array, dut, 4096 * sizeof(rtlreg_t));
  } else {
    memcpy(dut, csr_array, 4096 * sizeof(rtlreg_t));
  }
}

void isa_difftest_uarchstatus_cpy(void *dut, bool direction) {
  if (direction == DIFFTEST_TO_REF) {
    struct SyncState* ms = (struct SyncState*)dut;
    cpu.lr_valid = ms->lrscValid;
  } else {
    struct SyncState ms;
    ms.lrscValid = cpu.lr_valid;
    ms.lrscAddr = cpu.lr_addr;
    memcpy(dut, &ms, sizeof(struct SyncState));
  }
}

void isa_difftest_raise_intr(word_t NO) {
  cpu.pc = raise_intr(NO, cpu.pc);
}

#ifdef CONFIG_GUIDED_EXEC
void isa_difftest_guided_exec(void * guide) {
  memcpy(&cpu.execution_guide, guide, sizeof(struct ExecutionGuide));

  cpu.guided_exec = true;
  cpu_exec(1);
  cpu.guided_exec = false;
}
#endif

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

#ifdef CONFIG_MULTICORE_DIFF
void isa_difftest_set_mhartid(int n) {
  mhartid->val = n;
}
#endif
