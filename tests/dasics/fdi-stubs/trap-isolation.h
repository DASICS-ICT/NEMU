#ifndef FDI_TEST_TRAP_ISOLATION_H
#define FDI_TEST_TRAP_ISOLATION_H
#ifndef FDI_BANK_TEST
#error "Trap isolation is restricted to the raw FDI bank invariant test"
#endif
#include <common.h>
#include <stdlib.h>

/* This fixture tests private bank storage and export invariants only. Prevent
 * the unrelated decoder/CSR graph from entering its minimal build. Exception
 * constants merely satisfy unused function bodies; real instruction tests use
 * the shared reference, and any trap reached here is an unexpected failure. */
#define __INTR_H__
enum { EX_II = 2, EX_DASICS_U = 24, EX_DASICS_S = 25 };
__attribute__((noreturn)) void longjmp_exception(int cause) {
  fprintf(stderr, "Unexpected trap in FDI bank invariant fixture: %d\n", cause);
  abort();
}
#endif
