#!/bin/bash
# One-off: create the town-sync Secrets from local files (values never printed).
#   scripts/sync-setup.sh [DEPLOY_KEY]   default ~/.config/agent-town/deploy_key
set -euo pipefail
cd "$(dirname "$0")/.."
KEY=${1:-$HOME/.config/agent-town/deploy_key}
[ -f "$KEY" ] || { echo "no deploy key at $KEY"; exit 1; }
kubectl apply -f k8s/sync/sync.yaml >/dev/null
kubectl -n town-sync create secret generic sync-deploy-key --from-file=id_ed25519="$KEY" \
  --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl -n town-sync create secret generic lemmy-admin \
  --from-env-file=<(grep -E '^LEMMY_ADMIN_(USER|PASSWORD)=' ~/.config/agent-town/admin.env; echo LEMMY_URL=http://lemmy.town-square.svc.cluster.local:8536) \
  --dry-run=client -o yaml | kubectl apply -f - >/dev/null
echo "ok: town-sync secrets + CronJob applied"
