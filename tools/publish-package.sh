#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  echo "Usage: $0 PACKAGE.tar.gz NAME VERSION ARCH DESCRIPTION [DEPENDENCIES]" >&2
  exit 2
}
[[ $# -eq 5 || $# -eq 6 ]] || usage
dependencies=${6:-}
if [[ -n "$dependencies" && ! "$dependencies" =~ ^[A-Za-z0-9+_.-]+(,[A-Za-z0-9+_.-]+)*$ ]]; then echo "Invalid dependency list" >&2; exit 2; fi
archive=$1 name=$2 version=$3 arch=$4 description=$5
[[ -f "$archive" ]] || { echo "Package archive not found: $archive" >&2; exit 1; }
[[ "$name" =~ ^[A-Za-z0-9][A-Za-z0-9+_.-]*$ ]] || { echo "Invalid package name" >&2; exit 1; }
[[ "$version" =~ ^[A-Za-z0-9][A-Za-z0-9+_.+-]*$ ]] || { echo "Invalid version" >&2; exit 1; }
[[ "$arch" == x86_64 || "$arch" == i486 || "$arch" == aarch64 || "$arch" == all ]] || { echo "Unsupported architecture" >&2; exit 1; }
[[ "$archive" == *.tar.gz ]] || { echo "Packages must be .tar.gz archives" >&2; exit 1; }
command -v gh >/dev/null || { echo "GitHub CLI (gh) is required" >&2; exit 1; }
command -v sha256sum >/dev/null || { echo "sha256sum is required" >&2; exit 1; }
tar -tzf "$archive" >/dev/null || { echo "Invalid package archive" >&2; exit 1; }
while IFS= read -r item; do
  case "$item" in /*|../*|*/../*|*/..) echo "Unsafe archive path: $item" >&2; exit 1;; esac
done < <(tar -tzf "$archive")
filename=$(basename "$archive")
digest=$(sha256sum "$archive" | awk '{print $1}')
tag=nyan-repository
if ! gh release view "$tag" >/dev/null 2>&1; then
  gh release create "$tag" --title "VANTOR Nyan Package Repository" --notes "Official package assets for the VANTOR Linux Nyan repository."
fi
# Asset uploads are idempotent; index publication below is retried independently.
gh release upload "$tag" "$archive" --clobber

branch=$(git branch --show-current)
[[ -n "$branch" ]] || { echo "Cannot determine publishing branch" >&2; exit 1; }
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

for attempt in 1 2 3 4 5; do
  echo "[Nyan] Refreshing $branch before index update (attempt $attempt/5)."
  git fetch origin "$branch"
  git reset --hard FETCH_HEAD

  export VANTOR_PKG_NAME="$name" VANTOR_PKG_VERSION="$version" VANTOR_PKG_ARCH="$arch"
  export VANTOR_PKG_SHA256="$digest" VANTOR_PKG_FILE="$filename" VANTOR_PKG_DESCRIPTION="$description" VANTOR_PKG_DEPENDENCIES="$dependencies"
  python3 - <<'PY'
import os
from pathlib import Path

path = Path("packages/repository") / os.environ["VANTOR_PKG_ARCH"] / "Packages"
path.parent.mkdir(parents=True, exist_ok=True)
header = "# VANTOR-PACKAGES 1"
lines = path.read_text().splitlines() if path.exists() else [header]
if not lines or lines[0] != header:
    raise SystemExit(f"Invalid repository index: {path}")
name = os.environ["VANTOR_PKG_NAME"]
row = "\t".join([
    name,
    os.environ["VANTOR_PKG_VERSION"],
    os.environ["VANTOR_PKG_ARCH"],
    os.environ["VANTOR_PKG_SHA256"],
    os.environ["VANTOR_PKG_FILE"],
    os.environ["VANTOR_PKG_DESCRIPTION"].replace("\t", " ").replace("\n", " "),
    os.environ["VANTOR_PKG_DEPENDENCIES"],
])
lines = [line for line in lines if not line.startswith(name + "\t")]
lines.append(row)
path.write_text("\n".join(lines) + "\n")
PY
  git add "packages/repository/$arch/Packages"
  if git diff --cached --quiet; then
    echo "Nyan index already contains $name $version ($arch), SHA-256: $digest"
    exit 0
  fi
  git commit -m "Publish Nyan package $name $version ($arch)"
  if git push origin "HEAD:$branch"; then
    echo "Published $name $version ($arch), SHA-256: $digest"
    exit 0
  fi
  echo "[WARN] Push raced with another main update; next attempt rebuilds from the fresh remote index." >&2
done

echo "[ERROR] Could not publish after five fresh-index attempts." >&2
exit 1
