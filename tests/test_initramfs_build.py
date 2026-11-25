from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InitramfsBuildTests(unittest.TestCase):
    def test_builder_requires_busybox_and_init(self):
        script = (ROOT / "build/scripts/build-initramfs.sh").read_text()
        self.assertIn('"$ROOTFS/bin/busybox"', script)
        self.assertIn('"$ROOTFS/init"', script)
        self.assertIn("cpio", script)
        self.assertIn("gzip -t", script)

    def test_busybox_builder_fails_closed_on_unpinned_source(self):
        script = (ROOT / "build/scripts/build-busybox.sh").read_text()
        self.assertIn("--require-pinned --only busybox", script)
        self.assertIn("CONFIG_STATIC=y", script)
        self.assertIn("CONFIG_TC is not set", script)
        self.assertIn("CONFIG_PREFIX=", script)

    def test_iso_and_initramfs_output_contract_match(self):
        initramfs = (ROOT / "build/scripts/build-initramfs.sh").read_text()
        iso = (ROOT / "build/scripts/build-iso.sh").read_text()
        self.assertIn("build/work/initramfs/vantor-initramfs.cpio.gz", initramfs)
        self.assertIn('INITRAMFS="$WORK/initramfs/vantor-initramfs.cpio.gz"', iso)


if __name__ == "__main__":
    unittest.main()
