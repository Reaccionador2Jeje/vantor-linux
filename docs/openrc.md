# OpenRC integration policy

**Status:** approved architecture decision; implementation is staged behind the target C library.

## Decision

OpenRC is the mandatory service manager and init system for every VANTOR edition and supported architecture:

- VANTOR Genesis (x86_64)
- VANTOR Minimal (x86_64)
- VANTOR Legacy (i486)
- Future architectures must use the same OpenRC service model unless a documented technical incompatibility blocks that target.

BusyBox remains the bootstrap and recovery toolbox. Its shell, applets, DHCP client, mount tools, and other utilities remain useful, but BusyBox init and the custom VANTOR service supervisor are transitional and must not remain the normal service-management path after OpenRC is integrated.

## Responsibilities

OpenRC owns service dependency ordering, runlevels, service start/stop/restart/status, and orderly service startup and shutdown.

VANTOR-owned tools retain distribution-specific responsibilities:

- `vantorctl` is the user-facing control interface.
- `vantorctl service` delegates to OpenRC commands such as `rc-service`, `rc-update`, and `rc-status`.
- VANTOR service scripts live in `/etc/init.d` and follow OpenRC's service-script conventions.
- Runlevel membership is managed with `rc-update`; VANTOR must not maintain a second parallel service database.
- BusyBox remains available for rescue and early userspace utilities.

## Boot model

The intended normal boot path is OpenRC's `openrc-init` as PID 1, with the bootloader selecting `init=/sbin/openrc-init` only after the complete OpenRC userspace, runlevels, console getty, and shutdown path have been built and tested.

The existing BusyBox initramfs remains the bootstrap/recovery path during development. Do not switch the default boot command line to `openrc-init` until the integration checks pass. OpenRC documents both the normal PID 1 integration and the migration sequence in its upstream init guide.

## Build prerequisites and architecture gates

The current VANTOR repository has a first-stage Binutils/GCC bootstrap, but does not yet build and install a complete target C library. OpenRC is not a standalone static BusyBox applet: it is built with Meson and requires the target userspace runtime. Therefore:

1. Complete and pin the target C library and compiler runtime for x86_64.
2. Add pinned Meson/Ninja host build dependencies and a reproducible OpenRC source recipe.
3. Build OpenRC for x86_64 without optional PAM integration initially.
4. Install and validate the required OpenRC binaries, init scripts, runlevels, getty, and shutdown behavior in the rootfs.
5. Integrate `vantorctl service` with OpenRC and retire the custom supervisor from normal boot.
6. Repeat the build and boot checks for i486 before marking Legacy supported. A mandatory policy does not mean an untested binary is shipped.
7. Run the Genesis and Minimal images in Limbo/QEMU and test boot, console login, service dependency ordering, network startup, shutdown, and reboot before switching PID 1.

No guessed source checksums or unverified release versions may be added to `build/sources/sources.json`. Every upstream archive must have a verified digest before automated download/build.

## Acceptance criteria

- OpenRC is built for the target architecture and its installed executables have the expected ELF class and machine.
- `/sbin/openrc-init` can run as PID 1 in the target image.
- Required runlevels and console getty are enabled.
- Core VANTOR services start in dependency order and report state through OpenRC.
- `vantorctl service` delegates to OpenRC rather than the retired custom supervisor.
- Shutdown and reboot complete cleanly.
- CI builds each architecture independently; Legacy is not declared ready until its own checks pass.

## Upstream references

- [OpenRC source and build notes](https://github.com/OpenRC/openrc)
- [OpenRC user guide](https://github.com/OpenRC/openrc/blob/master/user-guide.md)
- [OpenRC init process guide](https://github.com/OpenRC/openrc/blob/master/init-guide.md)
- [OpenRC service script guide](https://github.com/OpenRC/openrc/blob/master/service-script-guide.md)
