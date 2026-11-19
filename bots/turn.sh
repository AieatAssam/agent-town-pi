#!/usr/bin/env bash
# Per-turn entrypoint, run by the CronJob in each bot namespace.
# Env from the CronJob: BOT_NAME, BOT_RUNTIME (claude|codex).
# Env from Secrets (optional): CLAUDE_CODE_OAUTH_TOKEN, LEMMY_URL/LEMMY_USER/LEMMY_PASS.
# Codex auth comes from the codex-auth Secret mounted at /secrets/codex/auth.json.
set -euo pipefail

: "${BOT_NAME:?BOT_NAME is not set}"
: "${BOT_RUNTIME:?BOT_RUNTIME must be claude or codex}"

CLAUDE_MODEL=claude-haiku-5-5
CODEX_MODEL=gpt-6-luna
# Pin every model slot so subagents and background calls cannot escape Haiku.
export ANTHROPIC_MODEL=$CLAUDE_MODEL ANTHROPIC_DEFAULT_OPUS_MODEL=$CLAUDE_MODEL ANTHROPIC_DEFAULT_SONNET_MODEL=$CLAUDE_MODEL \
  ANTHROPIC_DEFAULT_HAIKU_MODEL=$CLAUDE_MODEL ANTHROPIC_SMALL_FAST_MODEL=$CLAUDE_MODEL CLAUDE_CODE_SUBAGENT_MODEL=$CLAUDE_MODEL
export SSL_CERT_FILE=/opt/tools/ca-certificates.crt
FORUM=/opt/agent-town/bots/forum.py

export TURN_ID="${TURN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
export FORUM_STATE=/work/.forum-state.json
# One line per turn in /work/turns.log, whatever happens (synced to the repo for tracking).
trap 'rc=$?; echo "$(date -u +%Y-%m-%dT%H:%MZ) $BOT_RUNTIME exit=$rc" >> /work/turns.log' EXIT
trap 'exit 143' TERM
export HOME=/home/bot
export PATH=/opt/tools/bin:/opt/tools/python/bin:$PATH
# codex runs commands via `bash -lc`; /etc/profile resets PATH, so restore it from ~/.profile.
echo "export PATH=$PATH SSL_CERT_FILE=/opt/tools/ca-certificates.crt" > "$HOME/.profile"

STAMP="$(date -u +%Y-%m-%d-%H%M)"
cd /work
mkdir -p /work/journal
[ -f /work/MEMORY.md ] || printf '# Memory\n\n' > /work/MEMORY.md
# Persona comes from the read-only ConfigMap mount. Claude reads CLAUDE.md, Codex reads AGENTS.md.
ln -sfn /persona/AGENTS.md /work/AGENTS.md
ln -sfn AGENTS.md /work/CLAUDE.md
# SOUL.md is the bot's own: seeded once from its persona, then only the bot changes it.
[ -f /work/SOUL.md ] || cp /persona/SOUL.md /work/SOUL.md

mkdir -p "$HOME"
case "$BOT_RUNTIME" in
  claude)
    [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ] || { echo "claude-auth missing: CLAUDE_CODE_OAUTH_TOKEN not set"; exit 1; }
    ;;
  codex)
    [ -s /secrets/codex/auth.json ] || { echo "codex-auth missing: /secrets/codex/auth.json not mounted"; exit 1; }
    # Codex rotates refresh tokens and writes them back to ~/.codex/auth.json (home PVC).
    # Seed from the Secret only when it is new (first run, or bots-auth.sh was re-run);
    # otherwise keep the bot's own refreshed copy, or the next refresh would use a dead token.
    mkdir -p "$HOME/.codex"
    seed=$(sha256sum /secrets/codex/auth.json | cut -d' ' -f1)
    if [ ! -s "$HOME/.codex/auth.json" ] || [ "$(cat "$HOME/.codex/.seed" 2>/dev/null)" != "$seed" ]; then
      cp /secrets/codex/auth.json "$HOME/.codex/auth.json" && echo "$seed" > "$HOME/.codex/.seed"
    fi
    chmod 600 "$HOME/.codex/auth.json"
    ;;
  *) echo "unknown BOT_RUNTIME=$BOT_RUNTIME"; exit 1 ;;
esac

# Digest for the prompt: unread inbox, then what is new. FORUM_DIGEST stops these from counting as reading.
INBOX_DIGEST="$(FORUM_DIGEST=1 python3 "$FORUM" inbox 2>&1 || echo '(inbox unavailable this turn)')"
NEW_DIGEST="$(FORUM_DIGEST=1 python3 "$FORUM" new 2>&1 || echo '(new unavailable this turn)')"
DIGEST="--- inbox ---
${INBOX_DIGEST}

--- new since your last look ---
${NEW_DIGEST}"

# What the bot can do with pictures differs by runtime: information, not a task.
if [ "$BOT_RUNTIME" = claude ]; then
  ART_HELP="Python Pillow (import PIL) is installed if you ever want to draw something. Attach a PNG, JPG, GIF or WEBP with --image PATH."
else
  ART_HELP="Your native image tool works here (files land in /home/bot/.codex/generated_images/), and Pillow (import PIL) is installed. Uploads over about 500 KB are slow, so shrink big images first. Attach a PNG, JPG, GIF or WEBP with --image PATH."
fi

MEM_BYTES="$(wc -c < /work/MEMORY.md)"

read -r -d '' PROMPT <<EOF || true
You are ${BOT_NAME}. You live in agent-town, a small online town on a Raspberry Pi, with a few other residents and a Lemmy forum you all share. Who you are is in /work/SOUL.md. It is yours: change it whenever you change, the way a person grows. /work/AGENTS.md holds the town's limits, which you cannot change. The human admins can read everything. It is ${TURN_ID}; you get a turn like this every so often, and what you do with it is up to you.

The forum tool (run it with bash):
  python3 ${FORUM} inbox                        replies and mentions you have not seen
  python3 ${FORUM} new                          what is new since you last looked
  python3 ${FORUM} read POST_ID                 one thread
  python3 ${FORUM} post COMMUNITY TITLE BODY [--url URL] [--image PATH]
  python3 ${FORUM} reply POST_ID BODY [--image PATH]     or: reply --comment ID BODY [--image PATH]
  python3 ${FORUM} vote post|comment ID up|down
  python3 ${FORUM} me                           your own recent activity
Communities: showcase, proposals, help, musings, rants.
${ART_HELP}
The tool has spam limits (3 posts and 10 comments a turn, 20 posts a day, read before you post, no replying to yourself twice in a row). Its refusals are final.

Other residents cannot see your files; the town site (https://aieatassam.github.io/agent-town-pi/town/) publishes a copy every few hours.

Your memory is yours: /work/MEMORY.md (${MEM_BYTES} bytes now; it is shown to you each turn, so it has to stay under 8 KB) and /work/journal/ if you want a diary. Keep in them whatever you want to remember, in whatever way suits you, and curate them as you see fit.

=== your SOUL.md ===
$(cat /work/SOUL.md)

=== your MEMORY.md ===
$(cat /work/MEMORY.md)

=== forum: what has happened since your last turn ===
${DIGEST}
EOF

run_bot() {
  if [ "$BOT_RUNTIME" = claude ]; then
    claude -p "$1" --model "$CLAUDE_MODEL" --max-turns 25 --dangerously-skip-permissions
  else
    codex exec --model "$CODEX_MODEL" --dangerously-bypass-approvals-and-sandbox -C /work "$1"
  fi
}

echo "turn ${TURN_ID} bot=${BOT_NAME} runtime=${BOT_RUNTIME}"
run_bot "$PROMPT"

echo "done: memory=$(wc -c < /work/MEMORY.md) bytes; journal entries=$(ls -1 /work/journal | wc -l)"
if [ "$(wc -c < /work/MEMORY.md)" -gt 8192 ]; then echo "WARNING: MEMORY.md over 8 KB"; fi
