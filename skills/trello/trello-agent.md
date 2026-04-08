# Trello Agent

> **呢份 file 係 Mugi 操作 DOF Postpro Job List Trello board 用。**
> 所有 Trello 相關操作（create card、assign、dates、labels、checklists、move）都由呢份 file 主導。

---

## Credentials

```python
import os, requests

TRELLO_API_KEY = os.environ['TRELLO_API_KEY']
TRELLO_TOKEN   = os.environ['TRELLO_TOKEN']
AUTH = {'key': TRELLO_API_KEY, 'token': TRELLO_TOKEN}
BASE = 'https://api.trello.com/1'
```

⚠️ **唔可以 hardcode key / token。必須從 env vars 讀取。**

---

## Board Constants

```python
BOARD_ID = 'gThmFbyu'  # DOF Postpro Job List
```

---

## Pre-step（每個 Trello session 開始時做一次）

Fetch board metadata → cache in-memory，避免重複 API call：

```python
def fetch_board_meta():
    """Fetch lists, members, labels. Call once per session, cache results."""
    lists   = requests.get(f'{BASE}/boards/{BOARD_ID}/lists',   params={**AUTH, 'fields': 'id,name'}).json()
    members = requests.get(f'{BASE}/boards/{BOARD_ID}/members', params={**AUTH, 'fields': 'id,fullName,username'}).json()
    labels  = requests.get(f'{BASE}/boards/{BOARD_ID}/labels',  params={**AUTH, 'fields': 'id,name,color'}).json()
    return {
        'lists':   {l['name']: l['id'] for l in lists},        # name → id
        'members': {m['username']: m['id'] for m in members},  # username → id
        'labels':  {lb['name']: lb['id'] for lb in labels},    # name → id
        'lists_raw':   lists,
        'members_raw': members,
        'labels_raw':  labels,
    }

meta = fetch_board_meta()
```

**List naming convention：** `[J-number] [Project Title]`，例如 `J26016 HSUHK`、`J26041 HKTB`。

---

## Operations

### ⚠️ List 操作黃金規則：先搵，後建

**任何時候都唔可以直接 create 新 list，必須先 check board 上面係咪已有同名 list。**

```python
def find_or_create_list(job_number: str, project_title: str) -> dict:
    """
    ALWAYS call this instead of directly creating a list.
    Searches existing lists for one containing the job number.
    Returns existing list if found; only creates new one if truly absent.

    job_number    : e.g. 'J26054'
    project_title : e.g. 'EMSD QA'
    """
    lists = requests.get(f'{BASE}/boards/{BOARD_ID}/lists',
                         params={**AUTH, 'fields': 'id,name'}).json()

    # Search by job number (case-insensitive) — title may differ slightly
    for lst in lists:
        if job_number.lower() in lst['name'].lower():
            return {'list': lst, 'created': False}

    # Not found → create new
    new_list = requests.post(f'{BASE}/lists',
                             params={**AUTH, 'name': f'{job_number} {project_title}',
                                     'idBoard': BOARD_ID}).json()
    return {'list': new_list, 'created': True}
```

**回覆格式：**
- 找到現有 list → 「找到現有 list『J26054 EMSD QA』，append 落去。」
- 新建 list → 「Board 上冇呢個 job，建立新 list『J26054 EMSD QA』。」

---

### 1. List Projects（所有 active lists）

```python
def list_projects():
    lists = requests.get(f'{BASE}/boards/{BOARD_ID}/lists', params={**AUTH, 'fields': 'id,name,pos'}).json()
    return lists  # each: {id, name, pos}
```

---

### 2. Get Cards in a Project

```python
def get_cards_in_list(list_id):
    cards = requests.get(
        f'{BASE}/lists/{list_id}/cards',
        params={**AUTH, 'fields': 'id,name,due,start,dueComplete,idMembers,idLabels,pos'}
    ).json()
    return cards
```

用法：先從 `meta['lists']` 搵 list_id，再 call 呢個 function。

---

### 3. Get Card Detail（含 checklists）

```python
def get_card(card_id):
    card = requests.get(
        f'{BASE}/cards/{card_id}',
        params={**AUTH, 'checklists': 'all', 'checkItemStates': 'true',
                'fields': 'id,name,desc,due,start,dueComplete,idMembers,idLabels,idList,pos'}
    ).json()
    return card
```

---

### 4. Create Card

```python
def create_card(list_id, name, desc='', start=None, due=None, member_ids=None, label_ids=None):
    """
    list_id    : from meta['lists'][project_name]
    name       : card title (task name)
    desc       : optional description
    start/due  : ISO 8601 string e.g. '2026-04-10T00:00:00.000Z'
    member_ids : list of member id strings
    label_ids  : list of label id strings
    """
    payload = {**AUTH, 'idList': list_id, 'name': name}
    if desc:       payload['desc']       = desc
    if start:      payload['start']      = start
    if due:        payload['due']        = due
    if member_ids: payload['idMembers']  = ','.join(member_ids)
    if label_ids:  payload['idLabels']   = ','.join(label_ids)
    return requests.post(f'{BASE}/cards', params=payload).json()
```

---

### 5. Update Card

```python
def update_card(card_id, **kwargs):
    """
    Supported kwargs: name, desc, idList (move), due, start, dueComplete (bool), pos
    Examples:
      update_card(cid, name='New Title')
      update_card(cid, due='2026-04-15T00:00:00.000Z', start='2026-04-10T00:00:00.000Z')
      update_card(cid, idList=new_list_id)   # move to another project
      update_card(cid, dueComplete=True)     # mark complete
    """
    return requests.put(f'{BASE}/cards/{card_id}', params={**AUTH, **kwargs}).json()
```

---

### 6. Assign / Remove Member

```python
def add_member(card_id, member_id):
    return requests.post(f'{BASE}/cards/{card_id}/idMembers',
                         params={**AUTH, 'value': member_id}).json()

def remove_member(card_id, member_id):
    return requests.delete(f'{BASE}/cards/{card_id}/idMembers/{member_id}',
                           params=AUTH).json()
```

---

### 7. Add / Remove Label

```python
def add_label(card_id, label_id):
    return requests.post(f'{BASE}/cards/{card_id}/idLabels',
                         params={**AUTH, 'value': label_id}).json()

def remove_label(card_id, label_id):
    return requests.delete(f'{BASE}/cards/{card_id}/idLabels/{label_id}',
                           params=AUTH).json()
```

---

### 8. Archive Card（唔係 delete——move to archive）

```python
def archive_card(card_id):
    return requests.put(f'{BASE}/cards/{card_id}', params={**AUTH, 'closed': 'true'}).json()
```

⚠️ **唔好 delete card**。Archive = `closed: true`。如果 Kary 明確講 delete 先真係 delete。

---

### 9. Checklist Operations

#### 9a. Create Checklist on Card

```python
def create_checklist(card_id, name='Checklist'):
    return requests.post(f'{BASE}/checklists',
                         params={**AUTH, 'idCard': card_id, 'name': name}).json()
    # returns: {id, name, checkItems: []}
```

#### 9b. Add Checklist Item

```python
def add_checkitem(checklist_id, name, due=None, member_id=None, pos='bottom'):
    """
    name      : item description
    due       : ISO 8601 string (optional)
    member_id : single member id string (optional)
    pos       : 'top' | 'bottom' | number
    """
    payload = {**AUTH, 'name': name, 'pos': pos}
    if due:       payload['due']      = due
    if member_id: payload['idMember'] = member_id
    return requests.post(f'{BASE}/checklists/{checklist_id}/checkItems', params=payload).json()
```

#### 9c. Update Checklist Item

```python
def update_checkitem(card_id, checkitem_id, **kwargs):
    """
    Supported kwargs: name, state ('complete'|'incomplete'), due, idMember, pos
    Examples:
      update_checkitem(cid, iid, state='complete')
      update_checkitem(cid, iid, due='2026-04-12T00:00:00.000Z', idMember=member_id)
    """
    return requests.put(f'{BASE}/cards/{card_id}/checkItem/{checkitem_id}',
                        params={**AUTH, **kwargs}).json()
```

#### 9d. Delete Checklist Item

```python
def delete_checkitem(checklist_id, checkitem_id):
    return requests.delete(f'{BASE}/checklists/{checklist_id}/checkItems/{checkitem_id}',
                           params=AUTH).json()
```

#### 9e. Get Checklists on Card

```python
def get_checklists(card_id):
    return requests.get(f'{BASE}/cards/{card_id}/checklists', params=AUTH).json()
    # returns list of {id, name, checkItems: [{id, name, state, due, idMember}]}
```

---

## Label Auto-Detection（收到 create card request 時必須執行）

收到 card 相關 request，**先跑呢個邏輯**，自動 infer label，唔好等用戶明確指定。

### Label 定義

| Label | 意思 | 負責人 |
|-------|------|--------|
| `cut` | Editor 做嘅所有 task：任何版次 cut（1st / 2nd / 3rd / picture lock）、color grading、sound mixing、subtitle | Yik、Katy（editor 同事） |
| `mograph` | Motion graphics 同事做嘅所有 task：motion、animation、name tag / card、design、graphic、collage、lower third | Max、Keith（mograph 同事）、Kay（部分 design task） |
| `style frame` | Style frame 相關（Submit / Confirm / Reference）。**獨立 label，唔同時加 `mograph`。** | Kay（主責）、Max |
| `Pre-Pro` | 前期製作 task：PPM、call sheet、storyboard、script、site recce | Kary、KT |
| `Shooting` | 拍攝日相關 task | — |
| `from client` | 來自客戶嘅 feedback / comment / material | — |
| `VO recording` | VO、voiceover 錄音 | — |
| `final` | Final output / final delivery | — |
| `waiting comment/material` | 等緊客戶 feedback 或素材 | — |
| `RIP` | Dead / cancelled / archived project | — |

---

### Label Detection Rules（按優先順序）

**Rule 1 — Member 身份 → 最高優先**

Member 身份直接決定 label，唔理 task 名入面有冇 "cut" 字：

```python
# Member → label mapping
MOGRAPH_MEMBERS      = {'max', 'keith'}        # → 'mograph'（無論 task 係咩）
STYLE_FRAME_MEMBERS  = {'kay'}                 # → 先睇 style frame kw，否則 'mograph'
EDITOR_MEMBERS       = {'yik', 'katy'}         # → 'cut'
DIRECTOR_MEMBERS     = {'kary', 'benjy'}       # → 視乎 task kw：Pre-Pro / Shooting / from client / VO recording / final
```

**Director member 邏輯：** Kary / Benjy 係 project 負責導演，負責前期、拍攝、客戶溝通、VO、final 嘅監督。呢幾個 label 預設歸佢哋，同後期同事預設係 `cut` / `mograph` / `style frame` 係同一個邏輯。

```python
# 如果 assigned member 係 Kary 或 Benjy → 用 task keyword 揀 label：
DIRECTOR_LABEL_MAP = [
    (['ppm', 'pre-pro', 'pre pro', 'preproduction', 'pre-production',
      'call sheet', 'callsheet', 'storyboard', 'recce', 'site recce', 'script'],  'Pre-Pro'),
    (['shoot', 'shooting', 'filming', 'd1', 'd2', 'd3'],                           'Shooting'),
    (['comment from client', 'feedback from client', 'client comment',
      'client feedback', 'from client', 'fb1', 'fb2', 'fb3'],                     'from client'),
    (['vo recording', 'vo ', 'voiceover', 'voice over', 'voice-over'],             'VO recording'),
    (['final output', 'final delivery', 'final'],                                  'final'),
]
# 逐個 keyword group 對比 task name → 第一個 match 嘅 label 勝出
# 如果 task name 唔 match 任何 group → 唔加 label，回覆提示用戶手動指定
```

例：「Keith 做 1st cut 嘅 motion」→ Keith = mograph member → label: `mograph`（唔雙標 `cut`）

**Rule 2 — Style frame keyword → 獨立 label，唔疊加 `mograph`**

`style frame` 係獨立類別。一旦 task 名有 style frame 相關字眼，**只加 `style frame`，唔同時加 `mograph`**，就算 assigned 俾 Max / Kay 都係。

**Rule 3 — Task keyword（member 唔係 mograph/editor 時才 fallback 用）**

```python
def infer_labels(task_name: str, assigned_member_name: str = '') -> list[str]:
    """
    Priority:
      1. style frame keywords → 'style frame' only (exclusive)
      2. member identity      → mograph / cut by person
      3. task keywords        → fallback if member unknown
    """
    name_lower   = task_name.lower()
    member_lower = assigned_member_name.lower()
    labels = []

    # --- Priority 1: Style frame (exclusive label) ---
    style_frame_kw = ['style frame', 'styleframe', 'style ref', 'style reference']
    if any(kw in name_lower for kw in style_frame_kw):
        labels.append('style frame')
        # stop here — style frame doesn't stack with mograph
        # still check other non-mograph labels below
    else:
        # --- Priority 2: Member identity ---
        if any(m in member_lower for m in ['max', 'keith']):
            labels.append('mograph')
        elif 'kay' in member_lower:
            # Kay: design / mograph tasks
            mograph_kw = ['motion', 'mograph', 'animation', 'name tag', 'name card',
                          'lower third', 'graphic', 'design', 'collage', 'animate']
            labels.append('mograph' if any(kw in name_lower for kw in mograph_kw) else 'mograph')
            # Kay defaults to mograph unless style frame (handled above)
        elif any(m in member_lower for m in ['yik', 'katy']):
            labels.append('cut')
        else:
            # --- Priority 3: Task keyword fallback ---
            mograph_kw = ['motion', 'mograph', 'motion graphic', 'animation', 'animate',
                          'name tag', 'name card', 'lower third', 'graphic', 'design', 'collage']
            cut_kw     = ['1st cut', '2nd cut', '3rd cut', '4th cut', 'first cut', 'second cut',
                          'third cut', 'fourth cut', 'picture lock', 'pic lock', 'editing',
                          'color grading', 'colour grading', 'sound mixing', 'subtitle']
            if any(kw in name_lower for kw in mograph_kw):
                labels.append('mograph')
            elif any(kw in name_lower for kw in cut_kw):
                labels.append('cut')

    # --- Always check these (independent of mograph/cut) ---
    prepro_kw      = ['ppm', 'pre-pro', 'pre pro', 'preproduction', 'pre-production',
                      'call sheet', 'callsheet', 'storyboard', 'recce', 'site recce', 'script']
    shoot_kw       = ['shoot', 'shooting', 'filming', 'd1/', 'd2/', 'd3/']
    from_client_kw = ['comment from client', 'feedback from client', 'client comment',
                      'client feedback', 'from client', 'fb1', 'fb2', 'fb3']
    vo_kw          = ['vo recording', 'voiceover', 'voice over', 'voice-over']
    final_kw       = ['final output', 'final delivery']
    waiting_kw     = ['waiting', 'wait for', 'pending comment', 'pending material']

    if any(kw in name_lower for kw in prepro_kw):      labels.append('Pre-Pro')
    if any(kw in name_lower for kw in shoot_kw):       labels.append('Shooting')
    if any(kw in name_lower for kw in from_client_kw): labels.append('from client')
    if any(kw in name_lower for kw in vo_kw):          labels.append('VO recording')
    if any(kw in name_lower for kw in final_kw):       labels.append('final')
    if any(kw in name_lower for kw in waiting_kw):     labels.append('waiting comment/material')

    return list(dict.fromkeys(labels))  # deduplicate, preserve order
```

**Rule 4 — 唔確定（infer 唔到）→ 建 card 但唔加 label，回覆時提一句**

```
「已喺 J26039 British Council 建立 card「Revise Name Tag」，assign: Max，label: mograph。」
# 如果搵唔到 label：
「已建立 card，唔確定 label 類別，請你手動加。」
```

**唔需要 confirm 先 create。直接建，有錯等用戶糾正。**

---

### 例子

| 用戶講 | Label | 原因 |
|--------|-------|------|
| "Max今日要改British Council comment, need to revise name tag" | `mograph` | Max = mograph member |
| "Keith 做 HSUHK 嘅 motion for 1st cut" | `mograph` | Keith = mograph member，唔雙標 cut |
| "Yik 做 J26047 嘅 2nd cut editing" | `cut` | Yik = editor member |
| "Kay 做 EMSD 嘅 style frame" | `style frame` | style frame keyword 優先 |
| "Kay 做 HKTB 嘅 name tag design" | `mograph` | Kay + design/name tag keyword |
| "Submit style frame 俾客（Max 做）" | `style frame` | style frame keyword 優先，唔加 mograph |
| "Kary 負責 HKTB PPM" | `Pre-Pro` | Kary = director member + PPM keyword |
| "Benjy 做 EMSD 嘅 Shooting D1" | `Shooting` | Benjy = director member + shoot keyword |
| "Kary — comment from client HSUHK" | `from client` | Kary = director member + from client keyword |
| "Benjy 做 Final Output J26002" | `final` | Benjy = director member + final keyword |
| "Kary 做 VO Recording" | `VO recording` | Kary = director member + VO keyword |
| "Comment from client on HKTB 2nd cut"（冇指定 member） | `from client` | keyword fallback |
| "Shoot D2 EMSD Railway"（冇指定 member） | `Shooting` | keyword fallback |

---

## Date Format

Trello API 用 **ISO 8601 UTC**：`'2026-04-15T00:00:00.000Z'`

用戶講香港日期（e.g. 「4月15號」）→ convert 成 `'2026-04-15T00:00:00.000Z'` 再傳入。

---

## Planyway 關係

Planyway 直接讀取 Trello card 嘅：
- **`start` + `due`** → Timeline bar 嘅開始/結束
- **`idMembers`** → Workload view 嘅人員分配
- **`idLabels`** → Color coding

Mugi 只要正確 set 呢三樣，Planyway 自動 reflect，**唔需要直接操作 Planyway**。

---

## Workflow Pattern（收到 Trello 相關 request）

```
1. fetch_board_meta()          → 取得最新 lists / members / labels
2. 理解 user request           → 係邊個 project（list）? 邊張 card? 做咩操作?
3. 搵 ID                       → meta['lists'][project] / meta['members'][username]
4. Call 對應 function          → create / update / checklist ops
5. 返回 confirmation           → card name + 操作摘要（唔使顯示 raw JSON）
```

---

## Error Handling

| 情況 | 處理方式 |
|------|---------|
| API 返回 `401` | credentials 問題，報告 Kary：「Trello credentials 有問題，請 check Zeabur Variables」 |
| API 返回 `404` | card / list 唔存在，問用戶確認 ID 或 project name |
| API 返回 `429` | rate limit（300 req/10s per key），自動 retry 一次（sleep 2s），仍失敗就報告 |
| 搵唔到 member | 列出 `meta['members_raw']` 嘅 username 俾用戶揀 |
| 搵唔到 list | 列出所有 project lists 俾用戶確認 project name |
