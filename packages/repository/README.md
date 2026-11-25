# VANTOR package repository

Nyan reads a tab-separated index at:

`/repo/<architecture>/Packages`

Package archives are served from:

`/packages/<architecture>/<archive>`

## Index format — V1

The first line must be:

`# VANTOR-PACKAGES 1`

Each subsequent record is one tab-separated row:

`name<TAB>version<TAB>architecture<TAB>sha256<TAB>archive<TAB>description`

- Architecture is `x86_64`, `aarch64`, or `all`.
- Archives are gzip-compressed tar files (`.tar.gz`).
- SHA-256 is the lowercase digest of the exact archive bytes.
- Archive paths are flat filenames; path traversal and absolute paths are forbidden.
- A package archive contains paths relative to the target root (for example `usr/bin/hello`).
- Empty repositories contain only the format header and comments.

## Security and current limitations

Nyan verifies SHA-256 before extracting and rejects unsafe archive paths. A digest protects against accidental corruption, but does not authenticate who published an index. Signed repository metadata, dependency resolution, package scripts/hooks, rollback transactions, file ownership conflicts, and robust shared-file tracking are not implemented yet. Do not use this prototype as a production package manager.

The official mirror is being prepared on Cloudflare Workers + R2. Package downloads remain unavailable until R2 is enabled and release artifacts are published.
