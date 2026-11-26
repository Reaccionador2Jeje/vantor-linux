from __future__ import annotations
import json
import os
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
            for directory in ("mnt", "media", "opt", "srv", "proc", "sys", "dev", "run", "run/lock", "tmp", "var/cache", "var/lib", "var/log", "var/spool", "var/tmp"):
                self.assertTrue((output / directory).is_dir(), f"missing standard directory: /{directory}")
            self.assertEqual((output / "mnt").stat().st_mode & 0o777, 0o755)
            self.assertEqual((output / "tmp").stat().st_mode & 0o7777, 0o1777)
            self.assertEqual((output / "var/tmp").stat().st_mode & 0o7777, 0o1777)
            self.assertIn("ONE SYSTEM. EVERY GENERATION.", (output / "etc/motd").read_text())
            self.assertTrue((output / "init").stat().st_mode & 0o111)
            initramfs_init = (output / "init").read_text()
            self.assertIn("root=/dev/*", initramfs_init)
            self.assertIn("rootfstype=", initramfs_init)
            self.assertIn("busybox switch_root /newroot /sbin/vantor-init", initramfs_init)
            self.assertTrue((output / "sbin/vantor-init").stat().st_mode & 0o111)
            self.assertIn('VERSION="0.2.0"', (output / "sbin/vantor-init").read_text())
            self.assertTrue((output / "sbin/init").is_symlink())
            self.assertEqual((output / "sbin/init").readlink().as_posix(), "/sbin/openrc-init")
            self.assertFalse((output / "etc/inittab").exists())
            self.assertIn("vantor-modules", initramfs_init)
            self.assertIn("rootwait is bounded", initramfs_init)
            self.assertIn("switch_root /newroot /sbin/vantor-init", initramfs_init)
            self.assertTrue((output / "usr/sbin/vantor-storage").stat().st_mode & 0o111)
            storage = (output / "usr/sbin/vantor-storage").read_text()
            self.assertIn("mount -a", storage)
            self.assertIn("no formatting or partition changes", storage)
            self.assertIn('case "$device" in /dev/*)', storage)
            self.assertIn('case "$fstype" in ext2|ext3|ext4|vfat|exfat|ntfs|iso9660)', storage)
            self.assertIn("umount|unmount)", storage)
            self.assertIn("fstab-check)", storage)
            self.assertIn('exec mount -t "$fstype" -o nosuid,nodev', storage)
            self.assertIn('exec umount "$target"', storage)
            self.assertIn("mount-removable)", storage)
            self.assertIn("umount-removable)", storage)
            self.assertIn('[ "$removable" = 1 ]', storage)
            self.assertIn('ro,nosuid,nodev,noexec', storage)
            self.assertIn('target="/media/$name"', storage)
            self.assertTrue((output / "usr/bin/vantorctl").stat().st_mode & 0o111)
            self.assertTrue((output / "usr/bin/vantor-hw").stat().st_mode & 0o111)
            self.assertTrue((output / "usr/bin/nyan").stat().st_mode & 0o111)
            self.assertTrue((output / "usr/bin/vantor-install").stat().st_mode & 0o111)
            self.assertTrue((output / "usr/bin/vantor-splash").stat().st_mode & 0o111)
            if (output / "usr/bin/vantor-fb-splash").exists():
                self.assertTrue((output / "usr/bin/vantor-fb-splash").stat().st_mode & 0o111)
            splash = (output / "usr/bin/vantor-splash").read_text()
            self.assertIn("vantor-fb-splash", splash)
            self.assertIn('[ -c /dev/fb0 ]', splash)
            self.assertIn("VANTOR LINUX", splash)
            self.assertIn("ONE SYSTEM. EVERY GENERATION.", splash)
            self.assertIn('case "${1:-start}" in', splash)
            self.assertIn("nosplash", splash)
            self.assertTrue((output / "usr/share/nyan/catalog.tsv").is_file())
            self.assertIn("fastfetch", (output / "usr/share/nyan/catalog.tsv").read_text())
            self.assertIn("root:x:0:0:", (output / "etc/passwd").read_text())
            self.assertIn("busybox --install -s /bin", (output / "sbin/vantor-init").read_text())
            self.assertIn("live:x:1000:1000:", (output / "etc/passwd").read_text())
            self.assertIn("wheel:x:10:live", (output / "etc/group").read_text())
            self.assertIn("live ALL=(ALL:ALL) ALL", (output / "etc/sudoers.d/99-live").read_text())
            self.assertIn("live:$6$VANTORlive$", (output / "etc/shadow").read_text())
            self.assertIn("%wheel ALL=(ALL:ALL) ALL", (output / "etc/sudoers.d/10-wheel").read_text())
            self.assertEqual((output / "etc/sudoers").stat().st_mode & 0o777, 0o440)
            self.assertEqual((output / "etc/sudoers.d/99-live").stat().st_mode & 0o777, 0o440)
            self.assertTrue((output / "run/sudo").is_dir())
            self.assertEqual((output / "run/sudo").stat().st_mode & 0o777, 0o700)
            self.assertIn("root:!", (output / "etc/shadow").read_text())
            self.assertEqual((output / "etc/shadow").stat().st_mode & 0o777, 0o600)
            self.assertEqual((output / "etc/sudoers.d/10-wheel").stat().st_mode & 0o777, 0o440)
            self.assertIn("NYAN_REPO:=", (output / "etc/nyan.conf").read_text())
            rc_s = (output / "etc/init.d/rcS").read_text()
            self.assertIn("OpenRC runlevels manage services", rc_s)
            self.assertNotIn("/usr/sbin/vantor-network", rc_s)
            self.assertIn("logs|status", (output / "usr/bin/vantorctl").read_text())
            self.assertIn('exec /usr/sbin/vantor-service logs "$@"', (output / "usr/bin/vantorctl").read_text())
            self.assertIn("exec /sbin/init nonetwork", (output / "sbin/vantor-init").read_text())
            ctl = (output / "usr/bin/vantorctl").read_text()
            self.assertIn("recovery)", ctl)
            self.assertIn("VANTOR recovery mode: ACTIVE", ctl)
            self.assertIn("Add 'vantor.recovery'", ctl)
            self.assertTrue((output / "usr/sbin/vantor-service").stat().st_mode & 0o111)
            self.assertTrue((output / "etc/vantor/services").is_dir())
            service_manager = (output / "usr/sbin/vantor-service").read_text()
            self.assertIn("rc-service", service_manager)
            self.assertIn("rc-update", service_manager)
            self.assertIn("rc-status", service_manager)
            self.assertNotIn("vantor-service-supervisor", service_manager)
            self.assertTrue((output / "usr/sbin/vantor-network").stat().st_mode & 0o111)
            network = (output / "usr/sbin/vantor-network").read_text()
            self.assertIn("while IFS='=' read -r key value", network)
            self.assertNotIn('. "$network_cfg"', rc_s)
            self.assertIn("udhcpc -i", network)
            self.assertIn("ip route replace default", network)
            self.assertIn("nameserver", (output / "usr/share/udhcpc/default.script").read_text())
            self.assertTrue((output / "usr/sbin/vantor-modules").stat().st_mode & 0o111)
            self.assertIn("virtio_net", (output / "etc/modules").read_text())
            self.assertIn('storage) shift; if [ "$#" -gt 0 ]; then exec /usr/sbin/vantor-storage "$@"; else exec /usr/sbin/vantor-storage status; fi ;;', (output / "usr/bin/vantorctl").read_text())
            live_session = (output / "usr/bin/vantor-live-session").read_text()
            self.assertIn("exec /bin/sh -l", live_session)
            self.assertNotIn("busybox su", live_session)
            self.assertIn("administrative", live_session)
            self.assertEqual((output / "etc/fstab").stat().st_mode & 0o777, 0o644)
            self.assertTrue((output / "usr/share/vantor/branding/vantor-mark.svg").is_file())
            brand = json.loads((output / "etc/vantor-brand.json").read_text())
            self.assertEqual(brand["brand"], "VANTOR Linux")
            self.assertEqual(brand["core"]["init"], "OpenRC 0.64.1")
            self.assertEqual(brand["core"]["bootstrap"], "VANTOR Init 0.2.0")
            self.assertEqual(brand["core"]["hardware"], "VANTOR Hardware 0.1.0")
            for script in ("init", "sbin/vantor-init", "usr/sbin/vantor-modules", "usr/sbin/vantor-network", "usr/sbin/vantor-service", "usr/sbin/vantor-storage", "etc/init.d/rcS", "usr/bin/vantor-splash", "usr/bin/vantor-live-session", "usr/bin/vantorctl", "usr/bin/vantor-hw", "usr/bin/nyan", "usr/bin/vantor-install"):
                check = subprocess.run(["sh", "-n", str(output / script)], capture_output=True, text=True, check=False)
                self.assertEqual(check.returncode, 0, f"{script}: {check.stderr}")


    def test_i486_rootfs_selects_legacy_nyan_architecture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "rootfs-i486"
            result = subprocess.run(
                [sys.executable, str(BUILDER), "--output", str(output), "--arch", "i486"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('NYAN_ARCH:=i486', (output / "etc/nyan.conf").read_text())
            self.assertFalse((output / "usr/bin/vantor-fb-splash").exists())
            brand = json.loads((output / "etc/vantor-brand.json").read_text())
            self.assertEqual(brand["architecture"], "i486")

    def test_termux_launcher_has_valid_shell_syntax(self) -> None:
        launcher = ROOT / "tools" / "termux" / "vantor"
        result = subprocess.run(["sh", "-n", str(launcher)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        content = launcher.read_text()
        self.assertIn("proot --link2symlink -0 -r", content)
        self.assertIn("/usr/bin/vantor-termux-shell", content)

    def test_aarch64_rootfs_metadata_is_termux_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "rootfs-aarch64"
            result = subprocess.run(
                [sys.executable, str(BUILDER), "--output", str(output), "--arch", "aarch64"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('NYAN_ARCH:=aarch64', (output / "etc/nyan.conf").read_text())
            self.assertFalse((output / "usr/bin/vantor-fb-splash").exists())
            brand = json.loads((output / "etc/vantor-brand.json").read_text())
            self.assertEqual(brand["architecture"], "aarch64")

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
            self.assertIn("live:x:1000:1000:", passwd)
            self.assertIn("wheel:x:10:live,tester", (target / "etc/group").read_text())
            shadow = (target / "etc/shadow").read_text()
            self.assertRegex(shadow, r"(?m)^live:\$6\$VANTORlive\$")
            self.assertIn("tester:!", shadow)
            self.assertTrue((target / "home/live").is_dir())
            self.assertIn("wheel:!::live,tester", (target / "etc/gshadow").read_text())
            self.assertIn("%wheel ALL=(ALL:ALL) ALL", (target / "etc/sudoers.d/10-wheel").read_text())
            self.assertIn("live ALL=(ALL:ALL) ALL", (target / "etc/sudoers.d/99-live").read_text())
            self.assertEqual((target / "etc/hostname").read_text(), "test-vantor\n")
            self.assertTrue((target / "home/tester").is_dir())
            self.assertIn("tester:!", (target / "etc/shadow").read_text())

    def test_installer_preserves_reused_live_account_password(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "target"
            target.mkdir()
            self.build_rootfs(target)
            result = subprocess.run(
                ["sh", str(ROOT / "installer/vantor-install"), "--configure", str(target), "vantor", "live"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            shadow = (target / "etc/shadow").read_text()
            self.assertRegex(shadow, r"(?m)^live:\$6\$VANTORlive\$")
            self.assertTrue((target / "home/live").is_dir())
            self.assertIn("wheel:x:10:live", (target / "etc/group").read_text())
            self.assertIn("wheel:!::live", (target / "etc/gshadow").read_text())
            self.assertIn("live ALL=(ALL:ALL) ALL", (target / "etc/sudoers.d/99-live").read_text())

    def test_installer_prepares_kernel_initramfs_grub_and_fstab(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            target = base / "target"
            target.mkdir()
            (target / "etc").mkdir()
            kernel = base / "kernel"
            initramfs = base / "initramfs.cpio.gz"
            kernel.write_bytes(b"test-kernel")
            initramfs.write_bytes(b"test-initramfs")
            fakebin = base / "bin"
            fakebin.mkdir()
            mountpoint = fakebin / "mountpoint"
            mountpoint.write_text("#!/bin/sh\nexit 0\n")
            mountpoint.chmod(0o755)
            mounts = base / "mounts"
            mounts.write_text(f"/dev/vda1 {target} ext4 rw,relatime 0 0\n")
            env = dict(os.environ, PATH=str(fakebin) + os.pathsep + os.environ.get("PATH", ""),
                       VANTOR_PROC_MOUNTS=str(mounts))
            result = subprocess.run(
                ["sh", str(ROOT / "installer/vantor-install"), "--prepare-boot",
                 str(target), str(kernel), str(initramfs), "i486"],
                capture_output=True, text=True, check=False, env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((target / "boot/vantor-kernel").read_bytes(), b"test-kernel")
            self.assertEqual((target / "boot/vantor-initramfs.cpio.gz").read_bytes(), b"test-initramfs")
            grub = (target / "boot/grub/grub.cfg").read_text()
            self.assertIn("root=/dev/vda1 rootfstype=ext4", grub)
            self.assertIn("VANTOR Linux Minimal — i486", grub)
            fstab = (target / "etc/fstab").read_text()
            self.assertIn("/dev/vda1 / ext4 defaults 0 1", fstab)
            self.assertIn("proc /proc proc", fstab)

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
            usb = sysroot / "bus" / "usb" / "devices" / "1-1"
            usb.mkdir(parents=True)
            (usb / "idVendor").write_text("1234\n")
            (usb / "idProduct").write_text("abcd\n")
            (usb / "manufacturer").write_text("VANTOR Test\n")
            (usb / "product").write_text("USB Device\n")
            (sysroot / "class" / "net" / "eth0").mkdir(parents=True)
            (sysroot / "class" / "net" / "eth0" / "operstate").write_text("up\n")
            (sysroot / "class" / "net" / "eth0" / "address").write_text("02:00:00:00:00:01\n")
            env = dict(__import__("os").environ, VANTOR_PROC_ROOT=str(proc), VANTOR_SYS_ROOT=str(sysroot))
            result = subprocess.run(["sh", str(ROOT / "core/hardware/vantor-hw")], env=env, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            for expected in ("VANTOR Test CPU", "MemTotal:", "vda: sectors=4096", "vendor=0x1af4", "virtio0", "1234", "abcd", "VANTOR Test", "eth0 state=up"):
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
