#!/usr/bin/env bash
set -Eeuo pipefail

ARCH=${1:?usage: build-nyan-native.sh x86_64|i486}
OUT=${2:-build/nyan-native}
case "$ARCH" in x86_64|i486) ;; *) echo "Unsupported architecture: $ARCH" >&2; exit 2;; esac

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$ROOT/build/native-work-$ARCH"
OUT="$ROOT/$OUT"
rm -rf "$WORK" "$OUT"
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
TOOLCHAIN_ARCHIVE="$WORK/downloads/$TOOLCHAIN.tgz"
fetch_verify "https://github.com/musl-cc/musl.cc/releases/download/v0.0.1/$TOOLCHAIN.tgz" "$TOOLCHAIN_ARCHIVE" "$TOOLCHAIN_SHA"
mkdir -p "$WORK/toolchain"
tar -xzf "$TOOLCHAIN_ARCHIVE" -C "$WORK/toolchain" --strip-components=1
export PATH="$WORK/toolchain/bin:$PATH"
export CC="$TARGET-gcc" AR="$TARGET-ar" RANLIB="$TARGET-ranlib" STRIP="$TARGET-strip"
export CFLAGS="-Os -ffunction-sections -fdata-sections"
export LDFLAGS="-static -Wl,--gc-sections"
BUILD_TRIPLET="$(gcc -dumpmachine)"
"$CC" -dumpmachine
"$CC" -v 2>&1 | tail -n 1

NCURSES_TARBALL="$WORK/downloads/ncurses-6.6.tar.gz"
fetch_verify "https://ftp.gnu.org/pub/gnu/ncurses/ncurses-6.6.tar.gz" "$NCURSES_TARBALL" "355b4cbbed880b0381a04c46617b7656e362585d52e9cf84a67e2009b749ff11"
tar -xzf "$NCURSES_TARBALL" -C "$WORK/src"
mkdir -p "$WORK/build-ncurses"
(
  cd "$WORK/build-ncurses"
  "$WORK/src/ncurses-6.6/configure" \
    --build="$BUILD_TRIPLET" --host="$TARGET" --prefix=/usr/local \
    --with-normal --without-shared --without-debug --without-ada --without-cxx \
    --without-progs --without-tests --without-manpages --enable-widec \
    --disable-db-install --with-termlib --with-build-cc=cc
  make -j2
  make install.libs install.includes DESTDIR="$WORK/sysroot"
)
# Nano's configure probes the narrow terminfo name even with wide ncurses.
# Both names resolve to the same statically built musl-compatible archive.
ln -sf libtinfow.a "$WORK/sysroot/usr/local/lib/libtinfo.a"

NANO_TARBALL="$WORK/downloads/nano-9.2.tar.xz"
fetch_verify "https://ftp.gnu.org/gnu/nano/nano-9.2.tar.xz" "$NANO_TARBALL" "05ecb99247b782e8a5b3a25ed4101dd034b0236902f7449bc9795b717642f7e9"
tar -xJf "$NANO_TARBALL" -C "$WORK/src"
mkdir -p "$WORK/build-nano"
(
  cd "$WORK/build-nano"
  export CPPFLAGS="-I$WORK/sysroot/usr/local/include/ncursesw -I$WORK/sysroot/usr/local/include"
  export LDFLAGS="-static -L$WORK/sysroot/usr/local/lib -Wl,--gc-sections"
  export LIBS="-lncursesw -ltinfow"
  if ! "$WORK/src/nano-9.2/configure" \
    --build="$BUILD_TRIPLET" --host="$TARGET" --prefix=/usr/local \
    --disable-nls --disable-manpages --enable-tiny; then
    echo "[ERROR] nano configure failed; relevant config.log diagnostics:" >&2
    grep -A8 -B4 -E "cannot find|undefined reference|error:|failed program" config.log | tail -n 100 >&2 || tail -n 100 config.log >&2
    exit 1
  fi
  make -j2
  make install DESTDIR="$WORK/stage"
)

BIN="$WORK/stage/usr/local/bin/nano"
test -x "$BIN"
"$STRIP" "$BIN"
"$TARGET-readelf" -h "$BIN" > "$WORK/elf-header.txt"
if "$TARGET-readelf" -l "$BIN" | grep -q 'INTERP'; then
  echo "nano unexpectedly requires a dynamic interpreter" >&2
  exit 1
fi
if [ "$ARCH" = i486 ]; then
  qemu-i386 -cpu 486 "$BIN" --version
else
  "$BIN" --version
fi

mkdir -p "$WORK/stage/usr/local/share/doc/nano"
cat > "$WORK/stage/usr/local/share/doc/nano/VANTOR-BUILD" <<EOF
GNU nano 9.2
Target: $ARCH
C library: musl (static)
Terminal library: ncurses 6.6 (static)
Build profile: tiny, no NLS
EOF
tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner \
  -czf "$OUT/nano-9.2-$ARCH.tar.gz" -C "$WORK/stage" .
tar -tzf "$OUT/nano-9.2-$ARCH.tar.gz" >/dev/null
sha256sum "$OUT/nano-9.2-$ARCH.tar.gz"
echo "Built and smoke-tested GNU nano 9.2 for $ARCH"
