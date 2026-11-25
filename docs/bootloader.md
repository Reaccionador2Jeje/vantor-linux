# VANTOR Genesis bootloader

## Decision

The first VANTOR x86_64 bootloader is **GNU GRUB 2**. The bootloader is separate from the Linux kernel:

1. Firmware starts the machine (legacy BIOS or UEFI).
2. GRUB starts and displays the VANTOR menu.
3. GRUB loads the Linux kernel and initramfs into memory.
4. The kernel starts and unpacks the initramfs.
5. The initramfs runs VANTOR's \`/init\` entry point.

This first boot profile targets x86_64. Limbo PC Emulator is the manual Android test target; do not claim compatibility until a generated image has actually booted there.

## Menu

The maintained configuration is \`boot/grub/grub.cfg\`. It provides:

- **VANTOR Linux — Live Genesis:** normal Live boot.
- **VANTOR Linux — Live (Diagnostic mode):** verbose diagnostic boot.
- Reboot and power-off entries.

The x86_64 menu loads the native theme from `boot/grub/themes/vantor/theme.txt`. It uses the Deep Space navy background, cyan VANTOR title and selection, titanium menu text, and the **ONE SYSTEM. EVERY GENERATION.** slogan. The theme is bundled into the ISO by `build/scripts/build-iso.sh`; it does not fetch assets or fonts from the network.

The i486 Legacy menu intentionally stays in BIOS text mode, with the VANTOR palette and slogan, to avoid making older hardware depend on graphical GRUB support. When the installer prepares an x86_64 installed system, it copies the theme from the Live media if available. Legacy installed systems retain the text-mode menu.

## ISO layout

The ISO builder stages:

\`\`\`text
/boot/
├── vantor-kernel
├── vantor-initramfs.cpio.gz
└── grub/
    ├── grub.cfg
    └── themes/
        └── vantor/
            └── theme.txt
\`\`\`

GRUB's \`grub-mkrescue\` creates the ISO using BIOS and/or EFI platform modules installed on the build host. For both firmware paths, install the matching GRUB platform packages (commonly \`grub-pc-bin\` and \`grub-efi-amd64-bin\`) plus \`xorriso\`. Test both firmware modes; a GRUB menu alone does not prove both work.

## Build contract

The ISO builder expects:

- Kernel: \`build/work/kernel/arch/x86/boot/bzImage\`
- Initramfs: \`build/work/initramfs/vantor-initramfs.cpio.gz\`

When both exist and \`grub-mkrescue\` and \`xorriso\` are installed, run:

\`\`\`sh
make iso
\`\`\`

Output: \`output/vantor-genesis-0.1.0-x86_64.iso\`

The command deliberately fails instead of creating an incomplete image when the kernel or initramfs is absent. Those artifacts do not exist yet, so ISO creation is not available at this stage.

## Kernel handoff

The normal menu entry passes \`root=/dev/ram0\` and loads the initramfs. The initramfs must include required drivers and VANTOR's executable \`/init\`. The kernel build must enable initrd/initramfs support and x86_64 PC boot support. The exact command line and root-mount behavior will be verified during the first QEMU boot test.
