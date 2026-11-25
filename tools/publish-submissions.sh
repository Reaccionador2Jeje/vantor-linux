#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
command -v gh >/dev/null || { echo "GitHub CLI is required" >&2; exit 1; }
tag=nyan-repository
if ! gh release view "$tag" >/dev/null 2>&1; then
  gh release create "$tag" --title "VANTOR Nyan Community Packages" --notes "Community packages accepted into the official VANTOR repository."
fi
python3 tools/validate-submissions.py
shopt -s nullglob
published=0
for archive in incoming/*/*.tar.gz; do
  arch=$(basename "$(dirname "$archive")")
  stem=$(basename "$archive" .tar.gz)
  metadata="${archive%.tar.gz}.json"
  [[ -f "$metadata" ]] || { echo "Missing metadata for $archive" >&2; exit 1; }
  name=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["name"])' "$metadata")
  version=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["version"])' "$metadata")
  description=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["description"])' "$metadata")
  digest=$(sha256sum "$archive" | awk '{print $1}')
  filename=$(basename "$archive")
  gh release upload "$tag" "$archive" --clobber
  index="packages/repository/$arch/Packages"
  mkdir -p "$(dirname "$index")"
  [[ -f "$index" ]] || printf '# VANTOR-PACKAGES 1\n' > "$index"
  python3 - "$index" "$name" "$version" "$arch" "$digest" "$filename" "$description" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); name,version,arch,digest,filename,description=sys.argv[2:]
lines=p.read_text().splitlines()
if not lines or lines[0] != "# VANTOR-PACKAGES 1":
    raise SystemExit("Unsupported package index format")
row="\t".join((name,version,arch,digest,filename,description.replace("\t"," ").replace("\n"," ")))
lines=[line for line in lines if not line.startswith(name+"\t")]
lines.append(row)
p.write_text("\n".join(lines)+"\n")
PY
  rm -f "$archive" "$metadata"
  published=$((published+1))
done
if (( published > 0 )); then
  git config user.name "github-actions[bot]"
  git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
  git add packages/repository incoming
  git commit -m "Publish $published accepted Nyan community package(s)"
  git push
  echo "Published $published community package(s)."
else
  echo "No new community packages to publish."
fi
