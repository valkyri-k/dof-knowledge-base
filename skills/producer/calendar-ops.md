# Calendar Ops

> **呢份 file 只係 standalone calendar operations（add / move / reschedule / delete event）用。**
> 如果係 generate full production timeline，唔係呢度——read `skills/producer/producer-playbook.md`。

---

## Credentials

Google Calendar 操作用 Service Account。Boilerplate + credentials 喺 `technical/google-apis.md`。

⚠️ **禁止用 `gcal_*` MCP tools**——用 Service Account + Python boilerplate。

- Calendar ID（DOF Internal）: `dof.internal@gmail.com`
- HK Public Holidays: load 本地 `context/holidays/hk-*.json`（**唔好** call Google Calendar API — `en.hk#holiday@group.v.calendar.google.com` 已 deprecated / 404）

---

## Event Naming

| 對象 | 格式 | 例子 |
|------|------|------|
| Event title | `[Milestone] - [Project Shorthand]` | `1st Cut - HSUHK Student` |
| Event description | Job number 第一行，Director 第二行（**optional，見下**） | `J26015\nDirector: Kary` |
| Project Shorthand | Client name + 描述，簡短 | `HSUHK Student`、`EMSD Railway Chris` |

---

## Pre-step（任何 calendar op 之前做一次）

Load HK public holidays 由本地 JSON，cache in-memory。**唔好** call Google Calendar API。

**Schema**：頂層 dict，`holidays` field 係 list of `{date, weekday, name_en, name_zh}` objects。**唔好**對 list 盲 call `.keys()`。

```python
import json, glob

holiday_dates = set()
holiday_names_by_date = {}

for path in sorted(glob.glob('context/holidays/hk-*.json')):
    with open(path) as f:
        data = json.load(f)
    for h in data['holidays']:
        d = h['date']
        holiday_dates.add(d)
        holiday_names_by_date[d] = h.get('name_en') or h.get('name_zh', 'Public Holiday')
```

如 planning year JSON 未存在（e.g. 2027）→ surface 俾用戶：「⚠️ 本地未有 `hk-YYYY.json`，請 Kary 補返。」

---

## Rules（所有 standalone calendar ops 都要 run）

### Rule 1: Weekday + HK Public Holiday Check

Office milestone 嘅 target date 必須同時：
1. 係 weekday（Mon–Fri）
2. 唔係 HK 公眾假期（對 in-memory holiday set check）

Apply 喺：Script Lock、Submit / Confirm Video Flow / Graphics Ref / Style Frame、1st / 2nd / 3rd Cut、Client FB 1/2/3、Picture Lock、VO Recording、Final Output。

唔 apply 喺：Shoot（例外，直接 schedule）。

### Rule 2: Weekend / Holiday Cross Check

撞到 weekend 或 holiday → 必須 surface：

> 「⚠️ 留意：[date] 係 [Saturday / Sunday / 公眾假期 — name]，唔係 working day。
>
> 默認情況我會 push 返去 [next weekday]：
> - 要喺 [date] 排 → 你 explicit 講聲
> - 唔需要 → 我 reschedule 去 [next weekday]」

Shoot 係唯一 default exempt——唔需要 cross check weekend / holiday。

### Rule 3: Cut Delivery Saturation Check

將 cut delivery（colorId `"7"`）或 final output（colorId `"3"`）放上某一日之前，先 list 嗰日已有幾多同類 events：

- 已有 **≥ 4** → trigger warning，建議 push 後 1 日
- Warning message：

> 「⚠️ [date] 已有 [N] 條片要交（[list]）。建議 push 去 [next day]——後期 team 需要 buffer 做 review。要繼續排落 [date]？」

### Rule 4: Sohling Escalation

以下兩個情況 tag Sohling（`<@1489108444475686943>`）：
1. Push 1 日都解決唔到（hit deadline / 連日 saturated）
2. Standard rules 無法 resolve 嘅 hard conflict

> 「<@1489108444475686943> 入嚟睇下呢個 channel——[一句講咩 case]，想 check 排期。」

Mugi 唔自己硬 resolve ambiguous case——超出 rule book 直接 tag Sohling。

---

## Ops Flow

**原則：用戶叫 Mugi 做嘢 = 已確認意圖。Rules 係 safety check，唔係 decision pause。Happy path 唔等 confirm——直接執行，一行報告結果。**

### Description Policy（standalone ops）

Standalone calendar op 場景嘅用戶通常係 on-the-go（Benjy 拍緊嘢、client briefing 途中），**唔好 block on description**：

- **Job number 未提供** → 直接 create，event description 留空或用用戶提供嘅任何 info。Create 完之後加一句：「_Job number 未加，有時間加返落 description 就好。_」
- **Director 未指明** → 唔好追問，直接 create 無 Director field。用戶自己喺 request 入面有提到先填。
- **有人提 job number / director** → 照填落 description

**⚠️ 呢個 policy 只係 standalone ops。Producer Playbook 嘅 timeline push 一定要有 job number + director——嗰個場景用戶係坐定定計 timeline，information 齊。**

### Add Event

1. 先 run Rule 1 + 2 + 3 check（parallel：holiday fetch + saturation list）
2. **有任何 rule trigger ⚠️** → 顯示 warning + flag 具體問題，等用戶確認後再執行
3. **全部 pass ✅** → 直接 create，唔問——然後一行 report：

   > `✅ 已建立：1st Cut - Test Video | 2026-04-27 (Mon)`
   >
   > 如 job number 未提供，補一句：「_Job number 未加，有時間加返落 description 就好。_」

### Move / Reschedule

1. 計新 target date
2. Run Rule 1 + 2 + 3 check on 新 date
3. **有任何 rule trigger ⚠️** → 顯示 warning + 等確認
4. **全部 pass ✅** → 直接 update，一行 report：

   > `✅ 已更新：2nd Cut - HSUHK Student | 2026-05-08 (Fri) → 2026-05-09 (Mon)`
   >（唔顯示 colorId）

### Delete

- 用戶明確講「delete / cancel [event name]」→ list 出要 delete 嘅 events，等 confirm 後 call `events.delete`（Delete 唔可以 undo，保留確認步驟）
- 「移除」/「整走」呢類字眼 → 先問清楚係 delete 定 reschedule

---

## colorId Quick Reference

| 類別 | 包含嘅 Milestones | colorId | 顏色 |
|------|-------------------|---------|------|
| Pre-Production (DOF deliverable) | Script Received, Submit Video Flow, Submit Graphics Reference | `"5"` | Banana（黃色）|
| Style Frame submit | Submit Style Frame | `"9"` | Blueberry（深藍色）|
| Client Review | Script Lock, Confirm Graphics Ref, Confirm Style Frame, Client FB 1/2/3 | `"2"` | Sage（綠色）|
| Shooting | Shooting（single or multi-day）| `"11"` | Tomato（紅色）|
| Post-Production | 1st Cut, 2nd Cut, 3rd Cut, Picture Lock, Color/Sound/Subtitle | `"7"` | Peacock（淺藍色）|
| VO Recording | VO Recording window | `"1"` | Lavender（薰衣草紫）|
| Final Output | Final Output | `"3"` | Grape（葡萄紫）|
| 其他 | Site Recce, Wardrobe Fitting 等 | `"5"` | Banana（fallback）|

**判斷關鍵詞：**
- 「拍攝」「shoot」「shooting」→ `"11"`
- 「1st cut」「2nd cut」「3rd cut」「picture lock」「color」「sound mix」「subtitle」→ `"7"`
- 「script lock」「confirm video flow」「confirm graphics」「confirm style」「client feedback」「FB1」「FB2」「FB3」→ `"2"`
- 「style frame」「submit style」→ `"9"`
- 「final output」「交片」「出片」→ `"3"`
- 「VO」「配音」「voice over」→ `"1"`
- 「script received」「video flow」「graphics ref」→ `"5"`

**技術注意：**
- colorId 係 string（`"7"`，唔係 `7`）
- 所有 event 預設 all-day（用 `date`，唔係 `dateTime`）
- Timezone: `Asia/Hong_Kong`
