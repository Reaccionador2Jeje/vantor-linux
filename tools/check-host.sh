#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../build/config/vantor.conf
source "$ROOT/build/config/vantor.conf"

printf 'VANTOR host inspection — %s %s\n' "$VANTOR_NAME" "$VANTOR_VERSION"
printf 'Host: %s (%s)\n\n' "$(uname -s)" "$(uname -m)"

required=(bash make gcc g++ git python3 tar xz)
optional=(bison flex gawk m4 patch perl wget curl)

missing=0
for tool in "${required[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
        printf '[OK]       %s\n' "$tool"
    else
        printf '[MISSING]  %s (required for the planned build workflow)\n' "$tool"
        missing=1
    fi
done

for tool in "${optional[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
        printf '[OK]       %s\n' "$tool"
    else
        printf '[OPTIONAL] %s\n' "$tool"
    fi
done

if (( missing )); then
    printf '\nSome required host tools are missing. This is an inspection only; no packages were installed.\n' >&2
    exit 1
fi

printf '\nHost inspection completed. This does not mean VANTOR has been built.\n'
