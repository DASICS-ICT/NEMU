#!/usr/bin/env python3
"""Exercise aligned ordinary scalar DASICS accesses through real RV64 instructions."""

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
import struct
import subprocess
import sys
import time
import traceback


BASELINE = Path(__file__).with_name("m01-baseline.py")
if not BASELINE.exists():
    BASELINE = Path(__file__).with_name("run-model-tests.py")
SPEC = importlib.util.spec_from_file_location("scalar_model_baseline", BASELINE)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
check, words, csr = M.check, M.words, M.csr_insn
BASE, TARGET, DATA, POOL = M.BASE, M.TARGET, M.DATA, M.POOL
STRAP, MASK = M.UIT.STRAP, M.MASK64
FREASON, LIBCFG, LIBLO = 0x8B3, 0x880, 0x890
SENTINEL, STORE_VALUE = 0x0123456789ABCDEF, 0xFEDCBA9876543280
MEM_START = DATA - 16
INITIAL_MEMORY = bytes((0x80 + index * 13) & 0xFF for index in range(160))
FDI_EPOCH = 0x303000001


class FdiInit(C.Structure):
    _fields_ = [(name, C.c_uint32) for name in ("version", "bytes", "hart", "reserved")]
    _fields_ += [("epoch", C.c_uint64), ("required_features", C.c_uint64)]


class FdiState(C.Structure):
    _fields_ = [(name, C.c_uint32) for name in ("version", "bytes", "hart", "phase")]
    _fields_ += [("epoch", C.c_uint64), ("model_pc", C.c_uint64), ("words", C.c_uint64 * 52)]


def fdi_bind(ref):
    for name, args in {
        "capture_reset": [C.c_uint32, C.c_void_p, C.c_uint32],
        "get_state": [C.c_uint32, C.c_void_p, C.c_uint32],
        "init": [C.c_void_p, C.c_uint32],
    }.items():
        function = getattr(ref.lib, "difftest_fdi_" + name)
        function.restype, function.argtypes = C.c_int32, args


def fdi_snapshot(ref, reset=False):
    record = FdiState()
    name = "capture_reset" if reset else "get_state"
    check(getattr(ref.lib, "difftest_fdi_" + name)(0, C.byref(record), C.sizeof(record)),
          0, name + " status")
    check((record.version, record.bytes, record.hart, record.phase, record.epoch),
          (0x10000, 448, 0, 0 if reset else 1, 0 if reset else FDI_EPOCH),
          name + " header")
    check(record.model_pc, ref.regs()[M.REG_PC], name + " model PC")
    return list(record.words)


def load_instruction(width, signed=True, fp=False, offset=0):
    funct3 = {1: 0, 2: 1, 4: 2, 8: 3}[width]
    if not signed and width != 8:
        funct3 += 4
    if fp:
        funct3 = {2: 1, 4: 2, 8: 3}[width]
    return (offset & 0xFFF) << 20 | 9 << 15 | funct3 << 12 | 8 << 7 | (0x07 if fp else 0x03)


def store_instruction(width, fp=False, offset=0):
    imm = offset & 0xFFF
    return ((imm >> 5) << 25 | 8 << 20 | 9 << 15
            | {1: 0, 2: 1, 4: 2, 8: 3}[width] << 12
            | (imm & 31) << 7 | (0x27 if fp else 0x23))


def operations():
    result = {}
    for name, width, signed in (("lb", 1, True), ("lh", 2, True), ("lw", 4, True),
                                ("ld", 8, True), ("lbu", 1, False),
                                ("lhu", 2, False), ("lwu", 4, False)):
        result[name] = dict(width=width, write=False, fp=False, signed=signed,
                            instruction=load_instruction(width, signed), length=4, base=9)
    for name, width in (("sb", 1), ("sh", 2), ("sw", 4), ("sd", 8)):
        result[name] = dict(width=width, write=True, fp=False, signed=False,
                            instruction=store_instruction(width), length=4, base=9)
    for suffix, width in (("h", 2), ("w", 4), ("d", 8)):
        for write in (False, True):
            name = ("fs" if write else "fl") + suffix
            encode = store_instruction if write else load_instruction
            result[name] = dict(width=width, write=write, fp=True, signed=False,
                                instruction=encode(width, fp=True), length=4, base=9)
    # Encodings independently follow the compressed instruction bit layout.
    for name, width, write, fp, code, base in (
        ("c.lw", 4, False, False, 0x4080, 9), ("c.ld", 8, False, False, 0x6080, 9),
        ("c.sw", 4, True, False, 0xC080, 9), ("c.sd", 8, True, False, 0xE080, 9),
        ("c.fld", 8, False, True, 0x2080, 9), ("c.fsd", 8, True, True, 0xA080, 9),
        ("c.lwsp", 4, False, False, 0x4402, 2), ("c.ldsp", 8, False, False, 0x6402, 2),
        ("c.swsp", 4, True, False, 0xC022, 2), ("c.sdsp", 8, True, False, 0xE022, 2),
        ("c.fldsp", 8, False, True, 0x2402, 2), ("c.fsdsp", 8, True, True, 0xA022, 2),
    ):
        result[name] = dict(width=width, write=write, fp=fp, signed=not fp,
                            instruction=code, length=2, base=base)
    return result


OPS = operations()


def all_cases(enabled):
    result = {}

    def add(name, op="ld", **kwargs):
        result[name] = dict(op=op, **kwargs)

    for op in OPS:
        for allow in ((False, True) if enabled else (True,)):
            add(f"opcode:{op}:{'allow' if allow else 'deny'}", op, allow=allow)
        if not OPS[op]["write"] and not OPS[op]["fp"]:
            add(f"sign-extension:{op}", op, negative=True)
    for op in ("ld", "sd"):
        if enabled:
            for context in ("M", "HS", "HU", "VS", "VU"):
                for policy in ("enabled", "disabled", "other-enabled", "trusted", "close", "other-close"):
                    add(f"policy:{op}:{context}:{policy}", op, context=context,
                        policy=policy, allow=False)
            for slot in range(16):
                add(f"slot:{op}:{slot}", op, slot=slot)
            for boundary in ("lo", "last", "hi", "before", "empty", "reverse", "invalid", "wrong-permission", "high-bound"):
                add(f"bounds:{op}:{boundary}", op, boundary=boundary)
            for context in ("HU", "HS"):
                add(f"delegation:{op}:{context}", op, context=context, allow=False, delegate=True)
                for allow in (False, True):
                    add(f"stateen:{op}:{context}:{int(allow)}", op, context=context,
                        stateen=False, allow=allow)
            add(f"retry:{op}", op, allow=False, retry=True)
            add(f"mprv:{op}", op, context="M", allow=False, mprv=True, translation="valid")
            for tagged in (False, True):
                add(f"pmm:{op}:{int(tagged)}", op, tagged=tagged, pmm=True)
        for translation in ("valid", "high-va", "page-fault", "page-permission"):
            for allow in ((False, True) if enabled else (True,)):
                add(f"translation:{op}:{translation}:{int(allow)}", op,
                    translation=translation, allow=allow)
        for error in ("pmp", "pma", "physical-hole", "noncanonical"):
            add(f"priority:{op}:{error}", op, allow=False, error=error)
        add(f"address-add-wrap:{op}", op, wrap=True)
    for op in ("flh", "flw", "fld", "fsh", "fsw", "fsd"):
        add(f"priority:{op}:fp-disabled", op, allow=False, fp_disabled=True)
        add(f"translation:{op}:valid", op, translation="valid")
    return result


def page_tables(context, translation):
    root, middle, leaf = BASE + 0x10000, BASE + 0x11000, BASE + 0x12000
    tables = {address: bytearray(4096) for address in (root, middle, leaf)}
    pointer = lambda address: (address >> 12) << 10 | 1
    struct.pack_into("<Q", tables[root], 2 * 8, pointer(middle))
    struct.pack_into("<Q", tables[root], 258 * 8, pointer(middle))
    struct.pack_into("<Q", tables[middle], 0, pointer(leaf))
    flags = 0xCF | (0x10 if context == "HU" else 0)
    for index in range(32):
        value = pointer(BASE + index * 4096) | flags
        if index == (DATA - BASE) // 4096:
            if translation == "page-fault":
                value = 0
            elif translation == "page-permission":
                value &= ~6
        struct.pack_into("<Q", tables[leaf], index * 8, value)
    return (8 << 60) | (root >> 12), {address: bytes(content) for address, content in tables.items()}


def prepare(ref, case):
    op = OPS[case["op"]]
    context = case.get("context", "HU")
    mode, virtual = M.UIT.CONTEXTS[context]
    policy = case.get("policy", "enabled")
    enabled = ref.enabled
    own_enable = 1 if mode == 1 else 2
    config = 3
    if policy == "disabled":
        config = 0
    elif policy == "other-enabled":
        config = 3 ^ own_enable
    own_close = (3 if op["write"] else 4) if mode == 1 else (7 if op["write"] else 8)
    if policy == "close":
        config |= 1 << own_close
    elif policy == "other-close":
        config |= 1 << (own_close + 4 if mode == 1 else own_close - 4)
    trusted = policy == "trusted"
    lo, hi = (TARGET, TARGET + 16) if trusted else (TARGET + 0x80, TARGET + 0x88)
    slot = case.get("slot", 0)
    va, pa = DATA, DATA
    bound_lo, bound_hi = DATA, DATA + 64
    permission = 1 if op["write"] else 2
    nibble = 8 | permission if case.get("allow", True) or case.get("retry") else 0
    if case.get("retry"):
        nibble = 0
    boundary = case.get("boundary")
    if boundary == "last":
        va = pa = bound_hi - op["width"]
    elif boundary == "hi":
        va = pa = bound_hi
    elif boundary == "before":
        va = pa = bound_lo - op["width"]
    elif boundary == "empty":
        bound_hi = bound_lo
    elif boundary == "reverse":
        bound_lo, bound_hi = bound_hi, bound_lo
    elif boundary == "invalid":
        nibble &= ~8
    elif boundary == "wrong-permission":
        nibble = 8 | (2 if op["write"] else 1)
    elif boundary == "high-bound":
        bound_lo |= 1 << 63
        bound_hi |= 1 << 63
    translation = case.get("translation")
    if translation == "high-va":
        va = 0xFFFFFFC080004000
        bound_lo, bound_hi = va, va + 64
    error = case.get("error")
    if error == "physical-hole":
        va = 0x70000000
    if error == "noncanonical":
        va, translation = 0x0000008000004000, "valid"
    address_register = va
    instruction = op["instruction"]
    if case.get("wrap"):
        address_register = MASK - 7
        va = pa = 0
        instruction = store_instruction(op["width"], offset=8) if op["write"] else load_instruction(op["width"], offset=8)
    if case.get("pmm") and case.get("tagged"):
        address_register = va | (0x5A << 57)
    assignments = [(M.SCFG, config), (M.SLO, lo), (M.SHI, hi), (M.ULO, lo), (M.UHI, hi),
                   (LIBLO + 2 * slot, bound_lo), (LIBLO + 2 * slot + 1, bound_hi),
                   (LIBCFG, nibble << (slot * 4)), (FREASON, 7)] if enabled else []
    setup_code, pool = M.literal_writes(assignments)
    initial_fs = 0 if case.get("fp_disabled") else 1
    status = (0xA << 32) | mode << 11 | virtual << 39 | initial_fs << 13
    csrs = {0x300: status, 0x200: initial_fs << 13, 0x341: TARGET, 0x003: 0x1B}
    memory = bytearray(INITIAL_MEMORY)
    if case.get("negative"):
        memory[DATA - MEM_START + op["width"] - 1] |= 0x80
    extra = {POOL: pool, MEM_START: bytes(memory), M.MTRAP: words(M.addi(0, 0, 0)),
             STRAP: words(M.addi(0, 0, 0))}
    if translation:
        satp, tables = page_tables("HU" if case.get("mprv") else context, translation)
        csrs[0x180] = satp
        extra.update(tables)
    if error == "pmp":
        csrs.update({0x3A0: 0x1F18, 0x3B0: (DATA >> 2) | 0x1FF,
                     0x3B1: (1 << 46) - 1})
    if error == "pma":
        # The first NAPOT entry rejects the data page. R/W/X in the next
        # whole-space entry keep code, literals and trap handlers reachable.
        csrs.update({0x7C0: 0x1F18, 0x7C8: (DATA >> 2) | 0x1FF,
                     0x7C9: (1 << 46) - 1})
    if case.get("pmm"):
        csrs[0x10A] = 2 << 32
    if case.get("delegate"):
        csrs[0x302] = 1 << (25 if mode == 1 else 24)
    prelude = []
    gprs = {8: STORE_VALUE if op["write"] and not op["fp"] else SENTINEL,
            40: STORE_VALUE if op["write"] and op["fp"] else SENTINEL,
            op["base"]: address_register, 20: POOL}
    if case.get("mprv"):
        prelude = [csr(0x300, 1, 0, 7)]
        gprs[7] = (0xA << 32) | 1 << 17 | initial_fs << 13
    pc = TARGET + 4 * len(prelude)
    extra[TARGET] = words(*prelude) + instruction.to_bytes(op["length"], "little") + words(M.addi(0, 0, 0))
    if case.get("retry"):
        gprs[6] = (8 | permission) << (slot * 4)
        extra[M.MTRAP] = words(csr(LIBCFG, 1, 0, 6), M.MRET)
    ref.setup(words(*setup_code, M.MRET), gprs=gprs, csrs=csrs,
              mc=int(case.get("stateen", True)), sc=int(case.get("stateen", True)), extra_code=extra)
    if enabled:
        request = FdiInit(0x10000, 32, 0, 0, FDI_EPOCH, 3)
        check(ref.lib.difftest_fdi_init(C.byref(request), C.sizeof(request)), 0, "FDI init")
    ref.normal(len(setup_code) + 1 + len(prelude))
    check((ref.regs()[M.REG_MODE], ref.regs()[M.REG_V], ref.regs()[M.REG_PC]),
          (mode, virtual, pc), "real source-mode entry")
    requires = enabled and mode != 3 and bool(config & own_enable)
    guest_illegal = requires and bool(virtual)
    in_bound = bool(nibble & 8) and bool(nibble & permission) and bound_lo <= va and va + op["width"] - 1 < bound_hi
    allowed = not requires or (not virtual and (trusted or bool(config & (1 << own_close)) or in_bound))
    cause = None
    if case.get("fp_disabled") or guest_illegal:
        cause = 2
    elif translation in ("page-fault", "page-permission") or error == "noncanonical":
        cause = 15 if op["write"] else 13
    elif error in ("pmp", "pma", "physical-hole") or case.get("wrap"):
        cause = 7 if op["write"] else 5
    elif not allowed:
        cause = 25 if mode == 1 else 24
    return dict(op=op, pc=pc, va=va, pa=pa, instruction=instruction, cause=cause,
                initial_fs=initial_fs, context=context)


def check_access(ref, details, before_regs, before_memory, expected_cause):
    op, pc = details["op"], details["pc"]
    after = ref.regs()
    expected_regs = list(before_regs[:64])
    memory = bytearray(before_memory)
    if expected_cause is None:
        check(after[M.REG_PC], pc + op["length"], "normal successor")
        offset = details["pa"] - MEM_START
        if op["write"]:
            memory[offset:offset + op["width"]] = STORE_VALUE.to_bytes(8, "little")[:op["width"]]
        else:
            value = int.from_bytes(memory[offset:offset + op["width"]], "little", signed=op["signed"])
            if op["fp"] and op["width"] < 8:
                value |= MASK ^ ((1 << (8 * op["width"])) - 1)
            expected_regs[40 if op["fp"] else 8] = value & MASK
    check(list(after[:64]), expected_regs, "complete GPR/FPR result and denial preservation")
    check(ref.read_memory(MEM_START, len(memory)), bytes(memory), "complete watched-memory result")
    expected_fs = 3 if expected_cause is None and op["fp"] and not op["write"] else details["initial_fs"]
    check((ref.csrs()[0x300] >> 13) & 3, expected_fs, "FP dirty state")
    check(ref.csrs()[0x003] & 0xFF, 0x1B, "FCSR unchanged by scalar access")
    commit = ref.lib.difftest_store_commit
    commit.argtypes = [C.POINTER(C.c_uint64), C.POINTER(C.c_uint64), C.POINTER(C.c_uint8)]
    commit.restype = C.c_int
    if expected_cause is None and op["write"]:
        byte_offset = details["pa"] & 7
        addr = C.c_uint64(details["pa"] & ~7)
        data = C.c_uint64((STORE_VALUE & ((1 << (8 * op["width"])) - 1)) << (8 * byte_offset))
        mask = C.c_uint8(((1 << op["width"]) - 1) << byte_offset)
        check(commit(C.byref(addr), C.byref(data), C.byref(mask)), 0, "exact allowed store commit")
    # The native API returns 1 on an empty queue without changing arguments.
    # A mismatched entry also returns 1, so preserve-and-check sentinels matter.
    addr, data, mask = C.c_uint64(MASK), C.c_uint64(SENTINEL), C.c_uint8(0)
    check(commit(C.byref(addr), C.byref(data), C.byref(mask)), 1, "no extra or denied store commit")
    check((addr.value, data.value, mask.value), (MASK, SENTINEL, 0), "empty store queue sentinels")


def run_case(args):
    case = all_cases(args.state == "on")[args.case]
    ref = M.Reference(args.reference, args.state == "on")
    if ref.enabled:
        fdi_bind(ref)
        check(fdi_snapshot(ref, reset=True), [0] * 52, "natural FDI reset before imports")
    details = prepare(ref, case)
    before_regs = ref.regs()
    before_memory = ref.read_memory(MEM_START, len(INITIAL_MEMORY))
    before_fdi = fdi_snapshot(ref) if ref.enabled else None
    cause = details["cause"]
    ref.step(details["pc"], retired=cause is None)
    check_access(ref, details, before_regs, before_memory, cause)
    if cause is not None:
        delegated = bool(case.get("delegate")) and cause in (24, 25)
        bank = ref.csrs()
        check(ref.regs()[M.REG_PC], STRAP if delegated else M.MTRAP, "trap destination")
        check(ref.regs()[M.REG_MODE], 1 if delegated else 3, "trap mode")
        check(ref.regs()[M.REG_V], 0, "trap host context")
        offset = 0x100 if delegated else 0x300
        check(bank[offset + 0x42], cause, "exact selected cause")
        check(bank[offset + 0x41], details["pc"], "source EPC")
        check(bank[offset + 0x43], details["instruction"] if cause == 2 else details["va"], "complete TVAL")
        ref.metrics["isa_exceptions"] += 1
    if ref.enabled:
        expected = before_fdi[:]
        if cause in (24, 25):
            expected[42] = 3 if details["op"]["write"] else 2
        check(fdi_snapshot(ref), expected, "only selected FDI trap changes FReason")
    if case.get("retry"):
        check(cause, 24, "retry starts with actual HU denial")
        ref.normal(2)
        check(ref.regs()[M.REG_PC], details["pc"], "MRET retries unchanged source EPC")
        retry_regs = ref.regs()
        ref.step(details["pc"])
        check_access(ref, details, retry_regs, before_memory, None)
        check(fdi_snapshot(ref)[42], 3 if details["op"]["write"] else 2,
              "successful retry preserves earlier FReason")
    return {"case": args.case, "status": "PASS", "expected_cause": cause,
            "instruction": hex(details["instruction"]), "source_pc": hex(details["pc"]),
            "effective_va": hex(details["va"]), "metrics": ref.metrics}


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--state", choices=("on", "off"), required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--case")
    parser.add_argument("--select", action="append")
    args = parser.parse_args()
    args.reference = args.reference.resolve(strict=True)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    available = all_cases(args.state == "on")
    selected = [args.case] if args.case else args.select or list(available)
    if args.jobs < 1 or set(selected) - set(available):
        parser.error("positive jobs and known case names are required")
    if args.case:
        try:
            result = run_case(args)
        except Exception as error:
            traceback.print_exc()
            result = {"case": args.case, "status": "FAIL", "error": str(error)}
        print("DASICS_SCALAR_RESULT " + json.dumps(result), flush=True)
        return int(result["status"] != "PASS")
    if not args.output:
        parser.error("--output is required for a suite")
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("output must be empty to preserve earlier evidence")
    output.mkdir(parents=True, exist_ok=True)
    driver = output / "driver.py"
    helpers = {driver: Path(__file__), output / "m01-baseline.py": BASELINE,
               output / "uit-baseline.py": M.HELPER}
    for destination, source in helpers.items():
        destination.write_bytes(source.read_bytes())
    started, clock = timestamp(), time.monotonic()

    def execute(name):
        command = [sys.executable, "-B", str(driver), "--reference", str(args.reference),
                   "--state", args.state, "--case", name]
        stem = name.replace(":", "_")
        log = output / (stem + ".log")
        before, begin = timestamp(), time.monotonic()
        with log.open("w") as stream:
            try:
                process = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT,
                                         timeout=60, check=False)
                code, timeout = process.returncode, False
            except subprocess.TimeoutExpired:
                code, timeout = None, True
        result = {"case": name, "status": "FAIL", "exit_code": code, "timed_out": timeout,
                  "command": command, "log": str(log), "start_utc": before,
                  "end_utc": timestamp(), "elapsed_seconds": time.monotonic() - begin}
        markers = [line.removeprefix("DASICS_SCALAR_RESULT ") for line in log.read_text(errors="replace").splitlines()
                   if line.startswith("DASICS_SCALAR_RESULT ")]
        if markers:
            result.update(json.loads(markers[-1]))
        if code != 0 or timeout:
            result["status"] = "FAIL"
        (output / (stem + ".json")).write_text(json.dumps(result, indent=2) + "\n")
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(execute, selected))
    failures = sum(item["status"] != "PASS" for item in results)
    summary = {"schema": 1, "kind": "real-dasics-scalar-model-tests", "state": args.state,
               "reference": str(args.reference), "reference_sha256": hashlib.sha256(args.reference.read_bytes()).hexdigest(),
               "sources": {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in helpers},
               "start_utc": started, "end_utc": timestamp(), "elapsed_seconds": time.monotonic() - clock,
               "count": len(results), "passed": len(results) - failures, "failed": failures,
               "status": "FAIL" if failures else "PASS", "cases": results,
               "scope": "Aligned ordinary integer/FP/compressed scalar execution; no DUT comparison, nonaligned, atomic, vector, HLV/HSV, or complete MMIO validation. Architectural observations do not measure physical data-read counts."}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({key: value for key, value in summary.items() if key != "cases"}, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
