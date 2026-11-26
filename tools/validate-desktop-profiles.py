#!/usr/bin/env python3
"""Validate VANTOR desktop profile manifests against the Nyan package catalog."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "desktop/profiles"
CATALOG = ROOT / "packages/catalog.tsv"
ALLOWED = {
    "android-termux": {"platform": "android", "architecture": "aarch64", "mode": "virtual-display", "display": "tigervnc"},
    "pc": {"platform": "linux", "architecture": "x86_64", "mode": "native-display", "display": "xorg"},
    "remote": {"platform": "linux", "architecture": "any", "mode": "remote-access", "display": "remote"},
}
REQUIRED_KEYS = {"name", "platform", "architecture", "session", "display", "mode", "required", "optional", "notes"}


def fail(message: str) -> None:
    raise SystemExit(f"desktop profile validation: {message}")


def main() -> int:
    rows = {}
    for line in CATALOG.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) != 4:
            fail(f"malformed catalog row: {line}")
        rows[fields[0]] = fields[2]

    seen = set()
    for path in sorted(PROFILE_DIR.glob("*/PROFILE")):
        values = {}
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                fail(f"{path}: expected key=value, got {line!r}")
            key, value = line.split("=", 1)
            if key in values:
                fail(f"{path}: duplicate key {key}")
            values[key] = value
        missing = REQUIRED_KEYS - values.keys()
        if missing:
            fail(f"{path}: missing keys {', '.join(sorted(missing))}")
        name = values["name"]
        if name in seen or name != path.parent.name:
            fail(f"{path}: duplicate or mismatched profile name {name!r}")
        seen.add(name)
        if name not in ALLOWED:
            fail(f"{path}: profile is not in the supported manifest policy")
        for key, expected in ALLOWED[name].items():
            if values[key] != expected:
                fail(f"{path}: {key} must be {expected!r}")
        packages = []
        for key in ("required", "optional"):
            entries = [item.strip() for item in values[key].split(",") if item.strip()]
            if len(entries) != len(set(entries)):
                fail(f"{path}: duplicate package in {key}")
            packages.extend(entries)
        if not values["required"]:
            fail(f"{path}: required package list cannot be empty")
        unknown = sorted(set(packages) - rows.keys())
        if unknown:
            fail(f"{path}: packages missing from Nyan catalog: {', '.join(unknown)}")
        if any(rows[pkg] != "planned" for pkg in packages):
            fail(f"{path}: profile packages must remain planned until real archives are published")
        if name == "android-termux" and "xorg-server" in packages:
            fail(f"{path}: Android virtual-display profile must not depend on native Xorg")
        if name == "pc" and "tigervnc" in values["required"].split(","):
            fail(f"{path}: TigerVNC must remain optional for native PC desktop")
        if name == "remote" and values["session"] != "none":
            fail(f"{path}: remote-only profile must not select a local desktop session")
        print(f"validated {name}: {len(packages)} catalog packages (not yet installable)")
    if seen != set(ALLOWED):
        fail(f"missing profile manifests: {', '.join(sorted(set(ALLOWED) - seen))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
