# Lua language package for VANTOR

This directory defines the reproducible build of the first official Nyan programming-language package.

- Package name: `lua`
- Upstream version: `5.4.9`
- Target: `x86_64`
- Runtime: statically linked with musl for the initial bootstrap environment
- Commands after installation: `lua`, `luac`
- Upstream source: https://www.lua.org/ftp/lua-5.4.9.tar.gz
- SHA-256: `2335b6c582a52654f94612bf10d2f4672805d05329aa6568b1d8cd9e5c6fb8e6`

The GitHub Actions workflow downloads the official source, verifies its published SHA-256, builds and smoke-tests the interpreter, assembles a root-relative package archive, and publishes it to the Nyan GitHub Releases mirror.

The package is not considered available to users until the workflow completes successfully and the repository index contains the package row.

The package archive is validated from a saved tar listing so CI can run with strict pipeline error handling.

The CI build verifies the interpreter is static from ELF file metadata before packaging.
