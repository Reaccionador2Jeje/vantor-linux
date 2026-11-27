# VANTOR hardware compatibility

VANTOR Minimal is designed as a small console-first system. Hardware support is split into explicit profiles so a modern kernel is not accidentally shipped to machines it cannot run on.

## Supported development targets

| Profile | CPU baseline | Kernel line | State |
|---|---|---|---|
| Minimal x86_64 | AMD64 / Intel 64 | Linux 6.18.y | Main profile; build source still awaits a verified pin |
| Minimal Legacy i486 | 486SX / 486DX and newer IA-32 | Linux 6.1.y | Kernel and separate static i486 BusyBox build pipelines added; compilation and physical boot validation pending |
| 386 / 286 / 8086 | 80386 and earlier | Not supported by the selected modern kernel | Out of scope for this Linux build |

Linux 6.18 no longer offers 486 CPU support. VANTOR therefore uses the maintained 6.1.y source line for the 486 profile. The Linux 6.1.193 kernel.org checksum is pinned in build/sources/sources.json; the build is still subject to CI and hardware testing.

The 386 is not supported by current Linux kernels, and a 286/8086 cannot run a normal 32-bit Linux kernel. VANTOR does not claim these machines can boot this edition. Supporting them would require a separate historical kernel and userspace branch, not a compile-time switch.

## 486 profile

The legacy kernel configuration targets the 486SX CPU choice and enables math emulation for machines without an integrated FPU. It also enables a conservative set of legacy PC interfaces:
- ISA and EISA buses
- floppy and legacy IDE storage
- serial console and VGA text console
- NE2000 and 3Com 3c509 network adapters
- ext2/ext4, ISO9660 and FAT filesystems

The legacy kernel build is:

    make kernel-legacy

It produces build/work/kernel-legacy/vantor-legacy-kernel and the resolved configuration at kernel/configs/vantor-i486.config.

The complete image pipeline is:

    make image-legacy

This builds the i486 rootfs, static BusyBox, initramfs, legacy kernel and a text-mode BIOS ISO at output/vantor-minimal-0.1.0-i486.iso. GitHub Actions also has a full image workflow that uploads the ISO as a temporary build artifact. The image is not considered bootable until it has been tested in Limbo and on physical 486 hardware.

## Practical hardware expectations

The kernel's CPU floor is not the same as a usable system requirement. Real machines vary widely in RAM, storage, BIOS behavior and peripheral support. A 486 may boot a small console kernel but still lack enough memory or supported storage to run a full package installation comfortably. The first legacy release should therefore be treated as a low-resource console experiment, not a desktop distribution.

No physical 486 machine or Limbo legacy VM has been boot-tested yet. A successful kernel compilation is not proof of boot compatibility.


## ThinkPad Edge E430 target profile

The primary physical validation target for VANTOR Genesis is the Lenovo ThinkPad Edge E430 with an Intel Core i5-2520M. The x86_64 kernel configuration explicitly enables common laptop paths: Intel integrated graphics (i915), SATA/AHCI storage, Intel HD Audio with Realtek and HDMI codecs, Intel wireless (iwlwifi/iwlmvm), Intel wired Ethernet (e1000e), ACPI battery and thermal interfaces, backlight controls, USB host controllers and USB storage.

Enabling a driver does not guarantee that a wireless adapter works without its matching firmware. Firmware packaging, Wi-Fi association, suspend/resume, brightness keys, audio output and the exact E430 wireless-card variant still require physical checks. Ethernet is the preferred first-install network fallback. The E430 is an x86_64 target and must use Genesis, not the i486 Legacy image. Physical support is not validated until the machine boots from its own disk and storage, keyboard, display, network and power-management checks pass.
