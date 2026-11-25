#!/usr/bin/env python3
"""Validate VANTOR's upstream source manifest without downloading anything."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "build" / "sources" / "sources.json"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED = {"name", "version", "archive", "url", "sha256", "license", "role", "status"}


def fail(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-pinned", action="store_true",
                        help="fail unless every source has a verified SHA-256 and status=pinned")
    args = parser.parse_args()

    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON manifest: {exc}")

    if data.get("schema_version") != 1:
        fail("unsupported or missing schema_version")
    if data.get("target") != "x86_64-vantor-linux-gnu":
        fail("unexpected target; update validator when adding a target")
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        fail("sources must be a non-empty array")

    names: set[str] = set()
    unpinned: list[str] = []
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
        for field in ("version", "archive", "license", "role"):
            if not isinstance(item[field], str) or not item[field].strip():
                fail(f"{name}: {field} must be a non-empty string")
        parsed = urlparse(item["url"])
        if parsed.scheme != "https" or not parsed.netloc:
            fail(f"{name}: source URL must use HTTPS")
        digest = item["sha256"]
        if digest is None or digest == "":
            unpinned.append(name)
        elif not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            fail(f"{name}: sha256 must be 64 lowercase hexadecimal characters")
        if item["status"] not in {"candidate", "pinned"}:
            fail(f"{name}: status must be candidate or pinned")
        if item["status"] == "pinned" and not SHA256_RE.fullmatch(digest or ""):
            fail(f"{name}: pinned source requires a SHA-256 digest")

    if args.require_pinned and unpinned:
        fail("sources are not ready for automated builds; missing SHA-256: " + ", ".join(unpinned))
    print(f"[OK] Source manifest valid: {len(sources)} entries.")
    if unpinned:
        print("[INFO] Candidate-only sources (not downloadable by build automation): " + ", ".join(unpinned))
    else:
        print("[OK] Every source is pinned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
