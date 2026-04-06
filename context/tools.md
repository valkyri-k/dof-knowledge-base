# DOF Tools & Systems

## 主要工具一覽

| 工具 | 類別 | 用途 |
|------|------|------|
| Google Calendar（DOF Internal） | 排期 | 共用 milestone calendar，全 team 可見 |
| Google Docs | 文件 | Video Flow working document（後期核心）、Script、Brief |
| Google Sheets | 資料 | DOF Current Job List、Master Job Log、Sales Projection |
| Google Drive | 儲存 | 素材、成品、同 client 共享嘅 folder |
| Discord | 溝通 | Internal team 日常溝通，Doji bot + Mugi agent 入口 |
| WhatsApp | 溝通 | Client 溝通（日常 coordination + share edits）—— client 嘅主要渠道 |
| Email | 溝通 | Official 文件（quotation、script confirm）—— black and white 紀錄 |
| Dropbox / WeTransfer | 交付 | 成品交俾 Client |
| Vimeo | Archive | 成片 archive（Unlisted） |
| YouTube（Unlisted） | Cut review | 每個 cut 用 unlisted YouTube link 俾 Client 睇 |
| DaVinci Resolve / Premiere Pro | 後期剪接 | Editor 用 |
| After Effects | Motion Graphics | Motion Graphics 同事用 |

---

## Discord 結構

### 用途
- Internal team 日常溝通（2026 年由 Slack 遷移過嚟）
- Doji bot（slash commands）同 Mugi agent（自然語言）共存
- 所有 internal check（cut、design、reference）都喺度 share + 回覆——避免口頭無紀錄

### Channel 命名規則
| 階段 | 命名 | 例子 |
|------|------|------|
| Pitching 階段 | `Pitching_[Job No.]_[Project Title]` | `Pitching_J26015_HSUHK_Student` |
| Confirm 後 | `[Job No.]_[Project Title]`（去掉 Pitching prefix） | `J26015_HSUHK_Student` |

### Channel 管理
- **誰開：** 主要由 Kary + Sohling 負責
- **幾時開：** 一般等 confirm 後；但如需 pitching / tender → 提早開（需分享 client 材料、搵 reference）
- **Project 完結後：** Channel 搬去另一個 category（唔 archive、唔改名）
- **權限：** 所有人都可以開 channel

### Mugi 嘅位置
- **`#ai-agent`** channel — Mugi 嘅工作 channel
- Mugi 用 quote-reply 回覆（Discord plugin 唔支援 create thread）
- Doji 用 slash commands（`/callsheet`、`/timeline` 等），Mugi 用自然語言（`@agent-Mugi ...`）

---

## WhatsApp 規則

- 每個 project 開一個 WhatsApp group（DOF + client）
- **Ki 必須喺 WhatsApp group + email loop 入面**（公司規定）
- Share edits（cut）通常透過 WhatsApp（比較快）
- Official 嘢（quotation、script confirm）用 email 做 black and white 紀錄
- 兩邊都 send 最穩陣

---

## Internal Server（File Storage）

### Server Job Folder
- **命名：** `[Job No.]_[Project Title]`（固定，唔會因 pitching/confirm 改名）
- **內容：** 所有 materials、後期 graphics、working files
- **Project 完結後：** Folder 永遠留喺原位
- Server 空間有限（公司自建），正考慮將舊 project 定期 upload 去雲端

---

## Google Sheets 結構

| Sheet | 用途 | 負責人 |
|-------|------|--------|
| (Ki) dof job 2026 | Ki 嘅 admin record — quotation + invoice tracking | Ki 填，同事唔直接改 |
| Master Job List | 日常 project management working doc，Monday Stand-up 嘅 live reference | Kary + Sohling 維護 |
| Sales Projection | 銷售預測（forward-looking） | — |

**重要：** Master Job Log（backward-looking 事實記錄）同 Sales Projection（forward-looking 預測）係兩個**獨立** sheets，唔合併。

---

## Google Calendar 詳細

**Calendar Name:** DOF Internal
**Calendar ID:** `dof.internal@gmail.com`
**存取方式:** Service Account（`agent-mugi@gen-lang-client-0234599134.iam.gserviceaccount.com`）
**Credentials:** 存放喺 Zeabur Variable `GOOGLE_CALENDAR_CREDENTIALS`

**主要用途：**
- 記錄每個 project 嘅 milestones（Shoot、Cuts、Feedback、Final Output）
- 後期組睇住 calendar 安排工作量
- 全 team 追蹤排期

---

## DOF Internal Tools 關係圖

DOF 有一套自建工具，各有定位，互相唔重疊：

```
Project Portal (Airtable + UI)          DOF Planner
  ├── 新 job 建立（structured form）      ├── Timeline → Calendar batch push
  ├── Quotation 管理                     └── 一次過推所有 milestone
  └── Master Job Log
          │
          ▼
   Google Calendar (DOF Internal)
     ├── 人手直接操作 ◄──── 所有同事都可以
     ├── DOF Planner batch push ◄──── 開 job 時用
     └── Mugi 自然語言操作 ◄──── Discord 入面用
          │
          ▼
      Doji (Discord Bot)              Mugi (AI Agent)
        ├── Slash commands              ├── 自然語言 Calendar 操作
        ├── /callsheet                  ├── Production timeline 查詢
        ├── /timeline                   ├── DOF workflow 問題
        └── AI summary                  └── Naming convention enforcement
```

### 分工原則
| 操作 | 用邊個 |
|------|--------|
| 新 job 建立 | **必須經 Project Portal form**（structured input，database source of truth） |
| 一次過推所有 milestone 上 Calendar | **DOF Planner**（batch push） |
| 查詢 / 更新 / 搬個別 Calendar event | **Mugi** 或人手 |
| Slash command 觸發嘅動作 | **Doji** |
| 自由格式問題 | **Mugi** |

### 各工具狀態

| 工具 | 狀態 | 平台 |
|------|------|------|
| Shotflow Studio | ✅ Production | Vercel + Neon |
| Production Tracker | ⏸️ On Hold | Vercel + Neon |
| Project Portal | 🔄 In Dev | Vercel + Airtable |
| Doji（Discord Bot） | ✅ Production | Railway |
| n8n Workflows | 🔄 In Dev | Railway |
| DOF Planner | 🟡 Alpha | Railway |
| Mugi（AI Agent） | 🔄 Testing | Zeabur |

---

## AI Tools

| Tool | 用途 | 用喺邊 |
|------|------|--------|
| Gemini 2.0 Flash | Feedback parsing | Production Tracker |
| Gemini 3.1 Flash | Image generation | Shotflow Studio |
| Gemini (via n8n) | Script → shot list、summary | n8n workflows |
| Gemini (via Discord Bot) | AI summary、resource generation | Doji |
| Claude (Opus / Sonnet) | Development、strategy、Mugi runtime | All projects + Mugi |
