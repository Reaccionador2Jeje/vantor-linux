# VANTOR programming languages

Nyan distributes programming-language runtimes as ordinary, checksum-verified VANTOR packages.

## Available now

| Package | Version | Architecture | Commands | State |
|---|---:|---|---|---|
| `lua` | 5.4.9 | x86_64 | `lua`, `luac` | Published in Nyan |

Install Lua with:

```sh
nyan install lua
```

The package is built from the official Lua source archive, checked against its pinned SHA-256, statically linked with musl, smoke-tested, and published to the `nyan-repository` GitHub Release. Its package metadata is in `packages/repository/x86_64/Packages`.

## Build and publication

- Recipe/workflow: `.github/workflows/build-lua.yml`
- Build notes: `core/languages/lua/README.md`
- Publisher: `tools/publish-package.sh`

A language is considered available only after its real archive has been built, tested, uploaded, and added to the architecture index. Catalog entries marked `planned` or `building` are not installable.

## Next language targets

- C toolchain: compiler, assembler, linker, libc headers and development files must be packaged as a coherent, tested toolchain.
- Python 3: interpreter, standard library and required runtime modules.
- JavaScript: a maintained runtime and its supporting libraries.

These are roadmap targets, not published packages yet. The initial development profile currently depends on Lua only.
