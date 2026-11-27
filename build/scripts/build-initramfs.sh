#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$ROOT"
ROOTFS="${VANTOR_ROOTFS_DIR:-$ROOT/build/work/rootfs}"
OUTPUT_DIR="${VANTOR_INITRAMFS_DIR:-$ROOT/build/work/initramfs}"
OUTPUT_NAME="${VANTOR_INITRAMFS_NAME:-vantor-initramfs.cpio.gz}"
OUTPUT="$OUTPUT_DIR/$OUTPUT_NAME"
for command in cpio gzip fakeroot; do
    command -v "$command" >/dev/null 2>&1 || { echo "[ERROR] Required host command not found: $command" >&2; exit 1; }
done
[[ -x "$ROOTFS/bin/busybox" ]] || { echo "[ERROR] Static BusyBox is missing. Run 'make busybox' first." >&2; exit 1; }
[[ -x "$ROOTFS/init" ]] || { echo "[ERROR] VANTOR /init is missing. Run 'make rootfs' first." >&2; exit 1; }
[[ -x "$ROOTFS/usr/sbin/openrc-init" && -L "$ROOTFS/sbin/openrc-init" && -L "$ROOTFS/sbin/init" ]] || { echo "[ERROR] OpenRC payload or /sbin entry points are missing. Run 'make openrc'." >&2; exit 1; }
[[ "$(readlink "$ROOTFS/sbin/openrc-init")" == "/usr/sbin/openrc-init" ]] || { echo "[ERROR] Invalid /sbin/openrc-init link." >&2; exit 1; }
[[ "$(readlink "$ROOTFS/sbin/init")" == "/sbin/openrc-init" ]] || { echo "[ERROR] /sbin/init is not OpenRC." >&2; exit 1; }
[[ -x "$ROOTFS/usr/bin/sudo" && -x "$ROOTFS/usr/bin/visudo" ]] || { echo "[ERROR] Static sudo/visudo missing. Run 'make sudo'." >&2; exit 1; }
[[ "$(stat -c '%a' "$ROOTFS/usr/bin/sudo")" == "4755" ]] || { echo "[ERROR] sudo must have mode 4755." >&2; exit 1; }

# Validate sudo policy before packaging.
for policy in "$ROOTFS/etc/sudoers" "$ROOTFS/etc/sudoers.d/00-root" "$ROOTFS/etc/sudoers.d/10-wheel" "$ROOTFS/etc/sudoers.d/99-live"; do
    [[ -s "$policy" ]] || { echo "[ERROR] Missing or empty sudo policy: $policy" >&2; exit 1; }
    [[ "$(stat -c '%a' "$policy")" == "440" ]] || { echo "[ERROR] Sudo policy must be mode 0440: $policy" >&2; exit 1; }
done
grep -qxF '#includedir /etc/sudoers.d' "$ROOTFS/etc/sudoers" || { echo "[ERROR] sudoers.d is not included." >&2; exit 1; }
grep -qxF 'root ALL=(ALL:ALL) ALL' "$ROOTFS/etc/sudoers.d/00-root" || { echo "[ERROR] Root sudo policy is incorrect." >&2; exit 1; }
grep -qxF 'live ALL=(ALL:ALL) ALL' "$ROOTFS/etc/sudoers.d/99-live" || { echo "[ERROR] Live sudo policy is incorrect." >&2; exit 1; }
grep -qxF '%wheel ALL=(ALL:ALL) ALL' "$ROOTFS/etc/sudoers.d/10-wheel" || { echo "[ERROR] Wheel sudo policy is incorrect." >&2; exit 1; }
[[ "$(awk -F: '$1 == "live" { print $3 ":" $4 }' "$ROOTFS/etc/passwd")" == "1000:1000" ]] || { echo "[ERROR] Invalid live account identity." >&2; exit 1; }
grep -qxF 'wheel:x:10:live' "$ROOTFS/etc/group" || { echo "[ERROR] Live account is not a member of wheel." >&2; exit 1; }

fakeroot -- sh -c '
    set -eu
    rootfs="$1"
    policy_check="$(mktemp)"
    trap '\''rm -f "$policy_check"'\'' EXIT
    chown -hR 0:0 "$rootfs/etc/sudoers" "$rootfs/etc/sudoers.d"
    sed "s|^#includedir /etc/sudoers.d|#includedir $rootfs/etc/sudoers.d|" "$rootfs/etc/sudoers" > "$policy_check"
    chown 0:0 "$policy_check"
    chmod 0440 "$policy_check"
    "$rootfs/usr/bin/visudo" -c -f "$policy_check"
' sh "$ROOTFS"

KERNEL_RELEASE_FILE="${VANTOR_KERNEL_RELEASE_FILE:-$ROOT/build/work/kernel/kernelrelease}"
MODULES_ROOT="${VANTOR_MODULES_ROOT:-$ROOT/build/work/modules}/lib/modules"
if [[ "${VANTOR_SKIP_KERNEL_MODULES:-0}" == "1" ]]; then
    echo "[INFO] Loadable modules skipped for this image target."
elif [[ -s "$KERNEL_RELEASE_FILE" ]]; then
    KERNEL_RELEASE="$(cat "$KERNEL_RELEASE_FILE")"
    [[ "$KERNEL_RELEASE" =~ ^[A-Za-z0-9._+-]+$ ]] || { echo "[ERROR] Invalid kernel release: $KERNEL_RELEASE" >&2; exit 1; }
    MODULES_SOURCE="$MODULES_ROOT/$KERNEL_RELEASE"
    if [[ -d "$MODULES_SOURCE" ]]; then
        MODULES_DEST="$ROOTFS/lib/modules/$KERNEL_RELEASE"
        mkdir -p "$ROOTFS/lib/modules"
        rm -rf -- "$MODULES_DEST"
        cp -a "$MODULES_SOURCE" "$MODULES_DEST"
        if command -v depmod >/dev/null 2>&1; then
            depmod -b "$ROOTFS" "$KERNEL_RELEASE"
        fi
        echo "[OK] Included kernel modules: $KERNEL_RELEASE"
    else
        echo "[ERROR] Kernel modules missing: $MODULES_SOURCE" >&2
        exit 1
    fi
else
    echo "[WARN] No kernel release metadata; creating bootstrap initramfs without modules."
fi
mkdir -p "$OUTPUT_DIR"
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
SUDO_METADATA="$(gzip -dc "$OUTPUT" | cpio --list --verbose 2>/dev/null | awk '$NF ~ /(^|\/)usr\/bin\/sudo$/ { print $1 " " $3 " " $4; exit }')"
[[ "$SUDO_METADATA" == "-rwsr-xr-x root root" ]] || { echo "[ERROR] sudo metadata invalid: ${SUDO_METADATA:-missing}" >&2; exit 1; }
echo "[OK] VANTOR initramfs created: $OUTPUT"
echo "[INFO] Boot compatibility still requires QEMU/Limbo testing."
