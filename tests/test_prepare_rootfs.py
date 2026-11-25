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
    def test_creates_identity_and_early_init(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "rootfs"
            result = subprocess.run(
                [sys.executable, str(BUILDER), "--output", str(output)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('ID=vantor', (output / "etc/os-release").read_text())
            self.assertIn("ONE SYSTEM. EVERY GENERATION.", (output / "etc/motd").read_text())
            self.assertTrue((output / "init").stat().st_mode & 0o111)
            self.assertTrue((output / "usr/share/vantor/branding/vantor-mark.svg").is_file())
            brand = json.loads((output / "etc/vantor-brand.json").read_text())
            self.assertEqual(brand["brand"], "VANTOR Linux")

    def test_refuses_nonempty_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "rootfs"
            output.mkdir()
            (output / "keep").write_text("safe")
            result = subprocess.run(
                [sys.executable, str(BUILDER), "--output", str(output)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((output / "keep").read_text(), "safe")


if __name__ == "__main__":
    unittest.main()
