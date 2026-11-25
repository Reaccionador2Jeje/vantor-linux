# VANTOR testing with Limbo on Android

VANTOR's Android virtual-machine test target is **Limbo PC Emulator**. Do not use
QORVEX as a test dependency or as the runtime for this project.

Limbo is QEMU-based and documents support for x86 and x86_64 guest machines.
Its User networking mode provides NAT; TAP is not supported in the normal
unrooted setup. The Limbo guide also documents IDE disks, CD-ROM ISO images,
standard VGA, and a 2 GB guest-memory ceiling in the described interface.
Actual limits can vary by Limbo build and Android device.

## First VANTOR boot profile

Use this profile only after the project publishes a bootable BIOS-compatible ISO:

| Setting | VANTOR test value |
|---|---|
| Architecture | x86_64 |
| Machine | PC / i440fx-compatible, if selectable |
| CPU model | qemu64 or closest available generic x86_64 model |
| RAM | 512 MB initially; increase to 1024 MB if stable |
| Display | Standard VGA (std) |
| Boot device | CD-ROM with the VANTOR ISO |
| Disk | Optional qcow2 virtual disk for installation tests |
| Network | User-mode networking (NAT) |
| DNS | Use the DNS address configured in Limbo if guest name resolution fails |
| Interface | SDL for foreground testing; VNC if remote/background access is needed |

The first milestone is a text-mode boot reaching a VANTOR shell. A desktop
environment is deliberately out of scope for the first emulator test.

## Test sequence

1. Create a new virtual machine in Limbo and select x86_64.
2. Attach the published VANTOR ISO as the CD-ROM.
3. Start with 512 MB RAM and standard VGA.
4. Boot and record the last visible console output if startup fails.
5. Confirm the kernel starts, initramfs mounts, and the VANTOR init process reaches a shell.
6. Test the virtual disk separately after basic boot works.
7. Test NAT and DNS only after the guest has a network driver and userspace network configuration.

## Important constraints

- Limbo emulates an x86_64 computer; it does not turn the Android phone's ARM processor into a native x86_64 CPU. Emulation may be slow.
- Begin with a minimal console image. Large desktop environments may be too slow or memory-intensive for a phone-based emulator.
- Do not claim Limbo compatibility until a real VANTOR image has booted there.
- GitHub Actions can perform repeatable build and automated QEMU smoke tests; Limbo remains the manual Android validation target.
