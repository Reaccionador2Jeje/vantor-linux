# VANTOR Linux kernel

## Version and source

The initial kernel baseline is Linux **6.18.65**, from the upstream long-term-support 6.18.y series. Kernel.org lists this release as published on 23 November 2026. See the official [kernel archive](https://cdn.kernel.org/pub/linux/kernel/v6.x/) and [6.18.65 release announcement](https://lkml.iu.edu/hypermail/linux/kernel/2611.2/22488.html).

The source manifest pins this release using the SHA-256 published by kernel.org. The download helper verifies the archive before extraction; do not bypass this check.

## Build model

The first kernel is a native x86_64 build on the x86_64 GitHub Actions runner. The Linux kernel does not need the VANTOR userspace C library to produce the initial bzImage; it is built with the runner's host compiler and binutils. The independent VANTOR cross-toolchain remains a separate userspace bootstrap task.

Run:

    make kernel

The script:

1. Requires the Linux source to be pinned in build/sources/sources.json.
2. Downloads the archive through the repository's checksum-verifying fetcher.
3. Safely extracts the source tree.
4. Starts from upstream x86_64_defconfig.
5. Enables early userspace, console, VirtIO, storage, network and common virtual-PC drivers.
6. Runs olddefconfig and builds bzImage.
7. Builds the kernel image and loadable modules.\n8. Installs modules into an isolated staging tree and generates dependency metadata when `depmod` is available.\n9. Stores the resolved config, kernel release and build log.

Expected outputs:\n\n- `build/work/kernel/vantor-kernel`\n- `build/work/kernel/kernelrelease`\n- `build/work/modules/lib/modules/<kernel-release>/`

The dedicated GitHub Actions workflow compiles this target and uploads the kernel image, module tree and resolved configuration as a temporary workflow artifact. This artifact is not yet a signed installation release.

The canonical kernel build output remains at build/work/kernel/arch/x86/boot/bzImage for ISO assembly.

## Initial driver profile

The first profile prioritizes Limbo/QEMU's virtual PC: PCI, VirtIO block/network/console, common IDE/SCSI storage, E1000 networking, VGA/VT console, 8250 serial and USB host controllers. Drivers are built into the kernel where enabled by the baseline configuration so that early boot does not depend on unavailable modules.

## Current limitations

- The first automated x86_64 build is in progress; a green CI check is not itself proof of a successful kernel compilation.
- The generated kernel has not yet been boot-tested in Limbo.
- The initramfs is still a skeleton; BusyBox and the final /init environment must be assembled before the kernel can reach a usable VANTOR shell.
- A successful kernel build alone does not prove GRUB, BIOS, UEFI or Limbo compatibility.


## Legacy 32-bit kernel

VANTOR Minimal has a separate i486 Legacy kernel profile. It uses Linux **6.1.193**, whose archive is pinned using the SHA-256 published in kernel.org's signed checksum list. This older LTS line retains the 486SX configuration choice and supports math emulation for 486SX systems without an FPU.

Run:

    make kernel-legacy

The builder uses i386_defconfig, selects the 486SX CPU profile, enables math emulation and adds conservative ISA, floppy, IDE, VGA, serial and legacy network drivers. It writes:
- build/work/kernel-legacy/vantor-legacy-kernel
- kernel/configs/vantor-i486.config

This is a separate kernel artifact, not yet a complete 32-bit install image. The legacy BusyBox, package ABI, boot ISO and physical hardware validation remain follow-up work. The modern 6.18.65 kernel is not used for 486 systems.
