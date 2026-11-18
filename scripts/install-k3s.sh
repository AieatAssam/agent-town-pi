#!/usr/bin/env bash
# Re-runnable record of the k3s bootstrap for the Pi.
# Usage: scripts/install-k3s.sh <ssh-host>
#   <ssh-host>  an ssh alias from ~/.ssh/config (user, key and address live there)
# Optional env:
#   K3S_API_HOST      name the API cert and kubeconfig use (default: <ssh-host>.local)
#   KUBECONFIG_OUT    where to write the Mac kubeconfig (default: ~/.kube/<ssh-host>.yaml)
set -euo pipefail

HOST="${1:?usage: $0 <ssh-host>}"
API_HOST="${K3S_API_HOST:-$HOST.local}"
KUBECONFIG_OUT="${KUBECONFIG_OUT:-$HOME/.kube/$HOST.yaml}"
SSH=(ssh -o ConnectTimeout=5)

# Step 1: memory cgroup flags, then reboot once if the running kernel lacks them.
"${SSH[@]}" "$HOST" 'bash -s' <<'REMOTE'
set -euo pipefail
f=/boot/firmware/cmdline.txt
for opt in cgroup_enable=memory cgroup_memory=1; do
  grep -q "$opt" "$f" || sudo sed -i "1s/\$/ $opt/" "$f"
done
if ! grep -q 'cgroup_memory=1' /proc/cmdline; then
  echo "rebooting to apply cmdline"
  sudo systemctl reboot
fi
REMOTE

# Wait for SSH to come back (no-op when no reboot happened).
sleep 10
until "${SSH[@]}" -o BatchMode=yes "$HOST" true 2>/dev/null; do sleep 5; done

# Step 2: k3s with default traefik and local-path. tls-san lets the Mac use $API_HOST.
"${SSH[@]}" "$HOST" bash -s -- "$API_HOST" <<'REMOTE'
set -euo pipefail
sudo mkdir -p /etc/rancher/k3s
printf 'tls-san:\n  - %s\n' "$1" | sudo tee /etc/rancher/k3s/config.yaml >/dev/null
if ! systemctl is-active --quiet k3s; then
  curl -sfL https://get.k3s.io | sudo INSTALL_K3S_EXEC="--write-kubeconfig-mode 644" sh -
fi
for _ in $(seq 1 60); do
  sudo k3s kubectl get nodes --no-headers 2>/dev/null | grep -q ' Ready' && break
  sleep 5
done
sudo k3s kubectl get nodes
REMOTE

# Step 3: copy kubeconfig to the Mac, pointing at the API_HOST name.
umask 077
mkdir -p "$(dirname "$KUBECONFIG_OUT")"
"${SSH[@]}" "$HOST" 'sudo cat /etc/rancher/k3s/k3s.yaml' \
  | sed -E "s#server: https://[^:]+:6443#server: https://$API_HOST:6443#" > "$KUBECONFIG_OUT"
chmod 600 "$KUBECONFIG_OUT"
KUBECONFIG="$KUBECONFIG_OUT" kubectl get nodes
