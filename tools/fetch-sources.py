#!/usr/bin/env python3
"""Download only pinned VANTOR sources and verify upstream SHA-256/SHA-512."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "build" / "sources" / "sources.json"
DESTINATION = ROOT / "build" / "distfiles"
PATTERNS = {"sha256": re.compile(r"^[0-9a-f]{64}$"), "sha512": re.compile(r"^[0-9a-f]{128}$")}
CHUNK_SIZE = 1024 * 1024


def digest_file(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(CHUNK_SIZE), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def expected_digest(entry: dict) -> tuple[str, str]:
    for algorithm in ("sha256", "sha512"):
        value = entry.get(algorithm)
        if isinstance(value, str) and PATTERNS[algorithm].fullmatch(value):
            return algorithm, value
    abort(f"{entry.get('name', '<unnamed>')}: no valid pinned digest")


def abort(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="+", help="download only these source names")
    args = parser.parse_args()
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        abort(f"cannot read source manifest: {exc}")

    entries = manifest.get("sources", [])
    if args.only:
        wanted = set(args.only)
        entries = [entry for entry in entries if entry.get("name") in wanted]
        found = {entry.get("name") for entry in entries}
        if wanted != found:
            abort("unknown source name(s): " + ", ".join(sorted(wanted - found)))
    if not entries:
        abort("no source entries selected")

    for entry in entries:
        if entry.get("status") != "pinned":
            abort(f"{entry.get('name')}: source is not pinned; refusing to download")
        expected_digest(entry)

    DESTINATION.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        name, archive, url = entry["name"], entry["archive"], entry["url"]
        if Path(archive).name != archive or archive in {"", ".", ".."}:
            abort(f"{name}: unsafe archive filename")
        if urlparse(url).scheme != "https":
            abort(f"{name}: refusing non-HTTPS URL")
        algorithm, expected = expected_digest(entry)
        target = DESTINATION / archive
        if target.exists():
            if digest_file(target, algorithm) == expected:
                print(f"[OK] Already verified: {archive} ({algorithm})")
                continue
            abort(f"{name}: existing archive has an incorrect {algorithm} digest")

        fd, temporary_name = tempfile.mkstemp(prefix=f".{archive}.", dir=DESTINATION)
        os.close(fd)
        temporary = Path(temporary_name)
        hasher = hashlib.new(algorithm)
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "VANTOR-source-fetch/0.2"})
            with urllib.request.urlopen(request, timeout=90) as response, temporary.open("wb") as output:
                if urlparse(response.geturl()).scheme != "https":
                    abort(f"{name}: upstream redirected to non-HTTPS")
                while True:
                    chunk = response.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    hasher.update(chunk)
                    output.write(chunk)
            actual = hasher.hexdigest()
            if actual != expected:
                abort(f"{name}: {algorithm} mismatch (expected {expected}, got {actual})")
            temporary.replace(target)
            print(f"[OK] Downloaded and verified: {archive} ({algorithm})")
        except (OSError, urllib.error.URLError, TimeoutError) as exc:
            abort(f"{name}: download failed: {exc}")
        finally:
            temporary.unlink(missing_ok=True)

    print(f"[OK] All {len(entries)} selected source archives are verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
