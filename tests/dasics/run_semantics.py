#!/usr/bin/env python3
import argparse
import ctypes
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


GATE_CASES = (
    "taken_branch_main_call_entry",
    "taken_branch_return_pc",
    "taken_branch_active_zone_return_pc",
    "jump_main_call_entry",
    "jump_return_pc",
    "jump_active_zone_return_pc",
    "not_taken_branch_unchecked",
    "taken_branch_outside_allow_set",
    "jump_outside_allow_set",
    "load_fully_contained_in_one_bound",
    "store_fully_contained_in_one_bound",
    "aligned_load_outside_bound_rejected",
    "aligned_store_outside_bound_rejected",
    "misaligned_load_fully_contained",
    "misaligned_store_fully_contained",
    "all_bound_csrs_clear_low_three_bits",
    "u_ecall_untrusted_open_fault",
    "u_ecall_untrusted_closed_ordinary",
    "u_ecall_trusted_ordinary",
    "u_ecall_disabled_ordinary",
    "s_ecall_untrusted_open_fault",
    "s_ecall_untrusted_closed_ordinary",
    "s_ecall_trusted_ordinary",
    "s_ecall_disabled_ordinary",
    "call_j_trusted_updates_link_and_return_pc",
    "call_jr_trusted_updates_link_and_return_pc",
    "call_j_disabled_illegal_without_side_effect",
    "call_jr_disabled_illegal_without_side_effect",
    "call_j_untrusted_illegal_without_side_effect",
    "call_jr_untrusted_illegal_without_side_effect",
    "s_load_untrusted_open_fault",
    "s_load_untrusted_closed_allowed",
    "s_store_untrusted_open_fault",
    "s_store_untrusted_closed_allowed",
    "s_jump_untrusted_open_fault",
    "s_jump_untrusted_closed_allowed",
    "lb_allowed",
    "lb_denied",
    "lbu_allowed",
    "lbu_denied",
    "lh_allowed",
    "lh_denied",
    "lhu_allowed",
    "lhu_denied",
    "lw_allowed",
    "lw_denied",
    "lwu_allowed",
    "lwu_denied",
    "sb_allowed",
    "sb_denied_without_side_effect",
    "sh_allowed",
    "sh_denied_without_side_effect",
    "sw_allowed",
    "sw_denied_without_side_effect",
    "branch_jump_bound_slot0_allowed",
    "jal_jump_bound_slot0_allowed",
    "jalr_jump_bound_slot3_allowed",
    "jump_bound_high_endpoint_denied",
    "jump_bound_invalid_cfg_denied",
    "jump_bound_empty_range_denied",
    "jump_bound_reversed_range_denied",
    "jalr_main_call_entry_allowed",
    "jalr_outside_allow_set_denied",
    "u_load_trusted_bypasses_check",
    "u_load_disabled_bypasses_check",
    "u_load_closed_bypasses_check",
    "u_store_trusted_bypasses_check",
    "u_store_disabled_bypasses_check",
    "u_store_closed_bypasses_check",
    "u_jump_trusted_bypasses_check",
    "u_jump_disabled_bypasses_check",
    "u_jump_closed_bypasses_check",
    "write_only_bound_denies_load",
    "read_only_bound_denies_store",
    "permission_without_valid_denies_load",
    "lib_bound_slot15_allows_load",
    "empty_lib_bound_denies_load",
    "reversed_lib_bound_denies_store",
    "s_trusted_protected_csr_read_allowed",
    "s_untrusted_protected_csr_read_illegal",
    "s_untrusted_protected_csr_write_illegal",
    "s_call_j_trusted_updates_link_and_return_pc",
    "s_call_jr_trusted_updates_link_and_return_pc",
    "s_call_j_disabled_illegal_without_side_effect",
    "s_call_jr_disabled_illegal_without_side_effect",
    "s_call_j_untrusted_illegal_without_side_effect",
    "s_call_jr_untrusted_illegal_without_side_effect",
    "u_main_bound_high_endpoint_untrusted",
    "u_main_bound_empty_untrusted",
    "u_main_bound_reversed_untrusted",
    "u_main_bound_below_low_untrusted",
    "s_main_bound_high_endpoint_untrusted",
    "s_main_bound_empty_untrusted",
    "s_main_bound_reversed_untrusted",
    "s_main_bound_below_low_untrusted",
    "call_jr_non_ra_destination_trusted",
    "call_jr_non_ra_destination_illegal_without_side_effect",
    "call_j_nontrivial_positive_offset",
    "call_j_negative_offset",
    "taken_bne_outside_allow_set",
    "taken_blt_outside_allow_set",
    "taken_bge_outside_allow_set",
    "taken_bltu_outside_allow_set",
    "taken_bgeu_outside_allow_set",
    "jump_bound_slot1_allowed",
    "jump_bound_slot2_allowed",
    "compressed_jump_outside_allow_set",
    "compressed_jr_outside_allow_set",
    "compressed_jalr_outside_allow_set_without_link",
    "compressed_beqz_outside_allow_set",
    "compressed_bnez_outside_allow_set",
    "compressed_branch_not_taken_unchecked",
    "compressed_jump_main_call_entry_allowed",
    "s_load_trusted_bypasses_check",
    "s_load_disabled_bypasses_check",
    "s_store_trusted_bypasses_check",
    "s_store_disabled_bypasses_check",
    "s_jump_trusted_bypasses_check",
    "s_jump_disabled_bypasses_check",
    "s_untrusted_valid_read_bound_allowed",
    "s_untrusted_valid_write_bound_allowed",
    "s_untrusted_valid_jump_bound_allowed",
    "s_untrusted_special_target_allowed",
)

DIAGNOSTIC_CASES = (
    "load_spanning_adjacent_bounds",
    "load_spanning_overlapping_bounds",
    "store_spanning_adjacent_bounds",
    "partial_bound_load_tval",
)

CASE_NAMES = GATE_CASES + DIAGNOSTIC_CASES


class RefRegs(ctypes.Structure):
    _fields_ = [
        ("gpr", ctypes.c_uint64 * 32),
        ("fpr", ctypes.c_uint64 * 32),
        ("mode", ctypes.c_uint64),
        ("mstatus", ctypes.c_uint64),
        ("sstatus", ctypes.c_uint64),
        ("mepc", ctypes.c_uint64),
        ("sepc", ctypes.c_uint64),
        ("mtval", ctypes.c_uint64),
        ("stval", ctypes.c_uint64),
        ("mtvec", ctypes.c_uint64),
        ("stvec", ctypes.c_uint64),
        ("mcause", ctypes.c_uint64),
        ("scause", ctypes.c_uint64),
        ("satp", ctypes.c_uint64),
        ("mip", ctypes.c_uint64),
        ("mie", ctypes.c_uint64),
        ("mscratch", ctypes.c_uint64),
        ("sscratch", ctypes.c_uint64),
        ("mideleg", ctypes.c_uint64),
        ("medeleg", ctypes.c_uint64),
        ("pc", ctypes.c_uint64),
        ("fcsr", ctypes.c_uint64),
        ("tselect", ctypes.c_uint64),
        ("tdata1", ctypes.c_uint64),
        ("tinfo", ctypes.c_uint64),
    ]


def require_file(value, label):
    path = Path(value).resolve()
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    return path


def require_tool(value, label):
    resolved = shutil.which(value)
    if resolved is None:
        raise RuntimeError(f"missing {label}: {value}")
    return Path(resolved).resolve()


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_reference_identity(arguments):
    so_path = require_file(arguments.so, "NEMU reference shared object")
    config_path = require_file(arguments.config, "NEMU reference configuration")
    canonical_config = (
        Path(__file__).resolve().parents[2]
        / "configs"
        / "riscv64-nhv5-dasics-ref_defconfig"
    )
    canonical_config = require_file(canonical_config, "canonical DASICS defconfig")

    expected_config_path = (so_path.parent.parent / ".config").resolve()
    if config_path != expected_config_path:
        raise RuntimeError(
            "reference configuration must be the .config adjacent to the SO build: "
            f"expected={expected_config_path} actual={config_path}"
        )
    if config_path.read_bytes() != canonical_config.read_bytes():
        raise RuntimeError(
            "reference configuration does not exactly match "
            "riscv64-nhv5-dasics-ref_defconfig"
        )

    expected_sha256 = arguments.so_sha256.lower()
    if re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None:
        raise RuntimeError("NEMU reference SHA-256 must be 64 lowercase hex digits")
    actual_sha256 = sha256_file(so_path)
    if actual_sha256 != expected_sha256:
        raise RuntimeError(
            "NEMU reference SHA-256 mismatch: "
            f"expected={expected_sha256} actual={actual_sha256}"
        )
    return so_path


def read_symbol(nm_path, elf_path, name):
    completed = subprocess.run(
        [str(nm_path), "-n", "--defined-only", str(elf_path)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"nm failed: {completed.stderr.strip()}")
    matches = []
    for line in completed.stdout.splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[-1] == name and re.fullmatch(r"[0-9a-fA-F]+", fields[0]):
            matches.append(int(fields[0], 16))
    if len(matches) != 1:
        raise RuntimeError(f"expected one {name} symbol, found {matches}")
    return matches[0]


def configure_api(library):
    library.difftest_init.argtypes = []
    library.difftest_init.restype = None
    library.difftest_memcpy.argtypes = [
        ctypes.c_uint64,
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_bool,
    ]
    library.difftest_memcpy.restype = None
    library.difftest_regcpy.argtypes = [ctypes.c_void_p, ctypes.c_bool]
    library.difftest_regcpy.restype = None
    library.difftest_exec.argtypes = [ctypes.c_uint64]
    library.difftest_exec.restype = None


def run_case(library, image, done_pc, index, max_steps):
    library.difftest_init()
    image_buffer = (ctypes.c_ubyte * len(image)).from_buffer_copy(image)
    library.difftest_memcpy(
        0x80000000,
        ctypes.cast(image_buffer, ctypes.c_void_p),
        len(image),
        True,
    )

    registers = RefRegs()
    library.difftest_regcpy(ctypes.byref(registers), False)
    registers.pc = 0x80000000
    registers.gpr[0] = 0
    registers.gpr[10] = index
    library.difftest_regcpy(ctypes.byref(registers), True)

    for steps in range(max_steps + 1):
        library.difftest_regcpy(ctypes.byref(registers), False)
        if registers.pc == done_pc:
            return (
                registers.gpr[10],
                steps,
                registers.mcause,
                registers.mepc,
                registers.mtval,
                registers.gpr[11],
                registers.gpr[12],
            )
        if steps != max_steps:
            library.difftest_exec(1)
    raise RuntimeError(
        f"case={CASE_NAMES[index]} did not reach test_done within {max_steps} steps; "
        f"pc=0x{registers.pc:x}"
    )


def run_isolated_case(arguments, index):
    so_path = verify_reference_identity(arguments)
    elf_path = require_file(arguments.elf, "test ELF")
    bin_path = require_file(arguments.bin, "test binary")
    nm_path = require_tool(arguments.nm, "RISC-V nm")
    if ctypes.sizeof(RefRegs) != 696 or RefRegs.pc.offset != 656:
        raise RuntimeError("unexpected dedicated-reference register ABI")

    done_pc = read_symbol(nm_path, elf_path, "test_done")
    image = bin_path.read_bytes()
    library = ctypes.CDLL(str(so_path), mode=os.RTLD_NOW | os.RTLD_LOCAL)
    configure_api(library)
    return run_case(library, image, done_pc, index, arguments.max_steps)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--so", required=True)
    parser.add_argument("--so-sha256", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--elf", required=True)
    parser.add_argument("--bin", required=True)
    parser.add_argument("--nm", required=True)
    parser.add_argument("--max-steps", default=1000, type=int)
    parser.add_argument("--case-index", type=int)
    parser.add_argument("--diagnostic", action="store_true")
    arguments = parser.parse_args()

    if arguments.case_index is not None:
        if arguments.case_index < 0 or arguments.case_index >= len(CASE_NAMES):
            raise ValueError(f"invalid case index: {arguments.case_index}")
        result, steps, mcause, mepc, mtval, detail, aux = run_isolated_case(
            arguments, arguments.case_index
        )
        print(
            f"CASE_RESULT result=0x{result:x} steps={steps} "
            f"mcause=0x{mcause:x} mepc=0x{mepc:x} mtval=0x{mtval:x} "
            f"detail=0x{detail:x} aux=0x{aux:x}",
            flush=True,
        )
        return 0

    diagnostic_offset = len(GATE_CASES)
    selected_cases = DIAGNOSTIC_CASES if arguments.diagnostic else GATE_CASES
    failures = []
    for ordinal, name in enumerate(selected_cases):
        index = diagnostic_offset + ordinal if arguments.diagnostic else ordinal
        completed = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--so",
                arguments.so,
                "--so-sha256",
                arguments.so_sha256,
                "--config",
                arguments.config,
                "--elf",
                arguments.elf,
                "--bin",
                arguments.bin,
                "--nm",
                arguments.nm,
                "--max-steps",
                str(arguments.max_steps),
                "--case-index",
                str(index),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(f"case={name} subprocess failed: {detail}")
        match = re.fullmatch(
            r"CASE_RESULT result=0x([0-9a-f]+) steps=([0-9]+) "
            r"mcause=0x([0-9a-f]+) mepc=0x([0-9a-f]+) "
            r"mtval=0x([0-9a-f]+) detail=0x([0-9a-f]+) aux=0x([0-9a-f]+)",
            completed.stdout.strip(),
        )
        if not match:
            raise RuntimeError(f"case={name} returned malformed output: {completed.stdout!r}")
        result = int(match.group(1), 16)
        steps = int(match.group(2), 10)
        mcause = int(match.group(3), 16)
        mepc = int(match.group(4), 16)
        mtval = int(match.group(5), 16)
        detail = int(match.group(6), 16)
        aux = int(match.group(7), 16)
        if arguments.diagnostic:
            if result != 0:
                raise RuntimeError(
                    f"case={name} diagnostic fixture failed with result=0x{result:x}"
                )
            print(
                f"SPEC_BLOCKED case={name} steps={steps} mcause=0x{mcause:x} "
                f"mepc=0x{mepc:x} mtval=0x{mtval:x} freason=0x{detail:x} "
                f"store_changed={aux}",
                flush=True,
            )
            continue
        if result == 0:
            print(f"PASS case={name} steps={steps}", flush=True)
        else:
            print(
                f"FAIL case={name} result=0x{result:x} steps={steps} "
                f"mcause=0x{mcause:x} mepc=0x{mepc:x} mtval=0x{mtval:x} "
                f"detail=0x{detail:x} aux=0x{aux:x}",
                flush=True,
            )
            failures.append(name)

    if arguments.diagnostic:
        print(
            f"DASICS_DIAGNOSTIC_COMPLETE cases={len(selected_cases)} "
            "result=SPEC_BLOCKED",
            flush=True,
        )
        return 0
    if failures:
        print(
            "DASICS_SEMANTICS_FAIL "
            f"passed={len(selected_cases) - len(failures)} "
            f"failed={len(failures)} total={len(selected_cases)} "
            f"cases={','.join(failures)}",
            flush=True,
        )
        return 1
    print(f"DASICS_SEMANTICS_PASS cases={len(selected_cases)}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"DASICS_SEMANTICS_ERROR: {error}", file=sys.stderr, flush=True)
        raise SystemExit(2)
