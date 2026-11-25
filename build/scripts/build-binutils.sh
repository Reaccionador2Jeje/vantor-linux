#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT/build/config/vantor.conf"

: "${VANTOR_TARGET:?missing VANTOR_TARGET}"
: "${VANTOR_BUILD_JOBS:?missing VANTOR_BUILD_JOBS}"

TOOLS_PREFIX="$ROOT/build/tools"
SYSROOT="$ROOT/build/sysroot"
SOURCE="$ROOT/build/work/sources/binutils-2.47"
BUILD="$ROOT/build/work/build-binutils"

[[ -f "$SOURCE/configure" ]] || { echo "[ERROR] Binutils source not extracted: $SOURCE" >&2; exit 1; }
mkdir -p "$TOOLS_PREFIX" "$SYSROOT" "$BUILD"

cd "$BUILD"
"$SOURCE/configure" \
  --target="$VANTOR_TARGET" \
  --prefix="$TOOLS_PREFIX" \
  --with-sysroot="$SYSROOT" \
  --disable-nls \
  --disable-werror \
  --disable-gprofng \
  --disable-gold \
  --enable-deterministic-archives

make -j"$VANTOR_BUILD_JOBS"
make install

"$TOOLS_PREFIX/bin/$VANTOR_TARGET-ld" --version
echo "[OK] Binutils pass 1 installed for $VANTOR_TARGET"
