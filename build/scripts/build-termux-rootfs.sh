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
if grep -q '^CONFIG_TC=y {
  local key="$1" value="$2"
  if grep -q "^# ${key} is not set$" "$BUILD_DIR/.config"; then
    sed -i "s/^# ${key} is not set$/${key}=${value}/" "$BUILD_DIR/.config"
  elif grep -q "^${key}=" "$BUILD_DIR/.config"; then
    sed -i "s/^${key}=.*/${key}=${value}/" "$BUILD_DIR/.config"
  else
    printf '%s=%s\n' "$key" "$value" >> "$BUILD_DIR/.config"
  fi
}
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
cat > "$ROOTFS/usr/bin/vantor-termux-shell" <<'EOF'
#!/bin/sh
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export HOME=/root
export TERM="${TERM:-xterm-256color}"
echo "VANTOR Linux — Termux ARM64 userspace"
echo "PRoot session: Android supplies the kernel; VANTOR supplies this userspace."
exec /bin/sh -l
EOF
chmod 755 "$ROOTFS/usr/bin/vantor-termux-shell"
echo "[OK] VANTOR ARM64 PRoot userspace is ready: $ROOTFS"
 "$BUILD_DIR/.config"; then
  sed -i 's/^CONFIG_TC=y$/# CONFIG_TC is not set/' "$BUILD_DIR/.config"
fi

set_config() {
  local key="$1" value="$2"
  if grep -q "^# ${key} is not set$" "$BUILD_DIR/.config"; then
    sed -i "s/^# ${key} is not set$/${key}=${value}/" "$BUILD_DIR/.config"
  elif grep -q "^${key}=" "$BUILD_DIR/.config"; then
    sed -i "s/^${key}=.*/${key}=${value}/" "$BUILD_DIR/.config"
  else
    printf '%s=%s\n' "$key" "$value" >> "$BUILD_DIR/.config"
  fi
}
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
cat > "$ROOTFS/usr/bin/vantor-termux-shell" <<'EOF'
#!/bin/sh
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export HOME=/root
export TERM="${TERM:-xterm-256color}"
echo "VANTOR Linux — Termux ARM64 userspace"
echo "PRoot session: Android supplies the kernel; VANTOR supplies this userspace."
exec /bin/sh -l
EOF
chmod 755 "$ROOTFS/usr/bin/vantor-termux-shell"
echo "[OK] VANTOR ARM64 PRoot userspace is ready: $ROOTFS"
