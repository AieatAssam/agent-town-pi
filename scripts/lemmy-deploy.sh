#!/usr/bin/env bash
# Deploys the Lemmy stack (k8s/lemmy) to the k3s cluster. Run from the Mac. Re-runnable.
#
# Secrets live only in the cluster:
#   lemmy-secrets  generated once (random), never regenerated, so the Postgres
#                  password keeps matching the existing data directory.
#   lemmy-config   the rendered lemmy.hjson (k8s/lemmy/lemmy.hjson.tmpl with the
#                  secret values filled in). Re-rendered on every run.
set -euo pipefail

export KUBECONFIG="${KUBECONFIG:-$HOME/.kube/k3s-pi.yaml}"
NS=town-square
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if kubectl -n "$NS" get secret lemmy-secrets >/dev/null 2>&1; then
  echo "secret lemmy-secrets exists, keeping it"
else
  echo "creating secret lemmy-secrets (random values, not printed)"
  # create (not apply) fed on stdin: no plaintext in argv or last-applied annotations
  kubectl -n "$NS" create -f - <<YAML
apiVersion: v1
kind: Secret
metadata:
  name: lemmy-secrets
  namespace: $NS
type: Opaque
stringData:
  postgres-password: "$(openssl rand -hex 24)"
  pictrs-api-key: "$(openssl rand -hex 24)"
  admin-password: "$(openssl rand -hex 24)"
YAML
fi

secret_val() { kubectl -n "$NS" get secret lemmy-secrets -o "jsonpath={.data.$1}" | base64 -d; }
render() {
  sed -e "s|__POSTGRES_PASSWORD__|$(secret_val postgres-password)|" \
      -e "s|__PICTRS_API_KEY__|$(secret_val pictrs-api-key)|" \
      -e "s|__ADMIN_PASSWORD__|$(secret_val admin-password)|" \
      "$ROOT/k8s/lemmy/lemmy.hjson.tmpl"
}

kubectl -n "$NS" delete secret lemmy-config --ignore-not-found >/dev/null
kubectl -n "$NS" create secret generic lemmy-config --from-file=lemmy.hjson=<(render)

kubectl apply -k "$ROOT/k8s/lemmy"
kubectl -n "$NS" rollout restart deploy/lemmy >/dev/null

for d in postgres pictrs lemmy lemmy-ui; do
  kubectl -n "$NS" rollout status "deploy/$d" --timeout=300s
done
echo "lemmy stack is up. Next: scripts/lemmy-bootstrap.sh"
