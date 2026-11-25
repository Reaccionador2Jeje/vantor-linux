from __future__ import annotations

import subprocess
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / "desktop"


class DesktopGenesisTests(unittest.TestCase):
    def test_session_is_valid_shell_and_checks_dependencies(self) -> None:
        session = DESKTOP / "bin/vantor-session"
        self.assertTrue(session.stat().st_mode & 0o111)
        result = subprocess.run(["sh", "-n", str(session)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        source = session.read_text()
        for dependency in ("openbox", "tint2", "xsetroot"):
            self.assertIn(dependency, source)
        self.assertIn('openbox --config-file', source)
        self.assertIn('DISPLAY', source)
        self.assertIn('menu.xml', source)

    def test_session_fails_cleanly_without_x11(self) -> None:
        result = subprocess.run(
            ["sh", str(DESKTOP / "bin/vantor-session")],
            env={"PATH": "/usr/bin:/bin"}, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("DISPLAY is empty", result.stderr)

    def test_openbox_configuration_is_well_formed_xml(self) -> None:
        for relative in ("openbox/rc.xml", "openbox/menu.xml"):
            root = ET.parse(DESKTOP / relative).getroot()
            self.assertTrue(root.tag.endswith("openbox_config") or root.tag.endswith("openbox_menu"))

    def test_vantor_palette_and_shortcuts_are_present(self) -> None:
        config = (DESKTOP / "tint2/tint2rc").read_text()
        self.assertIn("#071321", (DESKTOP / "bin/vantor-session").read_text())
        self.assertIn("#0C1D30", config)
        self.assertIn("#00CFFF", config)
        self.assertTrue((DESKTOP / "themes/VANTOR/openbox-3/themerc").is_file())
        self.assertIn("<name>VANTOR</name>", (DESKTOP / "openbox/rc.xml").read_text())
        openbox = (DESKTOP / "openbox/rc.xml").read_text()
        for shortcut in ("W-Return", "W-e", "W-d", "C-A-Left", "C-A-Right"):
            self.assertIn(shortcut, openbox)

    def test_desktop_launcher_has_valid_entry(self) -> None:
        launcher = (DESKTOP / "applications/vantor-terminal.desktop").read_text()
        self.assertIn("[Desktop Entry]", launcher)
        self.assertIn("Exec=xterm", launcher)
        session = (DESKTOP / "xsessions/vantor.desktop").read_text()
        self.assertIn("Exec=/usr/bin/vantor-session", session)


if __name__ == "__main__":
    unittest.main()
