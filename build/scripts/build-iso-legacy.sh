#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WORK="$ROOT/build/work"
STAGING="$WORK/iso-root-legacy"
KERNEL="$WORK/kernel-legacy/arch/x86/boot/bzImage"
INITRAMFS="$WORK/initramfs-legacy/vantor-legacy-initramfs.cpio.gz"
GRUB_CFG="$ROOT/boot/grub/grub-legacy.cfg"
OUTPUT="$ROOT/output/vantor-minimal-0.1.0-i486.iso"

fail() {
    printf '[ERROR] %s\n' "$*" >&2
    exit 1
}

for command in grub-mkrescue xorriso; do
    command -v "$command" >/dev/null 2>&1 || fail "Required host command not found: $command"
done

[[ -s "$KERNEL" ]] || fail "Legacy kernel image missing: $KERNEL. Run 'make kernel-legacy' first."
[[ -s "$INITRAMFS" ]] || fail "Legacy initramfs missing: $INITRAMFS. Run 'make initramfs-legacy' first."
[[ -s "$GRUB_CFG" ]] || fail "Legacy GRUB configuration missing: $GRUB_CFG"

rm -rf -- "$STAGING"
mkdir -p "$STAGING/boot/grub" "$ROOT/output"
install -m 0644 "$KERNEL" "$STAGING/boot/vantor-legacy-kernel"
install -m 0644 "$INITRAMFS" "$STAGING/boot/vantor-legacy-initramfs.cpio.gz"
install -m 0644 "$GRUB_CFG" "$STAGING/boot/grub/grub.cfg"

printf '[INFO] Creating text-mode BIOS ISO for 486-class computers.\n'
grub-mkrescue -o "$OUTPUT" "$STAGING"
[[ -s "$OUTPUT" ]] || fail "GRUB did not produce the legacy ISO image."
printf '[OK] Created %s\n' "$OUTPUT"
printf '[INFO] BIOS and physical 486 boot testing are still required.\n'
