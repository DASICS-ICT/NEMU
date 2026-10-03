#!/usr/bin/env python3
"""Build isolated on/off references and run the FDI lifecycle regression batch."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--integration-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jobs", type=int, choices=range(1, 9), default=8)
    args = parser.parse_args()
    root = args.integration_root.resolve(strict=True)
    output = args.output.resolve()
    if socket.gethostname() != "cmy-zgclab-eda":
        parser.error("only cmy-zgclab-eda is approved for this batch")
    if not output.is_relative_to(root / "build/dasics/d01-state-record"):
        parser.error("output must be in the approved D01 evidence tree")
    output.mkdir(parents=True, exist_ok=False)
    drivers, logs = output / "drivers", output / "logs"
    drivers.mkdir()
    logs.mkdir()
    source = root / "dep/nemu/tests/dasics"
    for name in ("run-fdi-batch.py", "build-reference.py"):
        shutil.copyfile(source / name, drivers / name)
    record = {"status": "RUNNING", "started": now(), "host": socket.gethostname(),
              "pid": os.getpid(), "jobs": args.jobs, "commands": []}
    result_path = output / "result.json"

    def persist():
        result_path.write_text(json.dumps(record, indent=2) + "\n")

    def run(name, command):
        entry = {"name": name, "command": command, "started": now(), "log": str(logs / (name + ".log"))}
        record["commands"].append(entry)
        with Path(entry["log"]).open("x") as log:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            entry["pid"] = child.pid
            persist()
            rc = child.wait()
        entry.update(exit_code=rc, finished=now())
        persist()
        print(json.dumps(entry), flush=True)
        if rc:
            raise RuntimeError(name + " failed with exit code " + str(rc))

    persist()
    try:
        for selection in ("on", "off"):
            candidate = output / ("reference-" + selection)
            run("build-" + selection, [sys.executable, "-B", str(drivers / "build-reference.py"),
                "--integration-root", str(root), "--output", str(candidate), "--dasics", selection,
                "--evidence-task", "d01-state-record", "--jobs", str(args.jobs)])
        for selection in ("on", "off"):
            candidate = output / ("reference-" + selection)
            tests = candidate / "source/tests/dasics"
            reference = candidate / "build/riscv64-nemu-interpreter-so"
            run("fdi-" + selection, [sys.executable, "-B", str(tests / "run-fdi-tests.py"),
                "--reference", str(reference), "--state", selection, "--jobs", str(args.jobs),
                "--output", str(output / ("fdi-" + selection))])
            selected = ["legacy-transport", "basic-rvv"]
            selected += (["reset", "independence", "alias", "reason", "host-transition",
                          "uit:abi", "uit:sample-program", "uit:import-rejected:regcpy", "uit:import-rejected:csrcpy"]
                         if selection == "on" else ["off-protocol", "off:3012:0", "off:3012:1"])
            command = [sys.executable, "-B", str(tests / "run-model-tests.py"),
                       "--reference", str(reference), "--state", selection, "--jobs", str(min(4, args.jobs)),
                       "--output", str(output / ("regression-" + selection))]
            for name in selected:
                command.extend(("--select", name))
            run("regression-" + selection, command)
        record["status"] = "PASS"
    except Exception as error:
        record.update(status="FAIL", error=str(error))
    record.update(finished=now(), exit_code=0 if record["status"] == "PASS" else 1)
    persist()
    (output / "exit-code").write_text(str(record["exit_code"]) + "\n")
    return record["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
