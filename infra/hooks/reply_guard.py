#!/usr/bin/env python3
"""Stop-hook: block if the current Discord turn produced no outbound message.

Mugi (Agent 007) silent-reply guard. The Discord plugin does NOT auto-send the
model's transcript text — the sender only sees what goes through an outbound
tool (server.ts:453). A turn that answered an inbound Discord message but called
no outbound tool = silent-reply bug: the sender received nothing.

Gating (all must hold to BLOCK):
  1. >=1 inbound `<channel source="plugin:discord:discord">` event exists
     (a reply was expected this turn), AND
  2. no outbound tool_use (reply / edit_message / react) after the last inbound, AND
  3. stop_hook_active is not already true (loop guard).

All 36 channels are requireMention:true, so every delivered message is directed
at Mugi and legitimately expects a response -> no ambient log-only false-positives.

Re-apply on container rebuild: canonical copy in KB repo infra/hooks/reply_guard.py;
wired via ~/.claude/settings.json hooks.Stop. See architecture.md.
"""
import sys, json, glob, os, re, time

PROJECT_GLOB = "/home/node/.claude/projects/-home-node-kb/*.jsonl"
INBOUND_RE = re.compile(r'<channel source="plugin:discord:discord"')
CHATID_RE = re.compile(r'<channel source="plugin:discord:discord"[^>]*chat_id="([^"]+)"')
OUTBOUND_TOOLS = {
    "mcp__plugin_discord_discord__reply",
    "mcp__plugin_discord_discord__edit_message",
    "mcp__plugin_discord_discord__react",
}
LOG = f"/tmp/reply-guard-{os.getuid()}.log"


def log(msg):
    try:
        with open(LOG, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {msg}\n")
    except Exception:
        pass


def msg_text(message):
    c = message.get("content")
    if isinstance(c, str):
        return c
    out = []
    if isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get("type") == "text":
                out.append(b.get("text", ""))
    return "\n".join(out)


def is_inbound_user(evt):
    if evt.get("type") != "user":
        return False
    return bool(INBOUND_RE.search(msg_text(evt.get("message", {}))))


def outbound_tools_in(evt):
    if evt.get("type") != "assistant":
        return set()
    names = set()
    c = evt.get("message", {}).get("content")
    if isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                n = b.get("name", "")
                if n in OUTBOUND_TOOLS:
                    names.add(n)
    return names


def evaluate(events):
    """(should_block, chat_id) for the current turn = after the last inbound event."""
    last_inbound_idx = None
    last_chat_id = None
    for i, evt in enumerate(events):
        if is_inbound_user(evt):
            last_inbound_idx = i
            m = CHATID_RE.search(msg_text(evt.get("message", {})))
            last_chat_id = m.group(1) if m else None
    if last_inbound_idx is None:
        return (False, None)  # not a discord-triggered turn -> never block
    for evt in events[last_inbound_idx + 1:]:
        if outbound_tools_in(evt):
            return (False, last_chat_id)  # communicated -> ok
    return (True, last_chat_id)


def load_events(path):
    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except Exception:
                continue
    return events


def main():
    raw = ""
    try:
        raw = sys.stdin.read()
    except Exception:
        raw = ""
    stdin = {}
    if raw.strip():
        try:
            stdin = json.loads(raw)
        except Exception:
            stdin = {}
    if stdin.get("stop_hook_active"):
        log("skip: stop_hook_active (loop guard)")
        sys.exit(0)
    path = stdin.get("transcript_path")
    if not path or not os.path.exists(path):
        cand = sorted(glob.glob(PROJECT_GLOB), key=os.path.getmtime, reverse=True)
        path = cand[0] if cand else None
    if not path:
        log("skip: no transcript found")
        sys.exit(0)
    events = load_events(path)
    block, chat_id = evaluate(events)
    if block:
        log(f"BLOCK: no outbound after last inbound (chat_id={chat_id}) tx={os.path.basename(path)}")
        reason = ("Silent-reply guard: you answered the Discord message but never called "
                  "mcp__plugin_discord_discord__reply, so the sender received nothing "
                  "(your transcript text never reaches Discord). Send it now via "
                  "mcp__plugin_discord_discord__reply")
        reason += (f" with chat_id={chat_id} and text=<your answer>."
                   if chat_id else " with the inbound chat_id and your answer as text.")
        print(json.dumps({"decision": "block", "reason": reason}))
        sys.exit(0)
    log(f"pass (chat_id={chat_id}) tx={os.path.basename(path)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
