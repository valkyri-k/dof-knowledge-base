# DOF Job Lifecycle

## 概覽

一個 DOF job 由 client enquiry 到最終 close 嘅完整生命週期。

```
Client Enquiry → Ki logs job → Quotation → Client Confirm → Pre-Production → Shoot → Post → Delivery → Invoice → Close
```

---

## Stage 1: Client Enquiry

- **接收人：** 大部分搵 Ki；有時 Benjy / Sohling 先收到，pass 返俾 Ki
- **初步討論：** Monday Stand-up 會 informal 交流 job intel
- Ki 判斷 job type 同 assign 導演

### Job Assignment 路徑
| Job Type | 初步 Briefing | 導演 Assign |
|----------|-------------|------------|
| Regular（有拍攝） | Ki + Benjy | Benjy 帶導演去第一次 client meeting，或另行 brief |
| Post-only（純後期） | Ki + Sohling | Sohling 建議人選；Ki 有時直接 assign |

---

## Stage 2: Job Number + Quotation

### Job Number
- Format: `J` + 年份後兩位 + 3 位流水號（e.g. J26001, J26052）
- 由 Ki 手動 assign
- Ki 填入「(Ki) dof job 2026」sub-sheet

### Quotation Number
- Format: `Q` + 年份後兩位 + 3 位流水號（e.g. Q26051）
- Revision: Q26051R1 → Q26051R2（suffix versioning，唔跳號）
- 每次 revise 係新 document，唔係 overwrite
- Ki 人手出 quotation（email 形式）

### Retainer Projects（長期合約）
- 一份 master quotation covering 全 contract period
- 每月建獨立 Job Number（episode jobs）
- Episode jobs link 返 master job

---

## Stage 3: Master Job List Copy

**觸發條件（任一即可）：**
- Ki 已在 sub-sheet 填入 Job Number，或
- Ki 已發出 Quotation

**唔需要等** Client 確認 quotation。

**由誰做：** Kary + Sohling（人手 copy from Ki 嘅 sub-sheet）

**Copy 後預設 status：** `0_Pitching`

**時機：** 有空時隨時做；最遲係星期五（Monday Stand-up 前確保 list 係最新）

---

## Stage 4: Status 轉換

### `0_Pitching` → `1_Current`

**Standard path：**
- Client 正式書面確認 quotation → 轉 `1_Current` → 正式 kickstart

**Pragmatic path（提早轉）：**
- 回頭客（e.g. EMSD）口頭確認「呢件事會做」，雖然 quotation 仍在走審批流程
- Job 緊急，需要即刻 kickstart
- 目的：讓後期同事早點知道有嘢做，開始找 reference、做準備
- 核心判斷：「件事係咪真係會發生？」口頭確認 + 回頭客 = 足夠 signal

### `1_Current` → `Final Shared`
- 成品交付 + invoice 發出後更新
- 由 Kary / Sohling 喺 Monday Stand-up 更新

### 失敗 / 無回應
| 情況 | Remarks | 動作 |
|------|---------|------|
| Tender pitch 唔成功 | `Pitching failed` | Archive |
| 出完 quotation 一直無音訊 | `Client no reply` | Archive |

`0_Pitching` 可以長期存在，直到有明確結果才 archive。

---

## Monday Stand-up Meeting

- **時間：** 每週一早上 10:30am
- **延期：** 如大量同事外出拍攝或 Ki 放假 → 順延到星期二
- **用途：** 過 Master Job List，逐個 project check status + progress + blockers
- **參與者：** 全 team

### 星期五 Informal Sync
- Sohling / Kary 會喺 working day 完結前 informal 地 align（口頭，非正式 meeting）
- 確認有無新 entries 要 copy 入 Master Job List
- 留意有咩要喺 Monday 提出

---

## Master Job List Columns

| Column | 內容 |
|--------|------|
| Job Number | J26XXX |
| Cover | Project 封面圖 |
| Project Name | — |
| Brand | Client 品牌（e.g. DFI_Meadows、EMSD、CLP） |
| Client Contact | — |
| Status | `0_Pitching` / `1_Current` / `Final shared` / `Archived` / `Hold` |
| Director | 負責導演 |
| Post-Pro | 後期同事（可多人） |
| Current Progress | 導演每週更新 |
| Project Deadline | — |
| Output Versions | 交片格式、版本數 |
| Remarks | 備注 |
| Tag | 標籤（e.g. AI、Corporate） |

---

## Client 類型

DOF 服務嘅 client 有幾種類型，影響 project 嘅 dynamics：

| Client Type | 特徵 |
|-------------|------|
| Government | 靠招標，結果二元（贏 / 輸），流程較長較正式 |
| Corporate（大客回頭） | 關係型，相對穩定（e.g. CHANEL、CLP、EMSD） |
| NGO / Faith | 預算較少，週期較長 |
| 新客 | 完全未知，需要更多 alignment |
| Internal | DOF 自己嘅 project（portfolio、training） |

---

## Mugi 可以點幫

- **查詢 job status**：「J26015 而家咩狀態？」→ 搵 Calendar events 判斷（有冇 Shoot、有冇 1st Cut、最新 milestone 係咩）
- **理解 job lifecycle 問題**：「新 job 點開？」→ 解釋流程
- **協助 Calendar 管理**：Job status 變化時 → 幫手 update / 建立相應嘅 milestone events
