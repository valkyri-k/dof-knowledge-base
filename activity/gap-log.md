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

## [[2026-04-08]] 19:21 — @valkyri_k

Type: capability-gap
Request: Update DOF Current Job List sheet (J26041 CURRENT PROGRESS column) via Mugi。
Gap: 當時 OAuth refresh token 只授權 `drive` + `documents` 兩個 scope，冇 `https://www.googleapis.com/auth/spreadsheets`。Workaround：用 `drive` scope 行 `sheets.values.update` 都 work（驗證 200 OK，row 25 已更新），但會 block 將來嘅 batchUpdate / formatting / 加 sheet 等需要正式 spreadsheets scope 嘅操作。
Resolution: Kary 之後 re-consent OAuth flow，加埋 `spreadsheets` scope。2026-04-08 20:08 verify 過 refresh token 而家三個 scope 齊（`drive` + `documents` + `spreadsheets`）。Sheets full API 已 unlock。
Status: done

---

## [[2026-04-08]] 17:06 — @sohling_69845

Type: needs-discussion
Request: Assign team member by name to Trello card (Sohling 講「assign 俾 Yik」)
Gap: Trello board members 嘅 username / display name 同 CLAUDE.md Quick Reference 嘅 DOF team names 對唔上。e.g. Trello 上面有 `ylx176 | YL` 但 CLAUDE.md 講 Yik。Mugi 要靠估（YL = 估係 Yik），有機會 mismatch 入錯人。建議：喺 `skills/trello/trello-agent.md` 或者新 context file 加一個 mapping table（DOF name → Trello member id + username + display name），等 Mugi 唔使每次 fuzzy match。已知 mapping（從今晚 fetch 抽出嚟）：Benjy `benjy77`, Kary `karyto5`, Katy `katylau6`, Kay `kaychan37`, Keith `keith46552115`, Max `maximiliandof`, Sohling `sohling5`, Yik `ylx176`（implicitly confirmed — Sohling 後續無糾正），DOF AI bot `dreamoffishai`.
Status: open

---

## [[2026-04-26]] — @valkyri_k

Type: bug（behavioral）
Request: Discord message 處理（任何 message — 今次具體係 BOC Trendy Together 排 schedule）
Gap: Mugi internal 處理咗個 request（terminal 觀察到 process 咗 tool calls、創建咗 Calendar events），但**冇 send Discord reply 俾 Kary**。Kary 喺 Discord 等覆，container terminal 先見到 Mugi 跑緊。即係 reply step 被 silent skip。Kary 後尾再 prompt Mugi 先得到 acknowledgement（valkyri_k.md 2026-04-26 entry 有 Mugi 自己 ack「missed Apr 25 reply」）。

Root cause hypothesis：CLAUDE.md「必須回覆」rule 之前埋葬咗喺第 510 行（`行為原則` 第 1 條），attention weight 太低；亦只 cover 一個 failure mode（重複 question）。冇 cover：side-effect-only completion（events 已 create）、tool 跑完無 explicit verbal report、long task 無 ack-first。

Mitigation deployed [[2026-04-26]]（commit `766cbc2`）：
- 將 rule 升到 CLAUDE.md 最頂 `## 最高優先 Rule：絕對唔可以 silent` section
- 擴展至 10 個 silent failure modes（包括 side effect、tool fail、internal-reasoning-only）
- Ack-first pattern：>1 tool call 嘅 task 要先 ack
- End-of-turn self-check：每 turn 結束前驗證有無 send Discord message

Status: open（mitigation deployed，等 follow-up incident 數據驗證）— 同步 logged 落 [007-agent-mugi backlog](file:///Users/kary/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/DOF_Build/projects/007-agent-mugi/backlog/bugs/silent-no-discord-reply.md) bug file 做 vault-side tracking
