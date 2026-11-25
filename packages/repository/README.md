# VANTOR Community Mirror

The initial official mirror uses GitHub Releases for binary assets and this repository for package indexes. It requires no Cloudflare R2 or payment method.

## Public endpoints

- Index: `https://vantor-linux.cristopheriguaran-7.workers.dev/repo/<architecture>/Packages`
- Package: `https://vantor-linux.cristopheriguaran-7.workers.dev/packages/<architecture>/<archive>`
- Asset storage: GitHub Release tag `nyan-repository`

The Worker proxies indexes from this public repository and redirects package requests to matching GitHub Release assets.

## Index format — V1

First line: `# VANTOR-PACKAGES 1`. Each package row is tab-separated:

`name<TAB>version<TAB>architecture<TAB>sha256<TAB>archive<TAB>description`

Architectures: `x86_64`, `aarch64`, or `all`. Archives are gzip-compressed tar files. SHA-256 is the lowercase digest of exact archive bytes. Archive filenames must be flat filenames without path separators.

## Publishing

Use GitHub Actions workflow **Publish Nyan package**. Supply a repository-relative archive path, package name, version, architecture and description. The workflow validates the archive, calculates SHA-256, uploads the asset to release `nyan-repository`, updates the index and pushes the index commit.

The first published language package is Lua 5.4.9 for x86_64. See `packages/repository/x86_64/Packages` for its current digest and archive filename.

## Limits and security

GitHub Releases is suitable for an initial community repository, not an unlimited CDN or high-availability mirror. SHA-256 detects corruption but does not authenticate the publisher. Signed repository metadata, dependency resolution, transactional installation, shared-file ownership and rollback remain future work. The Nyan Genesis client currently rejects links/special archive entries and refuses to overwrite existing files. The current Nyan prototype is not production-safe.
