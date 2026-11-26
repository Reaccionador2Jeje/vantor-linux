from __future__ import annotations
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class OpenRCIntegrationTests(unittest.TestCase):
    def test_upstream_source_is_pinned(self) -> None:
        manifest = json.loads((ROOT / "build/sources/sources.json").read_text())
        source = next(item for item in manifest["sources"] if item["name"] == "openrc")
        self.assertEqual(source["version"], "0.64.1")
        self.assertEqual(source["status"], "pinned")
        self.assertEqual(source["url"], "https://github.com/OpenRC/openrc/archive/0.64.1.tar.gz")
        self.assertEqual(len(source["sha512"]), 128)

    def test_openrc_is_built_and_required_for_initramfs(self) -> None:
        builder = (ROOT / "build/scripts/build-openrc.sh").read_text()
        initramfs = (ROOT / "build/scripts/build-initramfs.sh").read_text()
        self.assertIn("meson setup", builder)
        self.assertIn("--prefix=/usr --bindir=sbin --sbindir=sbin", builder)
        self.assertIn("-Dsysvinit=true", builder)
        self.assertNotIn("-Dsysvinit=false", builder)
        self.assertIn("meson compile", builder)
        self.assertIn("openrc-init", builder)
        self.assertIn("ln -sfn /sbin/openrc-init", builder)
        self.assertIn("rc_bin_commands=(", builder)
        self.assertIn("rc_sbin_commands=(", builder)
        self.assertIn("checkpath openrc-user rc-depend", builder)
        self.assertNotIn("checkpath service openrc-user", builder)
        self.assertIn("rc-service rc-update rc-sstat rc-environ", builder)
        self.assertIn("rc-abort", builder)
        self.assertIn('verify_openrc_binary "$binary" "$ROOTFS/usr/lib/rc/bin/$binary"', builder)
        self.assertIn('verify_openrc_binary "$binary" "$ROOTFS/usr/lib/rc/sbin/$binary"', builder)
        self.assertIn("ln -sfn /usr/lib/rc/bin/checkpath", builder)
        self.assertIn("not OpenRC", initramfs)
        self.assertIn("static", builder)

    def test_openrc_0641_uses_rc_service_not_removed_service_alias(self) -> None:
        builder = (ROOT / "build/scripts/build-openrc.sh").read_text()
        self.assertIn("rc-service", builder)
        self.assertNotIn("checkpath service", builder)
        self.assertIn('verify_openrc_binary "$binary" "$ROOTFS/usr/sbin/$binary"', builder)

    def test_vantor_services_use_openrc(self) -> None:
        service = (ROOT / "tools/prepare-rootfs.py").read_text()
        self.assertIn("rc-service", service)
        self.assertIn("rc-update", service)
        for name in ("vantor-early", "vantor-modules", "vantor-network", "vantor-console"):
            script = ROOT / "core/openrc/init.d" / name
            self.assertTrue(script.is_file(), name)
            self.assertIn("#!/sbin/openrc-run", script.read_text())

if __name__ == "__main__":
    unittest.main()
