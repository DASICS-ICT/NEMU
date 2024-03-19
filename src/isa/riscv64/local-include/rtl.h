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

#ifndef __RISCV64_RTL_H__
#define __RISCV64_RTL_H__

#include <rtl/rtl.h>
#include "reg.h"
#include "csr.h"
#include <cpu/cpu.h>
#include "intr.h"

#define FBOX_MASK 0xFFFFFFFF00000000ull
// The bit pattern for a default generated 32-bit floating-point NaN
#define defaultNaNF32UI 0x7FC00000

static inline def_rtl(fbox, rtlreg_t *dest, rtlreg_t *src) {
  rtl_ori(s, dest, src, FBOX_MASK);
}

static inline def_rtl(funbox, rtlreg_t *dest, rtlreg_t *src) {
  if((*src & FBOX_MASK) == FBOX_MASK){
      rtl_andi(s, dest, src, ~FBOX_MASK);
  } else {
      *dest = defaultNaNF32UI;
  }
}

static inline def_rtl(fsr, rtlreg_t *fdest, rtlreg_t *src, int width) {
  if (width == FPCALL_W32) rtl_fbox(s, fdest, src);
  else if (width == FPCALL_W64) rtl_mv(s, fdest, src);
  else assert(0);
  void fp_set_dirty();
  fp_set_dirty();
}

#ifdef CONFIG_RVV

static inline def_rtl(lr, rtlreg_t* dest, int r, int width) {
  rtl_mv(s, dest, &reg_l(r));
}

static inline def_rtl(sr, int r, const rtlreg_t *src1, int width) {
  if (r != 0) { rtl_mv(s, &reg_l(r), src1); }
}

#endif // CONFIG_RVV

#ifdef CONFIG_RV_DASICS

static inline def_rtl(dasics_jcheck, vaddr_t target) {
  //dasics_redirect_helper(s->pc, target, s->snpc);
}

static inline def_rtl(set_dretpc, vaddr_t value) {
  uint8_t level, cur_level;
  if (dasics_in_trusted_zone(s->pc)) { level = 0; }
  else {
    cur_level = dasics_get_level(s->pc);
    if (dasics_level_overflow(cur_level)) {
      Logti("Dasics level overflow");
      longjmp_exception(EX_II);
      return;
    }
    level = cur_level + 1;
  }
  csr_array[CSR_DRETPC0 + level] = value;
}

static inline def_rtl(dasics_bndmv, const rtlreg_t *src, const rtlreg_t *dest, word_t type) {
  if (type != DIMV_MEM && type != DIMV_JMP) {
    Logti("DasicsBndMv: Unknown type: 0x%lx", type);
    longjmp_exception(EX_II);
    return;
  } else {
    switch (type) {
      case DIMV_MEM:
        if (*src >= MAX_DASICS_LIBBOUNDS || *dest >= MAX_DASICS_LIBBOUNDS) {
          Logti("DasicsBndMv: mem bound index overflow: src 0x%lx dest 0x%lx", *src, *dest);
          longjmp_exception(EX_II);
          return;
        }
        break;
      case DIMV_JMP:
        if ((*src > MAX_DASICS_JUMPBOUNDS && *src != DIMV_SCRATCH_INDEX)
            || (*dest >= MAX_DASICS_JUMPBOUNDS && *dest != DIMV_SCRATCH_INDEX)) {
          Logti("DasicsBndMv: jump bound index overflow: src 0x%lx dest 0x%lx", *src, *dest);
          longjmp_exception(EX_II);
          return;
        }
        break;
      default:
        break;
    }
  }
  if (!dasics_in_trusted_zone(s->pc)) {
    uint8_t level = dasics_get_level(s->pc);
    if (dasics_level_overflow(level)) {
      Logti("Dasics level overflow");
      longjmp_exception(EX_II);
      return;
    }
    uint8_t src_level, dest_level;
    bool dest_empty;
    switch(type) {
      case DIMV_MEM:
        src_level = dasics_liblevel_from_index(*src);
        dest_empty = (dasics_libcfg_from_index(*dest) & LIBCFG_V) == 0;
        dest_level = dasics_liblevel_from_index(*dest);
        if (level > src_level || (!dest_empty && level >= dest_level)) {
          Logti("Illegal DIBndMv");
          longjmp_exception(EX_II);
          return;
        }
        break;
      case DIMV_JMP:
        src_level = (*src == DIMV_SCRATCH_INDEX) ? dasics_scratchlevel() : dasics_jumplevel_from_index(*src);
        // always allow copying to scratchpad
        dest_empty = (*dest == DIMV_SCRATCH_INDEX) || (dasics_jumpcfg_from_index(*dest) & LIBCFG_V) == 0;
        dest_level = (*dest == DIMV_SCRATCH_INDEX) ? 0 : dasics_jumplevel_from_index(*dest);
        if (level > src_level || (!dest_empty && level >= dest_level)) {
          Logti("Illegal DIBndMv");
          return;
        }
        break;
      default:
        break;
    }
  }
  word_t src_cfg;
  uint8_t next_level = (dasics_in_trusted_zone(s->pc)) ? 0 : dasics_get_level(s->pc) + 1;
  word_t src_boundlo, src_boundhi;
  switch (type) {
    case DIMV_MEM:
      src_cfg = dasics_libcfg_from_index(*src);
      csr_array[CSR_DLCFG0] &= ~(LIBCFG_MASK << (*dest << 2));
      csr_array[CSR_DLCFG0] |= src_cfg << (*dest << 2);
      csr_array[CSR_DLBOUND0 + 2*(*dest)] = dasics_libbound_from_index(2*(*src));
      csr_array[CSR_DLBOUND0 + 2*(*dest) + 1] = dasics_libbound_from_index(2*(*src) + 1);
      csr_array[CSR_DLLEVEL] &= ~(DASICSLEVEL_MASK << (*dest << 1));
      csr_array[CSR_DLLEVEL] |= next_level << (*dest << 1);
      break;
    case DIMV_JMP:
      if (*src == DIMV_SCRATCH_INDEX) {
        src_cfg = dasics_scratchcfg();
        src_boundlo = csr_array[CSR_DSCRATCHBOUNDLO];
        src_boundhi = csr_array[CSR_DSCRATCHBOUNDLO + 1];
      } else {
        src_cfg = dasics_jumpcfg_from_index(*src);
        src_boundlo = dasics_jumpbound_low_from_index(*src);
        src_boundhi = dasics_jumpbound_high_from_index(*src);
      }
      if (*dest == DIMV_SCRATCH_INDEX) {
        csr_array[CSR_DSCRATCHCFG] = src_cfg;
        csr_array[CSR_DSCRATCHBOUNDLO] = src_boundlo;
        csr_array[CSR_DSCRATCHBOUNDLO + 1] = src_boundhi;
        csr_array[CSR_DSCRATCHLEVEL] = next_level;
      } else {
        csr_array[CSR_DJCFG] &= ~(JUMPCFG_MASK << (*dest << 4));
        csr_array[CSR_DJCFG] |= src_cfg << (*dest << 4);
        csr_array[CSR_DJBOUND0 + 2*(*dest)] = src_boundlo;
        csr_array[CSR_DJBOUND0 + 2*(*dest) + 1] = src_boundhi;
        csr_array[CSR_DJLEVEL] &= ~(DASICSLEVEL_MASK << (*dest << 1));
        csr_array[CSR_DJLEVEL] |= next_level << (*dest << 1);
      }
      break;
    default:
      break;
  }
}

static inline def_rtl(dasics_bndquery, rtlreg_t *dest, word_t type) {
  enum {DBQ_DENY, DBQ_RO, DBQ_RW, DBQ_EMPTY};
  uint8_t dasics_level = dasics_get_level(s->pc);
  word_t result = 0;
  switch (type) {
    case DIMV_MEM:
      for (int i = 0; i < MAX_DASICS_LIBBOUNDS; ++i) {
        uint8_t level = dasics_liblevel_from_index(i);
        uint8_t cfgval = dasics_libcfg_from_index(i);
        uint8_t res;
        if (!(cfgval & LIBCFG_V)) { res = DBQ_EMPTY; }
        else {
          if (level < dasics_level) { res = DBQ_DENY; }
          else if (level == dasics_level) { res = DBQ_RO; }
          else { res = DBQ_RW; }
        }
        result |= res << (i << 1);
      }
      break;
    case DIMV_JMP:
      for (int i = 0; i < MAX_DASICS_JUMPBOUNDS; ++i) {
        uint8_t level = dasics_jumplevel_from_index(i);
        uint16_t cfgval = dasics_jumpcfg_from_index(i);
        uint8_t res;
        if (!(cfgval & JUMPCFG_V)) { res = DBQ_EMPTY; }
        else {
          if (level < dasics_level) { res = DBQ_DENY; }
          else if (level == dasics_level) { res = DBQ_RO; }
          else { res = DBQ_RW; }
        }
        result |= res << (i << 1);
      }
      break;
    default:
      Logti("DasicsBndMv: Unknown type: 0x%lx", type);
      longjmp_exception(EX_II);
      return;
  }
  *dest = result;
}

#endif // CONFIG_RV_DASICS

#endif
