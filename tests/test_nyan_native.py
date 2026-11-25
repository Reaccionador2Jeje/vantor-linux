from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NyanNativeBuildTests(unittest.TestCase):
    def test_native_builders_are_valid_bash(self) -> None:
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("Bash is unavailable")
        for name in ("build-nyan-native.sh", "build-nyan-htop.sh"):
            result = subprocess.run(
                [bash, "-n", str(ROOT / "tools" / name)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, f"{name}: {result.stderr}")

    def test_builders_pin_sources_and_both_cpu_toolchains(self) -> None:
        nano = (ROOT / "tools/build-nyan-native.sh").read_text()
        htop = (ROOT / "tools/build-nyan-htop.sh").read_text()
        for value in (
            "x86_64-linux-musl-cross", "i486-linux-musl-cross",
            "c5d410d9f82a4f24c549fe5d24f988f85b2679b452413a9f7e5f7b956f2fe7ea",
            "1b7eceb2022f4a664028dd314c5c44332b601bd271e40f0934b4bc8fd3b0fcf5",
            "nano-9.2.tar.xz",
            "05ecb99247b782e8a5b3a25ed4101dd034b0236902f7449bc9795b717642f7e9",
            "ncurses-6.6.tar.gz",
            "355b4cbbed880b0381a04c46617b7656e362585d52e9cf84a67e2009b749ff11",
            "qemu-i386 -cpu 486", "readelf",
        ):
            with self.subTest(value=value):
                self.assertIn(value, nano)
        for value in (
            "htop-3.4.1.tar.xz",
            "904f7d4580fc11cffc7e0f06895a4789e0c1c054435752c151e812fead9f6220",
            "ncurses-6.6.tar.gz", "qemu-i386 -cpu 486", "readelf",
        ):
            with self.subTest(value=value):
                self.assertIn(value, htop)

    def test_native_workflow_builds_multiple_packages_in_parallel_matrix(self) -> None:
        workflow = (ROOT / ".github/workflows/build-nyan-native.yml").read_text()
        self.assertIn("package: nano", workflow)
        self.assertIn("package: htop", workflow)
        self.assertIn("arch: x86_64", workflow)
        self.assertIn("arch: i486", workflow)
        self.assertIn("vantor-nyan-native-publish", workflow)
        self.assertNotIn("build-image.yml", workflow)
        self.assertNotIn("build-kernel.yml", workflow)


if __name__ == "__main__":
    unittest.main()
