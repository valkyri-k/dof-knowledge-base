# DOF Production Pipeline

## 完整流程

```
Client Brief → Concept / Script → Script Breakdown → Pitch Deck → Call Sheet → Shoot → Post-Production → Delivery
```

---

## Pre-Production 階段

| 階段 | 產出 | 工具 |
|------|------|------|
| Client Brief | Brief document | Client 提供（各種格式：email、WhatsApp、PDF） |
| Concept / Script | Script document | Google Docs |
| Script Breakdown | Shot list、talent list、location list | Google Docs / Sheets |
| Pitch Deck / Storyboard | 客戶提案文件 | Shotflow Studio / Canva |
| Call Sheet | 拍攝日程表 | Google Docs / Sheets |

### Pitching 分類
| 情境 | 做法 |
|------|------|
| 回頭客 / simple job | 簡單 creative deck（Canva template） |
| 新客 / tender | 正式 technical proposal |
| 冇 pitching 需要 | 直接入 pre-production |

### Shooting
DOF 冇 in-house shooting crew，全部 outsource freelancers。導演有慣用嘅 freelancers；新導演可帶自己嘅。

---

## Pre-Production Timeline Logic（由 Shooting 倒推）

呢個係 DOF 標準 pitching deck 入面嘅固定 timeline template，統一各 project 嘅排期格式。實際排期由導演按 project 調整。

### Script → Shooting 主線

| Step | Working Days | 備註 |
|------|-------------|------|
| DOF 撰寫 Script（如需要） | 5 wd | 只有 DOF 寫 script 時計算 |
| Client Confirm Script | 2–3 wd | Client 提供 script 嘅話亦預留 confirm 時間 |
| 準備 Video Flow + Graphics Reference | 5–6 wd | 同步交 graphics reference |
| Client FB on Video Flow + Ref | 2–3 wd | |
| Confirm → Shooting | 3–4 wd | |

### Style Frame（平行線，可同 shooting overlap）

| Step | Working Days | 備註 |
|------|-------------|------|
| Submit Style Frame | 4–5 wd after Confirm Ref | |
| Client FB on Style Frame | 2–3 wd | |
| Confirm Style Frame | 理想 1st Cut 前 4–5 wd | 如果趕唔切就同 1st Cut 一齊交 |

**Style Frame Conditional Flow：**
- 理想：Style Frame 喺 1st Cut 之前 confirm → 1st Cut 已有正式 still graphics
- 趕唔切：Style Frame 同 1st Cut 一齊交 → 1st Cut 用 placeholder 假字 → 2nd Cut 先有 still graphics → 3rd Cut 先有 motion
- 呢個 delay 會推遲成個後期 pipeline 一個 cycle

---

## Post-Production 標準工時

### 四個 Tier（由鬆到緊）

| | Tier 1（標準） | Tier 2（內部壓縮） | Tier 3（客方壓縮） | Tier 4（終極壓縮） |
|---|---|---|---|---|
| 1st Cut（with still GFX） | 5 wd | 4 wd | 4 wd | 4 wd |
| Client Feedback | 3 wd | 2 wd | 1 wd | 1 wd |
| 2nd Cut（with animated GFX） | 3–5 wd | 3 wd | 3 wd | 3 wd |
| Client Feedback | 3 wd | 2 wd | 1 wd | 1 wd |
| 3rd Cut | 3 wd | 2 wd | 2 wd | ❌ 取消 |
| Client Feedback | 3 wd | 2 wd | 1 wd | ❌ 取消 |
| VO Recording buffer | 2–3 wd | 2 wd | 2 wd | 2 wd |
| Color + Sound | 2 wd | 1 wd | 1 wd | 1 wd |

**整個後期大約一個月（Tier 1）。**

**壓縮原則：** Plan 嘅時候一定攞鬆啲留 buffer，萬一客方突然有壓榨或者變動。極端 case 由導演自己處理。

---

## Post-Production 標準流程

### Cut 版本定義

| 版本 | 內容 |
|------|------|
| 1st Cut | Still graphics（靜態字卡）；或 placeholder「假字」+ AI guidetrack VO |
| 2nd Cut | Animated motion graphics + fine-tune color + SFX |
| 3rd Cut+ | 逐步收窄改動，直至 Picture Lock |
| After Picture Lock | VO recording（如需要）→ Subtitle → Final color grading → Audio mixing → Final Cut |

### Cut Submit 流程（每個 cut 一致）
1. Editor export 片
2. Upload **YouTube（Unlisted）**
3. Share link 俾 Client（WhatsApp + Email）
4. Client review → 提供 feedback
5. 導演整理 feedback → update Video Flow document（見 `client-feedback-workflow.md`）

### Client Feedback Stages
- **1st Cut + 2nd Cut**：通常係 Working Level（同 Client 接頭人 align）
- **2nd Cut 或 3rd Cut**：Client 可能拿去做 **Senior Approval**（額外需要幾日至一個禮拜）
- Senior Approval 時間視乎 Client，導演手動調整 timeline
- VO Recording 需要預 2–3 working days buffer（約 talent + studio），實際錄音只需一日

---

## 後期分工

| 角色 | 人 | 職責 |
|------|-----|------|
| Editor | Yik、Katy | Video editing（剪接、footage 組合、初步 color） |
| Motion Graphics | Keith、Max | 字卡、lower thirds、dividers、2D animation、infographics |
| Graphic Design | Kay（temporary） | KV、poster、banner（static graphic） |
| Post-Pro Supervisor | Sohling | 後期統籌、分工、QC、同導演對接 |

- Editor 同 Motion Graphics 用同一份 Google Doc 做 working document，各自睇自己負責嘅部分
- 做完喺 Google Doc mark done，導演可以睇到進度

---

## Video Flow Document（後期核心 working document）

後期嘅 **single source of truth**。導演根據 script 建立，後期同事對住做。

**典型 columns：**
| Column | 內容 |
|--------|------|
| Section / Timecode | Part name 或 timecode range |
| Script / VO | 旁白、對白 |
| Visual Description | 畫面描述、shot type |
| Screenshot REF | 參考圖、screencap |
| Graphics | 字卡、on-screen text 描述 |

**重點：**
- 前期冇 timecode（靠 script flow）
- First Cut 之後加入 timecode
- 每個 cut version 嘅 timecode 都唔同（加減咗 footage）
- Client 改 script → document 要跟住改

---

## Google Calendar 排期

DOF 有共用 **DOF Internal** Google Calendar，所有同事可見。

### 用途
- 記錄每個 project 嘅 milestones
- 後期組（Sohling、Max、Keith、Yik、Katy）睇住 calendar 安排工作量
- 全 team 追蹤排期

### 標準 Milestone Set
`Shoot` → `1st Cut` → `Client FB 1` → `2nd Cut` → `Client FB 2` → `3rd Cut` → `Picture Lock` → `Final Output`

Milestone 命名跟 `naming-conventions.md` 嘅規定。

### 點解 Calendar 咁重要
- 後期組**唯一知道幾時有嘢做**嘅渠道——calendar 唔齊全，佢哋無法評估工作量
- 一次過推十幾個 milestone 上 calendar 係大工作量 → 導致有導演唔想做
- 任何排期改動如果唔 update calendar → 後期睇到嘅係過時資訊
- 呢啲 pain points 正正係 DOF Planner（batch push）同 Mugi（自然語言管理）想解決嘅

### 操作原則（2026-04 確認）
- **就算 tentative 都要 mark**——Plan 完後客人未 confirm，時間一 plan 好就要擺入 calendar
- 改咗期**必須 update**
- Calendar event 建立 / 修改 = 混合模式：人手直接操作 OR 經 Mugi，兩者並行
- Naming convention enforcement → 靠 team agreement。無論人手定 agent 操作都要跟同一個 convention

---

## 最終交付

| 步驟 | 工具 |
|------|------|
| 導演 QC | — |
| Upload 俾 Client | Dropbox / WeTransfer / Client shared drive |
| Archive | Vimeo（Unlisted）—— 目前 ad hoc，方向：導演 share final 時同步上 Vimeo |
| Invoice + Close Job | Google Sheets（DOF Current Job List），Status → Final Shared |

---

## Subtitle

- 視乎 quotation 包唔包
- Client 提供 script 嘅片通常由 client 提供 subtitle
- 有時需要中文 + 英文版本
- 通常最後先上（VO recording 後 duration 會有少少變）
