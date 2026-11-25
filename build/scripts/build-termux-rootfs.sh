#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$ROOT"
source build/config/vantor.conf

case "$(uname -m)" in
  aarch64|arm64) ;;
  *) echo "[ERROR] Build this target on an ARM64 Linux host (GitHub ubuntu-24.04-arm)." >&2; exit 1;;
esac

VERSION="1.37.0"
SOURCE_DIR="$ROOT/build/work/sources/busybox-$VERSION"
BUILD_DIR="$ROOT/build/work/busybox-termux"
ROOTFS="$ROOT/build/work/rootfs-termux"

python3 tools/validate-sources.py --require-pinned --only busybox
python3 tools/fetch-sources.py --only busybox
if [[ ! -f "$SOURCE_DIR/Makefile" ]]; then
  python3 tools/extract-source.py "$ROOT/build/distfiles/busybox-$VERSION.tar.bz2" "$SOURCE_DIR"
fi
mkdir -p "$BUILD_DIR" "$ROOTFS"
python3 tools/prepare-rootfs.py --output "$ROOTFS" --arch aarch64
make -C "$SOURCE_DIR" O="$BUILD_DIR" defconfig

# BusyBox tc still references legacy CBQ kernel headers removed from modern headers.
if grep -q '^CONFIG_TC=y$' "$BUILD_DIR/.config"; then
  sed -i 's/^CONFIG_TC=y$/# CONFIG_TC is not set/' "$BUILD_DIR/.config"
fi

set_config() {
  local key="$1" value="$2"
  if grep -q "^# ${key} is not set$" "$BUILD_DIR/.config"; then
    sed -i "s/^# ${key} is not set$/${key}=${value}/" "$BUILD_DIR/.config"
  elif grep -q "^${key}=" "$BUILD_DIR/.config"; then
    sed -i "s/^${key}=.*/${key}=${value}/" "$BUILD_DIR/.config"
  else
    printf '%s=%s\\n' "$key" "$value" >> "$BUILD_DIR/.config"
  fi
}
set_config CONFIG_SHA1_HWACCEL n
set_config CONFIG_SHA256_HWACCEL n
set_config CONFIG_STATIC y
set_config CONFIG_VI y
set_config CONFIG_ASH y
set_config CONFIG_SH_IS_ASH y
set_config CONFIG_FEATURE_PREFER_APPLETS y
set_config CONFIG_MDEV y
set_config CONFIG_UDHCPC y
set_config CONFIG_IP y
set_config CONFIG_MOUNT y
set_config CONFIG_UMOUNT y
set_config CONFIG_DF y
set_config CONFIG_FREE y
set_config CONFIG_PS y
set_config CONFIG_FEATURE_SHADOWPASSWDS y
make -C "$SOURCE_DIR" O="$BUILD_DIR" oldconfig </dev/null
grep -q '^CONFIG_STATIC=y$' "$BUILD_DIR/.config"
make -C "$SOURCE_DIR" O="$BUILD_DIR" -j"${VANTOR_BUILD_JOBS:-$(nproc)}"
make -C "$SOURCE_DIR" O="$BUILD_DIR" CONFIG_PREFIX="$ROOTFS" install

test -x "$ROOTFS/bin/busybox"
test -x "$ROOTFS/bin/sh"
"$ROOTFS/bin/busybox" --list > "$BUILD_DIR/applets.txt"
for applet in sh ash vi mdev udhcpc ip mount umount df free ps; do
  grep -qx "$applet" "$BUILD_DIR/applets.txt" || { echo "[ERROR] Missing BusyBox applet: $applet" >&2; exit 1; }
done

mkdir -p "$ROOTFS/root/.config" "$ROOTFS/run" "$ROOTFS/tmp"
chmod 700 "$ROOTFS/root"
chmod 1777 "$ROOTFS/tmp"
cat > "$ROOTFS/etc/nyan.conf" <<'EOF'
# ARM64 Nyan packages will be enabled when the aarch64 repository is published.
NYAN_ARCH=aarch64
EOF
cat > "$ROOTFS/etc/profile" <<'EOF'
# VANTOR interactive shell defaults.
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export HOME=/root
export TERM="${TERM:-xterm-256color}"
export VANTOR_RUNTIME=proot
export PS1='\033[1;36mVANTOR\033[0m:\w# '
alias ll='ls -lah'
alias la='ls -A'
alias cls='clear'
EOF
cat > "$ROOTFS/etc/motd" <<'EOF'
\033[1;36m  __      __ _   _ _____ ___  ____  \
  \033[1;36m  \\ \\ /\\ / /| | | |_   _/ _ \\|  _ \\ 
  \033[1;36m   \\ V  V / | |_| | | || | | | | |_) |
  \033[1;36m    \\_/\\_/   \\__,_| |_| |_| |_| |____/
\033[0m
ONE SYSTEM. EVERY GENERATION.
Termux ARM64 userspace • Android provides the Linux kernel
EOF
cat > "$ROOTFS/usr/bin/vantor-info" <<'EOF'
#!/bin/sh
echo "VANTOR Linux — Termux ARM64"
echo "Version: 0.1.0"
echo "Architecture: aarch64"
echo "Runtime: PRoot userspace"
echo "Kernel: $(uname -sr)"
echo "Shell: ${SHELL:-/bin/sh}"
echo "Rootfs: /"
EOF
cat > "$ROOTFS/usr/bin/vantor-doctor" <<'EOF'
#!/bin/sh
failed=0
check() {
  label=$1; shift
  if "$@"; then printf '[ OK ] %s\n' "$label"
  else printf '[FAIL] %s\n' "$label"; failed=1
  fi
}
check "BusyBox executable" test -x /bin/busybox
check "VANTOR release metadata" test -s /etc/vantor-release
check "VANTOR shell entrypoint" test -x /usr/bin/vantor-termux-shell
check "procfs available" test -r /proc/version
check "host kernel visible" sh -c 'uname -s | grep -q Linux'
if [ -r /etc/resolv.conf ]; then
  echo "[INFO] DNS configuration is mounted."
else
  echo "[WARN] DNS configuration is not visible; check Termux resolver binding."
fi
exit "$failed"
EOF
cat > "$ROOTFS/usr/bin/vantor-termux-shell" <<'EOF'
#!/bin/sh
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export HOME=/root
export TERM="${TERM:-xterm-256color}"
export VANTOR_RUNTIME=proot
if [ "$#" -gt 0 ]; then
  exec "$@"
fi
printf '\033[1;36mVANTOR Linux\033[0m — Termux ARM64 userspace\n'
echo "Android supplies the kernel; VANTOR supplies this userspace."
echo "Run 'vantor-info' or 'vantor-doctor' to inspect this environment."
exec /bin/sh -l
EOF
chmod 755 "$ROOTFS/usr/bin/vantor-termux-shell" "$ROOTFS/usr/bin/vantor-info" "$ROOTFS/usr/bin/vantor-doctor"
echo "[OK] VANTOR ARM64 PRoot userspace is ready: $ROOTFS"
