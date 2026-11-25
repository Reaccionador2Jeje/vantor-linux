# Nyan — VANTOR package manager

Nyan is the native package-management project for VANTOR Linux. It will provide repository refresh, package search, installation, removal, upgrades, dependency resolution, and package verification.

## Genesis prototype

The initial POSIX shell client is at `packages/nyan/nyan`. It supports:

- `nyan update` — download the architecture-specific package index.
- `nyan list` — display indexed packages.
- `nyan install NAME` — download, verify SHA-256, and extract an archive.
- `nyan remove NAME` — remove files recorded for a package.

Configuration is available through `NYAN_REPO`, `NYAN_ARCH`, and `NYAN_ROOT`. The root override is intended for isolated testing.

## Current limitations

This is an early prototype, not a safe production package manager. It has no dependency solver, signatures, transactional rollback, file-conflict database, upgrade logic, or reliable shared-file ownership. Package archives must be trusted. Do not run it against a real system until those features and security tests are complete.

## Repository layout

- `packages/repository/<arch>/Packages` — tab-separated repository index.
- `packages/repository/README.md` — index and archive format.
- `packages/nyan/nyan` — client prototype.
- Cloudflare mirror paths: `/repo/<arch>/Packages` and `/packages/<arch>/<archive>`.
