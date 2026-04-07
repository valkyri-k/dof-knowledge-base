# Calendar Operations Guide（Mugi 操作手冊）

呢份係 Mugi 操作 Google Calendar 嘅完整 reference。所有 Calendar 操作都要跟呢度嘅規則。

**呢個 file 亦同時係 Standard Milestone Set 嘅 single source of truth。** CLAUDE.md 嘅 Document Generation → Milestone Completeness Rule section reference 呢度，唔好喺兩個地方分別維護 milestone list。

---

## 基本設定

- **DOF Internal Calendar ID:** `dof.internal@gmail.com`
- **HK Public Holidays Calendar ID:** `en.hk#holiday@group.v.calendar.google.com`（public，SA 直接 query 到，唔需要任何 sharing setup）
- **認證方式:** Service Account（環境變數 `GOOGLE_CALENDAR_CREDENTIALS`）
- **操作庫:** `google-api-python-client` + `google-auth`

---

## HK Public Holidays Reference

### 點 query

每次 Mugi plan timeline 或者 schedule 任何非 shooting milestone 之前，都必須 check HK public holidays，確保 office 性質嘅 milestone 唔會排到假期。Google 提供咗 public HK holiday calendar，service account 直接就可以 list events，唔需要任何 sharing setup。

```python
# Fetch HK public holidays for the planning range
holidays_resp = service.events().list(
    calendarId='en.hk#holiday@group.v.calendar.google.com',
    timeMin=range_start.isoformat() + 'T00:00:00Z',
    timeMax=range_end.isoformat() + 'T00:00:00Z',
    singleEvents=True,
    orderBy='startTime'
).execute()

holiday_dates = {
    e['start']['date']  # YYYY-MM-DD format
    for e in holidays_resp.get('items', [])
    if 'date' in e.get('start', {})
}

holiday_names_by_date = {
    e['start']['date']: e.get('summary', 'Public Holiday')
    for e in holidays_resp.get('items', [])
    if 'date' in e.get('start', {})
}
```

### 點 apply

對每個將要 schedule 嘅 milestone date，check：

1. 係咪 Saturday / Sunday？
2. 係咪喺 `holiday_dates` set 入面？

任一答 yes → trigger Working Day Cross Check（見下面）。

### Cache strategy

**同一個 Mugi conversation 入面，個 timeline session 共用同一個 `holiday_dates` set——唔好對每個 milestone 重新 fetch。** Mugi 喺 timeline planning 開頭一次過 fetch 整個 planning range（通常今日 → 今日 + 60 wd），cache 落 working memory 用到 planning session 完。

### 如果 fetch 失敗

Google holiday calendar 係 public 嘅，正常情況冇理由 fail，但如果真係 fetch 唔到（network / API error），Mugi 要**明顯 surface 俾用戶知**：

> 「⚠️ 我 fetch HK public holiday calendar 嗰陣 fail 咗 — 我會繼續 plan timeline，但**請你自己 double check 有冇 milestone 撞到 public holiday**。HK public holiday 通常包括：農曆新年、清明、復活節、勞動節、佛誕、端午、七一、中秋、國慶、重陽、聖誕。」

---

## Working Day Cross Check（非 shooting milestone 必須跟）

### 核心 Rule

**所有非 shooting milestone 必須喺 working day（Mon–Fri 而且唔係 HK public holiday）。** 只有用戶 explicit override 先例外。

| Milestone 類別 | Working day required? |
|----------------|----------------------|
| Pre-Pro DOF deliverable（Submit Video Flow、Submit Graphics Reference、Submit Style Frame）| ✅ |
| Client review milestone（Script Lock、Confirm Graphics Reference、Confirm Style Frame、Client FB 1/2/3）| ✅ |
| Post-Pro cuts（1st Cut、2nd Cut、3rd Cut、Picture Lock）| ✅ |
| VO Recording（window 入面每一日）| ✅ |
| Color / Sound Mixing / Subtitle | ✅ |
| Final Output | ✅ |
| Script Received（T0 anchor）| ✅ |
| **Shooting** | ❌ **Exempt**——shoot 喺 weekend / holiday 比較常見（event coverage、客戶 site visit、wedding 等），Mugi 唔需要 cross check shooting events |

### Cross Check 觸發時嘅做法

**Default behavior：** Mugi schedule milestone 落 weekend / holiday → 唔好默默接受，要即時 surface 俾用戶決定。

**Cross check message 模板：**

> 「⚠️ 留意：**[milestone name]** 嘅 **[date]** 係 **[Saturday / Sunday / 公眾假期 ([holiday name], e.g. 勞動節)]**，唔係正常 working day。
>
> 建議 push 去 **[next working day]**——咁個 timeline 仲係 align 標準工時。
>
> 除非你哋同 client 已經有共識嗰日要交嘢（例如客人 explicit 噉要 weekend / holiday delivery），先至 schedule 落去。
>
> 你想：
> - 跟建議嘅 [next working day]
> - 你已經 confirm 同 client 對齊 → 照 [date]」

### ❌ 絕對唔好寫死 brand exception

**唔好**假設「呢個 client / 呢個 brand 通常要 weekend」。即使曾經喺 HKTB 或 DFI 嘅 project 上面出現過 weekend / holiday delivery，都唔係呢類 client 嘅 norm——嗰啲係 exceptional case。**每次都要逐個 case 由用戶 explicit override。**

### 例外：用戶 explicit override

唯一可以 schedule 非 shooting milestone 落 weekend / holiday 嘅情況係用戶喺 chat 入面 **explicit 講明** client 真係要嗰日交嘢。Mugi 唔可以自己幫用戶假設。

---

## Event 命名規則（必須跟從）

### Title 格式

**Single-day milestone：**

```
[Milestone] - [Project Shorthand]
```

**Range / multi-day milestone（Shooting + VO Recording window）：**

```
([N] Days) [Milestone] - [Project Shorthand]
```

### 例子

| Type | Title | colorId |
|------|-------|---------|
| Single-day cut delivery | `1st Cut - HSUHK Student` | 7 |
| Range shooting（single day）| `(1 Day) Shooting - HSUHK Student` | 11 |
| Range shooting（multi day）| `(2 Days) Shooting - HSUHK Student` | 11 |
| Range VO recording | `(2 Days) VO Recording - HSUHK Student` | 1 |
| Style frame submit | `Submit Style Frame - HSUHK Student` | 9 |
| Script Lock | `Script Lock - HSUHK Student` | 2 |

**Shooting note：** 現有 Calendar 入面有啲 shoot event 用咗 `(N Days) - [Project]` 省略 `Shooting` milestone name。呢個 legacy convention 可以繼續用，但**新建 shoot event 建議用 `(N Days) Shooting - [Project]` 完整 format**，一致性較好。

**VO Recording note：** Window event **必須保留 milestone name**——即係 `(2 Days) VO Recording - [Project]`，**唔可以**省略成 `(2 Days) - [Project]`。否則 Calendar 滿哂 events 嘅時候用戶分唔到邊個係 shoot、邊個係 VO window。

### Description 格式

```
J26016
Director: Kary
[其他備註，如有]
```

- Job number 放 Description **第一行**（Google Calendar search 可以搵到 description 內容）
- Director 姓名放第二行
- Range event（Shooting / VO Window）第三行可以加 reasoning：

  ```
  J26016
  Director: Kary
  VO window: talent + studio booking 預兩日 buffer
  ```

### Special title override

| Milestone | Title | Description |
|-----------|-------|-------------|
| Script Lock（= Confirm Video Flow）| `Script Lock - [Project]` | `J26XXX\nDirector: [name]\n= Confirm Video Flow. Script 至少 90% firm。` |

**點解用 Script Lock 做 title：** 對導演同 client 都係最 actionable 嘅 framing（「你 script 鎖住未？」），而「Confirm Video Flow」比較 internal jargon。兩個概念係同一回事——一個 milestone，雙重意義。

### 命名原則

- **唔把 Job Number 放 title** — Calendar view 格太細，J-number 壓住有用資訊
- **Milestone 名稱必須用標準 set**（見下方 Standard Milestone Set），唔接受自由發揮
- **Project Shorthand 跟開 job 時定好嘅版本** — 唔好自己作

---

## Standard Milestone Set（single source of truth）

呢個係**完整 timeline 入面所有 milestones 嘅 canonical list**。Mugi 生成 timeline 時逐個 enumerate，唔可以揈做 date range，唔可以 silent 噉漏 push 邊個。

### Pre-Production

每個都係**獨立 row + 獨立 calendar event**，即使有啲 default 同一日 schedule（Submit Video Flow + Submit Graphics Ref；Script Lock + Confirm Graphics Ref）。

| # | Milestone | Calendar Title | Party | colorId | 由 previous milestone 算起 |
|---|-----------|---------------|-------|---------|---------------------------|
| 1 | Script Received | `Script Received - [Project]` | Client | 5 (Banana) | T0 anchor — client share script / materials 嘅日子 |
| 2 | Submit Video Flow | `Submit Video Flow - [Project]` | DOF | 5 (Banana) | **+5–6 wd from #1**（standard）/ +3–4 wd（compressed） |
| 3 | Submit Graphics Reference | `Submit Graphics Ref - [Project]` | DOF | 5 (Banana) | **Same day as #2**（default） |
| 4 | Script Lock | `Script Lock - [Project]` | Client | 2 (Sage) | **+5 wd from #2**（client review，可能涉及 senior approval）/ +3 wd min |
| 5 | Confirm Graphics Reference | `Confirm Graphics Ref - [Project]` | Client | 2 (Sage) | **Same day as #4**（default）/ 可以 propose 提早 |
| 6 | Submit Style Frame | `Submit Style Frame - [Project]` | DOF | 9 (Blueberry) | **+2–3 wd from #5** / +1 wd min — **only if project 有 style frame chain** |
| 7 | Confirm Style Frame | `Confirm Style Frame - [Project]` | Client | 2 (Sage) | **+1–2 wd from #6** / +1 wd min — same condition as #6 |

### Shooting

| # | Milestone | Calendar Title | Party | colorId | Notes |
|---|-----------|---------------|-------|---------|-------|
| 8 | Shooting | `([N] Days) Shooting - [Project]` | Both | 11 (Tomato) | Multi-day shoot 用一個 multi-day all-day event（唔好 split 做多個 single-day event）。Working Day Cross Check **exempt**。 |

**Pre-Pro → Shoot 最關鍵 dependency：**

**Shoot date − Script Lock (#4) = standard 7 wd / minimum 3 wd** — 即 Script Lock 同 Shoot 之間必須至少有 3 個 working day，standard 係 7 wd（預 props、location confirm、crew briefing、shotlist finalize 等 prep 工序）。

Mugi plan timeline 時通常由 shoot date **back-calculate** pre-pro chain：

```
Shoot date
  ↓ -7 wd standard / -3 wd min
Script Lock (#4)
  ↓ -5 wd standard / -3 wd min
Submit Video Flow (#2)
  ↓ -5~6 wd standard / -3~4 wd min
Script Received (#1, T0)
```

Standard pre-pro total：T0 → Shoot ≈ **17–18 wd (~3.5 週)**
Compressed pre-pro total：T0 → Shoot ≈ **9–10 wd (~2 週)**

### Post-Production

| # | Milestone | Calendar Title | Party | colorId | 由 previous 算起 |
|---|-----------|---------------|-------|---------|----------------|
| 9 | Submit 1st Cut | `1st Cut - [Project]` | DOF | 7 (Peacock) | **Shoot + 5 wd** / +4 wd min |
| 10 | Feedback on 1st Cut | `Client FB 1 - [Project]` | Client | 2 (Sage) | **#9 + 3 wd** / +1 wd min |
| 11 | Submit 2nd Cut | `2nd Cut - [Project]` | DOF | 7 (Peacock) | **#10 + 3–5 wd** / +3 wd min |
| 12 | Feedback on 2nd Cut | `Client FB 2 - [Project]` | Client | 2 (Sage) | **#11 + 3 wd** / +1 wd min |
| 13 | Submit 3rd Cut（optional）| `3rd Cut - [Project]` | DOF | 7 (Peacock) | **#12 + 3 wd** / +2 wd min |
| 14 | Feedback on 3rd Cut（optional）| `Client FB 3 - [Project]` | Client | 2 (Sage) | **#13 + 3 wd** / +1 wd min |
| 15 | Picture Lock | `Picture Lock - [Project]` | Both | 7 (Peacock) | #14 approve（or #12 if Option B skip 咗 #13/#14） |

### Delivery

| # | Milestone | Calendar Title | Party | colorId | 點計 |
|---|-----------|---------------|-------|---------|------|
| 16 | VO Recording (window) | `([N] Days) VO Recording - [Project]` | DOF | 1 (Lavender) | **Window**：開始 = #15 + 1 wd；長度 = 2 wd standard；結束 ≤ #18 - 2 wd。**Optional**——冇 VO recording / 用 AI VO 就 skip 整個 row |
| 17 | Color, Sound Mixing, Subtitle | `Color/Sound/Subtitle - [Project]` | DOF | 7 (Peacock) | **#16 window 結束之後 +1 wd**（如冇 VO 就 #15 + 1 wd） |
| 18 | Final Output | `Final Output - [Project]` | DOF | 3 (Grape) | **#17 + 1 wd** |

### VO Recording Window 詳細 logic

**VO recording 唔可以單日 schedule。** 同 shooting 一樣需要 talent + studio coordination，要預 window 俾 fallback。

| Field | Logic |
|-------|-------|
| **Window 開始** | Picture Lock + 1 wd（Picture Lock 翌日已經可以錄） |
| **Window 長度** | 2 wd（standard） |
| **Latest end** | Final Output - 2 wd（要時間 mix VO 入 final） |
| **Working day cross check** | Window 入面每一日都唔可以撞 weekend / public holiday。任一日撞 → shift 整個 window 後（preferred）；後面頂唔順 → shift 前；都唔得 → @Sohling escalate |
| **Preview + doc display 格式** | Date column: `May 21–22`；Day column: `Thu–Fri` |
| **Calendar push** | **一個 multi-day all-day event**（`start.date` = window 第一日，`end.date` = window 最後一日 + 1，因為 end 係 exclusive），colorId `1`，title `([N] Days) VO Recording - [Project]` |

### Color / Sound Mixing / Subtitle row（必須保留）

呢個 row 係 **client-facing transparency**——Kary 特登加入 template 嘅，原因係 client 有時會誤以為錄完 VO 就即刻有 final video。喺 timeline doc 入面顯示呢個 row 令 client 知道 final output 之前仲有 polish 工序。

| 特性 | 決定 |
|------|------|
| 係咪保留 | **係**——唔好 skip，即使只係 1 wd |
| Party column | DOF |
| 日子點計 | VO Window 結束之後 1 wd（如冇 VO 就 Picture Lock 之後 1 wd） |
| Calendar push? | 係（colorId 7 Peacock，當 Post-Pro） |
| Calendar title | `Color/Sound/Subtitle - [Project]` |

---

## Pre-Pro Chain Logic（reasoning）

呢個 chain 嘅 reasoning，方便 Mugi explain 俾用戶聽**點解某個 milestone 排嗰日**：

```
T0: Script Received（client share script / materials）
    ↓ DOF +5–6 wd（write Video Flow + 揀 Graphics Reference 並行）
[Same day]: Submit Video Flow + Submit Graphics Ref
    ↓ Client +5 wd（review，可能涉及 senior approval）
[Same day]: Script Lock (= Confirm Video Flow) + Confirm Graphics Ref
    ↓ DOF prep +7 wd standard / 3 wd min
[Optional, if has graphics chain]: Submit Style Frame → Confirm Style Frame
    ↓
Shoot
```

### 每個 step 嘅 rationale

- **Script Received → Submit Video Flow（5–6 wd）：** DOF 需要時間將 script breakdown 成 visual treatment + graphic reference。1–2 wd 太緊，因為 director 要諗 visual approach 同搵 reference。Compressed range 可以收縮到 3–4 wd 但唔建議。
- **Submit Video Flow → Script Lock（5 wd）：** Client 通常要做 internal review，可能涉及 senior approval。預鬆少少避免成個 timeline 喺呢度 stuck。Compressed min 3 wd。
- **Script Lock → Shoot（7 wd standard / 3 wd min）：** Pre-pro 準備時間——props、location confirm、crew briefing、shotlist finalize。如果 client 趕時間可以壓縮到 3 wd，但會影響 prep quality。
- **Graphics Reference 同 Video Flow bundle 一齊：** Default 同日 submit + 同日 confirm，因為費事 client 分開 approve 兩件事，亦顯得 unprofessional。但 **Calendar 入面係獨立 events**——後期同事（Keith、Max、Kay）需要知道 Reference 嘅 status，可能會搵 director 傾。如果 Script Lock → Shoot fall back 到 minimum 3 wd 嘅情況，Mugi 可以 propose **unbundle Confirm Graphics Reference 提早一日**，等 Style Frame chain 趕得切 shoot date。

### Script Lock 嘅 semantics

Script Lock = Confirm Video Flow：**同一回事，一個 milestone**。喺 Calendar 同 timeline doc 入面用 `Script Lock` framing。核心意義：

- Script 至少 **90% firm**——允許 client 之後「飛紙仔」，但通常只係加一句或微調，唔會影響整體 structure
- 定咗 script 後續 pre-pro 工序（props、location、shotlist）先有意義
- 呢個時間點亦 mark 咗 Video Flow document 嘅 final confirmation

### ❌ Pre-Pro Anti-patterns

| ❌ 錯 | ✅ 啱 |
|------|------|
| Submit Video Flow & Graphics Ref bundle 成一行（doc / calendar） | 兩個 separate rows + 兩個 separate calendar events（default 同日） |
| Confirm Video Flow & Graphics Ref bundle 成一行 | 兩個 separate rows + 兩個 separate calendar events（default 同日） |
| Script Lock 同 Confirm Video Flow 寫做兩個 milestone | 兩個係同一回事，title 統一用 `Script Lock - [Project]` |
| Script → Video Flow 預 1–2 wd | 預 5–6 wd（DOF 寫 Video Flow 真係需要時間） |
| Video Flow → Confirm 預 1–2 wd | 預 5 wd（client review 真係需要時間） |
| 漏 push pre-pro 上 Calendar，淨係 push shoot + post | 全部 pre-pro 都要逐個 push 上 Calendar |

---

## Optional Milestone Handling

呢套規則決定 Standard Milestone Set 入面邊啲 row 喺 specific project 入面 keep / skip。

| Milestone | 時候 skip | 點呈現 |
|-----------|---------|--------|
| **Submit Style Frame + Confirm Style Frame**（#6, #7） | 純拍攝、冇 motion graphics 嘅 simple corporate / event / 純粹拍攝冇後期 graphics | 完全 skip 兩行 |
| **Submit Graphics Reference + Confirm Graphics Reference**（#3, #5） | 冇 graphics reference 嘅 case（通常連 Style Frame 都 skip） | 完全 skip 兩行 |
| **3rd Cut + Client FB 3**（#13, #14） | 用戶話「2 cut 夠」/ tight schedule | 完全 skip 兩行 |
| **VO Recording window**（#16） | 用戶答冇 VO recording / 用 **AI VO** / 純配樂 / 無對白 | 完全 skip 一行 |
| **All Pre-pro + Shooting**（#1–8）| Pure post-pro genre（冇拍攝） | Skip pre-pro + shooting；post-pro 保留（Style Frame 如果係 post-pro 工序都保留） |

### 「Skip」嘅意思

**完全冇出現**——唔係用「—」/「skipped」/ 大 range 嚟 collapse。要嘛逐個 enumerate，要嘛完全消失。**冇中間態。**

### 純拍攝 special case（唔 generate timeline doc）

如果 project 純粹係**拍攝、冇任何 post 工序、冇 graphics、冇 cut delivery**——例如客戶要 footage rushes、event coverage raw deliverable——**Mugi 唔需要 generate timeline document**。淨係 mark 一個 shooting event 落 calendar 就完。

Mugi 嘅 reply：

> 「呢個 case 純粹係 shoot day，冇 cut delivery / post 工序，唔需要 generate timeline document。我直接幫你 mark `([N] Days) Shooting - [Project]` 落 Calendar 就得。OK 嗎？」

### Edge Case Escalation（Mugi 處理唔到就 @Sohling）

**任何 Mugi 處理唔到嘅複雜或 ambiguous case → 直接 escalate Sohling，唔好硬撐。** Mugi 仲喺 testing 階段，多 edge case / project-specific exception 未 cover 到。與其 hallucinate 一個錯嘅 timeline 令同事後期要 reverse engineer，不如直接交番俾人手。

**Escalate scenarios：**

- Multi-video project（一個 J-number 多條片，Timing 相互 dependency）
- Multi-version delivery（中文 + 英文 + 廣東話 + 不同 cut）
- 後期工序中嘅 unusual deliverable（Mugi knowledge base 未有嘅 milestone）
- Pre-pro chain 撞到 project-specific exception（e.g. client 堅持要某啲 unusual order）
- User 嘅 timing constraint Mugi calculate 唔出 feasible solution（e.g. shoot date 逼到 pre-pro 得 2 wd）
- Standard schedule 撞 saturation 而 push 前後都解決唔到
- 任何 Mugi 內心 uncertainty 都 trigger escalation

**Escalation message（標準 template）：**

> 「呢個 case 我 plan 唔到/唔肯定點 schedule——情況比較複雜，我未必有完整 picture。
>
> 不如等 Sohling 入嚟睇下：**@Sohling**，[一句概括 case，e.g. J26015 想 2 星期內出片，但 Script 仲未收到]，想 check 你哋會點 schedule。
>
> 傾好之後你可以直接俾個文字版 schedule 我（e.g.『Script May 1、Shoot May 10、Final May 24』），我幫你 generate doc + push Calendar。」

**核心原則：** Mugi 嘅價值喺於將 standard case 做得快，**唔係喺於處理所有 edge case**。處理唔到就交番去人手——好過 plan 錯嘢。

---

## Cut Delivery Saturation Check

**完整 logic + threshold reasoning + escalation case 見 CLAUDE.md → Document Generation → Calendar Integration → Cut Delivery Saturation Check section。** 呢個 rule 嘅 source of truth 喺 CLAUDE.md，因為 logic 同 director discussion patterns 緊密 coupled。

**簡單 summary：**

- **Threshold：** 一日 ≥ 4 條同類 events（cut delivery colorId 7 + final output colorId 3）→ saturated
- Mugi finalize timeline 之前 **mandatory check** 每個 cut delivery date
- Push 後 1 日係 preferred resolution；頂到 hard deadline → `@Sohling` escalate
- 呢個 check **一樣 apply 喺 standalone calendar ops**（用戶手動 add / move event），唔淨係 generation 先做

---

## colorId Mapping

建立或修改 Calendar event 時，必須根據 milestone 類別設定正確嘅 `colorId`。呢套顏色同 Doji Timeline 同 DOF Planner 完全一致。

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

### 判斷關鍵詞
- 「拍攝」「shoot」「shooting」→ colorId: `11`
- 「1st cut」「2nd cut」「3rd cut」「picture lock」「color grading」「sound mix」「subtitle」→ colorId: `7`
- 「script lock」「confirm video flow」「confirm graphics ref」「confirm style」「client feedback」「FB1」「FB2」「FB3」→ colorId: `2`（client 做嘅嘢）
- 「style frame」「submit style」→ colorId: `9`
- 「final output」「交片」「出片」→ colorId: `3`
- 「VO」「配音」「voice over」→ colorId: `1`
- 「script received」「video flow」「graphics ref」「graphics reference」→ colorId: `5`

### 技術注意
- colorId 係 **string**（`"7"`，唔係 `7`）
- 所有 single-day event 預設 **all-day**（用 `date`，唔係 `dateTime`）
- Range event（Shooting / VO Window）：**multi-day all-day event**，`start.date` = 第一日，`end.date` = 最後一日 + 1（API end 係 exclusive）
- Timezone: `Asia/Hong_Kong`

---

## 支援操作

### Search（搜尋 events）
- **By Job Number：** Search description field for `J26XXX`
- **By Date Range：** `timeMin` / `timeMax` filter
- **By Project Shorthand：** Search summary（title）field
- **組合：** 先用 date range 收窄，再 filter by keyword

**搵唔到 event 時：**
1. 試用 Job Number search description
2. 試用 Project Shorthand search summary
3. 如果都搵唔到 → 問用戶確認 project 名稱 / job number
4. 有可能係冇人入過 Calendar → 告知用戶「呢個 project 喺 Calendar 未有 events」

### Update（修改 event）
- 改日期 / 時間
- 改 title（e.g. 修正 milestone 名稱）
- 改 description
- 移除 TBC 標記
- **Update 後嘅 new date 必須 run Working Day Cross Check**（如果係 non-shooting milestone）

### Batch Update（批量更新）
- 一次過將某個 job 嘅所有 milestones 推遲 / 提前 N 日
- **做法：** Search by Job Number → get all events → update each event
- **確認流程：** List 出會影響嘅 events 俾用戶確認 → 用戶 confirm 後先執行
- **Batch update 後**：對每個 new date run Working Day Cross Check + Cut Delivery Saturation Check

### Add（新增 event）
- 建新 milestone event
- 必須跟 naming convention
- 必須設 colorId
- 加 description（Job Number + Director）
- **必須 run Working Day Cross Check + Saturation Check** before create（見 CLAUDE.md → Calendar Event Modification Rules → Universal）

### Remove TBC
- TBC event 喺 title 會有 `(TBC)` 標記
- 日期確認後 → remove `(TBC)` + 更新日期
- **Update 後嘅 confirmed date 要 run Working Day Cross Check**

---

## TBC Events

未確定日期嘅 milestone 可以先放 TBC（大概日期），title 加 `(TBC)`：

```
1st Cut - HSUHK Student (TBC)
```

當日期確認後：
1. Remove `(TBC)` from title
2. Update 到正確日期
3. Cross check working day（if non-shooting）

---

## 操作原則

### 1. 先確認再執行
任何 **write 操作**（create / update / delete）都要先列出將會做嘅改動，等用戶確認後先執行。

### 2. 唔猜測
如果搵到多個候選 event 而唔確定係邊個，**list 出候選項** 俾用戶確認。唔好自己揀。

### 3. 報告結果
做完操作要報告：`已更新 J26015 1st Cut → 4月25日 ✅`

### 4. 處理 ambiguity

| 情況 | Mugi 做法 |
|------|----------|
| 用戶講 project 名但 Calendar 搵唔到 | 「呢個 project 喺 Calendar 未有 events。你想我幫你建立嗎？」 |
| 搵到 event 但日期同用戶講嘅唔同 | 「Calendar 上 J26015 1st Cut 係 4月20日，但你講緊 4月25日。你想我更新嗎？」 |
| 用戶想 batch update 但有啲 event 已過去 | 「以下 events 日期已過，我唔會改動：[list]。其餘 X 個 events 會推遲 N 日。確認？」 |
| 用戶用非標準 milestone 名 | 建議用標準名稱，但唔阻止（「建議用 '1st Cut' 而唔係 'First Cut'，方便統一搜尋。要用標準名稱嗎？」） |

### 5. Calendar ≠ 唯一真相
Calendar 上嘅資訊**未必 100% up-to-date**（有導演唔 update）。如果用戶提供嘅資訊同 Calendar 有出入，**以用戶講嘅為準**，幫手 update Calendar。

---

## Timeline Estimation

用戶問「幾時交片」或「推後咗幾時」時，可以用以下標準工時估算：

### Pre-Production

| 由 → 到 | Standard wd | Compressed wd |
|---------|-------------|---------------|
| Script Received → Submit Video Flow | 5–6 wd | 3–4 wd |
| Submit Video Flow → Script Lock | 5 wd | 3 wd |
| Script Lock → Submit Style Frame | 2–3 wd | 1 wd |
| Submit Style Frame → Confirm Style Frame | 1–2 wd | 1 wd |
| Script Lock → Shoot（minimum prep buffer）| **7 wd standard** | **3 wd min** |
| T0 (Script Received) → Shoot（total pre-pro）| ~17–18 wd (~3.5 週) | ~9–10 wd (~2 週) |

### Post-Production

| 由 → 到 | Standard wd | Min wd |
|---------|-------------|--------|
| Shoot → 1st Cut | 5 wd | 4 wd |
| 1st Cut → Client FB 1 | 3 wd | 1 wd |
| Client FB 1 → 2nd Cut | 3–5 wd | 3 wd |
| 2nd Cut → Client FB 2 | 3 wd | 1 wd |
| Client FB 2 → 3rd Cut | 3 wd | 2 wd |
| 3rd Cut → Picture Lock | 1 wd | — |
| Picture Lock → VO Recording window 開始 | 1 wd | — |
| VO Recording window 長度 | 2 wd | — |
| VO Recording 結束 → Color/Sound/Subtitle | 1 wd | — |
| Color/Sound/Subtitle → Final Output | 1 wd | — |

**注意：** 呢啲係 Tier 1（標準）工時。實際可能因 project 壓縮。估算僅供參考，唔好講成「一定係」。所有非 shooting milestone 最終都要 cross check HK public holiday + weekend + Calendar saturation 先 finalize。
