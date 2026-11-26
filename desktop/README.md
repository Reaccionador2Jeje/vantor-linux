# VANTOR Desktop — Desktop component roadmap

VANTOR keeps the console-first Minimal base independent from graphical components. Desktop environments are optional Nyan profiles; do not add their dependency trees to the base ISO.

## Planned selectable profiles

| Profile | Session/display stack | Desktop |
|---|---|---|
| `wayland` | Wayland libraries, protocol definitions, seat service, D-Bus, Mesa, compositor | Compositor/test session only; Wayland is not a desktop |
| `xfce4` | Xorg + Xinit initially; Wayland compatibility is not assumed | Xfce session, panel, settings, XFWM, Thunar, terminal |
| `gnome` | Mutter, GNOME session, Wayland + Xorg fallback where built | GNOME Shell, Control Center, Nautilus, terminal |
| `kde-plasma` | KWin, Plasma workspace, Wayland + Xorg fallback where built | Plasma, Konsole, Dolphin |
| `lxqt` | Xorg initially; optional Wayland via a supported compositor such as labwc | LXQt session, panel, QTerminal, PCManFM-Qt |
| `lxde` | Xorg + Xinit | LXSession, LXPanel, Openbox, LXTerminal, PCManFM |

## Current status

The component names are recorded in `packages/catalog.tsv` as **planned**. They are not yet downloadable Nyan packages, and the profiles are not installable yet. The repository's package index is the source of truth for availability.

Desktop packaging requires a reproducible source build or trusted upstream binary package, dependency closure, per-architecture ABI/runtime validation, archive checksums, license notices and smoke tests. The first supported graphical target will be x86_64 Genesis. i486 Legacy remains console-first; ARM64 graphical packages are a separate target.

## Existing VANTOR session

The existing `desktop/bin/vantor-session` and Openbox/tint2 configuration are VANTOR's lightweight session integration. They are configuration files, not a complete published desktop package.

## Activation target

Once the packages are published, the intended workflow is:

```sh
nyan update
nyan profiles
nyan install-profile xfce4
```

A graphical login manager and session selector will be offered only after both the X11 and Wayland session paths have passed boot and login tests.

## Additional system components

The Nyan catalog also tracks optional supporting components (currently marked `planned`):

- **Login/display managers:** SDDM, GDM, LightDM, greetd. Choose one; do not enable several at once.
- **Display and compatibility:** X.Org Server, Xwayland, Xinit, XRandR, XInput, XKB, X.Org input/video drivers.
- **Window managers and utilities:** Openbox, XFWM, tint2, Picom, Rofi, dmenu, Plank, Feh, Nitrogen, LXAppearance.
- **Networking:** NetworkManager, its tray applet, wpa_supplicant, iwd, iproute2, iputils, OpenSSH, Avahi and DHCP clients.
- **Audio:** PipeWire, WirePlumber, PipeWire PulseAudio compatibility, ALSA tools, PulseAudio (legacy), and volume control.
- **Hardware and desktop integration:** libinput, Mesa/DRM/Vulkan, D-Bus, elogind/seat compatibility, Polkit, AccountsService, UDisks, GVfs, portals, fonts, icon themes, GTK and Qt.
- **Bluetooth, printing and scanning:** BlueZ, Blueman, CUPS, printer tools, SANE and Simple Scan.
- **Applications:** Firefox, Chromium, Thunderbird, LibreOffice, PDF/document viewers, image viewers, VLC/mpv, archive managers and editors.
- **System utilities:** GParted, disk usage tools, QEMU and virt-manager.

The package catalog records component names and intent; it does not mean the binaries, dependency closures or Nyan archives have been built. NetworkManager and VANTOR's current network service also need an explicit ownership/transition design before both can manage interfaces simultaneously.


## Platform-specific Nyan profiles

The profile manifests under `desktop/profiles/` now separate three use cases:

- `android-termux`: ARM64 Android userspace, XFCE session on a private TigerVNC `Xvnc` display. It does not assume Android provides a Linux DRM seat, a system display manager, or native Xorg.
- `pc`: x86_64 VANTOR Genesis with a native Xorg/Xinit session. TigerVNC and display managers are optional, not mandatory.
- `remote`: remote-access tools only (TigerVNC required; x11vnc, wayvnc, FreeRDP and Remmina optional). It does not install a local desktop session.

These are validated manifests, not installable profile packages yet. Nyan must not offer installation until all required packages and their runtime dependencies have built and been published for the target architecture. Android Termux is an ARM64 target and is separate from the x86_64 PC target.
