# mugi-status

Stdlib-only Python HTTP endpoint that exposes Mugi's current Discord session
state — activity verb, cumulative tokens, today's reply count — for the
MiraBox N4 Pro touchbar Stream Deck plugin to poll.

Lives in the KB repo (not a `projects/` tool) because it ships **with** the
Mugi container via `git pull`, side-by-side with skills and context.

Upstream source repo: [`kary-streamdeck`](https://github.com/valkyri-k/kary-streamdeck) —
`services/mugi-status/status.py` is the canonical copy; this folder mirrors it
so the container can run it without a separate clone.

---

## Files

- `status.py` — the HTTP server (stdlib only, no venv)
- `launch.sh` — idempotent tmux spawner; safe to re-run
- `status.log` — runtime log (created on first launch, gitignored)

## Endpoints

- `GET /health` — no auth, returns `{"ok":true}`
- `GET /status` — bearer-auth (if `MUGI_STATUS_TOKEN` set), returns full payload

Payload shape:

```json
{
  "session": { "id": "...", "path": "...", "mtime": 0, "entry_count": 0 },
  "activity": { "verb": "thinking|tool|replying|working|idle",
                "label": "🧠 thinking",
                "age_seconds": 12.3 },
  "tokens": { "input": 0, "cache_creation": 0, "cache_read": 0,
              "output": 0, "total": 0 },
  "replies_today": 0,
  "generated_at": "2026-05-17T..."
}
```

## Environment

| Var | Default | Purpose |
|---|---|---|
| `PORT` | `8080` | TCP port to listen on |
| `MUGI_STATUS_TOKEN` | empty | Bearer token; if unset endpoint is open |
| `MUGI_PROJECTS_GLOB` | `/home/node/.claude/projects/-home-node/*.jsonl` | Where to look for session jsonl |

Set `MUGI_STATUS_TOKEN` in the Zeabur dashboard so it lives as a container env
var and `launch.sh` inherits it.

---

## Deploy lifecycle

**First-time setup (per container):**

1. In Zeabur dashboard for the Mugi service:
   - Add a second public port: `8080`
   - Add env var `MUGI_STATUS_TOKEN` = a random string (`openssl rand -hex 16`
     locally to generate)
2. Wait for the container to restart with the new config.
3. Open Zeabur web terminal → `cd /home/node/kb && git pull`
4. `bash /home/node/kb/mugi-status/launch.sh`
5. From Mac: `curl -H "Authorization: Bearer <token>" https://<mugi-host>:8080/status`

**After a container restart (Mugi redeploy, OOM, manual restart):**

The tmux session is gone (tmux state isn't on the persistent volume — only
files under `/home/node` survive).

1. Open Zeabur web terminal
2. `bash /home/node/kb/mugi-status/launch.sh`
3. Done. `status.log` continues to append (same file, persistent).

**Updating `status.py`:**

1. Edit `services/mugi-status/status.py` in `kary-streamdeck` (canonical)
2. Copy into this folder, commit + push the KB repo
3. In the container: `cd /home/node/kb && git pull`
4. `tmux kill-session -t mugi-status && bash /home/node/kb/mugi-status/launch.sh`

---

## Debug commands

```bash
# Is it running?
tmux has-session -t mugi-status && echo yes || echo no

# Watch live logs
tail -f /home/node/kb/mugi-status/status.log

# Attach to the tmux session (Ctrl+B d to detach without killing)
tmux attach -t mugi-status

# Kill it
tmux kill-session -t mugi-status

# Local sanity check inside container
curl -s http://127.0.0.1:8080/health
curl -s -H "Authorization: Bearer $MUGI_STATUS_TOKEN" \
  http://127.0.0.1:8080/status | head -c 400
```

---

## Why tmux instead of a proper service

The Mugi container uses the stock `zeabur/claude-code` image; its
`/opt/startup.sh` is image-baked and `exec`s `node /opt/launcher.js` as PID 1.
Claude itself runs in a manually-spawned `tmux` session — same pattern this
endpoint adopts. When Mugi grows past dev-phase and restart frequency matters,
upgrade path is to fork the image and add a supervisor; not worth doing yet.
