# VANTOR graphical profile definitions

These are profile manifests for the planned Nyan desktop selector. Package names match `packages/catalog.tsv`. They are intentionally **not** Nyan installable metapackages until each listed package and its transitive runtime dependencies has a verified archive in the repository index.

## Wayland foundation — `wayland`

Required foundation: `wayland`, `wayland-protocols`, `mesa`, `dbus`, `seatd`, `xdg-desktop-portal`, and one compositor. The first minimal compositor target is `weston`; lightweight desktop sessions may use `wlroots` with `labwc`. Do not install both compositors by default.

## Xfce — `xfce4`

`xorg-server`, `xinit`, `dbus`, `mesa`, `xfce4-session`, `xfce4-panel`, `xfwm4`, `xfce4-settings`, `xfce4-terminal`, `thunar`, `xdg-desktop-portal`, `xdg-desktop-portal-gtk`.

## GNOME — `gnome`

`dbus`, `mesa`, `mutter`, `gnome-session`, `gnome-shell`, `gnome-control-center`, `gnome-terminal`, `nautilus`, `xdg-desktop-portal`, `xdg-desktop-portal-gtk`. Include GTK runtime and accessibility services in the dependency closure.

## KDE Plasma — `kde-plasma`

`dbus`, `mesa`, `qt6-base`, `qt6-wayland`, `kwin`, `plasma-workspace`, `plasma-desktop`, `konsole`, `dolphin`, `xdg-desktop-portal`, `xdg-desktop-portal-kde`.

## LXQt — `lxqt`

`xorg-server`, `dbus`, `mesa`, `qt6-base`, `lxqt-session`, `lxqt`, `labwc` (optional Wayland session), `qterminal`, `pcmanfm-qt`, `xdg-desktop-portal`.

## LXDE — `lxde`

`xorg-server`, `xinit`, `dbus`, `mesa`, `lxsession`, `lxpanel`, `openbox`, `lxterminal`, `pcmanfm`.

## Release gates

- Resolve dependencies from packages built for the target ABI; never mix Debian/Ubuntu packages blindly with VANTOR.
- Package symlinks, shared libraries, desktop entries, fonts, icons, D-Bus service files and systemd/OpenRC integration must be audited against VANTOR's init and Nyan archive policy.
- Verify session start, keyboard/mouse, framebuffer/DRM, networking, logout, and fallback to TTY in Limbo/QEMU.
- First release target: x86_64. i486 and aarch64 stay unavailable until their packages are built and tested.
