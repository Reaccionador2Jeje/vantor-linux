#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "[VANTOR] Checking source pins..."
make sources-ready
make fetch-sources

mkdir -p build/work/sources build/logs
python3 tools/extract-source.py build/distfiles/binutils-2.47.tar.xz build/work/sources/binutils
python3 tools/extract-source.py build/distfiles/gcc-16.2.0.tar.xz build/work/sources/gcc

export PATH="$ROOT/build/tools/bin:$PATH"
echo "[VANTOR] Building Binutils pass 1..."
bash build/scripts/build-binutils.sh 2>&1 | tee build/logs/binutils-pass1.log
echo "[VANTOR] Building GCC pass 1..."
bash build/scripts/build-gcc.sh 2>&1 | tee build/logs/gcc-pass1.log
echo "[VANTOR] Initial cross-toolchain stage completed."
