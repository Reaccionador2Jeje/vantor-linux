from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPERVISOR = ROOT / "core" / "services" / "vantor-service-supervisor"


class VantorServiceSupervisorTests(unittest.TestCase):
    def test_supervisor_has_valid_posix_shell_syntax(self) -> None:
        result = subprocess.run(
            ["sh", "-n", str(SUPERVISOR)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_unknown_restart_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            service = Path(temporary) / "service"
            service.write_text("#!/bin/sh\nexit 0\n")
            service.chmod(0o755)
            result = subprocess.run(
                ["sh", str(SUPERVISOR), "demo", str(service), "sometimes", "1",
                 str(Path(temporary) / "demo.log")],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)

    def test_on_failure_restarts_are_capped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            service = Path(temporary) / "service"
            log = Path(temporary) / "demo.log"
            service.write_text("#!/bin/sh\nexit 7\n")
            service.chmod(0o755)
            result = subprocess.run(
                ["sh", str(SUPERVISOR), "demo", str(service), "on-failure", "1", str(log)],
                capture_output=True,
                text=True,
                check=False,
                timeout=12,
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            contents = log.read_text()
            self.assertIn("restart attempt 5/5", contents)
            self.assertIn("restart limit reached", contents)


if __name__ == "__main__":
    unittest.main()
