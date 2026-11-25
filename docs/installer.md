# VANTOR Minimal Installer

`vantor-install` is the first version of VANTOR's native text-mode installer.

## Interface

- Uses `dialog` when available.
- Falls back to a keyboard-driven terminal menu when `dialog` is absent.
- Offers installation, installed-system account configuration and an About screen.
- The UI and provisioning logic live in one small shell program for the early BusyBox environment.

## Minimal installation flow

1. Boot the VANTOR Live environment.
2. Prepare and mount the destination filesystem yourself.
3. Run `vantor-install` as root.
4. Choose **Install VANTOR Minimal**.
5. Enter the mounted target path, hostname and standard username.
6. The installer refreshes Nyan and installs `vantor-profile-minimal`.
7. It ensures the root account, standard account, wheel group, sudoers policy and home directories exist.

The destination must be an empty mounted filesystem (a `lost+found` directory is allowed). The installer refuses `/` and symbolic-link targets.

## Safety boundaries in this version

- It does not partition, format, resize or erase disks.
- It does not edit the host's bootloader.
- It does not configure filesystems or generate `fstab`.
- Passwords are locked in the initial account database. Set secure passwords before using the installed system normally.
- The wheel sudoers policy is prepared, but the `sudo` executable is a separate package and is not yet included in the Minimal payload.
- A bootloader and a complete post-install boot test are still required before calling the installed system production-ready.

## Non-interactive provisioning test

```sh
sh installer/vantor-install --configure /tmp/vantor-root vantor tester
```

This command only creates account and hostname configuration under the supplied target directory. It does not install packages or touch the running host.


## Installed-system boot preparation

The installer now supports a target-only boot-file preparation command:

    vantor-install --prepare-boot TARGET KERNEL INITRAMFS ARCH

- TARGET must be a mounted filesystem, not / or a symlink.
- KERNEL and INITRAMFS must be existing, non-empty files.
- The root block device and filesystem type are detected from the target mount entry in /proc/mounts; the command does not accept a user-supplied disk path.
- Supported root filesystems are ext2, ext3 and ext4.
- Copies the kernel and initramfs into /boot, writes a GRUB menu and creates a root entry in /etc/fstab.
- Does not partition, format, erase or install GRUB to a disk. GRUB installation remains a separate, explicit step.

The initramfs entry point recognizes root=/dev/... and rootfstype=..., mounts the installed root and uses BusyBox switch_root to hand off to the installed /sbin/init. Without a root device argument, it continues into the Live system as before.

This flow is the boot plumbing; it still requires the Live environment to expose the kernel/initramfs files and a separate GRUB installation step before a target disk can boot independently.
