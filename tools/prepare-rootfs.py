#!/usr/bin/env python3
"""Assemble a deterministic VANTOR rootfs skeleton with its official identity."""
from __future__ import annotations
import argparse, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRANDING = ROOT / "assets" / "branding"
BRAND_FILES = ("vantor-mark.svg", "vantor-lockup.svg", "theme.json", "theme.css")

def write(path: Path, content: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(mode)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "work" / "rootfs")
    parser.add_argument("--arch", choices=("x86_64", "i486"), default="x86_64")
    args = parser.parse_args()
    output = args.output.resolve()
    if output == Path("/") or output == ROOT or output == ROOT / "rootfs":
        parser.error("refusing unsafe output directory")
    if output.exists() and any(output.iterdir()):
        parser.error(f"output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    theme = json.loads((BRANDING / "theme.json").read_text(encoding="utf-8"))
    brand_dir = output / "usr/share/vantor/branding"
    brand_dir.mkdir(parents=True, exist_ok=True)
    for name in BRAND_FILES:
        shutil.copy2(BRANDING / name, brand_dir / name)

    write(output / "etc/os-release", """NAME="VANTOR Linux"
PRETTY_NAME="VANTOR Linux Minimal 0.1.0"\nVARIANT="Minimal"\nVARIANT_ID=minimal
ID=vantor
ID_LIKE=linux
VERSION="0.1.0"
VERSION_ID="0.1.0"
VERSION_CODENAME=genesis
BUILD_ID=genesis
ANSI_COLOR="0;38;2;0;207;255"
HOME_URL="https://github.com/Reaccionador2Jeje/vantor-linux"
""")
    write(output / "etc/vantor-release", "VANTOR Linux 0.1.0 (Genesis)\n")
    write(output / "etc/passwd", """root:x:0:0:root:/root:/bin/sh
live:x:1000:1000:VANTOR Live User:/home/live:/bin/sh
""")
    write(output / "etc/group", """root:x:0:
wheel:x:10:live
users:x:100:
""")
    write(output / "etc/shadow", """root:!:19000:0:99999:7:::
live:!:19000:0:99999:7:::
""", 0o600)
    write(output / "etc/gshadow", """root:!::
wheel:!::live
users:!::
""", 0o600)
    write(output / "etc/sudoers", """# VANTOR Minimal sudo policy
# Passwords are locked in the Live image until explicitly configured.
#includedir /etc/sudoers.d
""", 0o440)
    write(output / "etc/sudoers.d/10-wheel", "%wheel ALL=(ALL:ALL) ALL\n", 0o440)
    (output / "root").mkdir(parents=True, exist_ok=True)
    (output / "root").chmod(0o700)
    (output / "home/live").mkdir(parents=True, exist_ok=True)
    (output / "home/live").chmod(0o700)
    write(output / "etc/fstab", """proc      /proc   proc      defaults          0 0
sysfs     /sys    sysfs     defaults          0 0
devtmpfs  /dev    devtmpfs  mode=0755         0 0
tmpfs     /run    tmpfs     mode=0755,nosuid  0 0
tmpfs     /tmp    tmpfs     mode=1777,nosuid  0 0
""")
    write(output / "etc/inittab", """# VANTOR Minimal BusyBox init configuration
::sysinit:/etc/init.d/rcS
tty1::respawn:/bin/busybox getty -L -n -l /usr/bin/vantor-live-session 0 tty1 vt100
ttyS0::respawn:/bin/busybox getty -L -n -l /usr/bin/vantor-live-session 115200 ttyS0 vt100
::ctrlaltdel:/bin/busybox reboot
::shutdown:/bin/busybox umount -a -r
""")
    write(output / "etc/init.d/rcS", """#!/bin/sh
# VANTOR early system setup; safe to run more than once.
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
mkdir -p /proc /sys /dev /run /tmp /var/log /home/live
mount -t proc proc /proc 2>/dev/null || true
mount -t sysfs sysfs /sys 2>/dev/null || true
mount -t devtmpfs devtmpfs /dev 2>/dev/null || true
chmod 1777 /tmp 2>/dev/null || true
hostname vantor 2>/dev/null || true
if command -v mdev >/dev/null 2>&1; then
    echo /bin/mdev > /proc/sys/kernel/hotplug 2>/dev/null || true
    /bin/busybox mdev -s 2>/dev/null || true
fi
# Expose the booted VANTOR ISO read-only so the installer can copy its kernel/initramfs.
mkdir -p /run/vantor-media
for media_dev in /dev/sr0 /dev/cdrom; do
    [ -b "$media_dev" ] || continue
    if mount -t iso9660 -o ro "$media_dev" /run/vantor-media 2>/dev/null; then
        echo "[VANTOR] Installation media mounted at /run/vantor-media."
        break
    fi
done
# Start DHCP only on detected non-loopback interfaces.
if command -v udhcpc >/dev/null 2>&1 && [ -d /sys/class/net ]; then
    for iface_path in /sys/class/net/*; do
        [ -e "$iface_path" ] || continue
        iface="${iface_path##*/}"
        [ "$iface" = lo ] && continue
        /bin/busybox udhcpc -i "$iface" -b -q -t 3 -T 2 >/dev/null 2>&1 || true
    done
fi
echo "[VANTOR] Minimal userspace is ready."
""", 0o755)
    write(output / "usr/bin/vantor-live-session", """#!/bin/sh
# Local Live console session; the root account remains locked.
exec /bin/busybox su -s /bin/sh - live
""", 0o755)
    write(output / "etc/profile", """# VANTOR shell defaults
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
export EDITOR=vi
export PAGER=more
: "${TERM:=vt100}"
export TERM
umask 022
if [ -r /etc/motd ]; then cat /etc/motd; fi
if [ -d /etc/profile.d ]; then
    for profile_script in /etc/profile.d/*.sh; do
        [ -r "$profile_script" ] && . "$profile_script"
    done
fi
""")
    write(output / "etc/hostname", "vantor\n")
    write(output / "etc/issue", "\n\nVANTOR Linux \\r (\\l)\nONE SYSTEM. EVERY GENERATION.\n\n")
    write(output / "etc/motd", "Welcome to VANTOR Linux Genesis.\nONE SYSTEM. EVERY GENERATION.\n\nIndependent origin. Independent base. Universal goal.\n")
    write(output / "etc/profile.d/vantor.sh", """# VANTOR interactive shell identity
if [ -n "$PS1" ]; then
    PS1='\\[\\033[1;36m\\]vantor\\[\\033[0m\\] \\[\\033[1;34m\\]\\w\\[\\033[0m\\] $ '
fi
""")

    write(output / "init", """#!/bin/sh
# VANTOR initramfs entry point: Live boot or switch to installed root.
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
mount -t proc proc /proc 2>/dev/null || true
mount -t sysfs sysfs /sys 2>/dev/null || true
mount -t devtmpfs devtmpfs /dev 2>/dev/null || true
/bin/busybox mdev -s 2>/dev/null || true

rootdev=""
rootfstype=""
for arg in $(cat /proc/cmdline 2>/dev/null); do
    case "$arg" in
        root=/dev/*) rootdev="${arg#root=}";;
        rootfstype=*) rootfstype="${arg#rootfstype=}";;
    esac
done

if [ -n "$rootdev" ]; then
    mkdir -p /newroot
    mounted=0
    if [ -n "$rootfstype" ]; then
        mount -t "$rootfstype" -o rw "$rootdev" /newroot && mounted=1
    else
        for fs in ext4 ext3 ext2; do
            mount -t "$fs" -o rw "$rootdev" /newroot && { rootfstype="$fs"; mounted=1; break; }
        done
    fi
    if [ "$mounted" -eq 1 ] && [ -x /newroot/sbin/init ]; then
        mkdir -p /newroot/dev /newroot/proc /newroot/sys /newroot/run
        mount -o move /dev /newroot/dev 2>/dev/null || true
        mount -o move /proc /newroot/proc 2>/dev/null || true
        mount -o move /sys /newroot/sys 2>/dev/null || true
        exec /bin/busybox switch_root /newroot /sbin/init
    fi
    echo "[VANTOR] Could not mount installed root $rootdev ($rootfstype)."
    exec /bin/sh
fi

if [ -x /sbin/vantor-init ]; then
    exec /sbin/vantor-init "$@"
fi
echo "[VANTOR] FATAL: /sbin/vantor-init is missing."
exec /bin/sh
""", 0o755)

    write(output / "sbin/vantor-init", """#!/bin/sh
# VANTOR Init 0.1.0 - minimal early-userspace orchestrator.
set -u
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
VERSION="0.1.0"
log() { echo "[VANTOR:init] $*"; }

mount_virtual_fs() {
    target="$1"; fstype="$2"; source="$3"
    mkdir -p "$target"
    if ! grep -q " $target " /proc/mounts 2>/dev/null; then
        mount -t "$fstype" "$source" "$target" 2>/dev/null || log "NOTICE: could not mount $fstype on $target"
    fi
}

if [ "${1:-}" = "--version" ]; then
    echo "VANTOR Init $VERSION"
    exit 0
fi
if [ "$$" -ne 1 ]; then log "NOTICE: running as PID $$; PID 1 is recommended."; fi

log "Starting VANTOR Linux Minimal..."
mkdir -p /proc /sys /dev /run /tmp
mount_virtual_fs /proc proc proc
mount_virtual_fs /sys sysfs sysfs
mount_virtual_fs /dev devtmpfs devtmpfs
chmod 1777 /tmp 2>/dev/null || true
hostname vantor 2>/dev/null || true

if [ -x /bin/busybox ]; then /bin/busybox --install -s /bin 2>/dev/null || true; fi
log "Kernel: $(uname -r 2>/dev/null || echo unknown)"
log "Userspace initialization complete."

if [ -x /sbin/init ]; then
    log "Handing control to /sbin/init."
    exec /sbin/init
fi
log "No system init is installed; entering emergency shell."
exec /bin/sh
""", 0o755)

    write(output / "usr/bin/vantorctl", """#!/bin/sh
# VANTOR Control 0.1.0 - read-only system diagnostics.
set -u
VERSION="0.1.0"
usage() {
    echo "VANTOR Control $VERSION"
    echo "Usage: vantorctl {help|version|info|hardware|network|status}"
}
case "${1:-help}" in
    help|-h|--help) usage ;;
    version|--version) echo "VANTOR Control $VERSION" ;;
    info) [ -r /etc/os-release ] && cat /etc/os-release ;;
    hardware) exec /usr/bin/vantor-hw ;;
    network)
        echo "== Network interfaces =="
        if [ -d /sys/class/net ]; then
            for iface in /sys/class/net/*; do
                [ -e "$iface" ] || continue
                name="${iface##*/}"; state="unknown"
                [ -r "$iface/operstate" ] && state="$(cat "$iface/operstate")"
                echo "$name: $state"
            done
        else echo "Network interface information unavailable"; fi
        echo "Diagnostic only: no network settings are changed."
        ;;
    status)
        echo "== VANTOR =="; [ -r /etc/vantor-release ] && cat /etc/vantor-release
        echo "Kernel: $(uname -r 2>/dev/null || echo unknown)"
        echo "Init PID: $(cat /proc/1/comm 2>/dev/null || echo unavailable)"
        echo "Uptime: $(cut -d ' ' -f 1 /proc/uptime 2>/dev/null || echo unavailable)"
        ;;
    *) usage >&2; exit 2 ;;
esac
""", 0o755)

    hardware_tool = ROOT / "core/hardware/vantor-hw"
    shutil.copy2(hardware_tool, output / "usr/bin/vantor-hw")
    (output / "usr/bin/vantor-hw").chmod(0o755)

    installer = ROOT / "installer/vantor-install"
    shutil.copy2(installer, output / "usr/bin/vantor-install")
    (output / "usr/bin/vantor-install").chmod(0o755)

    nyan_catalog = ROOT / "packages/catalog.tsv"
    (output / "usr/share/nyan").mkdir(parents=True, exist_ok=True)
    shutil.copy2(nyan_catalog, output / "usr/share/nyan/catalog.tsv")

    # Nyan is the native package manager and is available in the first boot image.
    nyan_client = ROOT / "packages/nyan/nyan"
    shutil.copy2(nyan_client, output / "usr/bin/nyan")
    (output / "usr/bin/nyan").chmod(0o755)
    nyan_config = """# Nyan package repository configuration
: "${NYAN_REPO:=https://vantor-linux.cristopheriguaran-7.workers.dev}"
: "${NYAN_ARCH:=ARCH_PLACEHOLDER}"
""".replace("ARCH_PLACEHOLDER", args.arch)
    write(output / "etc/nyan.conf", nyan_config)

    write(output / "etc/vantor-brand.json", json.dumps({
        "brand": theme["brand"], "edition": "Minimal", "architecture": args.arch, "version": "0.1.0", "codename": "Genesis",
        "slogan": theme["slogan"], "branding_path": "/usr/share/vantor/branding",
        "core": {"init": "VANTOR Init 0.1.0", "control": "VANTOR Control 0.1.0", "hardware": "VANTOR Hardware 0.1.0"}
    }, indent=2) + "\n")
    print(f"[OK] Prepared VANTOR {args.arch} rootfs skeleton at {output}")
    print(f"[OK] Installed {len(BRAND_FILES)} official branding assets.")
    print("[OK] Added VANTOR Init, Control, Hardware, Nyan and TUI installer.")
    print("[OK] Added root and live accounts, wheel group and locked-password sudo policy.")
    print("[INFO] Full service supervision and network configuration are not implemented yet.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
