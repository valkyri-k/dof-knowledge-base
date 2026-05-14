# Check Cut Saturation

> **用途：** Phase 2 trigger — 主動 propose shoot date candidates、check cut delivery saturation、處理 revised schedule regenerate。
> **Caller：** `skills/producer/producer-playbook.md` §0 Phase 2 (Push to Calendar 前)
> **Pair with：**
> - `skills/producer/generate-timeline.md`（Phase 1 timeline preview）
> - `skills/producer/calendar-ops.md`（Calendar list / write boilerplate）

---

## Shoot Date Planning（拍攝日未 lock 時，主動 propose）

**Trigger：** 用戶話「shoot date 仲未 confirm」/ 想搵日拍 / shoot date 留空 / 答「propose」/「揀日」。

**Combined turn pattern（單一 turn 兩段 script invocation）：**

呢個 case 嘅 reply 必須**一齊 surface**：(a) candidate list、(b) 用 default candidate 跑出嚟嘅 full-timeline preview、(c) explicit declaration 話今次 default 用咗邊個 candidate、(d) CTA 「想要 candidate 2 / 3 → 我 rerun」。

**步驟：**

1. 問用戶想 target 邊個 range（冇講就預設今日 + 7 至 14 working days）—— 如果 user 已經提供 final-output deadline / 上下文夠，就跳過呢步直接落 step 2
2. List Calendar events 喺嗰個 range，focus 揾：
   - 已 confirmed 嘅 shoot day（colorId 11）—— **hard conflict**，crew + gear 已 booked
   - 已 confirmed 嘅 cut delivery / picture lock / final output（colorId 7 / 3）—— **soft conflict**，post team occupied 但唔影響 shoot
   - VO recording / style frame confirm（colorId 1 / 9）—— light conflict，通常 OK
3. **Candidate phase — Run** `python3 scripts/timeline_backward.py --propose-shoot-mode --kickstart <today> --final-output <client deadline if known> --candidates 3`。Script 自動 handle Sat/Sun push、HK holiday avoid、Script Lock 5 wd minimum、tight-final flag。
4. **Pick default candidate**：
   - Default = `earliest_safe`
   - 如果 `earliest_safe` 撞 step 2 嘅 hard conflict（colorId 11） → fall through 落 candidate 2，再撞就落 candidate 3
   - 揀完一定要喺 reply explicit declare：「Default 用咗 candidate [N] = [date]」
5. **Full-timeline preview — Run** `python3 scripts/timeline_backward.py --today <today> --final-output <deadline> --shoot-mode standard --shoot-date <picked default> --has-vo <bool> --has-style-frame <bool> --project <name>`（即 `generate-timeline.md` Step 4 Pre-step A 嘅 invocation，但 shoot-date 用 step 4 揀出嚟嘅 default）
6. Parse 兩段 JSON → 寫 reply：candidate list（每個 date + weekday + wd_from_kickstart + label + Calendar conflict note）、explicit default declaration、full-timeline preview（milestones + warnings + cut_warnings 照 `generate-timeline.md` Step 4 reply convention echo）、CTA

**Reply template：**

> 「比較順嘅 candidate shoot dates：
> 1. **[date 1] (weekday)**——`earliest_safe`，Calendar 乾淨；kickstart 後 [N] wd
> 2. **[date 2] (weekday)**——`+1_buffer`，[Calendar 情況]
> 3. **[date 3] (weekday)**——`+2_buffer`，...
>
> [holidays_in_window 列表 + warnings echo]
>
> **今次我 default 用咗 candidate [N] = [date]** 行 full timeline preview（如果想用 candidate 2 / 3，講聲我 rerun）：
>
> [Full-timeline milestones list + VO window + warnings + cut_warnings — 跟 `generate-timeline.md` Step 4 reply convention]
>
> OK 唔 OK？OK 我就 push Calendar。」

**重要：**
- 唔好幫用戶 lock date——只係 propose + preview，最終決定喺人
- **Candidate phase + full-timeline phase 一定要喺同一 turn surface**——唔好淨 show full timeline 唔出 candidate list（user 唔知 default 用咗邊個 candidate = silent inferred shoot date）
- 用 default candidate 必須 explicit 講出嚟，唔可以 implicit
- **Candidate phase = zero inline Python**。Script 係 single source of truth；唔好 inline 重新 implement weekday / holiday math
- 用戶揀咗其他 candidate / lock date 之後 → rerun 行 `generate-timeline.md` Step 4 Pre-step A 嘅 full timeline script（加 `--shoot-date <picked>`）

---

## Cut Delivery Saturation Check（**Phase 2 trigger，唔喺 Phase 1 跑**）

**Saturation threshold：** 任何一日已有 **≥ 4 條片要交**（cut delivery colorId 7 + final output colorId 3 都計），嗰日就 saturated。

**做法（finalize timeline 之前自動執行）：**
1. 抽出每個 cut delivery date（1st Cut / 2nd Cut / 3rd Cut / Picture Lock / Final Output）
2. 對每個 date，list Calendar 嗰日同類 events（colorId 7 + colorId 3）
3. 已有 ≥ 4 → trigger warning

**Case 1：可以 push 後 1 日（preferred）**
> 「@用戶 開份 timeline 之前 flag 一樣嘢：
>
> 你嘅 **1st Cut 預咗 [date]**，但 Calendar 顯示嗰日已經有 4 條片要交。再塞落去會變第 5 條，post team 嗰日真係頂唔順。
>
> **建議 push 後 1 日 → [next weekday]**——Cascade 落去後續 milestone 都同步 push 1 日，final output 由 [X] → [Y]。
>
> 噉樣 OK 嗎？」

**Case 2：push 後就 miss deadline → escalate Sohling**
> 「呢個 case 有少少棘手：
>
> [1st Cut date] 同其他 4 條片撞——push 後一日嘅話 final output 嗰邊就 miss 咗 client deadline（[date]），冇 push 後嘅空間。
>
> 呢個唔係 Mugi 一個人 judge 到——可能要 reshuffle 其他 project 嘅 cut delivery。
>
> @Sohling 入嚟睇下呢個 channel，幫手睇下嗰一日點 reshuffle。
>
> 你決定咗點之後俾我個文字版 revised schedule，我幫你 generate `_r2`。」

**Case 3：完全冇撞** → 主動講聲：「Cut delivery dates check 過 Calendar，post team 嗰幾日相對乾淨，冇 saturation 問題 ✅」

**重要：**
- Mugi **唔好擅自 push date**——永遠 propose + 等用戶 confirm
- 呢個 check **Phase 2 每次都做**——first generation confirm 後、Pattern F/I compression/加 cut confirm 後、用戶俾返 revised schedule 後

---

## Regenerate from Revised Schedule

用戶同 Sohling 傾好之後，可能攞到 revised schedule。用戶直接俾個文字版 Mugi 處理：

**Flow：**
1. Parse revised schedule — 抽取每個 milestone 嘅新日期 / 新 status
2. Echo 返 parsed 嘅 revised schedule 等用戶 confirm
3. Generate **新 file，唔好 overwrite 原本**（加 version suffix）
4. Fill 新 dates 到 template（同樣 two-phase write-then-delete）
5. Update Calendar events 配合新 dates
6. Return new doc link + confirm Calendar 已 sync，附同樣嘅 double check 提示

**Version suffix：**
- Original: `Timeline_J26015_HSUHK Student_2026-04-07`
- Revised: `Timeline_J26015_HSUHK Student_2026-04-08_r2`

**Confirm before regenerate：**
> 「OK，我理解 revised schedule 係：
> - 1st Cut: May 11（原本 May 9，push 2 日）
> - Skip 3rd Cut + FB3
> - Final Output: May 30（原本 May 29，push 1 日）
>
> 對嗎？對就 regenerate 做 `_r2`。」
