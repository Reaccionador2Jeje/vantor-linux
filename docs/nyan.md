# Nyan — VANTOR package manager

Nyan is VANTOR's native package manager. It currently supports repository refresh, package discovery, SHA-256-verified archive installation, dependency-first installation, and removal.

## Commands

- `nyan update` — fetch the architecture-specific index.
- `nyan list` — list available packages.
- `nyan search TERM` — search package names and descriptions.
- `nyan show NAME` — inspect version, architecture, description and dependencies.
- `nyan languages` — list programming-language packages.
- `nyan catalog` — show bundled, published and planned core packages.
- `nyan install NAME` — resolve and install declared dependencies before the requested package.
- `nyan profiles` — list planned system profiles and their publication status.
- `nyan install-profile NAME` — reserved for profiles whose full package sets have been published.
- `nyan remove NAME` — remove files recorded for a package.

Configuration: `NYAN_REPO`, `NYAN_ARCH`, and `NYAN_ROOT`.

## Repository format

The tab-separated `Packages` index starts with `# VANTOR-PACKAGES 1`. Each row has six required fields and one optional dependency field:

`name<TAB>version<TAB>architecture<TAB>sha256<TAB>archive<TAB>description<TAB>dependency1,dependency2`

The optional seventh field is a comma-separated list of package names. Nyan installs dependencies first and detects dependency cycles. Published installation profiles are represented by meta-packages named `vantor-profile-PROFILE`; `nyan install-profile development` installs the profile package and its dependencies. Existing six-field rows remain valid. Dependency installation is not yet transactional: if a later package fails, already installed dependencies remain installed.

Nyan exposes five profile names:

- `minimal` — the primary VANTOR edition. Its meta-package depends on `vantor-base-files`, which contains the VANTOR bootstrap userspace and static BusyBox.
- `base` — reserved for a future split of the Minimal base into smaller independently maintained packages.
- `desktop` — graphics stack, display server, window manager and desktop applications; not yet published.
- `development` — Lua 5.4.9 starter language environment.
- `network` — DHCP, DNS, TLS and network diagnostic tools; not yet published.

The local package catalog is maintained in `packages/catalog.tsv` and is installed at `/usr/share/nyan/catalog.tsv`. It distinguishes bundled tools from packages that are still planned; planned entries are not installable yet.

The Minimal package workflow is `.github/workflows/build-nyan-minimal.yml`. It builds the base payload from the rootfs generator and BusyBox, then publishes the base package and Minimal meta-package. It does not make sudo, nano, full Vim or Fastfetch available yet; those remain separate package targets. The i486 package workflow builds a separate 32-bit BusyBox and publishes to `packages/repository/i486/Packages`.


## VANTOR Community Mirror

The initial mirror uses GitHub Releases, not Cloudflare R2:
- Indexes live under `packages/repository/<arch>/Packages`.
- Package assets are stored in the GitHub Release tagged `nyan-repository`.
- The website Worker proxies index requests and redirects archive requests to GitHub Releases.
- `tools/publish-package.sh` and package workflows automate publishing and SHA-256 index updates.

See [the repository format and publishing guide](../packages/repository/README.md).

## Security and limitations

This is experimental, not production-ready. It lacks signed repository metadata, transactional rollback, upgrade support, maintainer scripts, automatic dependency cleanup and shared-file ownership. The client rejects archive traversal, links and special files, refuses to overwrite existing system paths, and tracks installed file lists. SHA-256 alone does not authenticate repository publishers. Do not use this version to modify a real system.

## Lua 5.4.9

Lua is the first language package, built statically with musl. After its archive is published:

```sh
nyan update
nyan languages
nyan install lua
lua -v
```

The initial package does not yet provide LuaRocks.
