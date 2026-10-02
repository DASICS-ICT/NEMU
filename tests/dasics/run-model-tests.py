#!/usr/bin/env python3
"""Execute A01 v2 CSR expectations through a real shared NEMU reference."""

import argparse
import concurrent.futures
import ctypes as C
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import signal
import struct
import subprocess
import sys
import time
import traceback


# Reuse the frozen UIT wire declarations and existing compatibility programs.
# Suite evidence includes this dependency; its legacy off expectations are unused.
HELPER = Path(__file__).with_name("uit-baseline.py")
if not HELPER.exists():
    HELPER = Path(__file__).resolve().parent.parent / "user-timer/run-model-tests.py"
SPEC = importlib.util.spec_from_file_location("uit_baseline", HELPER)
UIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(UIT)
MASK64, BASE, MTRAP, DATA = UIT.MASK64, UIT.BASE, UIT.MTRAP, UIT.DATA
REG_PC, REG_MODE, REG_V = UIT.REG_PC, UIT.REG_MODE, UIT.REG_V
csr_insn, addi, words, check = UIT.csr_insn, UIT.addi, UIT.words, UIT.check
TARGET, POOL = BASE + 0x600, BASE + 0x8000
SENTINEL = 0xDCBA9876543210EF
MRET, ECALL, URET = 0x30200073, 0x00000073, 0x00200073
SCFG, UCFG, SLO, SHI, ULO, UHI = 0xBC4, 0x9E1, 0xBC5, 0xBC6, 0x9E2, 0x9E3

# Independent transcription of the frozen A01 v2 architectural table. No RTL,
# implementation headers, DUT state, or reference-exported FDI values form it.
FDI = {
    SCFG: ("FDISMainCfg", 0x7FF, "MainCfg"),
    UCFG: ("FDIUMainCfg", 0x7C2, "MainCfg"),
    SLO: ("FDISMainBoundLo", MASK64 ^ 7, "SLo"),
    SHI: ("FDISMainBoundHi", MASK64 ^ 7, "SHi"),
    ULO: ("FDIUMainBoundLo", MASK64 ^ 7, "ULo"),
    UHI: ("FDIUMainBoundHi", MASK64 ^ 7, "UHi"),
    0x880: ("FDILibCfg", 0xBBBBBBBBBBBBBBBB, "LibCfg"),
}
for index in range(16):
    for half in range(2):
        name = f"FDILibBound{'Hi' if half else 'Lo'}{index}"
        FDI[0x890 + index * 2 + half] = (name, MASK64 ^ 7, name)
for address, name in ((0x8B0, "FDIMainCallEntry"), (0x8B1, "FDIReturnPC"),
                      (0x8B2, "FDIActiveZoneReturnPC")):
    FDI[address] = (name, MASK64, name)
FDI[0x8B3] = ("FDIFReason", 7, "FReason")
FDI[0x8C8] = ("FDIJumpCfg", 0x0001000100010001, "JumpCfg")
for index in range(4):
    for half in range(2):
        name = f"FDIJumpBound{'Hi' if half else 'Lo'}{index}"
        FDI[0x8C0 + index * 2 + half] = (name, MASK64 ^ 7, name)
check(len(FDI), 52, "frozen CSR view count")
check(len({entry[2] for entry in FDI.values()}), 51, "frozen backing count")


class Oracle:
    def __init__(self):
        self.bank = {entry[2]: 0 for entry in FDI.values()}

    def read(self, address):
        _, mask, backing = FDI[address]
        return self.bank[backing] & mask

    def write(self, address, value):
        _, mask, backing = FDI[address]
        self.bank[backing] = (self.bank[backing] & ~mask) | (value & mask)

    def operation(self, address, funct3, encoded_source, value):
        old = self.read(address)
        if funct3 in (1, 5) or encoded_source:
            value = (value if funct3 in (1, 5) else old | value
                     if funct3 in (2, 6) else old & ~value)
            self.write(address, value)
        return old


class Reference(UIT.Reference):
    """Only initial standard fixture state may be imported; FDI uses instructions."""

    def __init__(self, path, enabled, protocol=False):
        UIT.layout_checks()
        self.lib = C.CDLL(str(path), mode=os.RTLD_LOCAL)
        signatures = {
            "difftest_init": (None, []),
            "difftest_set_ramsize": (None, [C.c_size_t]),
            "difftest_memcpy": (None, [C.c_uint64, C.c_void_p, C.c_size_t, C.c_bool]),
            "difftest_regcpy": (None, [C.c_void_p, C.c_bool]),
            "difftest_csrcpy": (None, [C.c_void_p, C.c_bool]),
            "difftest_exec": (None, [C.c_uint64]),
            "get_abs_instr_count": (C.c_uint64, []),
            "difftest_uit_query_caps": (C.c_int32, [C.c_void_p, C.c_uint32]),
            "difftest_uit_init": (C.c_int32, [C.c_void_p, C.c_uint32]),
            "difftest_uit_exec": (C.c_int32, [C.c_void_p, C.c_uint32, C.c_void_p, C.c_uint32]),
            "difftest_uit_raise_event": (C.c_int32, [C.c_void_p, C.c_uint32]),
            "difftest_uit_get_state": (C.c_int32, [C.c_void_p, C.c_uint32]),
            "difftest_uit_read_tx": (C.c_int32, [C.c_void_p, C.c_uint32]),
        }
        for name, (restype, argtypes) in signatures.items():
            function = getattr(self.lib, name)
            function.restype, function.argtypes = restype, argtypes
        self.caps = self.output("query_caps", UIT.Caps)
        for field, expected in (("version", UIT.VERSION), ("bytes", 64), ("xlen", 64),
                                ("vlen", 128), ("legacy_regcpy_bytes", 1400),
                                ("legacy_csrcpy_bytes", 32768), ("legacy_regcpy_arity", 2),
                                ("max_harts", 1), ("exec_request_bytes", 64),
                                ("event_request_bytes", 64), ("state_bytes", 112),
                                ("exec_result_bytes", 64),
                                ("enabled_features", 0x3F if enabled else 0)):
            check(getattr(self.caps, field), expected, "caps." + field)
        check(self.caps.supported_features & 0x3F, 0x3F, "supported wire features")
        self.lib.difftest_set_ramsize(16 << 20)
        self.lib.difftest_init()
        self.enabled, self.protocol = enabled, protocol
        self.started = False
        self.epoch, self.seq, self.uid, self.event_uid, self.count = 0x106, 0, 0, 0, 0
        self.metrics = dict.fromkeys(("controlled_execution_calls", "normal_execution_calls",
                                      "retired_instructions", "isa_exceptions", "samples",
                                      "hu_events", "uret", "protocol_rejections", "tx_records",
                                      "runtime_state_imports", "fdi_reads", "fdi_writes"), 0)

    def setup(self, code, **kwargs):
        if any(address in FDI for address in kwargs.get("csrs", {})):
            raise AssertionError("FDI setup must execute CSR instructions")
        kwargs.setdefault("start", self.protocol)
        super().setup(code, **kwargs)

    def normal(self, count=1, retired=True):
        super().normal(count, retired)
        self.started = True

    def step(self, pc, retired=True):
        check(self.regs()[REG_PC], pc, "instruction start PC")
        self.normal(retired=retired)


def load(rd, base, offset):
    return ((offset & 0xFFF) << 20) | base << 15 | 3 << 12 | rd << 7 | 0x03


def literal_writes(values):
    code, pool = [], []
    for address, value in values:
        code += [load(5, 20, 8 * len(pool)), csr_insn(address, 1, 0, 5)]
        pool.append(value & MASK64)
    return code, struct.pack("<" + "Q" * len(pool), *pool)


def snapshot_code():
    return words(*(csr_insn(address, 2, 12, 0) for address in FDI))


def snapshot(ref, oracle, pc):
    for index, address in enumerate(FDI):
        ref.step(pc + 4 * index)
        check(ref.regs()[12], oracle.read(address), FDI[address][0] + " snapshot")
        ref.metrics["fdi_reads"] += 1


def illegal(ref, pc, instruction):
    registers = ref.regs()
    check(registers[REG_MODE], 3, "ordinary illegal trap mode")
    check(registers[REG_V], 0, "ordinary illegal trap host context")
    check(registers[REG_PC], MTRAP, "ordinary illegal trap target")
    bank = ref.csrs()
    check(bank[0x342], 2, "ordinary illegal mcause")
    check(bank[0x341], pc, "illegal mepc is instruction source")
    check(bank[0x343], instruction, "illegal mtval is instruction encoding")
    ref.metrics["isa_exceptions"] += 1


def test_reset(ref):
    # The boot ROM is an existing ordinary jump sequence. No register/CSR import
    # occurs before these observations, including before the boot instructions.
    reset_pc = ref.regs()[REG_PC]
    # Shared initialization registers the flash map without allocating its
    # backing. The existing loader's null path installs the configured ROM;
    # this imports executable memory only, never architectural register state.
    load_flash = ref.lib.difftest_load_flash
    load_flash.restype, load_flash.argtypes = None, [C.c_void_p, C.c_size_t]
    load_flash(None, 0)
    ref.write_memory(BASE, snapshot_code())
    for _ in range(8):
        if ref.regs()[REG_PC] == BASE:
            break
        ref.normal()
    check(ref.regs()[REG_PC], BASE, "reset ROM reaches installed read program")
    snapshot(ref, Oracle(), BASE)
    ref.metrics["reset_observed_views"] = 52
    ref.metrics["initial_state_imports_before_reset"] = 0
    ref.metrics["reset_pc"] = reset_pc


def test_bank(ref, address):
    values = {0: 0, 5: 0xFEDCBA987654321F, 6: 0, 7: 0x1234567800000011,
              8: MASK64, 9: 0x4000000000000007}
    operations = [(1, 10, 8), (1, 10, 5), (2, 10, 7), (3, 10, 7),
                  (5, 10, 31), (6, 10, 16), (7, 10, 1),
                  (2, 10, 0), (3, 10, 0), (2, 10, 6), (3, 10, 6),
                  (6, 10, 0), (7, 10, 0), (1, 0, 6), (5, 0, 0),
                  (1, 0, 8), (1, 10, 0), (1, 10, 9)]
    code = []
    for funct3, rd, source in operations:
        code += [csr_insn(address, funct3, rd, source), csr_insn(address, 2, 11, 0)]
    ref.setup(words(*code), gprs=values, mc=0, sc=0)
    oracle = Oracle()
    for index, (funct3, rd, source) in enumerate(operations):
        old = oracle.operation(address, funct3, source, source if funct3 >= 5 else values[source])
        pc = BASE + 8 * index
        ref.step(pc)
        check(ref.regs()[REG_PC], pc + 4, "legal M CSR ignores stateen and source trust")
        if rd:
            check(ref.regs()[rd], old, "operation returns projected old view")
        ref.step(pc + 4)
        check(ref.regs()[11], oracle.read(address), "six-operation independent result")
        check(ref.regs()[0], 0, "x0 remains zero")
        ref.metrics["fdi_reads"] += 1 + int(bool(rd))
        ref.metrics["fdi_writes"] += int(funct3 in (1, 5) or source != 0)


def test_independence(ref):
    oracle, assignments = Oracle(), []
    for index, address in enumerate(FDI):
        value = 0xC321000000000005 | (index + 1) << 3
        assignments.append((address, value))
        oracle.write(address, value)
    # Lo > Hi and Hi == 0 are legal stored states, not corrected intervals.
    assignments += [(SLO, MASK64), (SHI, 0), (ULO, 0x8000000000000000),
                    (UHI, 0x8000000000000000)]
    for address, value in assignments[-4:]:
        oracle.write(address, value)
    code, pool = literal_writes(assignments)
    ref.setup(words(*code) + snapshot_code(), gprs={20: POOL}, extra_code={POOL: pool})
    ref.normal(len(code))
    snapshot(ref, oracle, BASE + len(code) * 4)


def test_alias(ref):
    actions = [(SCFG, 1, MASK64), (UCFG, 1, 0), (UCFG, 2, 0x7C2),
               (UCFG, 3, MASK64), (SCFG, 1, 0), (UCFG, 1, 0x7FF),
               (SCFG, 2, 0x3D), (UCFG, 2, 0), (UCFG, 3, 0)]
    code, pool = [], []
    for address, funct3, value in actions:
        code += [load(5, 20, 8 * len(pool)), csr_insn(address, funct3, 10, 5),
                 csr_insn(SCFG, 2, 11), csr_insn(UCFG, 2, 12)]
        pool.append(value)
    ref.setup(words(*code), gprs={20: POOL},
              extra_code={POOL: struct.pack("<" + "Q" * len(pool), *pool)})
    oracle = Oracle()
    for index, (address, funct3, value) in enumerate(actions):
        old = oracle.operation(address, funct3, 5, value)
        ref.normal(4)
        check(ref.regs()[10], old, "alias operation returns matching projection")
        check(ref.regs()[11], oracle.read(SCFG), "S view observes shared backing")
        check(ref.regs()[12], oracle.read(UCFG), "U view preserves original bit positions")
        if index == 1:
            check(ref.regs()[11], 0x3D, "U RW zero preserves hidden S bits")


def test_reason(ref):
    instructions = []
    for value in range(8):
        instructions += [csr_insn(0x8B3, 5, 0, value), csr_insn(0x8B3, 2, 10)]
    ref.setup(words(*instructions))
    for value in range(8):
        ref.normal(2)
        check(ref.regs()[10], value, "software FReason value " + str(value))


def permission_values(context, enables, trust, pc):
    s_trust, u_trust = (trust, not trust) if context == "HS" else (not trust, trust)
    bounds = lambda trusted: (pc & ~7, (pc & ~7) + 8) if trusted else (pc + 0x80, pc + 0x88)
    slo, shi = bounds(s_trust)
    ulo, uhi = bounds(u_trust)
    return [(SCFG, enables), (SLO, slo), (SHI, shi), (ULO, ulo), (UHI, uhi)]


def permitted(address, context, mc, sc, enables, trust):
    mode, virtual = UIT.CONTEXTS[context]
    if virtual or mode < ((address >> 8) & 3):
        return False
    if mode == 3:
        return True
    if not mc or (mode == 0 and not sc):
        return False
    return not (enables & (1 if mode == 1 else 2)) or trust


def test_permission(ref, address, context, mc, sc, enables, trust, write,
                    boundary=None, rewrite=None):
    mode, virtual = UIT.CONTEXTS[context]
    pc = TARGET if boundary != "last" else TARGET + 4
    assignments = [(item, (0xF13500000000000F | index << 4)) for index, item in enumerate(FDI)]
    assignments += permission_values(context, enables, trust, pc)
    if boundary:
        lo, hi = {"lo": (TARGET, TARGET + 8), "last": (TARGET, TARGET + 8),
                  "hi": (TARGET - 8, TARGET), "before": (TARGET + 8, TARGET + 16),
                  "next": (TARGET, TARGET + 8), "empty": (TARGET, TARGET),
                  "reverse": (TARGET + 8, TARGET),
                  "high": (0x8000000080000600, 0x8000000080000610)}[boundary]
        if boundary == "next":
            pc = TARGET - 4
        own = (SLO, SHI) if context == "HS" else (ULO, UHI)
        assignments += [(own[0], lo), (own[1], hi)]
        trust = lo <= pc < hi
    source = 0x5A5A76543210123F if rewrite is None else rewrite
    operation = csr_insn(address, 1, 10, 7) if write else csr_insn(address, 2, 10, 0)
    code, pool = literal_writes(assignments)
    oracle = Oracle()
    for item, value in assignments:
        oracle.write(item, value)
    expected = permitted(address, context, mc, sc, enables, trust)
    ref.setup(words(*code, MRET), mc=mc, sc=sc, gprs={7: source, 10: SENTINEL, 20: POOL},
              csrs={0x300: 0xA << 32 | mode << 11 | virtual << 39, 0x341: pc},
              extra_code={POOL: pool, pc: words(operation, ECALL), MTRAP: snapshot_code()})
    ref.normal(len(code) + 1)
    check(ref.regs()[REG_MODE], mode, "real MRET mode")
    check(ref.regs()[REG_V], virtual, "real MRET virtualization")
    ref.step(pc, retired=expected)
    if expected:
        check(ref.regs()[10], oracle.read(address), "permitted CSR old value")
        check(ref.regs()[REG_PC], pc + 4, "permitted CSR sequential successor")
        if write:
            oracle.write(address, source)
        ref.step(pc + 4, retired=False)
        check(ref.regs()[REG_PC], MTRAP, "real ECALL enters observation handler")
        check(ref.csrs()[0x342], {0: 8, 1: 9, 3: 11}[mode], "standard ECALL cause")
    else:
        illegal(ref, pc, operation)
        check(ref.regs()[10], SENTINEL, "denial preserves destination GPR")
    snapshot(ref, oracle, MTRAP)
    return expected


def test_transition(ref):
    # HS and HU write the same Lib/Jump banks, separated by an actual SRET.
    hs, hu = TARGET, TARGET + 0x100
    hs_code = words(csr_insn(0x880, 1, 10, 7), csr_insn(0x8C0, 1, 10, 8),
                    csr_insn(0x8C8, 1, 10, 9), 0x10200073)
    hu_code = words(csr_insn(0x880, 2, 10), csr_insn(0x8C0, 2, 11),
                    csr_insn(0x8C8, 2, 12), csr_insn(0x880, 1, 0, 6), ECALL)
    ref.setup(words(MRET), gprs={6: 0xA, 7: MASK64, 8: 0xE000000000000007, 9: MASK64},
              csrs={0x300: 0xA << 32 | 1 << 11, 0x341: hs, 0x141: hu},
              extra_code={hs: hs_code, hu: hu_code, MTRAP: words(csr_insn(0x880, 2, 13))})
    ref.normal(1)
    check(ref.regs()[REG_MODE], 1, "MRET enters HS")
    ref.normal(4)
    check(ref.regs()[REG_MODE], 0, "SRET enters HU")
    ref.normal(3)
    check(ref.regs()[10], FDI[0x880][1], "HU sees HS LibCfg")
    check(ref.regs()[11], 0xE000000000000000, "HU sees HS bound full high bits")
    check(ref.regs()[12], FDI[0x8C8][1], "HU sees HS JumpCfg")
    ref.normal(1)
    ref.normal(retired=False)
    ref.normal(1)
    check(ref.regs()[13], 0xA, "M sees HU update to same shared bank")


def test_readonly(ref, funct3, rd, source):
    instruction = csr_insn(0xF14, funct3, rd, source)
    write = funct3 in (1, 5) or source != 0
    ref.setup(words(instruction), gprs={5: 0, 10: SENTINEL})
    ref.step(BASE, retired=not write)
    if write:
        illegal(ref, BASE, instruction)
        check(ref.regs()[10], SENTINEL, "read-only write rejection preserves rd")
    else:
        check(ref.regs()[REG_PC], BASE + 4, "encoded zero read is legal")
        if rd:
            check(ref.regs()[rd], 0, "mhartid independent zero read")
    return not write


def test_delegation(ref):
    instructions = [csr_insn(0x302, 2, 10), csr_insn(0x602, 2, 11),
                    csr_insn(0x302, 1, 0, 5), csr_insn(0x602, 1, 0, 5),
                    csr_insn(0x302, 2, 12), csr_insn(0x602, 2, 13)]
    ref.setup(words(*instructions), gprs={5: MASK64})
    ref.normal(len(instructions))
    regs, bits = ref.regs(), 3 << 24
    check(regs[10] & bits, 0, "medeleg DASICS reset bits")
    check(regs[11] & bits, 0, "hedeleg DASICS reset bits")
    check(regs[12] & bits, bits if ref.enabled else 0, "conditional medeleg DASICS bits")
    check(regs[13] & bits, 0, "hedeleg never delegates host DASICS")


def test_off_reject(ref, address, write):
    instruction = URET if address == -1 else csr_insn(address, 1 if write else 2, 10, 5 if write else 0)
    ref.setup(words(instruction), gprs={5: MASK64, 10: SENTINEL})
    ref.step(BASE, retired=False)
    illegal(ref, BASE, instruction)
    check(ref.regs()[10], SENTINEL, "disabled operation preserves destination")


def test_no_alias(ref, address):
    instruction = csr_insn(address, 1, 10, 5)
    ref.setup(words(csr_insn(SCFG, 1, 0, 6), instruction),
              gprs={5: MASK64, 6: 0x35, 10: SENTINEL}, extra_code={MTRAP: snapshot_code()})
    ref.normal()
    ref.step(BASE + 4, retired=False)
    illegal(ref, BASE + 4, instruction)
    check(ref.regs()[10], SENTINEL, "retired alias rejection preserves rd")
    oracle = Oracle()
    oracle.write(SCFG, 0x35)
    snapshot(ref, oracle, MTRAP)


def test_basic(ref):
    # VLEN=128, e8/m1, four active elements: vmv.v.i 3; vadd.vi 4; vse8.v.
    vector = [(5 << 15) | (7 << 12) | (10 << 7) | 0x57,
              (0x17 << 26) | (1 << 25) | (3 << 15) | (3 << 12) | (1 << 7) | 0x57,
              (1 << 25) | (1 << 20) | (4 << 15) | (3 << 12) | (2 << 7) | 0x57,
              (1 << 25) | (20 << 15) | (2 << 7) | 0x27]
    ref.setup(words(addi(11, 0, 7), *vector), gprs={5: 4, 20: DATA},
              csrs={0x300: 0xA << 32 | 1 << 9})
    ref.normal(5)
    check(ref.regs()[REG_PC], BASE + 20, "ordinary scalar/RVV execution")
    check(ref.regs()[11], 7, "ordinary ADDI")
    check(ref.regs()[10], 4, "vsetvli selected VL")
    check(ref.read_memory(DATA, 4), bytes([7] * 4), "ordinary RVV arithmetic and store")


def test_off_protocol(ref):
    objects = (("init", UIT.Init()), ("raise_event", UIT.Event()),
               ("get_state", UIT.State()), ("read_tx", UIT.Tx()))
    for name, value in objects:
        C.memset(C.byref(value), 0xA5, C.sizeof(value))
        before = bytes(value)
        check(getattr(ref.lib, "difftest_uit_" + name)(C.byref(value), C.sizeof(value)),
              UIT.E["FEATURE"], "off inactive " + name)
        check(bytes(value), before, "off inactive call preserves buffer")
    request, result = UIT.Request(), UIT.Result()
    C.memset(C.byref(result), 0xA5, 64)
    check(ref.lib.difftest_uit_exec(C.byref(request), 64, C.byref(result), 64),
          UIT.E["FEATURE"], "off inactive exec")
    check(bytes(result), b"\xA5" * 64, "off exec leaves output untouched")
    check(ref.csrs()[0x301] & ((1 << 13) | (1 << 23)), 0, "off misa N/X absent")
    ref.metrics["protocol_rejections"] += 5


def test_uit(ref, arguments):
    name, args = arguments[0], arguments[1:]
    if name == "abi":
        UIT.test_abi(ref)
    elif name == "sample-program":
        UIT.test_sample_program(ref)
    elif name == "sample":
        UIT.test_sample(ref, int(args[0]), int(args[1]), int(args[2]), args[3], int(args[4]))
    elif name == "entry":
        UIT.test_entry(ref)
    elif name == "entry-upper":
        UIT.test_entry(ref, upper=args[0])
    elif name == "entry-denied":
        UIT.test_entry_denied(ref, args[0])
    elif name == "protocol":
        UIT.test_protocol(ref, args[0])
    elif name == "event-protocol":
        UIT.test_event_protocol(ref, args[0])
    elif name == "tx":
        UIT.test_tx(ref)
    elif name == "tx-rejected":
        UIT.test_tx_rejected(ref, args[0])
    elif name == "import-rejected":
        UIT.test_import_rejected(ref, args[0])
    else:
        raise AssertionError("unknown UIT compatibility case " + name)


def cases(enabled):
    common = ["legacy-transport", "delegation", "basic-rvv"]
    common += [f"readonly:{funct3}:{rd}:{source}" for funct3 in (1, 2, 3, 5, 6, 7)
               for rd in (0, 10) for source in (0, 5)]
    if not enabled:
        return common + ["off-protocol"] + [f"off:{address}:{write}" for address in
                (*FDI, *UIT.ALL_CSRS, -1) for write in (0, 1)]
    result = common + ["reset", "independence", "alias", "reason", "host-transition"]
    result += ["bank:" + str(address) for address in FDI]
    result += ["no-alias:" + str(address) for address in (0xBC3, 0x9E0)]
    # All addresses cross each encoding privilege and virtualization boundary.
    result += [f"permission:{address}:{context}:1:1:0:0:{write}"
               for address in FDI for context in UIT.CONTEXTS for write in (0, 1)]
    # The three encoded privilege classes cover independent stateen and enables.
    result += [f"permission:{address}:{context}:{mc}:{sc}:{enables}:{trust}:1"
               for address in (SCFG, UCFG, 0x880) for context in UIT.CONTEXTS
               for mc, sc in ((0, 0), (0, 1), (1, 0), (1, 1))
               for enables in (0, 1, 2, 3) for trust in (0, 1)
               if (mc, sc, enables, trust) != (1, 1, 0, 0)]
    # Read permission must traverse the same gates; the exhaustive write cases
    # alone cannot detect a path that accidentally authorizes all pure reads.
    result += [f"permission:{address}:{context}:{mc}:{sc}:{enables}:{trust}:0"
               for address, context, mc, sc, enables, trust in (
                   (UCFG, "HS", 0, 1, 0, 0),
                   (UCFG, "HS", 1, 0, 1, 0),
                   (UCFG, "HS", 1, 0, 1, 1),
                   (UCFG, "HS", 1, 0, 2, 0),
                   (0x880, "HU", 0, 1, 0, 0),
                   (0x880, "HU", 1, 0, 0, 0),
                   (0x880, "HU", 1, 1, 2, 0),
                   (0x880, "HU", 1, 1, 2, 1),
                   (0x880, "HU", 1, 1, 1, 0))]
    result += [f"boundary:{context}:{edge}" for context in ("HS", "HU")
               for edge in ("lo", "last", "hi", "before", "next", "empty", "reverse", "high")]
    # UCFG is S encoded; source authorization is therefore the S interval even
    # when the instruction modifies uEnable. Source-region edits use old bounds.
    result += ["prewrite:disable", "prewrite:enable", "prewrite:bound"]
    result += ["uit:" + name for name in
               ("abi", "sample-program", "entry", "entry-upper:M", "entry-upper:HS", "tx",
                "entry-denied:nested", "entry-denied:mode-VS", "entry-denied:mode-VU",
                "import-rejected:regcpy", "import-rejected:csrcpy",
                "protocol:epoch", "protocol:order", "protocol:duplicate",
                "protocol:pc", "protocol:missing", "protocol:wrong-sample-csr",
                "event-protocol:count", "event-protocol:duplicate", "event-protocol:target",
                "tx-rejected:address", "tx-rejected:width", "tx-rejected:read")]
    result += [f"uit:sample:{csr}:{funct3}:{rd}:{source}:{payload}"
               for csr, payload in ((0x800, 0x123456789ABCDEF0), (0x044, 1))
               for funct3, rd, source in ((1, 0, "x0"), (1, 10, "zero"),
                                         (2, 10, "zero"), (3, 10, "x0"),
                                         (5, 0, "x0"), (6, 10, "value"), (7, 10, "value"))]
    return result


def run_case(args):
    parts = args.case.split(":")
    name, values = parts[0], parts[1:]
    ref = Reference(args.reference, args.state == "on", protocol=name == "uit")
    status = "PASS"
    if name == "reset":
        test_reset(ref)
    elif name == "bank":
        test_bank(ref, int(values[0]))
    elif name == "independence":
        test_independence(ref)
    elif name == "alias":
        test_alias(ref)
    elif name == "reason":
        test_reason(ref)
    elif name == "host-transition":
        test_transition(ref)
    elif name == "permission":
        address, context, mc, sc, enables, trust, write = values
        allowed = test_permission(ref, int(address), context, int(mc), int(sc), int(enables),
                                  bool(int(trust)), bool(int(write)))
        status = "PASS" if allowed else "EXPECTED_REJECTION"
    elif name == "boundary":
        context, boundary = values
        allowed = test_permission(ref, 0x880, context, 1, 1, 3, False, True, boundary=boundary)
        status = "PASS" if allowed else "EXPECTED_REJECTION"
    elif name == "prewrite":
        # The U view cannot use U authorization to grant an HS write. Encoded
        # privileges prevent HS/HU from rewriting their own source-authority
        # fields, so these cases do not independently prove check/write order.
        settings = {"disable": (UCFG, "HS", 3, False, 0),
                    "enable": (UCFG, "HS", 0, False, 2),
                    "bound": (ULO, "HS", 1, False, TARGET)}
        address, context, enables, trust, rewrite = settings[values[0]]
        allowed = test_permission(ref, address, context, 1, 1, enables, trust, True, rewrite=rewrite)
        status = "PASS" if allowed else "EXPECTED_REJECTION"
    elif name == "readonly":
        allowed = test_readonly(ref, *(int(value) for value in values))
        status = "PASS" if allowed else "EXPECTED_REJECTION"
    elif name == "delegation":
        test_delegation(ref)
    elif name == "basic-rvv":
        test_basic(ref)
    elif name == "off":
        test_off_reject(ref, int(values[0]), int(values[1]))
        status = "EXPECTED_REJECTION"
    elif name == "off-protocol":
        test_off_protocol(ref)
        status = "EXPECTED_REJECTION"
    elif name == "no-alias":
        test_no_alias(ref, int(values[0]))
        status = "EXPECTED_REJECTION"
    elif name == "legacy-transport":
        UIT.test_legacy_transport(ref)
    elif name == "uit":
        test_uit(ref, values)
        if "protocol" in values[0] or "denied" in values[0] or "rejected" in values[0]:
            status = "EXPECTED_REJECTION"
    else:
        raise AssertionError("unknown model case " + args.case)
    result = {"case": args.case, "status": status, "metrics": ref.metrics}
    if name == "prewrite":
        result["coverage_note"] = (
            "Checks source authorization and rejected-write side effects. Encoded "
            "privileges prevent HS/HU writes to their own source-authority fields; "
            "check-before-write ordering additionally requires source review.")
    print("DASICS_MODEL_RESULT " + json.dumps(result), flush=True)


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--state", choices=("off", "on"), required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--jobs", type=int, choices=range(1, 5), default=4)
    parser.add_argument("--case", help="run one case in an isolated process")
    parser.add_argument("--select", action="append", help="run only these exact cases")
    args = parser.parse_args()
    args.reference = args.reference.resolve(strict=True)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    if args.case:
        try:
            run_case(args)
            return 0
        except Exception as error:
            traceback.print_exc()
            print("DASICS_MODEL_RESULT " + json.dumps({"case": args.case, "status": "FAIL",
                                                      "error": str(error)}), flush=True)
            return 1
    if not args.output:
        parser.error("--output is required for a suite")
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("output must be empty to preserve previous evidence")
    selected = args.select or cases(args.state == "on")
    invalid = set(selected) - set(cases(args.state == "on"))
    if invalid:
        parser.error("unknown selected cases: " + ", ".join(sorted(invalid)))
    output.mkdir(parents=True, exist_ok=True)
    driver = output / "driver.py"
    driver.write_bytes(Path(__file__).read_bytes())
    (output / "uit-baseline.py").write_bytes(HELPER.read_bytes())
    started, start_clock = timestamp(), time.monotonic()

    def execute(name):
        command = [sys.executable, str(driver), "--reference", str(args.reference),
                   "--state", args.state, "--case", name]
        stem = name.replace(":", "_")
        log = output / (stem + ".log")
        before, clock = timestamp(), time.monotonic()
        with log.open("w") as stream:
            try:
                process = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT,
                                         timeout=60, check=False)
                code, timed_out = process.returncode, False
            except subprocess.TimeoutExpired:
                code, timed_out = None, True
        result = {"case": name, "status": "FAIL", "exit_code": code,
                  "timed_out": timed_out, "command": command, "log": str(log),
                  "start_utc": before, "end_utc": timestamp(),
                  "elapsed_seconds": time.monotonic() - clock}
        log_text = log.read_text(errors="replace")
        markers = [line[len("DASICS_MODEL_RESULT "):] for line in log_text.splitlines()
                   if line.startswith("DASICS_MODEL_RESULT ")]
        if markers:
            result.update(json.loads(markers[-1]))
        if code != 0 or timed_out:
            result["status"] = "FAIL"
        if name.startswith("uit:import-rejected:"):
            operation = name.rsplit(":", 1)[1]
            expected = (code == -signal.SIGABRT
                        and "UIT_EXPECTED_IMPORT_ABORT " + operation in log_text
                        and "uit_check_import" in log_text
                        and "!uit.initialized && !uit.started" in log_text)
            result["status"] = "EXPECTED_TERMINATION" if expected else "FAIL"
            result["expected_termination"] = "SIGABRT in uit_check_import after valid fixture setup"
        (output / (stem + ".json")).write_text(json.dumps(result, indent=2) + "\n")
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(execute, selected))
    counts = {status: sum(result["status"] == status for result in results)
              for status in ("PASS", "EXPECTED_REJECTION", "EXPECTED_TERMINATION", "FAIL")}
    summary = {"schema": 1, "kind": "real-dasics-csr-model-tests", "state": args.state,
               "reference": str(args.reference), "reference_sha256": hashlib.sha256(args.reference.read_bytes()).hexdigest(),
               "driver": str(driver), "driver_sha256": hashlib.sha256(driver.read_bytes()).hexdigest(),
               "uit_helper_sha256": hashlib.sha256(HELPER.read_bytes()).hexdigest(),
               "command": sys.argv, "start_utc": started, "end_utc": timestamp(),
               "elapsed_seconds": time.monotonic() - start_clock, "count": len(results),
               "counts": counts, "status": "FAIL" if counts["FAIL"] else "PASS", "cases": results,
               "scope": "Real NEMU CSR execution and existing UIT compatibility only; no DUT oracle, FDI transport, hardware cycle proof, or complete U05 composition."}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({key: value for key, value in summary.items() if key != "cases"}, indent=2))
    return int(bool(counts["FAIL"]))


if __name__ == "__main__":
    sys.exit(main())
