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
