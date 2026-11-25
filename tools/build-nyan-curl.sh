#!/usr/bin/env bash
set -Eeuo pipefail

ARCH=${1:?usage: build-nyan-curl.sh x86_64|i486}
OUT=${2:-build/nyan-native}
case "$ARCH" in x86_64|i486) ;; *) echo "Unsupported architecture: $ARCH" >&2; exit 2;; esac
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$ROOT/build/curl-work-$ARCH"
OUT="$ROOT/$OUT"
rm -rf "$WORK" "$OUT/curl-8.23.0-$ARCH.tar.gz"
mkdir -p "$WORK/src" "$WORK/downloads" "$WORK/openssl" "$WORK/stage" "$OUT"

case "$ARCH" in
  x86_64)
    TOOLCHAIN="x86_64-linux-musl-cross"
    TOOLCHAIN_SHA="c5d410d9f82a4f24c549fe5d24f988f85b2679b452413a9f7e5f7b956f2fe7ea"
    OPENSSL_TARGET="linux-x86_64"
    ARCH_FLAGS=""
    ;;
  i486)
    TOOLCHAIN="i486-linux-musl-cross"
    TOOLCHAIN_SHA="1b7eceb2022f4a664028dd314c5c44332b601bd271e40f0934b4bc8fd3b0fcf5"
    OPENSSL_TARGET="linux-generic32"
    ARCH_FLAGS="-march=i486 -mno-mmx -mno-sse"
    ;;
esac
TARGET="$ARCH-linux-musl"
curl -fL --retry 3 "https://github.com/musl-cc/musl.cc/releases/download/v0.0.1/$TOOLCHAIN.tgz" -o "$WORK/downloads/$TOOLCHAIN.tgz"
echo "$TOOLCHAIN_SHA  $WORK/downloads/$TOOLCHAIN.tgz" | sha256sum -c -
mkdir -p "$WORK/toolchain"
tar -xzf "$WORK/downloads/$TOOLCHAIN.tgz" -C "$WORK/toolchain" --strip-components=1
export PATH="$WORK/toolchain/bin:$PATH"
export CC="$TARGET-gcc" AR="$TARGET-ar" RANLIB="$TARGET-ranlib" STRIP="$TARGET-strip"
export CFLAGS="-Os -ffunction-sections -fdata-sections $ARCH_FLAGS"
export LDFLAGS="-static -Wl,--gc-sections"
BUILD_TRIPLET="$(gcc -dumpmachine)"

OPENSSL="$WORK/downloads/openssl-3.5.9.tar.gz"
curl -fL --retry 3 "https://github.com/openssl/openssl/releases/download/openssl-3.5.9/openssl-3.5.9.tar.gz" -o "$OPENSSL"
echo "603f5602e2eef00d77fbd429d34dcd5822bb301757a1bc9cdb24c670f1eb859a  $OPENSSL" | sha256sum -c -
tar -xzf "$OPENSSL" -C "$WORK/src"
(
  cd "$WORK/src/openssl-3.5.9"
  ./Configure "$OPENSSL_TARGET" no-shared no-tests no-apps no-docs no-dso no-engine no-async no-comp no-legacy no-module no-asm \
    --prefix=/usr/local --openssldir=/etc/ssl
  make -j2
  make install_sw DESTDIR="$WORK/openssl"
)
OPENSSL_PREFIX="$WORK/openssl/usr/local"

CURL="$WORK/downloads/curl-8.23.0.tar.xz"
curl -fL --retry 3 "https://github.com/curl/curl/releases/download/curl-8_23_0/curl-8.23.0.tar.xz" -o "$CURL"
echo "8dadd7d2536a314f982ad05a651b713f426bf7d02cc2c76cffb9796f2218e6c5  $CURL" | sha256sum -c -
tar -xJf "$CURL" -C "$WORK/src"

# Bundle Mozilla root CAs from curl.se and verify against its published digest.
CA_BUNDLE="$WORK/downloads/cacert.pem"
curl -fL --retry 3 https://curl.se/ca/cacert.pem -o "$CA_BUNDLE"
curl -fL --retry 3 https://curl.se/ca/cacert.pem.sha256 -o "$WORK/downloads/cacert.pem.sha256"
CA_SHA="$(awk '{print $1}' "$WORK/downloads/cacert.pem.sha256")"
case "$CA_SHA" in ????????*) ;; *) echo "Invalid CA bundle SHA-256 metadata" >&2; exit 1;; esac
[ "${#CA_SHA}" -eq 64 ] || { echo "Invalid CA bundle SHA-256 length" >&2; exit 1; }
echo "$CA_SHA  $CA_BUNDLE" | sha256sum -c -
mkdir -p "$WORK/build-curl"
(
  cd "$WORK/build-curl"
  export CPPFLAGS="-I$OPENSSL_PREFIX/include"
  export LIBS="-L$OPENSSL_PREFIX/lib -lssl -lcrypto"
  export LDFLAGS="-static -L$OPENSSL_PREFIX/lib -Wl,--gc-sections"
  "$WORK/src/curl-8.23.0/configure" --build="$BUILD_TRIPLET" --host="$TARGET" \
    --prefix=/usr/local --with-openssl="$OPENSSL_PREFIX" \
    --disable-shared --enable-static --disable-manual --disable-ldap --disable-ldaps \
    --disable-rtsp --disable-dict --disable-telnet --disable-tftp --disable-pop3 \
    --disable-imap --disable-smb --disable-smtp --disable-gopher --disable-mqtt \
    --disable-ipfs --disable-file --without-zlib --without-brotli --without-zstd \
    --without-libpsl --without-libidn2 --with-ca-bundle=/etc/ssl/certs/ca-certificates.crt
  make -j2
  make install DESTDIR="$WORK/stage"
)
BIN="$WORK/stage/usr/local/bin/curl"
test -x "$BIN"
"$STRIP" "$BIN"
"$TARGET-readelf" -h "$BIN" > "$WORK/elf-header.txt"
if "$TARGET-readelf" -l "$BIN" | grep -q 'INTERP'; then
  echo "curl unexpectedly requires a dynamic interpreter" >&2
  exit 1
fi
if [ "$ARCH" = i486 ]; then
  qemu-i386 -cpu 486 "$BIN" --version | tee "$WORK/curl-version.txt"
else
  "$BIN" --version | tee "$WORK/curl-version.txt"
fi
grep -q "OpenSSL/3.5.9" "$WORK/curl-version.txt"
mkdir -p "$WORK/stage/usr/local/share/doc/curl"
cat > "$WORK/stage/usr/local/share/doc/curl/VANTOR-BUILD" <<EOF
curl 8.23.0
OpenSSL 3.5.9 LTS
Target: $ARCH
Static musl build; HTTP and HTTPS protocols enabled
Mozilla CA bundle included at /etc/ssl/certs/ca-certificates.crt
EOF
tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner \
  -czf "$OUT/curl-8.23.0-$ARCH.tar.gz" -C "$WORK/stage" .
tar -tzf "$OUT/curl-8.23.0-$ARCH.tar.gz" >/dev/null
sha256sum "$OUT/curl-8.23.0-$ARCH.tar.gz"
echo "Built and smoke-tested curl with OpenSSL for $ARCH"
