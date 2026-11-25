#!/usr/bin/env python3
"""Validate community package submissions without executing package contents."""
import json
import re
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCOMING = ROOT / "incoming"
MAX_SIZE = 20 * 1024 * 1024
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9+_.-]{0,63}$")
VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9+_.+-]{0,63}$")
ARCHES = {"x86_64", "aarch64", "all"}
errors = []
archives = sorted(INCOMING.glob("*/*.tar.gz")) if INCOMING.exists() else []
for archive in archives:
    arch_dir = archive.parent.name
    stem = archive.name[:-7]
    metadata_path = archive.with_name(stem + ".json")
    if arch_dir not in ARCHES:
        errors.append(f"{archive}: unsupported architecture directory")
        continue
    if not metadata_path.is_file():
        errors.append(f"{archive}: missing matching JSON metadata")
        continue
    if archive.stat().st_size > MAX_SIZE:
        errors.append(f"{archive}: exceeds 20 MiB limit")
        continue
    try:
        meta = json.loads(metadata_path.read_text(encoding="utf-8"))
        name, version, arch, description = (meta[k] for k in ("name", "version", "architecture", "description"))
        if not isinstance(name, str) or not NAME.fullmatch(name):
            raise ValueError("invalid package name")
        if not isinstance(version, str) or not VERSION.fullmatch(version):
            raise ValueError("invalid package version")
        if arch != arch_dir:
            raise ValueError("metadata architecture must match its directory")
        if stem != f"{name}-{version}":
            raise ValueError("archive filename must be <name>-<version>.tar.gz")
        if not isinstance(description, str) or not description.strip() or len(description) > 200:
            raise ValueError("description must contain 1–200 characters")
        with tarfile.open(archive, "r:gz") as tf:
            members = tf.getmembers()
            if not members:
                raise ValueError("archive is empty")
            for member in members:
                p = Path(member.name)
                if p.is_absolute() or ".." in p.parts or not member.name or "\\" in member.name:
                    raise ValueError(f"unsafe archive path: {member.name!r}")
                if member.isdev() or member.isfifo():
                    raise ValueError(f"device/FIFO entries are forbidden: {member.name!r}")
                if member.issym() or member.islnk():
                    target = Path(member.linkname)
                    if target.is_absolute() or ".." in target.parts or "\\" in member.linkname:
                        raise ValueError(f"unsafe link target: {member.linkname!r}")
        print(f"VALID: {archive.relative_to(ROOT)}")
    except Exception as exc:
        errors.append(f"{archive}: {exc}")
if not archives:
    print("No community package archives found; nothing to validate.")
if errors:
    print("\n".join("ERROR: " + e for e in errors), file=sys.stderr)
    sys.exit(1)
