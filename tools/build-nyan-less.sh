#!/usr/bin/env bash
set -Eeuo pipefail

ARCH=${1:?usage: build-nyan-less.sh x86_64|i486}
OUT=${2:-build/nyan-native}
case "$ARCH" in x86_64|i486) ;; *) echo "Unsupported architecture: $ARCH" >&2; exit 2;; esac
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$ROOT/build/less-work-$ARCH"
OUT="$ROOT/$OUT"
rm -rf "$WORK" "$OUT/less-710-$ARCH.tar.gz"
mkdir -p "$WORK/downloads" "$WORK/src" "$WORK/sysroot" "$WORK/stage" "$OUT"

case "$ARCH" in
  x86_64)
    TOOLCHAIN="x86_64-linux-musl-cross"
    TOOLCHAIN_SHA="c5d410d9f82a4f24c549fe5d24f988f85b2679b452413a9f7e5f7b956f2fe7ea"
    ARCH_FLAGS=""
    ;;
  i486)
    TOOLCHAIN="i486-linux-musl-cross"
    TOOLCHAIN_SHA="1b7eceb2022f4a664028dd314c5c44332b601bd271e40f0934b4bc8fd3b0fcf5"
    ARCH_FLAGS="-march=i486 -mno-mmx -mno-sse"
    ;;
esac
TARGET="$ARCH-linux-musl"
fetch_verify() {
  local url="$1" file="$2" expected="$3"
  curl -fL --retry 3 --retry-delay 2 "$url" -o "$file"
  echo "$expected  $file" | sha256sum -c -
}
fetch_verify "https://github.com/musl-cc/musl.cc/releases/download/v0.0.1/$TOOLCHAIN.tgz" "$WORK/downloads/$TOOLCHAIN.tgz" "$TOOLCHAIN_SHA"
mkdir -p "$WORK/toolchain"
tar -xzf "$WORK/downloads/$TOOLCHAIN.tgz" -C "$WORK/toolchain" --strip-components=1
export PATH="$WORK/toolchain/bin:$PATH"
export CC="$TARGET-gcc" AR="$TARGET-ar" RANLIB="$TARGET-ranlib" STRIP="$TARGET-strip"
export CFLAGS="-Os -ffunction-sections -fdata-sections $ARCH_FLAGS"
export LDFLAGS="-static -Wl,--gc-sections"
BUILD_TRIPLET="$(gcc -dumpmachine)"

NCURSES="$WORK/downloads/ncurses-6.6.tar.gz"
fetch_verify "https://ftp.gnu.org/pub/gnu/ncurses/ncurses-6.6.tar.gz" "$NCURSES" "355b4cbbed880b0381a04c46617b7656e362585d52e9cf84a67e2009b749ff11"
tar -xzf "$NCURSES" -C "$WORK/src"
mkdir -p "$WORK/build-ncurses"
(
  cd "$WORK/build-ncurses"
  "$WORK/src/ncurses-6.6/configure" --build="$BUILD_TRIPLET" --host="$TARGET" --prefix=/usr/local \\
    --with-normal --without-shared --without-debug --without-ada --without-cxx \\
    --without-progs --without-tests --without-manpages --enable-widec \\
    --disable-db-install --with-termlib --with-build-cc=cc
  make -j2
  make install.libs install.includes DESTDIR="$WORK/sysroot"
)
ln -sf libtinfow.a "$WORK/sysroot/usr/local/lib/libtinfo.a"

LESS="$WORK/downloads/less-710.tar.gz"
fetch_verify "https://www.greenwoodsoftware.com/less/less-710.tar.gz" "$LESS" "d1008fb78dcae1323ddab664bcb352a61f022b1b131bd8018548e021d975ec7a"
tar -xzf "$LESS" -C "$WORK/src"
mkdir -p "$WORK/build-less"
(
  cd "$WORK/build-less"
  export CPPFLAGS="-I$WORK/sysroot/usr/local/include/ncursesw -I$WORK/sysroot/usr/local/include"
  export LIBS="-L$WORK/sysroot/usr/local/lib -lncursesw -ltinfow"
  export LDFLAGS="-static -L$WORK/sysroot/usr/local/lib -Wl,--gc-sections"
  "$WORK/src/less-710/configure" --build="$BUILD_TRIPLET" --host="$TARGET" --prefix=/usr/local --with-curses
  make -j2
  make install DESTDIR="$WORK/stage"
)
BIN="$WORK/stage/usr/local/bin/less"
test -x "$BIN"
"$STRIP" "$BIN"
"$TARGET-readelf" -h "$BIN" > "$WORK/elf-header.txt"
if "$TARGET-readelf" -l "$BIN" | grep -q 'INTERP'; then
  echo "less unexpectedly requires a dynamic interpreter" >&2
  exit 1
fi
if [ "$ARCH" = i486 ]; then
  qemu-i386 -cpu 486 "$BIN" --version
  printf 'VANTOR Nyan pager smoke test\n' | qemu-i386 -cpu 486 "$BIN" -F -X
else
  "$BIN" --version
  printf 'VANTOR Nyan pager smoke test\n' | "$BIN" -F -X
fi
mkdir -p "$WORK/stage/usr/local/share/doc/less"
cp "$WORK/src/less-710/COPYING" "$WORK/stage/usr/local/share/doc/less/COPYING"
cat > "$WORK/stage/usr/local/share/doc/less/VANTOR-BUILD" <<EOF
less 710
Target: $ARCH
C library: musl (static)
Source SHA-256: d1008fb78dcae1323ddab664bcb352a61f022b1b131bd8018548e021d975ec7a
EOF
tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner \
  -czf "$OUT/less-710-$ARCH.tar.gz" -C "$WORK/stage" .
tar -tzf "$OUT/less-710-$ARCH.tar.gz" >/dev/null
sha256sum "$OUT/less-710-$ARCH.tar.gz"
echo "Built and smoke-tested less 710 for $ARCH"
