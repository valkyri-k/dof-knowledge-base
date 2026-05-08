---
Title: Discord plugin parent_id patch
Added: [[2026-05-09]]
Last-checked: [[2026-05-09]]
Status: applied-pending
Upstream: anthropics/claude-plugins-official (PR pending)
---

# Discord plugin — parent_id / chat_name patch

Adds thread-parent and channel-name fields to the inbound `notifications/claude/channel` envelope so Mugi can route per-job logging by parent channel ID when a Discord message arrives in a thread.

## Why

The vendored `claude-plugins-official/discord/0.0.4/server.ts` only ships `chat_id, message_id, user, user_id, ts` (plus optional `attachment_count` / `attachments`) in the inbound meta block. When Kary creates a thread inside a job channel (e.g. `#j26071-...` → "timeline" thread), Mugi sees `chat_id = thread_id` and has no way to discover the parent — `job-list.md` keys jobs by parent channel ID. Result: per-job activity log writes silently fail (channel ID not in cache).

The plugin already does parent lookup internally for ACL gating (`server.ts:278-280`). This patch lifts the same lookup into the notification payload so the model can use it.

## What it changes

Three edits to `server.ts`:

1. **Line 824 (variable extraction)** — after `const chat_id = msg.channelId`, derive `isThread`, `parent_id`, `parent_name`, `chat_name` from `msg.channel`.
2. **Line ~872 (meta payload)** — additively spread `chat_name`, `parent_id`, `parent_name` into the meta object when present. All three are optional / conditional, so the envelope shape is backwards-compatible for non-thread messages.
3. **Line 455 (instructions string)** — document the new attributes in the system instructions Claude reads on session start.

Patch file: `discord-plugin-parent-id.patch` (unified diff, +9/-1 net).

## Apply (in-container)

The container's `server.ts` has CRLF line endings; the patch is LF. Use `--ignore-whitespace`:

```bash
# In Mugi container (zeabur exec into project dof-agent / service claude-code)
cd /home/node/.claude/plugins/cache/claude-plugins-official/discord/0.0.4
cp server.ts server.ts.bak.2026-05-09
patch -p1 --ignore-whitespace < /path/to/discord-plugin-parent-id.patch
# Verify: grep -c parent_id server.ts  → 3
# Verify: wc -l server.ts              → 900 (was 893)
```

Then restart the `claude-code` service (Zeabur dashboard or CLI). Restart preserves `/home/node/kb/` and memory — only full container rebuild clears them.

## Rollback

```bash
mv server.ts.bak.2026-05-09 server.ts
# restart service
```

## Verification

After restart and `/clear`, send any message in a Discord thread. Mugi should see the inbound tag carry `parent_id="..." parent_name="..."`. Then test J26071 thread → per-job log should write to `activity/jobs/j26071-button-investhk-motion-graphic-videos.md`.

## Upstream

PR target: `anthropics/claude-plugins-official` (Apache-2.0). The patch is additive and backwards-compatible — non-thread messages get the same envelope as before. PR description should note: (a) discord.js already exposes `parentId` / `parent.name` on thread channels, (b) plugin already uses this internally for ACL, (c) no new tools or breaking changes.
