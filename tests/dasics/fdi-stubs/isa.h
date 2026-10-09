#ifndef FDI_TEST_ISA_H
#define FDI_TEST_ISA_H
#include <common.h>
extern struct FdiTestCpu {
  uint64_t pc;
  unsigned mode;
  bool v;
  struct { word_t tval, tval2, tinst; } trapInfo;
} cpu;
#endif
