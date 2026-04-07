# Calendar Operations Guide（Mugi 操作手冊）

呢份係 Mugi 操作 Google Calendar 嘅完整 reference。所有 Calendar 操作都要跟呢度嘅規則。

---

## 基本設定

- **Calendar ID:** `dof.internal@gmail.com`
- **認證方式:** Service Account（環境變數 `GOOGLE_CALENDAR_CREDENTIALS`）
- **操作庫:** `google-api-python-client` + `google-auth`

---

## Event 命名規則（必須跟從）

### Title 格式
```
[Milestone] - [Project Shorthand]
```

例子：
```
1st Cut - HSUHK Student
Client FB 1 - EMSD Railway Chris
Final Output - CLP TK CEO Msg
Shoot - HKBU Orientation
Picture Lock - MTR Safety
```

### Description 格式
```
J26016
Director: Kary
[其他備註，如有]
```

- Job number 放 Description **第一行**（Google Calendar search 可以搵到 description 內容）
- Director 姓名放第二行

### 命名原則
- **唔把 Job Number 放 title** — Calendar view 格太細，J-number 壓住有用資訊
- **Milestone 名稱必須用標準 set**（見下方），唔接受自由發揮
- **Project Shorthand 跟開 job 時定好嘅版本** — 唔好自己作一個

---

## 標準 Milestone Set

呢個係一個完整 timeline 嘅所有 milestones，按階段分組。**Push timeline 上 Calendar 時，default 行為係 push 完整集合**（適用嘅 milestones），唔好淨係 push post-pro section。

### Pre-Production

| Milestone | colorId | 顏色 | 用途 | 條件 |
|-----------|---------|------|------|------|
| `Client Confirm Script` | `2` | Client Feedback 綠 | Script 確認 deadline（client 做嘅嘢） | 標準 — 不論 client 提供定 DOF 撰寫都要有 |
| `Video Flow` | `5` | Pre-Pro 黃 | Submit Video Flow + Graphics Reference（DOF 做嘅嘢） | 標準 |
| `Confirm Video Flow` | `2` | Client Feedback 綠 | Client confirm Video Flow + Reference（client 做嘅嘢） | 標準 |
| `Submit Style Frame` | `9` | Style Frame 深藍 | Style Frame 提交（DOF 做嘅嘢） | 該 project 走 style frame 流程 |
| `Confirm Style Frame` | `2` | Client Feedback 綠 | Style Frame 確認（client 做嘅嘢） | 該 project 走 style frame 流程 |

### Shooting

| Milestone | colorId | 顏色 | 用途 | 備註 |
|-----------|---------|------|------|------|
| `Shoot` | `11` | Shooting 紅 | 拍攝日 | 多日就 push 多個 event |

### Post-Production

| Milestone | colorId | 顏色 | 用途 | 備註 |
|-----------|---------|------|------|------|
| `1st Cut` | `7` | Post-Pro 淺藍 | 第一版剪接交客 | 4–5 wd after shoot（標準） |
| `Client FB 1` | `2` | Client Feedback 綠 | 客戶第一輪 feedback deadline | |
| `2nd Cut` | `7` | Post-Pro 淺藍 | 第二版剪接交客 | 3–5 wd after Client FB 1 |
| `Client FB 2` | `2` | Client Feedback 綠 | 客戶第二輪 feedback deadline | |
| `3rd Cut` | `7` | Post-Pro 淺藍 | 第三版剪接交客 | 3 wd after Client FB 2 |
| `Client FB 3` | `2` | Client Feedback 綠 | 客戶第三輪 feedback deadline | 唔係每個 project 都有 |
| `Picture Lock` | `7` | Post-Pro 淺藍 | 畫面鎖定 | |
| `VO Recording` | `1` | VO 薰衣草紫 | 旁白錄音 | 如有需要 |
| `Final Output` | `3` | Final 葡萄紫 | 最終成品交付 | |

**重要：** 統一用呢套名稱。例如：
- ✅ `1st Cut - HSUHK Student`
- ❌ `1st cut EMSD`
- ❌ `Feedback on 1st cut`
- ❌ `First Cut`

---

## Milestone Selection Logic（push timeline 時用）

當你 build 或 push 一個完整 timeline 上 Calendar 時，**default 包含所有適用嘅 milestones**，唔好淨係 push post-pro。

### Default Inclusion Rules

| Milestone | Always Push? | 條件 |
|-----------|--------------|------|
| `Client Confirm Script` | ✅ Always | 不論 client 提供定 DOF 撰寫，都要有確認步驟 |
| `Video Flow` | ✅ Always | 標準 pre-pro deliverable |
| `Confirm Video Flow` | ✅ Always | 標準 pre-pro deliverable |
| `Submit Style Frame` | Conditional | 該 project 走 style frame 流程 |
| `Confirm Style Frame` | Conditional | 該 project 走 style frame 流程 |
| `Shoot` | Conditional | hasShooting === true（多日就 push 多個 event） |
| `1st Cut` → `Final Output` | ✅ Always | 標準 post-pro 流程 |
| `Client FB 3` | Conditional | 該 project 預咗 3 輪 client feedback |
| `VO Recording` | Conditional | needsVO === true |

### 常見錯誤（Anti-patterns）

- ❌ **只 push post-production milestones** — pre-pro 都要 push（包括 Client Confirm Script、Video Flow、Confirm Video Flow）
- ❌ **跳過 Style Frame milestones** — 除非用戶明確講該 project 唔走 style frame 流程
- ❌ **「壓縮版就唔 push pre-pro」** — 壓縮版只係縮短工時（後期 Tier 1 → Tier 2/3/4），milestone set 唔變
- ❌ **假設 client 提供 script 就唔需要 confirm** — 仍然要 push `Client Confirm Script`
- ❌ **顏色邏輯搞錯** — 原則：DOF 做嘅嘢 = 黃（Pre-Pro）；Client 做嘅嘢 = 綠（Client Feedback）。所以 `Video Flow`（DOF submit）= 黃；`Client Confirm Script` + `Confirm Video Flow`（client 確認）= 綠；Style Frame submit/confirm = `9` 深藍

### 用戶冇明確講要 push 邊啲時

Default 行為 = push **完整 milestone set**（pre-pro + shoot + post-pro），按上面 conditional rules filter。如果用戶只想 push 某個階段，佢會明確講「淨係 push post-pro」之類。

### Push 之前要列俾用戶睇

跟「先確認再執行」原則 — 列出將會 push 嘅完整 milestone list（按階段分組），等用戶 confirm 後先 batch create。如果有 milestone 用戶覺得唔需要，佢會話你知 skip 邊個。

---

## colorId Mapping

建立或修改 Calendar event 時，必須根據 milestone 類別設定正確嘅 `colorId`。呢套顏色同 Doji Timeline 同 DOF Planner 完全一致。

| 類別 | 包含嘅 Milestones | colorId | 顏色 |
|------|-------------------|---------|------|
| Pre-Production | Video Flow, Graphics Reference | `5` | Banana（黃色） |
| Style Frame | Submit Style Frame | `9` | Blueberry（深藍色） |
| Shooting | Shoot / Shooting Day(s) | `11` | Tomato（紅色） |
| Post-Production | 1st Cut, 2nd Cut, 3rd Cut, Picture Lock | `7` | Peacock（淺藍色） |
| Client Feedback | Client Confirm Script, Confirm Video Flow, Confirm Style Frame, Client FB 1, Client FB 2, Client FB 3 | `2` | Sage（綠色） |
| VO Recording | VO Recording | `1` | Lavender（薰衣草紫） |
| Final Output | Final Output | `3` | Grape（葡萄紫） |
| 其他 | Site Recce, Wardrobe Fitting 等 | `5` | Banana（fallback） |

### 判斷關鍵詞
- 「拍攝」「shoot」「shooting」→ colorId: `11`
- 「1st cut」「2nd cut」「3rd cut」「picture lock」→ colorId: `7`
- 「client feedback」「FB1」「FB2」「客 feedback」→ colorId: `2`
- 「style frame」「submit style」→ colorId: `9`（DOF 提交）
- 「confirm style」→ colorId: `2`（client 確認）
- 「final output」「交片」「出片」→ colorId: `3`
- 「VO」「配音」「voice over」→ colorId: `1`
- 「client confirm script」「confirm script」「confirm video flow」「client feedback」→ colorId: `2`（client 做嘅嘢）
- 「video flow」「graphics ref」或其他 pre-pro DOF deliverable → colorId: `5`

### 技術注意
- colorId 係 **string**（`"7"`，唔係 `7`）
- 所有 event 預設 **all-day**（用 `date`，唔係 `dateTime`）
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

### Batch Update（批量更新）
- 一次過將某個 job 嘅所有 milestones 推遲 / 提前 N 日
- **做法：** Search by Job Number → get all events → update each event
- **確認流程：** List 出會影響嘅 events 俾用戶確認 → 用戶 confirm 後先執行

### Add（新增 event）
- 建新 milestone event
- 必須跟 naming convention
- 必須設 colorId
- 加 description（Job Number + Director）

### Remove TBC
- TBC event 喺 title 會有 `(TBC)` 標記
- 日期確認後 → remove `(TBC)` + 更新日期

---

## TBC Events

未確定日期嘅 milestone 可以先放 TBC（大概日期），title 加 `(TBC)`：
```
1st Cut - HSUHK Student (TBC)
```

當日期確認後：
1. Remove `(TBC)` from title
2. Update 到正確日期

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

用戶問「幾時交片」或「推後咗幾時」時，可以用 `production-pipeline.md` 嘅標準工時估算：

| 由 → 到 | 標準 Working Days |
|---------|-------------------|
| Shoot → 1st Cut | 5 wd |
| 1st Cut → Client FB 1 | 3 wd |
| Client FB 1 → 2nd Cut | 3–5 wd |
| 2nd Cut → Client FB 2 | 3 wd |
| Client FB 2 → 3rd Cut | 3 wd |
| 3rd Cut → Picture Lock | 3 wd |
| Picture Lock → VO Recording | 2–3 wd |
| VO Recording → Final Output | 2 wd |

**注意：** 呢啲係 Tier 1（標準）工時。實際可能因 project 壓縮。估算僅供參考，唔好講成「一定係」。
