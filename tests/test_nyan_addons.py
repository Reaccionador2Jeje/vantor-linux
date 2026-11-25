from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADDONS = (
    "vantor-about",
    "vantor-doctor",
    "vantor-netdiag",
    "vantor-logview",
    "vantor-config-backup",
    "vantor-mountinfo",
)


class NyanAddonTests(unittest.TestCase):
    def test_every_addon_is_posix_shell_syntax_valid(self) -> None:
        shell = shutil.which("sh")
        if not shell:
            self.skipTest("POSIX shell is unavailable")
        for name in ADDONS:
            with self.subTest(addon=name):
                path = ROOT / "packages/addons" / name
                self.assertTrue(path.is_file(), f"missing addon: {name}")
                result = subprocess.run(
                    [shell, "-n", str(path)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_extras_workflow_publishes_addons_to_both_architectures(self) -> None:
        workflow = (ROOT / ".github/workflows/build-nyan-extras.yml").read_text()
        builder = (ROOT / "tools/build-nyan-extras.sh").read_text()
        for name in ADDONS:
            with self.subTest(addon=name):
                self.assertIn(name, builder)
                self.assertIn(name, workflow)
        self.assertIn("for arch in x86_64 i486", workflow)
        self.assertIn("packages/addons/**", workflow)


if __name__ == "__main__":
    unittest.main()
