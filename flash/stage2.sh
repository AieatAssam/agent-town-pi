#!/bin/bash
# Stage 2 (reversible): provision the loop-mounted image in RAM. Secrets are read on the Pi (Wi-Fi) or fetched as a hash; nothing secret is printed.
set -uo pipefail
SRV=http://192.168.1.10:8765
HOST=k3s-pi
CCDEF=GB TZONE=Europe/London
W=/dev/shm/flash; cd $W || exit 1
B=$W/b R=$W/r
mountpoint -q $B && mountpoint -q $R || { echo "image not mounted"; exit 1; }

# User: same name; the password hash was made on the Mac from the user's chosen creds
UH=$(curl -fs $SRV/secret/user) || { echo "no user hash"; exit 1; }
U=${UH%%:*}; H=${UH#*:}
[[ $H == '$6$'* ]] || { echo "bad hash"; exit 1; }

# Wi-Fi from the running system
WPA=/etc/wpa_supplicant/wpa_supplicant.conf
get() { sed -n "s/^[[:space:]]*$1=//p" $WPA | head -1; }
mkdir -p $R/etc/NetworkManager/system-connections
if [ -f $WPA ]; then
  SSID=$(get ssid); PSK=$(get psk); CC=$(sed -n 's/^country=//p' $WPA | head -1); SCAN=$(get scan_ssid)
  SSID=${SSID#\"}; SSID=${SSID%\"}; PSK=${PSK#\"}; PSK=${PSK%\"}
  NM=$R/etc/NetworkManager/system-connections/wifi.nmconnection
  {
    printf '[connection]\nid=wifi\ntype=wifi\nautoconnect=true\n\n[wifi]\nmode=infrastructure\nssid=%s\n' "$SSID"
    [ "$SCAN" = 1 ] && printf 'hidden=true\n'
    printf '\n[wifi-security]\nkey-mgmt=wpa-psk\npsk=%s\n\n[ipv4]\nmethod=auto\n\n[ipv6]\nmethod=auto\n' "$PSK"
  } > $NM
  chmod 600 $NM; chown root:root $NM
  echo "wifi: keyfile written (ssid ${#SSID} chars, psk ${#PSK} chars, country ${CC:-?}, hidden=${SCAN:-0})"
else
  cp -a /etc/NetworkManager/system-connections/. $R/etc/NetworkManager/system-connections/ && echo "wifi: copied NM profiles"
  CC=$(iw reg get 2>/dev/null | sed -n 's/^country \([A-Z][A-Z]\).*/\1/p' | head -1)
fi
mkdir -p $R/var/lib/systemd/rfkill && cp -a /var/lib/systemd/rfkill/. $R/var/lib/systemd/rfkill/ 2>/dev/null
for f in $R/var/lib/systemd/rfkill/*; do echo 0 > "$f"; done
CC=${CC:-$CCDEF}
[ -n "$CC" ] && ! grep -q ieee80211_regdom $B/cmdline.txt && sed -i "1 s/\$/ cfg80211.ieee80211_regdom=$CC/" $B/cmdline.txt

# cloud-init: user, hostname, ssh with password auth
cat > $B/user-data <<EOF
#cloud-config
hostname: $HOST
manage_etc_hosts: true
timezone: $TZONE
users:
  - name: $U
    groups: users,adm,dialout,audio,netdev,video,plugdev,cdrom,games,input,gpio,spi,i2c,render,sudo
    shell: /bin/bash
    lock_passwd: false
    passwd: $H
    sudo: ALL=(ALL) NOPASSWD:ALL
ssh_pwauth: true
runcmd:
  - [rfkill, unblock, wifi]
  - [raspi-config, nonint, do_wifi_country, "${CC:-US}"]
  - [systemctl, enable, ssh]
EOF
echo "$HOST" > $R/etc/hostname

# commit script (runs detached, from RAM)
DISK=/dev/$(lsblk -no pkname "$(findmnt -no SOURCE /)")
cat > $W/commit.sh <<EOF
#!/bin/bash
exec >$W/commit.log 2>&1
echo 1 > /proc/sys/kernel/sysrq
echo s > /proc/sysrq-trigger; echo u > /proc/sysrq-trigger
dd if=$W/os.img of=$DISK bs=4M oflag=direct conv=fsync status=progress
echo "dd exit \$?"
echo b > /proc/sysrq-trigger
EOF
sync; umount $B $R && losetup -d "$(cat loopdev)" && echo "image unmounted"
echo "user: $U  host: $HOST  target disk: $DISK ($(lsblk -dno SIZE,MODEL $DISK))"
ls -lh $W/os.img; free -h | sed -n 2p
echo STAGE2_DONE
