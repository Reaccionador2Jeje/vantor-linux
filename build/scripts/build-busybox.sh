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

# Build a self-contained static BusyBox so the first userspace does not depend
# on a not-yet-built VANTOR C library or dynamic loader.
if grep -q '^# CONFIG_STATIC is not set$' "$BUILD_DIR/.config"; then
    sed -i 's/^# CONFIG_STATIC is not set$/CONFIG_STATIC=y/' "$BUILD_DIR/.config"
elif grep -q '^CONFIG_STATIC=' "$BUILD_DIR/.config"; then
    sed -i 's/^CONFIG_STATIC=.*/CONFIG_STATIC=y/' "$BUILD_DIR/.config"
else
    printf '\nCONFIG_STATIC=y\n' >> "$BUILD_DIR/.config"
fi
make -C "$SOURCE_DIR" O="$BUILD_DIR" oldconfig </dev/null
make -C "$SOURCE_DIR" O="$BUILD_DIR" -j"$VANTOR_BUILD_JOBS"
make -C "$SOURCE_DIR" O="$BUILD_DIR" CONFIG_PREFIX="$ROOTFS" install

[[ -x "$ROOTFS/bin/busybox" ]] || { echo "[ERROR] BusyBox install did not produce /bin/busybox." >&2; exit 1; }
"$ROOTFS/bin/busybox" --list > "$BUILD_DIR/applets.txt"
echo "[OK] Static BusyBox installed into build/work/rootfs."
echo "[INFO] The VANTOR initramfs can now be assembled with: make initramfs"
