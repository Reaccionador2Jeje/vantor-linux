#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$ROOT"
source build/config/vantor.conf

VERSION="1.37.0"
SOURCE_DIR="$ROOT/build/work/sources/busybox-$VERSION"
BUILD_DIR="$ROOT/build/work/busybox"
ROOTFS="$ROOT/build/work/rootfs"

echo "[VANTOR] Checking the verified BusyBox source pin..."
python3 tools/validate-sources.py --require-pinned --only busybox
python3 tools/fetch-sources.py --only busybox

if [[ ! -f "$SOURCE_DIR/Makefile" ]]; then
    ARCHIVE="$ROOT/build/distfiles/busybox-$VERSION.tar.bz2"
    [[ -s "$ARCHIVE" ]] || { echo "[ERROR] BusyBox source archive is missing." >&2; exit 1; }
    python3 tools/extract-source.py "$ARCHIVE" "$SOURCE_DIR"
fi

[[ -f "$SOURCE_DIR/Makefile" ]] || { echo "[ERROR] BusyBox source tree is incomplete." >&2; exit 1; }
mkdir -p "$BUILD_DIR" "$ROOTFS"
make -C "$SOURCE_DIR" O="$BUILD_DIR" defconfig

# Keep the bootstrap independent from optional traffic-control headers.
if grep -q '^CONFIG_TC=y$' "$BUILD_DIR/.config"; then
    sed -i 's/^CONFIG_TC=y$/# CONFIG_TC is not set/' "$BUILD_DIR/.config"
fi

# Build a self-contained multicall binary and include the vi applet.
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
set_config CONFIG_FEATURE_PREFER_APPLETS y
for applet in CONFIG_GETTY CONFIG_SU CONFIG_MDEV CONFIG_UDHCPC CONFIG_MOUNT CONFIG_UMOUNT CONFIG_PASSWD CONFIG_CHPASSWD CONFIG_REBOOT CONFIG_HALT CONFIG_POWEROFF CONFIG_DF CONFIG_FREE CONFIG_PS CONFIG_DMESG; do
    set_config "$applet" y
done
set_config CONFIG_FEATURE_SHADOWPASSWDS y

make -C "$SOURCE_DIR" O="$BUILD_DIR" oldconfig </dev/null
grep -q '^CONFIG_STATIC=y$' "$BUILD_DIR/.config" || { echo "[ERROR] BusyBox static mode was not selected." >&2; exit 1; }
grep -q '^CONFIG_VI=y$' "$BUILD_DIR/.config" || { echo "[ERROR] BusyBox vi applet was not selected." >&2; exit 1; }

make -C "$SOURCE_DIR" O="$BUILD_DIR" -j"$VANTOR_BUILD_JOBS"
make -C "$SOURCE_DIR" O="$BUILD_DIR" CONFIG_PREFIX="$ROOTFS" install

[[ -x "$ROOTFS/bin/busybox" ]] || { echo "[ERROR] BusyBox install did not produce /bin/busybox." >&2; exit 1; }
"$ROOTFS/bin/busybox" --list > "$BUILD_DIR/applets.txt"
for applet in vi getty su mdev udhcpc mount umount passwd chpasswd reboot halt poweroff df free ps dmesg; do
    grep -qx "$applet" "$BUILD_DIR/applets.txt" || { echo "[ERROR] BusyBox applet is missing: $applet" >&2; exit 1; }
done
echo "[OK] Static BusyBox installed into build/work/rootfs."
echo "[OK] Shell, vi, Live login, DHCP, device discovery and core tools are enabled."
echo "[INFO] The VANTOR initramfs can now be assembled with: make initramfs"
