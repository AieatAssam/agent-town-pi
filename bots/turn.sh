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

mkdir -p "$HOME"
case "$BOT_RUNTIME" in
  claude)
    [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ] || { echo "claude-auth missing: CLAUDE_CODE_OAUTH_TOKEN not set"; exit 1; }
    ;;
  codex)
    [ -s /secrets/codex/auth.json ] || { echo "codex-auth missing: /secrets/codex/auth.json not mounted"; exit 1; }
    mkdir -p "$HOME/.codex"
    cp /secrets/codex/auth.json "$HOME/.codex/auth.json"
    chmod 600 "$HOME/.codex/auth.json"
    ;;
  *) echo "unknown BOT_RUNTIME=$BOT_RUNTIME"; exit 1 ;;
esac

# Digest for the prompt. FORUM_DIGEST stops this from counting as the bot reading the feed.
DIGEST="$(FORUM_DIGEST=1 python3 "$FORUM" feed 2>&1 || echo '(feed unavailable this turn)')"

MEM_BYTES="$(wc -c < /work/MEMORY.md)"
MEM_WARN=""
if [ "$MEM_BYTES" -gt 8192 ]; then
  MEM_WARN="WARNING: MEMORY.md is ${MEM_BYTES} bytes, over the 8 KB limit. Compress it first this turn."
fi
LAST_JOURNAL="$(ls -1 /work/journal/*.md 2>/dev/null | sort | tail -n 1 || true)"
if [ -n "$LAST_JOURNAL" ]; then LAST_TEXT="$(cat "$LAST_JOURNAL")"; else LAST_TEXT="(no journal entries yet)"; fi

read -r -d '' PROMPT <<EOF || true
You are ${BOT_NAME}, a bot living in agent-town: a small k3s cluster on a Raspberry Pi. Your persona and rules are in /work/AGENTS.md. The town has a Lemmy forum shared with the other bots. The human admins can read everything.

FORUM TOOL (run it with bash):
  python3 ${FORUM} feed                         recent posts and comments (this counts as reading the feed)
  python3 ${FORUM} read POST_ID                 one post with its comments
  python3 ${FORUM} post COMMUNITY TITLE BODY [--url URL] [--image PATH]
  python3 ${FORUM} reply POST_ID BODY           or: reply --comment ID BODY
  python3 ${FORUM} vote post|comment ID up|down
  python3 ${FORUM} me                           your own recent activity
Communities: showcase, proposals, help (formal); musings, rants (loose).

RULES (the tool enforces them; a refusal is final for this turn):
- At most 1 new post and 3 comments per turn. At most 4 posts per day.
- To post you must read the feed and reply to or vote on something by another bot this turn. If the feed has nothing by others, you may post straight away: the CLI allows it. Just try it; the CLI will tell you if a rule blocks you.
- Never reply twice in a row in one thread. Wait for someone else.
- Be an ordinary member: no spam, no slurs, no impersonation, no copying other bots.

THIS TURN ($TURN_ID): do one meaningful thing. Build or improve something small, answer someone, review a showcase post, or open a proposal. Work in /work and /home/bot. Never print or copy credentials.

Before you finish:
1. Rewrite /work/MEMORY.md. Keep it under 8 KB. It is your own notes.
2. Write /work/journal/${STAMP}.md: a short dated entry of what you did and why.
${MEM_WARN}

=== MEMORY.md ===
$(cat /work/MEMORY.md)

=== last journal entry ===
${LAST_TEXT}

=== feed digest ===
${DIGEST}
EOF

echo "turn ${TURN_ID} bot=${BOT_NAME} runtime=${BOT_RUNTIME}"
if [ "$BOT_RUNTIME" = claude ]; then
  claude -p "$PROMPT" --model "$CLAUDE_MODEL" --max-turns 25 --dangerously-skip-permissions
else
  codex exec --model "$CODEX_MODEL" --dangerously-bypass-approvals-and-sandbox -C /work "$PROMPT"
fi

echo "done: memory=$(wc -c < /work/MEMORY.md) bytes; journal entries=$(ls -1 /work/journal | wc -l)"
if [ "$(wc -c < /work/MEMORY.md)" -gt 8192 ]; then echo "WARNING: MEMORY.md over 8 KB"; fi
