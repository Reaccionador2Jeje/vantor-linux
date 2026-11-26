#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$ROOT"
ROOTFS="${VANTOR_ROOTFS_DIR:-$ROOT/build/work/rootfs}"
OUTPUT_DIR="${VANTOR_INITRAMFS_DIR:-$ROOT/build/work/initramfs}"
OUTPUT_NAME="${VANTOR_INITRAMFS_NAME:-vantor-initramfs.cpio.gz}"
OUTPUT="$OUTPUT_DIR/$OUTPUT_NAME"

for command in cpio gzip fakeroot; do
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
# Absolute symlinks inside a target rootfs are interpreted relative to the
# future system root, not the build runner's /. Test the real payload directly
# and validate the init symlink text without dereferencing it on the host.
[[ -x "$ROOTFS/usr/sbin/openrc-init" && -L "$ROOTFS/sbin/openrc-init" && -L "$ROOTFS/sbin/init" ]] || {
    echo "[ERROR] Real OpenRC payload or /sbin entry points are missing. Run 'make openrc' before building the initramfs." >&2
    exit 1
}
[[ "$(readlink "$ROOTFS/sbin/openrc-init")" == "/usr/sbin/openrc-init" ]] || {
    echo "[ERROR] /sbin/openrc-init does not point to the installed /usr/sbin/openrc-init." >&2
    exit 1
}
[[ "$(readlink "$ROOTFS/sbin/init")" == "/sbin/openrc-init" ]] || {
    echo "[ERROR] Refusing to package an ISO whose /sbin/init is not OpenRC." >&2
    exit 1
}
[[ -x "$ROOTFS/usr/bin/sudo" && -x "$ROOTFS/usr/bin/visudo" ]] || {
    echo "[ERROR] Static sudo and visudo are missing. Run 'make sudo' first." >&2
    exit 1
}
[[ "$(stat -c '%a' "$ROOTFS/usr/bin/sudo")" == "4755" ]] || {
    echo "[ERROR] /usr/bin/sudo must have mode 4755 before packaging." >&2
    exit 1
}

# Include loadable modules from the matching kernel build when available.
KERNEL_RELEASE_FILE="${VANTOR_KERNEL_RELEASE_FILE:-$ROOT/build/work/kernel/kernelrelease}"
MODULES_ROOT="${VANTOR_MODULES_ROOT:-$ROOT/build/work/modules}/lib/modules"
if [[ "${VANTOR_SKIP_KERNEL_MODULES:-0}" == "1" ]]; then
    echo "[INFO] Loadable modules skipped for this image target; required legacy drivers are built into its kernel."
elif [[ -s "$KERNEL_RELEASE_FILE" ]]; then
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
# The build runner is not root. fakeroot records root ownership for system
# files and preserves sudo's setuid bit in the initramfs.
# Stable ordering and gzip -n keep the archive reproducible.
fakeroot -- sh -c '
    set -eu
    rootfs="$1"
    chown -hR 0:0 "$rootfs"
    chmod 4755 "$rootfs/usr/bin/sudo"
    cd "$rootfs"
    find . -print0 | sort -z | cpio --null --create --format=newc --quiet
' sh "$ROOTFS" | gzip -9n > "$OUTPUT"

[[ -s "$OUTPUT" ]] || { echo "[ERROR] Initramfs archive is empty." >&2; exit 1; }
gzip -t "$OUTPUT"
SUDO_METADATA="$(gzip -dc "$OUTPUT" | cpio --list --verbose 2>/dev/null | awk '$NF == "./usr/bin/sudo" { print $1 " " $3 " " $4; exit }')"
[[ "$SUDO_METADATA" == "-rwsr-xr-x root root" ]] || {
    echo "[ERROR] Initramfs sudo must be root-owned and setuid (4755); got: ${SUDO_METADATA:-missing}" >&2
    exit 1
}
echo "[OK] VANTOR initramfs created: $OUTPUT"
echo "[INFO] This archive is ready for kernel/GRUB integration; it has not yet been boot-tested."
