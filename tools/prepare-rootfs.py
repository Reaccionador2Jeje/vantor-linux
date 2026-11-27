#!/usr/bin/env python3
"""Assemble a deterministic VANTOR rootfs skeleton with its official identity."""
from __future__ import annotations
import argparse, json, shutil, subprocess
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
    parser.add_argument("--arch", choices=("x86_64", "i486", "aarch64"), default="x86_64")
    args = parser.parse_args()
    output = args.output.resolve()
    if output == Path("/") or output == ROOT or output == ROOT / "rootfs":
        parser.error("refusing unsafe output directory")
    if output.exists() and any(output.iterdir()):
        parser.error(f"output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    # Standard mount points and writable FHS directories must exist before
    # the installer or init scripts try to use them.
    for directory in (
        "mnt", "media", "opt", "srv", "proc", "sys", "dev", "run",
        "run/lock", "tmp", "var/cache", "var/lib", "var/log",
        "var/spool", "var/tmp",
    ):
        (output / directory).mkdir(parents=True, exist_ok=True)
    (output / "tmp").chmod(0o1777)
    (output / "var/tmp").chmod(0o1777)

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
live:$6$VANTORlive$zCoOwgB64aI0dEmx47Fy12NjvDzSi48K2f6/S4OYWqVNJopzkYD/FXHHPu/s5m2Mrfrrfsi1D3Wq5xzhrcUFR1:19000:0:99999:7:::
""", 0o600)
    write(output / "etc/gshadow", """root:!::
wheel:!::live
users:!::
""", 0o600)
    write(output / "etc/sudoers", """# VANTOR Minimal sudo policy
# The Live account uses its existing password in Live and installed systems.
# Its sudo policy requires password authentication and is retained by the installer.
Defaults secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
#includedir /etc/sudoers.d
""", 0o440)
    # Preserve the conventional root sudo rule for root-shell compatibility.
    write(output / "etc/sudoers.d/00-root", "root ALL=(ALL:ALL) ALL\n", 0o440)
    write(output / "etc/sudoers.d/99-live", "live ALL=(ALL:ALL) ALL\n", 0o440)
    write(output / "etc/sudoers.d/10-wheel", "%wheel ALL=(ALL:ALL) ALL\n", 0o440)
    (output / "run/sudo").mkdir(parents=True, exist_ok=True)
    (output / "run/sudo").chmod(0o700)
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
    # The x86_64 image gets a tiny static fbdev renderer. Legacy remains text-only.
    if args.arch == "x86_64":
        splash_source = ROOT / "core/boot/vantor-fb-splash.c"
        splash_binary = output / "usr/bin/vantor-fb-splash"
        splash_binary.parent.mkdir(parents=True, exist_ok=True)
        compiler = shutil.which("cc")
        if compiler and splash_source.is_file():
            try:
                subprocess.run(
                    [compiler, "-static", "-Os", "-s", "-Wl,--build-id=none",
                     "-o", str(splash_binary), str(splash_source), "-lm"],
                    check=True, capture_output=True, text=True,
                )
                splash_binary.chmod(0o755)
            except (subprocess.CalledProcessError, OSError) as exc:
                splash_binary.unlink(missing_ok=True)
                print(f"[WARN] Static framebuffer splash unavailable; using text splash: {exc}")
                print(exc.stderr or exc.stdout or "no compiler diagnostics")
        else:
            print("[WARN] C compiler unavailable; using VANTOR text splash.")

    write(output / "usr/bin/vantor-splash", """#!/bin/sh
# VANTOR Genesis splash: framebuffer renderer first, ANSI console fallback.
set -u
[ -r /proc/cmdline ] || exit 0
case " $(cat /proc/cmdline) " in *" nosplash "*) exit 0;; esac
TTY=/dev/tty0
if [ -x /usr/bin/vantor-fb-splash ] && [ -c /dev/fb0 ]; then
    if /usr/bin/vantor-fb-splash "$@"; then
        [ "${1:-}" != finish ] || printf '\\033[?25h\\033[0m' > "$TTY" 2>/dev/null || true
        exit 0
    fi
fi
[ -w "$TTY" ] || exit 0
emit() { printf '%b' "$1" > "$TTY"; }
case "${1:-start}" in
    start)
        emit '\033[?25l\033[2J\033[H\033[48;2;7;19;33m'
        emit '\033[36m'
        emit '                         .-=================-.\n'
        emit '                    .-==   V A N T O R   ==-.\n'
        emit '                   /       / V \\       \\\n'
        emit '                  /_______/     \\_______\\\n'
        emit '                  \\       \\     /       /\n'
        emit '                   \\_______\\___/_______/\n'
        emit '\033[0m\n'
        emit '\033[1;97m                    VANTOR LINUX\033[0m\n'
        emit '\033[36m          ONE SYSTEM. EVERY GENERATION.\033[0m\n\n'
        emit '\033[90m                 INDEPENDENT • UNIVERSAL\033[0m\n\n'
        emit '\033[38;2;0;207;255m                 Initializing Genesis...\033[0m\n'
        ;;
    step)
        emit "\033[38;2;155;176;200m                 [VANTOR] $2\033[0m\n"
        ;;
    finish)
        emit '\033[?25h\033[0m\033[2J\033[H'
        ;;
    *) exit 2;;
esac
""", 0o755)

    write(output / "etc/modules", """# VANTOR preferred optional modules; built-in drivers are harmlessly skipped.
virtio_pci
virtio_blk
virtio_net
virtio_scsi
e1000
e1000e
ata_piix
ahci
sd_mod
sr_mod
cdrom
usb_storage
xhci_pci
ehci_pci
ohci_pci
ext2
ext4
isofs
fat
vfat
nls_cp437
nls_iso8859-1
""")
    write(output / "usr/sbin/vantor-modules", """#!/bin/sh
# Load optional kernel modules listed in /etc/modules.
set -u
[ -r /etc/modules ] || exit 0
if ! command -v modprobe >/dev/null 2>&1; then
    echo "[VANTOR] modprobe unavailable; using built-in kernel drivers."
    exit 0
fi
while IFS= read -r module || [ -n "$module" ]; do
    case "$module" in ""|\\#*) continue ;; esac
    if modprobe "$module" 2>/dev/null; then
        echo "[VANTOR] Loaded module: $module"
    fi
done < /etc/modules
exit 0
""", 0o755)

    write(output / "usr/sbin/vantor-network", """#!/bin/sh
# VANTOR Network: safe configuration parser and DHCP/static IPv4 setup.
set -u
PATH=/bin:/sbin:/usr/bin:/usr/sbin
CONFIG=/etc/vantor/network.conf
MODE=dhcp
INTERFACE=""
ADDRESS=""
GATEWAY=""
DNS=""
valid_iface() { case "$1" in ''|*[!A-Za-z0-9_.:-]*) return 1;; esac; [ "${#1}" -le 15 ]; }
valid_ipv4() {
    printf '%s\\n' "$1" | awk -F. 'NF==4 { for(i=1;i<=4;i++) if($i !~ /^[0-9]+$/ || $i>255) exit 1; exit 0 } { exit 1 }'
}
load_config() {
    [ -r "$CONFIG" ] || return 0
    while IFS='=' read -r key value || [ -n "$key$value" ]; do
        case "$key" in
            MODE) MODE=$value;;
            INTERFACE) INTERFACE=$value;;
            ADDRESS) ADDRESS=$value;;
            GATEWAY) GATEWAY=$value;;
            DNS) DNS=$value;;
            ''|'#'*) ;;
            *) echo "[VANTOR:network] Ignoring unknown setting: $key";;
        esac
    done < "$CONFIG"
}
start_dhcp() {
    iface=$1
    valid_iface "$iface" || { echo "[VANTOR:network] Invalid interface name."; return 1; }
    ip link set "$iface" up 2>/dev/null || true
    udhcpc -i "$iface" -s /usr/share/udhcpc/default.script -p "/run/udhcpc.$iface.pid" -b -q -t 4 -T 2
}
load_config
if ! command -v ip >/dev/null 2>&1 || ! command -v udhcpc >/dev/null 2>&1; then
    echo "[VANTOR:network] BusyBox ip/udhcpc is unavailable."
    exit 0
fi
if [ -n "$INTERFACE" ]; then
    valid_iface "$INTERFACE" || { echo "[VANTOR:network] Invalid configured interface."; exit 1; }
    case "$MODE" in
        dhcp) start_dhcp "$INTERFACE" || true;;
        static)
            case "$ADDRESS" in */*) ;; *) echo "[VANTOR:network] Static address needs a prefix."; exit 1;; esac
            address=${ADDRESS%/*}; prefix=${ADDRESS#*/}
            valid_ipv4 "$address" && case "$prefix" in ''|*[!0-9]*) false;; *) [ "$prefix" -ge 1 ] && [ "$prefix" -le 32 ];; esac || { echo "[VANTOR:network] Invalid static address."; exit 1; }
            valid_ipv4 "$GATEWAY" && valid_ipv4 "$DNS" || { echo "[VANTOR:network] Invalid gateway or DNS address."; exit 1; }
            ip link set "$INTERFACE" up || exit 1
            ip addr replace "$ADDRESS" dev "$INTERFACE" || exit 1
            ip route replace default via "$GATEWAY" dev "$INTERFACE" || true
            printf 'nameserver %s\\n' "$DNS" > /etc/resolv.conf
            ;;
        *) echo "[VANTOR:network] Unknown network mode: $MODE"; exit 1;;
    esac
else
    # Automatic discovery supports virtio, e1000 and legacy PC NIC names.
    found=0
    for iface_path in /sys/class/net/*; do
        [ -e "$iface_path" ] || continue
        iface=${iface_path##*/}
        [ "$iface" = lo ] && continue
        found=1
        start_dhcp "$iface" || true
    done
    [ "$found" -eq 1 ] || echo "[VANTOR:network] No network interfaces detected."
fi
exit 0
""", 0o755)

    write(output / "usr/sbin/vantor-service", """#!/bin/sh
# VANTOR Service Control delegates lifecycle operations to OpenRC.
set -eu
PATH=/bin:/sbin:/usr/bin:/usr/sbin
action=${1:-list}
usage() { echo "Usage: vantor-service {list|start|stop|restart|status|enable|disable|runlevels|logs} [SERVICE] [RUNLEVEL]"; }
case "$action" in
    list) exec rc-status -a ;;
    start|stop|restart|status)
        shift
        [ "$#" -ge 1 ] || { usage >&2; exit 2; }
        exec rc-service "$@"
        ;;
    enable|disable)
        shift
        [ "$#" -ge 1 ] || { usage >&2; exit 2; }
        service=$1
        runlevel=${2:-default}
        if [ "$action" = enable ]; then exec rc-update add "$service" "$runlevel"; fi
        exec rc-update del "$service" "$runlevel"
        ;;
    runlevels) exec rc-status -r ;;
    logs)
        [ -r /var/log/rc.log ] || { echo "OpenRC log is not available."; exit 1; }
        if [ "${2:-}" = follow ]; then exec tail -f /var/log/rc.log; else exec cat /var/log/rc.log; fi
        ;;
    *) usage >&2; exit 2 ;;
esac
""", 0o755)

    (output / "etc/vantor/services").mkdir(parents=True, exist_ok=True)
    (output / "etc/vantor/services").chmod(0o755)

    write(output / "etc/init.d/rcS", """#!/bin/sh
# Compatibility stub only. OpenRC owns normal startup and shutdown.
echo "[VANTOR] Legacy rcS hook is disabled; OpenRC runlevels manage services."
exit 0
""", 0o755)
    write(output / "usr/share/udhcpc/default.script", """#!/bin/sh
# Minimal BusyBox udhcpc hook for VANTOR.
case "$1" in
    deconfig)
        ip addr flush dev "$interface" 2>/dev/null || true
        ;;
    bound|renew)
        prefix=$(printf '%s\\n' "$subnet" | awk -F. 'NF==4 { n=0; zero=0; for(i=1;i<=4;i++){ v=$i; for(b=0;b<8;b++){ bit=int(v/128); if(bit){ if(zero) exit 1; n++; v-=128 } else zero=1; v*=2 } } print n }')
        [ -n "$prefix" ] || prefix=24
        ip link set "$interface" up 2>/dev/null || true
        ip addr replace "$ip/$prefix" dev "$interface" 2>/dev/null || true
        if [ -n "$router" ]; then
            set -- $router
            ip route replace default via "$1" dev "$interface" 2>/dev/null || true
        fi
        : > /etc/resolv.conf
        for server in $dns; do printf 'nameserver %s\\n' "$server" >> /etc/resolv.conf; done
        ;;
esac
exit 0
""", 0o755)

    write(output / "usr/bin/vantor-live-session", """#!/bin/sh
# The Live getty launches this program as root with -n (no password login).
# Keep the Live console administrative so Nyan and the installer work out of
# the box. The installed system is configured with an ordinary unprivileged user.
exec /bin/sh -l
""", 0o755)
    write(output / "etc/profile", """# VANTOR shell defaults
export PATH=/usr/local/sbin:/usr/local/bin:/bin:/sbin:/usr/bin:/usr/sbin
export EDITOR=vi
export PAGER=more
: "${TERM:=vt100}"
export TERM
umask 022
if [ -r /etc/locale.conf ]; then . /etc/locale.conf; export LANG LC_ALL; fi
if [ -r /etc/timezone ]; then TZ=$(cat /etc/timezone); export TZ; fi
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
mount -t tmpfs -o mode=0755,nosuid tmpfs /run 2>/dev/null || true
/bin/busybox mdev -s 2>/dev/null || true
# Load storage and filesystem drivers before looking for an installed root.
[ ! -x /usr/sbin/vantor-modules ] || /usr/sbin/vantor-modules

rootdev=""
rootfstype=""
for arg in $(cat /proc/cmdline 2>/dev/null); do
    case "$arg" in
        root=/dev/*) rootdev="${arg#root=}";;
        rootfstype=*) rootfstype="${arg#rootfstype=}";;
    esac
done

if [ -n "$rootdev" ]; then
    # rootwait is bounded so a missing disk cannot hang the machine forever.
    waited=0
    while [ ! -b "$rootdev" ] && [ "$waited" -lt 20 ]; do
        sleep 1
        waited=$((waited + 1))
        /bin/busybox mdev -s 2>/dev/null || true
    done
    mkdir -p /newroot
    mounted=0
    if [ -n "$rootfstype" ]; then
        mount -t "$rootfstype" -o rw "$rootdev" /newroot && mounted=1
    else
        for fs in ext4 ext2; do
            mount -t "$fs" -o rw "$rootdev" /newroot && { rootfstype="$fs"; mounted=1; break; }
        done
    fi
    if [ "$mounted" -eq 1 ] && [ -x /newroot/sbin/vantor-init ]; then
        mkdir -p /newroot/dev /newroot/proc /newroot/sys /newroot/run
        mount -o move /dev /newroot/dev 2>/dev/null || true
        mount -o move /proc /newroot/proc 2>/dev/null || true
        mount -o move /sys /newroot/sys 2>/dev/null || true
        mount -o move /run /newroot/run 2>/dev/null || true
        exec /bin/busybox switch_root /newroot /sbin/vantor-init
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
# VANTOR Init 0.2.0 - minimal early-userspace orchestrator.
set -u
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
VERSION="0.2.0"
log() { echo "[VANTOR:init] $*"; }
RECOVERY_MODE=0
for boot_arg in $(cat /proc/cmdline 2>/dev/null); do
    case "$boot_arg" in vantor.recovery|recovery|single) RECOVERY_MODE=1 ;; esac
done
if [ "$RECOVERY_MODE" -eq 1 ]; then
    log "Recovery mode: OpenRC will start the nonetwork runlevel."
fi

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
mount_virtual_fs /run tmpfs tmpfs
chmod 1777 /tmp 2>/dev/null || true
hostname vantor 2>/dev/null || true

if [ -x /bin/busybox ]; then /bin/busybox --install -s /bin 2>/dev/null || true; fi
log "Kernel: $(uname -r 2>/dev/null || echo unknown)"
log "Userspace initialization complete."

if [ -x /sbin/init ]; then
    if [ "$RECOVERY_MODE" -eq 1 ]; then
        log "Handing control to OpenRC nonetwork runlevel."
        exec /sbin/init nonetwork
    fi
    log "Handing control to OpenRC default runlevel."
    exec /sbin/init
fi
log "No system init is installed; entering emergency shell."
exec /bin/sh
""", 0o755)

    # The init symlink is explicit: both Live and installed boots enter BusyBox init.
    init_link = output / "sbin/init"
    if init_link.exists() or init_link.is_symlink():
        init_link.unlink()
    init_link.symlink_to("/sbin/openrc-init")

    write(output / "usr/sbin/vantor-storage", """#!/bin/sh
# VANTOR Storage: non-destructive block/filesystem inspection and fstab mounting.
set -u
PATH=/bin:/sbin:/usr/bin:/usr/sbin
action=${1:-status}
case "$action" in
    scan|status)
        echo "VANTOR STORAGE INVENTORY"
        if [ -d /sys/class/block ]; then
            for device in /sys/class/block/*; do
                [ -e "$device" ] || continue
                name=${device##*/}
                sectors=unknown
                [ -r "$device/size" ] && IFS= read -r sectors < "$device/size"
                model=unknown
                [ -r "$device/device/model" ] && IFS= read -r model < "$device/device/model"
                printf '%s sectors=%s model=%s\\n' "$name" "$sectors" "$model"
            done
        else
            echo "Block device inventory unavailable (sysfs not mounted)."
        fi
        echo
        echo "Mounted filesystems:"
        cat /proc/mounts 2>/dev/null || true
        ;;
    filesystems)
        echo "Kernel filesystem support:"
        cat /proc/filesystems 2>/dev/null || echo "procfs unavailable"
        ;;
    removable)
        echo "Removable block devices (read-only inventory):"
        found=0
        for entry in /sys/class/block/*; do
            [ -e "$entry" ] || continue
            name=${entry##*/}
            removable=0
            if [ -r "$entry/removable" ]; then
                IFS= read -r removable < "$entry/removable"
            elif [ -r "$entry/../removable" ]; then
                IFS= read -r removable < "$entry/../removable"
            fi
            [ "$removable" = 1 ] || continue
            found=1
            printf '/dev/%s\\n' "$name"
        done
        [ "$found" -eq 1 ] || echo "No removable block devices detected."
        ;;
    mount-removable)
        device=${2:-}; fstype=${3:-}
        case "$device" in /dev/*) ;; *) echo "device must be under /dev" >&2; exit 2;; esac
        [ -b "$device" ] || { echo "device is not a block device" >&2; exit 2; }
        name=${device##*/}
        entry="/sys/class/block/$name"
        [ -e "$entry" ] || { echo "device is not represented in sysfs" >&2; exit 2; }
        removable=0
        if [ -r "$entry/removable" ]; then
            IFS= read -r removable < "$entry/removable"
        elif [ -r "$entry/../removable" ]; then
            IFS= read -r removable < "$entry/../removable"
        fi
        [ "$removable" = 1 ] || { echo "refusing: device is not marked removable" >&2; exit 2; }
        case "$fstype" in ext2|ext3|ext4|vfat|exfat|ntfs|iso9660) ;; *) echo "unsupported filesystem type" >&2; exit 2;; esac
        target="/media/$name"
        mkdir -p "$target" || exit 1
        [ ! -L "$target" ] || { echo "mount point must not be a symlink" >&2; exit 2; }
        if awk -v path="$target" '$2 == path { found=1 } END { exit !found }' /proc/mounts; then
            echo "mount point is already in use" >&2; exit 2
        fi
        echo "Mounting removable media read-only at $target."
        exec mount -t "$fstype" -o ro,nosuid,nodev,noexec "$device" "$target"
        ;;
    umount-removable)
        device=${2:-}
        case "$device" in /dev/*) ;; *) echo "device must be under /dev" >&2; exit 2;; esac
        name=${device##*/}
        target="/media/$name"
        if ! awk -v path="$target" '$2 == path { found=1 } END { exit !found }' /proc/mounts; then
            echo "removable device is not mounted at $target" >&2; exit 2
        fi
        exec umount "$target"
        ;;
    mount)
        device=${2:-}; target=${3:-}; fstype=${4:-}
        case "$device" in /dev/*) ;; *) echo "device must be under /dev" >&2; exit 2;; esac
        [ -b "$device" ] || { echo "device is not a block device" >&2; exit 2; }
        case "$target" in /*) ;; *) echo "mount point must be absolute" >&2; exit 2;; esac
        [ "$target" != "/" ] || { echo "refusing to mount over /" >&2; exit 2; }
        case "$fstype" in ext2|ext3|ext4|vfat|exfat|ntfs|iso9660) ;; *) echo "unsupported filesystem type" >&2; exit 2;; esac
        mkdir -p "$target" || exit 1
        [ ! -L "$target" ] || { echo "mount point must not be a symlink" >&2; exit 2; }
        if awk -v path="$target" '$2 == path { found=1 } END { exit !found }' /proc/mounts; then
            echo "mount point is already in use" >&2; exit 2
        fi
        exec mount -t "$fstype" -o nosuid,nodev "$device" "$target"
        ;;
    umount|unmount)
        target=${2:-}
        case "$target" in /*) ;; *) echo "mount point must be absolute" >&2; exit 2;; esac
        [ "$target" != "/" ] || { echo "refusing to unmount /" >&2; exit 2; }
        if ! awk -v path="$target" '$2 == path { found=1 } END { exit !found }' /proc/mounts; then
            echo "mount point is not mounted" >&2; exit 2
        fi
        exec umount "$target"
        ;;
    fstab-check)
        [ -r /etc/fstab ] || { echo "/etc/fstab is missing" >&2; exit 1; }
        awk 'BEGIN { ok=1 } /^[[:space:]]*#/ || /^[[:space:]]*$/ { next } NF < 4 { printf "invalid fstab line %d\\n", NR; ok=0 } END { if (ok) print "/etc/fstab syntax looks valid"; exit !ok }' /etc/fstab
        ;;
    mount-all)
        echo "Mounting configured filesystems from /etc/fstab (no formatting or partition changes)."
        exec mount -a
        ;;
    *)
        echo "Usage: vantor-storage {scan|status|filesystems|removable|mount-removable DEVICE FSTYPE|umount-removable DEVICE|mount DEVICE TARGET FSTYPE|umount TARGET|fstab-check|mount-all}" >&2
        exit 2
        ;;
esac
""", 0o755)

    write(output / "usr/bin/vantorctl", """#!/bin/sh
# VANTOR Control 0.1.0 - read-only system diagnostics.
set -u
VERSION="0.1.0"
usage() {
    echo "VANTOR Control $VERSION"
    echo "Usage: vantorctl {help|version|info|hardware|network|storage|service|doctor|recovery|logs|status}"
}
case "${1:-help}" in
    help|-h|--help) usage ;;
    version|--version) echo "VANTOR Control $VERSION" ;;
    info) [ -r /etc/os-release ] && cat /etc/os-release ;;
    hardware) exec /usr/bin/vantor-hw ;;
    storage) shift; if [ "$#" -gt 0 ]; then exec /usr/sbin/vantor-storage "$@"; else exec /usr/sbin/vantor-storage status; fi ;;\n    service) shift; exec /usr/sbin/vantor-service "$@" ;;
    doctor) exec /usr/bin/vantor-doctor "$@" ;;
    recovery)
        recovery=0
        for boot_arg in $(cat /proc/cmdline 2>/dev/null); do
            case "$boot_arg" in vantor.recovery|recovery|single) recovery=1;; esac
        done
        if [ "$recovery" -eq 1 ]; then
            echo "VANTOR recovery mode: ACTIVE"
            echo "Automatic fstab mounts, network setup and optional services were skipped."
        else
            echo "VANTOR recovery mode: inactive"
            echo "Add 'vantor.recovery' to the kernel command line and reboot to enter recovery mode."
        fi
        ;;
    logs)
        shift
        exec /usr/sbin/vantor-service logs "$@"
        ;;
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

    # VANTOR Doctor is part of the base system: diagnostics must work offline.
    write(output / "usr/bin/vantor-doctor", """#!/bin/sh
# VANTOR Doctor 0.2.0 — read-only base-system diagnostics.
set -u
PATH=/bin:/sbin:/usr/bin:/usr/sbin
fail=0
warn=0
ok() { printf '[ OK ] %s\\n' "$1"; }
check_file() {
    label=$1 path=$2
    if [ -e "$path" ]; then ok "$label"
    else printf '[FAIL] %s (missing: %s)\\n' "$label" "$path"; fail=$((fail + 1)); fi
}
check_mount() {
    label=$1 path=$2
    if grep -q "[[:space:]]$path[[:space:]]" /proc/mounts 2>/dev/null; then ok "$label mounted"
    else printf '[WARN] %s is not mounted\\n' "$label"; warn=$((warn + 1)); fi
}
echo "VANTOR Doctor 0.2.0 — read-only diagnostics"
echo "== Core =="
check_file "Kernel release" /proc/sys/kernel/osrelease
check_file "Memory information" /proc/meminfo
check_file "CPU information" /proc/cpuinfo
check_file "VANTOR release" /etc/vantor-release
check_file "VANTOR init handoff" /sbin/vantor-init
check_file "OpenRC PID 1" /sbin/openrc-init
check_file "OpenRC service command" /sbin/rc-service
check_file "BusyBox" /bin/busybox
check_file "Sudo privilege manager" /usr/bin/sudo
check_file "Sudo policy validator" /usr/bin/visudo
check_file "VANTOR control" /usr/bin/vantorctl
check_file "Nyan package manager" /usr/bin/nyan
echo "== Virtual filesystems =="
check_mount procfs /proc
check_mount sysfs /sys
check_mount devtmpfs /dev
check_mount tmpfs /run
echo "== User environment =="
if [ -n "${USER:-}" ] && [ -d "${HOME:-/nonexistent}" ]; then ok "User environment ($USER)"
else printf '[WARN] User or home environment is incomplete\\n'; warn=$((warn + 1)); fi
if [ -r /etc/nyan.conf ]; then ok "Nyan repository configuration"
else printf '[FAIL] Nyan repository configuration missing\\n'; fail=$((fail + 1)); fi
if [ -d /sys/class/net ]; then
    found=0
    for iface in /sys/class/net/*; do
        [ -e "$iface" ] || continue
        [ "${iface##*/}" = lo ] && continue
        found=1
    done
    if [ "$found" -eq 1 ]; then ok "Network interface detected"
    else printf '[WARN] No network interface detected\\n'; warn=$((warn + 1)); fi
fi
echo "== Result =="
if [ "$fail" -gt 0 ]; then
    printf 'FAILED: %s critical issue(s), %s warning(s). No changes made.\\n' "$fail" "$warn"
    exit 1
fi
printf 'PASSED: base system checks completed, %s warning(s). No changes made.\\n' "$warn"
exit 0
""", 0o755)

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
        "core": {"init": "OpenRC 0.64.1", "bootstrap": "VANTOR Init 0.2.0", "control": "VANTOR Control 0.1.0", "hardware": "VANTOR Hardware 0.1.0"}
    }, indent=2) + "\n")
    print(f"[OK] Prepared VANTOR {args.arch} rootfs skeleton at {output}")
    print(f"[OK] Installed {len(BRAND_FILES)} official branding assets.")
    print("[OK] Added VANTOR Init, Control, Hardware, Nyan and TUI installer.")
    print("[OK] Added root and live accounts, wheel group and password-authenticated sudo policy.")
    print("[INFO] OpenRC will provide PID 1 and service management after its pinned build step.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
