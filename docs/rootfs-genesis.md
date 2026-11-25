# VANTOR Genesis root filesystem

The first system-integration step creates a **rootfs skeleton**, not a complete operating system image.

Run from the repository root:

```sh
make rootfs
```

The generated tree is written to `build/work/rootfs` (ignored build output). The generator refuses to overwrite a non-empty destination.

## Installed identity

- `/etc/os-release` — distribution identity and version.
- `/etc/vantor-release` — human-readable release marker.
- `/etc/hostname` — initial hostname, `vantor`.
- `/etc/issue` and `/etc/motd` — console greeting.
- `/etc/profile.d/vantor.sh` — restrained cyan VANTOR shell prompt.
- `/etc/vantor-brand.json` — machine-readable brand metadata.
- `/usr/share/vantor/branding/` — official SVG logos, CSS and JSON theme.
- `/init` — early-userspace mount setup and handoff to `/sbin/init`.

The init script expects BusyBox applets and a shell to be present in the final rootfs. Until BusyBox and the kernel are integrated, this generated skeleton is not independently bootable. The next build stage will install BusyBox, create device nodes or devtmpfs support, assemble the initramfs and perform a QEMU smoke test in CI. Manual Android testing remains Limbo PC Emulator.
