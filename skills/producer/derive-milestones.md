# Derive Milestones

> **用途：** Timeline generation Phase 1 — 由 Final Output anchor 倒推所有 milestones（hot path：canonical milestone list + completeness rule）。
> **Caller：** `skills/producer/producer-playbook.md` §0 Phase 1
> **Pair with：** `skills/producer/generate-timeline.md`（procedure / Pre-step / preview format）
> **詳細 algorithm：** `skills/producer/derive-milestones_reference.md`（VO window logic / Pre-Pro chain reasoning / Backward-Planning Step 0–F / Compressed-Edge-Case Branch / Extreme-Squeeze Tier / Compression Rules）—— Phase 1 hot path **唔需要**load。Troubleshoot / explain rationale 先 load。

---

> ## 🔒 HOLIDAY VERIFY BAN（呼應 producer-playbook.md Hard Rule #1）
>
> 呢份 file 純粹 reference algorithm — **唔可以**用嚟做 hand-verification 嘅藉口。所有 backward chain math（HK holiday skip / push_to_weekday / back_wd）由 `scripts/timeline_backward.py` 唯一實作。
>
> 讀完呢度之後**禁止**：
> - 「等我自己 verify 下個 chain 啱唔啱」嘅 inline Python
> - `cat hk-*.json` 確認 milestone 撞唔撞 PH
> - 重新計算 script 已 output 嘅 dates
>
> Script output = ground truth。如果 output 同直覺有差距 → reply 內部 reason，唔係 inline 重做。

---

## Standard Milestone Set（Single Source of Truth）

呢個係**完整 timeline 入面所有 milestones 嘅 canonical list**。Mugi 生成 timeline 時逐個 enumerate，唔可以揈做 date range，唔可以 silent 噉漏 push 邊個。

### Pre-Production

每個都係**獨立 row + 獨立 calendar event**，即使有啲 default 同一日 schedule（Submit Video Flow + Submit Graphics Ref；Script Lock + Confirm Graphics Ref）。

| # | Milestone | Calendar Title | Party | colorId | 由 previous milestone 算起 |
|---|-----------|---------------|-------|---------|---------------------------|
| 1 | Script Received | `Script Received - [Project]` | Client | 5 (Banana) | T0 anchor — client share script / materials 嘅日子 |
| 2 | Submit Video Flow | `Submit Video Flow - [Project]` | DOF | 5 (Banana) | **+5–6 wd from #1** |
| 3 | Submit Graphics Reference | `Submit Graphics Ref - [Project]` | DOF | 5 (Banana) | **Same day as #2**（default） |
| 4 | Script Lock | `Script Lock - [Project]` | Client | 2 (Sage) | **+5 wd from #2**（client review，可能涉及 senior approval） |
| 5 | Confirm Graphics Reference | `Confirm Graphics Ref - [Project]` | Client | 2 (Sage) | **Same day as #4**（default）/ 可以 propose 提早 |
| 6 | Submit Style Frame | `Submit Style Frame - [Project]` | DOF | 9 (Blueberry) | **+2–3 wd from #5** — **only if project 有 style frame chain** |
| 7 | Confirm Style Frame | `Confirm Style Frame - [Project]` | Client | 2 (Sage) | **+1–2 wd from #6** — same condition as #6 |

### Shooting

| # | Milestone | Calendar Title | Party | colorId | Notes |
|---|-----------|---------------|-------|---------|-------|
| 8 | Shooting | `([N] Days) Shooting - [Project]` | Both | 11 (Tomato) | Multi-day shoot 用一個 multi-day all-day event。Working Day Cross Check **exempt**。 |

**Pre-Pro → Shoot 最關鍵 dependency：** Shoot date − Script Lock (#4) = **7 wd**（standard）/ 3 wd（compressed min）。Pre-pro total T0 → Shoot ≈ **17–18 wd (~3.5 週)** standard。詳細 chain reasoning + compressed branch 見 `_reference.md`。

### Post-Production

⚠️ Cut / FB gap 係 **MINIMUM**——實際 distribute slack logic 喺 `_reference.md` Backward-Planning。Final Output 係 hard anchor，**唔係**由 #9 forward chain 推出嚟。

| # | Milestone | Calendar Title | Party | colorId | 由 previous 算起（MIN） |
|---|-----------|---------------|-------|---------|---------------------|
| 9 | Submit 1st Cut | `1st Cut - [Project]` | DOF | 7 (Peacock) | **Shoot + 5 wd**（pure-post：唔適用，pure-post 用 `--mode {animation\|mixed\|edit}` 由 picture_lock backward chain，milestone names 唔同） |
| 10 | Feedback on 1st Cut | `Client FB 1 - [Project]` | Client | 2 (Sage) | **#9 + 3 wd MIN** |
| 11 | Submit 2nd Cut | `2nd Cut - [Project]` | DOF | 7 (Peacock) | **#10 + 3 wd MIN**（slack distribute 加上去，cap 5 wd） |
| 12 | Feedback on 2nd Cut | `Client FB 2 - [Project]` | Client | 2 (Sage) | **#11 + 3 wd MIN** |
| 13 | Submit 3rd Cut（optional）| `3rd Cut - [Project]` | DOF | 7 (Peacock) | **#12 + 3 wd MIN** |
| 14 | Feedback on 3rd Cut（optional）| `Client FB 3 - [Project]` | Client | 2 (Sage) | **#13 + 3 wd MIN** |
| 15 | Picture Lock | `Picture Lock - [Project]` | Both | 7 (Peacock) | **Backward-derived**：VO window start - 1 wd（有 VO）/ #17 - 1 wd（冇 VO）。**唔係**由 #14 forward chain。 |

### Delivery

⚠️ Delivery tail 全部 **backward-derived from Final Output anchor**。

| # | Milestone | Calendar Title | Party | colorId | 點計 |
|---|-----------|---------------|-------|---------|------|
| 16 | VO Recording (window) | `([N] Days) VO Recording - [Project]` | DOF | 1 (Lavender) | **Backward-derived**：window end ≤ #18 - 2 wd；長度 2 wd；start = end - 2 wd + 1 day。**Optional**——冇 VO recording / 用 AI VO 就 skip。Window 詳細 logic（working day cross check / preview format）見 `_reference.md` |
| 17 | Color, Sound Mixing, Subtitle | `Color/Sound/Subtitle - [Project]` | DOF | 7 (Peacock) | **Backward-derived**：#18 - 1 wd。Doc 必須保留，Calendar 亦 push |
| 18 | Final Output | `Final Output - [Project]` | DOF | 3 (Grape) | **Client deadline anchor**——hard anchor，**永遠唔向前 pull**。冇 client deadline → 主動問用戶。 |

---

## Milestone Prerequisites Quick Reference（Pre-step B ordering check 用）

逐 milestone 喺 chat reply 之前掃一次。任何一條 fail → 重 derive，唔好 silent push。

| Milestone | 必須 ≥ 邊個 |
|---|---|
| Script Received (#1) | `effective_kickstart_date` |
| Submit Video Flow / Graphics Ref (#2/#3) | Script Received |
| Script Lock / Confirm Graphics Ref (#4/#5) | Submit Video Flow（**注意 Script Lock = Confirm Video Flow，同一回事**） |
| Submit Style Frame (#6) | Confirm Graphics Ref（only if style frame chain 存在） |
| Confirm Style Frame (#7) | Submit Style Frame |
| Shooting (#8) | Script Lock（standard +7 wd / compressed min +3 wd） |
| 1st Cut (#9) | Shooting |
| 後續 cut / FB (#10–14) | 上一 milestone + MIN gap |
| Picture Lock (#15) | 最後一個 FB（有 cut chain 嘅話） |
| VO Recording start (#16) | Picture Lock + 1 wd |
| Color/Sound/Subtitle (#17) | VO Recording end（有 VO）/ Picture Lock（冇 VO） |
| Final Output (#18) | Client deadline（hard anchor，**唔向前 pull**） |
| 任何 backward-derived milestone | `effective_kickstart_date`（撞穿 → 觸發 Step F Compressed-Edge-Case，見 `_reference.md`） |

---

## Milestone Completeness Rule（必須跟從，唔可以漏）

**核心要求：** 所有 milestone 逐個 enumerate——每個獨立一行 + 獨立日期。前期 milestones **絕對唔可以**揈成 date range，亦**絕對唔可以**喺 Calendar push 時悄悄丟咗。

**三個位都要 1:1 對齊：**
1. Timeline preview（chat reply 入面俾用戶睇嘅 markdown table）
2. Document generation（寫入 Timeline_Template 嘅每一行）
3. Calendar push list（push 上 dof.internal Calendar 嘅每個 event）

### Optional Milestone Handling

| Milestone | 何時 skip | 點呈現 |
|-----------|---------|--------|
| 3rd Cut + FB 3 | Option B（用戶話「2 cut 夠」/ tight schedule） | 完全唔出現——preview 跳過、template 用 DeleteTableRow、Calendar 唔 create |
| VO Recording | 冇 VO recording / AI VO / 純配樂 / 無對白 | 同上，完全唔出現 |
| Submit Style Frame + Confirm Style Frame | 冇 motion graphics 嘅 simple corporate / event | 主動問用戶有冇 graphics，冇就 skip |
| Submit Graphics Ref + Confirm Graphics Ref | **完全冇 graphics**（「graphics 較少」仍然保留——client 都要 sign-off） | 同上，完全唔出現 |
| 整套 Pre-Pro（Script Received → Style Frame） | Pure post-pro（冇拍攝） | Skip pre-pro + Shooting，由 1st Cut 開始 |
| Color/Sound/Subtitle | **唔好 skip** | Doc 一定有（client transparency）；Calendar 唔 create event |

**「Skip」= 完全冇出現。唔係用「—」/ 「skipped」/ date range 嚟 collapse。冇中間態。**

### ❌ Anti-patterns

| ❌ 錯                                                                          | ✅ 啱                                                                                            |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `Pre-Pro (Script Received / Video Flow / ...) \| Apr 8 – May 1 \| ~3.5 週 OK` | 7 行獨立 milestone，每行有自己嘅 date                                                                    |
| Submit Video Flow 排喺 Script Received 之後 1–2 wd                               | 5–6 wd（standard）/ 3–4 wd（compressed）                                                           |
| Script Lock 排喺 Submit Video Flow 之後 1–2 wd                                   | 5 wd——client review 通常要一個禮拜                                                                    |
| Script Lock 同 Shoot 之間得 2–3 wd                                               | 7 wd（standard）/ 3 wd（min）                                                                      |
| Preview 有 Pre-Pro，Calendar push list 由 Shooting 開始                           | Preview 同 Calendar push 完全 1:1                                                                 |
| VO Recording 變成單一 day                                                        | VO 係 multi-day window                                                                          |
| Submit Video Flow + Submit Graphics Ref 變成 1 row                             | 兩個 separate row / Calendar event                                                               |
| Office milestone 排到 weekend 或 HK 公眾假期                                        | Default 排 weekday + non-holiday；撞到就 cross check + push 走                                       |
| 將 Color/Sound/Subtitle 喺 doc 入面 delete 咗                                     | Doc 一定要保留（client transparency）                                                                 |
| Final Output 早過 client deadline（forward-chain from Shoot 推出嚟）                | Final Output = client deadline anchor，由 final 倒推 C/S → VO → Picture Lock。多出嚟嘅 slack 落 cut gaps |
| Drop 3rd cut → silent pull Final Output 早                                    | Drop cut 時 Final Output 唔郁，slack 改落 1st/2nd cut gap 同 feedback                                 |
| Window 14–19 wd silent decide 行 2-cut 或 3-cut compressed                     | Mugi 主動 flag trade-off + 問用戶                                                                   |
| 冇 client deadline 直接 forward-chain 計到 Final Output                           | 主動問 client 嗰邊有冇 confirm final delivery date                                                    |
| Backward-derived milestone < kickstart date 默默加 `[已過]` tag 當已完成              | Backward chain 撞穿 kickstart → 觸發 Compressed-Edge-Case Branch；除非用戶 explicit「[milestone] 已完成於 [date]」否則一律當未開始 |
| Standard timeline 排 Style Frame parallel-with-1st-cut（捨 pre-shoot confirm）        | Standard timeline 仍然 Submit + Confirm Style Frame pre-shoot；parallel-with-1st-cut **只准** Compressed-Edge-Case Branch 用 |
| Forward chain 唔 anchor today，backward chain 倒推到任何日子（包括早過今日）都算 valid       | Kickstart date = today（default），所有 backward-derived milestone ≥ effective_kickstart_date；觸發 Step F + Compressed-Edge-Case |
| Today 落 weekend / HK holiday，仍然將 Script Received 排喺 today（e.g. Sat）  | `effective_kickstart_date = next weekday + non-holiday`；所有 Compressed milestone math 用 effective kickstart，唔係 raw today |
| Compressed-Edge-Case 排 pre-pro 全 zero-gap parallel（Script + Video Flow + Graphics Ref 全部同日 submit）| Compressed pre-pro **sequential with 1–2 wd minimum gap**（default 2 wd / floor 1 wd）；收到 script 同日 submit video flow / graphics ref 唔 realistic |
| Compressed-Edge-Case 第一反應 force 2-cut / drop 3rd cut                  | **Default 3-cut**（squeeze cut gap + feedback time）；drop 落 2-cut only when Senior Approval Rule explicit trigger；連 3-cut compressed 都頂唔順 → Extreme-Squeeze Tier |
| Compressed branch 仍頂唔順 deadline，Mugi 自己 force 出 final answer / push calendar | 走 Extreme-Squeeze Tier：surface 3 propositions（client feedback time / cut count / 1st cut squeeze）俾**導演**call，等決定咗先 push calendar |

---

> **詳細 algorithm（troubleshoot / explain rationale 用）：** `skills/producer/derive-milestones_reference.md`
> - VO Recording Window full logic（working day cross check / preview format / Calendar push spec）
> - Pre-Pro Chain Reasoning（5–6 wd / 5 wd / 7 wd 點解）
> - Backward-Planning Algorithm Step 0–F（kickstart anchor / final output / backward tail / forward min / cut count decision / slack distribution / past-milestone gate）
> - Compressed-Edge-Case Branch（Step F triggered output template + ⚠️ warning）
> - Extreme-Squeeze Tier（導演 escalation template）
> - Compression Rules（trigger list + compressed minimums table + Single-Scenario Rule）
