#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
source build/config/vantor.conf

VERSION="0.64.1"
SOURCE_DIR="$ROOT/build/work/sources/openrc-$VERSION"
BUILD_DIR="$ROOT/build/work/openrc"
ROOTFS="${VANTOR_ROOTFS_DIR:-$ROOT/build/work/rootfs}"

for command in meson ninja pkg-config readelf; do
    command -v "$command" >/dev/null 2>&1 || {
        echo "[ERROR] Missing OpenRC host build dependency: $command" >&2
        exit 1
    }
done
pkg-config --exists 'libcap >= 2.33' || {
    echo "[ERROR] OpenRC requires libcap >= 2.33 development files." >&2
    exit 1
}
[[ -d "$ROOTFS" && -x "$ROOTFS/bin/busybox" ]] || {
    echo "[ERROR] Prepare the target rootfs and build BusyBox before OpenRC." >&2
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
export CFLAGS="-Os -static -fno-ident"
export LDFLAGS="-static"
meson setup "$BUILD_DIR" "$SOURCE_DIR" \
    --prefix=/usr --bindir=bin --sbindir=sbin --libdir=lib \
    --libexecdir=lib --sysconfdir=/etc --buildtype=release \
    -Ddefault_library=static -Dprefer_static=true \
    -Dbranding="VANTOR Linux" -Dnewnet=false -Dpam=false \
    -Daudit=disabled -Dselinux=disabled -Dsysvinit=false \
    -Dpkgconfig=false -Dbash-completions=false -Dzsh-completions=false \
    -Dshell=/bin/sh
meson compile -C "$BUILD_DIR" -j "$VANTOR_BUILD_JOBS"
DESTDIR="$ROOTFS" meson install -C "$BUILD_DIR"

for binary in openrc-init openrc openrc-run openrc-shutdown rc-service rc-update rc-status supervise-daemon start-stop-daemon checkpath; do
    path="$ROOTFS/sbin/$binary"
    [[ -x "$path" ]] || { echo "[ERROR] OpenRC did not install /sbin/$binary" >&2; exit 1; }
    if readelf -h "$path" >/dev/null 2>&1; then
        if readelf -l "$path" 2>/dev/null | grep -q 'INTERP'; then
            echo "[ERROR] OpenRC binary is dynamically linked: $path" >&2
            exit 1
        fi
    fi
done

install -d "$ROOTFS/etc/init.d" "$ROOTFS/etc/conf.d" "$ROOTFS/etc/runlevels/boot" "$ROOTFS/etc/runlevels/default"
install -m 0755 core/openrc/init.d/vantor-early "$ROOTFS/etc/init.d/vantor-early"
install -m 0755 core/openrc/init.d/vantor-modules "$ROOTFS/etc/init.d/vantor-modules"
install -m 0755 core/openrc/init.d/vantor-network "$ROOTFS/etc/init.d/vantor-network"
install -m 0755 core/openrc/init.d/vantor-console "$ROOTFS/etc/init.d/vantor-console"
install -m 0644 core/openrc/rc.conf "$ROOTFS/etc/rc.conf"
install -m 0644 core/openrc/conf.d/hostname "$ROOTFS/etc/conf.d/hostname"

# The upstream default runlevels include optional services that VANTOR does
# not ship yet. Keep only services whose required tools exist in this rootfs.
for service in fsck loopback swap sysctl hwclock keymaps mtab seedrng termencoding binfmt modules; do
    rm -f "$ROOTFS/etc/runlevels/boot/$service"
done
for service in cgroups; do
    [[ -e "$ROOTFS/etc/init.d/$service" ]] || rm -f "$ROOTFS/etc/runlevels/sysinit/$service"
done

link_service() {
    local runlevel="$1" service="$2"
    install -d "$ROOTFS/etc/runlevels/$runlevel"
    ln -sfn "../../init.d/$service" "$ROOTFS/etc/runlevels/$runlevel/$service"
}
link_service boot vantor-early
link_service boot vantor-modules
link_service default vantor-network
link_service default vantor-console.tty1
link_service default vantor-console.ttyS0
ln -sfn vantor-console "$ROOTFS/etc/init.d/vantor-console.tty1"
ln -sfn vantor-console "$ROOTFS/etc/init.d/vantor-console.ttyS0"

# OpenRC's own init becomes PID 1 after the VANTOR initramfs has mounted
# proc, sysfs, devtmpfs and /run and handed control to /sbin/init.
ln -sfn /sbin/openrc-init "$ROOTFS/sbin/init"
[[ "$(readlink "$ROOTFS/sbin/init")" == "/sbin/openrc-init" ]] || {
    echo "[ERROR] /sbin/init does not point to openrc-init." >&2
    exit 1
}
"$ROOTFS/sbin/openrc-init" --version >/dev/null 2>&1 || true
echo "[OK] OpenRC $VERSION installed into $ROOTFS."
echo "[OK] /sbin/init now resolves to the real OpenRC PID 1 implementation."
echo "[INFO] The ISO build will include this OpenRC-enabled rootfs in its initramfs."
