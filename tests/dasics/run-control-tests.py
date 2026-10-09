#!/usr/bin/env python3
"""Execute independent A01 control-flow expectations in real NEMU references."""

import argparse
import concurrent.futures
import importlib.util
import json
from pathlib import Path
import resource
import struct
import subprocess
import sys
import time
import traceback


FDI_HELPER = Path(__file__).with_name("fdi-baseline.py")
if not FDI_HELPER.exists():
    FDI_HELPER = Path(__file__).with_name("run-fdi-tests.py")
SPEC = importlib.util.spec_from_file_location("control_fdi_baseline", FDI_HELPER)
F = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(F)
M, check = F.M, F.M.check
PC, DEST = M.BASE + 0x600000, M.BASE + 0x601000
EBREAK = 0x00100073
RETURN, REASON, ENTRY, ACTIVE, JCFG = 0x8B1, 0x8B3, 0x8B0, 0x8B2, 0x8C8
OLD_RETURN, OLD_ENTRY, OLD_ACTIVE = M.BASE + 0x9000, M.BASE + 0x9100, M.BASE + 0x9200


def fdij(offset):
    # A01 defines a signed 23-bit byte displacement, not the standard J format.
    check(offset & 1, 0, "FDICALL.J aligned displacement")
    if not -(1 << 22) <= offset < (1 << 22):
        raise ValueError("FDICALL.J displacement outside A01 range")
    value = (offset & 0x7FFFFF) >> 1
    return (0x0B | ((value >> 21) & 1) << 31 | ((value >> 20) & 1) << 7
            | ((value >> 14) & 63) << 15 | ((value >> 10) & 15) << 8
            | (value & 1023) << 21)


def indirect(rd, rs, immediate=0, custom=False):
    return ((immediate & 4095) << 20 | rs << 15 | rd << 7
            | (0x100B if custom else 0x67))


def branch(kind, rs1, rs2, offset):
    return M.UIT.beq(rs1, rs2, offset) | kind << 12


def cj(offset):
    value = offset & 4095
    mapping = ((11, 12), (4, 11), (9, 10), (8, 9), (10, 8),
               (6, 7), (7, 6), (3, 5), (2, 4), (1, 3), (5, 2))
    return 0xA001 | sum(((value >> source) & 1) << dest for source, dest in mapping)


def cb(offset, nonzero=False):
    value = offset & 511
    mapping = ((8, 12), (4, 11), (3, 10), (7, 6), (6, 5), (2, 4), (1, 3), (5, 2))
    return (0xE001 if nonzero else 0xC001) | sum(
        ((value >> source) & 1) << dest for source, dest in mapping)


def packed(instruction):
    return struct.pack("<H" if instruction & 3 != 3 else "<I", instruction)


class Fixture:
    def __init__(self, ref, instruction, *, context="HU", config=3, trusted=False,
                 additions=(), gprs=None, mc=1, sc=1, delegate=False, target=DEST,
                 fetch_fault=False, code=None, standard_csrs=None, handlers=None):
        self.ref, self.instruction = ref, instruction
        self.oracle = M.Oracle()
        self.mode, self.virtual = M.UIT.CONTEXTS[context]
        self.length = len(packed(instruction))
        assignments = [(M.SCFG, config), (RETURN, OLD_RETURN), (REASON, 7),
                       (ENTRY, OLD_ENTRY), (ACTIVE, OLD_ACTIVE)]
        if trusted:
            lo, hi = (M.SLO, M.SHI) if self.mode == 1 else (M.ULO, M.UHI)
            assignments += [(lo, PC), (hi, PC + 8)]
        assignments += list(additions)
        setup, pool = M.literal_writes(assignments) if ref.enabled else ([], b"")
        for address, value in assignments:
            self.oracle.write(address, value)
        observers = M.words(*(M.csr_insn(address, 2, register) for register, address in
                              ((28, RETURN), (29, REASON), (30, ENTRY), (31, ACTIVE))))
        memory = {M.POOL: pool, PC: code or packed(instruction) + M.words(EBREAK),
                  M.MTRAP: observers, M.UIT.STRAP: observers}
        memory.update(handlers or {})
        if not fetch_fault and abs(target - PC) >= 8:
            memory[target] = M.words(EBREAK)
        registers = {1: M.SENTINEL, 10: M.SENTINEL, 20: M.POOL, **(gprs or {})}
        csrs = {0x300: 0xA << 32 | self.mode << 11 | self.virtual << 39,
                0x341: PC, 0x302: (3 << 24) if delegate else 0, **(standard_csrs or {})}
        # Reset capture precedes any fixture import. Binding afterwards forbids
        # every runtime import while the read-only wire observes implicit state.
        if ref.enabled:
            F.bind(ref.lib)
            F.reset(ref)
        ref.setup(M.words(*setup, M.MRET), gprs=registers, csrs=csrs,
                  extra_code=memory, mc=mc, sc=sc)
        if ref.enabled:
            F.initialize(ref.lib)
        ref.normal(len(setup) + 1)
        check(ref.regs()[M.REG_PC], PC, "fixture MRET source PC")
        check(ref.regs()[M.REG_MODE], self.mode, "fixture MRET source privilege")
        check(ref.regs()[M.REG_V], self.virtual, "fixture MRET source virtualization")
        self.before = list(ref.regs())[:32]
        self.delegate = delegate
        self.observe()

    def observe(self):
        if self.ref.enabled:
            F.state(self.ref, self.oracle)

    def execute(self, successor=None, link=None, call=False):
        count = self.ref.lib.get_abs_instr_count()
        self.ref.step(PC)
        check(self.ref.lib.get_abs_instr_count() - count, 1, "successful instruction counter delta")
        self.ref.metrics["checked_successful_count_deltas"] = self.ref.metrics.get("checked_successful_count_deltas", 0) + 1
        check(self.ref.regs()[M.REG_PC], successor, "completed control-flow successor")
        expected = self.before.copy()
        if link:
            expected[link] = PC + self.length
        check(list(self.ref.regs())[:32], expected, "only architectural link may change")
        if call:
            self.oracle.write(RETURN, PC + 4)
        self.observe()

    def trap(self, cause, tval, reason=None, pc=PC):
        delegated = self.delegate and cause in (24, 25)
        base, handler = (0x100, M.UIT.STRAP) if delegated else (0x300, M.MTRAP)
        check(self.ref.regs()[M.REG_PC], handler, "trap entry")
        check(self.ref.regs()[M.REG_MODE], 1 if delegated else 3, "trap privilege")
        check(self.ref.regs()[M.REG_V], 0, "trap host ownership")
        bank = self.ref.csrs()
        check(bank[base + 0x42], cause, "exact cause")
        check(bank[base + 0x41], pc, "source EPC")
        check(bank[base + 0x43], tval, "exact full-width TVAL")
        if reason is not None:
            self.oracle.write(REASON, reason)
        self.observe()
        self.ref.metrics["isa_exceptions"] += 1

    def reject(self, cause, tval, reason=None):
        count = self.ref.lib.get_abs_instr_count()
        self.ref.step(PC, retired=False)
        # Standard ECALL/EBREAK use an inline trap path in this reference and
        # count differently. Check only the longjmp exception contract here.
        if cause in (2, 24, 25):
            check(self.ref.lib.get_abs_instr_count() - count, 0, "rejected instruction counter delta")
            self.ref.metrics["checked_rejected_count_deltas"] = self.ref.metrics.get("checked_rejected_count_deltas", 0) + 1
        check(list(self.ref.regs())[:32], self.before, "rejection preserves every GPR")
        self.trap(cause, tval, reason)

    def read_observer(self):
        # M-mode uses ordinary CSR reads to cross-check the read-only wire.
        if self.ref.enabled and self.ref.regs()[M.REG_MODE] == 3:
            for register, address in ((28, RETURN), (29, REASON), (30, ENTRY), (31, ACTIVE)):
                self.ref.normal()
                check(self.ref.regs()[register], self.oracle.read(address), "real CSR observation")
                self.ref.metrics["fdi_reads"] += 1


def call_case(ref, kind, scenario):
    options = dict(trusted=True)
    offset, rd, rs, expected = 0x1000, 10, 7, True
    if scenario.startswith("imm="):
        offset = int(scenario[4:])
    elif scenario.startswith("rd="):
        rd = int(scenario[3:])
    elif scenario.startswith("source="):
        context = scenario[7:]
        options["context"] = context
        expected = context in ("HU", "HS")
    elif scenario == "untrusted":
        options["trusted"], expected = False, False
    elif scenario == "disabled":
        options["config"], expected = 0, False
    elif scenario == "other-enable":
        options["config"], expected = 1, False
    elif scenario == "close":
        options["config"] = 0x7FF
    elif scenario == "untrusted-close":
        options.update(config=0x7FF, trusted=False)
        expected = False
    elif scenario.startswith("stateen="):
        options["mc"], options["sc"] = (int(bit) for bit in scenario[8:].split(","))
    elif scenario == "trusted-target":
        options["additions"] = [(M.UHI, DEST + 8)]
    target = (PC + offset) & M.MASK64
    if kind == "j":
        instruction, link = fdij(offset), 1
    else:
        immediate = offset if scenario.startswith("imm=") else -3
        # Odd addition proves JALR-style bit-zero clearing. rd=rs1 uses old x7.
        base = ((target & ~1) - immediate + 1) & M.MASK64
        instruction, link = indirect(rd, rs, immediate, custom=True), rd
        options["gprs"] = {rs: base}
        target &= ~1
    expected = expected and ref.enabled
    fixture = Fixture(ref, instruction, target=target, **options)
    if not expected:
        fixture.reject(2, instruction)
        fixture.read_observer()
        return "EXPECTED_REJECTION"
    fixture.execute(target, link=link, call=True)
    if abs(target - PC) >= 8:
        ref.step(target, retired=False)
        fixture.trap(3, target, pc=target)
        fixture.read_observer()
    return "PASS"


# Each scenario has a hand-written A01 outcome; no production policy is read.
POLICY = {
    "deny": ({}, False), "trusted": ({"trusted": True}, True),
    "M": ({"context": "M"}, True), "HS": ({"context": "HS"}, False),
    "disabled": ({"config": 0}, True), "other-enable": ({"config": 1}, True),
    "close": ({"config": 3 | 1 << 9}, True),
    "other-close": ({"config": 3 | 1 << 5}, False),
    "hs-close": ({"context": "HS", "config": 3 | 1 << 5}, True),
    "stateen": ({"mc": 0, "sc": 0}, False),
    "guest": ({"context": "VU", "config": 0x7FF, "trusted": True}, "illegal"),
    "guest-disabled": ({"context": "VS", "config": 0}, True),
    "delegate": ({"delegate": True}, False),
    "hs-delegate": ({"context": "HS", "delegate": True}, False),
}


def jump_encoding(kind, target):
    offset = target - PC
    if kind == "jal":
        return M.UIT.jal(offset, 10), {}, 10
    if kind == "j":
        return M.UIT.jal(offset, 0), {}, 0
    if kind == "call":
        return M.UIT.jal(offset, 1), {}, 1
    if kind in ("jalr", "jalr-alias", "jr", "ret"):
        rd, rs = {"jalr": (10, 7), "jalr-alias": (7, 7), "jr": (0, 7), "ret": (0, 1)}[kind]
        return indirect(rd, rs), {rs: target | 1}, rd
    if kind == "c.j":
        return cj(offset), {}, 0
    rd, rs = (1, 1) if kind == "c.jalr-alias" else (1 if kind == "c.jalr" else 0, 7)
    return (0x9002 if rd else 0x8002) | rs << 7, {rs: target | 1}, rd


def jump_case(ref, kind, scenario):
    target = PC + 0x80
    options, expected = POLICY.get(scenario, ({}, True))
    options = dict(options)
    assignments = []
    if scenario.startswith("bound"):
        slot, edge = scenario[5:].split("=")
        lo, hi, valid = target, target + 8, True
        if edge == "last":
            target += 6
        elif edge == "hi":
            target += 8
        elif edge == "before":
            target -= 2
        elif edge == "empty":
            hi = lo
        elif edge == "reverse":
            lo, hi = hi, lo
        elif edge == "invalid":
            valid = False
        elif edge == "high":
            lo += 1 << 32
            hi += 1 << 32
        assignments += [(0x8C0 + 2 * int(slot), lo), (0x8C1 + 2 * int(slot), hi),
                        (JCFG, (1 << (16 * int(slot))) if valid else 0)]
        expected = edge in ("lo", "last")
    elif scenario.startswith("special"):
        slot, match = scenario[7:].split("=")
        assignments += [(int(slot), target if match == "hit" else target + (1 if match == "odd" else 1 << 32))]
        expected = match == "hit"
    elif scenario == "target-trusted-only":
        assignments += [(M.ULO, target), (M.UHI, target + 8)]
        expected = False
    elif scenario == "zero-specials":
        target, expected = 0, False
        assignments += [(ENTRY, 0), (RETURN, 0), (ACTIVE, 0)]
    elif scenario == "zero-bound":
        target, expected = 0, True
        assignments += [(JCFG, 1), (0x8C0, 0), (0x8C1, 8)]
    elif scenario == "high-target":
        target, expected = 0x8000000080600080, False
    options["additions"] = assignments
    instruction, gprs, link = jump_encoding(kind, target)
    target_backed = M.BASE <= target < M.BASE + (16 << 20)
    fixture = Fixture(ref, instruction, target=target, fetch_fault=not target_backed,
                      gprs=gprs, **options)
    if not ref.enabled:
        expected = True
    if expected == "illegal":
        fixture.reject(2, instruction)
    elif not expected:
        fixture.reject(25 if fixture.mode == 1 else 24, target, 4)
    else:
        fixture.execute(target, link=link)
        if target_backed:
            ref.step(target, retired=False)
            fixture.trap(3, target, pc=target)
    if ref.regs()[M.REG_PC] == M.MTRAP:
        fixture.read_observer()
    return "PASS" if expected is True else "EXPECTED_REJECTION"


# Operand pairs exercise signed/unsigned disagreement and decoder pseudos.
BRANCHES = {
    "beq": (0, 7, 8, 5, 5), "bne": (1, 7, 8, 5, 6),
    "blt": (4, 7, 8, M.MASK64, 0), "bge": (5, 7, 8, 0, M.MASK64),
    "bltu": (6, 7, 8, 0, M.MASK64), "bgeu": (7, 7, 8, M.MASK64, 0),
    "beqz": (0, 7, 0, 0, 0), "bnez": (1, 7, 0, 1, 0),
    "bltz": (4, 7, 0, M.MASK64, 0), "bgez": (5, 7, 0, 0, 0),
    "bgtz": (4, 0, 7, 0, 1), "blez": (5, 0, 7, 0, 0),
}


def branch_case(ref, kind, scenario):
    target, taken = PC + 0x40, scenario not in ("not-taken", "guest-not-taken")
    if kind in ("c.beqz", "c.bnez"):
        nonzero = kind == "c.bnez"
        instruction = cb(target - PC, nonzero)
        gprs = {8: int(taken == nonzero)}
    else:
        funct3, rs1, rs2, left, right = BRANCHES[kind]
        if not taken:
            if funct3 == 0:
                left, right = (1, 0) if rs2 == 0 else (0, 1)
            elif funct3 == 1:
                left = right = 0
            elif funct3 in (4, 6):
                left = right = 0
            else:
                left, right = (M.MASK64, 0) if rs2 == 0 else (0, 1)
        gprs = {register: value for register, value in ((rs1, left), (rs2, right)) if register}
        instruction = branch(funct3, rs1, rs2, target - PC)
    options = {}
    if scenario == "allow":
        options["additions"] = [(JCFG, 1), (0x8C0, target), (0x8C1, target + 8)]
    if scenario == "hs-deny":
        options["context"] = "HS"
    if scenario == "guest-not-taken":
        options["context"] = "VU"
    fixture = Fixture(ref, instruction, gprs=gprs, target=target, **options)
    denied = ref.enabled and taken and scenario != "allow"
    if denied:
        fixture.reject(25 if fixture.mode == 1 else 24, target, 4)
    else:
        successor = target if taken else PC + fixture.length
        fixture.execute(successor)
        ref.step(successor, retired=False)
        fixture.trap(3, successor, pc=successor)
    fixture.read_observer()
    return "EXPECTED_REJECTION" if denied else "PASS"


def ecall_case(ref, scenario):
    settings = {
        "HU": ({}, 24), "HS": ({"context": "HS"}, 25),
        "M": ({"context": "M"}, 11), "trusted": ({"trusted": True}, 8),
        "hs-trusted": ({"context": "HS", "trusted": True}, 9),
        "disabled": ({"config": 0}, 8), "other-enable": ({"config": 1}, 8),
        "close": ({"config": 3 | 1 << 6}, 8),
        "other-close": ({"config": 3 | 1 << 2}, 24),
        "hs-close": ({"context": "HS", "config": 3 | 1 << 2}, 9),
        "stateen": ({"mc": 0, "sc": 0}, 24),
        "guest": ({"context": "VU", "config": 0x7FF, "trusted": True}, 2),
        "guest-disabled": ({"context": "VS", "config": 0}, 10),
        "delegate": ({"delegate": True}, 24),
        "hs-delegate": ({"context": "HS", "delegate": True}, 25),
    }
    options, cause = settings[scenario]
    fixture = Fixture(ref, M.ECALL, **options)
    if not ref.enabled:
        cause = 10 if fixture.virtual and fixture.mode == 1 else {0: 8, 1: 9, 3: 11}[fixture.mode]
    fixture.reject(cause, M.ECALL if cause == 2 else 0, 1 if cause in (24, 25) else None)
    fixture.read_observer()
    return "EXPECTED_REJECTION" if cause in (2, 24, 25) else "PASS"


def fetch_case(ref, kind):
    # TOR permits execution below the destination, then forbids execute in its
    # page. The successful jump must commit before that next-fetch PMP fault.
    target = DEST
    instruction = indirect(10, 7, custom=kind == "call")
    fixture = Fixture(ref, instruction, target=target, fetch_fault=True, trusted=True,
                      gprs={7: target}, additions=[(ENTRY, target)],
                      standard_csrs={0x3A0: 0x0B0F, 0x3B0: target >> 2,
                                     0x3B1: (target + 4096) >> 2})
    if kind == "call" and not ref.enabled:
        fixture.reject(2, instruction)
        return "EXPECTED_REJECTION"
    fixture.execute(target, link=10, call=kind == "call")
    ref.step(target, retired=False)
    fixture.trap(1, target, pc=target)
    fixture.read_observer()
    return "PASS"


def invalid_case(ref, encoding):
    # Reserved custom-0 funct3 encodings and privileged MRET remain ordinary
    # illegal instructions even when source and target policy would permit.
    instruction = M.MRET if encoding == "mret" else 0x0B | int(encoding) << 12
    fixture = Fixture(ref, instruction, trusted=True, config=0x7FF)
    fixture.reject(2, instruction)
    fixture.read_observer()
    return "EXPECTED_REJECTION"


def special_case(ref, scenario):
    instruction = indirect(10, 7)
    if scenario.startswith("sdt-"):
        if scenario == "sdt-ecall":
            instruction = M.ECALL
        fixture = Fixture(ref, instruction, context="HS", delegate=True, gprs={7: DEST},
                          standard_csrs={0x300: 0xA << 32 | 1 << 11 | 1 << 24,
                                         0x30A: 1 << 59})
        check((ref.csrs()[0x300] >> 24) & 1, 1, "actual source SDT remains set")
        before = ref.lib.get_abs_instr_count()
        ref.step(PC, retired=False)
        check(ref.lib.get_abs_instr_count() - before, 0, "double-trap candidate does not complete")
        fixture.trap(16, 0 if scenario == "sdt-ecall" else DEST)
        check(ref.csrs()[0x34B], 25, "double trap retains original cause in mtval2")
        check(list(ref.regs())[:32], fixture.before, "double trap preserves all GPRs")
        fixture.read_observer()
    elif scenario == "rnmi-closed":
        fixture = Fixture(ref, instruction, gprs={7: DEST}, standard_csrs={0x744: 0})
        check(ref.csrs()[0x744] & 8, 0, "RNMI NMIE is closed before candidate")
        critical = ref.lib.difftest_raise_critical_error
        critical.argtypes, critical.restype = [], M.C.c_bool
        check(critical(), False, "no initial critical error")
        before = ref.lib.get_abs_instr_count()
        ref.step(PC, retired=False)
        check(ref.lib.get_abs_instr_count() - before, 0, "critical candidate does not complete")
        check(critical(), True, "RNMI-closed trap reports critical error")
        check(ref.regs()[M.REG_PC], 0, "critical trap existing zero-PC sentinel")
        check(list(ref.regs())[:32], fixture.before, "critical trap preserves all GPRs")
        fixture.observe()
    else:
        # The first actual DASICS trap opens an M handler with MDT set. A
        # subsequent M ECALL is diverted to RNMI, leaving the prior reason.
        fixture = Fixture(ref, instruction, gprs={7: DEST}, handlers={M.MTRAP: M.words(M.ECALL)})
        fixture.reject(24, DEST, 4)
        check((ref.csrs()[0x300] >> 42) & 1, 1, "first trap sets MDT")
        ref.step(M.MTRAP, retired=False)
        check(ref.csrs()[0x742], 11, "MDT routes second trap to mncause")
        check(ref.csrs()[0x741], M.MTRAP, "RNMI records the second source PC")
        check(ref.csrs()[0x744] & 8, 0, "RNMI delivery clears NMIE")
        check(ref.csrs()[0x342], 24, "RNMI leaves first ordinary mcause intact")
        check(ref.regs()[M.REG_PC], M.MTRAP, "RNMI handler target")
        fixture.observe()
    return "EXPECTED_REJECTION"


def cases(enabled):
    result = []
    common = ["source=" + context for context in M.UIT.CONTEXTS]
    common += ["untrusted", "disabled", "other-enable", "close", "untrusted-close", "trusted-target"]
    common += ["stateen=" + a + "," + b for a in "01" for b in "01"]
    for kind, offsets in (("j", (-4194304, -2097152, -1048576, -4096, -2, 0, 2, 4096,
                                 1048576, 2097152, 4194302)), ("jr", (-2048, -1, 0, 1, 2047))):
        result += [f"call:{kind}:{scenario}" for scenario in common + [f"imm={n}" for n in offsets]]
    result += ["call:jr:rd=" + str(rd) for rd in (0, 1, 7, 31)]
    kinds = ("jal", "j", "call", "jalr", "jalr-alias", "jr", "ret", "c.j", "c.jr", "c.jalr", "c.jalr-alias")
    for kind in kinds:
        result += [f"jump:{kind}:{scenario}" for scenario in ("deny", "trusted", "disabled", "delegate")]
    result += ["jump:jalr:" + scenario for scenario in POLICY if scenario not in ("deny", "trusted", "disabled", "delegate")]
    result += [f"jump:jalr:bound{slot}={edge}" for slot in range(4)
               for edge in ("lo", "last", "hi", "before", "empty", "reverse", "invalid", "high")]
    result += [f"jump:jalr:special{address}={match}" for address in (ENTRY, RETURN, ACTIVE) for match in ("hit", "high", "odd")]
    result += ["jump:jalr:" + scenario for scenario in
               ("target-trusted-only", "zero-specials", "zero-bound", "high-target")]
    result += [f"branch:{kind}:{scenario}" for kind in (*BRANCHES, "c.beqz", "c.bnez")
               for scenario in ("deny", "not-taken", "allow", "hs-deny")]
    result += ["ecall:" + scenario for scenario in ("HU", "HS", "M", "trusted", "hs-trusted", "disabled",
               "other-enable", "close", "other-close", "hs-close", "stateen", "guest", "guest-disabled", "delegate", "hs-delegate")]
    result += ["fetch:call", "fetch:jump"]
    result += ["branch:beq:guest-not-taken"]
    result += ["invalid:" + str(value) for value in (*range(2, 8), "mret")]
    if enabled:
        result += ["special:" + scenario for scenario in ("sdt-jump", "sdt-ecall", "rnmi-closed", "mdt-rnmi")]
    return result


def run_case(args):
    ref = M.Reference(args.reference, args.state == "on")
    kind, *arguments = args.case.split(":")
    function = {"call": call_case, "jump": jump_case, "branch": branch_case,
                "ecall": ecall_case, "fetch": fetch_case, "invalid": invalid_case, "special": special_case}[kind]
    status = function(ref, *arguments)
    ref.metrics["expected_retired_instructions"] = ref.metrics.pop("retired_instructions")
    print("DASICS_CONTROL_RESULT " + json.dumps({"case": args.case, "status": status,
                                                "metrics": ref.metrics}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--state", choices=("off", "on"), required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--jobs", type=int, choices=range(1, 49), default=4)
    parser.add_argument("--case")
    parser.add_argument("--select", action="append", help="run only an exact named case")
    args = parser.parse_args()
    args.reference = args.reference.resolve(strict=True)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    if args.case:
        try:
            run_case(args)
            return 0
        except Exception as error:
            traceback.print_exc()
            print("DASICS_CONTROL_RESULT " + json.dumps({"case": args.case, "status": "FAIL", "error": str(error)}), flush=True)
            return 1
    if not args.output:
        parser.error("--output is required for a suite")
    selected = args.select or cases(args.state == "on")
    invalid = set(selected) - set(cases(args.state == "on"))
    if invalid:
        parser.error("unknown cases: " + ", ".join(sorted(invalid)))
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("output must be empty to preserve evidence")
    output.mkdir(parents=True, exist_ok=True)
    for name, path in (("driver.py", Path(__file__)), ("fdi-baseline.py", FDI_HELPER),
                       ("m01-baseline.py", Path(M.__file__)), ("uit-baseline.py", M.HELPER)):
        (output / name).write_bytes(path.read_bytes())
    start, start_clock = M.timestamp(), time.monotonic()

    def execute(name):
        command = [sys.executable, str(output / "driver.py"), "--reference", str(args.reference),
                   "--state", args.state, "--case", name]
        stem = name.replace(":", "_")
        log = output / (stem + ".log")
        result = {"case": name, "status": "FAIL", "command": command, "log": str(log), "start_utc": M.timestamp()}
        with log.open("w") as stream:
            try:
                process = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, timeout=60, check=False)
                result["exit_code"] = process.returncode
            except subprocess.TimeoutExpired:
                result.update(exit_code=None, timed_out=True)
        prefix = "DASICS_CONTROL_RESULT "
        markers = [line[len(prefix):] for line in log.read_text(errors="replace").splitlines() if line.startswith(prefix)]
        if markers:
            result.update(json.loads(markers[-1]))
        if result["exit_code"] != 0:
            result["status"] = "FAIL"
        result["end_utc"] = M.timestamp()
        (output / (stem + ".json")).write_text(json.dumps(result, indent=2) + "\n")
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(execute, selected))
    counts = {status: sum(case["status"] == status for case in results) for status in ("PASS", "EXPECTED_REJECTION", "FAIL")}
    summary = {"schema": 1, "kind": "real-dasics-control-model-tests", "state": args.state,
               "reference": str(args.reference), "command": sys.argv, "count": len(results), "counts": counts,
               "start_utc": start, "end_utc": M.timestamp(), "elapsed_seconds": time.monotonic() - start_clock,
               "status": "FAIL" if counts["FAIL"] else "PASS", "cases": results,
               "scope": "A01 real instruction control-flow and trap semantics; no RTL timing or whole-core DiffTest claim."}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({key: value for key, value in summary.items() if key != "cases"}, indent=2))
    return int(bool(counts["FAIL"]))


if __name__ == "__main__":
    sys.exit(main())
