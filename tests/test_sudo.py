from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SudoIntegrationTests(unittest.TestCase):
    def test_upstream_sudo_source_is_pinned(self) -> None:
        manifest = json.loads((ROOT / "build/sources/sources.json").read_text())
        source = next(item for item in manifest["sources"] if item["name"] == "sudo")
        self.assertEqual(source["version"], "1.9.17p2")
        self.assertEqual(source["status"], "pinned")
        self.assertEqual(source["url"], "https://www.sudo.ws/sudo/dist/sudo-1.9.17p2.tar.gz")
        self.assertEqual(len(source["sha256"]), 64)

    def test_builds_static_sudo_for_both_architectures(self) -> None:
        script = (ROOT / "build/scripts/build-sudo.sh").read_text()
        for expected in ("--without-pam", "--disable-openssl", "--disable-shared", "--enable-static-sudoers", "-all-static",
                         "--disable-shared-libutil", "--with-rundir=/run/sudo",
                         "chmod 4755", "visudo", "readelf -l"):
            self.assertIn(expected, script)
        self.assertIn("fakeroot -- make DESTDIR=\"$ROOTFS\" install-binaries", script)
        self.assertIn("VANTOR_SUDO_ARCH", script)
        self.assertIn('export CFLAGS="-Os -fno-ident"', script)
        self.assertIn('CFLAGS="$BUILD_CFLAGS" LDFLAGS="$BUILD_LDFLAGS"', script)
        self.assertIn("Keep configure probes dynamically linkable", script)
        self.assertIn("-march=i486", script)

    def test_live_sudo_policy_requires_password_and_is_retained(self) -> None:
        rootfs = (ROOT / "tools/prepare-rootfs.py").read_text()
        installer = (ROOT / "installer/vantor-install").read_text()
        self.assertIn('etc/sudoers.d/99-live', rootfs)
        self.assertIn("live ALL=(ALL:ALL) ALL", rootfs)
        self.assertIn("live:$6$VANTORlive$", rootfs)
        self.assertIn("root ALL=(ALL:ALL) ALL", rootfs)
        self.assertIn("%wheel ALL=(ALL:ALL) ALL", rootfs)
        self.assertIn('etc/sudoers.d/00-root', rootfs)
        self.assertIn('root ALL=(ALL:ALL) ALL', installer)
        self.assertIn('live ALL=(ALL:ALL) ALL', installer)
        forbidden = 'rm -f ' + chr(34) + '$target/etc/sudoers.d/99-live' + chr(34)
        self.assertNotIn(forbidden, installer)
        self.assertNotIn('NOPASSWD', installer + rootfs)

    def test_initramfs_preserves_setuid_root_ownership(self) -> None:
        script = (ROOT / "build/scripts/build-initramfs.sh").read_text()
        self.assertIn('"$ROOTFS/usr/bin/sudo"', script)
        self.assertIn("stat -c", script)
        self.assertIn("fakeroot -- sh -c", script)
        self.assertIn('chown -hR 0:0 "$rootfs"', script)
        self.assertIn('chmod 4755 "$rootfs/usr/bin/sudo"', script)
        for required in ("etc/sudoers.d/00-root", "etc/sudoers.d/10-wheel",
                         "etc/sudoers.d/99-live", "visudo", "policy is incorrect",
                         "mode 0440", "Live account is not a member of wheel"):
            self.assertIn(required, script)

    def test_make_and_ci_include_sudo(self) -> None:
        makefile = (ROOT / "Makefile").read_text()
        self.assertIn("sudo-legacy", makefile)
        self.assertIn("$(MAKE) sudo", makefile)
        self.assertIn("$(MAKE) sudo-legacy", makefile)
        for workflow in (".github/workflows/build-userspace.yml",
                         ".github/workflows/build-image.yml",
                         ".github/workflows/build-legacy-image.yml"):
            content = (ROOT / workflow).read_text()
            self.assertIn("build-sudo.sh", content)
            self.assertIn("fakeroot", content)


if __name__ == "__main__":
    unittest.main()
