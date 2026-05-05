# Multi-channel Dispatch — OCR (v2)

> 呢份 file 只係**圖片 + tag Mugi**嘅 dispatch flow（v2）。
> 純 text input dispatch（v1）由 CLAUDE.md 嘅 `Dispatch decision` section + Resolution Rules 處理，唔需要 read 呢份 skill。

---

## Trigger

User 喺 Mugi home base channel（`#ai-agent-mugi`）post **image + tag `@agent-Mugi`**。可以有 caption（optional）。

唔屬 v2 scope（reply 講明唔處理）：
- 一張圖入面講多個 job（"1 image = 1 job" hard constraint）
- 圖片冇 task assignment 內容（純 reference image 等）

---

## Pipeline

```
image trigger
  → download image
  → Gemini Vision OCR (extract: job_hint, assignees, tasks)
  → merge with caption (caption wins on conflict, surface in dry-run)
  → resolve job_hint via Resolution Rules → J# + target channel
  → resolve assignees → Discord user IDs
  → compose dispatch message
  → 🛑 dry-run preview in home base
  → wait user confirm
  → dispatch to target channel
  → reply confirm 喺 home base
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
Extract task assignment info from this image. The image is likely a screenshot
of a chat, email, note, or whiteboard about assigning tasks to team members
for a specific production job.

Extract:
- job_hint: the project / job reference mentioned (string). Can be informal
  ("CLP HKMA", "Smart E", "HSUHK"), formal ("J26065"), or empty if unclear.
- assignees: list of person names mentioned as task receivers (e.g. ["Sohling", "Max"]).
- tasks: list of task descriptions, each as a short phrase (e.g. ["test the dispatch", "review draft"]).

Return JSON only, no prose. If a field is unclear, use empty string or empty list.

Example:
{"job_hint": "CLP HKMA", "assignees": ["Sohling"], "tasks": ["test the dispatch"]}
```

Use `gemini-2.0-flash`、temperature `0.1`、`response_mime_type: "application/json"`.

### 3. Merge with caption（if present）

如果 user 喺 image 之外有打 caption text：

| Caption 內容 | 處理 |
|---|---|
| 無 caption | 直接用 OCR 結果 |
| Caption 講 J# 或 project，OCR 都有 | Caption 為準（surface 喺 dry-run：「Caption 寫 X、OCR 出 Y，用 caption」） |
| Caption 講 assignee，OCR 冇 / 唔同 | Caption 為準 |
| Caption 補充 task detail，OCR 都有 | 兩個 merge（appended），surface 喺 dry-run |

### 4. Resolve job_hint → J# + target channel

Apply CLAUDE.md `Job Resolution` 5-layer rules（Project Name substring → Client cross-language → Aliases → Channel reverse-transliteration → Ambiguity clarify）。

| Resolve 結果 | 行為 |
|---|---|
| Layer 1–4 unique match | continue to step 5 |
| Layer 5 ambiguity（多 row match） | reply 列 candidates 問 clarify，**唔 dispatch、唔 dry-run**。User clarify 完返 step 4 |
| Resolve 唔到 | reply「OCR 攞到 `<job_hint>`，但 cache 搵唔到 match。Confirm 下個 J# 係邊個？」 |
| Match 到嘅 J# 係 no-channel-by-design | reply「呢個 job 冇 Discord channel，唔可以 dispatch」 |

### 5. Resolve assignees → Discord user IDs

Cross-ref `context/team-roles.md`（or job-list.md fallback）攞 Discord ID。

| Resolve 結果 | 行為 |
|---|---|
| 全部 resolve 到 | continue |
| 一啲 resolve 唔到 | dry-run 入面 flag「⚠️ `<name>` 搵唔到 Discord ID，會 plain text mention 唔 ping」並繼續 |

### 6. Compose dispatch message

Format（multi-user 在同一個 message 內 tag）：

```
@user1 @user2 — <task summary>

(from <trigger user>'s image @ <timestamp>)
```

Task summary 由 OCR `tasks` list 串成自然語句，分行 list 或 inline，視乎 task 數量（1–2 個 inline，3+ 用 bullet）。

### 7. Dry-run preview（home base reply）

Format：

```
🛑 Dry-run preview — confirm 落 send 落 channel

Target channel: #j26065-clp-hkma-smart-e-living
Tag: @Sohling
Message:
> @Sohling — test the dispatch
>
> (from @kary's image @ 2026-05-05 14:32)

OCR 結果：
- job_hint: "CLP HKMA" → resolved J26065 (Layer 2 client cross-language)
- assignees: ["Sohling"] → @Sohling
- tasks: ["test the dispatch"]

[caption conflict 段，如有]

Send 落？回「OK」/「send」/「yes」 confirm，「no」/「cancel」 abort，或者直接話我知改咩。
```

### 8. Wait for confirm

User reply：

| User reply | 行為 |
|---|---|
| "OK" / "send" / "yes" / "go" / "ok" | proceed to step 9 |
| "no" / "cancel" / "abort" / "stop" | reply「Cancelled」，end |
| 修改指示（e.g.「assignee 改埋 Max」） | re-compose、再出 dry-run preview，再等 confirm |
| 唔 clear | reply「Confirm 下：send / cancel / 改？」 |

### 9. Dispatch

Post 去 target channel。如果 channel 唔喺 allowlist → fail，tag Kary 報告（同 v1 一致）。

### 10. Reply confirm 喺 home base

```
✅ 已 tag @Sohling 喺 #j26065-clp-hkma-smart-e-living
```

---

## Open behavior（未定，pilot 期間 surface）

- OCR 完全 fail（image 唔係 text、太花、低 res）→ 暫定 reply「OCR 攞唔到任何資料，可以重 post 清晰啲嘅圖，或者直接打字 dispatch？」
- Caption 同 OCR 嚴重衝突（e.g. caption 講 job A、OCR 講 job B）→ 暫定一律 caption 為準 + dry-run flag，pilot 後再決定

---

## 唔屬 OCR skill scope

呢啲行為由 CLAUDE.md / 其他 skill 處理，呢度唔重複：
- Resolution Rules 5-layer 細節 → CLAUDE.md `Job Resolution`
- Allowlist gate / outbound channel policy → CLAUDE.md `Channel Policy`
- 純 text input dispatch（v1）→ CLAUDE.md `Dispatch decision`
- Discord post 機制 → Discord plugin（`discord:post-message`）
