#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$ROOT"
source build/config/vantor.conf

VERSION="1.37.0"
SOURCE_DIR="$ROOT/build/work/sources/busybox-$VERSION"
BUILD_DIR="$ROOT/build/work/busybox-legacy"
ROOTFS="$ROOT/build/work/rootfs-legacy"
CC_LEGACY="gcc -m32 -march=i486 -mtune=i486"

python3 tools/validate-sources.py --require-pinned --only busybox
python3 tools/fetch-sources.py --only busybox
if [[ ! -f "$SOURCE_DIR/Makefile" ]]; then
    python3 tools/extract-source.py "$ROOT/build/distfiles/busybox-$VERSION.tar.bz2" "$SOURCE_DIR"
fi
mkdir -p "$BUILD_DIR" "$ROOTFS"
make -C "$SOURCE_DIR" O="$BUILD_DIR" defconfig

# Disable an optional applet that relies on removed legacy kernel CBQ headers.
if grep -q '^CONFIG_TC=y$' "$BUILD_DIR/.config"; then
    sed -i 's/^CONFIG_TC=y$/# CONFIG_TC is not set/' "$BUILD_DIR/.config"
fi

set_config() {
    local key="$1" value="$2"
    if grep -q "^# ${key} is not set$" "$BUILD_DIR/.config"; then
        sed -i "s/^# ${key} is not set$/${key}=${value}/" "$BUILD_DIR/.config"
    elif grep -q "^${key}=" "$BUILD_DIR/.config"; then
        sed -i "s/^${key}=.*/${key}=${value}/" "$BUILD_DIR/.config"
    else
        printf '%s=%s\n' "$key" "$value" >> "$BUILD_DIR/.config"
    fi
}

set_config CONFIG_STATIC y
set_config CONFIG_VI y
set_config CONFIG_ASH y
set_config CONFIG_SH_IS_ASH y
set_config CONFIG_INIT y
set_config CONFIG_FEATURE_USE_INITTAB y
set_config CONFIG_START_STOP_DAEMON y
set_config CONFIG_GETTY y
set_config CONFIG_SU y
set_config CONFIG_MDEV y
set_config CONFIG_UDHCPC y
set_config CONFIG_IP y
set_config CONFIG_MOUNT y
set_config CONFIG_UMOUNT y
set_config CONFIG_PASSWD y
set_config CONFIG_CHPASSWD y
set_config CONFIG_REBOOT y
set_config CONFIG_HALT y
set_config CONFIG_POWEROFF y
set_config CONFIG_FEATURE_SHADOWPASSWDS y
set_config CONFIG_SWITCH_ROOT y

make -C "$SOURCE_DIR" O="$BUILD_DIR" CC="$CC_LEGACY" oldconfig </dev/null
grep -q '^CONFIG_STATIC=y$' "$BUILD_DIR/.config"
grep -q '^CONFIG_VI=y$' "$BUILD_DIR/.config"
make -C "$SOURCE_DIR" O="$BUILD_DIR" CC="$CC_LEGACY" -j"$VANTOR_BUILD_JOBS"
make -C "$SOURCE_DIR" O="$BUILD_DIR" CC="$CC_LEGACY" CONFIG_PREFIX="$ROOTFS" install

[[ -x "$ROOTFS/bin/busybox" ]] || { echo "[ERROR] Legacy BusyBox binary is missing." >&2; exit 1; }
file "$ROOTFS/bin/busybox" | grep -q 'ELF 32-bit'
readelf -h "$ROOTFS/bin/busybox" | grep -q 'Intel 80386'
"$ROOTFS/bin/busybox" --list > "$BUILD_DIR/applets.txt"
for applet in init start-stop-daemon vi getty su mdev udhcpc ip mount umount passwd chpasswd reboot halt poweroff switch_root; do
    grep -qx "$applet" "$BUILD_DIR/applets.txt" || { echo "[ERROR] Legacy BusyBox applet missing: $applet" >&2; exit 1; }
done
echo "[OK] Static i486 BusyBox built and installed into build/work/rootfs-legacy."
