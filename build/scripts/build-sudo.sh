#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

VERSION="1.9.17p2"
ARCH="${VANTOR_SUDO_ARCH:-x86_64}"
SOURCE_DIR="$ROOT/build/work/sources/sudo-$VERSION"
ARCHIVE="$ROOT/build/distfiles/sudo-$VERSION.tar.gz"

case "$ARCH" in
    x86_64)
        BUILD_DIR="$ROOT/build/work/sudo"
        ROOTFS="${VANTOR_BUILD_ROOTFS_DIR:-$ROOT/build/work/rootfs}"
        export CFLAGS="-Os -static -fno-ident"
        export LDFLAGS="-static -Wl,-z,relro,-z,now"
        ;;
    i486)
        BUILD_DIR="$ROOT/build/work/sudo-legacy"
        ROOTFS="${VANTOR_BUILD_ROOTFS_DIR:-$ROOT/build/work/rootfs-legacy}"
        export CC="${CC_LEGACY:-gcc -m32 -march=i486 -mtune=i486}"
        export CFLAGS="-m32 -march=i486 -mtune=i486 -Os -static -fno-ident"
        export LDFLAGS="-m32 -static -Wl,-z,relro,-z,now"
        ;;
    *)
        echo "[ERROR] Unsupported sudo target architecture: $ARCH" >&2
        exit 2
        ;;
esac

for command in make readelf file fakeroot; do
    command -v "$command" >/dev/null 2>&1 || {
        echo "[ERROR] Missing sudo build dependency: $command" >&2
        exit 1
    }
done

[[ -d "$ROOTFS" && -x "$ROOTFS/bin/busybox" ]] || {
    echo "[ERROR] Prepare the $ARCH rootfs and build BusyBox before sudo." >&2
    exit 1
}
python3 tools/validate-sources.py --require-pinned --only sudo
python3 tools/fetch-sources.py --only sudo
if [[ ! -f "$SOURCE_DIR/configure" ]]; then
    [[ -s "$ARCHIVE" ]] || { echo "[ERROR] Sudo source archive is missing." >&2; exit 1; }
    python3 tools/extract-source.py "$ARCHIVE" "$SOURCE_DIR"
fi
[[ -x "$SOURCE_DIR/configure" ]] || {
    echo "[ERROR] Sudo source tree is incomplete." >&2
    exit 1
}

rm -rf -- "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
(
    cd "$BUILD_DIR"
    "$SOURCE_DIR/configure" \
        --prefix=/usr \
        --bindir=/usr/bin \
        --sbindir=/usr/bin \
        --libexecdir=/usr/libexec \
        --sysconfdir=/etc \
        --with-rundir=/run/sudo \
        --with-secure-path \
        --disable-pie \
        --disable-shared \
        --enable-static-sudoers \
        --disable-shared-libutil \
        --without-pam \
        --disable-openssl \
        --disable-nls
    make -j"${VANTOR_BUILD_JOBS:-2}"
    fakeroot -- make DESTDIR="$ROOTFS" install-binaries
)

SUDO="$ROOTFS/usr/bin/sudo"
VISUDO="$ROOTFS/usr/bin/visudo"
for binary in "$SUDO" "$VISUDO"; do
    [[ -x "$binary" ]] || {
        echo "[ERROR] Sudo build did not install $binary" >&2
        exit 1
    }
    if readelf -l "$binary" 2>/dev/null | grep -q 'INTERP'; then
        echo "[ERROR] Sudo binary is dynamically linked: $binary" >&2
        exit 1
    fi
    case "$ARCH" in
        x86_64)
            readelf -h "$binary" | grep -q 'Advanced Micro Devices X86-64' || {
                echo "[ERROR] Wrong ELF architecture: $binary" >&2; exit 1;
            }
            ;;
        i486)
            readelf -h "$binary" | grep -q 'Intel 80386' || {
                echo "[ERROR] Wrong ELF architecture: $binary" >&2; exit 1;
            }
            ;;
    esac
done

chmod 4755 "$SUDO"
chmod 0755 "$VISUDO"
install -d "$ROOTFS/run/sudo" "$ROOTFS/usr/share/vantor" "$ROOTFS/usr/share/licenses/sudo"
install -m 0644 "$SOURCE_DIR/LICENSE.md" "$ROOTFS/usr/share/licenses/sudo/LICENSE.md"
chmod 0700 "$ROOTFS/run/sudo"
printf '%s\n' "$VERSION" > "$ROOTFS/usr/share/vantor/sudo-version"

# Check policy syntax with the just-built parser; ownership is normalized to
# root in the fakeroot initramfs packaging step.
fakeroot -- sh -c '
    set -eu
    rootfs="$1"
    visudo="$2"
    chown -hR 0:0 "$rootfs"
    validation_file="$(mktemp)"
    trap "rm -f \"$validation_file\"" EXIT
    sed "s|^#includedir /etc/sudoers.d|#includedir $rootfs/etc/sudoers.d|" "$rootfs/etc/sudoers" > "$validation_file"
    chown 0:0 "$validation_file"
    chmod 0440 "$validation_file"
    "$visudo" -c -f "$validation_file"
' sh "$ROOTFS" "$VISUDO"
echo "[OK] Sudo $VERSION installed as static $ARCH binaries."
echo "[OK] sudo is mode 4755; fakeroot packaging will record root ownership."
