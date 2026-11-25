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

    def test_initramfs_includes_matching_kernel_modules_when_available(self):
        script = (ROOT / "build/scripts/build-initramfs.sh").read_text()
        self.assertIn('KERNEL_RELEASE_FILE="${VANTOR_KERNEL_RELEASE_FILE:-$ROOT/build/work/kernel/kernelrelease}"', script)
        self.assertIn('MODULES_ROOT="${VANTOR_MODULES_ROOT:-$ROOT/build/work/modules}/lib/modules"', script)
        self.assertIn('cp -a "$MODULES_SOURCE" "$MODULES_DEST"', script)
        self.assertIn('depmod -b "$ROOTFS" "$KERNEL_RELEASE"', script)

    def test_legacy_initramfs_skips_foreign_x86_64_modules(self):
        script = (ROOT / "build/scripts/build-initramfs.sh").read_text()
        makefile = (ROOT / "Makefile").read_text()
        self.assertIn('VANTOR_SKIP_KERNEL_MODULES:-0', script)
        self.assertIn('VANTOR_SKIP_KERNEL_MODULES=1', makefile)

    def test_busybox_builder_fails_closed_on_unpinned_source(self):
        script = (ROOT / "build/scripts/build-busybox.sh").read_text()
        self.assertIn("--require-pinned --only busybox", script)
        self.assertIn("CONFIG_STATIC=y", script)
        self.assertIn("CONFIG_TC is not set", script)
        self.assertIn("CONFIG_PREFIX=", script)

    def test_busybox_switch_root_is_enabled_for_both_architectures(self):
        for name in ("build-busybox.sh", "build-busybox-legacy.sh"):
            script = (ROOT / "build/scripts" / name).read_text()
            self.assertIn("CONFIG_SWITCH_ROOT y", script)
        if name == "build-busybox.sh":
            self.assertIn("CONFIG_MODPROBE", script)
            self.assertIn("modprobe", script)
            self.assertIn("switch_root", script)

    def test_busybox_pid1_init_and_inittab_are_required(self):
        script = (ROOT / "build/scripts/build-busybox.sh").read_text()
        self.assertIn("set_config CONFIG_INIT y", script)
        self.assertIn("set_config CONFIG_FEATURE_USE_INITTAB y", script)
        self.assertIn("for applet in init vi", script)

    def test_legacy_busybox_has_init_and_service_control(self):
        script = (ROOT / "build/scripts/build-busybox-legacy.sh").read_text()
        self.assertIn("set_config CONFIG_INIT y", script)
        self.assertIn("set_config CONFIG_FEATURE_USE_INITTAB y", script)
        self.assertIn("set_config CONFIG_START_STOP_DAEMON y", script)
        self.assertIn("for applet in init start-stop-daemon", script)

    def test_busybox_service_manager_applet_is_enabled(self):
        script = (ROOT / "build/scripts/build-busybox.sh").read_text()
        self.assertIn("CONFIG_START_STOP_DAEMON", script)
        self.assertIn("start-stop-daemon", script)

    def test_iso_and_initramfs_output_contract_match(self):
        initramfs = (ROOT / "build/scripts/build-initramfs.sh").read_text()
        iso = (ROOT / "build/scripts/build-iso.sh").read_text()
        self.assertIn("VANTOR_INITRAMFS_DIR:-$ROOT/build/work/initramfs", initramfs)
        self.assertIn("VANTOR_INITRAMFS_NAME:-vantor-initramfs.cpio.gz", initramfs)
        self.assertIn('INITRAMFS="$WORK/initramfs/vantor-initramfs.cpio.gz"', iso)

    def test_legacy_image_uses_486_kernel_and_separate_initramfs(self):
        script = (ROOT / "build/scripts/build-iso-legacy.sh").read_text()
        grub = (ROOT / "boot/grub/grub-legacy.cfg").read_text()
        self.assertIn("kernel-legacy/arch/x86/boot/bzImage", script)
        self.assertIn("initramfs-legacy/vantor-legacy-initramfs.cpio.gz", script)
        self.assertIn("terminal_output console", grub)
        self.assertIn("vantor-legacy-kernel", grub)

    def test_framebuffer_splash_draws_scene_once_and_animates_progress_only(self):
        source = (ROOT / "core/boot/vantor-fb-splash.c").read_text()
        start = source.index('if(!strcmp(cmd,"start"))')
        step = source.index('} else if(!strcmp(cmd,"step"))', start)
        animation = source[start:step]
        frames = animation[animation.index("for(int i=0;i<18;i++)"):]
        self.assertIn('render_static("INITIALIZING VANTOR")', animation)
        self.assertIn("draw_progress(progress)", frames)
        self.assertNotIn("render_static(", frames)
        self.assertNotIn("background()", frames)
        self.assertIn("draw_orbit(cx,cy,rx,ry)", source)


if __name__ == "__main__":
    unittest.main()
