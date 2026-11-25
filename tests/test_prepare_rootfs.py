from __future__ import annotations
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools" / "prepare-rootfs.py"

class PrepareRootfsTests(unittest.TestCase):
    def build_rootfs(self, output: Path) -> None:
        result = subprocess.run([sys.executable, str(BUILDER), "--output", str(output)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_creates_identity_and_vantor_core(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "rootfs"
            self.build_rootfs(output)
            self.assertIn("ID=vantor", (output / "etc/os-release").read_text())
            self.assertIn("ONE SYSTEM. EVERY GENERATION.", (output / "etc/motd").read_text())
            self.assertTrue((output / "init").stat().st_mode & 0o111)
            self.assertTrue((output / "sbin/vantor-init").stat().st_mode & 0o111)
            self.assertTrue((output / "usr/bin/vantorctl").stat().st_mode & 0o111)
            self.assertTrue((output / "usr/share/vantor/branding/vantor-mark.svg").is_file())
            brand = json.loads((output / "etc/vantor-brand.json").read_text())
            self.assertEqual(brand["brand"], "VANTOR Linux")
            self.assertEqual(brand["core"]["init"], "VANTOR Init 0.1.0")
            for script in ("init", "sbin/vantor-init", "usr/bin/vantorctl"):
                check = subprocess.run(["sh", "-n", str(output / script)], capture_output=True, text=True, check=False)
                self.assertEqual(check.returncode, 0, f"{script}: {check.stderr}")

    def test_refuses_nonempty_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "rootfs"
            output.mkdir()
            (output / "keep").write_text("safe")
            result = subprocess.run([sys.executable, str(BUILDER), "--output", str(output)], capture_output=True, text=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((output / "keep").read_text(), "safe")

if __name__ == "__main__":
    unittest.main()
