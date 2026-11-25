# VANTOR Genesis — BusyBox and initramfs

The first bootable userspace is intentionally small. It consists of the generated
VANTOR rootfs skeleton and a statically linked BusyBox binary. Static linking lets
the early userspace run before the VANTOR cross-toolchain and C library are complete.

## Build sequence

On an Ubuntu 24.04 build host (or a matching GitHub Actions runner), install the
host build dependencies: `build-essential`, `bc`, `bison`, `flex`, `libssl-dev`,
`libelf-dev`, `cpio`, `gzip`, `python3`, and `make`.

Run:

1. `make rootfs`
2. `make busybox`
3. `make initramfs`
4. `make kernel`
5. `make iso`

The BusyBox build is fail-closed: it requires the BusyBox source entry to have a
verified upstream checksum in `build/sources/sources.json`. Do not invent or
copy an unverified checksum. Until it is pinned, `make busybox` must stop before
downloading or compiling.

## Early userspace contract

- Kernel loads the gzip-compressed `newc` cpio archive.
- Kernel executes `/init` as PID 1.
- `/init` mounts proc, sysfs and devtmpfs, prints the VANTOR identity and starts
  the available shell if a full init system is not present.
- BusyBox provides the minimal shell and applets needed for the first interactive
  boot. The VANTOR init script remains deliberately small.

## Output

`build/work/initramfs/vantor-initramfs.cpio.gz`

The ISO builder consumes this exact path. Creating the archive is not proof that
the kernel boots; the resulting ISO still needs to be tested in Limbo on Android.
