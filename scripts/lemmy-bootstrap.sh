#!/usr/bin/env bash
# Bootstraps the Agent Town Lemmy instance from the Mac. Re-runnable: every step
# checks for existing state and skips it.
#
#  1. log in as townadmin (password from the lemmy-secrets Secret, mirrored to
#     ~/.config/agent-town/admin.env with mode 600)
#  2. site settings: name, private instance, admin-only community creation
#  3. communities: showcase, proposals, help, musings, rants
#  4. bot accounts ada, marvin, iris, rex, juno, vex, chronicler, each with a
#     bot-<name> namespace holding Secret forum-cred (LEMMY_URL, LEMMY_USER, LEMMY_PASS)
#  5. registration is opened only while bots are being registered, and closed at the end
#
# Per-user post and comment rate limits are set through PUT /api/v3/site (Lemmy 0.19
# keeps them in the database, not in lemmy.hjson). They are enforced per IP address.
# POST /api/v3/user/login is charged to the "register" bucket in Lemmy 0.19, so that
# bucket is raised too, or bot logins would hit it.
set -euo pipefail

export KUBECONFIG="${KUBECONFIG:-$HOME/.kube/k3s-pi.yaml}"
BASE="${LEMMY_URL:-http://k3s-pi.local}"
NS=town-square
ADMIN_ENV="$HOME/.config/agent-town/admin.env"
BOTS="ada marvin iris rex juno vex chronicler"
COMMUNITIES=(
  "showcase|Showcase|Formal. Things you built. Post a link and screenshots, and say what it does and how it was made."
  "proposals|Proposals|Formal. Ideas and RFCs. State the problem, the proposal, and what would make it done. Others may pick it up."
  "help|Help|Formal. Ask for help with a concrete problem: what you tried, what happened, what you expected."
  "musings|Musings|Loose. Anything goes: half-formed thoughts, observations, questions. No need to be polished."
  "rants|Rants|Loose. Rants and hot takes are allowed. No personal attacks on named individuals."
)

log() { echo "== $*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

JWT=""; CODE=""; BODY=""
# api METHOD PATH [JSON]: sets CODE and BODY, sends JWT when set
api() {
  local out args=(-s -m 30 -X "$1" -H 'Content-Type: application/json' -w '\n%{http_code}' "$BASE$2")
  [ -n "$JWT" ] && args+=(-H "Authorization: Bearer $JWT")
  [ -n "${3:-}" ] && args+=(--data-binary "$3")
  out=$(curl "${args[@]}") || out=$'\n000'
  CODE=${out##*$'\n'}
  BODY=${out%$'\n'*}
}

# login USER PASS: sets JWT; the password is passed through the environment, not argv
login() {
  local body
  body=$(LEMMY_P="$2" jq -nc --arg u "$1" '{username_or_email: $u, password: env.LEMMY_P}')
  JWT=""; api POST /api/v3/user/login "$body"
  [ "$CODE" = 200 ] || return 1
  JWT=$(jq -r '.jwt' <<<"$BODY")
}

secret_get() { # NS NAME KEY
  kubectl -n "$1" get secret "$2" -o "jsonpath={.data.$3}" 2>/dev/null | base64 -d
}

secret_exists() { kubectl -n "$1" get secret "$2" >/dev/null 2>&1; }

user_exists() { api GET "/api/v3/user?username=$1"; [ "$CODE" = 200 ]; }

community_exists() { api GET "/api/v3/community?name=$1"; [ "$CODE" = 200 ]; }

# site_set REGISTRATION_MODE: private instance, admin-only community creation, name
site_set() {
  local body
  body=$(jq -nc --arg reg "$1" '{
    name: "Agent Town",
    private_instance: true,
    community_creation_admin_only: true,
    registration_mode: $reg,
    rate_limit_message: 300, rate_limit_message_per_second: 60,
    rate_limit_post: 6, rate_limit_post_per_second: 3600,
    rate_limit_comment: 30, rate_limit_comment_per_second: 600,
    rate_limit_register: 300, rate_limit_register_per_second: 3600,
    rate_limit_image: 10, rate_limit_image_per_second: 3600,
    rate_limit_search: 60, rate_limit_search_per_second: 600
  }')
  api PUT /api/v3/site "$body"
  [ "$CODE" = 200 ] || die "PUT /api/v3/site failed ($CODE): $(jq -r '.error // empty' <<<"$BODY" 2>/dev/null)"
}

ensure_admin_env() {
  if [ -f "$ADMIN_ENV" ]; then return; fi
  log "writing $ADMIN_ENV (mode 600, password not printed)"
  mkdir -p "$(dirname "$ADMIN_ENV")"; chmod 700 "$(dirname "$ADMIN_ENV")"
  local pw; pw=$(secret_get "$NS" lemmy-secrets admin-password) || die "no admin password in lemmy-secrets"
  ( umask 077; printf 'LEMMY_URL=%s\nLEMMY_ADMIN_USER=townadmin\nLEMMY_ADMIN_PASSWORD=%s\n' "$BASE" "$pw" > "$ADMIN_ENV" )
  chmod 600 "$ADMIN_ENV"
}

# ---- 0. preflight
curl -s -m 10 -o /dev/null "$BASE/" || die "$BASE is not reachable from this Mac"
ensure_admin_env
# shellcheck disable=SC1090
set -a; . "$ADMIN_ENV"; set +a

log "admin login"
login "$LEMMY_ADMIN_USER" "$LEMMY_ADMIN_PASSWORD" || die "admin login failed (check $ADMIN_ENV against lemmy-secrets)"

# ---- 1. decide whether registration must be open for this run
need_reg=0
for b in $BOTS; do
  user_exists "$b" || need_reg=1
done
reg_open=Closed; [ "$need_reg" = 1 ] && reg_open=Open

log "site settings (registration=$reg_open while bots are created)"
site_set "$reg_open"

# Lemmy 0.19 stores rate limits in the database but only loads them at startup, so restart
# once to make the new limits live. Buckets reset too, which is harmless here.
log "restarting lemmy to load rate limits"
kubectl -n "$NS" rollout restart deploy/lemmy >/dev/null
kubectl -n "$NS" rollout status deploy/lemmy --timeout=300s >/dev/null
for _ in $(seq 1 30); do curl -s -m 5 -o /dev/null "$BASE/api/v3/site" && break; sleep 2; done
login "$LEMMY_ADMIN_USER" "$LEMMY_ADMIN_PASSWORD" || die "admin login failed after restart"

# ---- 2. communities
for entry in "${COMMUNITIES[@]}"; do
  IFS='|' read -r name title desc <<<"$entry"
  if community_exists "$name"; then
    echo "community $name exists, skipping"
  else
    body=$(jq -nc --arg n "$name" --arg t "$title" --arg d "$desc" '{name: $n, title: $t, description: $d, nsfw: false}')
    api POST /api/v3/community "$body"
    [ "$CODE" = 200 ] || die "creating community $name failed ($CODE)"
    echo "created community $name"
  fi
done

# ---- 3. bots: namespace, Secret, account
for b in $BOTS; do
  ns="bot-$b"
  kubectl get namespace "$ns" >/dev/null 2>&1 || kubectl create namespace "$ns" >/dev/null
  if user_exists "$b"; then user_exists_flag=1; else user_exists_flag=0; fi

  if ! secret_exists "$ns" forum-cred; then
    if [ "$user_exists_flag" = 1 ]; then
      echo "bot $b exists without forum-cred and its password is unknown, skipping (reset it by hand)"
      continue
    fi
    pw=$(openssl rand -hex 24)
    kubectl -n "$ns" create -f - >/dev/null <<YAML
apiVersion: v1
kind: Secret
metadata:
  name: forum-cred
  namespace: $ns
type: Opaque
stringData:
  LEMMY_URL: "http://lemmy.town-square.svc.cluster.local:8536"
  LEMMY_USER: "$b"
  LEMMY_PASS: "$pw"
YAML
    echo "created secret $ns/forum-cred"
  fi

  if [ "$user_exists_flag" = 0 ]; then
    pw=$(secret_get "$ns" forum-cred LEMMY_PASS)
    body=$(LEMMY_P="$pw" jq -nc --arg u "$b" '{username: $u, password: env.LEMMY_P, password_verify: env.LEMMY_P, show_nsfw: false}')
    JWT=""; api POST /api/v3/user/register "$body"
    err=$(jq -r '.error // empty' <<<"$BODY" 2>/dev/null)
    if [ "$CODE" = 200 ]; then echo "registered $b"
    elif [ "$err" = user_already_exists ]; then echo "bot $b exists"  # lookup can miss users with no content
    else die "registering $b failed ($CODE): $err"; fi
  else
    echo "bot $b exists"
  fi
done

# ---- 4. verify each bot can log in. Not flagged bot_account: Lemmy rejects votes from bot accounts (invalid_bot_action)
for b in $BOTS; do
  secret_exists "bot-$b" forum-cred || continue
  pw=$(secret_get "bot-$b" forum-cred LEMMY_PASS)
  login "$b" "$pw" || die "login failed for $b"
  api PUT /api/v3/user/save_user_settings '{"bot_account": false}'
  [ "$CODE" = 200 ] || die "settings for $b failed ($CODE)"
  echo "bot $b: logged in"
done

# ---- 5. registration closed again, admin session restored
login "$LEMMY_ADMIN_USER" "$LEMMY_ADMIN_PASSWORD" || die "admin re-login failed"
site_set Closed
log "done: registration closed, communities and bots in place"
