# VANTOR testing with Limbo on Android

VANTOR's Android virtual-machine test target is **Limbo PC Emulator**. Do not use QORVEX as a test dependency or as the runtime for this project.

Limbo is QEMU-based and can emulate x86 and x86_64 guest machines. User networking provides NAT in supported configurations; TAP generally requires additional host support. Actual limits vary by Limbo build and Android device.

## First VANTOR boot profile

Use this profile after the project produces a bootable BIOS-compatible ISO:

| Setting | VANTOR test value |
|---|---|
| Architecture | x86_64 |
| Machine | PC / i440fx-compatible, if selectable |
| CPU model | qemu64 or closest available generic x86_64 model |
| RAM | 512 MB initially; increase to 1024 MB if stable |
| Display | Standard VGA |
| Boot device | CD-ROM with the VANTOR ISO |
| Disk | Optional virtual disk for later installation tests |
| Network | User-mode networking (NAT) |

## Bootloader test sequence

1. Create a new x86_64 virtual machine in Limbo.
2. Attach the VANTOR ISO as its CD-ROM.
3. Start with 512 MB RAM and standard VGA.
4. Confirm the GRUB menu appears.
5. Select **VANTOR Linux — Genesis**.
6. Confirm the kernel starts, initramfs unpacks, and VANTOR init reaches a shell.
7. Record the last visible console output if startup fails.

The initial test target is legacy BIOS boot. UEFI testing is a separate validation step and should only be marked supported after it succeeds.

## VANTOR Core validation checklist

After the ISO has been produced by GitHub Actions, use the following checks from the Live console:

| Area | Command or observation | Expected result |
|---|---|---|
| PID 1 | `vantorctl status` | Init PID reports BusyBox init |
| Hardware | `vantorctl hardware` | CPU, memory, block, PCI, VirtIO, USB and NIC inventory; unavailable buses are reported clearly |
| Storage | `vantorctl storage scan` | Detected virtual disks and mounted filesystems |
| Filesystems | `vantorctl storage filesystems` | Kernel filesystem list includes ext2/ext4 and ISO9660 where configured |
| Modules | `cat /proc/modules` | Loaded optional modules, if any; built-in drivers need not appear here |
| Network | `vantorctl network` | Available NIC names and link states |
| DHCP/DNS | `cat /etc/resolv.conf` | Resolver entries appear only if DHCP/static network configuration supplied them |
| Services | `vantorctl service list` | Installed optional service scripts, or a clear empty-list message |

Capture the diagnostic boot entry output if the normal splash hides an error. A successful ISO build or boot-catalog inspection is not evidence that the guest reached the Live console.

### Installed-root validation boundary

The initramfs now loads available modules before looking for `root=/dev/...`, waits a bounded interval for the device, mounts the selected ext2/ext4 filesystem, and hands control to `/sbin/vantor-init`. The installed root then uses BusyBox init and mounts configured `/etc/fstab` entries.

The current installer can prepare the kernel, initramfs, GRUB configuration and fstab on an already-mounted target. Its GRUB installation action still requires GRUB's installer utility and BIOS modules to be bundled in the Live environment. Therefore, do not mark a complete disk-install/GRUB boot as validated until that missing installer dependency is resolved and the installed-root path is tested in Limbo.

## Important constraints

- Limbo emulates an x86_64 computer; it does not turn an ARM Android processor into a native x86_64 CPU. Emulation may be slow.
- Begin with a minimal console image.
- Do not claim Limbo compatibility until a real VANTOR image has booted there.
- GitHub Actions can perform repeatable build and automated QEMU smoke tests; Limbo remains the manual Android validation target.


## Legacy i486 BIOS test profile

After the separate i486 ISO is built, use a 32-bit x86 machine profile:

| Setting | Legacy test value |
|---|---|
| Architecture | x86 / i386 |
| CPU model | 486, if Limbo exposes it |
| RAM | Start with 32 MB; try 64 MB if the guest cannot complete boot |
| Machine | PC / i440fx-compatible |
| Display | VGA text console |
| Boot device | CD-ROM with the i486 ISO |
| Firmware | Legacy BIOS; this profile does not target UEFI |

If Limbo only offers a Pentium CPU model, it can test the 32-bit boot path but does not prove 486SX compatibility. A real 486SX/486DX computer is still required to validate the CPU floor. The i486 ISO has not yet been confirmed to boot.
