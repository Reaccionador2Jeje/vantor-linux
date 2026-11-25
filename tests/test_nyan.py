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
        catalog = self.root / "usr/share/nyan/catalog.tsv"
        catalog.parent.mkdir(parents=True)
        catalog.write_text("# package\tcategory\tstatus\tdescription\nbusybox\tsystem\tbundled\tCore shell and utilities\nsudo\tadmin\tplanned\tPrivilege elevation\n")
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
        index.write_text("\n".join(existing) + "\n")

    def run_nyan(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["sh", str(NYAN), *args], env=self.env, capture_output=True, text=True, check=False)

    def test_catalog_shows_bundled_and_planned_packages(self) -> None:
        result = self.run_nyan("catalog")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("busybox", result.stdout)
        self.assertIn("bundled", result.stdout)
        self.assertIn("sudo", result.stdout)
        self.assertIn("planned", result.stdout)

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

    def test_installs_published_development_profile(self) -> None:
        self.add_package("lua", "usr/bin/lua", b"lua-runtime")
        self.add_package("vantor-profile-development", "usr/share/vantor/profiles/development.txt", b"Development profile", "lua")
        self.assertEqual(self.run_nyan("update").returncode, 0)
        profiles = self.run_nyan("profiles")
        self.assertIn("development", profiles.stdout)
        self.assertIn("available", profiles.stdout)
        result = self.run_nyan("install-profile", "development")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / "usr/bin/lua").exists())
        self.assertTrue((self.root / "usr/share/vantor/profiles/development.txt").exists())

    def test_installs_minimal_profile_and_base_dependency(self) -> None:
        self.add_package("vantor-base-files", "etc/os-release", b"ID=vantor\\n")
        self.add_package("vantor-profile-minimal", "usr/share/vantor/profiles/minimal.txt", b"VANTOR Minimal", "vantor-base-files")
        self.assertEqual(self.run_nyan("update").returncode, 0)
        profiles = self.run_nyan("profiles")
        self.assertIn("minimal", profiles.stdout)
        self.assertIn("available", profiles.stdout)
        result = self.run_nyan("install-profile", "minimal")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / "etc/os-release").exists())
        self.assertTrue((self.root / "usr/share/vantor/profiles/minimal.txt").exists())

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


    def test_installed_listing_and_verify_detect_missing_files(self) -> None:
        self.add_package("inspectable", "usr/bin/inspectable", b"inspect me\\n")
        self.assertEqual(self.run_nyan("update").returncode, 0)
        self.assertEqual(self.run_nyan("install", "inspectable").returncode, 0)
        listing = self.run_nyan("installed")
        self.assertEqual(listing.returncode, 0, listing.stderr)
        self.assertIn("inspectable", listing.stdout)
        verified = self.run_nyan("verify", "inspectable")
        self.assertEqual(verified.returncode, 0, verified.stderr)
        (self.root / "usr/bin/inspectable").unlink()
        missing = self.run_nyan("verify", "inspectable")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("missing usr/bin/inspectable", missing.stderr)

    def test_root_configuration_selects_target_architecture(self) -> None:
        index_dir = self.repo / "repo" / "i486"
        package_dir = self.repo / "packages" / "i486"
        index_dir.mkdir()
        package_dir.mkdir()
        archive = package_dir / "arch-test.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            data = b"i486 package\n"
            info = tarfile.TarInfo("usr/share/arch-test")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        (index_dir / "Packages").write_text(
            "# VANTOR-PACKAGES 1\n"
            f"arch-test\t1.0\ti486\t{digest}\tarch-test.tar.gz\tLegacy test\n"
        )
        config = self.root / "etc/nyan.conf"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text('NYAN_ARCH="i486"\n')
        self.env.pop("NYAN_ARCH", None)
        updated = self.run_nyan("update")
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertIn("i486", updated.stdout)
        installed = self.run_nyan("install", "arch-test")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual((self.root / "usr/share/arch-test").read_text(), "i486 package\n")

if __name__ == "__main__":
    unittest.main()
