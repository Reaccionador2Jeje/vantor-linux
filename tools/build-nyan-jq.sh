#!/usr/bin/env bash
set -Eeuo pipefail

ARCH=${1:?usage: build-nyan-jq.sh x86_64|i486}
OUT=${2:-build/nyan-native}
case "$ARCH" in x86_64|i486) ;; *) echo "Unsupported architecture: $ARCH" >&2; exit 2;; esac
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$ROOT/build/jq-work-$ARCH"
OUT="$ROOT/$OUT"
rm -rf "$WORK" "$OUT/jq-1.8.1-$ARCH.tar.gz"
mkdir -p "$WORK/downloads" "$WORK/src" "$WORK/stage" "$OUT"

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
export CFLAGS="-Os -std=c99 -ffunction-sections -fdata-sections $ARCH_FLAGS"
export LDFLAGS="-static -Wl,-Bstatic -Wl,--gc-sections"
BUILD_TRIPLET="$(gcc -dumpmachine)"

JQ="$WORK/downloads/jq-1.8.1.tar.gz"
fetch_verify "https://github.com/jqlang/jq/releases/download/jq-1.8.1/jq-1.8.1.tar.gz" "$JQ" "2be64e7129cecb11d5906290eba10af694fb9e3e7f9fc208a311dc33ca837eb0"
tar -xzf "$JQ" -C "$WORK/src"
mkdir -p "$WORK/build-jq"
(
  cd "$WORK/build-jq"
  "$WORK/src/jq-1.8.1/configure" --build="$BUILD_TRIPLET" --host="$TARGET" \
    --prefix=/usr/local --disable-shared --enable-static \
    --with-oniguruma=builtin --disable-maintainer-mode --disable-docs
  make -j2
  make install DESTDIR="$WORK/stage"
)
BIN="$WORK/stage/usr/local/bin/jq"
test -x "$BIN"
"$STRIP" "$BIN"
"$TARGET-readelf" -h "$BIN" > "$WORK/elf-header.txt"
if "$TARGET-readelf" -l "$BIN" | grep -q 'INTERP'; then
  echo "jq unexpectedly requires a dynamic interpreter" >&2
  exit 1
fi
if [ "$ARCH" = i486 ]; then
  qemu-i386 -cpu 486 "$BIN" --version
  printf '{"vantor":"linux","packages":12}\n' | qemu-i386 -cpu 486 "$BIN" -r '.vantor'
else
  "$BIN" --version
  printf '{"vantor":"linux","packages":12}\n' | "$BIN" -r '.vantor'
fi
mkdir -p "$WORK/stage/usr/local/share/doc/jq"
cp "$WORK/src/jq-1.8.1/COPYING" "$WORK/stage/usr/local/share/doc/jq/COPYING"
cat > "$WORK/stage/usr/local/share/doc/jq/VANTOR-BUILD" <<EOF
jq 1.8.1
Target: $ARCH
C library: musl (static)
Regex engine: bundled Oniguruma
Source SHA-256: 2be64e7129cecb11d5906290eba10af694fb9e3e7f9fc208a311dc33ca837eb0
EOF
tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner \
  -czf "$OUT/jq-1.8.1-$ARCH.tar.gz" -C "$WORK/stage" .
tar -tzf "$OUT/jq-1.8.1-$ARCH.tar.gz" >/dev/null
sha256sum "$OUT/jq-1.8.1-$ARCH.tar.gz"
echo "Built and smoke-tested jq 1.8.1 for $ARCH"
