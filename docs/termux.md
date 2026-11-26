# VANTOR on Android / Termux

The Termux target is an **ARM64 userspace running under PRoot**. It is a development and compatibility environment, not a virtual machine: Android continues to provide the Linux kernel. It cannot boot VANTOR's own kernel, load VANTOR kernel modules, or validate GRUB/initramfs. Use Limbo for those tests.

## Requirements

- An Android device with an ARM64 CPU (the current Redmi A5 is expected to be ARM64; verify with `uname -m`).
- Termux from a trusted distribution source.
- Free storage for the rootfs (the archive size is reported by the GitHub Release).

## Install with PRoot-Distro

Install the required Termux packages:

~~~sh
pkg update
pkg install proot-distro curl coreutils
uname -m
~~~

The device must report aarch64. Download the installer and run it:

~~~sh
curl -fL "https://raw.githubusercontent.com/Reaccionador2Jeje/vantor-linux/main/tools/termux/install-vantor" -o install-vantor
sh install-vantor
~~~

The installer downloads the official GitHub Release archive, verifies its SHA-256 checksum, installs it as the vantor container in PRoot-Distro, and places the vantor and vantor-pd launchers in Termux's executable path.

Start VANTOR:

~~~sh
vantor
~~~

Run one command without opening an interactive shell:

~~~sh
vantor uname -a
vantor vantor-info
vantor vantor-doctor
~~~

You can also use PRoot-Distro directly:

~~~sh
proot-distro login vantor -- /usr/bin/vantor-termux-shell
~~~

The archive can also be installed manually with proot-distro install /path/to/vantor-termux-aarch64-0.1.0.tar.gz --name vantor. PRoot-Distro accepts local rootfs archives and OCI images; VANTOR publishes the verified rootfs archive on GitHub Releases and a matching ARM64 container image on Docker Hub when publishing credentials are configured.

## Docker Hub image

The Docker image is an **ARM64 userspace container**, not a bootable ISO or a replacement for Android's kernel. The workflow builds it from `Dockerfile.termux` after assembling and validating the rootfs.

To enable publishing, configure these repository settings in GitHub:

1. In Docker Hub, create a Personal Access Token with read/write access for the VANTOR image repository. Do not use your Docker Hub account password.
2. In the GitHub repository, open **Settings → Secrets and variables → Actions**.
3. Under **Variables**, add `DOCKERHUB_USERNAME` with your Docker Hub username.
4. Under **Secrets**, add `DOCKERHUB_TOKEN` with the Personal Access Token value.

Never put the token in a commit, workflow file, issue, or chat. If account setup requires an age-eligible account holder, ask a parent or guardian to help with that setup.

After the variable and secret are saved, run **Actions → Build VANTOR Termux ARM64 userspace → Run workflow** on the `main` branch. Successful runs publish:

- `DOCKERHUB_USERNAME/vantor-linux:termux-arm64`
- `DOCKERHUB_USERNAME/vantor-linux:termux-0.1.0`

The workflow skips Docker Hub publishing when the username variable is absent. If the username is configured but the token is missing or invalid, the login step fails rather than silently pretending the image was published. The rootfs GitHub Release remains available independently.

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

The workflow `.github/workflows/build-termux.yml` uses an ARM64 GitHub-hosted runner, builds BusyBox from the repository's pinned source, assembles the VANTOR rootfs, validates the ELF architecture, and publishes a GitHub Release asset. When the Docker Hub variable and secret are configured, it also builds and pushes the ARM64 OCI image.
