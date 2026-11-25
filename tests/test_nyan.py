from __future__ import annotations

import hashlib
import http.server
import io
import os
import shutil
import subprocess
import tarfile
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NYAN = ROOT / "packages" / "nyan" / "nyan"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args: object) -> None:
        pass


class NyanIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        (self.repo / "repo" / "x86_64").mkdir(parents=True)
        (self.repo / "packages" / "x86_64").mkdir(parents=True)
        handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(self.repo), **kwargs)
        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.root = self.base / "target-root"
        self.root.mkdir()
        self.env = dict(os.environ)
        self.env.update({
            "NYAN_ROOT": str(self.root),
            "NYAN_REPO": f"http://127.0.0.1:{self.server.server_port}",
            "NYAN_ARCH": "x86_64",
        })

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def make_archive(self, name: str, entries: list[tuple[str, bytes, str]]) -> tuple[Path, str]:
        archive = self.repo / "packages" / "x86_64" / f"{name}.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            for path, data, kind in entries:
                info = tarfile.TarInfo(path)
                if kind == "file":
                    info.size = len(data)
                    tar.addfile(info, io.BytesIO(data))
                elif kind == "symlink":
                    info.type = tarfile.SYMTYPE
                    info.linkname = "../../outside"
                    tar.addfile(info)
                elif kind == "traversal":
                    info.size = len(data)
                    tar.addfile(info, io.BytesIO(data))
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        row = f"{name}\t1.0\tx86_64\t{digest}\t{name}.tar.gz\tLanguage: test package\n"
        (self.repo / "repo" / "x86_64" / "Packages").write_text("# VANTOR-PACKAGES 1\n" + row)
        return archive, digest

    def add_package(self, name: str, path: str, data: bytes, dependencies: str = "") -> None:
        archive = self.repo / "packages" / "x86_64" / f"{name}.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            info = tarfile.TarInfo(path)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        index = self.repo / "repo" / "x86_64" / "Packages"
        existing = index.read_text().splitlines() if index.exists() else ["# VANTOR-PACKAGES 1"]
        existing.append(f"{name}\t1.0\tx86_64\t{digest}\t{name}.tar.gz\tTest package\t{dependencies}")
        index.write_text("\\n".join(existing) + "\\n")

    def run_nyan(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["sh", str(NYAN), *args], env=self.env, capture_output=True, text=True, check=False)

    def test_update_install_and_remove(self) -> None:
        self.make_archive("sample", [("usr/bin/sample", b"hello VANTOR\n", "file")])
        self.assertEqual(self.run_nyan("update").returncode, 0)
        listing = self.run_nyan("languages")
        self.assertIn("sample", listing.stdout)
        installed = self.run_nyan("install", "sample")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        target = self.root / "usr/bin/sample"
        self.assertEqual(target.read_text(), "hello VANTOR\n")
        removed = self.run_nyan("remove", "sample")
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertFalse(target.exists())

    def test_installs_dependencies_before_requested_package(self) -> None:
        self.add_package("runtime", "usr/lib/runtime.txt", b"runtime\\n")
        self.add_package("application", "usr/bin/application", b"app\\n", "runtime")
        self.assertEqual(self.run_nyan("update").returncode, 0)
        result = self.run_nyan("install", "application")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / "usr/lib/runtime.txt").exists())
        self.assertTrue((self.root / "usr/bin/application").exists())
        self.assertTrue((self.root / "var/lib/nyan/installed/runtime").exists())

    def test_rejects_dependency_cycles(self) -> None:
        self.add_package("alpha", "usr/share/alpha", b"a", "beta")
        self.add_package("beta", "usr/share/beta", b"b", "alpha")
        self.assertEqual(self.run_nyan("update").returncode, 0)
        result = self.run_nyan("install", "alpha")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("dependency cycle", result.stderr)

    def test_rejects_path_traversal(self) -> None:
        self.make_archive("badpath", [("../outside.txt", b"escape", "traversal")])
        self.assertEqual(self.run_nyan("update").returncode, 0)
        result = self.run_nyan("install", "badpath")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root.parent / "outside.txt").exists())

    def test_rejects_symlink_entries(self) -> None:
        self.make_archive("badlink", [("usr/bin/escape", b"", "symlink")])
        self.assertEqual(self.run_nyan("update").returncode, 0)
        result = self.run_nyan("install", "badlink")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsupported archive entry type", result.stderr)

    def test_refuses_to_overwrite_existing_files(self) -> None:
        self.make_archive("collision", [("usr/bin/existing", b"package", "file")])
        target = self.root / "usr/bin/existing"
        target.parent.mkdir(parents=True)
        target.write_text("system file")
        self.assertEqual(self.run_nyan("update").returncode, 0)
        result = self.run_nyan("install", "collision")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_text(), "system file")


if __name__ == "__main__":
    unittest.main()
