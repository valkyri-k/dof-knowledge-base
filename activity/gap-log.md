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
