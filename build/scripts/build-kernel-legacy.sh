#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$ROOT"
source build/config/vantor.conf

VERSION="$VANTOR_LEGACY_KERNEL_VERSION"
SOURCE_NAME="linux-legacy"
SOURCE_DIR="$ROOT/build/work/sources/${SOURCE_NAME}-${VERSION}"
ARCHIVE="$ROOT/build/distfiles/linux-${VERSION}.tar.xz"
BUILD_DIR="$ROOT/build/work/kernel-legacy"
OUTPUT="$BUILD_DIR/arch/x86/boot/bzImage"

echo "[VANTOR] Validating the pinned legacy Linux source..."
python3 tools/validate-sources.py --require-pinned --only "$SOURCE_NAME"
python3 tools/fetch-sources.py --only "$SOURCE_NAME"

if [[ ! -f "$SOURCE_DIR/Makefile" ]]; then
    [[ -s "$ARCHIVE" ]] || { echo "[ERROR] Legacy kernel archive is missing." >&2; exit 1; }
    python3 tools/extract-source.py "$ARCHIVE" "$SOURCE_DIR"
fi
[[ -f "$SOURCE_DIR/Makefile" && -x "$SOURCE_DIR/scripts/config" ]] || {
    echo "[ERROR] Legacy kernel source tree is incomplete: $SOURCE_DIR" >&2
    exit 1
}

command -v gcc >/dev/null 2>&1 || { echo "[ERROR] gcc is required." >&2; exit 1; }
mkdir -p "$BUILD_DIR" "$ROOT/build/logs"
export ARCH=x86
export KBUILD_BUILD_USER=vantor
export KBUILD_BUILD_HOST=legacy-build
export KBUILD_BUILD_TIMESTAMP="1970-01-01 00:00:00 UTC"
export KBUILD_BUILD_VERSION=1

echo "[VANTOR] Configuring Linux ${VERSION} for 486SX/486DX-class PCs..."
make -C "$SOURCE_DIR" O="$BUILD_DIR" i386_defconfig
CONFIG="$BUILD_DIR/.config"

# Linux 6.1 retains the 486 CPU choices; the 6.18 baseline does not.
"$SOURCE_DIR/scripts/config" --file "$CONFIG" --disable M686
"$SOURCE_DIR/scripts/config" --file "$CONFIG" --disable M586
"$SOURCE_DIR/scripts/config" --file "$CONFIG" --enable M486SX
"$SOURCE_DIR/scripts/config" --file "$CONFIG" --enable MATH_EMULATION

enable=(
  BLK_DEV_INITRD BINFMT_ELF DEVTMPFS DEVTMPFS_MOUNT
  PROC_FS SYSFS TMPFS TTY VT VT_CONSOLE VGA_CONSOLE
  SERIAL_8250 SERIAL_8250_CONSOLE ISA EISA
  BLK_DEV_FD BLK_DEV_LOOP IDE IDE_GENERIC BLK_DEV_IDE BLK_DEV_IDECD
  BLK_DEV_IDEDISK ATA PATA_ISAPNP SCSI BLK_DEV_SD
  EXT2_FS EXT3_FS EXT4_FS ISO9660_FS JOLIET FAT_FS VFAT_FS MSDOS_FS
  BLK_DEV_SR CDROM MSDOS_PARTITION
  NET INET PACKET UNIX
  NE2000 8390 3C509 3C59X
  INPUT INPUT_EVDEV
)
for option in "${enable[@]}"; do
    "$SOURCE_DIR/scripts/config" --file "$CONFIG" --enable "$option"
done

"$SOURCE_DIR/scripts/config" --file "$CONFIG" --set-str LOCALVERSION "-vantor-legacy"
"$SOURCE_DIR/scripts/config" --file "$CONFIG" --disable LOCALVERSION_AUTO
make -C "$SOURCE_DIR" O="$BUILD_DIR" olddefconfig

grep -q '^CONFIG_M486SX=y$' "$CONFIG" || {
    echo "[ERROR] Linux did not retain the 486SX CPU profile." >&2
    exit 1
}
grep -q '^CONFIG_MATH_EMULATION=y$' "$CONFIG" || {
    echo "[ERROR] 486SX math emulation is not enabled." >&2
    exit 1
}

cp "$CONFIG" "$ROOT/kernel/configs/vantor-i486.config"
echo "[VANTOR] Building legacy bzImage..."
make -C "$SOURCE_DIR" O="$BUILD_DIR" -j"$VANTOR_BUILD_JOBS" bzImage 2>&1 | tee "$ROOT/build/logs/kernel-legacy-bzImage.log"

[[ -s "$OUTPUT" ]] || { echo "[ERROR] Legacy kernel build completed without bzImage." >&2; exit 1; }
install -D -m 0644 "$OUTPUT" "$BUILD_DIR/vantor-legacy-kernel"
echo "[OK] Legacy kernel built: build/work/kernel-legacy/vantor-legacy-kernel"
echo "[INFO] This kernel targets 486SX/486DX and later 32-bit x86 systems; hardware boot validation is still required."
