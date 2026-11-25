# Boot identity integration

VANTOR's boot visuals must use the shared identity in `assets/branding`.

Planned integration points:
- GRUB theme: dark navy background, titanium V mark, cyan selection/highlight.
- Kernel/early userspace splash: compact V mark and a restrained cyan progress indicator.
- Installer: same palette and typography, with high-contrast text fallback.

Do not add a runtime dependency on remote assets or fonts. Copy required assets into the generated boot image during the image-building stage. Keep a text-only fallback for firmware and emulators with limited graphics support.

This directory documents the integration contract; the bootloader and splash are not yet configured because the boot image stage has not been implemented.
