# VANTOR Linux

**ONE SYSTEM. EVERY GENERATION.**

VANTOR is an independent Linux distribution project for universal computing. It is being built from source rather than derived from an existing Linux distribution.

> **Status:** early development — Genesis 0.1.0. This repository does not yet contain a bootable operating-system image.

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
| First test target | QEMU |

These are project decisions, not claims that the components have already been integrated.

## Repository layout

- `build/config/` — versioned build configuration
- `build/scripts/` — build and validation scripts
- `docs/` — architecture and development notes
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

## Build status

The current CI validates repository structure and shell scripts. It does **not** yet compile a complete toolchain, kernel, or ISO. Those stages will be added and tested incrementally.

## Licensing

The repository's top-level license applies to original project files where applicable. Third-party components retain their own licenses and notices. Linux kernel licensing is governed by the kernel's own COPYING file and source headers.

## Contributing

See [docs/architecture.md](docs/architecture.md) for the initial design and current milestones.
