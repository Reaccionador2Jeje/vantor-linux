# VANTOR boot identity

The x86_64 Live ISO uses the native GRUB theme at
`boot/grub/themes/vantor/theme.txt`, staged at
`/boot/grub/themes/vantor/theme.txt`. It is loaded locally by GRUB and uses
GRUB's bundled Unicode font; it has no network or remote-font dependency.

Visual language:
- Deep Space background: `#071321`
- Cyan title and selected entry: `#00CFFF`
- Titanium menu text: `#B9CCE3`
- Muted Steel supporting text: `#9BB0C8`
- Slogan: **ONE SYSTEM. EVERY GENERATION.**

The i486 Legacy menu deliberately remains in BIOS text mode for compatibility
with older graphics adapters and emulators. It shares the VANTOR palette,
product naming and slogan.

The installed x86_64 boot configuration also receives the theme when the
installer can read it from the Live media. Legacy installations retain the
text-mode fallback.

The kernel/early-userspace splash is a separate surface. On x86_64, the rootfs
includes the static fbdev renderer from `core/boot/vantor-fb-splash.c` when
static host compilation is available. It draws the VANTOR orbital mark,
metallic V, name, slogan and progress bar directly into `/dev/fb0`. The
kernel enables framebuffer and common virtual-GPU paths, including DRM fbdev
emulation. If no supported framebuffer is available, the system falls back
to the ANSI splash. The i486 Legacy profile remains text-only by design.

The graphical animation and progress indicators are initialization milestones,
not a byte-accurate or kernel-wide progress measurement. Visual compatibility
still requires a real boot test in Limbo; the implementation does not claim
that this has already passed.
