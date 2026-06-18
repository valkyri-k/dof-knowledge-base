# Ad-hoc Reminder (set / list / edit / cancel)

> **用途：** 用戶叫 Mugi「到時提我 / 到時 post 一段嘢去某 channel」——set 一個 **one-off**（非 recurring）reminder，到指定時間由 poller 原文 post 出去。亦掌管之後 list / 改 / cancel。收到呢類 request 用呢份。
> **Callers：**
> - Set：「提我 X」、「remind me to X」、「今晚 9 點同 [channel] 講 X」、「聽日朝早 post X 落 J26XXX」、「夜啲喺呢度出返 X」、「set 個 reminder」
> - List：「我 set 咗咩 reminder」、「list 我啲 reminder」、「仲有咩未 post」
> - Edit：「改返頭先嗰個 reminder」、「改去 10 點」、「嗰段嘢改成 X」
> - Cancel：「cancel 嗰個 reminder」、「唔使 post 喇」、「刪咗頭先嗰個」
>
> **Scope（Type 1 — Replay only）：** message 喺 set 嗰刻已經 draft 好、**原文** 存落 `payload`，到時 poller 照 post，**Mugi 唔會喺發送嗰刻再生成或判斷**。如果用戶要嘅係「到時先睇情況做嘢 / 到時再查嘢再答」（要 Mugi 喺未來嗰刻動腦），嗰個係 **Type 2 — Wake**，分支未起 → 同用戶講「wake 類 reminder 仲未 build，而家只可以 set 一段固定 message 到時原文出」。

---

## Credentials

所有 Airtable 操作行 `scripts/reminder.js`（內部用 Zeabur env `AIRTABLE_PAT` + REST 打 DOF Reminders base `appaAEiqHzUfLCGAU` / table `Reminders`）。

> 🚫 **絕對禁止用任何 cloud MCP / connected Airtable tool**，就算 `claude mcp list` 顯示 ✓ Connected 都唔好用（同 Calendar / Vimeo 一樣：headless turn 唔保證有，亦違反 env-credential 原則）。

---

## No-Fallback Rule（hard）

呢個 skill 嘅 Airtable 讀寫**只可以**經 `scripts/reminder.js`。**唔可以**：

- 自己 call cloud Airtable MCP / connected tool
- 自己手寫 `fetch()` / `curl` 打 Airtable（script 已做晒 auth / schema / pagination）
- 估 record id、亂寫 channel id

撞到 script 行唔到（env 缺、API error、parse fail）→ **STOP，照原文 report error，唔好 improvise workaround**。

---

## 消費端（背景，唔使你做）

n8n workflow `d4VcGHDHLfeVKjgr`（Reminder Poster）每 5 分鐘 poll，搵 `status='pending'` + `type='replay'` + `fire_at` 已過嘅 row，原文 post 去 `target` channel，再 flip `status` 走 pending。你只負責**寫入（生產端）**。

---

## Ops Flow — SET

### Step 1 — 由 request 解析四樣嘢

| 欄位 | 點 resolve |
|---|---|
| `payload` | **要 post 出去嗰段原文**。用戶口述咩就存咩，**唔好 paraphrase / 加料**。message 喺 set 嗰刻定稿。 |
| `fire_at` | 用戶講嘅時間 → 換成 **ISO 8601 連 +08:00 offset**（Asia/Hong_Kong），e.g.「今晚 9 點」→ `2026-06-18T21:00:00+08:00`。相對時間（「兩個鐘後」「聽日朝早」）由你按當前 HK 時間計。時間含糊（「夜啲」冇講幾點）→ 問清楚先,唔好估。 |
| `target` | 見下面 Target Resolution |
| `label` | 你生成嘅短標題（人睇，e.g.「提 Benjy 交 J26033 grade」），方便之後 list / 認返。 |

**Target Resolution：**

1. **用戶明講指定去邊**（job channel / 某 channel）→ 照字面 resolve。指定 job → 由 `context/job-list.md` 反查 channel id（同 Job Resolution 一樣）。可一次過指定多個 job + tag 人。
2. **喺 job channel 入面 set + 冇講去邊** → **default 用當前 channel**（envelope `channel_id`；thread 用 `parent_id`）。**唔好重複問**「想出去邊」。
3. resolve 唔到（job-list 冇呢個 channel / 認唔到 reference）→ 問清楚，唔好亂寫 target。

**Tag 人（@mention）：** payload 入面提到要 tag 邊個同事 → 查 **CLAUDE.md `Team（快速查找）` table** 攞 Discord ID → 喺 payload 寫成 `<@Discord_ID>`（poller 原文 post 就會真係 tag 到）。table 入面冇個名（e.g. 未 record）→ 同用戶講「我 record 入面冇 [name] 嘅 Discord ID，補返俾我就 tag 到」，唔好亂 tag。

### Step 2 — 寫入（stdin heredoc，避開 quoting）

```bash
node scripts/reminder.js set <<'JSON'
{
  "label": "提 Benjy 交 J26033 grade",
  "fire_at": "2026-06-18T21:00:00+08:00",
  "target": "1303...",
  "payload": "<@1221464062085562441> 記得今晚 send J26033 嘅 grade reference 過嚟"
}
JSON
```

Script 回傳 `{ id, label, fire_at, target, type, status, payload }`。

### Step 3 — 覆述（直接寫入，唔 pre-confirm）

寫咗就即刻**覆述一次**，等用戶睇到錯即場 correct：

> ✅ Set 咗：**[label]**
> · 幾時發：[HK 可讀時間，e.g. 今晚 9:00]
> · 去邊：[channel 名 / id]
> · 原文：「[payload]」

### Step 4 — 記住 record id

**將回傳 `id` 留喺對話 context。** 用戶緊接住話要改 / cancel 呢條，直接用呢個 id（見下），唔使再 list、唔使再問係邊條。

---

## Ops Flow — EDIT / CANCEL / LIST（context-first）

**addressing 原則：憑 context 認返邊條，唔係硬性每次 list。**

- **啱 set 完即刻改 / cancel**（對話入面就嗰一條）→ 直接用 Step 4 記住嗰個 record id，**唔使 list、唔使問係邊條**。
- **過咗一輪先講、或者一次過 set 過幾條** → 含糊就先 `list` 出嚟（返 id + label + fire_at）按 context / label 對返邊條再 act；清楚就直接用記得嘅 id。判斷由你做。

**EDIT**（改時間 / 改原文 / 改 target）：

```bash
node scripts/reminder.js edit <recordId> <<'JSON'
{ "fire_at": "2026-06-18T22:30:00+08:00" }
JSON
```

只傳要改嘅欄（`label` / `fire_at` / `target` / `payload` / `type` 任一或多個）。改完照樣覆述新狀態。

**CANCEL**（un-fired，整條刪走）：

```bash
node scripts/reminder.js cancel <recordId>
```

回 `{ cancelled, deleted: true }` → 同用戶講「cancel 咗 [label]」。

**LIST**（default 只列 pending = 未發嘅 queue；要連 done/error 加 `--all`）：

```bash
node scripts/reminder.js list
```

回 JSON array。整理成人睇：逐條 **label → 幾時發 → 去邊 channel →（status）**。冇 pending → 講「而家冇未發嘅 reminder」。

---

## 邊界

- **只做 one-off**。用戶要「每日 / 每週」recurring → 唔係呢個 skill（reminder queue 唔 model recurring）；同佢講要 recurring 要另開 n8n cron。
- **唔好估時間**：含糊時間問清楚先寫。
- **payload 唔 paraphrase**：原文存原文。
