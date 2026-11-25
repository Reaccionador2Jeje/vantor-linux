# VANTOR Linux — Visual Identity

**Slogan:** ONE SYSTEM. EVERY GENERATION.  
**Origin:** Independent · **Base:** Independent · **Goal:** Universal

## Brand idea

VANTOR is an independent, adaptable Linux distribution. Its identity combines a forward-pointing metallic **V** with a cyan orbital ring: the V represents the system, while the orbit represents broad hardware reach and generations working together.

## Official assets

- `assets/branding/vantor-mark.svg` — emblem for icons and compact spaces.
- `assets/branding/vantor-lockup.svg` — full horizontal logo.
- `assets/branding/theme.json` — machine-readable design tokens.
- `assets/branding/theme.css` — reusable interface tokens and baseline styles.

## Color palette

| Token | Hex | Use |
|---|---|---|
| Deep Space | `#071321` | Main background |
| Night Surface | `#0C1D30` | Panels and surfaces |
| Raised Surface | `#132A43` | Selected/raised elements |
| VANTOR Cyan | `#00CFFF` | Primary accent and focus |
| Orbit Blue | `#0877FF` | Secondary accent |
| Titanium | `#B9CCE3` | Logo and secondary highlights |
| Snow | `#F4F8FF` | Main text |
| Muted Steel | `#9BB0C8` | Secondary text |

## Typography

- Display: Orbitron (use a local/system fallback if unavailable).
- Interface: Rajdhani.
- Fallback: Noto Sans.
- Never make the interface depend on downloading fonts at runtime.

## System-wide application plan

The same tokens and logo assets are the source of truth for:
1. Bootloader theme and boot splash.
2. Installer and first-run setup.
3. Login/greeter.
4. Desktop wallpaper, panel, menus and system settings.
5. Terminal prompt and system information.
6. Icon theme and notifications.

These assets establish the official design system now. Runtime integration will be added as each subsystem exists; VANTOR does not yet have a completed desktop, installer, greeter or bootable image, so this commit does not claim those surfaces are already running.

## Accessibility and usage

- Maintain readable contrast; cyan is an accent, not body-text color on dark backgrounds.
- Keep a visible keyboard focus ring.
- Respect reduced-motion preferences.
- Preserve clear space around the logo and do not stretch, rotate or recolor the official mark arbitrarily.
- Provide monochrome variants when a bootloader or firmware screen cannot render gradients.

## Versioning

This is VANTOR Visual Identity v1. Changes to palette, typography or logo geometry should update the JSON and CSS tokens together.
