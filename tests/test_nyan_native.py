from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NyanNativeBuildTests(unittest.TestCase):
    BUILDERS = (
        "build-nyan-native.sh",
        "build-nyan-htop.sh",
        "build-nyan-dialog.sh",
        "build-nyan-curl.sh",
    )

    def test_native_builders_are_valid_bash(self) -> None:
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("Bash is unavailable")
        for name in self.BUILDERS:
            result = subprocess.run(
                [bash, "-n", str(ROOT / "tools" / name)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, f"{name}: {result.stderr}")

    def test_nano_and_htop_sources_are_pinned(self) -> None:
        nano = (ROOT / "tools/build-nyan-native.sh").read_text()
        htop = (ROOT / "tools/build-nyan-htop.sh").read_text()
        for value in (
            "x86_64-linux-musl-cross", "i486-linux-musl-cross",
            "c5d410d9f82a4f24c549fe5d24f988f85b2679b452f2fe7ea",
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

    def test_dialog_uses_signed_pinned_upstream_snapshot(self) -> None:
        dialog = (ROOT / "tools/build-nyan-dialog.sh").read_text()
        self.assertIn("ThomasDickey/dialog-snapshots", dialog)
        self.assertIn("e65d9f4ed89ce05eeb5a266e14804bcd71416bca", dialog)
        self.assertIn("ncurses-6.6.tar.gz", dialog)
        self.assertIn("qemu-i386 -cpu 486", dialog)
        self.assertIn("readelf", dialog)

    def test_curl_pins_tls_and_transfer_sources(self) -> None:
        curl = (ROOT / "tools/build-nyan-curl.sh").read_text()
        for value in (
            "curl-8.23.0.tar.xz",
            "8dadd7d2536a314f982ad05a651b713f426bf7d02cc2c76cffb9796f2218e6c5",
            "openssl-3.5.9.tar.gz",
            "603f5602e2eef00d77fbd429d34dcd5822bb301757a1bc9cdb24c670f1eb859a",
            "qemu-i386 -cpu 486",
            "OpenSSL/3.5.9",
            "ca-certificates.crt",
            "cacert.pem.sha256",
        ):
            with self.subTest(value=value):
                self.assertIn(value, curl)

    def test_native_workflow_builds_four_packages_and_publishes_successes_once(self) -> None:
        workflow = (ROOT / ".github/workflows/build-nyan-native.yml").read_text()
        for package in ("nano", "htop", "dialog", "curl"):
            self.assertIn(f"package: {package}", workflow)
            self.assertIn(f"publish_one {package}", workflow)
        self.assertIn("arch: x86_64", workflow)
        self.assertIn("arch: i486", workflow)
        self.assertIn("fail-fast: false", workflow)
        self.assertIn("needs: build", workflow)
        self.assertIn("Download successful build artifacts", workflow)
        self.assertNotIn("build-image.yml", workflow)
        self.assertNotIn("build-kernel.yml", workflow)


if __name__ == "__main__":
    unittest.main()
