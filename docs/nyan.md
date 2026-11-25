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
- `nyan installed` — list packages recorded as installed in the selected root.
- `nyan verify [NAME]` — check the installed package records and report missing files; without a name, verify every recorded package.
- `nyan remove NAME` — remove files recorded for a package. Dependencies are retained until manually removed.

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

The local package catalog is maintained in `packages/catalog.tsv` and is installed at `/usr/share/nyan/catalog.tsv`. It distinguishes bundled tools from packages that are still building or planned; only packages present in the architecture-specific repository index can be installed with Nyan. Core VANTOR commands (`vantorctl`, `vantor-hw`, `vantor-network`, `vantor-storage`, `vantor-service`, `vantor-modules`, `vantor-install`) and BusyBox `vi` belong to the base system and must be present before the first normal login. They are not optional add-ons. The `sudoers` wheel policy is already generated in the rootfs, but the actual `sudo` executable is still being integrated; do not treat the policy file as a working sudo installation. `nano` and full `vim` remain optional editor packages, while BusyBox `vi` is available immediately.

The Minimal package workflow is `.github/workflows/build-nyan-minimal.yml`. It builds the base payload from the rootfs generator and BusyBox, then publishes the base package and Minimal meta-package. The base payload is the source of truth for essential VANTOR commands. `sudo` must be built into the base payload before it is described as preinstalled; `nano`, full Vim and Fastfetch remain optional package targets. The i486 package workflow builds a separate 32-bit BusyBox and publishes to `packages/repository/i486/Packages`.


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


## Universal utility collection

The isolated workflow `.github/workflows/build-nyan-extras.yml` also builds six architecture-independent POSIX-shell packages (architecture `all`), so the same verified archive can be installed on x86_64 and i486:

- `vantor-about` — release, kernel, architecture, hostname and uptime summary.
- `vantor-doctor` — read-only checks of core VANTOR filesystems and commands.
- `vantor-netdiag` — interface, route, DNS and default-gateway report.
- `vantor-logview` — simple log viewer with pager fallback.
- `vantor-config-backup` — creates a configuration archive and refuses to overwrite an existing output.
- `vantor-mountinfo` — readable mounted-filesystem report.

The commands are installed under `/usr/local/bin`. They use POSIX shell and the base system's BusyBox utilities; no compiler, libc or desktop stack is required. The doctor, network and mount reports are diagnostic-only. Configuration backup reads selected system configuration and writes a new archive in the current directory. The same architecture-independent archive is indexed separately for x86_64 and i486 so Nyan can discover it through each architecture's normal index.

These packages are marked `building` in `packages/catalog.tsv` until the isolated workflow successfully publishes their archives and updates the `all` repository index. They do not change kernel, ISO, legacy or general CI workflows.

## More terminal and file utilities

The Nyan extras workflow also builds six additional architecture-independent tools and publishes each into both the x86_64 and i486 indexes:

- `fastfetch` — a compact VANTOR-branded system summary (a lightweight shell implementation, not the upstream Fastfetch binary).
- `tree` — recursive directory listing.
- `watch` — repeat a command at a configurable interval.
- `which` — locate executable commands through `PATH`.
- `filetype` — identify common file formats using file signatures.
- `vtop` — compact process overview using `ps` or `/proc`.

All six are POSIX-shell tools installed under `/usr/local/bin`; they do not require a second C runtime. Their package status remains `building` until the isolated publisher succeeds. Native Nano, Dialog, htop and curl binaries are not falsely represented by these scripts: they require a separately validated build/runtime strategy for both CPU baselines and TLS support.

## Native terminal tools

Native packages are built in a separate workflow so their compiler and library dependencies do not affect kernel, ISO, Legacy, or general build workflows.

The native package workflow builds multiple packages in a four-job architecture/package matrix. GNU nano 9.2 is published for both x86_64 and i486. Its builder:
- Uses pinned musl cross-toolchains for x86_64 and i486, each checked against a SHA-256 digest.
- Builds ncurses 6.6 and nano from pinned source archives with verified SHA-256 digests.
- Produces statically linked binaries, avoiding a second runtime C library on the target system.
- Smoke-tests the x86_64 binary directly and the i486 binary under a 486 CPU emulator.
- Publishes only after the build and binary checks succeed.

GNU nano is available in both architecture indexes. The second native target is htop 3.4.1, built statically against the same pinned ncurses release with optional hwloc support disabled. Its two architecture jobs run independently alongside Nano; htop remains `building` until both package archives are published and verified in the indexes. Dialog, curl with TLS, and full Vim remain planned follow-up native builds; they are not represented as available packages yet.

## Installed package inspection

Use `nyan installed` to inspect the package database for the current root. Use `nyan verify` after an installation or system repair to confirm that every file recorded for each package still exists. A named check (`nyan verify busybox`) limits verification to one package. This checks file presence and ownership records; it does not yet validate installed file contents against per-file hashes or repair packages automatically.


## Catalog, batch installs and progress animation

- `nyan browse` lists all packages published in the current architecture index.
- `nyan search TERM` searches package names and descriptions.
- `nyan install PACKAGE [PACKAGE ...]` installs several requested packages in one invocation and resolves each package's declared dependencies.
- Every package (including dependencies) gets its own progress bar. A small `=^.^=` Nyan Cat marker moves along the bar as the package advances through resolving, downloading, verification, unpacking and installation. Each package's bar stays on one updating terminal line and finishes with a green `done` status.
- Progress bars are shown only on an interactive terminal. When stdout is redirected or captured, the animation is suppressed so scripts, tests and build logs stay clean.
- The percentage represents progress through the package installation stages, not a byte-exact download meter.

The catalog is architecture-specific. Only packages present in the selected repository index are installable; planned packages are not treated as published packages.


## Extra package set (0.1.0)

The isolated workflow `.github/workflows/build-nyan-extras.yml` builds and publishes four additional packages for both x86_64 and i486:

- `vantor-hardware` — optional standalone copy of the read-only hardware inventory command at `/usr/local/bin/vantor-hw`.
- `vantor-installer` — optional standalone installer copy at `/usr/local/sbin/vantor-install`; depends on `vantor-base-files`.
- `vantor-branding` — optional copy of official SVG marks and theme assets under `/usr/local/share/vantor/branding`.
- `vantor-docs` — system overview, license and Nyan documentation under `/usr/local/share/doc/vantor`.

Run the workflow manually from GitHub Actions, or let its path-filtered push trigger it. It publishes eight architecture-specific archives and updates only the corresponding Nyan repository indexes. The ISO, kernel, legacy-image and general CI workflows are not edited by this package expansion.
