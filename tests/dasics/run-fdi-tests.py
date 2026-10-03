#!/usr/bin/env python3
"""Check independent FDI export against encoded CSR execution and reset ordering."""
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
import subprocess
import sys
import time
import traceback

BASELINE = Path(__file__).with_name("m01-baseline.py")
if not BASELINE.exists():
    BASELINE = Path(__file__).with_name("run-model-tests.py")
SPEC = importlib.util.spec_from_file_location("fdi_model_baseline", BASELINE)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
check = M.check
VERSION, FEATURES, EPOCH = 0x10000, 3, 0x100000001


def fields(names, ctype):
    return [(name, ctype) for name in names.split()]


class Caps(C.Structure):
    _fields_ = (fields("version bytes state_bytes projection_words", C.c_uint32)
                + fields("supported_features enabled_features", C.c_uint64)
                + fields("xlen max_harts init_bytes projection_version machine_abi_major reserved32", C.c_uint32)
                + fields("reserved64", C.c_uint64))


class Init(C.Structure):
    _fields_ = fields("version bytes hart reserved", C.c_uint32) + fields("epoch required_features", C.c_uint64)


class State(C.Structure):
    _fields_ = (fields("version bytes hart phase", C.c_uint32)
                + fields("epoch model_pc", C.c_uint64) + [("words", C.c_uint64 * 52)])


def bind(lib):
    for name, arguments in {
        "query_caps": [C.c_void_p, C.c_uint32],
        "capture_reset": [C.c_uint32, C.c_void_p, C.c_uint32],
        "init": [C.c_void_p, C.c_uint32],
        "get_state": [C.c_uint32, C.c_void_p, C.c_uint32],
    }.items():
        fn = getattr(lib, "difftest_fdi_" + name)
        fn.argtypes, fn.restype = arguments, C.c_int32


def output(lib, name, cls=State, expected=0, hart=0, size=None, null=False):
    length = C.sizeof(cls)
    buffer = (C.c_ubyte * (length + 64))()
    C.memset(buffer, 0xa5, len(buffer))
    before = bytes(buffer)
    ptr = None if null else C.cast(C.byref(buffer, 32), C.c_void_p)
    arguments = (ptr, length if size is None else size)
    if name != "query_caps":
        arguments = (hart, *arguments)
    check(getattr(lib, "difftest_fdi_" + name)(*arguments), expected, name + " status")
    check(bytes(buffer)[:32], before[:32], name + " leading canary")
    check(bytes(buffer)[32 + length:], before[32 + length:], name + " trailing canary")
    if expected:
        check(bytes(buffer), before, name + " failure preserves entire output")
        return None
    return cls.from_buffer_copy(bytes(buffer)[32:32 + length])


def initialize(lib, expected=0, **changes):
    request = Init(VERSION, 32, 0, 0, EPOCH, FEATURES)
    for name, value in changes.items():
        setattr(request, name, value)
    before = bytes(request)
    check(lib.difftest_fdi_init(C.byref(request), 32), expected, "FDI init")
    check(bytes(request), before, "init input unchanged")


def state(ref, oracle=None):
    registers, csrs = bytes(ref.regs()), bytes(ref.csrs())
    count = ref.lib.get_abs_instr_count()
    record = output(ref.lib, "get_state")
    check((record.version, record.bytes, record.hart, record.phase, record.epoch),
          (VERSION, 448, 0, 1, EPOCH), "CURRENT header")
    check(record.model_pc, ref.regs()[M.REG_PC], "reference own current PC")
    check(list(record.words), [oracle.read(address) for address in M.FDI] if oracle else [0] * 52,
          "unmasked fixed projection")
    check(bytes(output(ref.lib, "get_state")), bytes(record), "repeat export is stable")
    check(bytes(ref.regs()), registers, "export preserves ordinary registers")
    check(bytes(ref.csrs()), csrs, "export preserves ordinary CSR array")
    check(ref.lib.get_abs_instr_count(), count, "export never executes instructions")
    return record


def reset(ref):
    count = ref.lib.get_abs_instr_count()
    record = output(ref.lib, "capture_reset")
    check((record.version, record.bytes, record.hart, record.phase, record.epoch),
          (VERSION, 448, 0, 0, 0), "RESET header")
    check(record.model_pc, ref.regs()[M.REG_PC], "natural reset PC retained")
    check(list(record.words), [0] * 52, "natural 52-word reset")
    check(ref.lib.get_abs_instr_count(), count, "capture has no execution")


def caps(lib, enabled):
    result = output(lib, "query_caps", Caps)
    expected = (VERSION, 64, 448, 52, 3, 3 if enabled else 0, 64, 1, 32, 1, 2, 0, 0)
    check(tuple(getattr(result, name) for name, _ in Caps._fields_), expected, "caps layout and capabilities")
    for size in (0, 63, 65):
        output(lib, "query_caps", Caps, -1, size=size)
    output(lib, "query_caps", Caps, -1, null=True)


def projection(ref):
    reset(ref)
    # Distinct values are loaded by the guest. FDI receives no host-side import.
    values = [(address, 0xfedcba0000000007 | ((index + 1) << 3))
              for index, address in enumerate(M.FDI)]
    code, pool = M.literal_writes(values)
    operations = []
    for address in M.FDI:
        for funct3, source in ((1, 5), (2, 6), (3, 7), (5, 31), (6, 16), (7, 1),
                               (2, 0), (3, 0), (6, 0), (7, 0)):
            operations.append((address, funct3, source))
            code.append(M.csr_insn(address, funct3, 10, source))
    ref.setup(M.words(*code), gprs={20: M.POOL, 6: 0, 7: 0x12345678fffffff1},
              extra_code={M.POOL: pool})
    initialize(ref.lib)
    oracle = M.Oracle()
    state(ref, oracle)
    pc = M.BASE
    for address, value in values:
        ref.step(pc)
        state(ref, oracle)
        ref.step(pc + 4)
        oracle.write(address, value)
        state(ref, oracle)
        pc += 8
    gprs = {5: values[-1][1], 6: 0, 7: 0x12345678fffffff1, 0: 0}
    for address, funct3, source in operations:
        old = oracle.operation(address, funct3, source, source if funct3 >= 5 else gprs[source])
        ref.step(pc)
        check(ref.regs()[10], old, "real CSR old value")
        state(ref, oracle)
        pc += 4
    return {"actual_instruction_count": len(code), "snapshots": len(code) + 1,
            "independent_projection_words": 52, "encoded_csr_operations": len(values) + len(operations)}


def run_case(args):
    enabled = args.state == "on"
    if args.case == "preinit":
        lib = C.CDLL(str(args.reference), mode=os.RTLD_LOCAL)
        bind(lib)
        caps(lib, enabled)
        output(lib, "capture_reset", expected=-4 if enabled else -2)
        output(lib, "get_state", expected=-4 if enabled else -2)
        initialize(lib, -4 if enabled else -2)
        return {}
    ref = M.Reference(args.reference, enabled)
    bind(ref.lib)
    caps(ref.lib, enabled)
    name = args.case
    if name == "projection":
        return projection(ref)
    if name == "errors":
        ordinary = bytes(ref.regs()), bytes(ref.csrs())
        for operation in ("capture_reset", "get_state"):
            for length in (0, 447, 449):
                output(ref.lib, operation, expected=-1, size=length)
            output(ref.lib, operation, expected=-1, null=True)
            output(ref.lib, operation, expected=-3 if enabled else -2, hart=1)
        check(ref.lib.difftest_fdi_init(None, 32), -1, "null initialization")
        request = Init(VERSION, 32, 0, 0, EPOCH, FEATURES)
        for length in (0, 31, 33):
            check(ref.lib.difftest_fdi_init(C.byref(request), length), -1, "initialization input length")
        for changes in ({"version": 0}, {"bytes": 31}, {"reserved": 1}):
            initialize(ref.lib, -1, **changes)
        for features in (0, 1, 2, 7):
            initialize(ref.lib, -2, required_features=features)
        initialize(ref.lib, -3 if enabled else -2, hart=1)
        initialize(ref.lib, -4 if enabled else -2, epoch=0)
        check((bytes(ref.regs()), bytes(ref.csrs())), ordinary, "invalid requests preserve architecture")
        if not enabled:
            output(ref.lib, "capture_reset", expected=-2)
            output(ref.lib, "get_state", expected=-2)
            initialize(ref.lib, -2)
            return {}
        output(ref.lib, "get_state", expected=-4)
        initialize(ref.lib, -4)
        reset(ref)
        output(ref.lib, "capture_reset", expected=-4)
        initialize(ref.lib)
        initialize(ref.lib, -4)
        output(ref.lib, "capture_reset", expected=-4)
        state(ref)
    elif name.startswith("late-import-"):
        operation = name[len("late-import-"):]
        data = ref.regs() if operation == "regcpy" else ref.csrs()
        getattr(ref.lib, "difftest_" + operation)(data, True)
        output(ref.lib, "capture_reset", expected=-4)
        initialize(ref.lib, -4)
    elif name == "late-exec":
        load = ref.lib.difftest_load_flash
        load.argtypes, load.restype = [C.c_void_p, C.c_size_t], None
        load(None, 0)
        ref.normal()
        output(ref.lib, "capture_reset", expected=-4)
        initialize(ref.lib, -4)
    elif name in ("exec-before-init", "uit-before-init"):
        reset(ref)
        instruction = M.csr_insn(0x040, 1, 0, 5) if name == "uit-before-init" else M.addi(6, 0, 7)
        ref.setup(M.words(instruction), gprs={5: 77})
        if name == "uit-before-init":
            ref.start()
            ref.execute(instruction)
        else:
            ref.normal()
        initialize(ref.lib, -4)
    elif name in ("event-before-capture", "event-before-init"):
        if name == "event-before-init":
            reset(ref)
        trap = ref.lib.difftest_raise_intr
        trap.argtypes, trap.restype = [C.c_uint64], None
        trap((1 << 63) | 7)
        if name == "event-before-capture":
            output(ref.lib, "capture_reset", expected=-4)
        initialize(ref.lib, -4)
    elif name in ("uit-event-before-init", "uit-isolated-event-before-init", "uit-rejected-before-init"):
        reset(ref)
        instructions = [M.csr_insn(0x005, 1, 0, 5), M.csr_insn(0x004, 1, 0, 7), M.csr_insn(0x000, 1, 0, 6)]
        ref.setup(M.words(*instructions), mode=3 if name == "uit-rejected-before-init" else 0,
                  gprs={5: M.BASE + 0x1000, 6: 1, 7: 0x10})
        ref.start()
        if name == "uit-event-before-init":
            for instruction in instructions:
                ref.execute(instruction)
            ref.raise_event()
            initialize(ref.lib, -4)
        elif name == "uit-isolated-event-before-init":
            # Seed only ordinary UIT fixture state to isolate the event path
            # from cpu_exec. No FDI state is imported or used as an oracle.
            bank = (C.c_uint64 * 4096).in_dll(ref.lib, "csr_array")
            bank[0x000], bank[0x004], bank[0x005] = 1, 0x10, M.BASE + 0x1000
            count = ref.lib.get_abs_instr_count()
            ref.raise_event()
            check(ref.lib.get_abs_instr_count(), count, "event bypasses cpu_exec")
            initialize(ref.lib, -4)
            return {"status": "PASS_ISOLATED_NATIVE", "scope":
                    "Internal ordinary UIT fixture isolates the actual event hook; not a complete public startup sequence"}
        else:
            before = bytes(ref.regs()), bytes(ref.csrs())
            ref.raise_event(expected=M.UIT.E["CONTEXT"])
            check((bytes(ref.regs()), bytes(ref.csrs())), before, "rejected event preserves architecture")
            initialize(ref.lib)
            state(ref)
    elif name == "uit-coexist":
        reset(ref)
        fdi_write, uit_write, fdi_read = M.csr_insn(0xbc4, 1, 0, 5), M.csr_insn(0x040, 1, 0, 6), M.csr_insn(0x9e1)
        ref.setup(M.words(fdi_write, uit_write, fdi_read), gprs={5: 0x7ff, 6: 0x12345678})
        initialize(ref.lib)
        ref.start()
        state(ref)
        ref.step(M.BASE)
        oracle = M.Oracle()
        oracle.write(0xbc4, 0x7ff)
        state(ref, oracle)
        ref.execute(uit_write)
        state(ref, oracle)
        check(ref.state().uscratch, 0x12345678, "UIT remains independent")
        ref.step(M.BASE + 8)
        check(ref.regs()[10], 0x7c2, "FDI source remains model-computed")
        state(ref, oracle)
    elif name == "illegal":
        reset(ref)
        instruction = M.csr_insn(0xbc4, 1, 10, 5)
        ref.setup(M.words(instruction), mode=1, virtual=1, gprs={5: M.MASK64})
        initialize(ref.lib)
        ref.normal(retired=False)
        M.illegal(ref, M.BASE, instruction)
        state(ref)
    elif name in ("reset-polluted", "init-polluted"):
        if name == "init-polluted":
            reset(ref)
        # Internal model fault injection, never the normal fixture or oracle path.
        write = ref.lib.dasics_csr_write
        write.argtypes, write.restype = [C.c_uint32, C.c_uint64], None
        write(0x8b0, 1)
        if name == "reset-polluted":
            output(ref.lib, "capture_reset", expected=-5)
        else:
            initialize(ref.lib, -5)
        write(0x8b0, 0)
        if name == "reset-polluted":
            reset(ref)
        initialize(ref.lib)
        state(ref)
    elif name.startswith("reject-"):
        reset(ref)
        if name != "reject-reset-after-capture":
            initialize(ref.lib)
        operation = name[len("reject-"):]
        print("FDI_EXPECTED_ABORT " + operation, flush=True)
        if operation.startswith("reset"):
            ref.lib.difftest_init()
        else:
            data = ref.regs() if operation == "regcpy" else ref.csrs()
            getattr(ref.lib, "difftest_" + operation)(data, True)
        raise AssertionError("forbidden operation returned")
    elif name in ("reset-no-session", "reinit-after-exec", "reinit-after-import"):
        if name == "reinit-after-exec":
            load = ref.lib.difftest_load_flash
            load.argtypes, load.restype = [C.c_void_p, C.c_size_t], None
            load(None, 0)
            ref.normal()
        elif name == "reinit-after-import":
            ref.lib.difftest_regcpy(ref.regs(), True)
        ref.lib.difftest_init()
        if enabled:
            output(ref.lib, "capture_reset", expected=-4)
            initialize(ref.lib, -4)
        # The passive FDI eligibility check must not disable ordinary reinit.
        registers = ref.regs()
        registers[M.REG_PC] = M.BASE
        ref.lib.difftest_regcpy(registers, True)
        payload = C.create_string_buffer(M.words(M.addi(6, 0, 7)))
        ref.lib.difftest_memcpy(M.BASE, payload, 4, True)
        ref.lib.difftest_exec(1)
        check(ref.regs()[6], 7, "ordinary execution remains usable after reinit")
    else:
        raise ValueError(name)
    return {}


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--state", choices=("off", "on"), required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--jobs", type=int, choices=range(1, 9), default=8)
    parser.add_argument("--case")
    args = parser.parse_args()
    args.reference = args.reference.resolve(strict=True)
    for cls, length in ((Caps, 64), (Init, 32), (State, 448)):
        check(C.sizeof(cls), length, "wire size " + cls.__name__)
        check(C.alignment(cls), 8, "wire alignment " + cls.__name__)
    check(State.words.offset, 32, "fixed projection offset")
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    if args.case:
        try:
            result = run_case(args)
            print("FDI_EXPORT_RESULT " + json.dumps({"status": "PASS", **result}), flush=True)
            return 0
        except Exception:
            traceback.print_exc()
            return 1
    if not args.output:
        parser.error("--output is required for a suite")
    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=False)
    driver = output_dir / "driver.py"
    driver.write_bytes(Path(__file__).read_bytes())
    (output_dir / "m01-baseline.py").write_bytes(BASELINE.read_bytes())
    (output_dir / "uit-baseline.py").write_bytes(M.HELPER.read_bytes())
    cases = ["preinit", "errors", "reset-no-session"]
    if args.state == "on":
        cases += ["projection", "late-import-regcpy", "late-import-csrcpy", "late-exec",
                  "exec-before-init", "uit-before-init", "uit-coexist", "illegal", "reset-polluted",
                  "init-polluted", "reject-regcpy", "reject-csrcpy", "reject-reset-after-capture", "reject-reset",
                  "reinit-after-exec", "reinit-after-import", "event-before-capture", "event-before-init",
                  "uit-event-before-init", "uit-isolated-event-before-init", "uit-rejected-before-init"]
    start = now()

    def run(name):
        command = [sys.executable, "-B", str(driver), "--reference", str(args.reference),
                   "--state", args.state, "--case", name]
        log = output_dir / (name + ".log")
        before = now()
        with log.open("x") as stream:
            try:
                rc = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, timeout=90).returncode
            except subprocess.TimeoutExpired:
                rc = None
        text = log.read_text(errors="replace")
        markers = [line[len("FDI_EXPORT_RESULT "):] for line in text.splitlines()
                   if line.startswith("FDI_EXPORT_RESULT ")]
        result = {"case": name, "exit_code": rc, "command": command, "log": str(log),
                  "started": before, "finished": now(), "status": "FAIL"}
        if rc == 0 and markers:
            result.update(json.loads(markers[-1]))
        if name.startswith("reject-"):
            operation = name[len("reject-"):]
            hook = "fdi_check_reset" if operation.startswith("reset") else "fdi_check_import"
            if rc == -signal.SIGABRT and "FDI_EXPECTED_ABORT " + operation in text and hook in text:
                result["status"] = "PASS_EXPECTED_ABORT"
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(run, cases))
    failed = [result["case"] for result in results if not result["status"].startswith("PASS")]
    result = {"status": "FAIL" if failed else "PASS", "state": args.state, "started": start,
              "finished": now(), "cases": results, "failed": failed,
              "reference": str(args.reference), "reference_sha256": hashlib.sha256(args.reference.read_bytes()).hexdigest(),
              "scope": "Actual NEMU FDI exports and encoded CSR execution; no DUT execution or full composition claim"}
    (output_dir / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "cases"}, indent=2))
    return int(bool(failed))


if __name__ == "__main__":
    sys.exit(main())
