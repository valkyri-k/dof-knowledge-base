# Client Feedback Workflow

## Overview

Client feedback 係後期製作最花時間嘅環節之一。唔係因為改嘢難，而係因為**收集、整理、同追蹤** feedback 嘅過程亂。

---

## Client 點樣俾 Feedback

| 渠道 | 格式 | 常見程度 |
|------|------|----------|
| WhatsApp Group | 截圖 + 文字訊息（散亂）；ad hoc comment | 最常見 |
| Word document | Table format（timecode + 改動描述） | 常見 |
| Excel | Table format（較有結構） | 少數 client |
| PowerPoint | 每頁 capture 截圖 + 標註 | 偶爾 |
| Email | 文字描述 | 偶爾 |

Client 通常會 reference **timecode**（「1:30 嗰度要改」），但唔會對應到 script 或 video flow 嘅結構。

---

## 標準處理流程（Best Practice）

### 1. 建立 Working Document
導演根據 script / video flow 起一份 **Google Doc**，入面有 table：
- 時間 / Section
- Script / VO
- 畫面描述
- Graphics

### 2. 後期同事用嚟做 Working Document
- 自己分工（Keith 做呢段、Max 做嗰段）
- 做完 mark done
- 導演可以睇到進度

### 3. Client Feedback 到達
- 導演 **consolidate** 所有渠道嘅 feedback 入 Google Doc 相應嘅 row
- 每個 cut version 都 update 同一份 doc

### 4. Discord 分享
- Consolidated version share 去 **Discord**（tag 相關後期同事）
- Discord 用於所有 internal check（cut、design、reference 都喺度 share + 回覆）
- 避免口頭講完冇紀錄——trace back 容易、可以 tag 導演睇嘢

### 5. 導演主動 Catch 矛盾
- 導演喺 consolidation 過程中主動 catch 矛盾 / 問題
- 提早 flag 客人，避免做完先發現方向錯

---

## Feedback 嘅循環

```
Client feedback (各種渠道)
    ↓
導演 consolidate → Google Doc
    ↓
Share 去 Discord (tag 後期)
    ↓
後期修改 → Mark done
    ↓
導演 QC → Export next cut
    ↓
Upload YouTube (Unlisted) → Share link
    ↓
Client review → 下一輪 feedback
    ↓
重複直至 Picture Lock
```

---

## Pain Points

### 1. 人手 Mapping 費時
Client 嘅 feedback format 同 internal working doc 結構唔同。每次收到新嘅 feedback，都要逐條對返係邊段。

### 2. Timecode 唔穩定
- 前期冇 timecode（只有 script flow）
- First Cut 之後先有 timecode
- 每個 cut version 嘅 timecode 都唔同（加減咗 footage）
- Client 改 script（VO 要重錄）→ 連文字都變

### 3. 多版本散亂
Client 可能 WhatsApp 一堆、email 一份、再補充一份 Excel。同一個 cut 可能有 2–3 個渠道嘅 feedback 要 merge。

### 4. 唔係每個導演都做 Consolidation
有導演直接 forward client 嘅 Word / WhatsApp 訊息去 Discord，冇統一嘅 working document。後期同事要自己 trace 多份文件，容易漏。

---

## Mugi 可以點幫

Mugi 而家唔直接參與 feedback 處理流程，但可以：
- **回答 feedback workflow 問題**：「1st Cut 之後 feedback 通常幾耐返嚟？」→ 答：標準 3 working days
- **協助 Calendar update**：「J26015 嘅 Client 延遲咗 feedback，要推後一個禮拜」→ batch update 後續 milestones
- **提供 timeline context**：feedback 延遲對後續 milestone 嘅 ripple effect
