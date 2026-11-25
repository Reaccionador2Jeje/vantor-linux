from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class KernelBuildContractTests(unittest.TestCase):
    def test_linux_source_is_candidate_until_checksum_is_verified(self) -> None:
        manifest = json.loads((ROOT / "build/sources/sources.json").read_text())
        linux = next(item for item in manifest["sources"] if item["name"] == "linux")
        self.assertEqual(linux["version"], "6.18.65")
        self.assertEqual(linux["status"], "candidate")
        self.assertIsNone(linux["sha256"])
        self.assertIsNone(linux["sha512"])

    def test_kernel_builder_requires_pinned_source_and_builds_bzimage(self) -> None:
        script = (ROOT / "build/scripts/build-kernel.sh").read_text()
        self.assertIn("validate-sources.py --require-pinned --only linux", script)
        self.assertIn("x86_64_defconfig", script)
        self.assertIn("bzImage", script)
        self.assertIn("VIRTIO_BLK", script)
        self.assertIn("VIRTIO_NET", script)

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
