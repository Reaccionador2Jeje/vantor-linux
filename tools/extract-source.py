#!/usr/bin/env python3
"""Safely extract a verified source archive, stripping its single top directory."""
from __future__ import annotations

import argparse
import shutil
import tarfile
import tempfile
from pathlib import Path


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
                bundle.extractall(staging, filter="data")
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
