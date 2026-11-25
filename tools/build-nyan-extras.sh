#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/build/nyan-extras"
rm -rf "$OUT"
mkdir -p "$OUT"

make_pkg() {
  local arch="$1" name="$2" description="$3" source="$4" destination="$5" dependency="${6:-}"
  local stage="$OUT/stage-$arch-$name"
  rm -rf "$stage"
  mkdir -p "$stage/$(dirname "$destination")"
  cp -a "$ROOT/$source" "$stage/$destination"
  local archive="$OUT/$name-0.1.0-$arch.tar.gz"
  tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner \
    -czf "$archive" -C "$stage" .
  tar -tzf "$archive" >/dev/null
  printf 'Built %s (%s): ' "$name" "$arch"
  sha256sum "$archive"
}

for arch in x86_64 i486; do
  make_pkg "$arch" vantor-hardware \
    "VANTOR read-only hardware inventory utility" \
    core/hardware/vantor-hw usr/bin/vantor-hw
  make_pkg "$arch" vantor-installer \
    "VANTOR text-mode system installer" \
    installer/vantor-install usr/sbin/vantor-install
  for file in vantor-mark.svg vantor-lockup.svg theme.json theme.css; do
    stage="$OUT/stage-$arch-vantor-branding"
    mkdir -p "$stage/usr/share/vantor/branding"
    cp "$ROOT/assets/branding/$file" "$stage/usr/share/vantor/branding/$file"
  done
  tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner \
    -czf "$OUT/vantor-branding-0.1.0-$arch.tar.gz" -C "$OUT/stage-$arch-vantor-branding" .
  tar -tzf "$OUT/vantor-branding-0.1.0-$arch.tar.gz" >/dev/null
  stage="$OUT/stage-$arch-vantor-docs"
  mkdir -p "$stage/usr/share/doc/vantor"
  cp "$ROOT/README.md" "$ROOT/LICENSE" "$ROOT/docs/nyan.md" "$stage/usr/share/doc/vantor/"
  tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner \
    -czf "$OUT/vantor-docs-0.1.0-$arch.tar.gz" -C "$stage" .
  tar -tzf "$OUT/vantor-docs-0.1.0-$arch.tar.gz" >/dev/null
done
