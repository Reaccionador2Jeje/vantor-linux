# VANTOR Core

VANTOR Core is the small distribution-owned userspace layer. BusyBox supplies static early-boot and recovery utilities; **OpenRC 0.64.1 owns normal PID 1 and all service lifecycle management**.

## Components

- **VANTOR Init 0.2.0** (`/sbin/vantor-init`): initramfs-to-system handoff helper. It mounts procfs, sysfs, devtmpfs and /run, then executes `/sbin/init`, which is linked to OpenRC's `/sbin/openrc-init`. In recovery mode it executes `/sbin/init nonetwork`.
- **Early entry point** (`/init`): runs from the initramfs, discovers an optional installed root, and hands control to VANTOR Init.
- **OpenRC** (`/sbin/openrc-init`, `/sbin/openrc`, `/sbin/rc-service`, `/sbin/rc-update`, `/sbin/rc-status`): PID 1, dependency ordering, runlevels, service control, and shutdown.
- **VANTOR Control 0.1.0** (`/usr/bin/vantorctl`): dispatches system information and diagnostics. Its service and log commands delegate to OpenRC.
- **VANTOR Doctor 0.2.0** (`/usr/bin/vantor-doctor`): built-in offline read-only checks for core binaries, virtual filesystem mounts, user environment, Nyan configuration, OpenRC and network-interface presence.
- **VANTOR Hardware 0.1.0** (`/usr/bin/vantor-hw`): read-only inventory of CPU, memory, block devices, PCI devices and bound drivers, VirtIO devices, USB devices and network interfaces.
- **VANTOR Modules** (`/usr/sbin/vantor-modules`): loads optional storage, filesystem, VirtIO, USB and network drivers listed in `/etc/modules`.
- **VANTOR Network** (`/usr/sbin/vantor-network`): reads installer settings as data, validates interface and IPv4 fields, applies static IPv4 or starts BusyBox DHCP.
- **VANTOR Storage** (`/usr/sbin/vantor-storage`): reports block devices, mounted filesystems and kernel filesystem support. Its explicit mount commands do not partition or format disks.

## OpenRC services

VANTOR installs native OpenRC service scripts in `/etc/init.d`:

- `vantor-early` starts the VANTOR boot presentation.
- `vantor-modules` loads configured optional modules.
- `vantor-network` configures network interfaces and stops its DHCP clients.
- `vantor-console.tty1` and `vantor-console.ttyS0` run supervised Live console sessions.
- OpenRC's `localmount` service mounts configured filesystems in the normal runlevel.

The `nonetwork` recovery runlevel keeps the console available but omits local filesystem mounts and network startup. The init handoff helper selects it when the kernel command line contains `vantor.recovery`, `recovery`, or `single`.

## Commands

| Command | Purpose |
|---|---|
| `vantorctl info` | Show OS release metadata |
| `vantorctl hardware` | Run the VANTOR Hardware inventory |
| `vantorctl network` | Report network interface operational states |
| `vantorctl storage scan` | List detected block devices and mounted filesystems |
| `vantorctl storage filesystems` | Show filesystem support exposed by the kernel |
| `vantorctl storage mount-all` | Mount configured `/etc/fstab` entries manually |
| `vantorctl service list` | Show OpenRC service status |
| `vantorctl service start NAME` | Start a service with `rc-service` |
| `vantorctl service stop NAME` | Stop a service with `rc-service` |
| `vantorctl service status NAME` | Check a service with `rc-service` |
| `vantorctl service enable NAME [RUNLEVEL]` | Enable a service with `rc-update` |
| `vantorctl service disable NAME [RUNLEVEL]` | Disable a service with `rc-update` |
| `vantorctl service runlevels` | Show configured runlevels |
| `vantorctl logs [follow]` | Read or follow `/var/log/rc.log` |
| `vantorctl recovery` | Report whether recovery mode was selected |
| `vantorctl status` | Show release, kernel, PID 1 and uptime |
| `vantorctl doctor` | Run offline base-system health checks |
| `vantorctl version` | Show command version |

## Build and test

The x86_64 image pipeline builds the rootfs, BusyBox, static OpenRC, initramfs and ISO in that order. `make image-legacy` performs the same integration with a 32-bit i486 OpenRC build. The initramfs builder refuses to package an image unless `/sbin/openrc-init` exists and `/sbin/init` points to it.

`make check` validates the rootfs generator, OpenRC service scripts, source pins and build contracts. ISO structure checks do not replace boot testing in Limbo/QEMU.

## Current boundaries

Network setup currently supports IPv4 DHCP and static configuration; it is not yet a full network manager and does not include Wi-Fi authentication or IPv6 configuration. Hardware inventory is descriptive, not a driver manager or hardware configuration utility.
