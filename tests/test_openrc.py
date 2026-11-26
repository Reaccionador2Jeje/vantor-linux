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

    def test_openrc_build_uses_upstream_install_inventory(self) -> None:
        builder = (ROOT / "build/scripts/build-openrc.sh").read_text()
        validator = (ROOT / "tools/validate-openrc-install.py").read_text()
        initramfs = (ROOT / "build/scripts/build-initramfs.sh").read_text()

        self.assertIn("meson setup", builder)
        self.assertIn("--prefix=/usr --bindir=sbin --sbindir=sbin", builder)
        self.assertIn("-Dsysvinit=true", builder)
        self.assertNotIn("-Dsysvinit=false", builder)
        self.assertIn("meson compile", builder)
        self.assertIn("openrc-init", builder)
        self.assertIn("ln -sfn /sbin/openrc-init", builder)
        self.assertIn("tools/validate-openrc-install.py", builder)
        self.assertGreater(builder.index("tools/validate-openrc-install.py"), builder.index("link_service default localmount"))
        self.assertNotIn("rc_bin_commands=(", builder)
        self.assertNotIn("rc_sbin_commands=(", builder)
        self.assertIn('["meson", "introspect", "--targets"', validator)
        self.assertIn('target.get("type") != "executable"', validator)
        self.assertIn('target.get("installed")', validator)
        self.assertIn("rc-service", validator)
        self.assertIn("rc-abort", validator)
        self.assertIn("not OpenRC", initramfs)
        self.assertIn("static", builder)

    def test_validator_covers_architecture_and_linkage(self) -> None:
        validator = (ROOT / "tools/validate-openrc-install.py").read_text()
        self.assertIn("Advanced Micro Devices X86-64", validator)
        self.assertIn("Intel 80386", validator)
        self.assertIn('"INTERP" in program.stdout', validator)
        self.assertIn("missing or non-executable installed target", validator)
        self.assertIn("Meson reported no installed executable payloads under /usr", validator)
        self.assertIn("broken runlevel service link", validator)
        self.assertIn("runlevels.rglob", validator)
        self.assertIn("usr/bin/", validator)

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
