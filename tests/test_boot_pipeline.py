from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BootPipelineTests(unittest.TestCase):
    def test_qemu_smoke_test_requires_live_shell_motd(self):
        workflow = (ROOT / ".github/workflows/test-image-qemu.yml").read_text()
        self.assertIn("Welcome to VANTOR Linux Genesis", workflow)
        self.assertIn("GRUB branding alone is not a successful boot", workflow)
        self.assertIn(r'connection.sendall(f"screendump {screen}\n".encode())', workflow)

    def test_qemu_smoke_test_preserves_failure_diagnostics(self):
        workflow = (ROOT / ".github/workflows/test-image-qemu.yml").read_text()
        self.assertIn("Preserve QEMU boot diagnostics", workflow)
        self.assertIn("vantor-screen.ppm", workflow)
        self.assertIn("vantor-screen.txt", workflow)
        self.assertIn("qemu.log", workflow)

    def test_busybox_source_fetch_uses_retry_and_verified_mirrors(self):
        fetcher = (ROOT / "tools/fetch-sources.py").read_text()
        manifest = (ROOT / "build/sources/sources.json").read_text()
        self.assertIn("for attempt in range(1, 4)", fetcher)
        self.assertIn('entry.get("mirrors", [])', fetcher)
        self.assertIn("actual != expected", fetcher)
        self.assertIn("sources.buildroot.net/busybox-1.37.0.tar.bz2", manifest)

    def test_bootloader_has_normal_and_diagnostic_entries(self):
        grub = (ROOT / "boot/grub/grub.cfg").read_text()
        self.assertIn("VANTOR Linux — Live Genesis", grub)
        self.assertIn("VANTOR Linux — Live (Diagnostic mode)", grub)
        self.assertIn("initrd /boot/vantor-initramfs.cpio.gz", grub)


if __name__ == "__main__":
    unittest.main()
