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
PRETTY_NAME="VANTOR Linux Genesis 0.1.0"
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
    write(output / "etc/hostname", "vantor\n")
    write(output / "etc/issue", "\n\nVANTOR Linux \\r (\\l)\nONE SYSTEM. EVERY GENERATION.\n\n")
    write(output / "etc/motd", "Welcome to VANTOR Linux Genesis.\nONE SYSTEM. EVERY GENERATION.\n\nIndependent origin. Independent base. Universal goal.\n")
    write(output / "etc/profile.d/vantor.sh", """# VANTOR interactive shell identity
if [ -n "$PS1" ]; then
    PS1='\\[\\033[1;36m\\]vantor\\[\\033[0m\\] \\[\\033[1;34m\\]\\w\\[\\033[0m\\] $ '
fi
""")

    write(output / "init", """#!/bin/sh
# First-stage entry point for VANTOR early userspace.
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
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

log "Starting VANTOR Linux Genesis..."
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

    # Nyan is the native package manager and is available in the first boot image.
    nyan_client = ROOT / "packages/nyan/nyan"
    shutil.copy2(nyan_client, output / "usr/bin/nyan")
    (output / "usr/bin/nyan").chmod(0o755)
    write(output / "etc/nyan.conf", """# Nyan package repository configuration
: "${NYAN_REPO:=https://vantor-linux.cristopheriguaran-7.workers.dev}"
: "${NYAN_ARCH:=x86_64}"
""")

    write(output / "etc/vantor-brand.json", json.dumps({
        "brand": theme["brand"], "version": "0.1.0", "codename": "Genesis",
        "slogan": theme["slogan"], "branding_path": "/usr/share/vantor/branding",
        "core": {"init": "VANTOR Init 0.1.0", "control": "VANTOR Control 0.1.0", "hardware": "VANTOR Hardware 0.1.0"}
    }, indent=2) + "\n")
    print(f"[OK] Prepared VANTOR rootfs skeleton at {output}")
    print(f"[OK] Installed {len(BRAND_FILES)} official branding assets.")
    print("[OK] Added VANTOR Init, Control, Hardware inventory and Nyan package manager.")
    print("[INFO] Full service supervision and network configuration are not implemented yet.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
