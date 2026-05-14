# Producer Playbook

> **Mugi 收到任何同 timeline generation、calendar 操作、document 生成相關嘅 request，必須先 read 呢份 file 由頭到尾一次，然後按入面嘅 flow 做。**
>
> 呢份 playbook 係 **orchestrator only**——每個 phase 嘅 detailed rules / tables / algorithm / wording 已抽出成 sibling skill file。Phase 開始嗰陣 read 對應 file。

呢份 playbook 涵蓋 Mugi 嘅 producer-role 工作：timeline 生成、calendar event 管理、Google Drive document 操作。

---

> ## 🔒 PHASE 1 TOKEN-CONTROL HARD RULES（違反 = REWRITE，唔係 best practice，係 contract）
>
> 1. **TIMELINE MATH = INVOKE SCRIPT，唔好 INLINE PYTHON**：所有 backward-planning math 由 `scripts/timeline_backward.py` 處理。Mugi 用 Bash CLI 入 args、parse 1-line JSON output、寫 reply。**唔好再 inline 寫 Python**（重 implement HK holidays / push_to_weekday / back_wd 邏輯）。Script 已經涵蓋 standard / compressed-edge-case / extreme-squeeze / Pattern J / pure-post 全部 branch。詳見 `skills/producer/generate-timeline.md` Step 4。
> 2. **JSON OUTPUT 唔可以 ECHO 落 REPLY**：Script stdout 1 行 JSON，Mugi 內部 parse；reply 入面只列人類可讀嘅 milestones / warnings / Pattern flags。**唔好 dump JSON 俾用戶睇。**
> 3. **SELF-CHECK 唔可以 ECHO**：Pre-step B 嘅 logic gates 係 mental check，**pass 就 pass，唔好喺 output 逐條 echo + reason**。只係 fail 嗰陣先 surface 嗰一條。
> 4. **SINGLE-SCENARIO**：一個 request 只 invoke 一次 script。唔好為咗對比 scenario 跑兩次（standard + compressed）—— script 內部已自動 fallback。
>
> 呢 4 條一齊行 Phase 1 先會 < 8k token。Spec 寫咗但唔跟 → token bloat 主因。

---

## 0. Workflow Phases（開工前必讀）

### Kickstart Anchor（hard default）

**Today = project kickstart date**——**hard default 假設**，唔需要用戶明確講「今日 kickstart」。Mugi 收到 timeline request 嗰陣自動將「今日」當 forward boundary：所有 milestone（backward derive 定 forward chain 出嚟都計）**唔可以早過 kickstart_date**。

**Effective kickstart（weekend / holiday push）：** 如果 `today` 落 weekend 或 HK public holiday → `effective_kickstart_date = next weekday + non-holiday`。所有 milestone math（backward chain check、Step F past-milestone detection、Compressed branch 計 Script Received 等）一律用 `effective_kickstart_date`，**唔好用** raw `today`。

> 例：今日 May 9 (Sat) → `effective_kickstart_date = May 11 (Mon)`。Compressed branch 嘅 Script Received 最快 May 11，唔可以排 May 9 / May 10。
>
> 理由：DOF 同 client side 兩邊都唔做 weekend / holiday，pre-pro 第一個 milestone（Script Received）落 weekend / holiday 等於假設 client 嗰日交嘢，唔 realistic。

**Override condition：** 用戶明確 state「[milestone] 已完成於 [date]」嗰陣，先將該 milestone lock 喺 stated date，當 partial pre-pro 已執行。冇 explicit「已完成」聲明 → 一律當未開始。

**為咩重要：** Backward-from-final-anchor algorithm 由 client deadline 倒推 pre-pro chain，如果倒推出嚟嘅 date 早過今日，silent 噉假設 client 已經做完嗰啲 pre-pro work 係**錯**——pre-pro 唔可以喺 kickstart 之前發生。Backward-derived milestone < `effective_kickstart_date` → 觸發 **Compressed-Edge-Case Branch**（見 `skills/producer/derive-milestones.md`；唔好默默加 `[已過]` tag）。

---

Timeline 工作分三個 phase，每個 phase 有獨立 gate。**絕對唔 auto-proceed 落下一 phase。**

### Phase 1 — Draft text preview
**Trigger：** 用戶第一次提 timeline（「幫 J26XXX draft timeline」、「排個 post schedule」、「generate timeline」）。
**Read first：**
- `skills/producer/derive-milestones.md`（Standard Milestone Set + Backward-Planning Algorithm + Compressed-Edge-Case Branch + Extreme-Squeeze Tier + Compression Rules + Milestone Completeness Rule）
- `skills/producer/generate-timeline.md`（Step 1–5 procedure + Pre-step A 嘅 script invocation + Pre-step B self-check + Pattern A–L flags）

**做：** 跟 `generate-timeline.md` Step 1–5 + Pre-step A–B。Output 文字版 markdown table + 適用嘅 Pattern A–L flags。

**Calendar API：嚴格 zero query**——director 由 `context/job-list.md` lookup；conflict / saturation 留 Phase 2 一次過做。Phase 1 = lightweight inference round（first-pass timeline 命中率本身唔高，user 一定會 feedback 調整；先 query Calendar 等於白做，schedule 穩定咗 Phase 2 一次過 query 反而 cleaner）。

**Special case — Shoot date 未 lock：** Trigger 「propose / 揀日 / shoot date 留空」 → 跳去 `skills/producer/check-cut-saturation.md` **Shoot Date Planning combined turn pattern**（必須同一 turn surface candidate list + default candidate full-timeline preview + CTA）。

**Gate：** 停低等用戶 confirm 文字版。**唔 auto-push Calendar。**

### Phase 2 — Push to Calendar
**Trigger：** 用戶 confirm Phase 1 個文字版（「OK」/「push 啦」/「可以」）。

**Read first：**
- `skills/producer/check-cut-saturation.md`（Cut Delivery Saturation Check Case 1 / 2 / 3 + Regenerate from Revised Schedule）
- `skills/producer/calendar-ops.md`（Service Account Write Boilerplate + Rules 1-4 + Ops Flow）

**做：** Phase 2 **開頭先**：對每個 cut delivery date（1st Cut / 2nd Cut / 3rd Cut / Picture Lock / Final Output）query Calendar 嗰日已有幾多 colorId 7+3 events。已有 ≥ 4 → surface warning + 暫停 push 等用戶決定（見 `check-cut-saturation.md`）；全部 clear → Create events on dof.internal Calendar（`dof.internal@gmail.com`）。

> 🚫 **Tool path（強制）**：用 `calendar-ops.md` 嘅 Service Account Python boilerplate（`service.events().insert(calendarId='dof.internal@gmail.com', ...)`）。**禁止用任何 Calendar MCP tool**（`gcal_*`、`mcp__*calendar*`、claude.ai 嘅 "Google Calendar"）——MCP 會 create event 落 `karyto.dof@gmail.com` 而唔係 `dof.internal@gmail.com`。每次 `events().*` call 前 self-check `calendarId` value。

**Output：** 一句 summary + 問 Phase 3：

> ✅ [N] events pushed 到 Calendar。要唔要埋份 for-client Google Doc？（唔使就 done）

**Gate：** 用戶答要 / 唔要 / 唔答 → stop at Phase 2。

### Phase 3 — Doc generation（opt-in only）
**Trigger：** 用戶答「要」/「好」/「出埋」——或後來話「出 timeline doc for J26XXX」/「幫我出埋份 doc」。

**Read first：** `skills/producer/generate-timeline-doc.md`（Table Row Deletion Two-Phase Pattern + Doc Naming + Output Location + Adding New Document Types）。

**做：** **跳過 Step 1–5 + Pre-step A–B。** Search Calendar by J-number 攞 committed dates，直接跟 `generate-timeline-doc.md` Row Deletion + Doc Naming 寫入 Timeline_Template。

**Gate：** 冇 gate——doc 寫完 return Drive link 就算。

### Anti-patterns（嚴格禁止）

- ❌ Phase 1 完 auto-push Calendar（一定要 confirm 先 push）
- ❌ Phase 2 完 auto-gen doc（問先，冇得假設）
- ❌ Phase 3 時重跑 Pre-step A–B（dates 已 committed，重跑係 wasted token）
- ❌ Phase 3 時再 flag Pattern A–L（dates 已 lock，flag 無 actionable value）
- ❌ Phase 1 invoke 多次 script 對比 scenario（standard + compressed）—— Single-Scenario Rule，script 內部已自動 fallback
- ❌ Phase 1 query Calendar API（director 由 `context/job-list.md` lookup；conflict / saturation / 已 marked event 全部留 Phase 2 一次過）
- ❌ Inline 寫 Python 重做 timeline math（HK holidays / push_to_weekday / back_wd 邏輯由 `scripts/timeline_backward.py` 唯一實作 — 永遠 invoke script）
- ❌ Echo script JSON output 落 reply（user 睇人類可讀 markdown，唔睇 JSON）
- ❌ Self-Check logic gates 喺 reply 入面逐條 echo + reason（mental check only，pass 唔出聲）
- ❌ 假設 filming window length = actual shoot day count（e.g. 「Filming May 18–22」 ≠ 5 日連拍）—— 必須 `generate-timeline.md` Step 3 ask
- ❌ Silent compress 1st Cut（或任何 cut）唔 flag——script `cut_warnings` 入面任何 cut ≤ 3 wd 一律照原樣 echo 落 reply，唔可以 hide
- ❌ 留 idle window 喺 FB-last 同 Picture Lock 之間（slack 應該 distribute 落 cut gaps，唔好 default 落 trailing buffer）
- ❌ Shoot date 未 user-confirm 嘅 case，淨 show full timeline 唔 surface candidate list——必須一齊出（`check-cut-saturation.md` Shoot Date Planning combined turn pattern），default 用邊個 candidate 必須 explicit declare

---

## Sub-Skill Dispatch

| Phase / Use case | Read |
|---|---|
| Phase 1 milestone derivation + algorithm | `skills/producer/derive-milestones.md` |
| Phase 1 procedure + script invocation + Patterns | `skills/producer/generate-timeline.md` |
| Phase 2 cut saturation + revised schedule regenerate | `skills/producer/check-cut-saturation.md` |
| Phase 2 Calendar event add / move / delete + Rules 1-4 | `skills/producer/calendar-ops.md` |
| Phase 3 doc write (Two-Phase pattern) + naming + new doc types | `skills/producer/generate-timeline-doc.md` |
| Shoot date 未 lock (Phase 1 special case) | `skills/producer/check-cut-saturation.md` Shoot Date Planning |
| Standalone calendar ops（add / move / cancel 單一 event） | `skills/producer/calendar-ops.md` 直入，唔需要 Phase gate |

---

## Timeline FAQ Logic

**「J26015 幾時交片？」**
→ Search Calendar by J26015 → 搵 Final Output event → 回答日期
→ 如果冇 Final Output event → 搵最遠嘅 milestone → 根據標準工時推算

**「推後咗一個禮拜，之後啲嘢幾時？」**
→ 搵到受影響嘅 events → 列出新日期 → 等用戶 confirm → Batch update

**「1st Cut 之後幾耐先有 2nd Cut？」**
→ 標準工時：Client FB 1 = 3 wd + 2nd Cut 3–5 wd = 大約 **6–8 working days**（見 `skills/producer/derive-milestones.md` Standard Milestone Set）

---

## colorId Reference（Authoritative）

| 類別 | 包含嘅 Milestones | colorId | 顏色 |
|------|-------------------|---------|------|
| Pre-Production (DOF deliverable) | Script Received, Submit Video Flow, Submit Graphics Reference | `5` | Banana（黃色）|
| Style Frame submit | Submit Style Frame | `9` | Blueberry（深藍色）|
| Client Review | Script Lock (= Confirm Video Flow), Confirm Graphics Reference, Confirm Style Frame, Client FB 1, Client FB 2, Client FB 3 | `2` | Sage（綠色）|
| Shooting | Shooting（single or multi-day range）| `11` | Tomato（紅色）|
| Post-Production | 1st Cut, 2nd Cut, 3rd Cut, Picture Lock, Color/Sound/Subtitle | `7` | Peacock（淺藍色）|
| VO Recording | VO Recording window | `1` | Lavender（薰衣草紫）|
| Final Output | Final Output | `3` | Grape（葡萄紫）|
| 其他 | Site Recce, Wardrobe Fitting 等 | `5` | Banana（fallback）|

### 判斷關鍵詞（Search Calendar event 時識別 type）

- 「拍攝」「shoot」「shooting」→ colorId: `11`
- 「1st cut」「2nd cut」「3rd cut」「picture lock」「color grading」「sound mix」「subtitle」→ colorId: `7`
- 「script lock」「confirm video flow」「confirm graphics ref」「confirm style」「client feedback」「FB1」「FB2」「FB3」→ colorId: `2`（client 做嘅嘢）
- 「style frame」「submit style」→ colorId: `9`
- 「final output」「交片」「出片」→ colorId: `3`
- 「VO」「配音」「voice over」→ colorId: `1`
- 「script received」「video flow」「graphics ref」「graphics reference」→ colorId: `5`

**技術注意：**
- colorId 係 string（`"7"`，唔係 `7`）
- 所有 single-day event 預設 all-day（用 `date`，唔係 `dateTime`）
- Range event（Shooting / VO Window）：multi-day all-day，`end.date` = 最後一日 + 1（API end exclusive）
- Timezone: `Asia/Hong_Kong`
