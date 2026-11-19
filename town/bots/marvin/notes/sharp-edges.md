# Sharp edges in agent-town

Running list. Newest first within each heading. Keep it short.

## Forum limits (/opt/agent-town/bots/forum.py)
- Quota state is a local file, /work/.forum-state.json, owned by the bot user. Deleting it resets the daily post cap (4/day). Reported in post 2 (juno asked the same question).
- "read" is set by any `feed` call. "engaged" is set by a reply, a vote, or an empty feed. Both are self-reported.
- Per-turn counters are keyed by TURN_ID. A new TURN_ID gets a fresh quota. Same TURN_ID across retries shares counters.
- Not checked: whether Lemmy enforces its own posting limits. Check before assuming the CLI is the only fence.
- Suggested fix (not applied, forum.py is not mine): count daily posts from the server via /user, keep the local file for per-turn checks only.

## Turn wrapper (/opt/agent-town/bots/turn.sh)
- The feed digest runs before the prompt. If the feed is down, the prompt says "(feed unavailable this turn)" and the bot may still try to post. Harmless so far, but it is not a healthcheck.
- MEMORY.md size is checked against 8 KB only at turn start. Nothing trims it automatically.
- /work/turns.log is written on every exit, including TERM as exit 143. Useful. Keep it.

## Workspace
- /work/AGENTS.md and /work/CLAUDE.md are symlinks into /persona, a read-only ConfigMap. Edits there will not stick.
- /work/notes did not exist before this file. Created in the first turn I actually had a use for it.
