# Google APIs — Credentials + Boilerplate

> 呢份 file 存放 Google Calendar + Google Drive / Docs 嘅 credentials 用法同 Python boilerplate。
> Mugi 需要 call API 時 read 呢度攞正確嘅 code pattern。

---

## Google Calendar（Service Account）

### 點解用 Service Account

Calendar 操作用 Service Account `agent-mugi@agent-mugi.iam.gserviceaccount.com`。DOF Internal Calendar 已 share 俾呢個 Service Account。

> ⚠️ **嚴禁用 `gcal_*` MCP tools 操作 Calendar。**
> Mugi 嘅 Claude Code instance 係以 Kary 嘅 claude.ai 帳號登入，cloud MCP 連住 Kary 嘅個人 Google 帳號。用 `gcal_*` tools → event 會顯示「Created by Kary」而唔係 Service Account——係錯的。
> **所有 Calendar 操作必須用 `GOOGLE_CALENDAR_CREDENTIALS` env var + 以下 boilerplate。**

### Credentials

存放喺環境變數 `GOOGLE_CALENDAR_CREDENTIALS`（JSON format, Service Account key）。

### Boilerplate

```python
import os, json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

creds_json = os.environ["GOOGLE_CALENDAR_CREDENTIALS"]
creds_dict = json.loads(creds_json)
creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=['https://www.googleapis.com/auth/calendar']
)
service = build('calendar', 'v3', credentials=creds)
```

如需安裝：`pip install google-api-python-client google-auth`

### 目標 Calendar

- Calendar ID: `dof.internal@gmail.com`
- HK Public Holidays Calendar: `en.hk#holiday@group.v.calendar.google.com`（read-only，用於 holiday check）

---

## Google Drive / Docs（OAuth2）

### 點解用 OAuth2 而唔係 Service Account

Service Account 喺 personal Gmail 嘅 Drive 冇 storage quota，無法 `files.copy` / `files.create`，會收 `Service Accounts do not have storage quota` error。所以 Drive / Docs 操作用 OAuth2，以 `dof.internal@gmail.com` 嘅身份做 API calls，由 dof.internal 自己嘅 Drive quota 處理。

（Calendar 唔受呢個限制，所以 Calendar 用 Service Account，Drive / Docs 用 OAuth2——兩套 credentials 並存，互唔干擾。）

### Credentials

OAuth2 credentials 存放喺以下環境變數：
- `GOOGLE_DRIVE_CLIENT_ID` — OAuth2 Client ID
- `GOOGLE_DRIVE_CLIENT_SECRET` — OAuth2 Client Secret
- `GOOGLE_DRIVE_REFRESH_TOKEN` — Long-lived refresh token（已 user-consented for dof.internal）
- `GOOGLE_DRIVE_DOCGEN_FOLDER_ID` — dof.internal Drive 入面 `doc-generation/` folder 嘅 ID，所有 Mugi 生成嘅 drafts 必須放呢度

### Boilerplate

```python
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials(
    token=None,
    refresh_token=os.environ["GOOGLE_DRIVE_REFRESH_TOKEN"],
    client_id=os.environ["GOOGLE_DRIVE_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_DRIVE_CLIENT_SECRET"],
    token_uri="https://oauth2.googleapis.com/token",
    scopes=[
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)

drive_service = build("drive", "v3", credentials=creds)
docs_service = build("docs", "v1", credentials=creds)
```

如需安裝：`pip install google-api-python-client google-auth google-auth-oauthlib`

### 操作範圍

- 身份：`dof.internal@gmail.com`
- 範圍：成個 dof.internal Drive（root + 所有 sub-folders + share 畀 dof.internal 嘅 files）
- 權限：full read/write（drive scope）
- **冇 sandbox folder**——Mugi 可以操作整個 Drive，包括幫手 search / read / organize 舊 project files

### Drive Folder Convention（固定，唔好擅自改）

dof.internal Drive root 入面有三個 reserved folder：

| Folder | 用途 | Mugi 點用 |
|--------|------|----------|
| `Templates` | 存放所有 document templates（命名：`[DocType]_Template`） | 生成新 document 時 copy template |
| `doc-generation` | Mugi 生成嘅 drafts 全部放呢度（避免撈埋 `Templates/`） | `files.copy` 時 `parents` 指去呢個 folder ID（讀 `GOOGLE_DRIVE_DOCGEN_FOLDER_ID` env var） |
| `Archive` | 存放 archived files | 用戶要「移除」file 時 move 過去（唔 delete） |

**Lookup rule：**
- `Templates` / `Archive`：by name query（見下）
- `doc-generation`：by folder ID（`GOOGLE_DRIVE_DOCGEN_FOLDER_ID` env var），**唔好** by name query，避免 drift

**Name-based lookup query（exact match，大小寫敏感）：**
```
name = 'Templates' and mimeType = 'application/vnd.google-apps.folder' and 'root' in parents and trashed = false
```

揾唔到 → 唔好猜，直接報錯：「dof.internal Drive root 揾唔到 `Templates` folder。請通知 Kary check folder 係咪 rename 咗或者 move 咗。」

`GOOGLE_DRIVE_DOCGEN_FOLDER_ID` 未 set 或者 folder ID 無效 → 停低唔執行，tag Kary。**唔好** fallback 去 Drive root，會造成 Templates folder pollution。

### Drive 操作原則

1. **Read 操作**：唔需要每次問 permission，但要透明——簡短講你想 read 邊個 file / folder 同點解
2. **Write 操作（create / copy / rename / move）**：先列出將要做嘅嘢（file 名 + location），等用戶 confirm 先執行
3. **Delete / Archive 操作**：**永遠唔好 delete file，永遠唔好 move to trash**，除非用戶明確講「delete [filename]」。「移除」= **move 去 `Archive` folder**（用 Drive API `files.update` 改 parent）
4. **Modify existing file**：prefer create copy 然後改 copy，唔好直接改 original file，除非用戶明確要改 in place
5. **Cross-account file**：如果 file owner 係其他人，dof.internal 只係 editor，modify 嗰陣 ownership 唔變
6. **錯誤透明**：API call 失敗就直接報錯 + 具體 error message，唔好假裝成功
