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

每個 target channel **只 send 一條 message**，message 入面 tag 該 channel 對應 job 嘅所有 assignees + 列晒所有 task。
- ❌ 唔好 spam：唔好同一個 channel 一個 task 一條 message
- ✅ 一個 channel = 一個 message，內含 multi-user tag + multi-task list

呢條 rule 同 v1 一致，純 text input 都跟。

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

Use `gemini-2.0-flash`、temperature `0.1`、`response_mime_type: "application/json"`.

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

每個 ready block compose 一條 message。Format：

```
@user1 @user2 — <task summary>

(from @<trigger user>'s image @ <timestamp>)
```

Task summary 規則：
- 1–2 個 task → inline，逗號分隔（e.g.「Style frame, Title x1」）
- 3+ 個 task → bullet list

### 7. Dry-run preview（home base reply）

列晒所有 block，ready 嘅 + 有問題嘅都列。Format：

```
🛑 Dry-run preview — OCR 攞到 N 個 job block，confirm 落 send

[1] ✅ Ready
Target: #j26065-clp-hkma-smart-e-living
Tag: @Sohling
Message:
> @Sohling — Style frame, Title x1, Divider x2
>
> (from @kary's image @ 2026-05-05 14:32)
OCR: "好E I" → resolved J26065 (Layer 2 client cross-language)

[2] ⚠️ Ambiguous
OCR: "快問快答" → match 到 2 個 job：
  - J26063 快問快答 EP1
  - J26068 快問快答 EP2
Reply 邊個（block 2: J26063 / J26068）

[3] ✅ Ready
Target: #j26064-megaworks-...
Tag: @Kay
Message:
> @Kay — Style frame
>
> (from @kary's image @ 2026-05-05 14:32)

[caption notes，如有]

Confirm 點？
- 「all」/「send」/「OK」 → send 全部 ready 嘅 block，跳過有問題嘅
- 「send 1, 3」 → 揀指定 block send
- 「block 2: J26063」 → resolve 緊 ambiguous
- 「cancel」 → 全部 abort
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

## Open behavior（未定，pilot 期間 surface）

- OCR 完全 fail（image 唔係 text、太花、低 res）→ 暫定 reply「OCR 攞唔到任何 block，可以重 post 清晰啲嘅圖，或者直接打字 dispatch？」
- OCR 攞到 block 但全部 job_hint empty / 全部 unresolved → 暫定一次過 reply 列出 block content + 問 user 逐個 confirm J#

---

## 唔屬 OCR skill scope

呢啲行為由 CLAUDE.md / 其他 skill 處理，呢度唔重複：
- Resolution Rules 5-layer 細節 → CLAUDE.md `Job Resolution`
- Allowlist gate / outbound channel policy → CLAUDE.md `Channel Policy`
- 純 text input dispatch（v1）→ CLAUDE.md `Dispatch decision`
- Discord post 機制 → Discord plugin（`discord:post-message`）
