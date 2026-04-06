# DOF Tools & Systems

## 主要工具一覽

| 工具 | 類別 | 用途 |
|------|------|------|
| Google Calendar（DOF Internal） | 排期 | 共用 milestone calendar，全 team 可見 |
| Google Docs | 文件 | Video Flow working document（後期核心）、Script、Brief |
| Google Sheets | 資料 | DOF Current Job List、Master Job Log、Sales Projection |
| Google Drive | 儲存 | 素材、成品、文件 |
| Discord | 溝通 | 日常 team 溝通，Doji bot + Mugi agent 入口 |
| Slack | 溝通 | 部分對外溝通（視乎 project） |
| Dropbox / WeTransfer | 交付 | 成品交俾 Client |
| Vimeo | Archive | 成片 archive（Unlisted） |
| YouTube（Unlisted） | Cut review | 每個 cut 用 unlisted YouTube link 俾 Client 睇 |
| DaVinci Resolve / Premiere Pro | 後期剪接 | Editor 用 |
| After Effects | Motion Graphics | Motion Graphics 同事用 |

---

## 內部開發工具（DOF Internal Tools）

| 工具 | 狀態 | 功能 |
|------|------|------|
| Shotflow Studio | Production | Storyboard + Pitch Deck 生成器 |
| Production Tracker | On hold | 後期 task tracking（未全面落地） |
| Project Portal | In Development | 內部 ops portal — Quotation、Job 管理、Brief consolidation |
| DOF Planner | Production | Timeline → Google Calendar batch push |
| Doji（Discord Bot） | Production | Discord slash commands（`/callsheet`、`/timeline` 等） |
| Mugi（AI Agent） | Production | Discord 自然語言 AI assistant（你自己） |
| n8n Workflows | Production | 自動化（Script → Shot List、Job Kick Off 等） |

---

## Google Calendar 詳細

**Calendar Name:** DOF Internal
**Calendar ID:** `dreamoffish.hk@gmail.com`
**存取方式:** Service Account（`agent-mugi@gen-lang-client-0234599134.iam.gserviceaccount.com`）
**Credentials:** 存放喺 Zeabur Variable `GOOGLE_CALENDAR_CREDENTIALS`

**主要用途：**
- 記錄每個 project 嘅 milestones（Shoot、Cuts、Feedback、Final Output）
- 後期組睇住 calendar 安排工作量
- 全 team 追蹤排期

---

## Discord 結構

- **#ai-agent** — Mugi 嘅工作 channel，所有 Mugi 對話喺度發生
- Doji bot 同 Mugi agent 可以共存喺同一 channel
- Doji：slash command 觸發（`/callsheet` 等）
- Mugi：自然語言觸發（`@agent-Mugi 幫我搵 J26015 幾時交片`）

---

## Google Sheets 結構

| Sheet | 用途 | 負責人 |
|-------|------|--------|
| DOF Current Job List | 現有 jobs 狀態追蹤 | Kary + Sohling 維護 |
| Master Job Log | 已完成 jobs 記錄（backward-looking） | — |
| Sales Projection | 銷售預測（forward-looking） | — |

**重要：** Master Job Log 同 Sales Projection 係兩個獨立 sheets，唔合併。
