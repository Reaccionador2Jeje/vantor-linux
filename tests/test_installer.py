from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InstallerContractTests(unittest.TestCase):
    def test_installer_has_separate_guarded_bios_and_uefi_paths(self) -> None:
        script = (ROOT / "installer/vantor-install").read_text()
        self.assertIn('mode=$(ask "GRUB firmware mode"', script)
        self.assertIn('--target=i386-pc', script)
        self.assertIn('--target=x86_64-efi', script)
        self.assertIn('--efi-directory="$esp"', script)
        self.assertIn('--no-nvram --removable', script)
        self.assertIn('Type the exact whole-disk path to continue:', script)
        self.assertIn('Type INSTALL-UEFI to continue:', script)
        self.assertIn('UEFI ESP must be mounted as FAT', script)
        self.assertIn('refusing to install GRUB to a partition', script)

    def test_installer_refuses_live_root_and_requires_mounted_target(self) -> None:
        script = (ROOT / "installer/vantor-install").read_text()
        self.assertIn('refusing to modify the Live root', script)
        self.assertIn('target is not a mounted filesystem', script)
        self.assertIn('GRUB configuration is missing; prepare boot files first', script)

    def test_installer_shell_syntax(self) -> None:
        shell = shutil.which("sh")
        if not shell:
            self.skipTest("POSIX shell unavailable")
        result = subprocess.run([shell, "-n", str(ROOT / "installer/vantor-install")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
