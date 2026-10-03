#!/usr/bin/env python3
"""Build an immutable DASICS reference candidate from local, frozen inputs."""

import argparse
import ctypes as C
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import shutil
import socket
import struct
import subprocess
import sys


HOST = "cmy-zgclab-eda"
DEFINITIONS = ("dasics-machine-abi.json", "dasics-uit-contract.json", "dasics-build-config.json")
CAP_NAMES = ("version", "bytes", "enabled_features", "supported_features", "xlen", "vlen",
             "legacy_regcpy_bytes", "legacy_csrcpy_bytes", "legacy_regcpy_arity", "max_harts",
             "exec_request_bytes", "event_request_bytes", "state_bytes", "exec_result_bytes")
HOOKS = ("uit_note_execution", "uit_note_retirement", "uit_validate_fetched", "uit_check_mmio",
         "uit_record_tx", "uit_check_import")
EXPORTS = ("difftest_init", "difftest_set_ramsize", "difftest_regcpy", "difftest_csrcpy",
           "difftest_memcpy", "difftest_exec", "difftest_uit_query_caps", "difftest_uit_init",
           "difftest_uit_exec", "difftest_uit_raise_event", "difftest_uit_get_state", "difftest_uit_read_tx",
           "difftest_fdi_query_caps", "difftest_fdi_capture_reset", "difftest_fdi_init", "difftest_fdi_get_state")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def guarded(size):
    data = (C.c_ubyte * (size + 64))()
    C.memset(data, 0xa5, len(data))
    return data, C.cast(C.byref(data, 32), C.c_void_p)


def guards(data, size, label):
    value = bytes(data)
    require(value[:32] == b"\xa5" * 32 and value[size + 32:] == b"\xa5" * 32,
            "ABI_CANARY_OVERWRITE: " + label)


def probe_child(reference, enabled):
    """Probe only the model ABI and a bounded instruction sequence, without a DUT."""
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    resource.setrlimit(resource.RLIMIT_AS, (4 << 30, 4 << 30))
    symbols = subprocess.check_output(["/usr/bin/nm", "-D", "--defined-only", str(reference)], text=True)
    exported = {line.split()[-1] for line in symbols.splitlines() if line.split()}
    require(set(EXPORTS) <= exported, "REFERENCE_EXPORT_MISSING")
    require(all(name in exported for name in HOOKS) if enabled else not set(HOOKS) & exported,
            "REFERENCE_PROTOCOL_HOOK_MISMATCH")
    library = C.CDLL(str(reference), mode=os.RTLD_LOCAL | os.RTLD_NOW)
    loaded = [line for line in Path("/proc/self/maps").read_text().splitlines()
              if line.split(maxsplit=5)[-1] == str(reference)]
    require(loaded, "REFERENCE_LOAD_NOT_OBSERVED")
    query = library.difftest_uit_query_caps
    query.argtypes, query.restype = [C.c_void_p, C.c_uint32], C.c_int32
    raw, pointer = guarded(64)
    require(query(pointer, 64) == 0, "REFERENCE_QUERY_FAILED")
    guards(raw, 64, "query")
    caps = dict(zip(CAP_NAMES, struct.unpack("<IIQQ10I", bytes(raw)[32:96])))
    expected = dict(zip(CAP_NAMES, (0x10000, 64, 0x3f if enabled else 0, 0x3f,
                                  64, 128, 1400, 32768, 2, 1, 64, 64, 112, 64)))
    require(caps == expected, f"REFERENCE_CAPABILITY_MISMATCH: {caps}")
    require(query(pointer, 63) == -1, "REFERENCE_QUERY_SIZE_NOT_REJECTED")
    guards(raw, 64, "query rejected size")
    fdi_query = library.difftest_fdi_query_caps
    fdi_query.argtypes, fdi_query.restype = [C.c_void_p, C.c_uint32], C.c_int32
    fdi_buffer, fdi_pointer = guarded(64)
    require(fdi_query(fdi_pointer, 64) == 0, "FDI_CAPABILITIES_QUERY_FAILED")
    guards(fdi_buffer, 64, "FDI capabilities")
    fdi_fields = ("version", "bytes", "state_bytes", "projection_words", "supported_features", "enabled_features",
                  "xlen", "max_harts", "init_bytes", "projection_version", "machine_abi_major", "reserved32", "reserved64")
    fdi_values = struct.unpack("<IIIIQQIIIIIIQ", bytes(fdi_buffer)[32:96])
    require(fdi_values == (0x10000, 64, 448, 52, 3, 3 if enabled else 0, 64, 1, 32, 1, 2, 0, 0),
            "FDI_CAPABILITIES_MISMATCH")
    fdi_caps = dict(zip(fdi_fields, fdi_values))
    fdi_epoch = 0xD010000000000001

    def fdi_snapshot(name, phase, epoch, pc, expected_words):
        function = getattr(library, "difftest_fdi_" + name)
        function.argtypes, function.restype = [C.c_uint32, C.c_void_p, C.c_uint32], C.c_int32
        data, pointer = guarded(448)
        before = bytes(data)
        require(function(0, pointer, 448) == (0 if enabled else -2), "FDI_STATE_STATUS: " + name)
        guards(data, 448, name)
        if not enabled:
            require(bytes(data) == before, "FDI_DISABLED_OUTPUT_CHANGED: " + name)
            return None
        values = struct.unpack("<IIIIQQ52Q", bytes(data)[32:480])
        require(values[:6] == (0x10000, 448, 0, phase, epoch, pc), "FDI_STATE_HEADER: " + name)
        require(list(values[6:]) == expected_words, "FDI_RAW_PROJECTION_MISMATCH: " + name)
        return {"phase": phase, "epoch": epoch, "model_pc": pc, "words": list(values[6:])}

    library.difftest_set_ramsize.argtypes, library.difftest_set_ramsize.restype = [C.c_size_t], None
    library.difftest_set_ramsize(16 << 20)
    library.difftest_init.argtypes, library.difftest_init.restype = [], None
    library.difftest_init()
    for name in ("regcpy", "csrcpy"):
        function = getattr(library, "difftest_" + name)
        function.argtypes, function.restype = [C.c_void_p, C.c_bool], None

    def read(name, size):
        data, ptr = guarded(size)
        getattr(library, "difftest_" + name)(ptr, False)
        guards(data, size, name + " read")
        return (C.c_uint64 * (size // 8)).from_buffer_copy(bytes(data)[32:32 + size])

    def write(name, data):
        size = C.sizeof(data)
        buffer, ptr = guarded(size)
        C.memmove(ptr, data, size)
        getattr(library, "difftest_" + name)(ptr, True)
        guards(buffer, size, name + " write")

    base, sentinel = 0x80000000, 0x123456789abcdef0
    regs = read("regcpy", 1400)
    require(regs[64] == 3, "REFERENCE_INITIAL_MODE_MISMATCH")
    fdi_reset = fdi_snapshot("capture_reset", 0, 0, regs[82], [0] * 52)
    regs[5], regs[7], regs[10], regs[71], regs[82] = sentinel, 0x7ff, sentinel, base + 0x1000, base
    write("regcpy", regs)
    require(bytes(read("regcpy", 1400)) == bytes(regs), "REGCPY_SENTINEL_MISMATCH")
    csrs = read("csrcpy", 32768)
    csrs[0x340] = 0x5a55f00dcafebeef
    write("csrcpy", csrs)
    require(bytes(read("csrcpy", 32768)) == bytes(csrs), "CSRCPY_SENTINEL_MISMATCH")
    # All imports precede execution. FDI state is only touched by encoded CSR instructions.
    instructions = [(7 << 20) | (5 << 15) | (6 << 7) | 0x13]
    if enabled:
        instructions += [(0xbc4 << 20) | (7 << 15) | (1 << 12) | (10 << 7) | 0x73,
                         (0x9e1 << 20) | (2 << 12) | (11 << 7) | 0x73,
                         (0x9e1 << 20) | (5 << 12) | (12 << 7) | 0x73,
                         (0xbc4 << 20) | (2 << 12) | (13 << 7) | 0x73]
    else:
        instructions += [(0xbc4 << 20) | (2 << 12) | (10 << 7) | 0x73]
    payload = C.create_string_buffer(struct.pack("<" + "I" * len(instructions), *instructions))
    library.difftest_memcpy.argtypes, library.difftest_memcpy.restype = [C.c_uint64, C.c_void_p, C.c_size_t, C.c_bool], None
    library.difftest_memcpy(base, payload, 4 * len(instructions), True)
    fdi_init = library.difftest_fdi_init
    fdi_init.argtypes, fdi_init.restype = [C.c_void_p, C.c_uint32], C.c_int32
    init_data, init_pointer = guarded(32)
    C.memmove(init_pointer, struct.pack("<IIIIQQ", 0x10000, 32, 0, 0, fdi_epoch, 3), 32)
    init_before = bytes(init_data)
    require(fdi_init(init_pointer, 32) == (0 if enabled else -2), "FDI_INITIALIZATION_STATUS")
    require(bytes(init_data) == init_before, "FDI_INITIALIZATION_INPUT_CHANGED")
    library.difftest_exec.argtypes, library.difftest_exec.restype = [C.c_uint64], None
    for _ in instructions:
        library.difftest_exec(1)
    final = read("regcpy", 1400)
    final_csrs = read("csrcpy", 32768)
    require(final[6] == sentinel + 7 and final[64] == 3, "ORDINARY_REFERENCE_EXECUTION_MISMATCH")
    require(final_csrs[0x340] == csrs[0x340], "CSR_SENTINEL_EXECUTION_DRIFT")
    if enabled:
        require(list(final[10:14]) == [0, 0x7c2, 0x7c2, 0x3d] and final[82] == base + 20,
                "FDI_CSR_EXECUTION_PROBE_MISMATCH")
    else:
        require(final[10] == sentinel and final_csrs[0x342] == 2 and final_csrs[0x341] == base + 4
                and final[82] == base + 0x1000, "FDI_OFF_ILLEGAL_PROBE_MISMATCH")
    fdi_current = fdi_snapshot("get_state", 1, fdi_epoch, final[82], [0x3d, 0] + [0] * 50)
    stubs = {}
    if not enabled:
        for name, size in (("init", 32), ("raise_event", 64), ("get_state", 112), ("read_tx", 64)):
            function = getattr(library, "difftest_uit_" + name)
            function.argtypes, function.restype = [C.c_void_p, C.c_uint32], C.c_int32
            data, ptr = guarded(size)
            stubs[name] = function(ptr, size)
            guards(data, size, name)
        function = library.difftest_uit_exec
        function.argtypes, function.restype = [C.c_void_p, C.c_uint32, C.c_void_p, C.c_uint32], C.c_int32
        request, request_ptr = guarded(64)
        response, response_ptr = guarded(64)
        stubs["exec"] = function(request_ptr, 64, response_ptr, 64)
        guards(request, 64, "exec request")
        guards(response, 64, "exec result")
        require(all(value == -2 for value in stubs.values()), "OFF_PROTOCOL_STUB_NOT_REJECTING")
    return {"status": "PASS", "capabilities": caps, "symbols": symbols,
            "reference": {"path": str(reference), "sha256": digest(reference), "loaded_maps": loaded},
            "regcpy_bytes": 1400, "csrcpy_bytes": 32768, "canary_bytes_each_side": 32,
            "regcpy_sentinel": sentinel, "csrcpy_sentinel": csrs[0x340],
            "ordinary_exec_calls": len(instructions), "instruction_words": instructions,
            "final_x6": final[6], "final_x10_x13": list(final[10:14]), "final_pc": final[82],
            "fdi_csr_smoke": enabled, "fdi_off_illegal": not enabled, "stub_probes": stubs,
            "uit_initializations": 0, "dut_executions": 0,
            "scope": "Reference ABI, encoded CSR smoke and independent FDI export; no DUT transport/comparison validation",
            "reference_fdi_caps": fdi_caps, "reference_fdi_reset": fdi_reset, "reference_fdi_current": fdi_current,
            "reference_fdi_reset_validated": enabled, "reference_fdi_export_validated": enabled,
            "reference_fdi_disabled_rejections_validated": not enabled,
            "dut_fdi_transport_validated": False, "fdi_difftest_comparison": False, "uit_fdi_policy": False,
            "full_a02_on_admission": False}


def build(args):
    require(socket.gethostname() == HOST, "EXECUTION_HOST_MISMATCH")
    require(args.mode == "shared", "DASICS_STANDALONE_UNSUPPORTED: this builder supports shared references only")
    require(1 <= args.jobs <= 8, "M01_BUILD_JOB_BUDGET: jobs must be between 1 and 8")
    integration = args.integration_root.resolve(strict=True)
    original_helper = integration / "scripts/simulation/dasics_development_common.py"
    # Load the frozen helper, so repository helpers cannot change during the build.
    require(original_helper.is_file(), "MISSING_INTEGRATION_EVIDENCE_HELPER")
    output = args.output.absolute()
    require(output == output.resolve(), "OUTPUT_PATH_ALIAS")
    require(output.is_relative_to(integration / "build/dasics" / args.evidence_task), "OUTPUT_OUTSIDE_TASK_EVIDENCE_ROOT")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir(exist_ok=False)
    drivers = output / "drivers"
    drivers.mkdir()
    shutil.copyfile(original_helper, drivers / original_helper.name)
    shutil.copyfile(Path(__file__), drivers / Path(__file__).name)
    common = load_module(drivers / original_helper.name, "m01_frozen_common")
    record = {"status": "RUNNING", "started": common.now(), "host": HOST,
              "argv": [sys.executable, "-B", *sys.argv], "dasics": args.dasics,
              "mode": args.mode, "jobs": args.jobs, "output": str(output), "evidence_task": args.evidence_task}
    common.write_json(output / "started.json", record)
    try:
        enabled = args.dasics == "on"
        nemu = integration / "dep/nemu"
        softfloat = integration / "kmh/hardware/xs-gen/fudian/berkeley-softfloat-3"
        defconfig = "riscv64-xs-dasics-ref_defconfig" if enabled else "riscv64-xs-ref_defconfig"
        for path in (nemu / "configs" / defconfig, softfloat / "COPYING.txt",
                     softfloat / "source/RISCV/specialize.h", softfloat / "build/Linux-x86_64-GCC/Makefile"):
            require(path.is_file(), f"MISSING_LOCAL_DEPENDENCY: {path}; downloads are forbidden")
        metadata, inputs = output / "source-metadata", output / "inputs"
        snapshots = {}
        for label, original in (("nemu", nemu), ("softfloat", softfloat)):
            snapshots[label] = common.freeze_repository(original, inputs / label, metadata, label)
        definitions = output / "definitions"
        definitions.mkdir()
        for name in DEFINITIONS:
            shutil.copyfile(integration / "config" / name, definitions / name)
        common.write_json(output / "input-manifest.json", {
            "source_inputs": common.file_manifest(inputs), "definitions": common.file_manifest(definitions),
            "drivers": common.file_manifest(drivers), "helper_source": str(original_helper),
            "helper_sha256": common.digest(drivers / original_helper.name)})
        common.write_json(output / "source-identity.json", {name: data["identity"] for name, data in snapshots.items()})
        source = output / "source"
        shutil.copytree(inputs / "nemu", source, symlinks=True)
        shutil.copytree(inputs / "softfloat", source / "resource/softfloat/repo", symlinks=True)
        source_files = common.file_manifest(source)
        common.write_json(output / "build-source-files.json", source_files)
        for name in ("build", "tmp", "cache"):
            (output / name).mkdir()
        tools = {name: common.tool_identity("/usr/bin/" + name)
                 for name in ("gcc", "g++", "make", "nm", "readelf", "ar", "ld", "flex", "bison", "strace")}
        tools["python"] = common.tool_identity(sys.executable)
        if shutil.which("ccache", path="/usr/bin:/bin"):
            tools["ccache"] = common.tool_identity("/usr/bin/ccache")
        common.write_json(output / "tools.json", tools)
        env = common.controlled_environment({"NEMU_HOME": str(source), "TMPDIR": str(output / "tmp"),
            "CCACHE_DIR": str(output / "cache"), "PYTHONDONTWRITEBYTECODE": "1",
            "GIT_CEILING_DIRECTORIES": str(output), "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": "/dev/null", "CCACHE_CONFIGPATH": "/dev/null"})
        checker = load_module(source / "scripts/check-dasics-config.py", "m01_config_check")
        require(checker.check(source / "configs" / defconfig) == enabled, "DEFCONFIG_REQUEST_MISMATCH")
        make = ["/usr/bin/make", "-C", str(source), "git_commit="]
        common.run_command(output, "configure", [*make, defconfig], source, env, trace=True)
        require(checker.check(source / ".config", source / "include/generated/autoconf.h",
                              source / "configs" / defconfig) == enabled, "GENERATED_REQUEST_MISMATCH")
        generated = checker.configuration(source / ".config")
        for name in ("CONFIG_ISA64", "CONFIG_SHARE", "CONFIG_RVV", "CONFIG_RVH", "CONFIG_RV_SMSTATEEN", "CONFIG_FPU_SOFT"):
            require(generated.get(name) == "y", "REFERENCE_REQUIRED_CONFIGURATION: " + name)
        for name in ("CONFIG_LIGHTQS", "CONFIG_MULTICORE_DIFF"):
            require(generated.get(name) != "y", "REFERENCE_UNSUPPORTED_CONFIGURATION: " + name)
        configuration = {"dasics": enabled, "shared": True, "defconfig": defconfig,
                         "generated": generated, "config_sha256": common.digest(source / ".config"),
                         "autoconf_sha256": common.digest(source / "include/generated/autoconf.h"),
                         "uit_wire_version": 0x10000, "standalone_on": "UNSUPPORTED"}
        common.write_json(output / "configuration.json", configuration)
        native = common.run_command(output, "native", [*make, f"BUILD_DIR={output / 'build'}", "-j", str(args.jobs)],
                                    source, env, trace=True)
        observed = common.load_json(Path(native["observed_inputs"]))
        sf_commands = [item["call"] for item in observed["executions"]
                       if '"gcc", "-c"' in item["call"] and '"-DSOFTFLOAT_FAST_INT64"' in item["call"]]
        require(sf_commands and all('"-fPIC"' in item and "source/RISCV" in item for item in sf_commands),
                "SOFTFLOAT_ACTUAL_PIC_RISCV_EVIDENCE_MISSING")
        common.write_json(output / "softfloat-compile-evidence.json", {"commands": sf_commands, "trace": native["trace"]})
        common.verify_manifest(source, source_files)
        for label, snapshot in snapshots.items():
            common.verify_manifest(inputs / label, snapshot["files"], allow_generated=False)
        require(common.digest(source / ".config") == configuration["config_sha256"] and
                common.digest(source / "include/generated/autoconf.h") == configuration["autoconf_sha256"],
                "GENERATED_CONFIGURATION_DRIFT")
        reference = output / "build/riscv64-nemu-interpreter-so"
        require(reference.is_file(), "REFERENCE_ARTIFACT_MISSING")
        probe_output = output / "probe.json"
        command = [str(Path(sys.executable).resolve()), "-B", str(drivers / Path(__file__).name),
                   "--probe-child", str(reference), str(probe_output), args.dasics]
        receipt = common.run_command(output, "probe", command, output, env, trace=True, timeout_seconds=60)
        report = common.load_json(probe_output)
        require(report["status"] == "PASS", "REFERENCE_PROBE_FAILED")
        common.write_json(output / "compiled-capabilities.json", {
            "architecture_switch": "CONFIG_RV_DASICS", "HasFDI": enabled,
            "uit_enabled_features": report["capabilities"]["enabled_features"], "uit_wire": report["capabilities"],
            "model_implemented": ["baseline", "fdi_csrs"] if enabled else ["baseline"],
            "validated": ["ordinary_abi", "ordinary_addi", "fdi_csr_smoke" if enabled else "fdi_off_illegal"],
            "model_fdi_observation": "encoded CSR reads to ordinary GPRs" if enabled else None,
            "reference_fdi_caps": report["reference_fdi_caps"],
            "reference_fdi_reset_validated": report["reference_fdi_reset_validated"],
            "reference_fdi_export_validated": report["reference_fdi_export_validated"],
            "reference_fdi_disabled_rejections_validated": report["reference_fdi_disabled_rejections_validated"],
            # These fields describe validation scope, not inferred hardware capabilities.
            "dut_fdi_transport_validated": False, "fdi_difftest_comparison": False, "uit_fdi_policy": False,
            "scope": "Reference export only; DUT transport/comparison and complete FDI/UIT composition are unvalidated",
            "full_a02_on_admission": False, "probe": "probe.json", "probe_exit_code": receipt["exit_code"]})
        artifact_paths = [reference, source / ".config", source / "include/generated/autoconf.h",
                          source / "include/config/auto.conf", source / "lib-include/difftest-user-timer.h",
                          source / "resource/softfloat/repo/build/Linux-x86_64-GCC/softfloat.a",
                          output / "configuration.json", output / "compiled-capabilities.json", probe_output,
                          output / "input-manifest.json", output / "tools.json", output / "source-identity.json"]
        common.write_json(output / "artifacts.json", {
            str(path.relative_to(output)): {"sha256": common.digest(path), "bytes": path.stat().st_size}
            for path in artifact_paths})
        record.update(status="BUILT", reference=str(reference), reference_sha256=common.digest(reference))
    except Exception as error:
        record.update(status="FAILED", error=str(error))
    record["finished"] = common.now()
    common.write_json(output / "result.json", record)
    print(json.dumps(record, sort_keys=True))
    return 0 if record["status"] == "BUILT" else 1


def main():
    if len(sys.argv) == 5 and sys.argv[1] == "--probe-child":
        reference, output, selection = Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
        require(selection in ("off", "on"), "INVALID_DASICS_SELECTION")
        with output.open("x") as stream:
            json.dump(probe_child(reference.resolve(strict=True), selection == "on"), stream, indent=2)
            stream.write("\n")
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--integration-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dasics", choices=("off", "on"), required=True)
    parser.add_argument("--evidence-task", choices=("m01-nemu-csr", "d01-state-record"), default="m01-nemu-csr")
    parser.add_argument("--mode", choices=("shared", "standalone"), default="shared")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    try:
        return build(args)
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
