#!/usr/bin/env python3
"""Reject retired selectors and unsupported DASICS requests before Kconfig."""

import argparse
from pathlib import Path
import re


RETIRED = ("CONFIG_RV_USER_TIMER", "CONFIG_DIFFTEST_UIT")
REQUIRED = ("CONFIG_SHARE", "CONFIG_RVH", "CONFIG_RV_SMSTATEEN")
UNSUPPORTED = ("CONFIG_LIGHTQS", "CONFIG_MULTICORE_DIFF", "CONFIG_MODE_USER")
RETIRED_CONFIGS = ("riscv64-xs-uit06-ref_defconfig", "riscv64-xs-uit06-off-ref_defconfig")


def configuration(path):
    text = path.read_text()
    for name in RETIRED:
        if re.search(r"\b" + name + r"\b", text):
            raise ValueError(f"RETIRED_DASICS_SELECTOR: {name}; select CONFIG_RV_DASICS instead")
    values = {}
    for line in text.splitlines():
        match = re.fullmatch(r"(CONFIG_[A-Z0-9_]+)=(.*)", line)
        if match:
            name, value = match.groups()
            if name in values:
                raise ValueError(f"DUPLICATE_CONFIG_SELECTION: {name}")
            values[name] = value
    if "CONFIG_RV_DASICS" in values and values["CONFIG_RV_DASICS"] not in ("y", "n"):
        raise ValueError("INVALID_DASICS_SELECTION: CONFIG_RV_DASICS accepts only y or n")
    if values.get("CONFIG_RV_DASICS") == "y":
        if values.get("CONFIG_SHARE") != "y":
            raise ValueError("DASICS_STANDALONE_UNSUPPORTED: controlled timing inputs require shared reference")
        for name in REQUIRED:
            if values.get(name) != "y":
                raise ValueError(f"DASICS_REQUIRED_CONFIGURATION: {name}")
        for name in UNSUPPORTED:
            if values.get(name) in ("y", "m"):
                raise ValueError(f"DASICS_EXECUTION_MODE_UNSUPPORTED: {name}")
    return values


def check(path, header=None, requested=None):
    if path.name in RETIRED_CONFIGS:
        raise ValueError("RETIRED_UIT_DEFCONFIG: use riscv64-xs-dasics-ref_defconfig or riscv64-xs-ref_defconfig")
    values = configuration(path)
    enabled = values.get("CONFIG_RV_DASICS") == "y"
    if requested is not None:
        wanted = configuration(requested).get("CONFIG_RV_DASICS") == "y"
        if enabled != wanted:
            raise ValueError("DASICS_REQUEST_GENERATED_MISMATCH")
    if header is not None:
        defines = dict(re.findall(r"^#define\s+(CONFIG_\w+)\s+(.*)$", header.read_text(), re.MULTILINE))
        for name in RETIRED:
            if name in defines:
                raise ValueError(f"RETIRED_DASICS_SELECTOR: {name} in generated header")
        if ("CONFIG_RV_DASICS" in defines) != enabled or (enabled and defines["CONFIG_RV_DASICS"] != "1"):
            raise ValueError("DASICS_CONFIG_HEADER_MISMATCH")
        if enabled:
            for name in REQUIRED:
                if defines.get(name) != "1":
                    raise ValueError(f"DASICS_REQUIRED_GENERATED_CONFIGURATION: {name}")
            for name in UNSUPPORTED:
                if name in defines:
                    raise ValueError(f"DASICS_EXECUTION_MODE_UNSUPPORTED: {name}")
    return enabled


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("configuration", type=Path)
    parser.add_argument("--header", type=Path)
    parser.add_argument("--requested", type=Path)
    args = parser.parse_args()
    try:
        check(args.configuration, args.header, args.requested)
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
