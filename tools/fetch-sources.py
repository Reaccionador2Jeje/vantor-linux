#!/usr/bin/env python3
"""Download only pinned VANTOR sources and verify SHA-256 before keeping them."""
from __future__ import annotations

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
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CHUNK_SIZE = 1024 * 1024


def abort(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        abort(f"cannot read source manifest: {exc}")

    entries = manifest.get("sources", [])
    if not entries:
        abort("source manifest is empty")

    for entry in entries:
        name = entry.get("name", "<unnamed>")
        digest = entry.get("sha256")
        if entry.get("status") != "pinned" or not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            abort(f"{name}: source is not pinned; refusing to download")

    DESTINATION.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        name = entry["name"]
        archive = entry["archive"]
        if Path(archive).name != archive or archive in {"", ".", ".."}:
            abort(f"{name}: unsafe archive filename")
        url = entry["url"]
        if urlparse(url).scheme != "https":
            abort(f"{name}: refusing non-HTTPS URL")

        target = DESTINATION / archive
        if target.exists():
            current = hashlib.sha256(target.read_bytes()).hexdigest()
            if current == entry["sha256"]:
                print(f"[OK] Already verified: {archive}")
                continue
            abort(f"{name}: existing archive has the wrong SHA-256; remove it manually")

        fd, temporary_name = tempfile.mkstemp(prefix=f".{archive}.", dir=DESTINATION)
        os.close(fd)
        temporary = Path(temporary_name)
        hasher = hashlib.sha256()
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "VANTOR-source-fetch/0.1"})
            with urllib.request.urlopen(request, timeout=60) as response, temporary.open("wb") as output:
                final_url = response.geturl()
                if urlparse(final_url).scheme != "https":
                    abort(f"{name}: upstream redirected to a non-HTTPS URL")
                while True:
                    chunk = response.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    hasher.update(chunk)
                    output.write(chunk)
            actual = hasher.hexdigest()
            if actual != entry["sha256"]:
                abort(f"{name}: SHA-256 mismatch (expected {entry['sha256']}, got {actual})")
            temporary.replace(target)
            print(f"[OK] Downloaded and verified: {archive}")
        except (OSError, urllib.error.URLError, TimeoutError) as exc:
            abort(f"{name}: download failed: {exc}")
        finally:
            temporary.unlink(missing_ok=True)

    print(f"[OK] All {len(entries)} upstream source archives are verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
