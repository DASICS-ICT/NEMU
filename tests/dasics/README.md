# DASICS Semantic Regression

This directory builds a small bare-metal image and executes every case in an
isolated process through the public NEMU difftest API. It accepts only a shared
object built with the exact `riscv64-nhv5-dasics-ref_defconfig` ABI. The build
tree `.config` must be adjacent to `build/`, and the caller must supply the
trusted shared-object SHA-256. Per-case process isolation prevents reference
initialization state from leaking between cases,
and each case explicitly clears all LibBound, JumpCfg, and special-target state
that it may consume. Build artifacts are written below `/tmp` by default.

The supported invocation in a LinkNan workspace is the top-level task:

```bash
xmake nemu-dasics-semantics-test --jobs=48
```

The local Makefile is an implementation detail used by that task. The top-level
entry builds and identifies the exact reference shared object, supplies its
SHA-256, and keeps the test artifacts and log under
`build/software/nemu-dasics-semantics/`.

The default semantic gate covers only cases with a unique architectural oracle:

- taken branch and jump admission for `MainCallEntry`, `ReturnPC`, and
  `ActiveZoneReturnPC`;
- taken BEQ, BNE, BLT, BGE, BLTU, and BGEU rejection outside the target allow
  set;
- taken branch, JAL, and JALR admission through valid JumpBound slot 0 and
  all four JumpBound slots, including 16-bit `JumpCfg` slot selection;
- JumpBound `[lo, hi)` high-end rejection, invalid config rejection, and empty
  or reversed bound rejection;
- JALR admission through `MainCallEntry` and rejection outside the complete
  target allow set;
- compressed jump, JR, JALR, BEQZ, and BNEZ target checks, including rejected
  JALR link preservation and a not-taken branch witness;
- no DASICS target check for a not-taken branch;
- rejection of taken branches and jumps outside the allow set when `JumpCfg`
  and all three special targets are zero;
- successful 8-byte load and store witnesses whose complete ranges fit one
  permitted LibBound, including loaded and stored value checks;
- independent allow and deny witnesses for every RV64 integer scalar load and
  store width, including signed extension, unchanged denied-load destinations,
  and complete denied-store data preservation;
- U-mode trusted, disabled, and per-operation closed bypass behavior for load,
  store, and jump checks, including the resulting data or target side effect;
- LibBound read/write permission separation, required valid bits, slot 15
  selection, and empty or reversed bound rejection;
- rejection of aligned 8-byte load and store witnesses outside the configured
  LibBound, including original `vaddr` in `mtval` and no store update;
- ordinary load/store address-misaligned traps for 8-byte accesses that remain
  fully contained in one permitted LibBound, including zero `FReason`, original
  `vaddr` in `mtval`, and absence of a partial store update; and
- low-three-bit WARL clearing for every S/U MainBound, LibBound, and JumpBound
  CSR; and
- U-mode and S-mode ecall behavior for disabled, trusted, untrusted-open, and
  untrusted-closed configurations, including precise cause, EPC, TVAL, and
  `FReason`; and
- raw `DASICSCALL.J/JR` behavior for trusted, disabled, and untrusted U-mode
  execution, including link and `ReturnPC` updates on success and absence of
  those side effects on an ordinary illegal-instruction trap; and
- `DASICSCALL.JR` decoded non-`x1` destinations and `DASICSCALL.J` nontrivial
  positive and negative distributed immediates;
- S-mode load, store, and jump behavior for untrusted open and closed fault
  controls, plus trusted and disabled bypass behavior, including precise S
  check-fault state and bypass side effects.
- S-mode untrusted success through valid read/write LibBounds, a valid
  JumpBound, and a special control-flow target;
- S-mode protected-CSR trusted access and untrusted read/write rejection,
  including destination, CSR, and `FReason` preservation;
- S-mode raw `DASICSCALL.J/JR` trusted, disabled, and untrusted behavior; and
- U-mode and S-mode MainBound high-end, empty, reversed, and below-low
  classification using precise ecall-fault witnesses; and
- N-extension HU load/store check faults delegated through `medeleg[24]` and
  `sedeleg[24]`, including HU handler entry, `ucause/uepc/utval/uscratch`,
  `ustatus.UIE/UPIE`, `FReason`, `uret` recovery, non-virtual `virtMode=0`,
  unchanged denied-load destination, and suppressed denied-store side effect.

Four cross-bound observations are specification-blocked. An 8-byte scalar that
crosses the 8-byte bound-address grain is necessarily misaligned, while the
priority between an ordinary misaligned exception and an FDI range-check fault
is not frozen. These observations are excluded from the default gate and never
produce a semantic PASS or FAIL. Capture them separately from the LinkNan root:

```bash
xmake nemu-dasics-semantics-test --jobs=48 --diagnostic
```

The diagnostic output records `mcause`, `mepc`, `mtval`, `FReason`, and whether
the cross-bound store changed memory. It covers adjacent read bounds,
overlapping read bounds, adjacent write bounds, and the partially permitted
load used to observe `mtval`.

Address-plus-size overflow is intentionally not exercised. Its architectural
behavior remains specification-blocked and this test must not establish an
implicit result for it.
