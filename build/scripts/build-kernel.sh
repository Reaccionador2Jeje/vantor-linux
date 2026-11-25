#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "\${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
source build/config/vantor.conf

: "\${VANTOR_KERNEL_VERSION:?missing VANTOR_KERNEL_VERSION}"
: "\${VANTOR_BUILD_JOBS:?missing VANTOR_BUILD_JOBS}"

ARCH=x86
SOURCE_DIR="$ROOT/build/work/sources/linux-\${VANTOR_KERNEL_VERSION}"
ARCHIVE="$ROOT/build/distfiles/linux-\${VANTOR_KERNEL_VERSION}.tar.xz"
BUILD_DIR="$ROOT/build/work/kernel"
OUTPUT="$BUILD_DIR/arch/x86/boot/bzImage"

echo "[VANTOR] Validating the pinned Linux source..."
python3 tools/validate-sources.py --require-pinned --only linux
python3 tools/fetch-sources.py --only linux

if [[ ! -f "$SOURCE_DIR/Makefile" ]]; then
    [[ -s "$ARCHIVE" ]] || { echo "[ERROR] Linux source archive is missing." >&2; exit 1; }
    python3 tools/extract-source.py "$ARCHIVE" "$SOURCE_DIR"
fi

[[ -f "$SOURCE_DIR/Makefile" && -x "$SOURCE_DIR/scripts/config" ]] || {
    echo "[ERROR] Linux source tree is incomplete: $SOURCE_DIR" >&2
    exit 1
}

mkdir -p "$BUILD_DIR" "$ROOT/build/logs"
export ARCH
export KBUILD_BUILD_USER=vantor
export KBUILD_BUILD_HOST=build
export KBUILD_BUILD_TIMESTAMP="1970-01-01 00:00:00 UTC"
export KBUILD_BUILD_VERSION=1

echo "[VANTOR] Creating the x86_64 baseline configuration..."
make -C "$SOURCE_DIR" O="$BUILD_DIR" x86_64_defconfig

CONFIG="$BUILD_DIR/.config"
enable=(
  BLK_DEV_INITRD
  BINFMT_ELF
  DEVTMPFS
  DEVTMPFS_MOUNT
  PROC_FS
  SYSFS
  TMPFS
  TTY
  VT
  VT_CONSOLE
  SERIAL_8250
  SERIAL_8250_CONSOLE
  VGA_CONSOLE
  FRAMEBUFFER_CONSOLE
  PCI
  PCI_MSI
  VIRTIO
  VIRTIO_PCI
  VIRTIO_BLK
  VIRTIO_NET
  VIRTIO_CONSOLE
  SCSI
  BLK_DEV_SD
  SCSI_VIRTIO
  ATA
  ATA_PIIX
  E1000
  E1000E
  EXT4_FS
  ISO9660_FS
  FAT
  MSDOS_PARTITION
  EFI_PARTITION
  NET
  INET
  PACKET
  UNIX
  INPUT
  INPUT_EVDEV
  USB
  USB_XHCI_HCD
  USB_EHCI_HCD
  USB_OHCI_HCD
  USB_STORAGE
)
for option in "\${enable[@]}"; do
    "$SOURCE_DIR/scripts/config" --file "$CONFIG" --enable "$option"
done

"$SOURCE_DIR/scripts/config" --file "$CONFIG" --set-str LOCALVERSION "-vantor"
"$SOURCE_DIR/scripts/config" --file "$CONFIG" --disable LOCALVERSION_AUTO

make -C "$SOURCE_DIR" O="$BUILD_DIR" olddefconfig
cp "$CONFIG" "$ROOT/kernel/configs/vantor-x86_64.config"

echo "[VANTOR] Building bzImage..."
make -C "$SOURCE_DIR" O="$BUILD_DIR" -j"$VANTOR_BUILD_JOBS" bzImage 2>&1 | tee "$ROOT/build/logs/kernel-bzImage.log"

[[ -s "$OUTPUT" ]] || { echo "[ERROR] Kernel build completed without bzImage." >&2; exit 1; }
install -D -m 0644 "$OUTPUT" "$ROOT/build/work/kernel/vantor-kernel"
echo "[OK] VANTOR kernel built: build/work/kernel/vantor-kernel"
echo "[INFO] Modules and initramfs assembly are separate next steps."
