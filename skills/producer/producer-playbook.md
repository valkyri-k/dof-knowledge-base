# Producer Playbook

> **Mugi 收到任何同 timeline generation、calendar 操作、document 生成相關嘅 request，必須先 read 呢份 file 由頭到尾一次，然後按入面嘅 flow 做。唔可以靠記憶答。**

呢份 playbook 涵蓋 Mugi 嘅 producer-role 工作：timeline 生成、calendar event 管理、Google Drive document 操作。

---

## 1. High-Level Milestone Shape（Quick Recap）

> **Authoritative source（含 colorId mapping + 每個 milestone 嘅日期計算規則）：`context/calendar-operations-guide.md` Standard Milestone Set section。**
> 呢度係 quick recall only——generate 之前必須 read authoritative source，唔好憑呢段記憶 enumerate。

```
Pre-Pro:
  Script Received (T0)
  → Submit Video Flow + Submit Graphics Ref（同日，T0 + 5–6 wd standard / 3–4 wd compressed）
  → Script Lock + Confirm Graphics Ref（同日，Submit + 5 wd）
  → Submit Style Frame
  → Confirm Style Frame

Shooting:
  Single multi-day event（Script Lock + 7 wd standard / 3 wd min）

Post-Pro:
  1st Cut → Client FB 1 → 2nd Cut → Client FB 2 → [3rd Cut → Client FB 3 optional] → Picture Lock

Delivery:
  VO Recording window（PicLock + 1 wd start, 2 wd length, end ≤ Final Output - 2 wd）
  Color/Sound/Subtitle（doc-only，Calendar 唔 push）
  Final Output
```

**Submit / Confirm bundling rule：**
- Client-facing：同日 submit / 同日 confirm（兩對各一日）
- Calendar：4 separate events（surgical unbundle — post team 將來可能要分開 track）
- Doc / preview：4 independent rows

---

## 2. Calendar Event Modification Rules（Universal）

**呢套 rules 唔淨係 timeline generation 先做——任何時候 Mugi 要 add / move / reschedule / delete calendar events 都要 run。**

| Use case | 例子 |
|----------|------|
| Document Generation push timeline milestones | Timeline_Template 產生嘅 cut delivery events |
| 用戶手動 add event | 「J26015 1st cut 擺 5月10日」 |
| 用戶 move / reschedule event | 「將 J26015 2nd cut 延遲 2 日」 |
| 用戶 delete event | 「cancel 咗 J26008 個 VO recording」 |

**Mugi 嘅 default behavior：** 收到任何 calendar modification request → 先 run Rule 1 + 2 + 3，發現 trigger 就 flag 出嚟等用戶 confirm，唔好 silent 噉執行。

### Rule 1: Weekday + HK Public Holiday Check

任何 office 性質嘅 milestone target date 默認必須同時滿足：
1. **Weekday**（Mon–Fri）
2. **唔係 HK 公眾假期**（用 `en.hk#holiday@group.v.calendar.google.com` query verify）

Apply 喺**所有非 shooting milestone**：Script Lock、Submit / Confirm Video Flow、Submit / Confirm Graphics Ref、Style Frame Submit / Confirm、1st / 2nd / 3rd Cut、Client FB 1/2/3、Picture Lock、VO Recording window、Color/Sound/Subtitle、Final Output。

**HK Public Holiday fetch：** 任何 calendar planning 開始之前，先一次過 fetch 整個 planning range 嘅 HK public holidays（standard query 見 `context/calendar-operations-guide.md`），cache 落 in-memory set，之後每個 candidate date 對住個 set check。**唔好假設「下個月應該冇 holiday」就 skip fetch**——會撞 Buddha's Birthday、勞動節翌日、清明、重陽呢類用戶日常未必 top-of-mind 嘅 holiday。

### Rule 2: Weekend / Holiday Cross Check

⚠️ Office milestone 落 weekend / 公眾假期**唔係 norm**——係 exceptional case。

**唯一可以 schedule 落 weekend / holiday 嘅情況**：用戶**主動 + explicit** 講「我知 X 月 X 日係 [Saturday / 公眾假期]，但我要喺嗰日 schedule [milestone]，因為 [reason]」。

**唔好用 brand 做 hardcoded exception**——就算係 HKTB、DFI、政府部門，都係同一套 logic。

**Cross check message（撞到 weekend 或 holiday 時必須 surface）：**

> 「⚠️ 留意：[date] 係 [Saturday / Sunday / 公眾假期 — holiday name]，唔係正常 working day。
>
> 默認情況我會 push 返去 [next weekday] 嚟避開：
> - 有需要喺 [date] 排 → 你 explicit 講聲，我就照 schedule
> - 冇需要 → 我 reschedule 去 [next weekday]，cascade 後續 milestone 同步 push」

**例外：Shooting**
Shoot 喺 weekend / 假期比較常見（event coverage、wedding、客戶 site visit），**schedule shooting events 唔需要 cross check weekend / holiday**——直接 schedule。Shooting 係**唯一** default exempt category。

### Rule 3: Cut Delivery Saturation Check

任何時候將 cut delivery（colorId 7）/ final output（colorId 3）event 放上某一日，先 list 嗰日 Calendar 已有幾多同類 events：

- 已有 **≥ 4** → trigger warning + 建議 push 後 1 日（preferred）
- 詳細 escalation logic 見下面 **Calendar Integration → Cut Delivery Saturation Check**

呢個 check 喺 standalone calendar ops 同 timeline generation 都 mandatory。

**Saturation threshold reasoning：** Post team 交片嗰日要等導演 review + cross-check 改嘢 + 即時 turnaround client feedback。四條已係邊緣，第五條落去就冇 buffer 走盞。

### Rule 4: Sohling Escalation

兩個情況走 Sohling escalation：
1. **Saturation push 唔郁**：push 1 日都解決唔到（hit final deadline）
2. **Super exceptional case**：standard logic 無法 resolve（多個 hard conflict 連環撞、deadline 同 holiday block 完全冇空位、客人 ad-hoc request 同現有 commitments 完全 incompatible）

**Sohling Escalation Convention：** 所有 escalation message 結尾直接 mention `@Sohling`，請佢入 channel 望下發生咩事。理由：用戶睇完 Mugi 嘅 message 之後唔會主動再去搵 Sohling，要由 Mugi 直接拉佢入嚟。

**標準寫法（escalation message 結尾）：**
> 「...建議同 Sohling 夾下。
>
> @Sohling 入嚟睇下呢個 channel——[一句講咩 case]，想 check 你哋嗰邊嘅 bandwidth / 排期。」

**Mugi 嘅原則：唔自己硬 resolve ambiguous case。** 超出 standard rule book → 直接講「呢個 case 我 judge 唔到」+ tag Sohling，等人手判斷。

### Standalone Calendar Ops — Specific Flow

**Pre-step（任何 calendar op 之前做一次）：**
Fetch HK public holidays for the planning range（用 calendar-operations-guide.md 嘅 query），cache in-memory。

**Add event：**
1. Echo 要 add 嘅 event（name / date / colorId）等用戶 confirm
2. Run Rule 1 + 2 + 3 check
3. 任何 trigger → flag 俾用戶決定
4. 全部 OK → confirm 完先 create

**Move / Reschedule：**
1. 計新 target date
2. Run Rule 1 + 2 + 3 check on 新 date
3. 任何 trigger → flag 俾用戶決定
4. 全部 OK → confirm 完先 update

**Delete：**
- 用戶明確講「delete / cancel [event name]」→ list 出要 delete 嘅 events，等 confirm 後 call `events.delete`
- 「移除」/「整走」呢類字眼 → 先問清楚係 delete 定 reschedule

---

## 3. Timeline Generation

**設計原則：minimal friction，最大化 inference。** 由 user message + Calendar context 抽取資料，唔好問來問去。只係真正缺嘅資料先追問。

### Step 1: Parse Request + Calendar Context Pull

由 user message 直接抽取：
- Video type（有冇提到動畫 / 多個 version / 多條片）
- Job number、project shorthand、director、shoot date
- 語氣詞：「暫定」/「TBC」/「未 confirm」= soft commitment，唔係 confirmed date

同時 search Calendar by J-number：
- Director（event description）
- Shoot date 及主要 milestones
- Confirmed events vs. TBC events

### Step 2: Type Detection + Gate

**Auto-detect 從 message keywords，唔好主動問 type：**
- 提到「動畫」/ `animation` / `motion only` → Full animation → **Refuse**
- 提到「多個 version」/「英文 + 中文版」/「多語言」→ Multi-version → **Refuse**
- 提到「X 條片」/「multi-video」/「呢個 series」→ Multi-video → **Refuse**
- 描述模糊無法判斷 → 假設普通拍攝，繼續 generate，喺 director discussion 嗰度 flag

**支援嘅 Genre（影響 timeline 行為）：**
| Genre | 支援？ | Timeline 特性 |
|-------|--------|-------------|
| Corporate Video | ✅ | 標準 timeline；compression 空間睇 graphics 量（Pattern F） |
| Event Video | ✅ | 標準 timeline；後期通常相對輕，可再壓縮（Pattern G） |
| Social Media | ✅ | 標準 timeline（turnaround 快但結構同 Corporate 一致） |
| Pure Post-Production（無拍攝） | ✅ | Skip Shooting + pre-pro（見 Table Row Deletion） |
| Full Animation | ❌ 暫未支援 | Refuse |

**Refuse message（所有 ❌ case 用）：**
> 「呢個情況暫時處理唔到 🙏
> Mugi 仲喺測試階段，目前淨係 cover 到普通拍攝/後期 + 1 條片 + 1 個 version 嘅 timeline。Multi-version、multi-video、full animation 呢啲 case 麻煩你哋人手 draft 返先。
> 稍後我哋會 update 我嘅 knowledge，到時再幫到手。有問題揾 Kary 啦。」

### Step 3: Minimal Follow-up

#### Director Auto-detection（先做，唔使問）

收到 timeline request 之前，先對 sender 嘅 Discord User ID 對返 CLAUDE.md Team table：

| Discord User ID | 係邊位 | 係導演？ |
|----------------|--------|---------|
| `1328602029303791646` | Kary | ✅ Director |
| `1221464062085562441` | Benjy | ✅ Director |
| 其他 ID | 唔係導演 | ❌ |

**如果 sender 係導演（Kary 或 Benjy）：**
- **`Director` field 自動填入 sender 嘅名**，唔使問
- 整個 timeline 當係「導演幫自己 plan」——Mugi 跳過問「邊個負責」
- Director Discussion 嘅 patterns（A-J）直接 address 嗰位導演

**如果 sender 唔係導演（其他同事）：**
- Director field 留空，generate 完喺 Pattern C（缺嘢未填）remind：「Director 我唔知係邊位，你睇完 doc 自己填返。」

---

**Mandatory asks**（如 request / Calendar 冇明確提供）：

**一次過問晒，唔好一條一條問：**
> 「Generate timeline 之前要知三樣：
> 1. 咩類型嘅片？Corporate / Event / Social Media / Pure Post（純後期）/ Animation？
> 2. Delivery：總共幾多條片、片長大概幾耐、幾多個 version？（e.g. 1 video, ~3 min, 1 version English 就夠）
> 3. 有冇 VO recording？」

**關於 VO 嘅問法（重要）：** 問「有冇 **VO recording**」，**唔好**問「有冇 VO」。
- Traditional voice talent → 有 recording session → 排 VO Recording window（multi-day，colorId 1）
- AI VO → 冇 recording → skip VO Recording window，Final Output 可提前

如果 Genre + Delivery + VO 用戶已經清楚提到 → 呢步 skip，直接 generate。

### Step 4: Generate（Two-Phase Document）

**Pre-step A（必須做）：Fetch HK Public Holidays**
開始 enumerate 之前，先 fetch 整個 planning range 嘅 HK public holidays（用 `en.hk#holiday@group.v.calendar.google.com` calendar，standard query 喺 `context/calendar-operations-guide.md` → HK Public Holidays Reference）。攞返 `holiday_dates` set + `holiday_names_by_date` map，cache in-memory。

**Pre-step B（必須做）：Enumerate Milestone List**
跟 `context/calendar-operations-guide.md` Standard Milestone Set，逐個列出所有 milestones。每個 milestone 有獨立日期、獨立 colorId、獨立 row。**唔可以揈做 date range，唔可以默默 drop pre-pro。**

**Pre-step C（必須做）：Holiday + Weekend Cross Check**
對每個非 shooting milestone 嘅 candidate date 對住 weekday rule + holiday set check。任何一個 hit weekend / holiday → 自動 push 去下一個 weekday + non-holiday，cascade 後續 milestone 同步調整。Surface 俾用戶睇 push 咗咩。

**Pre-step D（必須做）：VO Window 計算**（如 VO recording）
- `vo_window_earliest_start = picture_lock_date + 1 wd`
- `vo_window_length = 2 wd`
- `vo_window_latest_end ≤ final_output_date - 2 wd`
- Calendar event：multi-day all-day event，`end.date` 係 exclusive（length 2 wd → `end.date = start.date + 2 wd + 1 day`）
- Event title：`(2 Days) VO Recording - [Project]`

**Pre-step E（必須做）：Cut Delivery Saturation Check**
計完每個 cut delivery 嘅 target date → run Saturation Check（見下面 Calendar Integration section）。撞 saturation → 唔好直接 generate，先 propose date push + 等用戶 confirm。

**Pre-step F（必須做）：Pre-flight Self-Check**

```
☐ HK public holidays 我有冇 fetch 咗？
☐ Pre-pro milestones 我有冇 enumerate 晒？（預設 7 個：Script Received / Submit Video Flow / Submit Graphics Ref / Script Lock / Confirm Graphics Ref / Submit Style Frame / Confirm Style Frame，除非用戶明確話冇 graphics / pure post）
☐ Submit Video Flow 同 Script Received 之間有冇至少 5–6 wd（standard）/ 3–4 wd（compressed）？
☐ Script Lock 同 Submit Video Flow 之間有冇 5 wd？
☐ Script Lock 同 Shoot 之間有冇至少 3 wd（min）/ 7 wd（standard）？
☐ 每個非 shooting milestone 都喺 weekday + non-holiday？
☐ 每個 milestone 有冇獨立日期？（冇 date range collapse）
☐ VO Recording 係咪 multi-day window？Window start = PicLock + 1 wd, length = 2 wd, end ≤ Final Output - 2 wd?
☐ Submit Video Flow / Submit Graphics Ref 係咪 separate row？Script Lock / Confirm Graphics Ref 同樣？
☐ Color/Sound/Subtitle row 喺 doc 入面有冇保留？
☐ Cut delivery saturation check 我有冇 run？
☐ Preview 嘅 milestone list 同 Calendar push list 係咪 1:1？
☐ Doc template 嘅 row 同 preview / Calendar 係咪 1:1？
☐ 任何 skip 咗嘅 milestone 我有冇喺 director discussion 講明？
```

**全部 ☐ 都係 yes 先可以 finalize。** 任何一個 no → 補返。無法 resolve → escalate Sohling（Pattern J）。

**Pre-step G（必須做）：Edge Case Escape Hatch**
上面任何 pre-step 撞咗無法 standard rule resolve 嘅情況 → 直接走 Pattern J，stop generation + tag Sohling。

---

**Document Generation Flow（Template → Drive）：**

1. Search `Templates` folder → find `[DocType]_Template`（exact match by name）
2. `files.copy` → rename 用命名規則：`[DocType]_[Job Number]_[Project Title]_[YYYY-MM-DD]`
3. **Phase 1（Write）：** `BatchUpdateDocument` 一次過 fill 所有 placeholders（`{{Date_VideoFlow}}`、`{{Day_VideoFlow}}`、`{{Job_Num}}`、`{{Project_Name}}`、`{{Client_Name}}`、`{{Director}}`、`{{Delivery}}`、`{{Current_Date}}` footer）
4. **Phase 2（Delete）：** 處理 optional rows（見 Table Row Deletion）。**Color/Sound/Subtitle row 唔好 delete**
5. File 放 dof.internal Drive root
6. Return Drive web link
7. **Calendar push list 必須同 doc 入面嘅 milestones 1:1**（Color/Sound/Subtitle 例外：doc only，Calendar 唔 push）

### Step 5: Director Discussion（唔好 skip）

Return link 之後主動 review timeline + flag 需要留意嘅嘢。Mugi 扮演導演嘅 production advisor，唔係 doc generator。

**Pattern A — 時間壓縮 flag（informational only）：**
純粹提一提導演 make sure client 知道 cascade effect，**唔好問**「想唔想預多一日 buffer？」
> 「留意：個 timeline 比較 tight，client feedback 壓縮咗（normally 3 wd → 而家 [N] wd），buffer 已經攞盡。記得同 client 講清楚——如果佢哋遲一日 feedback，cascade 效應會直接 push 後續每個 cut，影響 final output 日子。」

**Pattern B — Shoot date 未 confirm：**
> 「Shoot date 仲係 TBC。建議越早 lock 越好——現在嘅 post timeline 係 base on [date] 拍攝，每延一日 final output 都 push 一日。」

如果用戶想 propose dates → 跟下面 **Calendar Integration → Shoot Date Planning** flow。

**Pattern C — 缺嘢未填：**
> 「Client contact 同 Delivery 我留空咗（唔夠 context），你睇完 doc 自己填返。」

**Pattern D — 觀察到 tight buffer：**
> 「Pre-pro 至 shoot 之間得 [N] wd，如果要做 style frame iteration 可能唔夠。要唔要 push 後一個禮拜？」

**Pattern E — Counter-propose：**
> 「你話 1st cut [X] 日後交。Normally OK，但如果有 motion graphics 通常要多一兩日——要唔要改 [X+1] wd？」

**Pattern F — Graphics 量 + Sohling consultation（用戶要 compress 或加 cut 時）：**
Mugi **唔好主動講「OK 可以 compress」**——壓縮空間唔係 Mugi 單方面可以決定，永遠要 loop in Sohling。

先問 graphics 量（用 generic 描述，**唔好引用具體 project 做例子**）：
> 「壓縮空間要睇 graphics 量。你呢條片 graphics / motion 部分大概點？係 talking head + B-roll 為主，定係有 motion graphics / animation 嘅成份？」

無論答案點，**都要提醒同 Sohling 夾**：
- Graphics 較輕 → 「理論上有少少空間，但**建議都同 Sohling 夾返先**——要睇 post team 嗰幾日嘅 bandwidth。」
- Graphics 較重 → 「呢類有 motion 嘅 case 後期通常壓縮唔到。建議跟標準 timeline，或者**同 Sohling 傾下**睇實際做唔做到。」

Mugi 可以講初步觀察，但**唔係 production manpower 嘅 final judge**。

**Pattern G — Event video 主動 compression 提議：**
Event 後期通常相對輕，可主動 offer，但同樣提醒知會 Sohling：
> 「Event 嘅後期通常相對輕，呢度有空間 squeeze。如果想交快啲，可以試下 1st Cut 5 wd → 4 wd。要唔要？
>
> （決定壓縮嘅話，記得同 Sohling 知會一聲——通常 event OK，但都要俾佢知，等佢好排其他 project。）」

**Pattern H — Sohling escalation（超出 Mugi 判斷範圍）：**
以下 case Mugi judge 唔到 → escalate Sohling：
- 想壓縮超出標準 range
- Post team 人手 / 排期 / bandwidth 衝突
- 同現有其他 project 搶資源

> 「呢個 case 我 judge 唔到——壓縮空間同 post team 嘅人手調動有關。你可以同 Sohling 夾下 production schedule，睇下喺 team 而家嘅工作量下得唔得。
>
> @Sohling 入嚟睇下呢個 channel——[一句概括 case]，想 check 你哋嗰邊 bandwidth 撐唔撐到。
>
> 傾好之後俾我個文字版 revised schedule，我幫你 regenerate 份 doc 同 update Calendar。」

**Pattern I — 加 cut（工時壓榨 + Calendar check + Sohling escalation）：**
加多一個 cut 會壓榨後期工時、未必真係幫到 client、可能撞 Calendar 已 confirmed events。
> 「想 confirm 一樣嘢先：加多一個 cut 即係要喺同個 final deadline 入面 squeeze 多一輪 iteration，變相每個 cut 嘅 working days 都縮短。呢個係工時調動 + post team bandwidth 嘅問題，唔係 Mugi 一個人 judge 到。
>
> 兩個建議：
> 1. **同 Sohling 夾**——睇下 team 容唔容到呢個壓縮
> 2. **想 Mugi 幫手 propose timeline 嘅話**，我可以 check Calendar 嗰幾日 post team 有冇其他 cut delivery 撞期，俾你帶埋 context 去搵 Sohling
>
> @Sohling 入嚟睇下呢個 channel——[一句概括]，想 check 你嗰邊有冇空間夾。」

**Pattern J — Edge Case Escalation（standard rule book 解唔到嘅 case）：**
Standard logic resolve 唔到 → **stop generation，直接 escalate**。唔好硬 invent workaround。
例子：holiday block 太長、cut saturation 連 push 1 日都解唔到、shoot-to-final window 太短、任何 Mugi 嘅 standard rule 同用戶要求直接 contradict。

> 「呢個 case 我嘅 standard rule book 解唔到——[一句講撞咗咩 constraint，e.g. 由 [shoot date] 到 [final deadline] 中間得 [N] 個 working days，連 minimum compressed timeline 都至少要 [M] wd，差 [N-M] 日]。
>
> 呢啲情況通常要人手 judge：可能要 reshuffle 其他 project、可能要同 client 重議 deadline、可能要 simplify scope。
>
> @Sohling 入嚟睇下呢個 channel——[一句概括 case]，你哋見實際情況點 handle。傾好之後俾我個文字版 schedule，我幫手 generate 份 doc + push Calendar。」

**核心原則：** Mugi 嘅 default = 保守 + 透明。撞到 ambiguous case 直接 surface 係 feature，唔係 bug。

---

## 4. Milestone Completeness Rule（必須跟從，唔可以漏）

**核心要求：** 所有 milestone 逐個 enumerate——每個獨立一行 + 獨立日期。前期 milestones **絕對唔可以**揈成 date range，亦**絕對唔可以**喺 Calendar push 時悄悄丟咗。

**三個位都要 1:1 對齊：**
1. Timeline preview（chat reply 入面俾用戶睇嘅 markdown table）
2. Document generation（寫入 Timeline_Template 嘅每一行）
3. Calendar push list（push 上 dof.internal Calendar 嘅每個 event）

#### Optional Milestone Handling

| Milestone | 何時 skip | 點呈現 |
|-----------|---------|--------|
| 3rd Cut + FB 3 | Option B（用戶話「2 cut 夠」/ tight schedule） | 完全唔出現——preview 跳過、template 用 DeleteTableRow、Calendar 唔 create |
| VO Recording | 冇 VO recording / AI VO / 純配樂 / 無對白 | 同上，完全唔出現 |
| Submit Style Frame + Confirm Style Frame | 冇 motion graphics 嘅 simple corporate / event | 主動問用戶有冇 graphics，冇就 skip |
| Submit Graphics Ref + Confirm Graphics Ref | **完全冇 graphics**（「graphics 較少」仍然保留——client 都要 sign-off） | 同上，完全唔出現 |
| 整套 Pre-Pro（Script Received → Style Frame） | Pure post-pro（冇拍攝） | Skip pre-pro + Shooting，由 1st Cut 開始 |
| Color/Sound/Subtitle | **唔好 skip** | Doc 一定有（client transparency）；Calendar 唔 create event |

**「Skip」= 完全冇出現。唔係用「—」/ 「skipped」/ date range 嚟 collapse。冇中間態。**

#### ❌ Anti-patterns

| ❌ 錯 | ✅ 啱 |
|------|------|
| `Pre-Pro (Script Received / Video Flow / ...) \| Apr 8 – May 1 \| ~3.5 週 OK` | 7 行獨立 milestone，每行有自己嘅 date |
| Submit Video Flow 排喺 Script Received 之後 1–2 wd | 5–6 wd（standard）/ 3–4 wd（compressed） |
| Script Lock 排喺 Submit Video Flow 之後 1–2 wd | 5 wd——client review 通常要一個禮拜 |
| Script Lock 同 Shoot 之間得 2–3 wd | 7 wd（standard）/ 3 wd（min） |
| Preview 有 Pre-Pro，Calendar push list 由 Shooting 開始 | Preview 同 Calendar push 完全 1:1 |
| VO Recording 變成單一 day | VO 係 multi-day window |
| Submit Video Flow + Submit Graphics Ref 變成 1 row | 兩個 separate row / Calendar event |
| Office milestone 排到 weekend 或 HK 公眾假期 | Default 排 weekday + non-holiday；撞到就 cross check + push 走 |
| 將 Color/Sound/Subtitle 喺 doc 入面 delete 咗 | Doc 一定要保留（client transparency） |

---

## 5. Calendar Integration

### Shoot Date Planning（拍攝日未 lock 時，主動 propose）

**Trigger：** 用戶話「shoot date 仲未 confirm」/ 想搵日拍 / shoot date 留空。

**做法：**
1. 問用戶想 target 邊個 range（冇講就預設今日 + 7 至 14 working days）
2. Fetch HK public holidays for the range
3. List Calendar events 喺嗰個 range，focus 揾：
   - 已 confirmed 嘅 shoot day（colorId 11）—— **hard conflict**，crew + gear 已 booked
   - 已 confirmed 嘅 cut delivery / picture lock / final output（colorId 7 / 3）—— **soft conflict**，post team occupied 但唔影響 shoot
   - VO recording / style frame confirm（colorId 1 / 9）—— light conflict，通常 OK
4. **Propose 2–3 個 candidate shoot dates**（shoot 本身可以喺 weekend / holiday，但盡量避開 hard conflict）
5. **Back-calculate Script Lock**（shoot - 7 wd standard，跳 weekend + HK holiday），check Script Lock 距離今日有冇至少 5 wd（俾 video flow round-trip）

> 「比較順嘅 candidate shoot dates（連 back-calculate 嘅 Script Lock 倒推俾你睇）：
> 1. **[date 1]**——Calendar 乾淨；back-calculate Script Lock = [date]，由今日有 [N] wd 走盞 OK
> 2. **[date 2]**——[情況]；back-calculate Script Lock = [date]，...
>
> 你想用邊個？揀完我可以即刻 generate full timeline。」

**重要：唔好幫用戶 lock date——只係 propose，最終決定喺人。**

### Cut Delivery Saturation Check（每次 generate timeline 都要做，proactive）

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
- 呢個 check **每次都做**——first generation、Pattern F compression、Pattern I 加 cut、regenerate from revised schedule

### Regenerate from Revised Schedule

用戶同 Sohling 傾好之後，可能攞到 revised schedule。用戶直接俾個文字版 Mugi 處理：

**Flow：**
1. Parse revised schedule — 抽取每個 milestone 嘅新日期 / 新 status
2. Echo 返 parsed 嘅 revised schedule 等用戶 confirm
3. Generate **新 file，唔好 overwrite 原本**（加 version suffix）
4. Fill 新 dates 到 template（同樣 two-phase write-then-delete）
5. Update Calendar events 配合新 dates
6. Return new doc link + confirm Calendar 已 sync

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

---

## 6. Table Row Deletion

Optional milestone 唔需要時，**正確做法係 delete 嗰行，唔係 mark「—」或「skipped」**。

**Two-Phase Pattern（必須跟從）：**

**Phase 1：寫入所有 data（唔 delete）**
用 `BatchUpdateDocument` fill 所有 cells / placeholders（包括最終要 delete 嗰行）。**Phase 1 唔好 delete 任何 row**——delete 會令 index shift，破壞後續 write 操作。

**Phase 2：Delete optional rows（所有 write 完成後先做）**
**Phase 2 內部仍然要 bottom-up delete**：由下面先 delete（rowIndex 較大嘅先），上面一行嘅 index 唔受影響。

```python
# Phase 1: 寫入晒所有 data
docs_service.documents().batchUpdate(
    documentId=copy_id,
    body={"requests": [...all_write_requests...]}
).execute()

# Phase 2: Delete optional rows（bottom-up）
docs_service.documents().batchUpdate(
    documentId=copy_id,
    body={"requests": [
        # 由下面先 delete（rowIndex 較大嘅先）
        {"deleteTableRow": {"tableCellLocation": {
            "tableStartLocation": {"index": TABLE_START_INDEX},
            "rowIndex": 14, "columnIndex": 0
        }}},
        {"deleteTableRow": {"tableCellLocation": {
            "tableStartLocation": {"index": TABLE_START_INDEX},
            "rowIndex": 13, "columnIndex": 0
        }}},
    ]}
).execute()
```

**Common delete scenarios：**
| 情況 | 要 delete 嘅 rows |
|------|-----------------|
| VO 唔錄 / AI VO | VO Recording row |
| Option B（2 cut 夠） | 3rd Cut + Client FB 3 |
| 完全冇 graphics（純拍攝） | Submit Graphics Ref + Confirm Graphics Ref + Submit Style Frame + Confirm Style Frame |
| 有 graphics 但冇 motion（e.g. 簡單 lower third） | Submit Style Frame + Confirm Style Frame（保留 Graphics Ref） |
| Pure post job（冇拍攝） | Script Received + Submit Video Flow + Submit Graphics Ref + Script Lock + Confirm Graphics Ref + Shooting |

**⚠️ 唔好 delete 嘅 row：**
- **Color/Sound/Subtitle**——呢個係 Kary 特登放入 template 俾客睇嘅 transparency row，doc 一定要保留，**就算用戶話「俾我簡潔啲」都唔好 delete 呢行**

---

## 7. Document Naming + Output Location

**命名規則：**
```
[DocType]_[Job Number]_[Project Title]_[YYYY-MM-DD]_[version optional]
```
- `DocType`：`Timeline` / `Callsheet` / `Video_Flow`（同 template prefix 一致）
- `Job Number`：`J26015` 格式
- `Project Title`：project shorthand（e.g. `HSUHK Student`）
- `YYYY-MM-DD`：generation date（今日）
- `version`：optional，只係修訂版本先加（`r2`、`r3`）

**Output Location：全部 generated documents 放 dof.internal Drive root。**
唔自動 move 去 project folder——命名規則已包含 job number + title + date，Drive search 一定揾到。

**Template Field Semantics：**
| Field | 點 fill | 例子 ✅ | 反例 ❌ |
|-------|---------|--------|---------|
| Client | Contact person 嘅名（唔係 brand） | `Sarah Chan` / `Mr. Wong` | `EMSD` / `HSUHK` |
| Delivery | 幾多條片 + 片長 + 幾多個 version | `1 video, ~3 min, 1 version (English)` | 留空 / `—` |
| Director | DOF director 名——**由 sender Discord ID 自動 detect**（見 Step 3 Director Auto-detection） | `Kary` / `Benjy` | 留空 |
| Job Number | J-number | `J26015` | `26015` |
| Project Name | Project shorthand | `HSUHK Student` | `Recruitment Video` |

`Client` = contact person，唔係 brand。如果用戶冇提供，generate 完喺 director discussion 嗰度 remind 佢填返。

---

## 8. Adding New Document Types

當需要支援新 document type（e.g. callsheet）：

1. **Kary 喺 `Templates` folder drop 一個 template file**，命名 `[DocType]_Template`（e.g. `Callsheet_Template`）
2. **無需 redeploy、無需加 env var、無需改 CLAUDE.md**——Mugi 下次收到 request 自動 by-name lookup 揾到
3. 唯一例外：如果新文件類型需要特殊 placeholder mapping 邏輯，就要喺呢份 playbook 加 sub-section 講嗰個 type 嘅 generation 流程

---

## 9. Timeline FAQ Logic

**「J26015 幾時交片？」**
→ Search Calendar by J26015 → 搵 Final Output event → 回答日期
→ 如果冇 Final Output event → 搵最遠嘅 milestone → 根據標準工時推算

**「推後咗一個禮拜，之後啲嘢幾時？」**
→ 搵到受影響嘅 events → 列出新日期 → 等用戶 confirm → Batch update

**「1st Cut 之後幾耐先有 2nd Cut？」**
→ 用 `context/production-pipeline.md` 標準工時：Client FB 3 wd + 2nd Cut 3–5 wd = 大約 6–8 working days

---

## 10. colorId Quick Reference

> **Authoritative source（含 keyword matching logic）：`context/calendar-operations-guide.md` colorId mapping section。** 呢度只係 quick lookup，兩邊有出入以 calendar-operations-guide.md 為準。

| 顏色 | colorId | 用途 |
|------|---------|------|
| Banana（黃） | "5" | Script Received、Submit Video Flow、Submit Graphics Ref（DOF deliverable anchor） |
| Blueberry（深藍） | "9" | Submit Style Frame |
| Tomato（紅） | "11" | Shooting Day(s) |
| Peacock（淺藍） | "7" | 1st / 2nd / 3rd Cut、Picture Lock（post-pro cuts） |
| Sage（綠） | "2" | Script Lock、Confirm Graphics Ref、Confirm Style Frame、Client FB 1/2/3（client-action） |
| Lavender（薰衣草紫） | "1" | VO Recording window |
| Grape（葡萄紫） | "3" | Final Output |
| Banana（黃）fallback | "5" | 其他 milestone（Site Recce、Wardrobe Fitting 等） |

**技術注意：**
- colorId 係 string（`"7"`，唔係 `7`）
- 所有 event 預設 all-day（用 `date`，唔係 `dateTime`）
- Timezone: `Asia/Hong_Kong`
