# Nyan — VANTOR package manager

Nyan is VANTOR's native package manager. The current shell prototype supports repository refresh, listing, basic archive installation and removal.

## Commands
- `nyan update` — fetch the architecture-specific index.
- `nyan list` — list indexed packages and their descriptions.
- `nyan languages` — list programming-language packages (repository entries tagged `Language:`).
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


## Programming languages

The first language package is **Lua 5.4.9** for x86_64. Its GitHub Actions workflow builds a static interpreter with musl, verifies the official upstream source checksum, runs a smoke test, and publishes the archive and package-index entry to the GitHub Releases mirror.

After the package is published:

```sh
nyan update
nyan languages
nyan install lua
lua -v
```

The package is not installable until its build-and-publish workflow succeeds and the index contains the `lua` entry. The initial package does not yet provide LuaRocks.
