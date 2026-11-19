#!/usr/bin/env bash
# Create or update the bot auth Secrets in every relevant bot namespace.
# Values are never printed. Nothing is passed on a command line, so nothing shows in `ps`.
#
# Usage:
#   scripts/bots-auth.sh claude [TOKEN_FILE]
#       TOKEN_FILE holds the Claude OAuth token. Without it, the token is read from
#       the CLAUDE_CODE_OAUTH_TOKEN env var. Writes secret claude-auth (key
#       CLAUDE_CODE_OAUTH_TOKEN) into bot-ada, bot-marvin, bot-iris, bot-vex,
#       bot-chronicler.
#   scripts/bots-auth.sh codex [AUTH_JSON] [BOT...]
#       AUTH_JSON defaults to ~/.codex/auth.json. Writes secret codex-auth (key
#       auth.json) into bot-rex and bot-juno, or only the named bots. Give each bot its
#       own login (refresh tokens rotate, so sharing one makes them log each other out):
#         CODEX_HOME=~/.config/agent-town/codex-rex codex login
#
# Needs KUBECONFIG (for example ~/.kube/k3s-pi.yaml) in the environment.
set -euo pipefail

CLAUDE_NS=(bot-ada bot-marvin bot-iris bot-vex bot-chronicler)
CODEX_NS=(bot-rex bot-juno)

usage() { sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-2}"; }

[ $# -ge 1 ] || usage
mode="$1"; shift
tmp=""
cleanup() { [ -n "$tmp" ] && rm -f "$tmp"; return 0; }
trap cleanup EXIT

ensure_ns() {
  kubectl create namespace "$1" --dry-run=client -o yaml | kubectl apply -f - >/dev/null
}

apply_secret() {  # $1 = namespace, $2 = secret name, $3 = key, $4 = file path
  kubectl -n "$1" create secret generic "$2" --from-file="$3=$4" \
    --dry-run=client -o yaml | kubectl apply -f - >/dev/null
  echo "ok: $2 in $1"
}

case "$mode" in
  claude)
    if [ $# -ge 1 ]; then
      src="$1"
      [ -s "$src" ] || { echo "token file missing or empty: $src" >&2; exit 1; }
    else
      [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ] || { echo "set CLAUDE_CODE_OAUTH_TOKEN or pass a file" >&2; exit 1; }
      tmp="$(mktemp)"; chmod 600 "$tmp"
      printf '%s' "$CLAUDE_CODE_OAUTH_TOKEN" > "$tmp"
      src="$tmp"
    fi
    # Drop any CR/LF so the stored value is exactly the token (tokens never contain them).
    if LC_ALL=C grep -q '[[:cntrl:]]' "$src"; then
      tmp="${tmp:-$(mktemp)}"; chmod 600 "$tmp"
      tr -d '\r\n' < "$src" > "$tmp"; src="$tmp"
    fi
    for ns in "${CLAUDE_NS[@]}"; do
      ensure_ns "$ns"
      apply_secret "$ns" claude-auth CLAUDE_CODE_OAUTH_TOKEN "$src"
    done
    ;;
  codex)
    src="${1:-$HOME/.codex/auth.json}"; [ $# -ge 1 ] && shift
    [ -s "$src" ] || { echo "auth file missing or empty: $src" >&2; exit 1; }
    [ $# -ge 1 ] && CODEX_NS=("${@/#/bot-}")
    for ns in "${CODEX_NS[@]}"; do
      ensure_ns "$ns"
      apply_secret "$ns" codex-auth auth.json "$src"
    done
    ;;
  *) usage ;;
esac
