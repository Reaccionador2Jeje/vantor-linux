from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NyanNativeBuildTests(unittest.TestCase):
    def test_native_builder_is_valid_bash(self) -> None:
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("Bash is unavailable")
        script = ROOT / "tools/build-nyan-native.sh"
        result = subprocess.run(
            [bash, "-n", str(script)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_native_builder_pins_sources_and_both_cpu_toolchains(self) -> None:
        script = (ROOT / "tools/build-nyan-native.sh").read_text()
        for value in (
            "x86_64-linux-musl-cross",
            "i486-linux-musl-cross",
            "c5d410d9f82a4f24c549fe5d24f988f85b2679b452413a9f7e5f7b956f2fe7ea",
            "1b7eceb2022f4a664028dd314c5c44332b601bd271e40f0934b4bc8fd3b0fcf5",
            "nano-9.2.tar.xz",
            "05ecb99247b782e8a5b3a25ed4101dd034b0236902f7449bc9795b717642f7e9",
            "ncurses-6.6.tar.gz",
            "355b4cbbed880b0381a04c46617b7656e362585d52e9cf84a67e2009b749ff11",
            "qemu-i386 -cpu 486",
            "readelf",
        ):
            with self.subTest(value=value):
                self.assertIn(value, script)

    def test_native_workflow_isolated_and_matrix_builds_both_architectures(self) -> None:
        workflow = (ROOT / ".github/workflows/build-nyan-native.yml").read_text()
        self.assertIn("matrix:", workflow)
        self.assertIn("arch: [x86_64, i486]", workflow)
        self.assertIn("build-nyan-native.sh", workflow)
        self.assertIn("vantor-nyan-native-publish", workflow)
        self.assertNotIn("build-image.yml", workflow)
        self.assertNotIn("build-kernel.yml", workflow)


if __name__ == "__main__":
    unittest.main()
