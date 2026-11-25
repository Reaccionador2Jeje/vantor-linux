#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT/build/config/vantor.conf"

: "${VANTOR_TARGET:?missing VANTOR_TARGET}"
: "${VANTOR_BUILD_JOBS:?missing VANTOR_BUILD_JOBS}"

TOOLS_PREFIX="$ROOT/build/tools"
SYSROOT="$ROOT/build/sysroot"
SOURCE="$ROOT/build/work/sources/gcc"
BUILD="$ROOT/build/work/build-gcc"

[[ -x "$TOOLS_PREFIX/bin/$VANTOR_TARGET-as" ]] || { echo "[ERROR] Build Binutils pass 1 first." >&2; exit 1; }
[[ -f "$SOURCE/configure" ]] || { echo "[ERROR] GCC source not extracted: $SOURCE" >&2; exit 1; }
mkdir -p "$SYSROOT" "$BUILD"

cd "$BUILD"
"$SOURCE/configure" \
  --target="$VANTOR_TARGET" \
  --prefix="$TOOLS_PREFIX" \
  --with-sysroot="$SYSROOT" \
  --with-newlib \
  --without-headers \
  --enable-languages=c \
  --disable-shared \
  --disable-threads \
  --disable-libatomic \
  --disable-libgomp \
  --disable-libquadmath \
  --disable-libssp \
  --disable-libstdcxx \
  --disable-nls \
  --disable-multilib \
  --disable-bootstrap

make -j"$VANTOR_BUILD_JOBS" all-gcc
make install-gcc

"$TOOLS_PREFIX/bin/$VANTOR_TARGET-gcc" --version
echo "[OK] GCC pass 1 installed for $VANTOR_TARGET (C compiler only; no target libc yet)."
