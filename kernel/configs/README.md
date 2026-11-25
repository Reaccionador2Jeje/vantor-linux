# VANTOR kernel configuration

The first configuration is generated from upstream \`x86_64_defconfig\` and then enables the drivers needed for a small QEMU/Limbo PC:

- initramfs and early userspace support
- devtmpfs, procfs, sysfs and tmpfs
- VGA/VT and 8250 serial console
- PCI and VirtIO PCI, block, network and console
- common emulated PC storage and network devices
- ext4, ISO9660 and basic FAT partition support
- USB host controllers and USB storage

The build script writes the resolved configuration to \`kernel/configs/vantor-x86_64.config\` after \`olddefconfig\`. That generated file is the exact configuration used for that kernel source version.

The first target is a QEMU-compatible virtual PC. Hardware drivers for physical laptops, Wi-Fi chipsets, GPUs and ARM devices are not implied by this baseline.
