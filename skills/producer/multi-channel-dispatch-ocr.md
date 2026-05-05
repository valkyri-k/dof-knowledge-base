# Multi-channel Dispatch — OCR (v2)

> 呢份 file 只係**圖片 + tag Mugi**嘅 dispatch flow（v2）。
> 純 text input dispatch（v1）由 CLAUDE.md 嘅 `Dispatch decision` section + Resolution Rules 處理，唔需要 read 呢份 skill。

---

## Trigger

User 喺 Mugi home base channel（`#ai-agent-mugi`）post **image + tag `@agent-Mugi`**。可以有 caption（optional）。

**支援 1 image 講多個 job + 多個 task**——典型 use case 係手寫 note 一次過 assign 幾個 job 俾唔同 designer。每個 job → 獨立 resolve、獨立 message、fan out 落各自 target channel。

唔屬 v2 scope（reply 講明唔處理）：
- 圖片冇 task assignment 內容（純 reference image 等）

---

## Output rule（重要）

每個 target channel **只 send 一條 message**，內部要清楚講邊個 task 邊個負責：

- ❌ 唔好 spam：唔好同一個 channel 一個 task 一條 message
- ❌ 唔好 multi-user 時將 user tag 喺頂、task flat list（睇唔出邊個負責邊樣）
- ✅ Single-assignee → header `@user` + flat bullet
- ✅ Multi-assignee → 每 task `— @assignee(s)` 後綴

詳細 format 見 step 6。呢條 rule 同 v1 一致（CLAUDE.md `Outbound message rule` section），純 text input 都跟。

---

## Pipeline

```
image trigger
  → download image
  → Gemini Vision OCR (extract: list of job blocks, each with job_hint + assignees + tasks)
  → merge with caption (caption can override / supplement, surface in dry-run)
  → for each block:
      resolve job_hint via Resolution Rules → J# + target channel
      resolve assignees → Discord user IDs
      compose 1 dispatch message (multi-user tag + task list)
  → 🛑 dry-run preview in home base (列晒 N 個 dispatch)
  → wait user confirm
  → fan out: dispatch to N target channels
  → reply confirm 喺 home base (summary)
```

**Dry-run 係 mandatory**——OCR accuracy 唔可靠，必須 user verify 先 dispatch。Text input（v1）唔需要 dry-run，因為 user 自己打字已 verify。

---

## Step-by-step

### 1. Detect + download image

Discord trigger 帶 image attachment。Save 落 temp path（e.g. `/tmp/dispatch-ocr-<msg_id>.png`）。

### 2. OCR via Gemini Vision

Read `technical/gemini-api.md` 攞 boilerplate。

Prompt（hardcoded 入 skill execution）：

```
Extract task assignment info from this image. The image is likely a handwritten
note, screenshot, chat, email, or whiteboard about assigning tasks to team
members for one or more production jobs.

The image may contain MULTIPLE job blocks. Each block typically reads:
  <job hint>: <assignee> — <task 1>, <task 2>, ...
or
  <job hint> → <assignee> → <tasks>
or any visually grouped pattern indicating "this set of tasks belongs to this
job and is assigned to this person".

Extract a list of blocks. For each block:
- job_hint: project / job reference (string). Can be informal ("CLP HKMA",
  "快問快答", "Smart E"), formal ("J26065"), or empty if unclear.
- assignees: list of person names mentioned as task receivers
  (e.g. ["Sohling", "Max"]).
- tasks: list of task descriptions, each as a short phrase
  (e.g. ["Style frame", "Title x1", "Name tag x3"]).

Return JSON only, no prose. If a field is unclear, use empty string or empty list.
If text is illegible, mark uncertain text with "?" suffix (e.g. "Smart E?").

Schema:
{
  "blocks": [
    {"job_hint": "...", "assignees": [...], "tasks": [...]},
    ...
  ]
}

Example:
{
  "blocks": [
    {"job_hint": "快問快答", "assignees": ["Kay"], "tasks": ["Style frame", "Title x1", "Name tag x3"]},
    {"job_hint": "好E I", "assignees": ["Sohling"], "tasks": ["Style frame", "Title x1", "Divider x2"]}
  ]
}
```

Use `gemini-2.5-flash`、temperature `0.1`、`response_mime_type: "application/json"`.（Default per `technical/gemini-api.md`；2.0-flash 已 sunset 2026-06-01）

### 3. Merge with caption（if present）

Caption 通常會 cover 全圖（e.g.「呢張 note 係今日 design task」）或 override 個別 block（e.g.「第二個其實係 J26064」）。

| Caption 內容 | 處理 |
|---|---|
| 無 caption | 直接用 OCR `blocks` |
| Caption 講全圖 context（e.g.「今日 design task」） | 加入 dry-run preview 做 framing，唔改 block content |
| Caption 講 J# / project override 某 block | Caption 為準，replace 嗰個 block 嘅 `job_hint`，dry-run flag |
| Caption 加 assignee（e.g.「第一個 task Kay 同 Yik 一齊做」） | Append 落對應 block 嘅 assignees，dry-run flag |
| Caption 同 OCR 嚴重衝突（block count 唔對、task list 完全唔一樣） | Surface 喺 dry-run + ask clarify，**唔 dispatch** |

### 4. Resolve each block → J# + target channel

對 `blocks` 入面每一個 block，apply CLAUDE.md `Job Resolution` 5-layer rules（Project Name substring → Client cross-language → Aliases → Channel reverse-transliteration → Ambiguity clarify）。

| Block resolve 結果 | 行為 |
|---|---|
| Layer 1–4 unique match | 該 block 入 dispatch list |
| Layer 5 ambiguity（多 row match） | 該 block mark ambiguous，dry-run 入面列 candidates 問 clarify |
| Resolve 唔到 | 該 block mark unresolved，dry-run 入面 reply「block N OCR 攞到 `<job_hint>`，cache 搵唔到，confirm J#？」 |
| Match 到嘅 J# 係 no-channel-by-design | 該 block mark no-channel，dry-run 入面 flag「呢個 job 冇 Discord channel，唔可以 dispatch，會 skip」 |

**Partial dispatch 容許**：N 個 block 入面，只要至少一個 resolve 到，dry-run 都展示晒 N 個 + flag 邊個 ready / 邊個有問題。User 可以喺 confirm 時話「send 第 1、2，第 3 cancel」。

### 5. Resolve assignees → Discord user IDs

對每個 block 嘅 assignees，cross-ref `context/team-roles.md`（or job-list.md fallback）攞 Discord ID。

| Resolve 結果 | 行為 |
|---|---|
| 全部 resolve 到 | continue |
| 一啲 resolve 唔到 | dry-run 入面 flag「⚠️ `<name>` 搵唔到 Discord ID，會 plain text mention 唔 ping」並繼續 |

### 6. Compose dispatch message（per block）

每個 ready block compose **真正派出去 target channel** 嘅 message。睇個 block 入面 task↔assignee mapping 揀 format：

**Single-assignee block**（所有 task 都同一個 user）：

```
@user1

• <task 1>
• <task 2>

(from @<trigger user>'s image @ <timestamp>)
```

**Multi-assignee block**（task 分配俾唔同 user）：

```
• <task A> — @user1
• <task B> — @user1 @user2
• <task C> — @user2

(from @<trigger user>'s image @ <timestamp>)
```

規則：
- Single-assignee：第一行 `@user`（真 Discord mention，會 ping），隔一行 bullet list，bullet 唔重複 user name
- Multi-assignee：每 bullet `<task> — @assignee(s)`，多人共做同一 task 用 space 分開多個 @mention
- Multi-assignee 唔用 header mention line（bullet 入面 @mention 已經 ping）
- 1 個 task 都用 bullet（一致）
- 末行 attribution（trigger user 嘅 image timestamp）

### 7. Dry-run preview（home base reply）

**核心原則**：preview 係俾 trigger user 對 OCR result 啱唔啱，唔係 render 完整 message。
- ❌ 唔好出真 `@mention`（preview render 出嚟會 ping 同事，誤會係真 dispatch）
- ❌ 唔好 quote 完整 dispatch message（霸位 + 重複資訊）
- ❌ 唔好顯示 self-verify 過程（e.g. "Layer 2 client cross-language match"）
- ✅ 純文字 user name（"Katy" 唔好寫 `@Katy`）
- ✅ 一個 block 兩行：第一行 = OCR 攞到嘅 job hint → resolved channel + assignee；第二行 = task list

Compact format：

```
🛑 Dry-run — OCR 攞到 N 個 block，confirm 落 send

[1] 快問快答 → #j26066-emsd-quiz-of-farewell-party (Katy)
    Style frame, Title x1, Name tag x3

[2] 好E工 → #j26067-emsd-best-ce-award-competition-video (Sohling)
    Style frame, Title x1, Divider x2

「all」/「send」send 全部 ・「send 1, 2」揀指定 ・「cancel」abort
```

問題 block format（保持 compact）：

```
[3] ⚠️ Ambiguous: 「快問快答」→ J26063 / J26068，覆「block 3: J26063」揀
[4] ❓ Unresolved: 「Smart X」搵唔到 match，覆 J# 或「block 4: skip」
[5] 🚫 No channel: 「Cartier still shooting」(J26010) 冇 Discord channel，會 skip
[6] ⚠️ Assignee 「Tom」搵唔到 Discord ID，會 plain text mention 唔 ping
```

Caption note（如有）一行擺最尾：
```
ℹ️ Caption「今日 design task」已 apply 做 framing
ℹ️ Caption override block 2 job → J26064（OCR 出 "好E工" 但 caption 寫 J26064）
```

### 8. Wait for confirm

User reply：

| User reply | 行為 |
|---|---|
| "all" / "send" / "OK" / "yes" / "go" | proceed to step 9，send 所有 ready block，skip 有問題 block |
| "send 1, 3" / "send 1 同 3" / 列出 block 編號 | send 指定 block |
| "block N: <answer>" / 直接答 ambiguous | re-resolve 嗰個 block，再出 dry-run |
| "no" / "cancel" / "abort" / "stop" | reply「Cancelled」，end |
| 修改指示（e.g.「block 1 加 Max」「block 2 cancel」） | apply 修改，再出 dry-run |
| 唔 clear | reply「Confirm 下：send all / send N / 改 / cancel？」 |

### 9. Dispatch（fan out）

對 user 確認嘅每個 block，post 去 target channel。Sequential post（順 block 順序），每 post 完一個 log 短 status。如果某個 channel 唔喺 allowlist → 嗰個 fail，tag Kary 報告，繼續 dispatch 其他 block。

### 10. Reply confirm 喺 home base（summary）

```
✅ Dispatch 完成 (N/M)
- ✅ #j26065-clp-hkma-smart-e-living: tagged @Sohling
- ✅ #j26064-megaworks-...: tagged @Kay
- ⏭ block 2 skipped (ambiguous, 你揀咗 cancel)
- ❌ #j26068-...: 唔喺 allowlist，未 send（@kary check）
```

---

## OCR fallback behaviour（confirmed [[2026-05-05]]）

OCR confidence 低 / 完全讀唔到嗰陣，**reply 返 trigger user**，**唔 dispatch、唔估**：

| 情況 | Reply |
|---|---|
| OCR 完全 fail（image 唔係 text、太花、太暗、低 res、太 blur） | 「OCR 攞唔到任何 block — 可能張圖太 blur / 光線不足 / 字太細。可以**直接打字 dispatch**（e.g.「remind Sohling to do style frame for CLP HKMA」），或者**重影一張清楚啲嘅圖**再 tag 我」 |
| OCR 攞到 block 但全部 `job_hint` empty / unresolved | 一次過 reply 列出每個 block 嘅 OCR content + 問 user 逐個 confirm J#，或者改 text input |
| OCR 攞到 block 但部分字眼有 `?` uncertainty marker（block partial confidence） | 照行 dry-run，preview 入面保留 `?` marker 等 user 對；user 可以 confirm 或者改 text input |

核心原則：**OCR ≠ trusted input**。寧 ask 唔好估 partial dispatch。Reply 必須講清楚問題（blur / 太暗 / 字辨認唔到）+ 俾 fallback option（text input 或重影）。

## Dry-run preview format

現狀 plain text inline format（step 7）暫用，等 Sohling 實測完 feedback 再 iterate。Pilot 期間如果 user feedback 話冗 / 唔 readable，escalate 改 markdown code block 或者 attachment。

---

## 唔屬 OCR skill scope

呢啲行為由 CLAUDE.md / 其他 skill 處理，呢度唔重複：
- Resolution Rules 5-layer 細節 → CLAUDE.md `Job Resolution`
- Allowlist gate / outbound channel policy → CLAUDE.md `Channel Policy`
- 純 text input dispatch（v1）→ CLAUDE.md `Dispatch decision`
- Discord post 機制 → Discord plugin（`discord:post-message`）
