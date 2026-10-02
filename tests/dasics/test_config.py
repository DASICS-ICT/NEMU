"""Configuration guard regressions; no native compilation or dependency access."""

import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("dasics_config_guard", ROOT / "scripts/check-dasics-config.py")
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)
VALID_ON = "CONFIG_RV_DASICS=y\nCONFIG_SHARE=y\nCONFIG_RVH=y\nCONFIG_RV_SMSTATEEN=y\n"
VALID_HEADER = "".join("#define " + line.split("=")[0] + " 1\n" for line in VALID_ON.splitlines())


class ConfigGuardTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="dasics-config-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def fixture(self, name, text):
        path = self.root / name
        path.write_text(text)
        return path

    def test_valid_on_and_off(self):
        on = self.fixture("on", VALID_ON)
        header = self.fixture("autoconf.h", VALID_HEADER)
        self.assertTrue(GUARD.check(on, header, on))
        for text in ("CONFIG_RV_DASICS=n\n", "# CONFIG_RV_DASICS is not set\n", ""):
            with self.subTest(configuration=text):
                off = self.fixture("off", text)
                empty_header = self.fixture("off.h", "")
                self.assertFalse(GUARD.check(off, empty_header, off))

    def test_retired_selectors(self):
        for name in ("CONFIG_RV_USER_TIMER", "CONFIG_DIFFTEST_UIT"):
            for selection in (name + "=y\n", "# " + name + " is not set\n"):
                with self.subTest(selection=selection):
                    path = self.fixture("retired", selection)
                    with self.assertRaisesRegex(ValueError, "RETIRED_DASICS_SELECTOR"):
                        GUARD.check(path)

    def test_retired_defconfig_names(self):
        for name in ("riscv64-xs-uit06-ref_defconfig", "riscv64-xs-uit06-off-ref_defconfig"):
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, "RETIRED_UIT_DEFCONFIG"):
                    GUARD.check(self.root / name)

    def test_invalid_values_and_requested_values(self):
        off = self.fixture("off", "CONFIG_RV_DASICS=n\n")
        for value in ("m", "1", "0", "true", "", "y "):
            with self.subTest(value=value):
                invalid = self.fixture("invalid", "CONFIG_RV_DASICS=" + value + "\n")
                with self.assertRaisesRegex(ValueError, "INVALID_DASICS_SELECTION"):
                    GUARD.check(invalid)
                with self.assertRaisesRegex(ValueError, "INVALID_DASICS_SELECTION"):
                    GUARD.check(off, requested=invalid)

    def test_required_configuration(self):
        for name in ("CONFIG_SHARE", "CONFIG_RVH", "CONFIG_RV_SMSTATEEN"):
            with self.subTest(name=name):
                path = self.fixture("missing", VALID_ON.replace(name + "=y\n", ""))
                diagnostic = "DASICS_STANDALONE_UNSUPPORTED" if name == "CONFIG_SHARE" else "DASICS_REQUIRED_CONFIGURATION"
                with self.assertRaisesRegex(ValueError, diagnostic):
                    GUARD.check(path)

    def test_unsupported_configuration(self):
        for name in ("CONFIG_LIGHTQS", "CONFIG_MULTICORE_DIFF", "CONFIG_MODE_USER"):
            with self.subTest(name=name):
                path = self.fixture("unsupported", VALID_ON + name + "=y\n")
                with self.assertRaisesRegex(ValueError, "DASICS_EXECUTION_MODE_UNSUPPORTED"):
                    GUARD.check(path)

    def test_header_presence_and_value(self):
        off = self.fixture("off", "CONFIG_RV_DASICS=n\n")
        on = self.fixture("on", VALID_ON)
        for value in ("0", "1", "n"):
            with self.subTest(off_header_value=value):
                header = self.fixture("off.h", "#define CONFIG_RV_DASICS " + value + "\n")
                with self.assertRaisesRegex(ValueError, "DASICS_CONFIG_HEADER_MISMATCH"):
                    GUARD.check(off, header)
        for header_text in ("", VALID_HEADER.replace("CONFIG_RV_DASICS 1", "CONFIG_RV_DASICS 0")):
            with self.subTest(on_header=header_text):
                with self.assertRaisesRegex(ValueError, "DASICS_CONFIG_HEADER_MISMATCH"):
                    GUARD.check(on, self.fixture("on.h", header_text))

    def test_requested_state_mismatch(self):
        off = self.fixture("off", "CONFIG_RV_DASICS=n\n")
        on = self.fixture("on", VALID_ON)
        for generated, requested in ((off, on), (on, off)):
            with self.subTest(generated=generated.name):
                with self.assertRaisesRegex(ValueError, "DASICS_REQUEST_GENERATED_MISMATCH"):
                    GUARD.check(generated, requested=requested)

    def test_generated_dependencies(self):
        on = self.fixture("on", VALID_ON)
        for name in ("CONFIG_SHARE", "CONFIG_RVH", "CONFIG_RV_SMSTATEEN"):
            with self.subTest(name=name):
                header = self.fixture("missing.h", VALID_HEADER.replace("#define " + name + " 1\n", ""))
                with self.assertRaisesRegex(ValueError, "DASICS_REQUIRED_GENERATED_CONFIGURATION"):
                    GUARD.check(on, header)

    def test_make_external_selectors_rejected_before_configuration(self):
        environment = dict(os.environ)
        for name in ("CONFIG_RV_USER_TIMER", "CONFIG_DIFFTEST_UIT", "CONFIG_RV_DASICS"):
            environment.pop(name, None)
        # An invalid NEMU_HOME proves rejection precedes source/config parsing.
        environment["NEMU_HOME"] = str(self.root / "missing-nemu")
        for name in ("CONFIG_RV_USER_TIMER", "CONFIG_DIFFTEST_UIT", "CONFIG_RV_DASICS"):
            diagnostic = "DASICS_MAKE_SELECTION_UNSUPPORTED" if name == "CONFIG_RV_DASICS" else "RETIRED_DASICS_SELECTOR"
            for source in ("command", "environment"):
                for value in ("y", "n", ""):
                    with self.subTest(name=name, source=source, value=value):
                        command = ["make", "-n", "help"]
                        selected_env = dict(environment)
                        if source == "command":
                            command.append(name + "=" + value)
                        else:
                            selected_env[name] = value
                        result = subprocess.run(command, cwd=ROOT, env=selected_env,
                                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                text=True, timeout=10, check=False)
                        self.assertEqual(result.returncode, 2, result.stdout)
                        self.assertIn(diagnostic, result.stdout)
                        self.assertNotIn("is not a NEMU repo", result.stdout)


if __name__ == "__main__":
    unittest.main()
