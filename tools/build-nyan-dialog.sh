#!/usr/bin/env bash
set -Eeuo pipefail

ARCH=${1:?usage: build-nyan-dialog.sh x86_64|i486}
OUT=${2:-build/nyan-native}
case "$ARCH" in x86_64|i486) ;; *) echo "Unsupported architecture: $ARCH" >&2; exit 2;; esac
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$ROOT/build/dialog-work-$ARCH"
OUT="$ROOT/$OUT"
rm -rf "$WORK" "$OUT/dialog-1.3-20260721-$ARCH.tar.gz"
mkdir -p "$WORK/src" "$WORK/downloads" "$WORK/sysroot" "$WORK/stage" "$OUT"

case "$ARCH" in
  x86_64)
    TOOLCHAIN="x86_64-linux-musl-cross"
    TOOLCHAIN_SHA="c5d410d9f82a4f24c549fe5d24f988f85b2679b452413a9f7e5f7b956f2fe7ea"
    ;;
  i486)
    TOOLCHAIN="i486-linux-musl-cross"
    TOOLCHAIN_SHA="1b7eceb2022f4a664028dd314c5c44332b601bd271e40f0934b4bc8fd3b0fcf5"
    ;;
esac
TARGET="$ARCH-linux-musl"
curl -fL --retry 3 "https://github.com/musl-cc/musl.cc/releases/download/v0.0.1/$TOOLCHAIN.tgz" -o "$WORK/downloads/$TOOLCHAIN.tgz"
echo "$TOOLCHAIN_SHA  $WORK/downloads/$TOOLCHAIN.tgz" | sha256sum -c -
mkdir -p "$WORK/toolchain"
tar -xzf "$WORK/downloads/$TOOLCHAIN.tgz" -C "$WORK/toolchain" --strip-components=1
export PATH="$WORK/toolchain/bin:$PATH"
export CC="$TARGET-gcc" AR="$TARGET-ar" RANLIB="$TARGET-ranlib" STRIP="$TARGET-strip"
export CFLAGS="-Os -ffunction-sections -fdata-sections"
export LDFLAGS="-static -Wl,--gc-sections"
BUILD_TRIPLET="$(gcc -dumpmachine)"

curl -fL --retry 3 https://ftp.gnu.org/pub/gnu/ncurses/ncurses-6.6.tar.gz -o "$WORK/downloads/ncurses-6.6.tar.gz"
echo "355b4cbbed880b0381a04c46617b7656e362585d52e9cf84a67e2009b749ff11  $WORK/downloads/ncurses-6.6.tar.gz" | sha256sum -c -
tar -xzf "$WORK/downloads/ncurses-6.6.tar.gz" -C "$WORK/src"
mkdir -p "$WORK/build-ncurses"
(
  cd "$WORK/build-ncurses"
  "$WORK/src/ncurses-6.6/configure" --build="$BUILD_TRIPLET" --host="$TARGET" --prefix=/usr/local \
    --with-normal --without-shared --without-debug --without-ada --without-cxx \
    --without-progs --without-tests --without-manpages --enable-widec \
    --disable-db-install --with-termlib --with-build-cc=cc
  make -j2
  make install.libs install.includes DESTDIR="$WORK/sysroot"
)
ln -sf libtinfow.a "$WORK/sysroot/usr/local/lib/libtinfo.a"

# The upstream snapshot is pinned to a maintainer-signed commit.
git -c advice.detachedHead=false clone --filter=blob:none --no-checkout https://github.com/ThomasDickey/dialog-snapshots.git "$WORK/src/dialog"
git -C "$WORK/src/dialog" fetch --depth=1 origin e65d9f4ed89ce05eeb5a266e14804bcd71416bca
git -C "$WORK/src/dialog" checkout --detach e65d9f4ed89ce05eeb5a266e14804bcd71416bca
test "$(git -C "$WORK/src/dialog" rev-parse HEAD)" = "e65d9f4ed89ce05eeb5a266e14804bcd71416bca"
mkdir -p "$WORK/build-dialog"
(
  cd "$WORK/build-dialog"
  export CPPFLAGS="-I$WORK/sysroot/usr/local/include/ncursesw -I$WORK/sysroot/usr/local/include"
  export LIBS="-L$WORK/sysroot/usr/local/lib -lncursesw -ltinfow"
  export LDFLAGS="-static -L$WORK/sysroot/usr/local/lib -Wl,--gc-sections"
  "$WORK/src/dialog/configure" --build="$BUILD_TRIPLET" --host="$TARGET" \
    --prefix=/usr/local --disable-nls --enable-widec --with-ncursesw --disable-manpages
  make -j2
  make install DESTDIR="$WORK/stage"
)

BIN="$WORK/stage/usr/local/bin/dialog"
test -x "$BIN"
"$STRIP" "$BIN"
"$TARGET-readelf" -h "$BIN" > "$WORK/elf-header.txt"
if "$TARGET-readelf" -l "$BIN" | grep -q 'INTERP'; then
  echo "dialog unexpectedly requires a dynamic interpreter" >&2
  exit 1
fi
if [ "$ARCH" = i486 ]; then qemu-i386 -cpu 486 "$BIN" --version; else "$BIN" --version; fi
mkdir -p "$WORK/stage/usr/local/share/doc/dialog"
cat > "$WORK/stage/usr/local/share/doc/dialog/VANTOR-BUILD" <<EOF
Dialog snapshot t20260721
Upstream commit: e65d9f4ed89ce05eeb5a266e14804bcd71416bca
Target: $ARCH
C library: musl (static)
Terminal library: ncurses 6.6 (static)
EOF
tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner \
  -czf "$OUT/dialog-1.3-20260721-$ARCH.tar.gz" -C "$WORK/stage" .
tar -tzf "$OUT/dialog-1.3-20260721-$ARCH.tar.gz" >/dev/null
sha256sum "$OUT/dialog-1.3-20260721-$ARCH.tar.gz"
echo "Built and smoke-tested Dialog for $ARCH"
