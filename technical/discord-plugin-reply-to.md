---
Title: Discord plugin reply_to patch
Added: [[2026-06-19]]
Last-checked: [[2026-06-19]]
Status: applied-pending
Upstream: anthropics/claude-plugins-official (PR pending)
---

# Discord plugin — reply_to jump-link patch

Adds reply-reference fields to the inbound `notifications/claude/channel` envelope so that when a Discord message is itself a **reply (quote)** to another message, Mugi can surface a clickable jump link back to the quoted message. Used by `skills/integration/reminder-set.md`: when someone replies to a message + tags Mugi "remind me to follow up this tomorrow", the fired reminder carries a link back to the original.

> Sibling of [[discord-plugin-parent-id]] — same vendored file, same in-container re-apply story. Both patches must be re-applied after any plugin reinstall/update.

## Why

The vendored `claude-plugins-official/discord/0.0.4/server.ts` does not put any reply/referenced-message info in the inbound meta block. discord.js already exposes `msg.reference` (messageId / channelId / guildId) and `msg.fetchReference()`, so the data is available — this patch lifts it into the notification payload.

Use case: Benjy sends a message in a job channel telling Max to follow up. Max wants to deal with it later, so he **replies to** Benjy's message and tags Mugi: "remind me to follow up this tomorrow." When the reminder fires tomorrow, Max gets a jump link straight back to Benjy's original message.

## What it changes

Two edits to `server.ts` (additive, backwards-compatible — non-reply messages get the same envelope as before):

1. **`handleInbound`, just before the "Attachment listing" comment** — build a `replyMeta` object from `msg.reference` + `msg.fetchReference()`.
2. **meta payload object** — spread `...replyMeta` in after the `ts:` line.
3. **Instructions string (~line 455)** — document the new attributes for session start.

Fields surfaced: `reply_to_link` (Discord jump URL), `reply_to_id`, `reply_to_excerpt` (≤140 char, when fetchable), `reply_to_author` (when fetchable).

## Re-apply (in-container)

After a plugin reinstall the file reverts. Re-apply the block below.

### Edit 1 — reply block (insert before `// Attachment listing goes in meta only`)

```ts
  // Reply reference — if this message is a reply, surface a jump link (+ short
  // excerpt/author) so a reminder can point back to the original message.
  const replyMeta: Record<string, string> = {}
  const refId = msg.reference?.messageId
  if (refId) {
    const gid = msg.reference?.guildId ?? msg.guildId ?? undefined
    const cid = msg.reference?.channelId ?? chat_id
    if (gid) replyMeta.reply_to_link = `https://discord.com/channels/${gid}/${cid}/${refId}`
    replyMeta.reply_to_id = refId
    try {
      const ref = await msg.fetchReference()
      const excerpt = (ref.content || "").replace(/\s+/g, " ").trim().slice(0, 140)
      if (excerpt) replyMeta.reply_to_excerpt = excerpt
      replyMeta.reply_to_author = ref.author.username
    } catch {}
  }
```

> ⚠️ **The `\s+` backslash matters.** When re-applying via `echo`/heredoc into the container, the backslash in `/\s+/g` is easily stripped → becomes `/s+/g`, which matches literal "s" letters and mangles every excerpt containing an "s". After applying, verify: `grep -n 'replace(/.s+/g' server.ts` should show `\s+`, NOT `s+`. (This exact bug shipped on first apply 2026-06-19 and was fixed in place.)

### Edit 2 — meta payload (after the `ts:` line)

```ts
        ts: msg.createdAt.toISOString(),
        ...replyMeta,
```

### Edit 3 — instructions string (~line 455, append to the channel description)

> When the inbound message is itself a reply to another message, the tag also carries reply_to_link (a clickable Discord jump URL to that original message), plus reply_to_excerpt and reply_to_author when fetchable — use these when the request refers to "this"/"呢件事" (e.g. setting a reminder that should point back to the quoted message).

### Steps

```bash
# In Mugi container (zeabur service exec --id 69d3781093577fe0061de8d5)
cd /home/node/.claude/plugins/cache/claude-plugins-official/discord/0.0.4
cp server.ts server.ts.bak.replyto.$(date +%F)
# ...apply the three edits...
chown node:node server.ts          # root edits leave root-owned files
# Verify
grep -c reply_to_link server.ts    # → 2 (instruction string + code)
grep -n 'replace(/\\s+/g' server.ts | grep excerpt   # → must show \s+, not s+
```

Then restart the service (Zeabur dashboard / CLI). Restart preserves `/home/node/kb/` + memory; only a full rebuild clears them.

## Rollback

```bash
mv server.ts.bak.replyto.2026-06-19 server.ts
# restart service
```

## Verification (live, needs real Discord)

Reply to any message in an allowlisted channel + tag Mugi "remind me to follow up this tomorrow". Mugi should:
1. See the inbound tag carry `reply_to_link="https://discord.com/channels/..."`.
2. Append `↩︎ 原文（[author]）：[excerpt]` + the link to the reminder payload.
3. When the reminder fires, Max can click the link back to the original message.

## Upstream

PR target: `anthropics/claude-plugins-official` (Apache-2.0). Additive + backwards-compatible. PR notes: discord.js already exposes `msg.reference` / `fetchReference()`; no new tools or breaking changes; mirrors the existing internal use at `server.ts:304`.
