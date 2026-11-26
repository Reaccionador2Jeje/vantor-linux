#!/usr/bin/env python3
"""Validate every executable OpenRC installs, using Meson's target inventory.

This deliberately avoids a hand-maintained list of every upstream helper:
when OpenRC adds, removes, or renames an executable, the validator follows
the pinned source's Meson install metadata automatically.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


REQUIRED = {
    "x86_64": {
        "/usr/sbin": (
            "openrc-init", "openrc", "openrc-run", "openrc-shutdown",
            "rc-service", "rc-update", "rc-sstat", "rc-environ",
            "start-stop-daemon", "supervise-daemon",
            "halt", "poweroff", "reboot", "shutdown",
        ),
        "/usr/lib/rc/bin": ("checkpath", "openrc-user", "rc-depend"),
        "/usr/lib/rc/sbin": ("rc-abort",),
    },
    "i486": {
        "/usr/sbin": (
            "openrc-init", "openrc", "openrc-run", "openrc-shutdown",
            "rc-service", "rc-update", "rc-sstat", "rc-environ",
            "start-stop-daemon", "supervise-daemon",
            "halt", "poweroff", "reboot", "shutdown",
        ),
        "/usr/lib/rc/bin": ("checkpath", "openrc-user", "rc-depend"),
        "/usr/lib/rc/sbin": ("rc-abort",),
    },
}


def fail(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--rootfs", required=True, type=Path)
    parser.add_argument("--arch", choices=tuple(REQUIRED), required=True)
    args = parser.parse_args()

    try:
        raw = subprocess.check_output(
            ["meson", "introspect", "--targets", str(args.build_dir)],
            text=True,
        )
        targets = json.loads(raw)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        fail(f"cannot read Meson install target inventory: {exc}")

    installed = set()
    problems: list[str] = []
    checked = 0

    for target in targets:
        if target.get("type") != "executable" or not target.get("installed"):
            continue
        destinations = target.get("install_filename") or []
        if isinstance(destinations, str):
            destinations = [destinations]
        for destination in destinations:
            # Meson's target inventory can include OpenRC's generated
            # /etc/runlevels symlink entries. They are service registrations,
            # not executable payloads; validate those links against the final
            # assembled rootfs below, after VANTOR prunes optional services.
            relative = str(destination).lstrip("/")
            if not relative.startswith(("usr/bin/", "usr/sbin/", "usr/lib/")):
                continue
            path = args.rootfs / relative
            installed.add("/" + relative)
            checked += 1
            if not path.is_file() or not os.access(path, os.X_OK):
                problems.append(f"missing or non-executable installed target: {path}")
                continue

            header = subprocess.run(
                ["readelf", "-h", str(path)], capture_output=True, text=True
            )
            if header.returncode != 0:
                # Meson can install executable scripts as well as ELF files.
                if path.read_bytes()[:2] != b"#!":
                    problems.append(f"not an ELF executable or script: {path}")
                continue

            expected_machine = (
                "Advanced Micro Devices X86-64"
                if args.arch == "x86_64"
                else "Intel 80386"
            )
            if expected_machine not in header.stdout:
                problems.append(f"wrong {args.arch} ELF machine: {path}")
            program = subprocess.run(
                ["readelf", "-l", str(path)], capture_output=True, text=True
            )
            if program.returncode == 0 and "INTERP" in program.stdout:
                problems.append(f"dynamically linked executable: {path}")

    if checked == 0:
        problems.append("Meson reported no installed executable payloads under /usr")

    # Validate the final service graph, not Meson's pre-pruning install plan.
    # Every relative runlevel link must resolve to a real init script.
    runlevels = args.rootfs / "etc/runlevels"
    if runlevels.exists():
        for link in sorted(runlevels.rglob("*")):
            if not link.is_symlink():
                continue
            target = os.readlink(link)
            try:
                if os.path.isabs(target):
                    resolved = (args.rootfs / target.lstrip("/")).resolve(strict=True)
                else:
                    resolved = link.resolve(strict=True)
                if not resolved.is_file():
                    problems.append(f"runlevel target is not a service file: {link} -> {target}")
            except (OSError, RuntimeError):
                problems.append(f"broken runlevel service link: {link} -> {target}")

    for directory, names in REQUIRED[args.arch].items():
        for name in names:
            path = directory.rstrip("/") + "/" + name
            if path not in installed:
                # Required entry points may be generated by Meson as symlinks;
                # in that case validate the resulting rootfs path directly.
                actual = args.rootfs / path.lstrip("/")
                if not actual.is_file() or not os.access(actual, os.X_OK):
                    problems.append(f"required OpenRC command is absent: {actual}")

    if problems:
        for problem in problems:
            print(f"[ERROR] {problem}", file=sys.stderr)
        return 1

    print(
        f"[OK] Validated {checked} installed OpenRC executable targets "
        f"from Meson metadata ({args.arch}); required init/service entry points present."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
