from __future__ import annotations
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools" / "prepare-rootfs.py"

class PrepareRootfsTests(unittest.TestCase):
    def build_rootfs(self, output: Path) -> None:
        result = subprocess.run([sys.executable, str(BUILDER), "--output", str(output)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_creates_identity_and_vantor_core(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "rootfs"
            self.build_rootfs(output)
            self.assertIn("ID=vantor", (output / "etc/os-release").read_text())
            self.assertIn("ONE SYSTEM. EVERY GENERATION.", (output / "etc/motd").read_text())
            self.assertTrue((output / "init").stat().st_mode & 0o111)
            self.assertTrue((output / "sbin/vantor-init").stat().st_mode & 0o111)
            self.assertTrue((output / "usr/bin/vantorctl").stat().st_mode & 0o111)
            self.assertTrue((output / "usr/bin/vantor-hw").stat().st_mode & 0o111)
            self.assertTrue((output / "usr/bin/nyan").stat().st_mode & 0o111)
            self.assertTrue((output / "usr/bin/vantor-install").stat().st_mode & 0o111)
            self.assertTrue((output / "usr/share/nyan/catalog.tsv").is_file())
            self.assertIn("fastfetch", (output / "usr/share/nyan/catalog.tsv").read_text())
            self.assertIn("root:x:0:0:", (output / "etc/passwd").read_text())
            self.assertIn("live:x:1000:1000:", (output / "etc/passwd").read_text())
            self.assertIn("wheel:x:10:live", (output / "etc/group").read_text())
            self.assertIn("%wheel ALL=(ALL:ALL) ALL", (output / "etc/sudoers.d/10-wheel").read_text())
            self.assertIn("root:!", (output / "etc/shadow").read_text())
            self.assertEqual((output / "etc/shadow").stat().st_mode & 0o777, 0o600)
            self.assertEqual((output / "etc/sudoers.d/10-wheel").stat().st_mode & 0o777, 0o440)
            self.assertIn("NYAN_REPO:=", (output / "etc/nyan.conf").read_text())
            inittab = (output / "etc/inittab").read_text()
            self.assertIn("/etc/init.d/rcS", inittab)
            self.assertIn("vantor-live-session", inittab)
            self.assertIn("ttyS0", inittab)
            self.assertIn("/bin/busybox getty", inittab)
            self.assertIn("udhcpc", (output / "etc/init.d/rcS").read_text())
            self.assertIn("/bin/busybox su -s /bin/sh - live", (output / "usr/bin/vantor-live-session").read_text())
            self.assertEqual((output / "etc/fstab").stat().st_mode & 0o777, 0o644)
            self.assertTrue((output / "usr/share/vantor/branding/vantor-mark.svg").is_file())
            brand = json.loads((output / "etc/vantor-brand.json").read_text())
            self.assertEqual(brand["brand"], "VANTOR Linux")
            self.assertEqual(brand["core"]["init"], "VANTOR Init 0.1.0")
            self.assertEqual(brand["core"]["hardware"], "VANTOR Hardware 0.1.0")
            for script in ("init", "sbin/vantor-init", "etc/init.d/rcS", "usr/bin/vantor-live-session", "usr/bin/vantorctl", "usr/bin/vantor-hw", "usr/bin/nyan", "usr/bin/vantor-install"):
                check = subprocess.run(["sh", "-n", str(output / script)], capture_output=True, text=True, check=False)
                self.assertEqual(check.returncode, 0, f"{script}: {check.stderr}")


    def test_installer_configures_root_live_and_wheel_without_touching_host(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "target"
            target.mkdir()
            self.build_rootfs(target)
            result = subprocess.run(
                ["sh", str(ROOT / "installer/vantor-install"), "--configure", str(target), "test-vantor", "tester"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            passwd = (target / "etc/passwd").read_text()
            self.assertIn("root:x:0:0:", passwd)
            self.assertIn("tester:x:1001:1001:", passwd)
            self.assertIn("tester:x:1001:", (target / "etc/group").read_text())
            self.assertIn("wheel:x:10:live,tester", (target / "etc/group").read_text())
            self.assertIn("%wheel ALL=(ALL:ALL) ALL", (target / "etc/sudoers.d/10-wheel").read_text())
            self.assertEqual((target / "etc/hostname").read_text(), "test-vantor\n")
            self.assertTrue((target / "home/tester").is_dir())
            self.assertIn("tester:!", (target / "etc/shadow").read_text())

    def test_hardware_inventory_reads_proc_and_sys_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            proc = base / "proc"
            sysroot = base / "sys"
            (proc).mkdir()
            (proc / "cpuinfo").write_text("processor : 0\nmodel name : VANTOR Test CPU\n")
            (proc / "meminfo").write_text("MemTotal:       2048000 kB\nMemAvailable:   1024000 kB\n")
            (sysroot / "block" / "vda").mkdir(parents=True)
            (sysroot / "block" / "vda" / "size").write_text("4096\n")
            (sysroot / "bus" / "pci" / "devices" / "0000:00:02.0").mkdir(parents=True)
            pci = sysroot / "bus" / "pci" / "devices" / "0000:00:02.0"
            (pci / "vendor").write_text("0x1af4\n")
            (pci / "device").write_text("0x1000\n")
            (pci / "class").write_text("0x020000\n")
            (sysroot / "bus" / "virtio" / "devices" / "virtio0").mkdir(parents=True)
            (sysroot / "bus" / "virtio" / "devices" / "virtio0" / "vendor").write_text("0x1af4\n")
            (sysroot / "bus" / "virtio" / "devices" / "virtio0" / "device").write_text("0x1000\n")
            (sysroot / "class" / "net" / "eth0").mkdir(parents=True)
            (sysroot / "class" / "net" / "eth0" / "operstate").write_text("up\n")
            (sysroot / "class" / "net" / "eth0" / "address").write_text("02:00:00:00:00:01\n")
            env = dict(__import__("os").environ, VANTOR_PROC_ROOT=str(proc), VANTOR_SYS_ROOT=str(sysroot))
            result = subprocess.run(["sh", str(ROOT / "core/hardware/vantor-hw")], env=env, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            for expected in ("VANTOR Test CPU", "MemTotal:", "vda: sectors=4096", "vendor=0x1af4", "virtio0", "eth0 state=up"):
                self.assertIn(expected, result.stdout, expected)

    def test_refuses_nonempty_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "rootfs"
            output.mkdir()
            (output / "keep").write_text("safe")
            result = subprocess.run([sys.executable, str(BUILDER), "--output", str(output)], capture_output=True, text=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((output / "keep").read_text(), "safe")

if __name__ == "__main__":
    unittest.main()
