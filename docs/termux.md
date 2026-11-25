# VANTOR on Android / Termux

The Termux target is an **ARM64 userspace running under PRoot**. It is a development and compatibility environment, not a virtual machine: Android continues to provide the Linux kernel. It cannot boot VANTOR's own kernel, load VANTOR kernel modules, or validate GRUB/initramfs. Use Limbo for those tests.

## Requirements

- An Android device with an ARM64 CPU (the current Redmi A5 is expected to be ARM64; verify with `uname -m`).
- Termux from a trusted distribution source.
- Free storage for the rootfs (the archive size is reported by the GitHub Release).

## Install

In Termux:

```sh
pkg update
pkg install proot tar curl
uname -m
```

The device must report `aarch64`. Download the latest archive from the [VANTOR Termux ARM64 release](https://github.com/Reaccionador2Jeje/vantor-linux/releases/tag/termux-aarch64), then extract it:

```sh
mkdir -p "$HOME/vantor/rootfs"
curl -fL "https://github.com/Reaccionador2Jeje/vantor-linux/releases/download/termux-aarch64/vantor-termux-aarch64-0.1.0.tar.gz" -o "$HOME/vantor/rootfs.tar.gz"
tar -xzf "$HOME/vantor/rootfs.tar.gz" -C "$HOME/vantor/rootfs"
mkdir -p "$HOME/.local/bin"
curl -fL "https://raw.githubusercontent.com/Reaccionador2Jeje/vantor-linux/main/tools/termux/vantor" -o "$HOME/.local/bin/vantor"
chmod +x "$HOME/.local/bin/vantor"
export PATH="$HOME/.local/bin:$PATH"
vantor
```

Verify the archive against the adjacent `SHA256SUMS` release asset before extraction if you want an independent integrity check.

## What works in this target

- VANTOR identity, release files and ARM64 static BusyBox.
- BusyBox shell, `vi`, basic file/process and network applets.
- VANTOR shell utilities and read-only userspace diagnostics where supported.
- PRoot root emulation for filesystem operations within the rootfs.

## Current limitations

- This is not a boot of VANTOR's kernel. Android's kernel remains active.
- PRoot does not provide real root privileges, kernel namespaces, device management or service supervision.
- Do not run the normal VANTOR init or installer inside this environment.
- Nyan's ARM64 repository is not published yet; the image sets `NYAN_ARCH=aarch64` but package installation is unavailable until that repository exists.
- The first ARM64 target is a test userspace, not a complete ARM64 ISO or native Android app.

## Rebuild

The workflow `.github/workflows/build-termux.yml` uses an ARM64 GitHub-hosted runner, builds BusyBox from the repository's pinned source, assembles the VANTOR rootfs, validates the ELF architecture and publishes a GitHub Release asset. Docker Hub publishing is optional and activates only after repository secrets `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` are configured.
