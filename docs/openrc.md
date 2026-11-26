# OpenRC integration

**OpenRC 0.64.1 is the real PID 1 and service manager in VANTOR's x86_64 and i486 ISO build pipelines.**

## Source and build

The upstream source archive is pinned in `build/sources/sources.json` with the SHA-512 digest published in Gentoo's distfile Manifest. The build uses Meson and Ninja, disables optional PAM, audit, SELinux and OpenRC's separate networking implementation, and links the OpenRC executables statically against the build runner's C runtime and libcap. Static executables avoid adding a second dynamic loader/runtime dependency to the minimal rootfs.

Run the ordered image pipeline:

- `make rootfs`
- `make busybox`
- `make openrc`
- `make initramfs`
- `make iso`

For the Legacy target, use `make image-legacy`; it cross-builds 32-bit OpenRC with i486 compiler flags and the i386 libcap development package. The CI image inspection checks ELF machine type and rejects dynamically linked OpenRC PID 1 binaries. Actual CPU compatibility still requires a boot test on a 486-class QEMU CPU or physical hardware.

## Boot ownership

The initramfs `/init` mounts the early virtual filesystems and calls `/sbin/vantor-init`. That small VANTOR handoff helper prepares procfs, sysfs, devtmpfs and /run, then executes `/sbin/init`. The OpenRC build replaces that symlink with `/sbin/openrc-init`; the initramfs builder refuses to package an image unless this exact target is present.

BusyBox remains the static early-userspace and recovery toolbox. Its `init` applet is no longer the normal PID 1. The old VANTOR shell service supervisor is not installed into the rootfs.

## VANTOR service integration

- `vantor-early` starts the VANTOR boot presentation.
- `vantor-modules` loads the optional modules listed in `/etc/modules`.
- `vantor-network` configures interfaces using the existing BusyBox `ip` and `udhcpc` tools.
- `vantor-console.tty1` and `vantor-console.ttyS0` are OpenRC-supervised login consoles.
- OpenRC's own runlevels provide dependency ordering and orderly service shutdown.

`vantorctl service` delegates to `rc-service`, `rc-update` and `rc-status`. It does not keep a parallel service database.

## Validation

`make check` validates the integration scripts and rootfs contract. The Genesis and Legacy image workflows compile OpenRC, verify required commands, confirm static ELF binaries, and inspect the resulting initramfs and ISO. These checks establish that OpenRC is included; they do not replace boot testing in Limbo/QEMU.
