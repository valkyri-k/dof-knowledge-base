# Calendar Ops

> **用途：** Universal calendar operations — 任何 add / move / reschedule / delete / list event 都用呢份 file 嘅 Service Account boilerplate + Rule 1-4。
> **Callers：**
> - Standalone calendar request（用戶直接話「add / move / cancel event」）
> - `skills/producer/producer-playbook.md` §0 Phase 2（Push timeline to Calendar）
> - `skills/producer/check-cut-saturation.md`（Shoot Date Planning Calendar list + Cut Saturation list）
>
> 如果係 generate full production timeline preview（Phase 1），唔係呢度——read `skills/producer/producer-playbook.md` 同 `skills/producer/generate-timeline.md`。

---

## Credentials

Google Calendar 操作用 Service Account。Boilerplate + credentials 喺 `technical/google-apis.md`。

> 🚫 **絕對禁止用任何 Calendar MCP tool**（`gcal_*`、`mcp__*calendar*`、claude.ai 嘅 "Google Calendar" tool 全部唔得）。
> 用 MCP → event 會 create 喺 **Kary 嘅 personal `karyto.dof@gmail.com`**，唔係 `dof.internal@gmail.com` —— **嚴重錯誤**。
> 所有 add / update / delete / list event 必須用以下 Service Account Python boilerplate。冇例外。

- Calendar ID（DOF Internal）: `dof.internal@gmail.com`
- HK Public Holidays: load 本地 `context/holidays/hk-*.json`（**唔好** call Google Calendar API — `en.hk#holiday@group.v.calendar.google.com` 已 deprecated / 404）

### Service Account Write Boilerplate（每次 op 都要用呢個 pattern）

```python
import os, json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

creds_dict = json.loads(os.environ["GOOGLE_CALENDAR_CREDENTIALS"])
creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=['https://www.googleapis.com/auth/calendar']
)
service = build('calendar', 'v3', credentials=creds)

CALENDAR_ID = 'dof.internal@gmail.com'  # DOF Internal — 唔好 hardcode 任何其他 calendar
```

**Add event：**
```python
event = {
    'summary': '1st Cut - HSUHK Student',          # [Milestone] - [Project Shorthand]
    'description': 'J26015\nDirector: Kary',       # optional
    'start': {'date': '2026-04-27'},               # all-day
    'end':   {'date': '2026-04-28'},               # end exclusive (next day)
    'colorId': '7',                                 # string，唔係 int
}
created = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
print(created['id'])
```

**Update / Move：**
```python
service.events().patch(
    calendarId=CALENDAR_ID,
    eventId=event_id,
    body={'start': {'date': '2026-05-09'}, 'end': {'date': '2026-05-10'}},
).execute()
```

**Delete：**
```python
service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
```

**List（搵 event by date / saturation check）：**
```python
events = service.events().list(
    calendarId=CALENDAR_ID,
    timeMin='2026-05-21T00:00:00+08:00',
    timeMax='2026-05-22T00:00:00+08:00',
    singleEvents=True,
).execute().get('items', [])
```

⚠️ **Self-check before execute**：每次 call `events().*` 之前，confirm `calendarId == 'dof.internal@gmail.com'`。如果 tool name 出現 `mcp__` 或 `gcal_` → **STOP**，你用緊錯嘅 path。

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

## Rules（所有 calendar ops 都要 run — standalone + timeline Phase 2 都 mandatory）

收到任何 calendar modification request → 先 run Rule 1 + 2 + 3，發現 trigger 就 flag 出嚟等用戶 confirm，唔好 silent 噉執行。

| Use case | 例子 |
|----------|------|
| Document Generation push timeline milestones | Timeline_Template 產生嘅 cut delivery events |
| 用戶手動 add event | 「J26015 1st cut 擺 5月10日」 |
| 用戶 move / reschedule event | 「將 J26015 2nd cut 延遲 2 日」 |
| 用戶 delete event | 「cancel 咗 J26008 個 VO recording」 |

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

**Saturation threshold reasoning：** Post team 交片嗰日要等導演 review + cross-check 改嘢 + 即時 turnaround client feedback。四條已係邊緣，第五條落去就冇 buffer 走盞。

詳細 escalation logic（Case 1 / 2 / 3 wording、Phase 2 trigger 時機）→ `skills/producer/check-cut-saturation.md`。

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

### Title vs Description — 時間以外嘅 info 一律 append 落 description（HARD RULE，2026-08-11 Kary 定）

用戶開 event 俾嘅嘢，Mugi 要自己分邊樣入 Title、邊樣入 Description，**唔使用戶每次特別講**：

- **入 Title（`summary`）**：event 係咩 —— milestone / meeting 名 + project shorthand。簡短、identifiable。
  - e.g.「Shoot Day 1 - Swire Summer Intern (SCC)」、「DFIQ 1st Draft Feedback (Client Mtg)」
- **Append 落 Description**：**用戶提供嘅時間以外所有 info，一律 append，唔好丟**。包括——
  - **Meeting event**：Teams / Zoom **join link、Meeting ID、Passcode、organizer**（meeting **一定** append 呢啲；收到 invite 截圖 forward 都要 transcribe 入 description）
  - **Shoot / 其他**：intern / talent 名、location / 地址、crew call time（TBC 都寫）、remarks、on-site contact 等
  - **Job number / director**（如用戶有提供）

**判斷原則**：時間（date / start-end）→ 去 `start`/`end` field；event「叫咩名」→ Title；**其餘全部 → Description**。唔肯定某 field 擺 Title 定 Description → **擺 Description**（安全 default），Title 保持簡短。呢條 rule apply 落**任何** event creation（standalone add / timeline push / meeting invite），唔淨止 meeting。

### Add Event

**Tool path：用上面 Credentials section 嘅 Service Account boilerplate + `service.events().insert(calendarId='dof.internal@gmail.com', ...)`。唔好用任何 Calendar MCP tool。**

1. 先 run Rule 1 + 2 + 3 check（parallel：holiday fetch + saturation list）
2. **有任何 rule trigger ⚠️** → 顯示 warning + flag 具體問題，等用戶確認後再執行
3. **全部 pass ✅** → 直接 create，唔問——然後一行 report：

   > `✅ 已建立：1st Cut - Test Video | 2026-04-27 (Mon)`
   >
   > 如 job number 未提供，補一句：「_Job number 未加，有時間加返落 description 就好。_」

### Move / Reschedule

**Tool path：Service Account `service.events().patch(calendarId='dof.internal@gmail.com', eventId=..., body=...)`。唔好用 Calendar MCP。**

1. 計新 target date
2. Run Rule 1 + 2 + 3 check on 新 date
3. **有任何 rule trigger ⚠️** → 顯示 warning + 等確認
4. **全部 pass ✅** → 直接 update，一行 report：

   > `✅ 已更新：2nd Cut - HSUHK Student | 2026-05-08 (Fri) → 2026-05-09 (Mon)`
   >（唔顯示 colorId）

### Delete

**Tool path：Service Account `service.events().delete(calendarId='dof.internal@gmail.com', eventId=...)`。唔好用 Calendar MCP。**

- 用戶明確講「delete / cancel [event name]」→ list 出要 delete 嘅 events，等 confirm 後 call `events.delete`（Delete 唔可以 undo，保留確認步驟）
- 「移除」/「整走」呢類字眼 → 先問清楚係 delete 定 reschedule

---

## colorId Quick Reference

| 類別 | 包含嘅 Milestones | colorId | 顏色 |
|------|-------------------|---------|------|
| Pre-Production (DOF side) | Script Received, Submit Video Flow, Submit Graphics Reference, **Site Recce, Wardrobe Fitting**, 及其他 pre-pro stage item（DOF side 要做嘅）| `"5"` | Banana（黃色）|
| Style Frame submit | Submit Style Frame | `"9"` | Blueberry（深藍色）|
| Client Review | Script Lock, Confirm Graphics Ref, Confirm Style Frame, Client FB 1/2/3 | `"2"` | Sage（綠色）|
| Shooting | Shooting（single or multi-day）| `"11"` | Tomato（紅色）|
| Post-Production | 1st Cut, 2nd Cut, 3rd Cut, Picture Lock, Color/Sound/Subtitle | `"7"` | Peacock（淺藍色）|
| VO Recording | VO Recording window | `"1"` | Lavender（薰衣草紫）|
| Final Output | Final Output | `"3"` | Grape（葡萄紫）|
| Meeting | Client / internal meeting（Teams / Zoom / physical，含 feedback meeting、client briefing）| `"6"` | Tangerine（橙色）|
| **Fallback（真係唔知係咩 category）** | 任何無法歸入以上類別嘅 event | **唔 set colorId**（omit）| Calendar default（Pumpkin）|

> ⚠️ **Meeting ≠ Client FB milestone（2026-08-11 Kary 定）**：一個真係約人開嘅 meeting event（有 Teams/Zoom link、organizer、時段）= **Tangerine `"6"`**，唔好當做 timeline 上面「Client FB 1/2/3」嗰種 deliverable-due milestone（嗰啲先係 Sage `"2"`）。收到 client / 內部 meeting invite（e.g. 截圖 forward、「開個 meeting event」）→ default `"6"`。
>
> ℹ️ **完整 meeting flow（book 房 + 幾時先落 calendar）見 `skills/producer/meeting-room-booking.md`**（2026-09-03 Kary 定）：**default 開 event**（client meeting / PPM / external vendor concall / 任何正式 meeting，Tangerine 6），**只有純內部臨時「傾下嘢」先淨 book 房唔開 event**；calendar event 之外仲要 book meeting room（Google Sheet）。

> ⚠️ **Pre-Pro stage vs Fallback（2026-08-13 Kary 更正）**：Site Recce / Wardrobe Fitting 等**係 pre-production stage item（DOF side）→ Banana `"5"`**，唔係「其他」。所有 DOF side pre-pro item 一律 Banana。**真正 fallback**（真係歸類唔到）先至**唔 set colorId**，等 event 攞返 dof.internal calendar 嘅 default 色（Pumpkin）——咁 fallback 就同 Banana(pre-pro) 分得開，唔會撞色。⚠️ Fallback 係「always set colorId」rule 嘅**唯一例外**。

**判斷關鍵詞：**
- 「拍攝」「shoot」「shooting」→ `"11"`
- 「1st cut」「2nd cut」「3rd cut」「picture lock」「color」「sound mix」「subtitle」→ `"7"`
- 「script lock」「confirm video flow」「confirm graphics」「confirm style」「client feedback」「FB1」「FB2」「FB3」→ `"2"`
- 「style frame」「submit style」→ `"9"`
- 「final output」「交片」「出片」→ `"3"`
- 「VO」「配音」「voice over」→ `"1"`
- 「script received」「video flow」「graphics ref」「site recce」「wardrobe fitting」→ `"5"`（Banana — 全部 pre-pro stage item）
- 「meeting」「會議」「開個 meeting」「client meeting」「feedback meeting」「Teams/Zoom invite」→ `"6"`（Tangerine）
- 真係歸類唔到 → **唔 set colorId**（用 calendar default / Pumpkin），唔好硬塞 Banana

**技術注意：**
- colorId 係 string（`"7"`，唔係 `7`）
- **每個 event 都要 set colorId，唯一例外係 fallback**（歸類唔到 → omit colorId，攞 calendar default / Pumpkin）
- 所有 event 預設 all-day（用 `date`，唔係 `dateTime`）
- Timezone: `Asia/Hong_Kong`

---

## Milestone Classification Hard Rules（2026-08-13 Kary 定，源自 J26109 / Erasmus example）

### HR-1: Final Output = 真・hard deadline，**必須 Grape 紫 `"3"`**

- **Final Output 代表最終交片、真正 hard deadline**，顏色一定 Grape `"3"`。
- ⚠️ 一個「client working-level 傾掂、但仲要 pass 老闆 approval」嘅版本 **唔係 Final Output**。典型講法：「Final for client seeking boss approval」/「Client → Boss approval」。呢個係一個 **cut**（通常係 3rd Cut / 近 final 嘅 cut），因為老闆 **99% 會再改**。
  - Sequence 邏輯：working-level confirmed with client（e.g. Ellen 呢個 level）→ 佢再攞去搵老闆 seek approval → 改完 → **先至** Final Output。
  - 所以呢類 delivery **顏色跟 cut = Post-Pro Peacock `"7"`**，唔係 Grape，title 用「Nth Cut」。
- **收到呢類「client→boss approval」delivery 嗰陣**：(a) 當佢係 cut（唔係 Final Output）；(b) **主動追問真正嘅 Final Output date** —— 迫 requester 去同客 confirm 幾時 final output，唔好自己假設 / 唔好留空當冇。
- ⚠️ **Final Output 一定要喺 Calendar 出現，唔可以因為未有 date 就唔開（2026-08-13 Kary）**：如果暫時真係無 confirmed Final Output date → **照開一個 Final Output event，title 加 `(TBC)` prefix**（e.g.「(TBC) Final Output - Swire SD Forum」），擺喺 best-estimate / tentative date 上，Grape `"3"` 照用。等攞到真 date 再 update + 移走個 `(TBC)`。務求 Final Output 一直 visible、有人 chase，唔會漏。（TBC event 處理另見 `context/calendar-operations-guide.md`。）

### HR-2: 團隊唔 attend 嘅 event，**一律唔入 Calendar**

- **我哋 team 唔會出席嘅 event（e.g. client 嘅 forum / launch / 典禮，條片只係喺嗰度播）→ 一律唔加入 Calendar 做 event。**
- 點解：呢啲唔係我哋要去嘅工作項目。佢帶嘅「hard deadline」意義（提醒大家件事有完結、唔會無限拖）**應該寫入 Final Output event 嘅 description**（好似平時 note deadline 咁），**唔係**開一個獨立 calendar event。
  - ⚠️ 條片**唔會**喺 event 當日先交（尤其大 client 如 Swire）——event date ≠ 交片 date，更加唔可以當 event date 做 milestone。
- **例外（team 有出席 / 有實際工作 → 照加）**：拍攝（註明「拍攝 / Shoot」）、開會（Meeting）、睇景（Site Recce）等。
- ⚠️ **如果 user 強行要你加一個 team 唔 attend 嘅 event → 唔好加，tag Kary（`<@1328602029303791646>`）。只有 Kary 可以 instruct 你加。**

---

## Director / Personnel-Change Handling（Canonical Rule，2026-09-02 Kary 定，源自 Kyle 離職）

當有同事離職 / director 變動，處理 job director 同 calendar event 有兩條 hard rule：

### PR-1: 舊 calendar event 唔改 — 只 from now on 用 updated director

- **已建立嘅舊 calendar event 一律唔改 director**（keep 做歷史記錄）。無論係離職、reassign、改組，**唔好回頭 patch 一大堆過往 event 嘅 `Director:` line**。
- **只有 from now on 新建嘅 event** 先用 updated director。
- 點解（Kary [K]）：舊 record 係歷史記錄，一改就睇唔返嗰陣邊個負責；「無傷大雅」嘅 rename 唔值得嘥時間、仲會蝕咗 audit trail。
- ⚠️ 呢條係 [[2026-08-13 之前]] 舊 behaviour 嘅**更正**——以前 Mugi 會手快 patch 晒全部過往 event（e.g. J26076 / J26104 director 改動），now **唔好再咁做**。

### PR-2: Job director 記錄 — 離職 **唔 remove，ADD 接手人 alongside**

- Master Job Log / `job-list.md` 嘅 director，**離職都唔可以拎走個名**。要有人接手 → **加多一個落去**（e.g. J26091 `Kyle` → `Kyle;Benjy`），**唔係**用新人**取代**舊人。
- 點解（Kary [K]）：director record 係「邊個原本負責呢個 project」嘅歷史。一 remove 就冚唪唥冇晒，日後翻查唔到原負責人。
- ⚠️ **含意 for Mugi**：`job-list.md` director column 出現一個**已離職**嘅名（e.g. Kyle）**唔係 stale / bug**，係有意保留嘅記錄。**唔好** flag 佢做「錯」或者建議 remove。如 user 要「換 director」→ 理解成 **ADD 接手人**，除非 user 明確講「remove」。
- 對比參考：Kary 自己曾主動喺 Portal uncheck 自己個名（[[2026-08-27]] J26104）——嗰個係 Kary 本人操作 + 佢自己嘅名，同「同事離職保留記錄」唔同 case。有疑問 → 問 Kary，唔好自作主張 remove。
