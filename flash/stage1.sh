#!/bin/bash
# Stage 1 (reversible): stop k3s, fetch + verify Pi OS Lite into RAM, loop-mount it, show what the boot partition holds.
set -euo pipefail
URL=https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2026-10-06/2026-10-06-raspios-trixie-arm64-lite.img.xz
W=/dev/shm/flash
F=$(basename "$URL")

echo "[1] stop k3s"
systemctl stop k3s k3s-agent 2>/dev/null || true
/usr/local/bin/k3s-killall.sh >/dev/null 2>&1 || true
mount -o remount,size=6G /dev/shm
mkdir -p $W && cd $W

echo "[2] download + verify"
[ -f "$F" ] || curl -fL# -o "$F" "$URL"
curl -fsL -o "$F.sha256" "$URL.sha256"
sha256sum -c "$F.sha256"
xz -l "$F" | tail -1

echo "[3] decompress"
[ -f os.img ] || { xz -dc "$F" > os.img && rm "$F"; }
ls -lh os.img

echo "[4] loop-mount"
LOOP=$(losetup -j os.img | cut -d: -f1); [ -n "$LOOP" ] || LOOP=$(losetup -fP --show os.img)
mkdir -p b r
mountpoint -q b || mount "${LOOP}p1" b
mountpoint -q r || mount "${LOOP}p2" r
echo "$LOOP" > loopdev

echo "[5] boot partition:"; ls b | tr '\n' ' '; echo
for f in user-data network-config meta-data userconf.txt; do [ -f b/$f ] && { echo "--- $f"; grep -v '^\s*#' b/$f | grep -v '^\s*$' | head -12; }; done
echo "[6] root disk: $(lsblk -no pkname "$(findmnt -no SOURCE /)")  wifi src: $(ls /etc/wpa_supplicant/wpa_supplicant.conf /etc/NetworkManager/system-connections/ 2>/dev/null | tr '\n' ' ')"
free -h | sed -n 2p
echo STAGE1_DONE
