# VANTOR toolchain plan

## Goal

Produce a reproducible x86_64 cross-toolchain for the independent VANTOR target
`x86_64-vantor-linux-gnu`. The build must not depend on an installed Linux
distribution's target libraries or headers.

## Bootstrap sequence

1. **Host inspection** — record the GitHub Actions runner tool versions and required host packages.
2. **Binutils pass 1** — build assembler, linker and binary utilities for the VANTOR target.
3. **GCC pass 1** — build a minimal C compiler with no target libc.
4. **Linux API headers** — install sanitized kernel userspace headers into the target sysroot.
5. **glibc** — build the target C library using the cross-toolchain.
6. **libgcc / final GCC** — finish compiler runtime support and rebuild the compiler against the target libc.
7. **BusyBox** — build the first minimal target userspace.
8. **Kernel and initramfs** — build a kernel and a tiny initramfs, then boot it under QEMU.

The first two stages now have build scripts: `build-binutils.sh` and `build-gcc.sh`.
`build-toolchain.sh` orchestrates them after source verification. They install only
under `build/tools` and `build/sysroot`, never into the runner's system directories.
The manual `VANTOR Toolchain` GitHub Actions workflow installs host build dependencies,
runs `make toolchain`, and uploads build logs and toolchain artifacts.

## Candidate upstream versions (2026-11-24)

| Component | Candidate | Reason |
|---|---:|---|
| GNU Binutils | 2.47 | Upstream release archive exists |
| GCC | 16.2.0 | Listed in GNU's release timeline |
| glibc | 2.44 | Upstream's current stable release |
| Linux | 6.18.65 | Current 6.18 long-term-support point release |
| BusyBox | 1.37.0 | Stable baseline; upstream marks 1.38.0 unstable |

Binutils 2.47 is pinned with the SHA-256 published in the upstream release announcement. GCC 16.2.0 is pinned with the SHA-512 published in the official GNU release directory. The validator and downloader accept either SHA-256 or SHA-512. glibc, Linux, and BusyBox remain candidates until their own source integrity metadata is verified.

## Source integrity

- `tools/validate-sources.py` validates the JSON manifest.
- `tools/extract-source.py` extracts verified archives with Python's safe `data` filter.
- `tests/test_source_tools.py` checks normal extraction, path traversal rejection, and existing-directory handling.
- `make sources-ready` fails until every manifest source has a verified SHA-256 or SHA-512 digest and status `pinned`.
- The bootstrap driver currently validates and downloads only the pinned Binutils and GCC inputs using `--only binutils gcc`; later stages will be enabled as their own sources are pinned.
- `tools/fetch-sources.py` refuses unpinned entries, downloads over HTTPS,
  verifies SHA-256, and only then moves an archive into `build/distfiles`.
- Downloads are never extracted automatically.
- `make clean` removes generated work and downloaded archives but preserves
  the source manifest and its policy documentation.

## Build acceptance criteria

A toolchain stage is not considered complete merely because a command exits
successfully. Each stage must publish:

- exact source version and SHA-256;
- build configuration and target triplet;
- logs and resulting binary versions;
- a smoke test proving the compiler emits VANTOR-targeted ELF objects;
- a clean-run reproducibility check where practical.

The initial toolchain workflow can build the bootstrap subset (Binutils and GCC) while later component sources remain unpinned. No bootable ISO is claimed until the kernel and initramfs boot successfully
in Limbo on Android and the guest reaches a VANTOR login or shell. See [testing-limbo.md](testing-limbo.md).
