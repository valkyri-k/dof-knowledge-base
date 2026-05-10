# Per-Job Activity Tracking + Project Overview Schema

> Extracted from CLAUDE.md on [[2026-05-10]] to reduce context-bloat warning.
> **Read this full file when**:
> - 喺 per-job channel 收 message（channel ID match `context/job-list.md` Active Jobs row）→ 並行寫 user activity + per-job activity log
> - 收到 `/project-overview` skill / 要 derive Project Overview section
>
> Per-job files 永遠用 absolute path `/home/node/kb/activity/jobs/<channel-name>.md`。

---

## Per-Job Activity Tracking

> **並行規則（HARD RULE）**：當 channel ID match 到 `context/job-list.md` Active Jobs 一行 → user activity log（`<username>.md`）+ per-job activity log（`activity/jobs/<channel-name>.md`）**兩個都要寫**。Per-job log 唔係取代 user log，係**並行**——`<username>.md` 係 per-user master timeline，per-job log 係 channel-scoped slice，兩邊都要 capture 同一件事，自然會 duplicate，呢個係 design intention。

User 喺 per-job channel interact 嗰陣，將 interaction summary append 去 `/home/node/kb/activity/jobs/<channel-name>.md`。Purpose：clear session 後 future-Mugi 入到 channel 即刻有 baseline understanding，唔需要 user 每次重複講 job background。

**Channel match：** 用 inbound channel envelope 嘅 `parent_id`（如果有）— 否則 fall back `chat_id` — 去對 `context/job-list.md` Active Jobs table。Match 到 → 寫 per-job log。Match 唔到（DM / general / `#ai-agent` / no-channel-by-design jobs）→ 唔寫，照常規 user activity log。

**Thread handling（重要）：** Thread message 嘅 envelope 會 carry `parent_id`（parent channel ID）+ `parent_name`（parent channel name）。**Lookup key 永遠用 `parent_id` when present**，唔好用 `chat_id`（thread 自己嘅 ID）。Thread match 到 → 寫入 parent 嘅 per-job file（`activity/jobs/<parent-channel-name>.md`），thread 內所有 iteration 都歸入同一個 job log。Entry 入面注明 thread name / topic（例：「— in thread: timeline-v2」）方便日後追溯。

> **若果 envelope 冇 `parent_id` 但你身處 thread**（罕見，e.g. plugin 未 patch），即停手寫 per-job log，照寫 user activity log，並 surface 一句「thread parent 認唔到，per-job log skipped」俾用戶。**唔好估**亦唔好寫去 thread ID 嘅檔名。

**Filename：** 取 `job-list.md` row 嘅 `Discord Channel Name` column verbatim，去掉開頭 `#`。例：`#j26016_hsuhk-student-excellence-video-series` → `j26016_hsuhk-student-excellence-video-series.md`。**唔做** underscore→hyphen / case normalization——Channel Name 本身點 spell 就點 spell。

**File 唔存在 → scaffold + 即場 append entry（atomic）：**

```markdown
---
job_no: <Job No>
client: <Client>
project_name: <Project Name>
director: <Director>
discord_channel_id: <Channel ID>
discord_channel_name: <Channel Name>
created: [[YYYY-MM-DD]]
last_updated: [[YYYY-MM-DD]]
---

# <Job No> — <Project Name>

## Job Context
<!-- Reserved for Master Job Log integration. 暫時留空，唔寫。 -->

## Interaction Log
```

Frontmatter 全部 column 抄自 `job-list.md` row。**Scaffold 同第一個 entry 必須喺同一個 Write call 完成**——唔可以 create skeleton file 然後 leave `## Interaction Log` 空（否則睇似 Mugi 認到 job 但冇做嘢）。冇 entry 可以寫 → 唔好建 file，照寫 user activity log 就算。

**Entry format：**

```
### [[YYYY-MM-DD]] <morning/afternoon/evening> — <topic>
- **Kary 問**：<1-2 行 summary>
- **Mugi 做**：<1-2 行 outcome / decision>
- **Followup**：<pending / waiting on，如有；冇就 omit>
```

Cross-ref 如有相關 `gap-log.md` / `kary-dev-log.md` entry，加一行 `→ gap-log [[YYYY-MM-DD]] entry` / `→ dev-log [[YYYY-MM-DD]] entry`。

**Log-worthiness（HARD RULE）：** 喺 thread / per-job channel **每一次同 user 嘅互動**都要 append 一行 Interaction Log entry——包括 identification reply（「呢個係 J26071」）、status query reply、quick lookup、dispatch confirmation。短互動寫短 entry（一句 Kary 問 + 一句 Mugi 答，Followup omit），但**唔可以唔寫**。完整 audit trail > log 簡潔。

唯一例外：repeated noise（同一 thread 連續 2+ 條完全相同 query），可以 collapse 成一行「× N 次」。

**唔即時 push：** Per-job log 嘅 `git add` + `commit` + `push` 跟 user activity log 一齊喺 **Pre-Clear Sequence** single commit 處理（同 `kary-dev-log.md` / `gap-log.md` 一個 commit）。每次 interact 唔即時 push。

**File 寫入永遠用 absolute path** `/home/node/kb/activity/jobs/<filename>.md`（同 user activity log 嘅 path rule 一致）。

**同其他 log 嘅關係：** Per-job log 係**補充**，唔取代 `<username>.md` user activity log。Per-user 仍然係 master timeline，per-job 係 channel-scoped slice。

---

## Per-Job Project Overview Section

> Schema locked [[2026-05-10]] via J26071 pilot（Phase A manual draft）。Source idea：[[mugi-owned-project-overview-skill]]、[[per-job-project-overview-section]]。

`## Project Overview` section 由 `skills/producer/project-overview.md` skill 寫入（**唔係** 預設 scaffold 一部分）。Section 位置：喺 `# <Job No> — <Project Name>` 標題下面、`## Job Context` 上面。

### Section structure

```markdown
## Project Overview
> Last-derived: [[YYYY-MM-DD]]
> Source: <Mugi /project-overview pilot manual draft | Phase B Portal push | etc.> [[YYYY-MM-DD]]
> Generated from: <brief / quotation / SOW / meeting minutes>

[FULL verbatim Project Overview content — from Kary's chat `dof-project-overview` skill output 或 Phase B Portal-generated draft。**唔做 summary**。]

### Hard Deadlines
[Immutable external dates。Mugi planning / suggestion 嘅 hard boundary。]

### Project Constraints
[Non-negotiable project limits — license / hardware / structural / timeline-affecting。]

### Working Timeline
> Source of truth = Google Calendar（job_no `JXXXXX` 對應 events）。下面只係 latest snapshot reference，唔係 SoT。
> Last synced to Calendar: [[YYYY-MM-DD]] — N events
[Tentative milestones。]

### Current Phase
[Manual-stated only。Overwrite，唔留 history。]

### Open Issues
[Table format：# / Issue / Owner / Resolve by。]

### Recent Material Decisions
[Bullet list with [[YYYY-MM-DD]] prefix。]
```

### Sub-section update modes (HARD RULE)

| Sub-section | 性質 | Update mode | SoT |
|---|---|---|---|
| (verbatim PO) | Derived from source | Overwrite on full re-derive | Job note |
| Hard Deadlines | Immutable external | Append-only；change 要明 surface | Job note |
| Project Constraints | Immutable structural | Append；resolve 嗰陣 mark | Job note |
| Working Timeline | Tentative milestones | Snapshot only；Calendar push 後由 plan-timeline skill auto-update | **Google Calendar** |
| Current Phase | Ephemeral state | **Overwrite，manual-stated only**；唔自動 derive、唔留 history | Job note (minimal) |
| Open Issues | State + history mix | Append；resolve 嗰陣 mark / remove | Job note |
| Recent Material Decisions | Event log | Append-only | Job note |

**Current Phase HARD RULE：** 只寫 user explicitly-stated context（e.g.「Script 喺 Kary draft 緊」、「等緊 Buttons confirm VO direction」）。Auto-derive from date + Working Timeline 嘅嘢**唔寫 file**，問嗰陣即 derive。Reduces stale risk。

### Mandatory extraction (when running `/project-overview` skill)

Skill 必須 extract 兩類 immutable knowledge — extract 唔到就主動問 user，**用具象化 examples，唔用 abstract term**。

**A. Hard Deadlines —** 問法 example：「呢個 job 有冇 hard deadline？即係話，呢個日期一定唔可以改。常見例子：影片要喺某個 event 入面播（event date 已定）、Award submission deadline、客戶已 announce 嘅 launch date。導演 brief 階段通常知道但唔一定寫喺 PO，請列出嚟（日期 + 原因）。冇就 confirm 一聲。」

**B. Project Constraints（影響 timeline 嘅流程 / 結構限制）—** 問法 example：「除咗 hard deadline 之外，有冇其他嘢會影響 timeline？常見要 check：
1. Client 內部 approval rounds — 客戶要過幾多輪 senior approval？每輪 turnaround 幾耐？
2. 特別事項影響製作時間（external party dependencies、talent availability window）
3. Shooting date — lock 死、彈性、定未定？
4. Hardware / spec lock（display 設備 / aspect ratio / colour space）
5. License 要求（buyout / royalty-free 限制）」

呢條 list 唔係 exhaustive — 係 prompting categories。User 補充 fall outside list 嘅嘢照收。

### Calendar sync follow-up

當 user confirm 已將 timeline push 上 Google Calendar 之後，**plan-timeline skill 必須 auto-update** Working Timeline section：寫 `Last synced to Calendar: [[YYYY-MM-DD]]` + 列 N events snapshot + 強調 SoT = Calendar。唔需要 user 再叫一次。

### Edit safety

寫入 `## Project Overview` 嗰陣**唔可以**誤 touch `## Job Context` / `## Interaction Log`。每個 sub-section 改動只 touch 對應範圍。Re-run skill = overwrite 整個 `## Project Overview` section（git history 做 audit trail）；個別 sub-section update = surgical edit。

