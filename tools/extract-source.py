#!/usr/bin/env python3
"""Safely extract a verified source archive, preserving contained relative links."""
from __future__ import annotations

import argparse
import os
import shutil
import tarfile
import tempfile
from pathlib import Path, PurePosixPath


def normalized_path(parts: tuple[str, ...], linkname: str) -> tuple[str, ...]:
    """Resolve a POSIX archive link lexically without allowing root escape."""
    if not linkname or linkname.startswith("/") or "\\" in linkname:
        raise ValueError(f"unsafe archive link target: {linkname!r}")
    stack = list(parts)
    for part in PurePosixPath(linkname).parts:
        if part in ("", "."):
            continue
        if part == "..":
            if not stack:
                raise ValueError(f"archive link escapes extraction root: {linkname!r}")
            stack.pop()
        else:
            stack.append(part)
    return tuple(stack)


def safe_extract(bundle: tarfile.TarFile, staging: Path) -> None:
    members: list[tuple[tarfile.TarInfo, tuple[str, ...]]] = []
    seen: dict[tuple[str, ...], tarfile.TarInfo] = {}
    for member in bundle.getmembers():
        raw = PurePosixPath(member.name)
        if raw.is_absolute() or "\\" in member.name or any(part == ".." for part in raw.parts):
            raise ValueError(f"unsafe archive path: {member.name!r}")
        parts = tuple(part for part in raw.parts if part not in ("", "."))
        if not parts:
            continue
        if parts in seen:
            previous = seen[parts]
            if not (member.isdir() and previous.isdir()):
                raise ValueError(f"duplicate archive path: {member.name!r}")
            continue
        if not (member.isdir() or member.isreg() or member.issym() or member.islnk()):
            raise ValueError(f"unsupported archive entry type: {member.name!r}")
        seen[parts] = member
        members.append((member, parts))

    # Kernel and other upstream source archives use one containing directory.
    top_dirs = [
        parts[0] for member, parts in members
        if len(parts) == 1 and member.isdir()
    ]
    root_prefix = (top_dirs[0],) if len(top_dirs) == 1 and all(parts[0] == top_dirs[0] for _, parts in members) else None

    symlink_paths = {parts for member, parts in members if member.issym()}
    regular_paths = {parts for member, parts in members if member.isreg()}
    for member, parts in members:
        for length in range(1, len(parts)):
            if parts[:length] in symlink_paths:
                raise ValueError(f"archive entry traverses a symlink directory: {member.name!r}")
        if member.issym():
            target = normalized_path(parts[:-1], member.linkname)
            if root_prefix and target[:len(root_prefix)] != root_prefix:
                raise ValueError(f"symlink leaves source tree: {member.name!r}")
        elif member.islnk():
            target = normalized_path((), member.linkname)
            if root_prefix and target[:len(root_prefix)] != root_prefix:
                raise ValueError(f"hard link leaves source tree: {member.name!r}")
            if target not in regular_paths:
                raise ValueError(f"hard link target is not a regular archive file: {member.linkname!r}")

    # Create real directories first, then regular files, hard-link copies, and
    # finally symlinks. No archive-controlled symlink can become a parent path.
    for member, parts in sorted(members, key=lambda item: len(item[1])):
        if member.isdir():
            target = staging.joinpath(*parts)
            target.mkdir(parents=True, exist_ok=True)
    for member, parts in members:
        if member.isreg() or member.islnk():
            target = staging.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            source = bundle.extractfile(member)
            if source is None:
                raise ValueError(f"cannot read archive member: {member.name!r}")
            with source, target.open("xb") as output:
                shutil.copyfileobj(source, output)
            target.chmod(member.mode & 0o777)
    for member, parts in members:
        if member.issym():
            target = staging.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(member.linkname, target)
    for member, parts in sorted(members, key=lambda item: len(item[1]), reverse=True):
        if member.isdir():
            target = staging.joinpath(*parts)
            target.chmod(member.mode & 0o777)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    archive = args.archive.resolve(strict=True)
    destination = args.destination.resolve()
    if destination.exists():
        raise SystemExit(f"[ERROR] destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="vantor-extract-", dir=destination.parent) as temporary:
        staging = Path(temporary)
        try:
            with tarfile.open(archive, mode="r:*") as bundle:
                safe_extract(bundle, staging)
        except (tarfile.TarError, OSError, ValueError) as exc:
            raise SystemExit(f"[ERROR] unsafe or invalid archive {archive.name}: {exc}") from exc

        children = list(staging.iterdir())
        source_root = children[0] if len(children) == 1 and children[0].is_dir() else staging
        destination.mkdir()
        try:
            for child in source_root.iterdir():
                shutil.move(str(child), destination / child.name)
        except OSError as exc:
            shutil.rmtree(destination, ignore_errors=True)
            raise SystemExit(f"[ERROR] could not prepare source tree: {exc}") from exc

    print(f"[OK] Safely extracted source: {archive.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
