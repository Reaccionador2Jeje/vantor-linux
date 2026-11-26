# Sudo

VANTOR integrates upstream **sudo 1.9.17p2** as its privilege-delegation tool. It is built from the pinned upstream source for both x86_64 Genesis and i486 Legacy.

## Build

```sh
make sudo
# or
make sudo-legacy
```

The build disables PAM and dynamic plugin loading, embeds the sudoers policy plugin, and statically links the executable so it does not depend on a shared C runtime being present in the minimal rootfs. The build validates the ELF architecture and rejects dynamic executables.

## Live environment policy

The temporary Live account belongs to `wheel` and uses the documented Live password `vantor`. Both `/etc/sudoers.d/99-live` and the general `wheel` rule in `/etc/sudoers.d/10-wheel` require authentication. Run `passwd` in the Live session to change the password for that session.

The installer removes `99-live` when configuring a target system, so the Live exception is not copied into an installed system. The Live password is a public convenience credential, not a secret; never reuse it on an installed system. The installer removes `99-live`, and installed accounts must be assigned their own passwords.

## Setuid and archive ownership

`/usr/bin/sudo` is installed with mode `4755`. The build runner is unprivileged, so the initramfs packager uses `fakeroot` to encode root ownership and preserve the setuid bit in the cpio archive. It refuses to package an image if sudo, visudo, or the expected mode is missing.

## Security notes

- Keep `/etc/sudoers` and every included policy file owned by root and mode `0440`.
- Edit policy with `visudo`, not a plain text editor.
- Do not reuse the public Live password on installed systems.
- Sudo is not a replacement for account passwords, least-privilege policy, or careful review of commands granted to administrators.
