#!/usr/bin/env bash
set -Eeuo pipefail

ARCH=${1:?usage: build-nyan-htop.sh x86_64|i486}
OUT=${2:-build/nyan-native}
case "$ARCH" in x86_64|i486) ;; *) echo "Unsupported architecture: $ARCH" >&2; exit 2;; esac
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$ROOT/build/htop-work-$ARCH"
OUT="$ROOT/$OUT"
rm -rf "$WORK" "$OUT/htop-3.4.1-$ARCH.tar.gz"
mkdir -p "$WORK/downloads" "$WORK/src" "$WORK/sysroot" "$WORK/stage" "$OUT"

fetch_verify() {
  local url="$1" file="$2" expected="$3"
  curl -fL --retry 3 --retry-delay 2 "$url" -o "$file"
  echo "$expected  $file" | sha256sum -c -
}

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
fetch_verify "https://github.com/musl-cc/musl.cc/releases/download/v0.0.1/$TOOLCHAIN.tgz" "$WORK/downloads/$TOOLCHAIN.tgz" "$TOOLCHAIN_SHA"
mkdir -p "$WORK/toolchain"
tar -xzf "$WORK/downloads/$TOOLCHAIN.tgz" -C "$WORK/toolchain" --strip-components=1
export PATH="$WORK/toolchain/bin:$PATH"
export CC="$TARGET-gcc" AR="$TARGET-ar" RANLIB="$TARGET-ranlib" STRIP="$TARGET-strip"
export CFLAGS="-Os -ffunction-sections -fdata-sections"
export LDFLAGS="-static -Wl,--gc-sections"
BUILD_TRIPLET="$(gcc -dumpmachine)"

NCURSES="$WORK/downloads/ncurses-6.6.tar.gz"
fetch_verify "https://ftp.gnu.org/pub/gnu/ncurses/ncurses-6.6.tar.gz" "$NCURSES" "355b4cbbed880b0381a04c46617b7656e362585d52e9cf84a67e2009b749ff11"
tar -xzf "$NCURSES" -C "$WORK/src"
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

HTOP="$WORK/downloads/htop-3.4.1.tar.xz"
fetch_verify "https://github.com/htop-dev/htop/releases/download/3.4.1/htop-3.4.1.tar.xz" "$HTOP" "904f7d4580fc11cffc7e0f06895a4789e0c1c054435752c151e812fead9f6220"
tar -xJf "$HTOP" -C "$WORK/src"
mkdir -p "$WORK/build-htop"
(
  cd "$WORK/build-htop"
  export CPPFLAGS="-I$WORK/sysroot/usr/local/include/ncursesw -I$WORK/sysroot/usr/local/include"
  export CURSES_CFLAGS="-I$WORK/sysroot/usr/local/include/ncursesw -D_XOPEN_SOURCE=600"
  export CURSES_LIBS="-L$WORK/sysroot/usr/local/lib -lncursesw -ltinfow"
  export LDFLAGS="-static -L$WORK/sysroot/usr/local/lib -Wl,--gc-sections"
  "$WORK/src/htop-3.4.1/configure" --build="$BUILD_TRIPLET" --host="$TARGET" \
    --prefix=/usr/local --enable-static --with-curses=ncursesw --disable-hwloc
  make -j2
  make install DESTDIR="$WORK/stage"
)

BIN="$WORK/stage/usr/local/bin/htop"
test -x "$BIN"
"$STRIP" "$BIN"
"$TARGET-readelf" -h "$BIN" > "$WORK/elf-header.txt"
if "$TARGET-readelf" -l "$BIN" | grep -q 'INTERP'; then
  echo "htop unexpectedly requires a dynamic interpreter" >&2
  exit 1
fi
if [ "$ARCH" = i486 ]; then qemu-i386 -cpu 486 "$BIN" --version; else "$BIN" --version; fi

mkdir -p "$WORK/stage/usr/local/share/doc/htop"
cat > "$WORK/stage/usr/local/share/doc/htop/VANTOR-BUILD" <<EOF
htop 3.4.1
Target: $ARCH
C library: musl (static)
Terminal library: ncurses 6.6 (static)
Optional hwloc support: disabled
EOF
tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner \
  -czf "$OUT/htop-3.4.1-$ARCH.tar.gz" -C "$WORK/stage" .
tar -tzf "$OUT/htop-3.4.1-$ARCH.tar.gz" >/dev/null
sha256sum "$OUT/htop-3.4.1-$ARCH.tar.gz"
echo "Built and smoke-tested htop 3.4.1 for $ARCH"
