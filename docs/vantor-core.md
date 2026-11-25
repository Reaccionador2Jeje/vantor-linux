# VANTOR Core

VANTOR Core is the first project-owned userspace layer in Genesis. It is deliberately small and shell-based so it can run inside the static BusyBox bootstrap before the final toolchain and libc are ready.

## Components

- **VANTOR Init 0.1.0** (`/sbin/vantor-init`): mounts procfs, sysfs and devtmpfs when available, creates runtime directories, prints boot diagnostics, then hands off to `/sbin/init`. If no system init is installed, it opens an emergency shell.
- **Early entry point** (`/init`): delegates to VANTOR Init and provides a minimal emergency fallback.
- **VANTOR Control 0.1.0** (`/usr/bin/vantorctl`): dispatches system information and diagnostics commands.
- **VANTOR Hardware 0.1.0** (`/usr/bin/vantor-hw`): read-only inventory of CPU, memory, block devices, PCI devices, VirtIO devices and network interfaces.\n- **VANTOR Modules** (`/usr/sbin/vantor-modules`): loads optional drivers listed in `/etc/modules` through BusyBox `modprobe`; built-in kernel drivers are unaffected.
- **VANTOR Network** (`/usr/sbin/vantor-network`): reads installer settings as data (never executes the config file), validates interface and IPv4 fields, applies static IPv4 or discovers network interfaces and starts BusyBox DHCP. The DHCP hook configures the address, default route and DNS resolver.

## Commands

| Command | Purpose |
|---|---|
| `vantorctl info` | Show OS release metadata |
| `vantorctl hardware` | Run the VANTOR Hardware inventory |
| `vantorctl network` | Report network interface operational states |
| `vantorctl status` | Show release, kernel, PID 1 and uptime |
| `vantorctl version` | Show command version |

VANTOR Hardware reads procfs and sysfs only. It does not load drivers, change device state, configure networking, or write to hardware. Missing procfs/sysfs data is reported as unavailable rather than guessed. For isolated tests, the collector accepts `VANTOR_PROC_ROOT` and `VANTOR_SYS_ROOT` fixture paths.

## Build and test

`make rootfs` generates these files under `build/work/rootfs`. `make check` runs rootfs generator tests and validates generated shell syntax.

## Current boundaries

This is a bootstrap init, not a complete service manager. It does not yet supervise long-running services, parse dependency graphs, manage runlevels, or guarantee zombie reaping. Network setup supports basic IPv4 DHCP and static configuration; it is not yet a full network manager and does not include Wi-Fi authentication or IPv6 configuration. Hardware inventory is descriptive, not a driver manager or hardware configuration utility.
