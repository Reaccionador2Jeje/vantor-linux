from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class VantorWebsiteTests(unittest.TestCase):
    def test_worker_source_is_valid_javascript_when_node_is_available(self) -> None:
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is unavailable")
        result = subprocess.run(
            [node, "--check", str(ROOT / "website" / "worker.js")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_official_site_has_complete_navigation_and_sections(self) -> None:
        source = (ROOT / "website" / "worker.js").read_text()
        for section in (
            'id="sistema"',
            'id="ediciones"',
            'id="arquitectura"',
            'id="instalar"',
            'id="documentacion"',
        ):
            with self.subTest(section=section):
                self.assertIn(section, source)
        for edition in ("VANTOR Minimal", "VANTOR Legacy", "VANTOR Termux"):
            self.assertIn(edition, source)
        self.assertIn("Nyan Community Mirror", source)
        self.assertIn("prefers-reduced-motion", source)
        self.assertNotIn("__BACKTICK__", source)

    def test_site_is_honest_about_iso_validation_status(self) -> None:
        source = (ROOT / "website" / "worker.js").read_text()
        self.assertIn("ISO en validación", source)
        self.assertIn("no se presenta todavía como una versión estable", source)
        self.assertIn("no es una ISO", source)


if __name__ == "__main__":
    unittest.main()
