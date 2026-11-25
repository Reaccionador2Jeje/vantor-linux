# VANTOR Linux kernel

## Primary target: x86_64

VANTOR builds the Linux 6.18.65 long-term-support kernel from the upstream kernel.org archive. The archive is pinned by the SHA-256 published in kernel.org's `sha256sums.asc` manifest and verified by `tools/fetch-sources.py` before extraction.

Build locally with:

```sh
make kernel
```

The build uses `x86_64_defconfig`, then enables the hardware and boot features required by VANTOR Genesis: initramfs, devtmpfs, proc/sysfs, PCI, virtio block/network, common legacy storage controllers, ext4, ISO9660, framebuffer console, VESA/EFI framebuffer, and supported DRM framebuffer paths.

Output: `build/work/kernel/vantor-kernel`

The generated configuration is recorded at `kernel/configs/vantor-x86_64.config`. GitHub Actions builds this target independently and publishes the kernel and configuration as a workflow artifact.

## Legacy target: i486

The separate Linux 6.1.193 target retains 486SX support and math emulation. It is built with `make kernel-legacy`; do not mix its kernel or initramfs with the x86_64 image.

## Validation boundary

A successful compile proves that the kernel image was produced, not that it boots on every physical machine or emulator. Limbo boot testing remains a separate acceptance step. Module packaging and final ISO integration are still required before calling either image complete.
