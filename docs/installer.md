# VANTOR Minimal Installer

`vantor-install` is the first version of VANTOR's native text-mode installer.

## Interface

- Uses `dialog` when available.
- Falls back to a keyboard-driven terminal menu when `dialog` is absent.
- Offers installation, installed-system account configuration, boot-file preparation and an About screen.
- The UI and provisioning logic live in one small shell program for the early BusyBox environment.

## Minimal installation flow

1. Boot the VANTOR Live environment. Live startup attempts to mount the booted ISO read-only at /run/vantor-media.
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
- BusyBox `su` is enabled for both x86_64 and i486 and its `/bin/su` applet link is recreated during system initialization. It requires a usable target-account password; the initial installer leaves root and the standard user's passwords locked. The wheel sudoers policy is prepared, but the `sudo` executable is not included yet.
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


## Installer configuration additions

The interactive installer now includes these additional setup actions:

- **Network:** records DHCP or static IPv4 configuration (interface, address/prefix, gateway and DNS) under `/etc/vantor/network.conf`. VANTOR startup applies the saved static configuration with `ip`, or requests a DHCP lease. If no saved network configuration exists, startup falls back to DHCP on detected interfaces.
- **Nyan mirror:** accepts an HTTPS repository base URL and saves it in `/etc/nyan.conf`. The installation flow asks for the mirror before refreshing the package index.
- **Additional packages:** refreshes the selected Nyan index and accepts package names separated by spaces. Nyan verifies package checksums and dependency metadata as it installs.
- **System preferences:** saves hostname, locale (`/etc/locale.conf`) and timezone (`/etc/timezone`); copies the timezone file to `/etc/localtime` when it exists in the Live environment.

These options are also available from the installer menu after installation. The current package selection prompt uses package names rather than a graphical catalog; package availability depends on the selected mirror and architecture. Static networking requires the BusyBox `ip` applet in the image.


## Disk inspection and GRUB BIOS installation

The installer menu now provides two additional actions:

- **Inspect disks and partitions** displays `lsblk` output when available, or falls back to `/proc/partitions` and optional `blkid`. This action is read-only.
- **Install GRUB bootloader** checks that the installed target is mounted and already has a generated `/boot/grub/grub.cfg`. It identifies the parent whole disk from sysfs, rejects partition paths, and requires the user to type the exact disk path before running `grub-install --target=i386-pc`.

Important: the current Live image does not yet bundle `grub-install` and its BIOS modules. The menu therefore reports that the feature is unavailable and makes no disk changes until those tools are included in a future image. This implementation is a guarded integration point, not proof of a working installed bootloader. The disk inventory is informational only; partitioning and formatting remain manual.


## Standard mount points

The Minimal root filesystem creates `/mnt` and `/media` at image-build time, so the installer default `/mnt` exists. `/mnt` is only an empty mount point until an existing partition is mounted there; creating the directory does not mount or format a disk. The installer can also create a custom mount point such as `/mnt/vantor-target` before mounting an existing supported filesystem.

## Mounting an existing installation partition

The installer menu includes **Mount existing Linux partition**. It accepts an existing block device and an ext2, ext3, or ext4 filesystem, then mounts it at a user-selected absolute mount point (default `/mnt/vantor-target`). It refuses non-`/dev` paths, non-block devices, unsupported filesystem types, symbolic-link mount points, and mount points that are already in use. It does not create partitions, format filesystems, or erase data.

After mounting, choose **Install VANTOR Minimal** and enter that exact mount point. The installer now passes the selected target through to the hostname/locale/timezone and additional-package steps, avoiding accidental writes to a different default path.


## Nyan package catalog and batch installation

Installer 0.4.0 refreshes the selected architecture's Nyan index and displays every package published for that architecture. Enter one or more package names separated by spaces to install them in one Nyan invocation; enter `search:TERM` to search the catalog and then choose package names from the results. The installer uses the target root, repository mirror and architecture selected for that installation. Nyan validates each package name and resolves dependencies. During interactive terminal installs, Nyan displays a small animated Nyan Cat-style progress indicator for resolving, downloading, verifying and unpacking each package. Non-interactive output remains clean and machine-readable. The catalog only contains packages actually published for the selected architecture; it does not imply that every planned package exists yet.
