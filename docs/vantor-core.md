# VANTOR Core

VANTOR Core is the first project-owned userspace layer in Genesis. It is deliberately small and shell-based so it can run inside the static BusyBox bootstrap before the final toolchain and libc are ready.

## Components

- **VANTOR Init 0.1.0** (`/sbin/vantor-init`): mounts procfs, sysfs and devtmpfs when available, creates runtime directories, prints boot diagnostics, then hands off to `/sbin/init`. If no system init is installed, it opens an emergency shell.
- **Early entry point** (`/init`): delegates to VANTOR Init and provides a minimal emergency fallback.
- **VANTOR Control 0.1.0** (`/usr/bin/vantorctl`): read-only system information commands.

## Commands

| Command | Purpose |
|---|---|
| `vantorctl info` | Show OS release metadata |
| `vantorctl hardware` | Report CPU, memory and block devices visible through procfs/sysfs |
| `vantorctl network` | Report interface operational states |
| `vantorctl status` | Show release, kernel, PID 1 and uptime |
| `vantorctl version` | Show command version |

The network command is diagnostic only. It does not bring interfaces up, request DHCP leases, change DNS, or configure routes.

## Build and test

`make rootfs` generates these files under `build/work/rootfs`. `make check` runs rootfs generator tests and validates generated shell syntax.

## Current boundaries

This is a bootstrap init, not a complete service manager. It does not yet supervise long-running services, parse dependency graphs, manage runlevels, or guarantee zombie reaping. Those require a dedicated PID 1 implementation and integration tests. The fallback shell is intended for bring-up and debugging, not production recovery policy.
