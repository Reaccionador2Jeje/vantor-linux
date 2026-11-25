from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class KernelBuildContractTests(unittest.TestCase):
    def test_linux_source_is_candidate_until_checksum_is_verified(self) -> None:
        manifest = json.loads((ROOT / "build/sources/sources.json").read_text())
        linux = next(item for item in manifest["sources"] if item["name"] == "linux")
        self.assertEqual(linux["version"], "6.18.65")
        self.assertEqual(linux["status"], "pinned")
        self.assertEqual(linux["sha256"], "c92606f956f09dc50b5a0e2af9e86763fce27ada1647de97f8d1ac8cfc95801d")
        self.assertIsNone(linux["sha512"])

    def test_kernel_builder_requires_pinned_source_and_builds_bzimage(self) -> None:
        script = (ROOT / "build/scripts/build-kernel.sh").read_text()
        self.assertIn("validate-sources.py --require-pinned --only linux", script)
        self.assertIn("x86_64_defconfig", script)
        self.assertIn("bzImage", script)
        self.assertIn("VIRTIO_BLK", script)
        self.assertIn("VIRTIO_NET", script)
        self.assertIn("FRAMEBUFFER_CONSOLE", script)
        self.assertIn("DRM_FBDEV_EMULATION", script)
        self.assertIn("DRM_BOCHS", script)

    def test_x86_64_kernel_workflow_builds_and_uploads_kernel(self) -> None:
        workflow = (ROOT / ".github/workflows/build-kernel.yml").read_text()
        self.assertIn("make kernel", workflow)
        self.assertIn("build/work/kernel/vantor-kernel", workflow)
        self.assertIn("actions/upload-artifact@v4", workflow)
        self.assertIn("CONFIG_FRAMEBUFFER_CONSOLE=y", workflow)
        self.assertIn("make check", workflow)

    def test_framebuffer_splash_renderer_is_valid_c(self) -> None:
        source = ROOT / "core/boot/vantor-fb-splash.c"
        self.assertTrue(source.is_file())
        compiler = shutil.which("cc")
        if compiler:
            result = subprocess.run(
                [compiler, "-fsyntax-only", str(source)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.skipTest("host C compiler is unavailable")

    def test_legacy_linux_source_is_pinned_to_upstream_checksum(self) -> None:
        manifest = json.loads((ROOT / "build/sources/sources.json").read_text())
        legacy = next(item for item in manifest["sources"] if item["name"] == "linux-legacy")
        self.assertEqual(legacy["version"], "6.1.193")
        self.assertEqual(legacy["status"], "pinned")
        self.assertEqual(legacy["sha256"], "e47276bbbc8aa191c5421ff2f6e0da87e25073042bc242e4afb1e53ab4ddcd80")

    def test_legacy_builder_targets_486sx(self) -> None:
        script = (ROOT / "build/scripts/build-kernel-legacy.sh").read_text()
        self.assertIn("--only \"$SOURCE_NAME\"", script)
        self.assertIn("i386_defconfig", script)
        self.assertIn("--enable M486SX", script)
        self.assertIn("--file \"$CONFIG\" --enable MATH_EMULATION", script)
        self.assertIn("bzImage", script)


if __name__ == "__main__":
    unittest.main()
