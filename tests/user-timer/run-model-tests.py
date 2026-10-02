#!/usr/bin/env python3
"""Exercise the real reference ABI in isolated processes using encoded RV64 code."""

import argparse
import concurrent.futures
import ctypes as C
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


VERSION = 0x00010000
FEATURES = 0x3F
BASE = 0x80000000
HANDLER = BASE + 0x1000
MTRAP = BASE + 0x2000
STRAP = BASE + 0x3000
DATA = BASE + 0x4000
UART_TX = 0x40600004
MASK64 = (1 << 64) - 1
# RV64 + FP + H + VLEN128 + SDTRIG legacy prefix, checked by negotiated size.
REG_MODE, REG_PC, REG_V = 64, 82, 83
E = dict(ABI=-1, FEATURE=-2, STATE=-3, EPOCH=-4, ORDER=-5, ID=-6,
         PC=-7, INSTRUCTION=-8, CSR=-9, SAMPLE_MISSING=-10,
         SAMPLE_UNEXPECTED=-11, SAMPLE_DUPLICATE=-12, PAYLOAD=-13,
         CONTEXT=-14, OVERFLOW=-15, UNSUPPORTED=-16, EXECUTION=-17)
BANK = {0x000: ("ustatus", 0x11), 0x004: ("uie", 0x10),
        0x005: ("utvec", MASK64 ^ 3), 0x040: ("uscratch", MASK64),
        0x041: ("uepc", MASK64 ^ 1), 0x042: ("ucause", MASK64),
        0x043: ("utval", MASK64)}
ALL_CSRS = tuple(BANK) + (0x044, 0x800)
CONTEXTS = {"M": (3, 0), "HS": (1, 0), "HU": (0, 0),
            "VS": (1, 1), "VU": (0, 1)}


def fields(names, ctype):
    return [(name, ctype) for name in names.split()]


class Caps(C.Structure):
    _fields_ = (fields("version bytes", C.c_uint32)
                + fields("enabled_features supported_features", C.c_uint64)
                + fields("xlen vlen legacy_regcpy_bytes legacy_csrcpy_bytes "
                         "legacy_regcpy_arity max_harts exec_request_bytes "
                         "event_request_bytes state_bytes exec_result_bytes", C.c_uint32))


class Init(C.Structure):
    _fields_ = (fields("version bytes hart required_features", C.c_uint32)
                + fields("epoch reserved", C.c_uint64))


class Request(C.Structure):
    _fields_ = (fields("version bytes hart kind", C.c_uint32)
                + fields("epoch transaction_uid control_seq diagnostic_pc", C.c_uint64)
                + [("instruction", C.c_uint32), ("csr", C.c_uint16),
                   ("funct3", C.c_uint8), ("sample_kind", C.c_uint8),
                   ("sample_payload", C.c_uint64)])


class Result(C.Structure):
    _fields_ = (fields("version bytes hart reserved", C.c_uint32)
                + fields("epoch transaction_uid control_seq", C.c_uint64)
                + fields("outcome exception_cause sample_consumed csr_write_valid", C.c_uint32)
                + fields("csr_write_value", C.c_uint64))


class Event(C.Structure):
    _fields_ = (fields("version bytes hart event_kind", C.c_uint32)
                + fields("epoch event_uid control_seq boundary_pc diagnostic_target "
                         "prior_instruction_count", C.c_uint64))


class State(C.Structure):
    _fields_ = (fields("version bytes hart flags", C.c_uint32)
                + fields("epoch last_control_seq ustatus uie utvec uscratch uepc "
                         "ucause utval pc mode", C.c_uint64)
                + fields("v in_handler", C.c_uint32))


class Tx(C.Structure):
    _fields_ = (fields("version bytes hart reserved", C.c_uint32)
                + fields("epoch tx_seq pc address data", C.c_uint64)
                + fields("len reserved2", C.c_uint32))


def check(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: actual={actual!r}, expected={expected!r}")


def layout_checks():
    for cls, size in ((Caps, 64), (Init, 32), (Request, 64), (Result, 64),
                      (Event, 64), (State, 112), (Tx, 64)):
        check(C.sizeof(cls), size, cls.__name__ + " size")
        check(C.alignment(cls), 8, cls.__name__ + " alignment")
    for cls, field, offset in ((Caps, "enabled_features", 8), (Request, "epoch", 16),
                               (Request, "instruction", 48), (Request, "sample_payload", 56),
                               (Result, "outcome", 40), (Event, "boundary_pc", 40),
                               (State, "ustatus", 32), (State, "pc", 88),
                               (State, "in_handler", 108), (Tx, "data", 48)):
        check(getattr(cls, field).offset, offset, cls.__name__ + "." + field)


def csr_insn(csr, funct3=2, rd=10, source=0):
    return csr << 20 | source << 15 | funct3 << 12 | rd << 7 | 0x73


def addi(rd, rs, value):
    return (value & 0xFFF) << 20 | rs << 15 | rd << 7 | 0x13


def store_insn(source, address, offset=0, width=3):
    value = offset & 0xFFF
    return (value >> 5) << 25 | source << 20 | address << 15 | width << 12 | (value & 31) << 7 | 0x23


def jal(offset, rd=0):
    value = offset & 0x1FFFFF
    return (((value >> 20) & 1) << 31 | ((value >> 1) & 0x3FF) << 21
            | ((value >> 11) & 1) << 20 | ((value >> 12) & 0xFF) << 12 | rd << 7 | 0x6F)


def beq(rs1, rs2, offset):
    value = offset & 0x1FFF
    return (((value >> 12) & 1) << 31 | ((value >> 5) & 63) << 25
            | rs2 << 20 | rs1 << 15 | ((value >> 1) & 15) << 8
            | ((value >> 11) & 1) << 7 | 0x63)


def words(*instructions):
    return struct.pack("<" + "I" * len(instructions), *instructions)


class Reference:
    """Legacy TO_REF calls are restricted to initial fixture construction."""

    def __init__(self, path, enabled=True):
        layout_checks()
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
        self.caps = self.output("query_caps", Caps)
        for field, expected in (("version", VERSION), ("bytes", 64), ("xlen", 64),
                                 ("vlen", 128), ("legacy_regcpy_bytes", 1400),
                                 ("legacy_csrcpy_bytes", 32768), ("legacy_regcpy_arity", 2),
                                 ("max_harts", 1), ("exec_request_bytes", 64),
                                 ("event_request_bytes", 64), ("state_bytes", 112),
                                 ("exec_result_bytes", 64),
                                 ("enabled_features", FEATURES if enabled else 0x20)):
            check(getattr(self.caps, field), expected, "caps." + field)
        check(self.caps.supported_features & FEATURES, FEATURES, "supported features")
        self.lib.difftest_set_ramsize(16 << 20)
        self.lib.difftest_init()
        self.enabled = enabled
        self.started = False
        self.epoch = 0x106
        self.seq = 0
        self.uid = 0
        self.event_uid = 0
        self.count = 0
        self.metrics = {"controlled_execution_calls": 0, "normal_execution_calls": 0,
                        "retired_instructions": 0,
                        "isa_exceptions": 0, "samples": 0, "hu_events": 0,
                        "uret": 0, "protocol_rejections": 0, "tx_records": 0,
                        "runtime_state_imports": 0}

    def output(self, name, cls):
        # The guard follows the exact public object size, so over-copies fail.
        buffer = (C.c_uint8 * (C.sizeof(cls) + 32))()
        C.memset(buffer, 0xA5, C.sizeof(buffer))
        check(getattr(self.lib, "difftest_uit_" + name)(buffer, C.sizeof(cls)), 0, name)
        check(bytes(buffer)[C.sizeof(cls):], b"\xA5" * 32, name + " output guard")
        return cls.from_buffer_copy(buffer)

    def legacy(self, name, size):
        buffer = (C.c_uint8 * (size + 32))()
        C.memset(buffer, 0xA5, len(buffer))
        getattr(self.lib, "difftest_" + name)(buffer, False)
        check(bytes(buffer)[size:], b"\xA5" * 32, name + " output guard")
        return (C.c_uint64 * (size // 8)).from_buffer_copy(buffer)

    def regs(self):
        return self.legacy("regcpy", 1400)

    def csrs(self):
        return self.legacy("csrcpy", 32768)

    def state(self):
        state = self.output("get_state", State)
        for name, value in (("version", VERSION), ("bytes", 112), ("hart", 0),
                            ("flags", 0), ("epoch", self.epoch), ("last_control_seq", self.seq)):
            check(getattr(state, name), value, "state." + name)
        return state

    def setup(self, code, pc=BASE, mode=3, virtual=0, mc=1, sc=1,
              gprs=None, csrs=None, start=True, extra_code=None):
        if self.started:
            raise AssertionError("fixture initialization cannot overwrite runtime state")
        regs = self.regs()
        regs[REG_MODE] = mode
        regs[65] = 0
        regs[67] = BASE
        regs[68] = BASE
        regs[71] = MTRAP
        regs[72] = STRAP
        regs[75] = 0
        regs[76] = 0
        regs[77] = 0
        regs[80] = 0
        regs[81] = 0
        regs[REG_PC] = pc
        regs[REG_V] = virtual
        for register, value in (gprs or {}).items():
            regs[register] = value & MASK64
        self.lib.difftest_regcpy(regs, True)
        bank = self.csrs()
        bank[0x30C] = (bank[0x30C] & ~1) | mc
        bank[0x10C] = (bank[0x10C] & ~1) | sc
        bank[0x3A0] = 0x1F
        bank[0x3B0] = (1 << 46) - 1
        for address, value in (csrs or {}).items():
            if address in ALL_CSRS:
                raise AssertionError("user bank values must come from real instructions")
            bank[address] = value & MASK64
        self.lib.difftest_csrcpy(bank, True)
        check(bytes(self.csrs()), bytes(bank), "initial full CSR copy round trip")
        mirrored = self.regs()
        self.lib.difftest_regcpy(mirrored, True)
        check(bytes(self.regs()), bytes(mirrored), "initial full register copy round trip")
        self.write_memory(pc, code)
        for address, content in (extra_code or {}).items():
            self.write_memory(address, content)
        if start:
            self.start()

    def start(self):
        init = Init(VERSION, 32, 0, self.caps.enabled_features, self.epoch, 0)
        check(self.lib.difftest_uit_init(C.byref(init), 32), 0, "init")
        self.started = True
        state = self.state()
        for name, _ in BANK.values():
            check(getattr(state, name), 0, "reset " + name)
        check(state.in_handler, 0, "reset handler")

    def write_memory(self, address, content):
        if self.started:
            raise AssertionError("code/data imports are restricted to fixture setup")
        buffer = C.create_string_buffer(content)
        self.lib.difftest_memcpy(address, buffer, len(content), True)

    def read_memory(self, address, size):
        buffer = C.create_string_buffer(size)
        self.lib.difftest_memcpy(address, buffer, size, False)
        return buffer.raw

    def normal(self, count=1, retired=True):
        for _ in range(count):
            self.lib.difftest_exec(1)
            self.count += int(retired)
            self.metrics["normal_execution_calls"] += 1
            self.metrics["retired_instructions"] += int(retired)

    def request(self, instruction, sample_kind=0, payload=0):
        return Request(VERSION, 64, 0, 2 if instruction == 0x00200073 else 1,
                       self.epoch, self.uid + 1, self.seq + 1, self.regs()[REG_PC],
                       instruction, 0xFFFF if instruction == 0x00200073 else instruction >> 20,
                       (instruction >> 12) & 7, sample_kind, payload)

    def execute(self, instruction, sample_kind=0, payload=0, exception=False):
        request = self.request(instruction, sample_kind, payload)
        result = self.call_exec(request)
        check(result.outcome, int(exception), "ISA outcome")
        check(result.exception_cause, 2 if exception else 0, "ISA exception cause")
        check(result.sample_consumed, int(bool(sample_kind) and not exception), "sample consumed")
        self.seq, self.uid = request.control_seq, request.transaction_uid
        self.count += int(not exception)
        self.metrics["controlled_execution_calls"] += 1
        self.metrics["retired_instructions"] += int(not exception)
        self.metrics["samples"] += result.sample_consumed
        self.metrics["isa_exceptions"] += int(exception)
        self.metrics["uret"] += int(instruction == 0x00200073 and not exception)
        return result

    def call_exec(self, request, expected=0, request_bytes=64, result_bytes=64):
        guarded = (C.c_uint8 * 96)()
        C.memset(guarded, 0xA5, 96)
        status = self.lib.difftest_uit_exec(C.byref(request), request_bytes, guarded, result_bytes)
        check(status, expected, "exec status")
        check(bytes(guarded)[64:], b"\xA5" * 32, "exec output guard")
        if expected:
            self.metrics["protocol_rejections"] += 1
        result = Result.from_buffer_copy(guarded)
        if not expected:
            for field, value in (("version", VERSION), ("bytes", 64), ("hart", 0),
                                  ("reserved", 0), ("epoch", request.epoch),
                                  ("transaction_uid", request.transaction_uid),
                                  ("control_seq", request.control_seq)):
                check(getattr(result, field), value, "result." + field)
        return result

    def event(self):
        state = self.state()
        return Event(VERSION, 64, 0, 1, self.epoch, self.event_uid + 1,
                     self.seq + 1, state.pc, state.utvec, self.count)

    def raise_event(self, event=None, expected=0):
        event = event or self.event()
        check(self.lib.difftest_uit_raise_event(C.byref(event), 64), expected, "event status")
        if expected:
            self.metrics["protocol_rejections"] += 1
        else:
            self.seq, self.event_uid = event.control_seq, event.event_uid
            self.metrics["hu_events"] += 1


def expect_illegal(ref):
    registers = ref.regs()
    check(registers[64], 3, "illegal trap mode")
    check(registers[73], 2, "illegal trap mcause")
    check(registers[REG_PC], MTRAP, "illegal trap target")


def test_bank(ref, address):
    name, mask = BANK[address]
    operations = [(1, 10, 5), (2, 10, 7), (3, 10, 7), (5, 10, 31),
                  (6, 10, 16), (7, 10, 1), (2, 0, 0), (3, 0, 0),
                  (2, 10, 6), (3, 10, 6), (1, 0, 6), (5, 0, 0),
                  (6, 0, 0), (7, 0, 0)]
    code = [csr_insn(address, *op) for op in operations]
    source_values = {0: 0, 5: 0xFEDCBA987654321F, 6: 0, 7: 0x1234567800000011}
    ref.setup(words(*code), gprs=source_values)
    before = ref.csrs()
    old = 0
    for instruction, (funct3, rd, source) in zip(code, operations):
        value = source if funct3 >= 5 else source_values[source]
        write = funct3 in (1, 5) or source != 0
        result = ref.execute(instruction)
        if rd:
            check(ref.regs()[rd], old, "bank old value")
        if write:
            calculated = value if funct3 in (1, 5) else old | value if funct3 in (2, 6) else old & ~value
            old = calculated & mask
            check(result.csr_write_value, calculated & MASK64, "bank independent write request")
        check(result.csr_write_valid, int(write), "bank write enable")
        check(getattr(ref.state(), name), old, name + " architectural write")
        check(ref.regs()[0], 0, "x0")
    after = ref.csrs()
    for csr in (0x100, 0x104, 0x105, 0x140, 0x141, 0x142, 0x143,
                0x300, 0x304, 0x305, 0x340, 0x341, 0x342, 0x343):
        check(after[csr], before[csr], "independent M/S bank " + hex(csr))


def test_permission(ref, address, context, mc, sc, supplied=False, write=False):
    mode, virtual = CONTEXTS[context]
    legal = ref.enabled and not virtual and (mode == 3 or mc and (mode == 1 or sc))
    instruction = csr_insn(address, 1, 0, 5) if write else csr_insn(address)
    sample = ((1 if address == 0x800 else 2 if address == 0x044 else 0)
              if not write and (legal or supplied) else 0)
    write_value = 0xFEDCBA987654321F
    ref.setup(words(instruction), mode=mode, virtual=virtual, mc=mc, sc=sc,
              gprs={5: write_value, 10: 0xA55A})
    result = ref.execute(instruction, sample, 1 if sample else 0, exception=not legal)
    if not legal:
        expect_illegal(ref)
    else:
        if write:
            check(result.csr_write_valid, 1, "permitted write enable")
            check(result.csr_write_value, write_value, "permitted write value")
            if address in BANK:
                name, mask = BANK[address]
                check(getattr(ref.state(), name), write_value & mask, "permitted bank write")
        else:
            check(ref.regs()[10], 1 if address == 0x800 else 16 if address == 0x044 else 0,
                  "permitted read rd")
        check(ref.regs()[REG_PC], BASE + 4, "permitted read PC")


def test_sample(ref, address, funct3, rd, source_case, payload):
    source, source_value = {"x0": (0, 0), "zero": (6, 0), "value": (5, 0x123)}[source_case]
    if funct3 >= 5:
        source = {"x0": 0, "zero": 1, "value": 31}[source_case]
        source_value = source
    instruction = csr_insn(address, funct3, rd, source)
    required = not (funct3 in (1, 5) and rd == 0)
    kind = (1 if address == 0x800 else 2) if required else 0
    old = payload if address == 0x800 else payload << 4
    write = funct3 in (1, 5) or source != 0
    value = source_value if funct3 in (1, 5) else old | source_value if funct3 in (2, 6) else old & ~source_value
    ref.setup(words(instruction), gprs={5: 0x123, 6: 0})
    result = ref.execute(instruction, kind, payload if required else 0)
    check(result.csr_write_valid, int(write), "controlled write request")
    if write:
        check(result.csr_write_value, value & MASK64, "independent RMW write value")
    if rd:
        check(ref.regs()[rd], old, "sample rd")
    check(ref.regs()[0], 0, "sample x0")


def test_sample_program(ref):
    instruction = csr_insn(0x800)
    ref.setup(words(instruction, addi(11, 10, 3), beq(10, 21, 8),
                    addi(12, 0, 99), store_insn(11, 20), jal(-20)),
              gprs={20: DATA, 21: 5})
    for sample, result, branch_marker in ((5, 8, 0), (7, 10, 99)):
        check(ref.regs()[REG_PC], BASE, "same dynamic read PC")
        ref.execute(instruction, 1, sample)
        ref.normal(2)
        if sample != 5:
            ref.normal()
        ref.normal()
        check(struct.unpack("<Q", ref.read_memory(DATA, 8))[0], result, "sample dependent store")
        check(ref.regs()[12], branch_marker, "sample dependent branch")
        ref.normal()


def prepare_entry(ref, context="HU", mc=1, sc=1, status=1, enable=0x10,
                  upper=None, old_pending=None, return_upie_zero=False, return_epc_write=False,
                  before_exception=None, nmie=1):
    setup = [csr_insn(0x000, 1, 0, 5), csr_insn(0x004, 1, 0, 6),
             csr_insn(0x005, 1, 0, 7), csr_insn(0x040, 1, 0, 8),
             csr_insn(0x041, 1, 0, 9), csr_insn(0x042, 1, 0, 10),
             csr_insn(0x043, 1, 0, 11)]
    boundary = BASE + 0x102
    mode, virtual = CONTEXTS[context]
    csrs = {0x300: mode << 11 | virtual << 39, 0x341: boundary, 0x744: nmie << 3}
    extra = {boundary: b"\x01\x00\x01\x00" + words(addi(12, 12, 1)),
             HANDLER: words(0x00200073)}
    if old_pending is not None:
        extra[boundary] = words(csr_insn(0x044)) + extra[boundary]
    if return_upie_zero:
        extra[HANDLER] = words(csr_insn(0x000, 1, 0, 0), 0x00200073)
    if return_epc_write:
        extra[HANDLER] = words(csr_insn(0x041, 1, 0, 9), 0x00200073)
    if before_exception:
        extra[boundary] = words(0x00200073 if before_exception == "uret" else 0x00000073) + extra[boundary]
        extra[MTRAP] = words(csr_insn(0x341, 2, 15, 0), addi(15, 15, 4),
                             csr_insn(0x341, 1, 0, 15), 0x30200073)
    if upper:
        extra[HANDLER] = words(0x00000073, csr_insn(0x000), 0x00200073)
        is_supervisor = upper == "HS"
        trap_csr = 0x141 if is_supervisor else 0x341
        revoke_csr = 0x10C if is_supervisor else 0x30C
        extra[STRAP if is_supervisor else MTRAP] = words(
            csr_insn(revoke_csr, 7, 0, 1), csr_insn(trap_csr, 2, 15, 0),
            addi(15, 15, 4), csr_insn(trap_csr, 1, 0, 15),
            0x10200073 if is_supervisor else 0x30200073)
        if is_supervisor:
            csrs[0x302] = (1 << 8) | (1 << 2)
    ref.setup(words(*setup, 0x30200073), mc=mc, sc=sc,
              gprs={5: status, 6: enable, 7: HANDLER | 3, 8: 0x123456789ABCDEF0,
                    9: DATA | 3, 10: 0x42, 11: 0x55},
              csrs=csrs, extra_code=extra)
    for instruction in setup:
        ref.execute(instruction)
    ref.normal()
    check(ref.state().pc, boundary, "MRET boundary with bit1")
    check(ref.state().mode, mode, "MRET mode")
    check(ref.state().v, virtual, "MRET virtualization")
    if old_pending is not None:
        ref.execute(csr_insn(0x044), 2, old_pending)
        check(ref.regs()[10], old_pending << 4, "old pending sample")
        boundary += 4
    return boundary


def test_entry(ref, upper=None, old_pending=None):
    boundary = prepare_entry(ref, upper=upper, old_pending=old_pending)
    for index in range(2 if upper is None else 1):
        ref.raise_event()
        state = ref.state()
        for name, expected in (("pc", HANDLER), ("uepc", boundary),
                                ("ucause", 0x8000000000000004), ("utval", 0),
                                ("ustatus", 0x10), ("mode", 0), ("v", 0),
                                ("in_handler", 1), ("uscratch", 0x123456789ABCDEF0)):
            check(getattr(state, name), expected, "entry." + name)
        if upper:
            ref.normal(retired=False)
            check(ref.regs()[74 if upper == "HS" else 73], 8, "upper ECALL cause")
            ref.metrics["isa_exceptions"] += 1
            state = ref.state()
            check(state.in_handler, 1, "upper trap retains handler")
            check(state.pc, STRAP if upper == "HS" else MTRAP, "upper trap target")
            ref.normal(5)
            check(ref.state().in_handler, 1, "upper return retains handler")
            check(ref.state().pc, HANDLER + 4, "upper return PC")
            ref.execute(csr_insn(0x000), exception=True)
            check(ref.state().in_handler, 1, "revoked CSR trap retains handler")
            ref.normal(5)
            check(ref.state().pc, HANDLER + 8, "resume at real URET")
        ref.execute(0x00200073)
        state = ref.state()
        for name, expected in (("pc", boundary), ("uepc", boundary), ("ustatus", 0x11),
                                ("in_handler", 0), ("mode", 0), ("v", 0)):
            check(getattr(state, name), expected, "return." + name)
        if index == 0 and upper is None:
            ref.normal(2)
            boundary += 4
    if upper:
        check(ref.csrs()[0x10C if upper == "HS" else 0x30C] & 1, 0,
              "URET does not restore CSR access")


def test_entry_denied(ref, reason):
    arguments = {"mode-M": {"context": "M"}, "mode-HS": {"context": "HS"},
                 "mode-VS": {"context": "VS"}, "mode-VU": {"context": "VU"},
                 "mc": {"mc": 0}, "sc": {"sc": 0},
                 "uie": {"status": 0x10}, "utie": {"enable": 0}, "nmie": {"nmie": 0}}
    prepare_entry(ref, **arguments.get(reason, {}))
    if reason == "nested":
        ref.raise_event()
    before = bytes(ref.state())
    ref.raise_event(expected=E["CONTEXT"])
    check(bytes(ref.state()), before, "rejected event leaves architecture unchanged")


def test_uret_illegal(ref, context):
    mode, virtual = CONTEXTS[context]
    ref.setup(words(0x00200073), mode=mode, virtual=virtual)
    ref.execute(0x00200073, exception=True)
    expect_illegal(ref)


def test_uret_dispatch(ref, context):
    mode, virtual = CONTEXTS[context]
    ref.setup(words(0x00200073), mode=mode, virtual=virtual)
    before_count = ref.lib.get_abs_instr_count()
    before_sequence = ref.state().last_control_seq
    ref.normal(retired=False)
    check(ref.lib.get_abs_instr_count(), before_count, "raw URET does not retire")
    ref.metrics["native_retirement_checks"] = 1
    ref.metrics["native_uret_retirement_delta"] = ref.lib.get_abs_instr_count() - before_count
    if ref.enabled:
        state = State()
        check(ref.lib.difftest_uit_get_state(C.byref(state), C.sizeof(state)),
              E["STATE"], "enabled raw URET requires its descriptor")
        check(ref.regs()[REG_PC], BASE, "descriptor rejection precedes PC update")
        check(ref.regs()[73], 0, "descriptor rejection is not an ISA exception")
        ref.metrics["protocol_rejections"] += 1
    else:
        expect_illegal(ref)
        check(ref.state().last_control_seq, before_sequence, "off raw URET does not consume control sequence")
        ref.metrics["isa_exceptions"] += 1


def test_protocol(ref, name):
    instruction = csr_insn(0x800)
    ref.setup(words(instruction, instruction))
    request = ref.request(instruction, 1, 7)
    mutations = {"version": ("version", VERSION + 1, "ABI"),
                 "header-size": ("bytes", 63, "ABI"),
                 "hart": ("hart", 1, "ID"),
                 "epoch": ("epoch", ref.epoch - 1, "EPOCH"),
                 "order": ("control_seq", 2, "ORDER"),
                 "id-zero": ("transaction_uid", 0, "ID"),
                 "pc": ("diagnostic_pc", BASE + 4, "PC"),
                 "instruction": ("instruction", csr_insn(0x800, 2, 11), "INSTRUCTION"),
                 "csr": ("csr", 0x044, "CSR"),
                 "funct3": ("funct3", 3, "CSR"),
                 "kind": ("kind", 9, "INSTRUCTION"),
                 "sample-kind": ("sample_kind", 3, "PAYLOAD")}
    if name in mutations:
        field, value, expected = mutations[name]
        setattr(request, field, value)
        ref.call_exec(request, E[expected])
    elif name in ("request-size", "result-size"):
        ref.call_exec(request, E["ABI"], request_bytes=63 if name == "request-size" else 64,
                      result_bytes=63 if name == "result-size" else 64)
    elif name == "missing":
        request.sample_kind = request.sample_payload = 0
        ref.call_exec(request, E["SAMPLE_MISSING"])
    elif name == "missing-after-sample":
        ref.execute(instruction, 1, 7)
        ref.call_exec(ref.request(instruction), E["SAMPLE_MISSING"])
    elif name == "wrong-sample-csr":
        request.sample_kind = 2
        request.sample_payload = 1
        ref.call_exec(request, E["SAMPLE_UNEXPECTED"])
    elif name == "duplicate":
        ref.execute(instruction, 1, 7)
        request = ref.request(instruction, 1, 9)
        request.transaction_uid = ref.uid
        ref.call_exec(request, E["ID"])
    elif name == "sequence-replay":
        ref.execute(instruction, 1, 7)
        ref.call_exec(request, E["ORDER"])
    else:
        raise AssertionError(name)


def test_unexpected(ref, name):
    instruction = csr_insn(0x000 if name == "ordinary" else 0x800, 1, 0, 0)
    ref.setup(words(instruction))
    request = ref.request(instruction, 1, 5)
    ref.call_exec(request, E["SAMPLE_UNEXPECTED"])


def test_pending_payload(ref):
    instruction = csr_insn(0x044)
    ref.setup(words(instruction))
    ref.call_exec(ref.request(instruction, 2, 2), E["PAYLOAD"])


def test_event_protocol(ref, name):
    prepare_entry(ref)
    if name == "duplicate":
        ref.raise_event()
        ref.execute(0x00200073)
    event = ref.event()
    mutations = {"pc": ("boundary_pc", event.boundary_pc + 2, "PC"),
                 "target": ("diagnostic_target", event.diagnostic_target + 4, "PC"),
                 "count": ("prior_instruction_count", event.prior_instruction_count + 1, "ORDER"),
                 "type": ("event_kind", 2, "UNSUPPORTED"),
                 "epoch": ("epoch", event.epoch - 1, "EPOCH"),
                 "id": ("event_uid", 0, "ID"),
                 "duplicate": ("event_uid", ref.event_uid, "ID"),
                 "version": ("version", VERSION + 1, "ABI"),
                 "header-size": ("bytes", 63, "ABI"),
                 "hart": ("hart", 1, "ID"),
                 "order": ("control_seq", event.control_seq + 1, "ORDER")}
    field, value, expected = mutations[name]
    setattr(event, field, value)
    before = bytes(ref.state())
    ref.raise_event(event, E[expected])
    check(bytes(ref.state()), before, "invalid event leaves architecture unchanged")


def test_init(ref, name):
    ref.setup(words(addi(10, 0, 1)), start=False)
    init = Init(VERSION, 32, 0, FEATURES, ref.epoch, 0)
    mutations = {"feature": ("required_features", FEATURES | 0x80, "FEATURE"),
                 "reserved": ("reserved", 1, "ABI"),
                 "version": ("version", VERSION + 1, "ABI"),
                 "hart": ("hart", 1, "ID"),
                 "epoch-zero": ("epoch", 0, "EPOCH")}
    if name in mutations:
        field, value, expected = mutations[name]
        setattr(init, field, value)
    elif name == "late":
        ref.normal()
        expected = "STATE"
    elif name == "repeat":
        ref.start()
        expected = "STATE"
    else:
        raise AssertionError(name)
    check(ref.lib.difftest_uit_init(C.byref(init), 32), E[expected], "init rejection")
    ref.metrics["protocol_rejections"] += 1


def test_abi(ref):
    ref.setup(words(addi(10, 0, 7)))
    check(ref.csrs()[0x301] & (1 << 13), 0, "enabled misa.N remains clear")
    check(bool(ref.csrs()[0x301] & (1 << 23)), True, "enabled misa.X advertises nonstandard extension")
    for name, cls in (("query_caps", Caps), ("get_state", State), ("read_tx", Tx)):
        value = cls()
        for size in (C.sizeof(cls) - 1, C.sizeof(cls) + 1):
            check(getattr(ref.lib, "difftest_uit_" + name)(C.byref(value), size),
                  E["ABI"], name + " rejects nonexact size")
            ref.metrics["protocol_rejections"] += 1
    init, event = Init(), Event()
    check(ref.lib.difftest_uit_init(C.byref(init), 31), E["ABI"], "init rejects short input")
    check(ref.lib.difftest_uit_raise_event(C.byref(event), 63), E["ABI"], "event rejects short input")
    ref.metrics["protocol_rejections"] += 2
    ref.normal()
    check(ref.regs()[10], 7, "normal execution remains available")


def test_tx(ref):
    ref.setup(words(store_insn(5, 6, width=0), addi(5, 5, 1), store_insn(5, 6, width=0)),
              gprs={5: 65, 6: UART_TX})
    ref.normal(3)
    for index, pc in enumerate((BASE, BASE + 8), 1):
        tx = ref.output("read_tx", Tx)
        for name, value in (("version", VERSION), ("bytes", 64), ("hart", 0),
                            ("reserved", 0), ("epoch", ref.epoch), ("tx_seq", index),
                            ("pc", pc), ("address", UART_TX), ("data", 64 + index),
                            ("len", 1), ("reserved2", 0)):
            check(getattr(tx, name), value, "TX." + name)
        ref.metrics["tx_records"] += 1
    tx = Tx()
    check(ref.lib.difftest_uit_read_tx(C.byref(tx), 64), 1, "TX queue empty")


def test_tx_rejected(ref, name):
    address = UART_TX - 4 if name == "address" else UART_TX
    instruction = (6 << 15 | 5 << 7 | 0x03) if name == "read" else store_insn(5, 6, width=2 if name == "width" else 0)
    ref.setup(words(instruction), gprs={5: 65, 6: address})
    ref.normal(retired=False)
    tx = Tx()
    check(ref.lib.difftest_uit_read_tx(C.byref(tx), 64), E["UNSUPPORTED"], "MMIO rejection")
    ref.metrics["protocol_rejections"] += 1


def test_disabled(ref):
    ref.setup(words(addi(10, 0, 7)), start=False)
    init = Init(VERSION, 32, 0, FEATURES, ref.epoch, 0)
    check(ref.lib.difftest_uit_init(C.byref(init), 32), E["FEATURE"], "off init feature rejection")
    ref.start()
    ref.normal()
    check(ref.regs()[10], 7, "off legacy execution")
    check(ref.csrs()[0x301] & (1 << 13), 0, "misa.N remains clear")
    check(ref.csrs()[0x301] & (1 << 23), 0, "off misa.X remains clear")
    ref.metrics["protocol_rejections"] += 1


def test_return_upie_zero(ref):
    boundary = prepare_entry(ref, return_upie_zero=True)
    ref.raise_event()
    ref.execute(csr_insn(0x000, 1, 0, 0))
    check(ref.state().ustatus, 0, "handler independently clears UPIE")
    ref.execute(0x00200073)
    state = ref.state()
    check(state.ustatus, 0x10, "URET copies zero UPIE to UIE and sets UPIE")
    check(state.pc, boundary, "URET with zero UPIE target")
    check(state.in_handler, 0, "URET with zero UPIE clears handler")


def test_return_epc_write(ref):
    prepare_entry(ref, return_epc_write=True)
    ref.raise_event()
    ref.execute(csr_insn(0x041, 1, 0, 9))
    check(ref.state().uepc, DATA + 2, "handler sets independent UEPC with bit1")
    ref.execute(0x00200073)
    check(ref.state().pc, DATA + 2, "URET uses current UEPC without adding 2 or 4")


def test_exception_before_hu(ref, name):
    boundary = prepare_entry(ref, before_exception=name)
    if name == "uret":
        ref.execute(0x00200073, exception=True)
    else:
        ref.normal(retired=False)
        check(ref.regs()[73], 8, "HU ECALL cause")
        ref.metrics["isa_exceptions"] += 1
    check(ref.regs()[REG_PC], MTRAP, "fault before HU enters M handler")
    ref.normal(4)
    check(ref.state().pc, boundary + 4, "fault handler advances own MEPC")
    ref.raise_event()
    check(ref.state().uepc, boundary + 4, "HU boundary excludes nonretiring fault")
    ref.execute(0x00200073)
    check(ref.state().pc, boundary + 4, "HU returns after recovered fault")


def test_legacy_transport(ref):
    original_registers = ref.regs()
    registers = type(original_registers).from_buffer_copy(original_registers)
    positions = list(range(1, 64)) + [99] + list(range(100, 164)) + [174]
    for position in positions:
        registers[position] = 0xA53C790E2168B4D0 ^ position
    ref.lib.difftest_regcpy(registers, True)
    observed = ref.regs()
    for position in positions:
        check(observed[position], registers[position], "legacy register sentinel " + str(position))
    ref.lib.difftest_regcpy(original_registers, True)
    original_csrs = ref.csrs()
    csrs = type(original_csrs).from_buffer_copy(original_csrs)
    # The final two unimplemented slots prove that the complete CSR array is copied.
    for position in (0xFFE, 0xFFF):
        csrs[position] = 0x971234567890ABCD ^ position
    ref.lib.difftest_csrcpy(csrs, True)
    observed_csrs = ref.csrs()
    for position in (0xFFE, 0xFFF):
        check(observed_csrs[position], csrs[position], "legacy CSR tail sentinel")
    ref.lib.difftest_csrcpy(original_csrs, True)
    ref.setup(words(addi(10, 0, 7)))
    ref.normal()
    check(ref.regs()[10], 7, "legacy ABI fixture retains real execution")


def test_import_rejected(ref, name):
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    ref.setup(words(addi(10, 0, 7)))
    buffer = ref.regs() if name == "regcpy" else ref.csrs()
    print("UIT_EXPECTED_IMPORT_ABORT " + name, flush=True)
    getattr(ref.lib, "difftest_" + name)(buffer, True)
    raise AssertionError("post-init import returned instead of aborting")


def cases(enabled, suite):
    if suite == "uret-dispatch":
        return (["uret-dispatch:" + context for context in CONTEXTS]
                + ["uret-illegal:" + context for context in CONTEXTS])
    if not enabled:
        result = ["disabled", "tx", "legacy-transport"]
        if suite == "all":
            result += ["import-rejected:regcpy", "import-rejected:csrcpy"]
            result += [f"permission:{csr}:{context}:1:1" for csr in ALL_CSRS for context in CONTEXTS]
            result += [f"permission-write:{csr}:{context}:1:1" for csr in ALL_CSRS for context in CONTEXTS]
            result += ["uret-illegal:" + context for context in CONTEXTS]
            result += ["uret-dispatch:" + context for context in CONTEXTS]
        return result
    result = ["abi", "bank:64", "sample-program", "entry", "tx"]
    if suite == "smoke":
        return result
    result += [f"bank:{csr}" for csr in BANK if csr != 64]
    result += [f"permission:{csr}:{context}:{mc}:{sc}"
               for csr in ALL_CSRS for context in CONTEXTS for mc in (0, 1) for sc in (0, 1)]
    result += [f"permission-write:{csr}:{context}:{mc}:{sc}"
               for csr in ALL_CSRS for context in CONTEXTS for mc in (0, 1) for sc in (0, 1)]
    result += [f"denied-sample:{csr}:{context}:0:0" for csr in (0x044, 0x800)
               for context in ("HS", "HU", "VS", "VU")]
    result += [f"sample:{csr}:{funct3}:{rd}:{source}:{payload}"
               for csr in (0x800, 0x044) for funct3 in (1, 2, 3, 5, 6, 7)
               for rd in (0, 10) for source in ("x0", "zero", "value")
               for payload in ((0, 0x123456789ABCDEF0) if csr == 0x800 else (0, 1))]
    result += ["uret-illegal:" + context for context in CONTEXTS]
    result += ["uret-dispatch:" + context for context in CONTEXTS]
    result += ["entry-upper:M", "entry-upper:HS", "entry-old-pending:0", "entry-old-pending:1",
               "return-upie-zero", "return-epc-write", "legacy-transport"]
    result += ["exception-before-hu:uret", "exception-before-hu:ecall"]
    result += ["import-rejected:regcpy", "import-rejected:csrcpy"]
    result += ["entry-denied:" + name for name in
               ("mode-M", "mode-HS", "mode-VS", "mode-VU", "mc", "sc", "uie", "utie", "nested", "nmie")]
    result += ["protocol:" + name for name in
               ("version", "header-size", "hart", "epoch", "order", "id-zero", "pc",
                "instruction", "csr", "funct3", "kind", "sample-kind", "request-size",
                "result-size", "missing", "missing-after-sample", "wrong-sample-csr",
                "duplicate", "sequence-replay")]
    result += ["unexpected:ordinary", "unexpected:purewrite", "pending-payload"]
    result += ["event-protocol:" + name for name in
               ("pc", "target", "count", "type", "epoch", "id", "order", "duplicate", "version", "header-size", "hart")]
    result += ["init:" + name for name in ("feature", "reserved", "version", "hart", "epoch-zero", "late", "repeat")]
    result += ["tx-rejected:" + name for name in ("address", "width", "read")]
    return result


def run_case(args):
    ref = Reference(args.reference, bool(args.expect_enabled))
    pieces = args.case.split(":")
    name, parameters = pieces[0], pieces[1:]
    if name == "abi":
        test_abi(ref)
    elif name == "bank":
        test_bank(ref, int(parameters[0]))
    elif name in ("permission", "permission-write", "denied-sample"):
        csr, context, mc, sc = parameters
        test_permission(ref, int(csr), context, int(mc), int(sc), name == "denied-sample",
                        name == "permission-write")
    elif name == "sample":
        csr, funct3, rd, source, payload = parameters
        test_sample(ref, int(csr), int(funct3), int(rd), source, int(payload))
    elif name == "sample-program":
        test_sample_program(ref)
    elif name in ("entry", "entry-upper"):
        test_entry(ref, parameters[0] if parameters else None)
    elif name == "entry-old-pending":
        test_entry(ref, old_pending=int(parameters[0]))
    elif name == "return-upie-zero":
        test_return_upie_zero(ref)
    elif name == "return-epc-write":
        test_return_epc_write(ref)
    elif name == "exception-before-hu":
        test_exception_before_hu(ref, parameters[0])
    elif name == "legacy-transport":
        test_legacy_transport(ref)
    elif name == "import-rejected":
        test_import_rejected(ref, parameters[0])
    elif name == "entry-denied":
        test_entry_denied(ref, parameters[0])
    elif name == "uret-illegal":
        test_uret_illegal(ref, parameters[0])
    elif name == "uret-dispatch":
        test_uret_dispatch(ref, parameters[0])
    elif name == "protocol":
        test_protocol(ref, parameters[0])
    elif name == "unexpected":
        test_unexpected(ref, parameters[0])
    elif name == "pending-payload":
        test_pending_payload(ref)
    elif name == "event-protocol":
        test_event_protocol(ref, parameters[0])
    elif name == "init":
        test_init(ref, parameters[0])
    elif name == "tx":
        test_tx(ref)
    elif name == "tx-rejected":
        test_tx_rejected(ref, parameters[0])
    elif name == "disabled":
        test_disabled(ref)
    else:
        raise AssertionError("unknown case " + args.case)
    print("UIT_MODEL_RESULT " + json.dumps({"case": args.case, "status": "PASS", "metrics": ref.metrics}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--expect-enabled", type=int, choices=(0, 1), default=1)
    parser.add_argument("--suite", choices=("smoke", "all", "uret-dispatch"), default="all")
    parser.add_argument("--jobs", type=int, default=min(os.cpu_count() or 1, 8))
    parser.add_argument("--case", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.expect_enabled == 0:
        parser.error("legacy UIT-off enabled=0x20 is retired; use tests/dasics/run-model-tests.py for DASICS off; frozen historical drivers retain their original contract")
    args.reference = args.reference.resolve(strict=True)
    if args.case:
        try:
            run_case(args)
            return 0
        except Exception as error:
            traceback.print_exc()
            print("UIT_MODEL_RESULT " + json.dumps({"case": args.case, "status": "FAIL", "error": str(error)}), flush=True)
            return 1
    if not args.output:
        parser.error("--output is required for a suite")
    root = Path(__file__).resolve().parents[4]
    evidence_root = root / "build/user-timer/uit06/controlled-inputs-r01"
    output = args.output.resolve()
    if not output.is_relative_to(evidence_root.resolve()):
        parser.error("output must be inside " + str(evidence_root))
    if output.exists() and any(output.iterdir()):
        parser.error("output must be empty to preserve previous evidence")
    output.mkdir(parents=True, exist_ok=True)
    driver = output / "driver.py"
    driver.write_bytes(Path(__file__).read_bytes())
    selected = cases(bool(args.expect_enabled), args.suite)
    started = time.time()

    def execute(name):
        command = [sys.executable, str(driver), "--reference", str(args.reference),
                   "--expect-enabled", str(args.expect_enabled), "--case", name]
        log = output / (name.replace(":", "_") + ".log")
        before = time.time()
        with log.open("w") as stream:
            try:
                process = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT,
                                         timeout=60, check=False)
                code = process.returncode
            except subprocess.TimeoutExpired:
                code = 124
        result = {"case": name, "status": "FAIL", "exit_code": code,
                  "command": command, "log": str(log), "elapsed_seconds": time.time() - before}
        log_text = log.read_text(errors="replace")
        markers = [line[len("UIT_MODEL_RESULT "):] for line in log_text.splitlines()
                   if line.startswith("UIT_MODEL_RESULT ")]
        if markers:
            result.update(json.loads(markers[-1]))
        if code != 0:
            result["status"] = "FAIL"
        if name.startswith("import-rejected:"):
            operation = name.split(":", 1)[1]
            expected = (code == -signal.SIGABRT
                        and "UIT_EXPECTED_IMPORT_ABORT " + operation in log_text
                        and "uit_check_import" in log_text
                        and "!uit.initialized && !uit.started" in log_text)
            result["status"] = "PASS" if expected else "FAIL"
            result["expected_termination"] = "SIGABRT in uit_check_import after successful fixture setup"
            if expected:
                result["metrics"] = {"forbidden_import_attempts": 1,
                                     "forbidden_import_rejections": 1, "runtime_state_imports": 0}
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = list(pool.map(execute, selected))
    totals = {}
    for result in results:
        for key, value in result.get("metrics", {}).items():
            totals[key] = totals.get(key, 0) + value
    failed = [result["case"] for result in results if result["status"] != "PASS"]
    summary = {"schema": 1, "kind": "real-reference-model-tests", "reference": str(args.reference),
               "driver": str(driver),
               "enabled": bool(args.expect_enabled), "suite": args.suite, "command": sys.argv,
               "elapsed_seconds": time.time() - started, "count": len(results),
               "passed": len(results) - len(failed), "failed": len(failed),
               "status": "FAIL" if failed else "PASS", "metrics": totals, "cases": results,
               "scope": "Real NEMU model and protocol execution; no DUT execution or timer-generation proof."}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({key: value for key, value in summary.items() if key != "cases"}, indent=2))
    for name in failed:
        print("FAIL " + name)
    return int(bool(failed))


if __name__ == "__main__":
    sys.exit(main())
