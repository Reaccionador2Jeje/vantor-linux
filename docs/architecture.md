# VANTOR Genesis architecture

## Purpose

VANTOR is an independent distribution assembled from upstream source projects. It is not a respin of Debian, Ubuntu, Arch, Fedora, or another distribution.

## First milestone

The first milestone is a minimal x86_64 system that can boot in QEMU. A graphical desktop is deliberately out of scope until the base system is reproducible.

## Boot sequence

1. Platform firmware: legacy BIOS or UEFI.
2. GNU GRUB 2: displays the VANTOR boot menu and loads the kernel/initramfs.
3. Linux kernel: initializes x86_64 hardware and unpacks the initramfs.
4. Initramfs: provides the minimal early userspace and mounts required virtual filesystems.
5. VANTOR \`/init\`: starts the initial userspace process and eventually the system shell.

GRUB is the initial bootloader; it is not a replacement for the Linux kernel. See [bootloader design](bootloader.md).

## Initial component plan

1. Cross-toolchain: GNU Binutils and GCC targeting x86_64 VANTOR.
2. C library: glibc built for the target.
3. Bootloader: GNU GRUB 2 with BIOS and UEFI platform modules.
4. Kernel: upstream Linux configured for the first virtual-machine target.
5. Userland: BusyBox and a minimal root filesystem.
6. Initramfs and ISO: assemble the early userspace and package it with GRUB.
7. QEMU smoke test: verify the complete firmware-to-shell boot path.

The exact upstream versions, source URLs, signatures, and SHA-256 checksums must be recorded in a source manifest before automated downloads are enabled.

## Build principles

- Build in an isolated directory; never overwrite host system files.
- Pin every source release and verify its checksum.
- Keep host tools separate from target tools.
- Fail immediately when a required command or artifact is missing.
- Preserve build logs as CI artifacts.
- Do not publish an ISO until a boot test succeeds.

## Architecture policy

x86_64 is the first supported build target. AArch64 is a planned second target. Additional architectures require their own toolchain configuration, kernel configuration, bootloader target and automated boot tests.

## Current status

The repository has an initial GRUB 2 menu and a guarded ISO assembly script. The ISO builder requires a built kernel and initramfs, which are not yet available. The rootfs generator is a skeleton; BusyBox, kernel, initramfs and full boot integration remain future work. No bootable ISO is claimed.
