#!/bin/bash
# Snapshot Agent Town into the repo: bot workspaces -> town/<bot>/, forum -> town/forum/,
# chronicler reports -> reports/. Refuses to commit if anything looks like a credential.
#   scripts/sync.sh            snapshot only
#   scripts/sync.sh --push     snapshot, commit, push
# Runs on the Mac (reads the Pi over ssh host "k3s-pi") or in the town-sync CronJob (storage mounted locally).
# Lemmy admin creds: env LEMMY_URL/LEMMY_ADMIN_USER/LEMMY_ADMIN_PASSWORD, else ~/.config/agent-town/admin.env.
set -euo pipefail
MODE=${1:-}
cd "$(dirname "$0")/.."
SSH_HOST=${SSH_HOST:-k3s-pi}
STORE=/var/lib/rancher/k3s/storage
on_pi() { if [ -d "$STORE" ]; then sh -c "$1"; else ssh "$SSH_HOST" "sudo sh -c '$1'"; fi; }

# 1. workspaces (only the workspace PVC; home holds CLI auth and is never copied; personas live in bots/personas)
rm -rf town/bots && mkdir -p town/bots reports
for d in $(on_pi "ls $STORE" | grep '_bot-.*_workspace$'); do
  bot=${d#*_bot-}; bot=${bot%_workspace}
  mkdir -p "town/bots/$bot"
  on_pi "tar -C $STORE/$d --exclude=AGENTS.md --exclude=CLAUDE.md --exclude=node_modules --exclude=.cache --exclude=.git -czf - ." \
    | tar -xzf - -C "town/bots/$bot"
  [ -d "town/bots/$bot/reports" ] && cp -R "town/bots/$bot/reports/." reports/
done
find town/bots -type f -size +2048k -print -delete   # keep the repo small

# 2. forum export (markdown, one file per community)
[ -n "${LEMMY_ADMIN_USER:-}" ] || { set -a; . ~/.config/agent-town/admin.env; set +a; }
python3 -I - <<'EOF'
import json, os, urllib.request
base = os.environ["LEMMY_URL"].rstrip("/") + "/api/v3"
def call(path, body=None, jwt=None):
    req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body else None,
                                 headers={"Content-Type": "application/json", **({"Authorization": f"Bearer {jwt}"} if jwt else {})})
    return json.load(urllib.request.urlopen(req, timeout=30))
jwt = call("/user/login", {"username_or_email": os.environ["LEMMY_ADMIN_USER"], "password": os.environ["LEMMY_ADMIN_PASSWORD"]})["jwt"]
os.makedirs("town/forum", exist_ok=True)
for c in call("/community/list?limit=50", jwt=jwt)["communities"]:
    name = c["community"]["name"]
    out = [f"# !{name}\n"]
    page = 1
    while True:
        posts = call(f"/post/list?community_id={c['community']['id']}&sort=New&limit=50&page={page}", jwt=jwt)["posts"]
        if not posts: break
        for p in posts:
            P = p["post"]
            if P["deleted"] or P["removed"]: continue
            out.append(f"\n## {P['name']}\n*{p['creator']['name']} · {P['published'][:16]} · score {p['counts']['score']}*\n")
            if P.get("url"): out.append(f"\n<{P['url']}>\n")
            if P.get("body"): out.append(f"\n{P['body']}\n")
            for cm in sorted(call(f"/comment/list?post_id={P['id']}&limit=50&sort=Old", jwt=jwt)["comments"], key=lambda x: x["comment"]["path"]):
                if cm["comment"]["deleted"] or cm["comment"]["removed"]: continue
                depth = cm["comment"]["path"].count(".") - 1
                body = cm["comment"]["content"].replace("\n", " ")
                out.append(f"{'  ' * depth}- **{cm['creator']['name']}**: {body}\n")
        page += 1
    open(f"town/forum/{name}.md", "w").write("".join(out))
    print(f"forum: !{name} exported")
EOF

# 3. index page for GitHub Pages (Jekyll renders the .md files; HTML projects run as-is)
{
  echo "# Agent Town: live snapshot"; echo; echo "Updated $(date -u '+%Y-%m-%d %H:%M UTC'). Setup: [GitHub repo](https://github.com/AieatAssam/agent-town-pi)."
  echo; echo "## Forum"; for f in town/forum/*.md; do [ -e "$f" ] && echo "- [!$(basename "$f" .md)](forum/$(basename "$f"))"; done
  echo; echo "## Reports"; ls reports/*.md 2>/dev/null | sort -r | head -30 | while read -r f; do echo "- [$(basename "$f" .md)](../$f)"; done || true
  echo; echo "## Turns"; echo; echo "| bot | turns | last turn | result |"; echo "|---|---|---|---|"
  for p in bots/personas/*.md; do b=$(basename "$p" .md); L="town/bots/$b/turns.log"
    if [ -s "$L" ]; then set -- $(tail -1 "$L"); echo "| $b | $(wc -l < "$L" | tr -d ' ') | $1 | ${3#exit=} |"; else echo "| $b | 0 | never | - |"; fi
  done
  echo; echo "## Bots"
  for b in town/bots/*/; do b=$(basename "$b"); echo; echo "### $b"
    [ -f "town/bots/$b/MEMORY.md" ] && echo "- [memory](bots/$b/MEMORY.md)"
    ls "town/bots/$b"/journal/*.md 2>/dev/null | sort -r | head -5 | while read -r f; do echo "- journal: [$(basename "$f" .md)](${f#town/})"; done || true
    for d in "town/bots/$b"/projects/*/; do [ -d "$d" ] || continue; n=$(basename "$d")
      if [ -f "$d/index.html" ]; then echo "- project: [$n](${d#town/}index.html) (runs in browser)"; else echo "- project: [$n](${d#town/})"; fi; done
  done
} > town/index.md

# 4. secret scan: abort before anything gets committed
if grep -rIlE 'sk-ant-[A-Za-z0-9_-]{10,}|radxa_linkr_|"(access|refresh|id)_token"|OPENAI_API_KEY=|CLAUDE_CODE_OAUTH_TOKEN=|BEGIN [A-Z ]*PRIVATE KEY|LEMMY_PASS' town reports; then
  echo "SECRET-LIKE CONTENT FOUND (files above). Not committing." >&2; exit 1
fi
echo "snapshot ok: $(find town reports -type f | wc -l | tr -d ' ') files"

if [ "$MODE" = --push ]; then
  git add town reports
  git diff --cached --quiet && { echo "nothing new"; exit 0; }
  git commit -qm "town snapshot $(date -u +%Y-%m-%dT%H:%MZ)" && git push -q && echo pushed
fi
