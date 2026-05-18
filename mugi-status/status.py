"""Mugi Discord session /status endpoint.

Reads Claude Code session jsonl from the Mugi container, finds the
most-recently-modified Discord-active session, and returns activity
state + cumulative token count + today's reply count as JSON.

Stdlib-only on purpose: deploys to Mugi container without venv setup.
"""

from __future__ import annotations

import glob
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

PROJECTS_GLOB = os.environ.get(
    "MUGI_PROJECTS_GLOB",
    "/home/node/.claude/projects/-home-node/*.jsonl",
)
DISCORD_MARKER = '<channel source="plugin:discord:discord"'
DISCORD_MARKER_ESCAPED = '<channel source=\\"plugin:discord:discord\\"'
REPLY_TOOL_NAME = "mcp__plugin_discord_discord__reply"
PORT = int(os.environ.get("PORT", "8080"))
AUTH_TOKEN = os.environ.get("MUGI_STATUS_TOKEN", "").strip()

NOISE_TYPES = {"system", "queue-operation", "file-history-snapshot"}


def _is_mugi_running() -> bool:
    """Return True if tmux 'main' session exists (Mugi process is live)."""
    try:
        result = subprocess.run(
            ["tmux", "ls"], capture_output=True, text=True, timeout=3
        )
        return result.returncode == 0 and "main" in result.stdout
    except Exception:
        return False

IDLE_AFTER_SECONDS = 120
NEW_SESSION_GRACE_SECONDS = 120  # treat new non-Discord session as "no session" for this long


def _humanize_age(seconds: float) -> str:
    s = int(seconds)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m"
    if s < 86400:
        return f"{s // 3600}h"
    return f"{s // 86400}d"


def find_current_discord_session() -> str | None:
    """Return path of the most-recently-modified jsonl that has Discord traffic."""
    candidates: list[tuple[float, str]] = []
    for path in glob.glob(PROJECTS_GLOB):
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            continue
        candidates.append((mtime, path))
    candidates.sort(reverse=True)

    for _mtime, path in candidates:
        if _file_has_discord(path):
            return path
    return None


def _find_newest_jsonl() -> tuple[float, str] | None:
    """Return (mtime, path) of the most recently modified jsonl regardless of content."""
    best: tuple[float, str] | None = None
    for path in glob.glob(PROJECTS_GLOB):
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            continue
        if best is None or mtime > best[0]:
            best = (mtime, path)
    return best


def _file_has_discord(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(2 * 1024 * 1024)
        return DISCORD_MARKER_ESCAPED.encode() in chunk
    except OSError:
        return False


def parse_entries(path: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def _content_blocks(entry: dict[str, Any]) -> list[dict[str, Any]]:
    msg = entry.get("message") or {}
    content = msg.get("content")
    if isinstance(content, list):
        return [c for c in content if isinstance(c, dict)]
    return []


def _is_assistant_reply_tool(entry: dict[str, Any]) -> bool:
    if entry.get("type") != "assistant":
        return False
    for c in _content_blocks(entry):
        if c.get("type") == "tool_use" and c.get("name") == REPLY_TOOL_NAME:
            return True
    return False


def _today_utc_range() -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    return start, now.isoformat()


def derive_activity(entries: list[dict[str, Any]], now_ts: float) -> dict[str, Any]:
    """Walk entries backward, skip noise, classify last meaningful entry."""
    last: dict[str, Any] | None = None
    for entry in reversed(entries):
        if entry.get("type") in NOISE_TYPES:
            continue
        if entry.get("isMeta") and entry.get("type") == "user":
            content = (entry.get("message") or {}).get("content", "")
            if isinstance(content, str) and DISCORD_MARKER not in content:
                continue
        last = entry
        break

    if last is None:
        return {"verb": "idle", "label": "💤 no activity", "age_seconds": None}

    ts_str = last.get("timestamp", "")
    try:
        ts_dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        age = max(0.0, now_ts - ts_dt.timestamp())
    except (ValueError, TypeError):
        age = 0.0

    etype = last.get("type")
    msg = last.get("message") or {}

    if etype == "assistant":
        blocks = _content_blocks(last)
        kinds = {b.get("type") for b in blocks}
        stop_reason = msg.get("stop_reason", "")

        if stop_reason == "tool_use" or "tool_use" in kinds:
            tool_name = next(
                (b.get("name", "?") for b in blocks if b.get("type") == "tool_use"),
                "?",
            )
            short = tool_name.replace("mcp__plugin_discord_discord__", "").replace(
                "mcp__", ""
            )
            return {
                "verb": "tool",
                "label": f"🔧 {short}",
                "tool_name": short,
                "age_seconds": age,
            }

        if "text" in kinds and stop_reason == "end_turn":
            if age < 5:
                return {"verb": "replying", "label": "💬 replying", "age_seconds": age}
            return {
                "verb": "idle",
                "label": f"💤 idle {_humanize_age(age)}",
                "age_seconds": age,
            }

    if etype == "user" and age < IDLE_AFTER_SECONDS:
        content = msg.get("content")
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    return {
                        "verb": "working",
                        "label": "🔧 working",
                        "age_seconds": age,
                    }
        if isinstance(content, str) and DISCORD_MARKER in content:
            return {"verb": "thinking", "label": "🧠 thinking", "age_seconds": age}

    return {"verb": "idle", "label": f"💤 idle {_humanize_age(age)}", "age_seconds": age}


def last_usage_tokens(entries: list[dict[str, Any]]) -> dict[str, int]:
    """Pull cumulative token counters from the latest assistant message usage."""
    for entry in reversed(entries):
        if entry.get("type") != "assistant":
            continue
        usage = (entry.get("message") or {}).get("usage") or {}
        if not usage:
            continue
        input_tokens = int(usage.get("input_tokens") or 0)
        cache_create = int(usage.get("cache_creation_input_tokens") or 0)
        cache_read = int(usage.get("cache_read_input_tokens") or 0)
        output = int(usage.get("output_tokens") or 0)
        return {
            "input": input_tokens,
            "cache_creation": cache_create,
            "cache_read": cache_read,
            "output": output,
            "total": input_tokens + cache_create + cache_read + output,
        }
    return {"input": 0, "cache_creation": 0, "cache_read": 0, "output": 0, "total": 0}


def count_replies_today(entries: list[dict[str, Any]]) -> int:
    start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    count = 0
    for entry in entries:
        if not _is_assistant_reply_tool(entry):
            continue
        ts = entry.get("timestamp", "")
        try:
            ts_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        if ts_dt >= start:
            count += 1
    return count


def build_status() -> dict[str, Any]:
    if not _is_mugi_running():
        return {
            "session": None,
            "activity": {"verb": "offline", "label": "⛔ offline", "age_seconds": None},
            "tokens": {"input": 0, "cache_creation": 0, "cache_read": 0, "output": 0, "total": 0},
            "replies_today": 0,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    now_ts = time.time()
    session_path = find_current_discord_session()

    # If a newer non-Discord session was created within the grace window, don't
    # show stale data from the old Discord session — treat it as "no session yet".
    if session_path is not None:
        newest = _find_newest_jsonl()
        if newest is not None:
            newest_mtime, newest_path = newest
            if newest_path != session_path and newest_mtime > now_ts - NEW_SESSION_GRACE_SECONDS:
                session_path = None

    if session_path is None:
        return {
            "session": None,
            "activity": {"verb": "idle", "label": "💤 no session", "age_seconds": None},
            "tokens": {
                "input": 0,
                "cache_creation": 0,
                "cache_read": 0,
                "output": 0,
                "total": 0,
            },
            "replies_today": 0,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    entries = parse_entries(session_path)
    return {
        "session": {
            "id": os.path.basename(session_path).replace(".jsonl", ""),
            "path": session_path,
            "mtime": os.path.getmtime(session_path),
            "entry_count": len(entries),
        },
        "activity": derive_activity(entries, now_ts),
        "tokens": last_usage_tokens(entries),
        "replies_today": count_replies_today(entries),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


class Handler(BaseHTTPRequestHandler):
    def _check_auth(self) -> bool:
        if not AUTH_TOKEN:
            return True
        header = self.headers.get("Authorization", "")
        return header == f"Bearer {AUTH_TOKEN}"

    def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler API)
        path = self.path.rstrip("/")
        if path == "/health":
            body = b'{"ok":true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path not in ("/status", ""):
            self.send_response(404)
            self.end_headers()
            return
        if not self._check_auth():
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error":"unauthorized"}')
            return
        try:
            payload = build_status()
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        except Exception as exc:  # noqa: BLE001
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(exc)}).encode())
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: Any) -> None:  # quieter access log
        return


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    auth = "bearer-required" if AUTH_TOKEN else "open"
    print(
        f"mugi-status listening on :{PORT} (glob={PROJECTS_GLOB}, auth={auth})",
        flush=True,
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
