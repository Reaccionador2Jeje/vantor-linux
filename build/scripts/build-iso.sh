#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "\${BASH_SOURCE[0]}")/../.." && pwd)"
WORK="\${ROOT}/build/work"
STAGING="\${WORK}/iso-root"
KERNEL="\${WORK}/kernel/arch/x86/boot/bzImage"
INITRAMFS="\${WORK}/initramfs/vantor-initramfs.cpio.gz"
GRUB_CFG="\${ROOT}/boot/grub/grub.cfg"
OUTPUT="\${ROOT}/output/vantor-genesis-0.1.0-x86_64.iso"

fail() {
    printf '[ERROR] %s\n' "$*" >&2
    exit 1
}

for command in grub-mkrescue xorriso; do
    command -v "$command" >/dev/null 2>&1 || fail "Required host command not found: $command"
done

[[ -s "\${KERNEL}" ]] || fail "Kernel image missing: \${KERNEL}. Build the VANTOR kernel first."
[[ -s "\${INITRAMFS}" ]] || fail "Initramfs missing: \${INITRAMFS}. Build the VANTOR initramfs first."
[[ -s "\${GRUB_CFG}" ]] || fail "GRUB configuration missing: \${GRUB_CFG}"

rm -rf -- "\${STAGING}"
mkdir -p "\${STAGING}/boot/grub" "\${ROOT}/output"
install -m 0644 "\${KERNEL}" "\${STAGING}/boot/vantor-kernel"
install -m 0644 "\${INITRAMFS}" "\${STAGING}/boot/vantor-initramfs.cpio.gz"
install -m 0644 "\${GRUB_CFG}" "\${STAGING}/boot/grub/grub.cfg"

printf '[INFO] Creating GRUB ISO using available BIOS/UEFI platform modules.\n'
grub-mkrescue -o "\${OUTPUT}" "\${STAGING}"
[[ -s "\${OUTPUT}" ]] || fail "GRUB did not produce the ISO image."
printf '[OK] Created %s\n' "\${OUTPUT}"
printf '[INFO] Verify BIOS and UEFI boot in QEMU before calling this release bootable.\n'
