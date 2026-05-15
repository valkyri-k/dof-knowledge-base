# User Activity Log Schema + Pre-Clear Sequence

> Extracted from CLAUDE.md on [[2026-05-10]] to reduce context-bloat warning.
> **Read this full file when**:
> - 收到「clear」/「pre-clear」/「session summary 啦」等 keyword → 行整套 Pre-Clear Sequence
> - 收到 Profile-shaping instruction（「Profile 改返 X」/「Working Style 應該係 X」/「promote Pending Profile Review 嗰條」）→ 行 In-Discord Profile Correction Protocol
> - 維護 user activity log（write Request Log / Open Threads / Session Summary / Profile candidate）
>
> Activity files 永遠用 absolute path `/home/node/kb/activity/<file>`。

---

## User Activity Tracking

Activity log 嘅核心 purpose 係**俾將來嘅 Mugi（clear session 之後）有個長期記憶**，等可以低成本 rebuild context，唔需要 reload 成個 conversation。

### 路徑（重要）

Activity files 全部放喺 **`/home/node/kb/activity/`**（即係 repo 入面，會 sync 上 GitHub）。Mugi 寫嘅時候**永遠用 absolute path** `/home/node/kb/activity/<file>`，唔好用 bare relative path `activity/<file>`——`/home/node/activity` 而家係 symlink 指返 `kb/activity`，但係將來如果 setup 又出錯，bare path 可能 silent 寫去 wrong folder 而 push 唔到 GitHub。同樣 apply 落 `gap-log.md`、`kary-dev-log.md` 同任何將來新 activity file。

### File 結構（5-section hybrid schema）

每個 user activity file 有 **5 個 section**，各有用途：

1. **Profile**（top） — 靜態資訊（Discord ID / Role / Common requests / Notes）
2. **User Practice Profile**（如有） — Mugi 對 user working style / shorthand / response preference 嘅 stable derived rules，由 **Kary 喺 Discord 直接 trigger correction** 維護（見 §In-Discord Profile Correction Protocol）。Pre-Clear Sequence Step 5 會 draft candidate 入 Pending Profile Review 做 audit trail，但**唔自動 promote** 入呢度。
3. **Pending Profile Review**（如有） — Mugi 觀察到嘅 profile candidate。每次 Pre-Clear Sequence Step 5 append。**唔影響 runtime behavior**，runtime 只 load `User Practice Profile`。**呢個 section 而家係 audit trail**——Mugi 自己唔 promote、Claude Code 都唔做 batch review。Kary 偶爾 scan，覺得有 entry 值得入 Profile 就喺 Discord 直接叫 Mugi 改（見 §In-Discord Profile Correction Protocol）。
4. **Open Threads** — 未 resolved 嘅 pending items（incremental update，resolved 就刪）
5. **Recent Session Summaries** — Narrative form 嘅 session 紀錄，每次 clear session 前寫一段
6. **Request Log** — Table form 嘅 scan ledger（每件事一行）

### 點維護

| 時機 | 做咩 |
|------|------|
| **新用戶** | 建立 file，填入 Profile（Discord ID、Role、Notes）+ 起 4 個 section heading |
| **每件事完成** | Append 一行入 **Request Log** table（Date / Request / Outcome）——automatic，唔等用戶叫。**唔好 git push**——push 只係 pre-clear 同 daily cron 先做 |
| **喺 per-job channel 做嘢** | 除咗 update user activity log，**同步**寫入對應 per-job activity file（見 §Per-Job Activity Tracking）。兩個 log **並行寫**，唔係二選一 |
| **遇到 pending item**（blocked / waiting for / 等用戶決定） | Append 入 **Open Threads** section，標注日期 + cross-ref 去相關 gap-log / dev-log entry |
| **Open thread resolved** | 即時刪走嗰行（keep section 短） |
| **觀察到 user 有 repeat pattern / explicit profile-shaping instruction / correction** | Pre-Clear Sequence 嘅 Step 5 自動 detect + draft 入 **Pending Profile Review** section（標 `status: pending-review`）做 audit trail。Runtime 唔即時 apply。**永遠唔好** silent self-promote 入 active **User Practice Profile**。Profile promotion 由 Kary 喺 Discord 直接 trigger（見 §In-Discord Profile Correction Protocol）。 |
| **Session 自然結束 / clear 之前** | 寫一段 **Session Summary**（2-5 句 narrative，capture 今日做咗咩 + decision + 學到咩） |
| **Session 開始** | Read `/home/node/kb/activity/<username>.md`——先掃 Open Threads，再睇最近 1-2 段 Session Summary，最後睇 Request Log table 揾具體日期 |
| **Profile updates** | 發現用戶常見 request pattern → update Common requests 同 Notes |

### Single-Update per turn 規則

對**同一個 activity file**，**每個 conversation turn 只可以 Edit 一次**。將同 turn 入面所有要寫嘅嘢（Request Log row、Open Threads append、Profile draft、Session Summary）**喺 plan 階段 batch 埋**，最後一次 Edit 一齊寫入 file。

**Why：**
- 第二次 Edit 嘅 `old_string` 對住 first Edit 之後嘅 file state，容易 mismatch → retry → 多 turn round-trip
- 每次 Edit 都產生一個 tool result（係成個 file diff），inflate context
- File state 反覆變動會 invalidate Mugi 自己嘅 mental model

**Apply 落邊：**
- **Request Log automatic append** — 如果同 turn 仲要寫 Open Threads / Profile draft → 三樣嘢合併成 **一次** Edit
- **Pre-Clear Sequence** — Step 1-5 全部寫去 user activity file 嘅嘢 batch 成 **一次** Edit；user activity + dev-log + gap-log 係三個 file，各自 1 Edit OK（跨 file 唔受限）
- **In-Discord Profile Correction** — Step 2 + Step 3（edit Profile entry + add Evidence pointer）合併成 **一次** Edit
- **Per-job + user activity 並行寫** — 兩個唔同 file，各自 1 Edit；唔係將兩個 file 嘅 update 合併

**唔受限制：**
- 唔同 file（user activity / per-job activity / dev-log / gap-log 各算各）
- Read（read-only，唔改 state）
- Bash（git ops、status check 等）

**Failure mode（呢條 rule 防咩）：** Edit Request Log → 再 Edit Open Threads 用緊 stale snapshot → `old_string not found` → retry → 浪費 turn + context。

---

**Session Summary 點寫：**

唔係淨係 list 做過咩（嗰啲喺 Request Log 已經有），而係**講 context / 點解 / decision / 學到咩**。例：

> ### 2026-04-08 evening session
> 主力 stress test calendar ops + instruction infra。新 0a58a4c no-confirm rule 過 happy path test。Surface 咗 Planyway/Trello Timeline integration capability gap → logged 落 gap-log。發現 setup-level bug（`/home/node/activity` 唔係 symlink → Mugi 之前寫 activity 寫去 raw folder 唔入 repo），fix 咗（symlink + CLAUDE.md 明文化），完整 root cause 入 dev-log。Decision: long-term 用 absolute path 寫 activity，bare relative path 太危險。

呢個 narrative form 容納 table row 容唔落嘅 nuance。

### File format（template）

```markdown
# <username>

- **Discord ID:** <id>
- **Role:** <role or Unknown>
- **Common requests:** <patterns>
- **Notes:** <anything useful>

---

## User Practice Profile
（由 Kary 喺 Discord 直接叫 Mugi 改入嚟——見 §In-Discord Profile Correction Protocol。Mugi 自己 Pre-Clear Sequence 唔可以 promote 入呢度）

### Responsibilities
- [confirmed responsibility / domain]

### Working Style
- [observed stable interaction style]

### Response Guidance
- [how Mugi should adapt replies]

### Known Shorthand
- [phrase] = [meaning]

### Evidence
- [[YYYY-MM-DD]] [brief evidence pointer]

---

## Pending Profile Review
（Mugi Pre-Clear Sequence draft，audit trail；Kary 偶爾 scan，覺得有 entry 值得入 Profile 就喺 Discord 直接叫 Mugi 改）

### [[YYYY-MM-DD]] <morning/afternoon/evening>

- entry: <profile statement>
  category: responsibilities | working-style | response-guidance | shorthand
  confidence: high | medium | low
  source: explicit | observed | corrected
  evidence:
    - [[YYYY-MM-DD]] <brief evidence pointer>
  proposed_visibility: kary-only | team-shared
  status: pending-review
  drafted_by: mugi
  drafted_at: YYYY-MM-DD

---

## Open Threads
（pending items，resolved 即時刪）

- [YYYY-MM-DD] <thread description> — <blocked on / waiting for / next action>（cross-ref: gap-log / dev-log entry 如有）

---

## Recent Session Summaries
（每次 clear 前寫一段 narrative，新嘅放底）

### YYYY-MM-DD <morning/afternoon/evening> session
<2-5 句 narrative — context、decision、學到咩>

---

## Request Log
| Date | Request | Outcome |
|------|---------|---------|
| YYYY-MM-DD | ... | ... |
```

### 點解呢個 schema work（cost angle）

Conversation context 越長，每 turn 嘅成本 scale 緊 O(N²)——reload + re-cache 都貴。Auto-compact 係 lossy summary 但仍然要每 turn re-read，冇真正 saving。**最有效嘅 cost control：定期 clear session，靠 activity log 做長期記憶。** Activity log 喺 disk 上，read 嘅 cost 係幾百 token vs conversation 幾萬 token。

Mugi 嘅責任：寫 activity log 嘅時候要諗「**將來嘅自己 clear 完之後返嚟睇呢段，夠唔夠 rebuild context？**」 唔夠 → 加多啲 narrative；夠 → 唔好為咗詳細而塞 noise。

### Pre-Clear Sequence（用戶話「clear」嗰陣 Mugi 自動做嘅嘢）

**Trigger keywords：** 用戶（任何 user，但**通常係 Kary**）講以下任何一句 → Mugi 自動 run 整套 pre-clear sequence：

- 「clear」/「clear session」/「clear conversation」/「clear chat」
- 「我要 clear」/「準備 clear」/「clear 喇」/「我而家 clear」
- 「pre-clear」/「session summary 啦」/「summarize 之後 clear」

**唔 trigger 嘅情況：**
- 「clear 唔 clear 好」/「考慮 clear」（係 hesitation，唔係 commit）
- 「點解要 clear」（係問問題）
- 「clear」出現喺其他 context（e.g.「clear the calendar event」「make it clear」）

**Sequence steps（一氣呵成做晒，唔逐步問用戶）：**

1. **更新 Open Threads** — 由 conversation context 抽出今晚新出現嘅 pending items，append 入 sender 嘅 activity file Open Threads section。同時 review 現有 Open Threads，如果今晚已經 resolved → 刪走。
2. **寫 Session Summary** — Append 一段新嘅 narrative 入 Recent Session Summaries section，跟 standard format `### YYYY-MM-DD <morning/afternoon/evening> session`。內容要 capture：今晚做咗咩主要 work、邊啲 decisions、學到咩、有冇 surface 新 issue / capability gap。**唔好 list 細節**——細節已經喺 Request Log table，narrative 講 nuance。
3. **更新 Request Log** — 將今晚發生但未 log 嘅 entries append 入 table（每件主要事一行）。
4. **Cross-update related logs**（如有需要） — 如果今晚有 architectural decision / bug fix / capability gap，update 埋 `kary-dev-log.md` 或 `gap-log.md` 嘅相關 entry。
5. **Profile candidate detection** — 呢個 step 拆兩部分：

   **Part A — Review（MANDATORY，永遠唔可以 skip）**：每個 sender 嘅 message + 自己今晚 reply 都要 explicit walk through 三條 promotion criteria，**心入面（或 chain-of-thought）行過一次**，唔可以默默略過：
   - **Explicit profile-shaping instruction**：sender 講「以後我講 X 即係指 Y」/「你記住我負責 Z」/「以後 reply 我簡短啲」等明顯指令 → confidence: high, source: explicit
   - **Correction signal**：sender 修正 Mugi 對佢嘅理解（「我唔係 director 啦，我係 producer」）→ confidence: high, source: corrected
   - **Repeat pattern**：sender 表現一致 working style / shorthand / preference，**且過往 activity log 有同類 evidence** → 2 次 confidence: low；3+ 次 confidence: medium。Source: observed。

   **Part B — Draft（CONDITIONAL）**：Review 後得出嘅 candidates，每條 draft 一個 entry 入 sender activity file 嘅 **Pending Profile Review** section（schema 見 File format template）。如果 Part A 結論係 0 candidate → 唔需要寫 file，但 review 嘅 fact 仍然要喺 Step 7 report 出嚟（「Profile review: 0 candidate」）。

   **絕對禁止**：跳過 Part A 直接寫「Profile drafts: 0」。Review 必須真係 run 過，唔係 default-skip 嘅 escape hatch。

   **Skip 細則（apply 落 Part B draft 動作，唔 apply 落 Part A review）：**
   - 純 quick lookup / 閒聊冇 substantive interaction → skip
   - Sender 已存在 active **User Practice Profile** entry 同 candidate 矛盾 → 仍然 draft 但 entry 加 `conflicts_with: <existing entry text>` field，等 Kary 解
   - 同類 candidate 已喺 Pending Profile Review section（未被 review） → skip duplicate，但 evidence list append 新 evidence pointer
   - 對其他 user 嘅 personal evaluation（e.g.「Benjy 慢」） → **絕對唔 draft**，呢類嘢去 `kary/reasoning/`，唔入 Mugi profile

   **Visibility 默認：**
   - 一般 working-style / shorthand → `proposed_visibility: team-shared`
   - 個人 admin preference / 涉及第三方人嘅 context → `proposed_visibility: kary-only`

   **永遠唔好** silent self-promote 入 active **User Practice Profile**——只能 draft 入 Pending Profile Review。Profile promotion 由 Kary 喺 Discord 直接觸發（見 §In-Discord Profile Correction Protocol），唔再經 Claude Code batch review。
6. **Commit + push** — Stage 全部相關 file，single commit（message 簡述今晚主題），push 上 GitHub。Commit message format 跟現有 convention。
7. **Report 俾用戶** — 一個簡潔 message。**Mandatory fields，每次都要齊**（即使 value 係 0 或 skip）：

   1. `Commit <hash> pushed`
   2. `Open threads: N` （括號內列 thread topic，N=0 寫「none」）
   3. `Cross-log updates: <list 邊個 file updated 或 'skip — 今晚冇 architectural decision'>`（Step 4 result）
   4. `Profile review: N candidate drafted` （N=0 都要寫，**證明 Part A review 真係 run 過**；如果 N>0 列每條 sender + category + source）（Step 5 result）
   5. `Session: <主題>`（Step 2 narrative 嘅 1 句 condensed version）
   6. `OK 你而家可以 /clear 啦`

   例（happy path）：

   > ✅ Pre-clear done. Commit `abc1234` pushed.
   > Open threads: 2 (Planyway 方向 / activity.bak 待刪).
   > Cross-log updates: kary-dev-log.md (activity-path bug fix), gap-log.md (Planyway gap).
   > Profile review: 1 candidate drafted (sohling: response-guidance, observed × 3).
   > Session: stress test + activity-path bug fix + memory schema rework.
   > OK 你而家可以 /clear 啦。

   例（quiet session，所有 conditional step 都 skip）：

   > ✅ Pre-clear done. Commit `xyz5678` pushed.
   > Open threads: none.
   > Cross-log updates: skip — 今晚冇 architectural decision / bug / capability gap.
   > Profile review: 0 candidate drafted.
   > Session: J260ZZ timeline test, Compressed-Edge-Case branch trigger 確認.
   > OK 你而家可以 /clear 啦。

   **絕對禁止省略任何 mandatory field**——「冇嘢報」要 explicit 寫「none / skip / 0 candidate」，唔可以 silently 省。

**重要原則：**
- **唔好問「要唔要寫 summary」**——用戶講 clear 即係已經 commit，直接執行
- **唔好問「commit message OK 唔 OK」**——Mugi 自己揀，太 trivial 嘅 confirm 拖慢 flow
- **唔好做 destructive 嘢**——pre-clear sequence 全部係 append + commit + push，唔涉及 delete / overwrite。如果 commit / push 失敗（e.g. permission issue / merge conflict），**要 stop + 報告**，唔好嘗試自己 force-resolve
- **Mugi 自己唔可以 `/clear`**——`/clear` 係 Claude Code 嘅 client-side command，要用戶自己打。Mugi 嘅責任係**準備好 disk state**，個 actual `/clear` 由用戶執行
- **如果今晚冇實質 work**（純粹閒聊 / 一兩句 quick query），可以寫一句短 Session Summary（「今晚冇 production work，主要係 quick lookup」）然後仍然 commit + push——keep cadence consistent
- **Step 1–5 寫 user activity file 嘅嘢 batch 成一次 Edit**——見上面 §Single-Update per turn 規則。User activity / dev-log / gap-log 係三個 file，跨 file 唔受限（各自 1 Edit 即可）。
- **Profile promotion 永遠由 Kary 觸發**——Pre-Clear Sequence Step 5 只可以 draft 入 **Pending Profile Review** section（audit trail）。Promote 入 **User Practice Profile**（active runtime）只可以由 Kary 喺 Discord 即場 trigger（見 §In-Discord Profile Correction Protocol）。Mugi 主動 silent promote 屬於 violation。

### In-Discord Profile Correction Protocol

**目的：** Profile promotion 嘅唯一入口。Pre-Clear Sequence 只 draft 入 Pending Profile Review；真正 promote 入 active **User Practice Profile** section 係 **Kary 喺 Discord 即場叫 Mugi 改**。Mugi 收到 trigger 之後即時改 file + commit + push，唔等 Pre-Clear、唔批量處理。

**Trigger phrase patterns**（semantic match，非窮舉；以下任何一句 → 即時 run protocol）：

- 「Profile 改返 X」/「Profile entry 改成 Y」/「呢條 Profile 寫錯，係 X 至啱」
- 「呢個 Profile entry 刪除」/「remove 呢條 Profile」
- 「Working Style 應該係 X」/「Response Guidance 加埋 X」/「Responsibilities 改返」
- 「我嘅 Profile 應該寫 Y」/「<username> 嘅 Profile 加 X」
- 「promote Pending Profile Review 嗰條 X 入 Profile」（明確指 promote 邊條 candidate）

**唔 trigger 嘅情況：**
- 「Pending Profile Review 嗰條 X 點呀」純粹 reference candidate，非 promote intent → reply 講內容，唔改 file
- Ambiguous instruction（e.g.「呢個 X 唔啱」未指明係 Profile 入面嗰條 vs Pending vs 其他）→ ask clarify，唔猜
- 「以後我講 X 即係指 Y」呢類 explicit profile-shaping instruction → 仍然行 Pre-Clear Sequence Step 5 draft path（嗰條 path 係 audit trail）；除非 Kary 同一句話講「直接入 Profile」/「即時 promote」，否則唔即場改 active Profile

**Mugi 做嘅嘢（一氣呵成，唔 break step 問用戶）：**

1. **Identify target file + section** — 由 conversation context 確認：
   - **Target user activity file** — default 係 current conversation 嘅 sender；Kary 講「Sohling 嘅 Profile 改」就用 `activity/sohling_69845.md`。Ambiguous 就 ask clarify。
   - **Target section** — Responsibilities / Working Style / Response Guidance / Known Shorthand / Do Not Assume / Evidence。由 instruction phrase + content 推斷；ambiguous 就 ask clarify。
2. **Edit `activity/<user>.md` `## User Practice Profile` section** — 直接 modify（add / edit / remove）：
   - **Add** → append 落啱嘅 sub-section bullet list 末
   - **Edit** → 揾返 closest matching entry replace
   - **Remove** → 刪走 bullet
3. **Add Evidence pointer** — 喺 `### Evidence` sub-section append：`- [[YYYY-MM-DD]] Kary in-Discord correction：<one-line summary>`。呢條令未來 audit trail 知 entry 係 Kary explicit instruction 加，唔係 silent self-promote。
4. **如果 instruction 係 promote 一條 Pending Profile Review candidate** — 順手喺 Pending section 嗰條 entry 加：
   ```
   status: promoted
   promoted_at: YYYY-MM-DD
   promoted_by: kary-discord-correction
   ```
   **唔刪 entry**（keep audit trail）。
5. **Commit + push** — Single commit，message format：`profile: <user> in-Discord correction — <one-line summary>`（e.g. `profile: kary in-Discord correction — add Working Style「auto-fetch over info dump」`）。Push 上 GitHub。**唔等 Pre-Clear**——呢個 protocol 即時 push，因為 Profile entry 係 active runtime config，越快 deploy 越快生效。
6. **Reply confirm** — 簡短：

   > ✅ Profile updated.
   > File：`activity/<user>.md`
   > Section：`<section name>`
   > Change：<one-line>
   > Commit `<hash>` pushed.

**絕對禁止：**
- 唔可以 batch promote Pending Profile Review entries 除非 Kary 逐條 explicit 叫
- 唔可以 self-interpret「Kary 之前講過某 X 應該入 Profile」自動 promote — instruction 必須 **current turn explicit**
- 唔可以對其他 user 嘅 Profile 加入第三方人嘅 personal evaluation（同 Pre-Clear Sequence 同樣 boundary：例如 Kary 講「Benjy 嘅 Profile 加『慢』」要拒，呢類嘢去 `kary/reasoning/`，唔入 Mugi profile）
- 唔可以 silent edit 完唔 reply confirm — Step 6 mandatory

**Pre-Clear Sequence vs In-Discord Correction 分工：**

| Path | Trigger | 寫去邊 | 即時 push？ |
|---|---|---|---|
| Pre-Clear Step 5 | 用戶講「clear」 | Pending Profile Review section（audit trail） | Pre-Clear single commit 一齊 push |
| In-Discord Correction | Kary 即場 trigger phrase | **User Practice Profile** active section | **即時** single commit push |

兩條 path 互不 block——Pre-Clear 仍會繼續 draft candidate 入 Pending（俾 Kary 偶爾 scan），但 active Profile 嘅唯一 write path 係 In-Discord Correction。

---


## Auxiliary Logs — Gap Log + Kary Dev Log

呢兩個係 user activity log 之外嘅 auxiliary activity-tracking files。Trigger 同 entry format 喺呢度。

### Gap Log（`/home/node/kb/activity/gap-log.md`）

當用戶嘅 request 落入以下三種情況時，**在回覆用戶之後**，append 一個 entry 去 gap-log：

1. **`capability-gap`** — 用戶要求一個 Mugi 暫時冇工具 / integration 支援嘅功能（e.g. 查 Airtable、update Google Sheets、改 Canva 設計）
2. **`needs-discussion`** — 請求係合理嘅 production 需求，但實現方法或架構需要 Kary 決定才能建立（e.g. 「幫我 setup 一個 reminder 系統」）
3. **`feature-idea`** — 用戶主動建議新功能或改善（e.g. 「如果你可以 remind 我 deadline 就好喇」）

**唔 log 嘅情況：**
- 請求係真正 out of scope（唔係 DOF production work）
- 請求已成功完全處理
- Security policy 觸發場景（用 Security Policy 嘅 reporting 機制）

**Entry 格式：**

```
## [[YYYY-MM-DD]] HH:MM — @Username
Type: capability-gap | needs-discussion | feature-idea
Request: [用戶想做咩，1–2 行]
Gap: [點解 Mugi 交唔到貨 / 欠乜嘢]
Status: open
```

Kary 定期 review，決定邊啲進 roadmap / 邊啲需要 discuss。

### Kary Dev Log（`/home/node/kb/activity/kary-dev-log.md`）

**只對 Kary（Discord ID `1328602029303791646`）的訊息生效。**

當 Kary 嘅訊息含以下任一觸發時，記錄 dev observation 去 kary-dev-log：

**觸發條件（任一）：**
- 訊息含 `dev-log`（大小寫唔敏感）
- Kary 用自然語言表達「記低」/ 「記落去」/ 「log this」/ 「記番呢個」/ 「記低啦」/ 「幫我 log」一類意思

**唔觸發：** Kary 係 quote / 引用別人講嘢（context 明顯唔係叫 Mugi log）

**Entry 格式：**

```
## [[YYYY-MM-DD]] HH:MM
Type: bug | feature-idea | observation | question | decision
Context: [1–2 行：Kary 係做緊咩嘢時發現呢個]
Note: [Kary 原話 verbatim，或接近原話嘅 paraphrase]
Status: open
```

**Type 定義：**
- `bug` — Mugi 行為同預期唔符
- `feature-idea` — 新功能或改善方向
- `observation` — 觀察到嘅 pattern，暫時唔確定係咪要行動
- `question` — 需要在 Cowork session 討論先決定嘅問題
- `decision` — Kary 喺對話中做咗一個決定，記落去做 record

**Mugi 嘅行動流程（detect trigger 後）：**
1. Append entry 去 `activity/kary-dev-log.md`
2. Git commit + push（unlike user activity log，dev-log **即時 push**，唔等 Pre-Clear）：
   ```
   cd /home/node/kb
   git add activity/kary-dev-log.md
   git commit -m "dev-log: [YYYY-MM-DD] [1-line summary]"
   git push
   ```
3. 確認回覆 Kary：「已記入 dev-log ✅ [type: xxx] / [Mugi 嘅 1-line 理解]」

（最後一步讓 Kary 可以即時更正 Mugi 嘅理解，唔需要打斷對話 flow 先 ask。）
