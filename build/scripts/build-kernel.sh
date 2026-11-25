#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$ROOT"
source build/config/vantor.conf

: "${VANTOR_KERNEL_VERSION}"
: "${VANTOR_BUILD_JOBS}"

ARCH=x86
SOURCE_DIR="$ROOT/build/work/sources/linux-$VANTOR_KERNEL_VERSION"
ARCHIVE="$ROOT/build/distfiles/linux-$VANTOR_KERNEL_VERSION.tar.xz"
BUILD_DIR="$ROOT/build/work/kernel"
OUTPUT="$BUILD_DIR/arch/x86/boot/bzImage"
MODULES_DIR="$ROOT/build/work/modules"

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

mkdir -p "$BUILD_DIR" "$ROOT/build/logs" "$ROOT/build/work/kernel"
export ARCH
export KBUILD_BUILD_USER=vantor
export KBUILD_BUILD_HOST=build
export KBUILD_BUILD_TIMESTAMP="1970-01-01 00:00:00 UTC"
export KBUILD_BUILD_VERSION=1

echo "[VANTOR] Creating the x86_64 baseline configuration..."
make -C "$SOURCE_DIR" O="$BUILD_DIR" x86_64_defconfig

CONFIG="$BUILD_DIR/.config"
enable=(
  BLK_DEV_INITRD BINFMT_ELF DEVTMPFS DEVTMPFS_MOUNT
  PROC_FS SYSFS TMPFS TTY VT VT_CONSOLE
  SERIAL_8250 SERIAL_8250_CONSOLE VGA_CONSOLE FRAMEBUFFER_CONSOLE
  FB FB_VESA FB_EFI DRM DRM_BOCHS DRM_VIRTIO_GPU DRM_SIMPLEDRM DRM_FBDEV_EMULATION
  PCI PCI_MSI VIRTIO VIRTIO_PCI VIRTIO_BLK VIRTIO_NET VIRTIO_CONSOLE
  SCSI BLK_DEV_SD BLK_DEV_SR CDROM SCSI_VIRTIO ATA ATA_PIIX SATA_AHCI E1000 E1000E
  EXT2_FS EXT4_FS ISO9660_FS JOLIET FAT_FS VFAT_FS MSDOS_FS NLS_CODEPAGE_437 NLS_ISO8859_1
  MSDOS_PARTITION EFI_PARTITION
  NET INET PACKET UNIX INPUT INPUT_EVDEV
  USB USB_XHCI_HCD USB_EHCI_HCD USB_OHCI_HCD USB_STORAGE
)
for option in "${enable[@]}"; do
    "$SOURCE_DIR/scripts/config" --file "$CONFIG" --enable "$option"
done

"$SOURCE_DIR/scripts/config" --file "$CONFIG" --set-str LOCALVERSION "-vantor"
"$SOURCE_DIR/scripts/config" --file "$CONFIG" --disable LOCALVERSION_AUTO

make -C "$SOURCE_DIR" O="$BUILD_DIR" olddefconfig
cp "$CONFIG" "$ROOT/kernel/configs/vantor-x86_64.config"

echo "[VANTOR] Building bzImage and loadable modules with $VANTOR_BUILD_JOBS jobs..."
compiler_args=()
if command -v ccache >/dev/null 2>&1; then
    compiler_args+=(CC="ccache gcc" HOSTCC="ccache gcc")
    echo "[VANTOR] ccache enabled for incremental compiler reuse."
fi
make -C "$SOURCE_DIR" O="$BUILD_DIR" -j"$VANTOR_BUILD_JOBS" "${compiler_args[@]}" bzImage modules 2>&1 | tee "$ROOT/build/logs/kernel-build.log"
if command -v ccache >/dev/null 2>&1; then
    ccache --show-stats
fi

[[ -s "$OUTPUT" ]] || { echo "[ERROR] Kernel build completed without bzImage." >&2; exit 1; }
install -D -m 0644 "$OUTPUT" "$ROOT/build/work/kernel/vantor-kernel"

echo "[VANTOR] Installing modules into isolated staging tree..."
rm -rf -- "$MODULES_DIR"
mkdir -p "$MODULES_DIR"
make -C "$SOURCE_DIR" O="$BUILD_DIR" \
    INSTALL_MOD_PATH="$MODULES_DIR" INSTALL_MOD_STRIP=1 modules_install

KERNEL_RELEASE="$(make --no-print-directory -s -C "$SOURCE_DIR" O="$BUILD_DIR" kernelrelease | tail -n 1 | tr -d '\r')"
[[ "$KERNEL_RELEASE" =~ ^[A-Za-z0-9._+-]+$ ]] || {
    echo "[ERROR] Invalid kernel release string: $KERNEL_RELEASE" >&2
    exit 1
}
MODULES_RELEASE_DIR="$MODULES_DIR/lib/modules/$KERNEL_RELEASE"
[[ -d "$MODULES_RELEASE_DIR" ]] || {
    echo "[ERROR] Module installation did not create $MODULES_RELEASE_DIR" >&2
    exit 1
}
if command -v depmod >/dev/null 2>&1; then
    depmod -b "$MODULES_DIR" "$KERNEL_RELEASE"
else
    echo "[WARN] depmod unavailable; target system must regenerate module dependencies."
fi
printf '%s\n' "$KERNEL_RELEASE" > "$ROOT/build/work/kernel/kernelrelease"

echo "[OK] VANTOR kernel built: build/work/kernel/vantor-kernel"
echo "[OK] VANTOR modules staged for $KERNEL_RELEASE"
