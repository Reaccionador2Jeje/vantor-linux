# VANTOR Genesis architecture

## Purpose

VANTOR is an independent distribution assembled from upstream source projects. It is not a respin of Debian, Ubuntu, Arch, Fedora, or another distribution.

## First milestone

The first milestone is a minimal x86_64 system that can boot in QEMU. A graphical desktop is deliberately out of scope until the base system is reproducible.

## Initial component plan

1. Cross-toolchain: GNU Binutils and GCC targeting x86_64 VANTOR.
2. C library: glibc built for the target.
3. Kernel: upstream Linux configured for the first virtual-machine target.
4. Userland: BusyBox and a minimal root filesystem.
5. Boot: a documented boot path and QEMU smoke test.

The exact upstream versions, source URLs, signatures, and SHA-256 checksums must be recorded in a source manifest before automated downloads are enabled.

## Build principles

- Build in an isolated directory; never overwrite host system files.
- Pin every source release and verify its checksum.
- Keep host tools separate from target tools.
- Fail immediately when a required command or artifact is missing.
- Preserve build logs as CI artifacts.
- Do not publish an ISO until a boot test succeeds.

## Architecture policy

x86_64 is the first supported build target. AArch64 is a planned second target. Additional architectures require their own toolchain configuration, kernel configuration, and automated boot tests.

## Current status

The repository currently contains project metadata, configuration, and validation scaffolding. It does not yet contain a toolchain builder, kernel build, root filesystem image, or bootable ISO.
