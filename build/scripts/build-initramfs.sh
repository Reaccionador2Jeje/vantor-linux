#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$ROOT"
ROOTFS="${VANTOR_ROOTFS_DIR:-$ROOT/build/work/rootfs}"
OUTPUT_DIR="${VANTOR_INITRAMFS_DIR:-$ROOT/build/work/initramfs}"
OUTPUT_NAME="${VANTOR_INITRAMFS_NAME:-vantor-initramfs.cpio.gz}"
OUTPUT="$OUTPUT_DIR/$OUTPUT_NAME"

for command in cpio gzip; do
    command -v "$command" >/dev/null 2>&1 || {
        echo "[ERROR] Required host command not found: $command" >&2
        exit 1
    }
done

[[ -x "$ROOTFS/bin/busybox" ]] || {
    echo "[ERROR] Static BusyBox is missing. Run 'make busybox' first." >&2
    exit 1
}
[[ -x "$ROOTFS/init" ]] || {
    echo "[ERROR] VANTOR /init is missing. Run 'make rootfs' first." >&2
    exit 1
}

# Include loadable modules from the matching kernel build when available.
KERNEL_RELEASE_FILE="$ROOT/build/work/kernel/kernelrelease"
MODULES_ROOT="$ROOT/build/work/modules/lib/modules"
if [[ -s "$KERNEL_RELEASE_FILE" ]]; then
    KERNEL_RELEASE="$(cat "$KERNEL_RELEASE_FILE")"
    [[ "$KERNEL_RELEASE" =~ ^[A-Za-z0-9._+-]+$ ]] || {
        echo "[ERROR] Invalid kernel release string: $KERNEL_RELEASE" >&2
        exit 1
    }
    MODULES_SOURCE="$MODULES_ROOT/$KERNEL_RELEASE"
    if [[ -d "$MODULES_SOURCE" ]]; then
        MODULES_DEST="$ROOTFS/lib/modules/$KERNEL_RELEASE"
        mkdir -p "$ROOTFS/lib/modules"
        rm -rf -- "$MODULES_DEST"
        cp -a "$MODULES_SOURCE" "$MODULES_DEST"
        if command -v depmod >/dev/null 2>&1; then
            depmod -b "$ROOTFS" "$KERNEL_RELEASE"
        fi
        echo "[OK] Matching kernel modules included: $KERNEL_RELEASE"
    else
        echo "[ERROR] Kernel release is recorded but modules are missing: $MODULES_SOURCE" >&2
        exit 1
    fi
else
    echo "[WARN] No kernel release metadata found; creating a modules-free bootstrap initramfs."
fi

mkdir -p "$OUTPUT_DIR"
(
    cd "$ROOTFS"
    # Stable ordering and gzip -n keep the archive reproducible.
    find . -print0 | sort -z | cpio --null --create --format=newc --quiet
) | gzip -9n > "$OUTPUT"

[[ -s "$OUTPUT" ]] || { echo "[ERROR] Initramfs archive is empty." >&2; exit 1; }
gzip -t "$OUTPUT"
echo "[OK] VANTOR initramfs created: $OUTPUT"
echo "[INFO] This archive is ready for kernel/GRUB integration; it has not yet been boot-tested."
