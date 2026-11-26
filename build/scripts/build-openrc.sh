#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
source build/config/vantor.conf

VERSION="0.64.1"
ARCH="${VANTOR_OPENRC_ARCH:-x86_64}"
SOURCE_DIR="$ROOT/build/work/sources/openrc-$VERSION"
case "$ARCH" in
    x86_64)
        BUILD_DIR="$ROOT/build/work/openrc"
        ROOTFS="${VANTOR_ROOTFS_DIR:-$ROOT/build/work/rootfs}"
        export CFLAGS="-Os -static -fno-ident"
        export LDFLAGS="-static"
        export PKG_CONFIG_LIBDIR="/usr/lib/x86_64-linux-gnu/pkgconfig:/usr/share/pkgconfig"
        CROSS_ARGS=()
        ;;
    i486)
        BUILD_DIR="$ROOT/build/work/openrc-legacy"
        ROOTFS="${VANTOR_ROOTFS_DIR:-$ROOT/build/work/rootfs-legacy}"
        export CFLAGS="-m32 -march=i486 -mtune=i486 -Os -static -fno-ident"
        export LDFLAGS="-m32 -static"
        export PKG_CONFIG_LIBDIR="/usr/lib/i386-linux-gnu/pkgconfig:/usr/share/pkgconfig"
        CROSS_FILE="$ROOT/build/work/openrc-i486.ini"
        mkdir -p "$(dirname "$CROSS_FILE")"
        cat > "$CROSS_FILE" <<'CROSS'
[binaries]
c = ['gcc', '-m32', '-march=i486', '-mtune=i486']
pkgconfig = 'pkg-config'
strip = 'strip'

[host_machine]
system = 'linux'
cpu_family = 'x86'
cpu = 'i486'
endian = 'little'

[properties]
needs_exe_wrapper = true
CROSS
        CROSS_ARGS=(--cross-file "$CROSS_FILE")
        ;;
    *)
        echo "[ERROR] Unsupported OpenRC target architecture: $ARCH" >&2
        exit 2
        ;;
esac

for command in meson ninja pkg-config readelf; do
    command -v "$command" >/dev/null 2>&1 || {
        echo "[ERROR] Missing OpenRC build dependency: $command" >&2
        exit 1
    }
done
pkg-config --exists 'libcap >= 2.33' || {
    echo "[ERROR] OpenRC requires target libcap >= 2.33 development files." >&2
    exit 1
}
[[ -d "$ROOTFS" && -x "$ROOTFS/bin/busybox" ]] || {
    echo "[ERROR] Prepare the $ARCH rootfs and build BusyBox before OpenRC." >&2
    exit 1
}

python3 tools/validate-sources.py --require-pinned --only openrc
python3 tools/fetch-sources.py --only openrc
if [[ ! -f "$SOURCE_DIR/meson.build" ]]; then
    python3 tools/extract-source.py "$ROOT/build/distfiles/openrc-$VERSION.tar.gz" "$SOURCE_DIR"
fi
[[ -f "$SOURCE_DIR/meson.build" && -f "$SOURCE_DIR/meson_options.txt" ]] || {
    echo "[ERROR] OpenRC source tree is incomplete." >&2
    exit 1
}

rm -rf -- "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
meson setup "$BUILD_DIR" "$SOURCE_DIR" "${CROSS_ARGS[@]}" \
    --prefix=/usr --bindir=bin --sbindir=sbin --libdir=lib \
    --libexecdir=lib --sysconfdir=/etc --buildtype=release \
    -Ddefault_library=static -Dprefer_static=true \
    -Dbranding='"VANTOR Linux"' -Dnewnet=false -Dpam=false \
    -Daudit=disabled -Dselinux=disabled -Dsysvinit=false \
    -Dpkgconfig=false -Dbash-completions=false -Dzsh-completions=false \
    -Dshell=/bin/sh
meson compile -C "$BUILD_DIR" -j "$VANTOR_BUILD_JOBS"
DESTDIR="$ROOTFS" meson install -C "$BUILD_DIR"

for binary in openrc-init openrc openrc-run openrc-shutdown rc-service rc-update rc-status supervise-daemon start-stop-daemon checkpath; do
    path="$ROOTFS/sbin/$binary"
    [[ -x "$path" ]] || { echo "[ERROR] OpenRC did not install /sbin/$binary" >&2; exit 1; }
    if readelf -h "$path" >/dev/null 2>&1; then
        readelf -l "$path" 2>/dev/null | grep -q 'INTERP' && {
            echo "[ERROR] OpenRC binary is dynamically linked: $path" >&2
            exit 1
        }
        case "$ARCH" in
            x86_64) readelf -h "$path" | grep -q 'Advanced Micro Devices X86-64' || { echo "[ERROR] Wrong ELF machine: $path" >&2; exit 1; } ;;
            i486) readelf -h "$path" | grep -q 'Intel 80386' || { echo "[ERROR] Wrong ELF machine: $path" >&2; exit 1; } ;;
        esac
    fi
done

install -d "$ROOTFS/etc/init.d" "$ROOTFS/etc/conf.d" "$ROOTFS/etc/runlevels/boot" "$ROOTFS/etc/runlevels/default"
install -m 0755 core/openrc/init.d/vantor-early "$ROOTFS/etc/init.d/vantor-early"
install -m 0755 core/openrc/init.d/vantor-modules "$ROOTFS/etc/init.d/vantor-modules"
install -m 0755 core/openrc/init.d/vantor-network "$ROOTFS/etc/init.d/vantor-network"
install -m 0755 core/openrc/init.d/vantor-console "$ROOTFS/etc/init.d/vantor-console"
install -m 0644 core/openrc/rc.conf "$ROOTFS/etc/rc.conf"
install -m 0644 core/openrc/conf.d/hostname "$ROOTFS/etc/conf.d/hostname"

# VANTOR keeps the upstream core runlevels and removes optional services
# whose supporting utilities are not shipped in the minimal image.
for service in fsck loopback swap sysctl hwclock keymaps mtab seedrng termencoding binfmt modules; do
    rm -f "$ROOTFS/etc/runlevels/boot/$service"
done
link_service() {
    local runlevel="$1" service="$2"
    install -d "$ROOTFS/etc/runlevels/$runlevel"
    ln -sfn "../../init.d/$service" "$ROOTFS/etc/runlevels/$runlevel/$service"
}
link_service boot vantor-early
link_service boot vantor-modules
# Mount local filesystems only in the normal default runlevel. Recovery keeps
# consoles but deliberately skips localmount and network startup.
rm -f "$ROOTFS/etc/runlevels/boot/localmount"
link_service default localmount
link_service default vantor-network
link_service default vantor-console.tty1
link_service default vantor-console.ttyS0
link_service nonetwork vantor-console.tty1
link_service nonetwork vantor-console.ttyS0
ln -sfn vantor-console "$ROOTFS/etc/init.d/vantor-console.tty1"
ln -sfn vantor-console "$ROOTFS/etc/init.d/vantor-console.ttyS0"

ln -sfn /sbin/openrc-init "$ROOTFS/sbin/init"
[[ "$(readlink "$ROOTFS/sbin/init")" == "/sbin/openrc-init" ]] || {
    echo "[ERROR] /sbin/init does not point to openrc-init." >&2
    exit 1
}
echo "[OK] OpenRC $VERSION installed as static $ARCH binaries into $ROOTFS."
echo "[OK] /sbin/init now resolves to the real OpenRC PID 1 implementation."
