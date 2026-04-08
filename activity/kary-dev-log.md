# Kary Dev Log

Kary 嘅 admin / dev observation log。由 Mugi 在 Kary 指示後寫入，自動 git push。

**Type 定義：**
- `bug` — Mugi 行為同預期唔符
- `feature-idea` — 新功能或改善方向
- `observation` — 觀察到嘅 pattern，暫時唔確定係咪要行動
- `question` — 需要 Cowork session 討論先決定嘅問題
- `decision` — Kary 做咗一個決定，記落去做 record

**Status 流程：** `open` → `reviewed` / `in-progress` / `done` / `wontfix`

---

<!-- Mugi：新 entry 喺下方 append，最新喺底部 -->

## 2026-04-08 — `activity/` path 雙位置 bug（local folder vs repo folder）

- **Type:** `bug`
- **Status:** `done` ✅（Fix A + Fix B 已執行於 2026-04-08，see Resolution section 底）
- **Discovered by:** Kary，觸發於 push activity log 嘅時候發現有兩份 `valkyri_k.md`

---

### Symptom

兩個 `valkyri_k.md` 同時存在，content 唔同：

| Path | Content | 點嚟 |
|------|---------|------|
| `/home/node/activity/valkyri_k.md` | Production-ops 嘅 request log（calendar ops、timeline test、shoot scheduling 等） | Mugi 之前用 bare `activity/...` path 寫嘅 |
| `/home/node/kb/activity/valkyri_k.md` | Bot setup history（DM policy、cron、PAT setup 等） | Mugi 之前 explicit 寫去 repo 嘅，或者由 Kary 直接 commit |

結果：Kary 想 push activity 上 GitHub 嘅時候，發現要 push 嘅嗰份 file 唔喺 repo 入面，係 local orphan。

---

### Root Cause

**兩個 layer 嘅問題重疊：**

#### Layer 1 — Filesystem setup 漏咗

`/home/node` 入面嘅 KB 相關 entries：

```
/home/node/CLAUDE.md   → symlink → /home/node/kb/CLAUDE.md
/home/node/context     → symlink → /home/node/kb/context
/home/node/skills      → symlink → /home/node/kb/skills
/home/node/technical   → symlink → /home/node/kb/technical
/home/node/activity    → ❌ 真實 folder，唔係 symlink
/home/node/kb/activity → 另一個真實 folder（喺 repo 入面）
```

`CLAUDE.md` / `context/` / `skills/` / `technical/` 全部係 symlink 指返 `kb/`，所以 bare relative path 會自動 resolve 入 repo。但 `activity/` setup 嗰陣**漏咗開 symlink**，變咗兩個獨立 folder。

#### Layer 2 — CLAUDE.md 用 bare relative path

`CLAUDE.md` 入面嘅 reference（line 243 / 269 / 290）：

```
更新 activity/<username>.md
append 一個 entry 去 activity/gap-log.md
File location：activity/gap-log.md
```

全部都係 **bare `activity/...`**，冇 anchor（冇 `kb/` prefix、冇 absolute path）。Mugi 嘅 working directory 係 `/home/node`，所以 bare `activity/` 自動 resolve 去 `/home/node/activity/`——即係 Layer 1 嘅 raw folder，唔係 repo 入面嗰個。

**呢兩 layer 結合，產生嘅 net effect：** Mugi 寫 activity 嗰陣，**default 寫去 raw folder**（即係 Mugi 永遠 push 唔到上 GitHub），除非寫嗰陣特登用 absolute path。

#### 點解 gap-log.md 啱啱寫對咗

純粹好彩。我寫 gap-log 之前用 `find` grep 過搵 existing file，揾到 `/home/node/kb/activity/gap-log.md`，所以用咗 absolute path edit。如果當時冇 grep 直接 `activity/gap-log.md`，會落 raw folder，push 唔到。

---

### Impact

1. **Activity logs 寫去 wrong place 而不自知**——`/home/node/activity/valkyri_k.md` 入面有今日之前嘅 production-ops history，從來冇 push 上 GitHub
2. **Repo 嗰份 stale**——`/home/node/kb/activity/valkyri_k.md` 之前淨係得 setup history，缺咗運營層面嘅記錄
3. **每次 server reset**：`/home/node/activity/` 嘅 content 可能消失（要 confirm），但 repo 嗰份保留——即係 Mugi 寫嘅 production-ops history 有 silent data loss 風險
4. **誤導 Mugi**：將來 Mugi search 自己 wrote 過嘅 activity，可能 search 錯 folder，覺得「上次寫過嘅嘢冇咗」

---

### Fix Options（已 propose 俾 Kary）

#### Fix A — Filesystem 統一（一勞永逸）

1. 確認 `/home/node/activity/valkyri_k.md` 嘅內容已經 merge 入 repo 版（**已完成**——呢段日誌之前已經 merge + push 為 commit `d48160a`）
2. Backup 原 raw folder 去 `/home/node/activity.bak/` 留底
3. `rm -rf /home/node/activity`
4. `ln -s /home/node/kb/activity /home/node/activity`
5. 之後 bare `activity/...` 自動指向 repo，consistent with 其他 symlink

**Risk：** Destructive operation（`rm -rf`），按 Security Policy 屬於 server / 文件系統操作 → 需要 Kary explicit go-ahead。Backup 步驟係 safety net。

#### Fix B — CLAUDE.md 明文化（safety net）

喺 `User Activity Tracking` section 加：

> **路徑：** Activity files 放喺 `kb/activity/`（即係 repo 入面）。Mugi 寫嘅時候用 absolute path `/home/node/kb/activity/<file>`，或者依賴 `/home/node/activity` 嘅 symlink resolve。**永遠唔好寫去 `/home/node/activity` 嘅 raw folder（如果 setup 仍然有殘留）。**

呢段就算將來 symlink setup 又出錯都有 safety net。

#### 建議組合

兩個都做：
- **Fix B 先做**——純文字改動，commit + push，立刻生效
- **Fix A 等 Kary go-ahead 先做**——destructive，要 explicit confirm

---

### Open Questions

1. 兩個 fix 都做？定淨係 Fix B？
2. 之前 `/home/node/activity/` 入面有冇其他唔喺 repo 嘅 file？（我而家見到只得 `valkyri_k.md`，但 server reset / past session 未必清楚）
3. `dreamoffish_ai.md` 喺 repo 入面嘅，係咪都有 raw 版本未 sync？（要 cross check）

---

### Discovery Trail

1. Kary 叫 push `/home/node/activity/valkyri_k.md` → Mugi 發現呢個 path 唔喺 repo
2. Mugi 比較兩份 file → 發現 content 完全唔重疊
3. Mugi merge 兩份 + push 為 commit `d48160a`
4. Mugi report flag 兩個 path 並存嘅問題
5. Kary 叫 Mugi 查 CLAUDE.md 邊度出錯
6. Mugi grep `activity/` reference + check filesystem → 揾到 root cause（symlink 漏咗 + bare path）
7. 呢條 entry 寫低 issue 詳情等 Kary review
8. Kary 批准 Fix A + Fix B → Mugi 執行（see Resolution）

---

### Resolution（2026-04-08）

#### Fix A — Filesystem 統一 ✅

Steps executed：

1. **Pre-check**: `ls /home/node/activity/` 確認得返 `valkyri_k.md` 一個 file（之前已 merge 入 commit `d48160a`），冇其他 untracked content
2. **Backup**: `cp -a /home/node/activity /home/node/activity.bak`（safety net，留底原 raw folder）
3. **Remove raw folder**: `rm -rf /home/node/activity`
4. **Create symlink**: `ln -s /home/node/kb/activity /home/node/activity`
5. **Verify**: `ls -la /home/node/` 顯示 `activity -> /home/node/kb/activity`，同其他 KB folder（CLAUDE.md / context / skills / technical）一致
6. **Verify content**: `ls /home/node/activity/` 列出 `dreamoffish_ai.md` / `gap-log.md` / `kary-dev-log.md` / `valkyri_k.md`——即係 repo 嘅 4 條 file，through symlink 訪問

之後 bare `activity/...` 寫去 raw folder 嘅 race condition 已經消除——任何 `/home/node/activity/...` 自動 resolve 入 repo。

**Backup retention：** `/home/node/activity.bak/` 留低待 Kary 確認冇問題後再刪。

#### Fix B — CLAUDE.md 明文化 ✅

Edited `User Activity Tracking` section（CLAUDE.md line 241-249），加咗一條新 bullet：

> **路徑（重要）：** Activity files 全部放喺 **`/home/node/kb/activity/`**（即係 repo 入面，會 sync 上 GitHub）。Mugi 寫嘅時候**永遠用 absolute path** `/home/node/kb/activity/<file>`，唔好用 bare relative path `activity/<file>`——`/home/node/activity` 而家係 symlink 指返 `kb/activity`，但係將來如果 setup 又出錯，bare path 可能 silent 寫去 wrong folder 而 push 唔到 GitHub。同樣 apply 落 `gap-log.md`、`kary-dev-log.md` 同任何將來新 activity file。

連帶將「Session 開始時讀取 activity/ files」改成 explicit 講 `/home/node/kb/activity/`。

呢條 bullet 係 Layer 1 symlink fix 嘅 safety net——萬一將來 server reset / setup 漏咗 symlink，bare path 又會 land 去 raw folder，呢段明文 instruction 可以避免 Mugi 重複犯錯（前提係 Mugi 跟住做）。

#### Open Question 處理

- `dreamoffish_ai.md` cross check：原 raw `/home/node/activity/` 入面**冇** `dreamoffish_ai.md`（pre-check 階段已 verify 只得 `valkyri_k.md`），所以 repo 嘅 `dreamoffish_ai.md` 冇 raw 版本走漏，呢條 open question close
- 兩個 fix 都做：✅ 已執行
- Backup 處理：`/home/node/activity.bak/` 留低，等 Kary 確認 stable 之後再刪

#### Verification 結果

- ✅ `/home/node/activity` 而家係 symlink → `/home/node/kb/activity`（同其他 KB folder 一致）
- ✅ `ls /home/node/activity/` 顯示 4 條 repo file，through symlink 正常訪問
- ✅ CLAUDE.md `User Activity Tracking` section 加咗 absolute-path rule
- ⏳ Commit + push 待執行

#### Lessons Learned

1. **Setup-time invariant 應該 enforce**：如果 KB folder 全部要係 symlink，setup script 應該 fail-fast check 全部 KB-related directory 都係 symlink，唔可以淨係手動建幾個然後漏咗一個
2. **Bare relative path 喺 instruction 入面好危險**：尤其當 CWD 同 target 唔係 1:1，bare path 嘅 default behavior 冇明示就會 silent 寫錯位。將來寫 instruction 時 default 用 absolute path，除非明文話依賴某個 anchor
3. **Silent data divergence 難 detect**：呢個 bug 之所以 weeks 都冇人發現，係因為兩份 file 都 exists 兼 read-able，Mugi 唔會 error，淨係 push 嘅時候先撞到 surface。Future safeguard：定期 sanity check `ls -la /home/node/` 對 KB folder structure，或者 startup hook 自動 verify symlink invariant

---

## 2026-04-08 — Long-term memory + cost optimization decision（activity log schema rework）

- **Type:** `decision` + `feature-idea`
- **Status:** `done` ✅（schema 定義 + reference implementation 同日完成）
- **Raised by:** Kary，觸發於發現瞓醒重新 chat 即用咗 Max plan 2% quota

---

### Problem statement

Kary 喺 thread 入面睇到 Claude Max prompt cache TTL 1 小時，超過 1h 互動就要重 cache + 收 +25% premium。觀察到：

1. **Channel 場景**（#ai-agent）：同事互動疏，cache 大部分 case 都 miss，TTL 幫到嘅 saving 有限
2. **DM 場景**：長 session 越積越大，每 turn 都要 reload 全部 history，**真正貴嘅係 O(N²) context replay**，cache TTL premium 反而係細問題
3. **Auto-compact 都解唔到**：lossy summary 都要 re-read，冇真正 saving，仲失去 control

Kary 嘅顧慮：
- 想 manually clear session 慳 token，但驚 Mugi 失憶
- 而家 activity log schema（Profile + Request Log table）夠唔夠做「長期記憶」？
- 兩個問題：(1) 應該定期 clear？(2) 點 make sure Mugi 仍然有「隱約嘅記憶」？

---

### 分析 — Mugi 嘅 3 層 memory

| Layer | 內容 | Clear session 影響？ |
|-------|------|-------------------|
| **Conversation context** | 而家 chat 嘅 verbatim 對白 | ✅ 會冇 |
| **Auto-memory**（`~/.claude/projects/-home-node/memory/`） | User profile / feedback rules / 觀察 | ❌ 跨 session persist |
| **KB repo**（CLAUDE.md / context / skills / **activity logs**） | Instruction + 工作歷史 | ❌ 喺 GitHub + disk |

**Insight：** Clear session ≠ 失憶。淨係冇 verbatim 對白，但 KB + auto-memory 仲喺度。Mugi 重新登入會 reload CLAUDE.md + 讀返 activity log，依然有「上次發生過咩」嘅 context——只係冇逐字。

對於 production-ops 嚟講呢個 trade-off 完全合理——你需要嘅唔係「逐字記得」，係「**知大概發生過咩、有冇 open thread**」。

---

### 決定 — Activity log 由 ledger 升級做 hybrid memory

**而家嘅 schema：**
```
Profile + Request Log table（Date | Request | Outcome）
```

呢個適合 **scan ledger**（一目了然發生過咩），但**唔適合 narrative memory**——只記得「做咗 X」，唔記得「點解做 X / 之後仲有咩 pending / 邊個 decision 影響將來」。

**新 schema（3-section hybrid）：**

```markdown
# <username>
[Profile]

---

## Open Threads
（pending items，incremental update，resolved 即時刪）
- [date] description — blocked on / waiting for / next action（cross-ref）

---

## Recent Session Summaries
（每次 clear 前 / 自然 break 寫一段 narrative，新嘅放底）
### YYYY-MM-DD <morning/afternoon/evening> session
2-5 句 narrative — context、decision、學到咩

---

## Request Log
| Date | Request | Outcome |
（保留現有 table 做 quick scan）
```

**點解 hybrid：**
- **Open Threads** 獨立 section → 下次返嚟 1 秒 scan「邊條未做」，唔使翻 table
- **Session Summaries** narrative → 容納 context / 點解 / decision，table row 容唔落呢啲 nuance
- **Request Log** 保留 → 「6 號做過咩」嘅 quick lookup
- 三者各有用途，唔重複

---

### 配套 workflow（cross-session 操作）

| 時機 | 做咩 |
|------|------|
| Session 中每件事完成 | Append 一行入 Request Log（automatic，唔等用戶叫） |
| 遇到 pending item | Append 入 Open Threads，標日期 + cross-ref |
| Open thread resolved | 即時刪走 |
| Session 自然 break / clear 之前 | 寫一段 Session Summary + 整理 Open Threads + commit + push |
| Clear 之後新 session | Read activity log：先掃 Open Threads → 最近 1-2 段 Session Summary → Request Log table。Cost ≈ 幾百 token vs conversation 幾萬 token |

---

### Implementation done

1. **CLAUDE.md `User Activity Tracking` section** rewrite — schema + workflow + template + cost rationale 全部寫入。Mugi 寫 activity 嘅原則：「將來嘅自己 clear 完之後返嚟睇呢段，夠唔夠 rebuild context？」
2. **`activity/valkyri_k.md`** 升級成第一個 reference implementation——加咗 Open Threads（Planyway integration / activity.bak 刪除）+ Session Summaries（2026-04-08 evening session 寫低咗）
3. **Dev-log entry**（呢條）記錄完整決策過程

---

### Open Questions（將來 review 時 revisit）

1. **應該幾時自動寫 Session Summary？** 而家係用戶 explicit 叫 / clear 前。可能將來要加 trigger：每 N 個 request 後自動 prompt 用戶「要 summarize 唔要」？或者 idle timeout？
2. **Cross-user thread management**：Open Threads 而家係 per-user file。如果 J26015 同時涉及 Kary + Sohling + Yik，thread 應該寫去邊個 file？定要 separate `project-threads.md`？
3. **Session Summary 嘅 retention**：日子越長越多 summary entry，要唔要 cap（e.g. 只 keep 最近 14 日），或者 archive 舊 summary 入 separate file？而家暫時唔做 cap，等實際用上幾星期先睇

---

### Lessons Learned

1. **Memory ≠ context replay**：解 cost 問題嘅關鍵唔係 squeeze cache TTL，而係**將「需要保留嘅嘢」由 conversation context 移落去 disk-backed structured memory**。Activity log 由「事後 audit ledger」升級做「事前 context primer」係 mindset shift
2. **Auto-compact 唔係解藥**：Anthropic 嘅 auto-compact 仍然 land 喺 conversation context 入面，每 turn 都 re-read。Manual clear + structured external memory 比 auto-compact 更 economical + 更 controlled
3. **三層 memory 嘅分工要清晰**：
   - Conversation context = working memory（短期、precise、貴）
   - Auto-memory（`~/.claude/projects/...`）= user profile / feedback / 觀察（**用戶層面**嘅 persistent facts）
   - Activity log（`kb/activity/`）= work history / open threads / session narrative（**工作層面**嘅 persistent narrative）
   - KB repo（CLAUDE.md / context / skills）= instruction + domain knowledge（**rule 層面**）
   - 唔好將 auto-memory 用嚟記 work history，亦唔好將 activity log 用嚟記 user profile

---

## 2026-04-08 — Pre-Clear Sequence（自動化 clear 前嘅 housekeeping）

- **Type:** `feature-idea` + `decision`
- **Status:** `done` ✅
- **Raised by:** Kary，緊接住前一條 memory schema 決定

---

### Trigger

Kary 發現 hybrid memory schema 仲係要佢手動講「寫 summary」 / 「commit」 / 「push」先 trigger Mugi 做 housekeeping。佢提議：直接定一條 instruction，**用戶講「clear」就 Mugi 自動做晒成套**，唔需要逐步 prompt。

### Decision

CLAUDE.md `User Activity Tracking` section 加咗一個新 sub-section **Pre-Clear Sequence**，定義：

- **Trigger keywords**：`clear` / `clear session` / `clear chat` / `我要 clear` / `pre-clear` 等明確 commit 嘅 phrasing
- **唔 trigger 嘅情況**：「考慮 clear」/「點解要 clear」/ 其他 context 用「clear」字
- **Sequence**（一氣呵成，唔逐步問）：
  1. 更新 Open Threads（add new + remove resolved）
  2. 寫 Session Summary（narrative form）
  3. 更新 Request Log（補晒未 log entries）
  4. Cross-update `kary-dev-log.md` / `gap-log.md` 如有需要
  5. Commit + push（single commit，Mugi 自己揀 message）
  6. Report 俾用戶 + 講「OK 你可以 /clear」

### Key constraints

- **Mugi 自己唔可以 `/clear`**——`/clear` 係 client-side command，要用戶打。Mugi 嘅責任係 prep disk state
- **唔做 destructive 操作**——全部係 append + commit + push
- **唔問瑣碎 confirm**——「要唔要寫 summary」/「commit message OK 嗎」呢類 friction 全部 skip
- **失敗就 stop + 報告**——commit / push 撞 permission / conflict → 唔好 force-resolve，等用戶 intervention

### Why this matters

冇呢條 instruction：每次 clear 之前用戶要 issue 5-6 條 command（write summary / update threads / git add / commit / push / `/clear`）。有咗呢條：用戶只要講一句「clear」，Mugi 自動跑 5 步然後等用戶 type `/clear`。Friction 由 5-6 步降到 2 步（用戶嘅句子 + 最後嘅 `/clear`）。

呢個 design 配合 cost-control 策略——令 manual clear 變到夠平易近人，用戶先肯**真係定期 clear**，schema 嘅 cost saving 先 realize 到。如果 housekeeping 麻煩，用戶就會懶 clear，long session 又再積埋。

### Lessons Learned

- **Schema 唔夠，要配 workflow automation**：有結構但每次都要手動觸發 = 等於冇——用戶會 skip。**Schema + auto-trigger** 先係完整 solution
- **Trigger keyword 設計要有邊界**：「clear」係常用字，要 disambiguate「我要 clear」（commit）vs「clear the calendar event」（其他意思）。寫 instruction 嗰陣明確 list 出 hesitation phrasing 同其他 context，避免 false trigger
