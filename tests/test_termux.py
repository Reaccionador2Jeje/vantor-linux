from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERMUX = ROOT / "tools" / "termux"


class TermuxIntegrationTests(unittest.TestCase):
    def test_termux_scripts_have_valid_shell_syntax(self) -> None:
        for name in ("vantor", "install-vantor", "vantor-pd"):
            path = TERMUX / name
            self.assertTrue(path.is_file(), f"missing {path}")
            result = subprocess.run(["sh", "-n", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, f"{name}: {result.stderr}")

    def test_launcher_supports_doctor_and_arbitrary_commands(self) -> None:
        source = (TERMUX / "vantor").read_text()
        self.assertIn("host_doctor()", source)
        self.assertIn("proot --link2symlink -0 -r", source)
        self.assertIn('/usr/bin/vantor-termux-shell "$@"', source)
        self.assertIn("VANTOR_ROOTFS", source)

    def test_installer_verifies_release_checksum_and_uses_proot_distro(self) -> None:
        source = (TERMUX / "install-vantor").read_text()
        self.assertIn("sha256sum -c -", source)
        self.assertIn('proot-distro install --name vantor "$WORK/$ARCHIVE"', source)
        self.assertIn('uname -m', source)
        self.assertIn("already exists", source)

    def test_proot_distro_login_wrapper_preserves_command_arguments(self) -> None:
        source = (TERMUX / "vantor-pd").read_text()
        self.assertIn("proot-distro login vantor -- /usr/bin/vantor-termux-shell", source)
        self.assertIn('proot-distro login vantor -- "$@"', source)
