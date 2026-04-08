# Gap Log — User Requests & Capability Gaps

Mugi 自動記錄「做唔到」或「需要跟進」嘅 user request。Kary 定期 review，決定行動。

**Type 定義：**
- `capability-gap` — 缺乏 tool / API / integration
- `needs-discussion` — 需要 Kary 決定架構或方向
- `feature-idea` — 用戶主動建議新功能

**Status 流程：** `open` → `reviewed` / `in-progress` / `done` / `wontfix`

---

<!-- Mugi：新 entry 喺下方 append，最新喺底部 -->

## 2026-04-08 — Planyway / Trello integration for post team Timeline view

- **Type:** `needs-discussion` + `capability-gap`
- **Status:** `open`
- **Reported by:** Kary（Discord channel `#ai-agent`，message `1491251254633169068`）

**Problem statement（用戶原話 + Mugi 理解）：**
Post team 用 Planyway 管理工作。Planyway 有 Calendar sync 功能，但 sync 入嚟嘅 calendar items **去唔到 Planyway 嘅 Timeline view**——Calendar 同 Timeline 喺 Planyway 入面係兩個分開嘅 surface，calendar event mirror 唔到去 timeline，timeline 要手動 manage。Kary 嘅 hypothesis：Planyway Timeline view 係 read Trello card 嘅 due date 砌出嚟，所以 source-of-truth 必須係 Trello card 而唔係 external calendar event。即係 Mugi 而家 push 上 dof.internal Calendar 嘅 milestones，post team 喺 Planyway Timeline 用唔到。

**Mugi 而家做唔到嘅嘢：**
- 冇 Trello API credentials（要新增 env var：`TRELLO_API_KEY` + `TRELLO_API_TOKEN`）
- 唔知 post team 用緊嘅 Trello board structure（一個 master board？每 project 一個 board？list naming convention？）
- 未 verify Planyway 嘅 architecture 假設（Planyway 官方 API 開放程度未 confirm，可能要走 Trello 嗰邊做 integration）
- 知識庫冇任何 Planyway / Trello 嘅 context file

**3 條已 propose 嘅方向（等 Kary 揀）：**
1. **Mugi push 去 Trello（唔再 push Calendar）** — Trello card 做 source of truth，Calendar 由 Trello → Planyway → Calendar reverse sync。Trade-off：dof.internal Calendar 唔再係主控
2. **雙向 push（Calendar + Trello 同時）** — 兩邊都建立。Trade-off：desync 風險高
3. **Calendar 主控 + on-demand mirror 去 Trello** — Mugi 收到指令先 sync。Trade-off：要記住 trigger

**Open questions for Kary：**
- 揀邊條方向（1 / 2 / 3 / 其他）？
- post team 而家點用 Planyway / Trello 嘅 board structure？
- 想唔想 Mugi 先 verify Planyway 架構假設（搵文檔）先傾，定直接攞個方向落實？

**Next action：** 等 Kary review + 揀方向。揀完之後 capability-gap 部分要 set up Trello credentials + 寫 integration logic（可能要新增 `skills/producer/trello-ops.md`）。

---

## [[2026-04-08]] 14:23 — @valkyri_k

Type: capability-gap
Request: Storyboard card 加 checklist，items `Video 1` assign Max / `Video 2` assign Keith
Gap: Trello 嘅 checklist item member assignment 係 Advanced Checklists feature（Standard+ plan power-up），呢個 board 而家冇 enable。試過 `PUT /cards/{id}/checkItem/{iid}` 加 `idMember` param —— API return 200 但 silent ignore（GET 返嚟 `idMember: null`）。Verify 過 board `premiumFeatures` 冇相關 flag。Fallback 用咗 `@username` mention 加落 item 個名度（Trello auto-link 但唔算 formal assignment，唔入 Workload view）。可能 fix：upgrade Trello workspace plan，或者 default 將「assign 到 checklist item」嘅 request 自動轉做 split-cards approach（card-level member assignment 係 free）。
Status: open

---

## [[2026-04-08]] 17:06 — @sohling_69845

Type: needs-discussion
Request: Assign team member by name to Trello card (Sohling 講「assign 俾 Yik」)
Gap: Trello board members 嘅 username / display name 同 CLAUDE.md Quick Reference 嘅 DOF team names 對唔上。e.g. Trello 上面有 `ylx176 | YL` 但 CLAUDE.md 講 Yik。Mugi 要靠估（YL = 估係 Yik），有機會 mismatch 入錯人。建議：喺 `skills/trello/trello-agent.md` 或者新 context file 加一個 mapping table（DOF name → Trello member id + username + display name），等 Mugi 唔使每次 fuzzy match。已知 mapping（從今晚 fetch 抽出嚟）：Benjy `benjy77`, Kary `karyto5`, Katy `katylau6`, Kay `kaychan37`, Keith `keith46552115`, Max `maximiliandof`, Sohling `sohling5`, Yik `ylx176`（implicitly confirmed — Sohling 後續無糾正），DOF AI bot `dreamoffishai`.
Status: open
