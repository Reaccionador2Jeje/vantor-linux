#!/usr/bin/env python3
"""Assemble a deterministic VANTOR rootfs skeleton with its official identity."""
from __future__ import annotations

import argparse
import json
import shutil
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

    os_release = """NAME="VANTOR Linux"
PRETTY_NAME="VANTOR Linux Genesis 0.1.0"
ID=vantor
ID_LIKE=linux
VERSION="0.1.0"
VERSION_ID="0.1.0"
VERSION_CODENAME=genesis
BUILD_ID=genesis
ANSI_COLOR="0;38;2;0;207;255"
HOME_URL="https://github.com/Reaccionador2Jeje/vantor-linux"
"""
    write(output / "etc/os-release", os_release)
    write(output / "etc/vantor-release", "VANTOR Linux 0.1.0 (Genesis)\\n")
    write(output / "etc/hostname", "vantor\\n")
    write(output / "etc/issue", "\\n\\nVANTOR Linux \\r (\\l)\\nONE SYSTEM. EVERY GENERATION.\\n\\n")
    write(output / "etc/motd", """
Welcome to VANTOR Linux Genesis.
ONE SYSTEM. EVERY GENERATION.

Independent origin. Independent base. Universal goal.
""".lstrip())
    profile = """# VANTOR interactive shell identity
if [ -n "$PS1" ]; then
    PS1='\\[\\033[1;36m\\]vantor\\[\\033[0m\\] \\[\\033[1;34m\\]\\w\\[\\033[0m\\] $ '
fi
"""
    write(output / "etc/profile.d/vantor.sh", profile)
    init = """#!/bin/sh
# Minimal early userspace entry point for VANTOR Genesis.
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
mount -t proc proc /proc 2>/dev/null || true
mount -t sysfs sysfs /sys 2>/dev/null || true
mount -t devtmpfs devtmpfs /dev 2>/dev/null || true
hostname vantor 2>/dev/null || true
echo
echo "VANTOR Linux Genesis 0.1.0"
echo "ONE SYSTEM. EVERY GENERATION."
echo
if [ -x /sbin/init ]; then
    exec /sbin/init
fi
echo "[VANTOR] /sbin/init is not installed yet; starting emergency shell."
exec /bin/sh
"""
    write(output / "init", init, 0o755)
    write(output / "etc/vantor-brand.json", json.dumps({
        "brand": theme["brand"],
        "version": "0.1.0",
        "codename": "Genesis",
        "slogan": theme["slogan"],
        "branding_path": "/usr/share/vantor/branding"
    }, indent=2) + "\\n")
    print(f"[OK] Prepared VANTOR rootfs skeleton at {output}")
    print(f"[OK] Installed {len(BRAND_FILES)} official branding assets.")
    print("[INFO] BusyBox, kernel modules and a bootable initramfs are not included yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
