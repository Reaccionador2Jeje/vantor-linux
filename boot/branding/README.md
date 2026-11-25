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

The kernel/early-userspace splash is a separate surface and is not implemented
by this GRUB theme.
