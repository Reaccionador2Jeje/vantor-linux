# VANTOR Linux

**ONE SYSTEM. EVERY GENERATION.**

VANTOR is an independent Linux distribution project for universal computing. It is being built from source rather than derived from an existing Linux distribution.

> **Status:** early development — Genesis 0.1.0. This repository does not yet contain a bootable operating-system image.

## Official identity

![VANTOR Linux emblem](assets/branding/vantor-mark.svg)

The official identity uses a metallic V emblem and cyan orbital ring, with a deep-space navy interface palette. The source of truth is [assets/branding/theme.json](assets/branding/theme.json), with reusable CSS tokens in [assets/branding/theme.css](assets/branding/theme.css). Read the [visual identity guide](docs/branding.md).

The rootfs generator now installs these assets into \`/usr/share/vantor/branding\` and sets the distribution identity, console greeting, hostname and initial shell prompt. Bootloader, graphical login, installer and desktop integration will follow when those components exist.

## Project goals

- Build an independent x86_64 Linux system from source.
- Keep build inputs and versions explicit.
- Automate validation and builds with GitHub Actions.
- Produce a minimal bootable image before adding a desktop environment.
- Expand to AArch64 and other architectures only after the first target is reproducible.

## Initial technical direction

| Area | Initial choice |
|---|---|
| Target | x86_64 |
| Kernel | Upstream Linux |
| C library | glibc |
| Toolchain | GNU Binutils + GCC |
| Minimal userspace | BusyBox |
| Init | BusyBox init initially; service design remains open |
| Build environment | GitHub Actions |
| Android VM test app | Limbo PC Emulator (QEMU engine) |

These are project decisions, not claims that the components have already been integrated.

## Repository layout

- \`assets/branding/\` — official logo and shared visual design tokens
- \`boot/branding/\` — boot identity integration contract
- \`build/config/\` — versioned build configuration
- \`build/scripts/\` — build and validation scripts
- \`docs/\` — architecture, branding, and development notes
- \`kernel/\` — kernel configuration and integration
- \`packages/\` — package metadata and recipes
- \`rootfs/\` — root filesystem skeleton documentation
- \`tests/\` — automated tests
- \`tools/\` — developer utilities

## Getting started

The host-check script reports the tools available on your build machine:

\`\`\`bash
bash tools/check-host.sh
\`\`\`

Run repository checks and unit tests:

\`\`\`bash
make check
\`\`\`

Assemble the initial root filesystem skeleton:

\`\`\`bash
make rootfs
\`\`\`

The generated tree is placed in \`build/work/rootfs\`. It is not bootable yet because BusyBox, the kernel, and the final initramfs image have not been integrated.

## Toolchain and emulator development

The first x86_64 cross-toolchain plan is documented in [docs/toolchain.md](docs/toolchain.md). The initial Linux kernel baseline is 6.18.65, with its build contract and QEMU driver profile documented in [docs/kernel.md](docs/kernel.md). Android VM testing is documented in [docs/testing-limbo.md](docs/testing-limbo.md); Limbo PC Emulator is the selected manual test target. Initial build scripts exist for Binutils pass 1 and GCC pass 1, with a manual [GitHub Actions toolchain workflow](.github/workflows/toolchain.yml).

Upstream candidates are recorded in \`build/sources/sources.json\`; each source must have a verified digest before download/build automation can use it. \`make sources-ready\` deliberately fails until all selected sources are pinned. \`make fetch-sources\` verifies digests before saving archives.

## Community package contributions

Anyone can propose packages through a fork and Pull Request; repository write access is not required. Add a validated `.tar.gz` archive and matching JSON metadata under `incoming/<architecture>/`. GitHub Actions validates submissions, and accepted changes are published to the Nyan GitHub Releases mirror. See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete process and safety rules.

## Build status

CI validates repository structure, configuration, source metadata, safe extraction, rootfs generation and rootfs identity files. The first-stage toolchain scripts, GRUB boot menu, kernel build script and initial rootfs generator are implemented. Binutils and GCC bootstrap sources are pinned; glibc, Linux and BusyBox remain unpinned. No completed compiler, kernel, initramfs or bootable image is claimed yet. The kernel source remains unpinned until its official checksum is verified.

## Nyan package management

VANTOR's native package manager is **Nyan**. The initial POSIX shell prototype and repository index format are documented in [docs/nyan.md](docs/nyan.md). The official package mirror is being prepared on the project website; package downloads are not available until Cloudflare R2 storage is enabled and signed packages are published.

## Licensing

The repository's top-level license applies to original project files where applicable. Third-party components retain their own licenses and notices. Linux kernel licensing is governed by the kernel's own COPYING file and source headers.

## Contributing

See [docs/architecture.md](docs/architecture.md), [docs/toolchain.md](docs/toolchain.md), [docs/rootfs-genesis.md](docs/rootfs-genesis.md), [docs/testing-limbo.md](docs/testing-limbo.md), and [docs/branding.md](docs/branding.md).
