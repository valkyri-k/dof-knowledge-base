# Meeting Handling — Room Booking + Calendar Event

> Canonical rule 2026-09-03（Kary 定，源自 Meeting Room Reservation sheet write 打通後）。
> 兩件可以獨立、可以一齊發生嘅事：**(A) book meeting room**（Google Sheet）+ **(B) create Calendar event**。
> 收到 meeting / 開會 / book 房相關 request → read 呢個 file。

---

## 0. 兩個 action，分開判斷

| Action | 幾時做 |
|--------|-------|
| **A. Book meeting room**（sheet）| 只要係實體開會 / user 叫 book 房。我哋通常都喺房開會，所以 **point 都要 book 房**。User 亦可以**獨立**淨叫「幫我 book 房」（唔一定有 meeting event）。 |
| **B. Create Calendar event** | **只有 client meeting 先落 calendar**。純內部自己傾嘢 → **唔使 create event**（淨 book 房）。 |

**Client vs internal 判斷**：有 client name / 「同 client 開會」/ client briefing / client feedback / 有外部參與者 → client meeting（做埋 B）。純內部 sync / 自己傾嘢 → 淨 A。**唔肯定 client 定 internal → 問 user**（因為 create event 係 side effect，寧問莫估）。

---

## 1. Action A — Book Meeting Room（Google Sheet）

### Sheet identity
- **Spreadsheet**：`Meeting Room Reservation`
- **Spreadsheet ID**：`1fZeoCHzRMPqROorxhjK5zemTL8uGKmWlUWKoe7pbw-s`
- Owner 係第三方（`chunyatchi@gmail.com`），`dof.internal@gmail.com` 有 **canEdit** → 用 Drive OAuth 寫。

### Credentials / boilerplate（Hard Rule — 唔可以用 MCP）
- 用 `technical/google-apis.md` §Google Drive / Docs OAuth2 boilerplate 起 `sheets_service`（`build("sheets","v4", …)`）。
- ⚠️ **Scope 只准 `drive` + `documents`**。Sheets API v4 用 `drive` scope 就讀寫得到，**唔使 `spreadsheets` scope**。多列 `spreadsheets` → refresh `invalid_scope` 全掛（[[2026-09-03]] 實測踩過）。
- 詳細 gotcha 見 `technical/google-apis.md` line ~89。

### Sheet 結構（月 tab × 週 grid）
- 每個月一個 tab，命名 `MMM-YY`（e.g. `Sep-26`、`Aug-26`）。**先由 date 揀啱 tab**。
- Row 2 = 星期 header（Monday…Sunday），每個星期佔 **2 columns**：左=Small Room（細房）、右=Large Room（大房）。
- Column 對照：Mon=A/B、Tue=C/D、Wed=E/F、Thu=G/H、Fri=I/J、Sat=K/L、Sun=M/N（左=Small、右=Large）。
- 每個 **週 block**：一行「日子號碼」row（e.g. `K4='5'`），跟住下面幾行係嗰日嘅 booking。
- **日子號碼坐喺該星期嘅 Small-Room column**（e.g. 星期六 5 號 → `K4`；Large Room 就係隔離 `L`）。
- Booking cell 格式：`<Name> HH:MM - HH:MM`（e.g. `Kary 10:00 - 11:00`）。

### 落格 algorithm
1. **Tab** = date 嘅 `MMM-YY`。
2. **Weekday** 用 Python 計（`datetime.strptime(...).strftime("%A")` — Hard Rule，唔可以靠記憶），決定星期 → column pair。
3. 喺該星期 **Small-Room column** 搵到 value == 日子號碼嗰個 cell = date row `R`。
4. **Room column**：Small = 該星期 small col；Large = small col + 1。
5. 喺 room column、`R` 下面第一個**空** row（喺下一個 date row 之前）寫入。
6. Value = `<requesting user 個名> HH:MM - HH:MM`。
7. **寫之前先 read 該格 / 該 room column 嗰個 week block 睇有冇 conflict**；寫完 read-back 確認。

### Room 選擇（user 無講 → 自動揀，唔問）
- **User 講明大房 / 細房** → book 嗰間。
- **User 無講** → **自動優先大房**；大房嗰個時段已經有人 book → **自動轉細房**。**唔使問 user** —— 直接 book，user 想改就自己 revert（2026-09-03 Kary 定）。
- 兩間都 book 咗嗰個時段 → flag user，唔好硬塞。

### Booking cell label
- **一律用 requesting user 個名**（即叫我 book 房嗰個人），同 calendar event `Attendee:` 一致。

### 日期 check scope（room booking）
- **Python weekday 必做**（要擺啱 column，兼 Date↔Day 一致）。
- **唔跑 holiday / Sunday block check** —— 開會可以喺任何日子（同 attended events 一樣），唔受 milestone-holiday rule 限制。

---

## 2. Action B — Calendar Event（只 client meeting）

用 `skills/producer/calendar-ops.md` 標準 Service Account 寫入 path（dof.internal calendar）。要點：

| Field | 值 |
|-------|----|
| **Title（summary）** | **跟 user 講法**（user 點叫就點寫，唔硬套 milestone 命名） |
| **Time** | user 講嘅時間 → `start` / `end`（Title vs Description hard rule） |
| **colorId** | **`"6"` Tangerine**（keep，同現有 Meeting rule 一致 — 2026-09-03 Kary confirm 唔用 Pumpkin） |
| **Meeting link**（Teams / Zoom 等） | append 落 **description**（join link / Meeting ID / passcode / organizer 全部 transcribe） |
| **Description — attendee** | `Attendee: <requesting user>`（log 邊個 user） |
| **Description — job** | **淨係喺 job channel 收到先 mark job**：description 第一行寫 `J26XXX - {Job Name}`（channel → job-list.md 反查 J# + project name）。喺 home base / 非 job channel → **唔理 job、唔 log job** |
| **Director** | 唔寫（meeting 唔屬 job milestone；job channel 只 mark J#，唔加 director） |

Description 例（job channel client meeting）：
```
J26065 - CLP HKMA
Attendee: Kary
Teams: https://teams.microsoft.com/l/meetup-join/...
Meeting ID: 123 456 789 / Passcode: abcd
```
Description 例（非 job channel client meeting）：
```
Attendee: Kary
Teams: https://teams.microsoft.com/l/...
```

### 日期 check scope（meeting event）
- Python weekday verify（Date↔Day 一致）。
- **唔 block holiday / Sunday**（meeting 可以任何日子，同 Shoot 一樣屬 attended event）。

---

## 3. 完整 flow（收到 meeting request）

1. **判斷**：純內部傾嘢 → 淨 Action A。Client meeting → A + B。獨立「book 房」→ 淨 A。唔肯定 client/internal → 問。
2. **Room**：user 有講房就用；無講 → **自動優先大房、大房 taken 轉細房（唔問，user 想改自己 revert）**。
3. **Book 房**（Action A）：Python weekday → 揀 tab / column → 搵 date row → 空格寫 `<user> HH:MM - HH:MM` → read-back。
4. **（client 先做）Calendar event**（Action B）：Tangerine 6、title 跟 user、link→desc、`Attendee: <user>`、job channel 加 `J26XXX - {Job Name}`。
5. **Reply confirm**：講清楚 book 咗邊間房 + 邊日邊個時段（+ 如有 create 咗 calendar event 就一齊報）。任何 side effect 都要 confirm 句（e.g.「已 book 大房 9/5（六）10:00–11:00 ✅」）。
