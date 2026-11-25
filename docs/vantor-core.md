# VANTOR Core

VANTOR Core is the first project-owned userspace layer in Genesis. It is deliberately small and shell-based so it can run inside the static BusyBox bootstrap before the final toolchain and libc are ready.

## Components

- **VANTOR Init 0.1.0** (`/sbin/vantor-init`): mounts procfs, sysfs and devtmpfs when available, creates runtime directories, prints boot diagnostics, then hands off to `/sbin/init`. If no system init is installed, it opens an emergency shell.
- **Early entry point** (`/init`): delegates to VANTOR Init and provides a minimal emergency fallback.
- **VANTOR Control 0.1.0** (`/usr/bin/vantorctl`): dispatches system information and diagnostics commands.
- **VANTOR Hardware 0.1.0** (`/usr/bin/vantor-hw`): read-only inventory of CPU, memory, block devices, PCI devices and bound drivers, VirtIO devices, USB devices and network interfaces.
- **VANTOR Modules** (`/usr/sbin/vantor-modules`): loads optional storage, filesystem, VirtIO, USB and network drivers listed in `/etc/modules` through BusyBox `modprobe`; built-in kernel drivers are unaffected. The initramfs invokes this before searching for an installed root filesystem.
- **VANTOR Network** (`/usr/sbin/vantor-network`): reads installer settings as data (never executes the config file), validates interface and IPv4 fields, applies static IPv4 or discovers network interfaces and starts BusyBox DHCP. The DHCP hook configures the address, default route and DNS resolver.
- **VANTOR Service Control** (`/usr/sbin/vantor-service`): starts, stops, restarts, lists and checks optional foreground daemons using BusyBox `start-stop-daemon`. Service scripts live in `/etc/vantor/services/*.service`; runtime PID files live in `/run/vantor/services/`.
- **VANTOR Storage** (`/usr/sbin/vantor-storage`): reports block devices, mounted filesystems and kernel filesystem support. `mount-all` mounts configured `/etc/fstab` entries; it never partitions, formats or edits disks.
- **Process supervision**: BusyBox `init` is PID 1 and uses `/etc/inittab` to run `rcS` and respawn local console sessions. VANTOR Service Control manages optional daemons, but is not a crash-restarting supervisor.

## Commands

| Command | Purpose |
|---|---|
| `vantorctl info` | Show OS release metadata |
| `vantorctl hardware` | Run the VANTOR Hardware inventory |
| `vantorctl network` | Report network interface operational states |
| `vantorctl storage scan` | List detected block devices and mounted filesystems |
| `vantorctl storage filesystems` | Show filesystem support exposed by the kernel |
| `vantorctl storage mount-all` | Mount configured `/etc/fstab` entries |
| `vantorctl service list` | List installed optional services |
| `vantorctl service start NAME` | Start a service |
| `vantorctl service stop NAME` | Stop a service |
| `vantorctl service status NAME` | Check a service process |
| `vantorctl status` | Show release, kernel, PID 1 and uptime |
| `vantorctl version` | Show command version |

VANTOR Hardware reads procfs and sysfs only. It does not load drivers, change device state, configure networking, or write to hardware. Missing procfs/sysfs data is reported as unavailable rather than guessed. For isolated tests, the collector accepts `VANTOR_PROC_ROOT` and `VANTOR_SYS_ROOT` fixture paths.

## Build and test

`make rootfs` generates these files under `build/work/rootfs`. `make check` runs rootfs generator tests and validates generated shell syntax. `make image` performs the ordered x86_64 kernel → rootfs → BusyBox → initramfs → ISO pipeline. `make image-legacy` builds the 486-compatible BIOS ISO with its own BusyBox and initramfs; the legacy initramfs explicitly skips x86_64 kernel modules.

## Current boundaries

The initramfs loads available storage/filesystem modules before attempting the installed root, waits up to 20 seconds for the selected block device, then switches root through `/sbin/vantor-init`. `/sbin/init` is explicitly linked to BusyBox. During normal startup, VANTOR mounts configured fstab entries without formatting or partitioning. The x86_64 kernel enables ext2, ext4 (which also handles ext3 volumes), ISO9660/Joliet, FAT/VFAT, VirtIO block/SCSI, AHCI and optical-drive support; the i486 kernel includes its compatible filesystem and legacy storage drivers. The ISO workflow checks the generated boot catalog but does not prove a successful machine boot.

This is a minimal service layer, not a full init replacement. BusyBox init remains PID 1 and owns console respawn and child reaping. VANTOR Service Control manages optional foreground daemons but does not automatically restart crashed services, resolve dependencies, or manage runlevels. Network setup supports basic IPv4 DHCP and static configuration; it is not yet a full network manager and does not include Wi-Fi authentication or IPv6 configuration. Hardware inventory is descriptive, not a driver manager or hardware configuration utility.
