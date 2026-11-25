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
