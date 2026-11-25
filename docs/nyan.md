# Nyan — VANTOR package manager

Nyan is VANTOR's native package manager. The current shell prototype supports repository refresh, listing, basic archive installation and removal.

## Commands
- `nyan update` — fetch the architecture-specific index.
- `nyan list` — list indexed packages.
- `nyan install NAME` — download and verify SHA-256 before extraction.
- `nyan remove NAME` — remove files recorded for a package.

Configuration: `NYAN_REPO`, `NYAN_ARCH`, and `NYAN_ROOT`.

## VANTOR Community Mirror

The initial mirror uses GitHub Releases, not Cloudflare R2:
- Indexes live under `packages/repository/<arch>/Packages`.
- Package assets are stored in the GitHub Release tagged `nyan-repository`.
- The website Worker proxies index requests and redirects archive requests to GitHub Releases.
- `tools/publish-package.sh` and `.github/workflows/publish-package.yml` automate publishing and SHA-256 index updates.

See [the repository format and publishing guide](../packages/repository/README.md).

## Current limitations

This is experimental, not production-ready. It lacks dependency resolution, signatures, transactional rollback, file-conflict detection, reliable shared-file ownership, upgrade logic and safe handling of maintainer scripts. SHA-256 alone does not authenticate repository publishers. Do not use this version to modify a real system.
