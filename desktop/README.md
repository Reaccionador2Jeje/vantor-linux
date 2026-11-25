# VANTOR Desktop — Genesis Shell

VANTOR Desktop begins as a deliberately lightweight X11 session for the x86_64 edition. The first implementation composes proven upstream building blocks while keeping the VANTOR session, menu, panel configuration, keyboard map and visual identity in this repository.

## First-stage stack

- Xorg Server + Xinit: display server and session startup (provided as system packages).
- Openbox: lightweight window manager.
- tint2: VANTOR-configured panel and task list.
- xterm: terminal fallback.
- pcmanfm: optional desktop icons and file manager integration.
- xsetroot: low-cost dark desktop background.

This is not a claim that these dependencies are already shipped in the ISO. They are tracked as planned Nyan packages until their source builds, dependency closure and binary archives are published.

## Files

- \`bin/vantor-session\`: validates the display and required tools, starts the panel and optional desktop manager, then runs Openbox.
- \`openbox/rc.xml\`: window behavior and keyboard shortcuts.
- \`openbox/menu.xml\`: VANTOR root menu.
- \`tint2/tint2rc\`: bottom panel using the official navy/cyan palette.
- \`applications/\`: desktop launchers.

## Starting a session (once dependencies are installed)

From a local text login:

\`\`\`sh
startx /usr/bin/vantor-session
\`\`\`

The desktop uses Super+Enter for a terminal, Super+E for the file manager (when installed), Super+D to show the desktop, and Ctrl+Alt+Left/Right to switch workspaces. Right-click the desktop for the VANTOR menu.

## Compatibility policy

The first graphical target is x86_64. The i486 Legacy profile remains console-first; a graphical stack is optional and must never become a dependency of the base system. The session deliberately avoids a compositor and GPU-only effects so it can run on modest virtual and physical graphics adapters.

## Not implemented yet

The login/display manager, native VANTOR settings application, native file manager, package installer GUI, compositor, accessibility UI and complete graphical package build are later milestones. The initial session is an integration layer, not a finished desktop environment.
