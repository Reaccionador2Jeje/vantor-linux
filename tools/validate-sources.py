#!/usr/bin/env python3
"""Validate VANTOR upstream source pins without downloading anything."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "build" / "sources" / "sources.json"
DIGESTS = {"sha256": re.compile(r"^[0-9a-f]{64}$"), "sha512": re.compile(r"^[0-9a-f]{128}$")}
REQUIRED = {"name", "version", "archive", "url", "sha256", "sha512", "license", "role", "status"}


def fail(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-pinned", action="store_true")
    parser.add_argument("--only", nargs="+", help="validate only these source names")
    args = parser.parse_args()

    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON manifest: {exc}")

    if data.get("schema_version") != 1 or data.get("target") != "x86_64-vantor-linux-gnu":
        fail("unsupported manifest schema or target")
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        fail("sources must be a non-empty array")

    names: set[str] = set()
    archives: set[str] = set()
    selected = []
    for item in sources:
        if not isinstance(item, dict):
            fail("each source entry must be an object")
        missing = REQUIRED - item.keys()
        if missing:
            fail(f"source entry is missing fields: {', '.join(sorted(missing))}")
        name = item["name"]
        if not isinstance(name, str) or not name or name in names:
            fail(f"invalid or duplicate source name: {name!r}")
        names.add(name)
        if args.only and name not in args.only:
            continue
        selected.append(item)
        for field in ("version", "archive", "license", "role"):
            if not isinstance(item[field], str) or not item[field].strip():
                fail(f"{name}: {field} must be a non-empty string")
        archive = item["archive"]
        if archive in archives or Path(archive).name != archive:
            fail(f"{name}: archive filename must be unique and contain no path")
        archives.add(archive)
        parsed = urlparse(item["url"])
        if parsed.scheme != "https" or not parsed.netloc:
            fail(f"{name}: source URL must use HTTPS")

        valid_digest = False
        for algorithm, pattern in DIGESTS.items():
            digest = item[algorithm]
            if digest not in (None, ""):
                if not isinstance(digest, str) or not pattern.fullmatch(digest):
                    fail(f"{name}: invalid {algorithm} digest")
                valid_digest = True
        if item["status"] not in {"candidate", "pinned"}:
            fail(f"{name}: status must be candidate or pinned")
        if item["status"] == "pinned" and not valid_digest:
            fail(f"{name}: pinned source requires a verified SHA-256 or SHA-512 digest")
        if args.require_pinned and (item["status"] != "pinned" or not valid_digest):
            fail(f"{name}: source is not pinned")

    if args.only:
        missing_names = set(args.only) - names
        if missing_names:
            fail("unknown source name(s): " + ", ".join(sorted(missing_names)))
    if not selected:
        fail("no source entries selected")
    print(f"[OK] Validated {len(selected)} source manifest entries.")
    unpinned = [x["name"] for x in selected if x["status"] != "pinned"]
    if unpinned:
        print("[INFO] Not yet pinned: " + ", ".join(unpinned))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
