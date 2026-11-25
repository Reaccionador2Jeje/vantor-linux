#!/usr/bin/env python3
"""Safely extract a verified source archive into a clean directory."""
from __future__ import annotations

import argparse
import shutil
import tarfile
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
    destination.mkdir()

    try:
        with tarfile.open(archive, mode="r:*") as bundle:
            bundle.extractall(destination, filter="data")
    except (tarfile.TarError, OSError, ValueError) as exc:
        shutil.rmtree(destination, ignore_errors=True)
        raise SystemExit(f"[ERROR] unsafe or invalid archive {archive.name}: {exc}") from exc

    print(f"[OK] Extracted verified archive: {archive.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
