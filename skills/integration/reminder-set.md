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
| `payload` | 要 post 出去嗰段。**唔好照抄原話** —— 跟下面〈Payload 點砌〉處理（動作內容逐字保留、排程時間語轉 fire-moment、提第二個人加 attribution）。 |
| `fire_at` | 用戶講嘅時間 → 換成 **ISO 8601 連 +08:00 offset**（Asia/Hong_Kong），e.g.「今晚 9 點」→ `2026-06-18T21:00:00+08:00`。相對時間（「兩個鐘後」「聽日朝早」）由你按當前 HK 時間計。時間含糊（「夜啲」冇講幾點）→ 問清楚先,唔好估。⚠️ **Discord envelope `ts` 係 UTC**——計算相對 fire_at 之前，必須先 +08:00 換成 HKT（e.g. `ts="...T01:35Z"` = HKT 09:35）。 |
| `target` | 見下面 Target Resolution |
| `label` | 你生成嘅短標題（人睇，e.g.「提 Benjy 交 J26033 grade」），方便之後 list / 認返。 |
| `requested_by` | **邊個 set 呢條**（人睇 + attribution 用）。攞 envelope `user_id` 去 **CLAUDE.md `Team（快速查找）` table** map 返 canonical DOF 名（e.g. `1328602029303791646` → `Kary`）；map 唔到 fallback envelope `user`（display name）。 |
| `requested_by_id` | envelope `user_id` **原樣存**（穩定 audit key，名變 / 撞名都認得返）。 |

**Target Resolution：**

1. **用戶明講指定去邊**（job channel / 某 channel）→ 照字面 resolve。指定 job → 由 `context/job-list.md` 反查 channel id（同 Job Resolution 一樣）。可一次過指定多個 job + tag 人。
2. **喺 job channel 入面 set + 冇講去邊** → **default 用當前 channel**（envelope `channel_id`；thread 用 `parent_id`）。**唔好重複問**「想出去邊」。
3. resolve 唔到（job-list 冇呢個 channel / 認唔到 reference）→ 問清楚，唔好亂寫 target。

**Tag 人（@mention）：** payload 入面提到要 tag 邊個同事 → 查 **CLAUDE.md `Team（快速查找）` table** 攞 Discord ID → 喺 payload 寫成 `<@Discord_ID>`（poller 原文 post 就會真係 tag 到）。table 入面冇個名（e.g. 未 record）→ 同用戶講「我 record 入面冇 [name] 嘅 Discord ID，補返俾我就 tag 到」，唔好亂 tag。

### Payload 點砌（核心 —— 唔係照抄原話）

`payload` 喺 set 嗰刻就 draft 死、原文存，到時 poller 照 post。但**砌嘅時候要企喺「fire 嗰一刻」嘅視角寫**，因為呢段字係到時先有人睇。三條 rule：

1. **動作內容逐字保留** —— 用戶想提醒做嘅嗰件事（check calendar / send grade / 問 client），原文唔好 paraphrase、唔好加油添醋、唔好換字。

2. **排程時間語 → fire-moment deixis** —— 用戶句子入面**用嚟定 `fire_at` 嗰個時間詞**，唔屬於 message 內容，要按「到時睇返」嘅視角轉返：
   - 「**星期一** check calendar」（星期一 = 幾時 fire）→ fire 嗰日就係星期一，message 講「**今日** check calendar」
   - 「**聽日朝** send grade」→「**今朝** send grade」
   - 「**兩個鐘後**提我食藥」→ 純相對排程詞，fire 嗰刻冇對應 deixis → drop 咗，淨低「**記得**食藥」
   - 拿唔準點轉 → fallback「**記得 [動作]**」，唔好硬塞返個排程時間詞落 message。

3. ⚠️ **分清「排程時間」定「內容時間」** —— 句子可以同時有兩個時間詞，**只有定 `fire_at` 嗰個**先轉 deixis；屬於動作內容嗰個**原文保留**。
   - 例：「提我**聽日**問 client **星期五**得唔得」→ 聽日 = 排程（定 fire_at，轉 fire-moment）、星期五 = 內容（client 要答嘅嗰日，原文留）→ payload =「**記得問 client 星期五得唔得**」。

### Attribution（提第二個人先加）

當 **target 收件人 ≠ 設定人**（即係叫 Mugi 提另一個同事），message 結尾要 attribute 返係邊個叫提，收件人先知唔係 bot 自己出。

- Format：`<@收件人Discord_ID> [砌好嘅內容] —— from [設定人 canonical 名]`
- 設定人**淨係寫個名，唔好 @-tag**（避免重複 ping 個設定人；收件人先要 ping）。
- 設定人 canonical 名 = `requested_by`（已由 envelope `user_id` map 好）。
- **自己提自己**（收件人 = 設定人，e.g.「提我…」）→ **唔加 attribution**。
- 例：Kary 講「提 Sohling 星期一 check calendar」→ payload =`<@SohlingId> 記得今日 check calendar —— from Kary`

### Reply-to link（引用咗 message 先有）

有陣時用戶係 **reply（引用）緊另一條 message** 嗰陣先叫 Mugi 提醒（e.g. Benjy send 咗條 message 叫人 follow up，Max reply 嗰條再 tag Mugi 講「remind me to follow up this tomorrow」）。Discord channel envelope 喺呢個情況會帶埋：

| envelope 欄位 | 係咩 |
|---|---|
| `reply_to_link` | 跳返去被引用嗰條 message 嘅 Discord jump URL（`https://discord.com/channels/.../.../...`）|
| `reply_to_excerpt` | 被引用嗰條 message 嘅頭 ~140 字摘要（fetch 唔到就冇）|
| `reply_to_author` | 被引用嗰條 message 嘅作者 username（fetch 唔到就冇）|

**規則：envelope 一帶 `reply_to_link`，就 append 落 payload 結尾**，等 fire 出嚟嗰陣收件人可以直接撳返入去 refer 返當時想提醒嘅原文。

- Format：砌好嘅內容（連 attribution，如果有）之後另起一行 →
  `↩︎ 原文（[reply_to_author]）：[reply_to_excerpt]\n[reply_to_link]`
  - `reply_to_excerpt` / `reply_to_author` fetch 唔到 → 嗰部分 drop，淨係留 `↩︎ 原文：[reply_to_link]`。
- **link 永遠原樣保留**，唔好改寫、唔好砌短，Discord 要靠完整 URL 先 jump 到。
- self-reminder 同 other-directed 都照加（兩種情況收件人都用得着條 link）。
- 用戶句子明顯指返被引用嗰件事（「呢件事」「this」「跟返」）→ 內容部分照〈Payload 點砌〉砌，link 純粹做 reference，**唔好**將 excerpt 當成動作內容塞入去 paraphrase。
- 例（Max reply Benjy 條 message 講「remind me to follow up this tomorrow」）→ payload：
  ```
  記得今日 follow up 返呢件事
  ↩︎ 原文（Benjy）：Max 你跟返 J26033 個 client feedback
  https://discord.com/channels/123/456/789
  ```

### Step 2 — 寫入（stdin heredoc，避開 quoting）

```bash
node scripts/reminder.js set <<'JSON'
{
  "label": "提 Benjy 交 J26033 grade",
  "fire_at": "2026-06-18T21:00:00+08:00",
  "target": "1303...",
  "payload": "<@1221464062085562441> 記得今晚 send J26033 嘅 grade reference 過嚟 —— from Kary",
  "requested_by": "Kary",
  "requested_by_id": "1328602029303791646"
}
JSON
```

`requested_by` / `requested_by_id` 每次都帶埋（見 Step 1 表）；自己提自己都照存，淨係 payload 唔加 attribution wrapper。Script 回傳 `{ id, label, fire_at, target, type, status, requested_by, requested_by_id, payload }`。

### Step 3 — 覆述（直接寫入，唔 pre-confirm）

寫咗就即刻**覆述一次**，等用戶睇到錯即場 correct：

> ✅ Set 咗：**[label]**
> · 幾時發：[HK 可讀時間，e.g. 今晚 9:00]
> · 去邊：[channel 名 / id]
> · 原文：「[payload]」

⚠️ **覆述兩個必守規矩：**
1. **時間用 HKT** —— 寫你 set 時計嗰個 `+08:00` 香港時間，**唔好**攞 script 返回嘅 `fire_at`（Airtable 正規化成 UTC `Z`，e.g. `01:38:00.000Z`）原樣 render，否則會少 8 個鐘（曾經出過「今晚 1:38 AM」其實係 9:38 AM 嘅 bug）。
2. **原文唔好真 mention** —— payload 入面嘅 `<@id>` 喺覆述度要寫成純文字 `@名`（查 Team table 還原個名），**唔好**保留 `<@id>` syntax，否則 confirm 嗰刻就 ping 多次收件人（poller 真正 post 出去嗰份先用真 `<@id>`）。
3. **有 reply link 就講一聲** —— payload 帶咗 `↩︎ 原文…` jump link，覆述度簡單講「· 連返原文 link」就夠，唔使 render 成完整 URL。

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

回 JSON array（每條含 `requested_by`）。整理成人睇：逐條 **label → 幾時發 → 去邊 channel → 邊個 set（`requested_by`）→（status）**。冇 pending → 講「而家冇未發嘅 reminder」。

---

## 邊界

- **只做 one-off**。用戶要「每日 / 每週」recurring → 唔係呢個 skill（reminder queue 唔 model recurring）；同佢講要 recurring 要另開 n8n cron。
- **唔好估時間**：含糊時間問清楚先寫。
- **Payload boundary（見〈Payload 點砌〉+〈Attribution〉+〈Reply-to link〉）**：(1) 動作內容逐字保留、唔 paraphrase；(2) 排程時間詞轉 fire-moment deixis（星期一→今日），內容時間詞原文留；(3) 提第二個人加 `—— from [設定人]` attribution，自己提自己唔加；(4) envelope 帶 `reply_to_link` 就 append `↩︎ 原文…` jump link（link 原樣保留）。
