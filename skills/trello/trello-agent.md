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
