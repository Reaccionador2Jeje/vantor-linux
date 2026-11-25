from __future__ import annotations

import io
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTRACTOR = ROOT / "tools" / "extract-source.py"


class ExtractSourceTests(unittest.TestCase):
    def make_archive(self, path: Path, member_name: str, payload: bytes = b"vantor-test") -> None:
        info = tarfile.TarInfo(member_name)
        info.size = len(payload)
        with tarfile.open(path, "w:gz") as archive:
            archive.addfile(info, io.BytesIO(payload))

    def test_extracts_normal_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            archive = base / "source.tar.gz"
            destination = base / "out"
            self.make_archive(archive, "source/README")
            result = subprocess.run(
                [sys.executable, str(EXTRACTOR), str(archive), str(destination)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((destination / "source" / "README").read_bytes(), b"vantor-test")

    def test_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            archive = base / "malicious.tar.gz"
            destination = base / "out"
            self.make_archive(archive, "../escape.txt")
            result = subprocess.run(
                [sys.executable, str(EXTRACTOR), str(archive), str(destination)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((base / "escape.txt").exists())
            self.assertFalse(destination.exists())

    def test_refuses_existing_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            archive = base / "source.tar.gz"
            destination = base / "out"
            destination.mkdir()
            self.make_archive(archive, "source/README")
            result = subprocess.run(
                [sys.executable, str(EXTRACTOR), str(archive), str(destination)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
