# VANTOR Linux

**ONE SYSTEM. EVERY GENERATION.**

VANTOR is an independent Linux distribution project for universal computing. It is being built from source rather than derived from an existing Linux distribution.

> **Status:** early development — Genesis 0.1.0. This repository does not yet contain a bootable operating-system image.

## Official identity

![VANTOR Linux emblem](assets/branding/vantor-mark.svg)

The official identity uses a metallic V emblem and cyan orbital ring, with a deep-space navy interface palette. The source of truth is [assets/branding/theme.json](assets/branding/theme.json), with reusable CSS tokens in [assets/branding/theme.css](assets/branding/theme.css). Read the [visual identity guide](docs/branding.md).

The identity is intended to be consistent across the bootloader, boot splash, installer, login screen, desktop, terminal, icons, notifications, and system settings. These shared assets are ready; runtime integration will happen as those system components are implemented.

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

- `assets/branding/` — official logo and shared visual design tokens
- `boot/branding/` — boot identity integration contract
- `build/config/` — versioned build configuration
- `build/scripts/` — build and validation scripts
- `docs/` — architecture, branding, and development notes
- `kernel/` — kernel configuration and integration
- `packages/` — package metadata and recipes
- `rootfs/` — root filesystem skeleton
- `tests/` — automated tests
- `tools/` — developer utilities

## Getting started

The host-check script reports the tools available on your build machine:

```bash
bash tools/check-host.sh
```

Run repository checks locally:

```bash
make check
```

## Toolchain development

The first x86_64 cross-toolchain plan is documented in [docs/toolchain.md](docs/toolchain.md), and Android VM testing is documented in [docs/testing-limbo.md](docs/testing-limbo.md). Limbo PC Emulator is the selected manual test target. Initial build scripts now exist for Binutils pass 1 and GCC pass 1, with a manual [GitHub Actions toolchain workflow](.github/workflows/toolchain.yml). Upstream candidates are recorded in `build/sources/sources.json`; they are not build-approved until their SHA-256 digests are verified. `make check` runs repository checks and source-extraction tests. `make sources-ready` deliberately fails until every source is pinned. `make fetch-sources` downloads only pinned archives and verifies each digest before saving it.

## Build status

The current CI validates repository structure, configuration, source metadata, and safe extraction tests. The first-stage build scripts are implemented. Binutils and GCC bootstrap archives have upstream-published integrity pins; glibc, Linux, and BusyBox remain unpinned and are excluded from the bootstrap build. No compiler, kernel, or bootable image is claimed as built yet.

## Licensing

The repository's top-level license applies to original project files where applicable. Third-party components retain their own licenses and notices. Linux kernel licensing is governed by the kernel's own COPYING file and source headers.

## Contributing

See [docs/architecture.md](docs/architecture.md), [docs/toolchain.md](docs/toolchain.md), and [docs/branding.md](docs/branding.md) for the project's design.
