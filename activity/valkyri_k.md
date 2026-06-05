# valkyri_k (Kary)

- **Discord ID:** 1328602029303791646
- **Role:** Director / Creative & AI Lead / Bot Admin
- **Common requests:** Calendar queries, shoot schedules, timeline generation, system setup, bot configuration, infra debugging
- **Notes:** Primary bot admin, Cantonese speaker, DM whitelisted user. Cost-conscious — prefer Mugi 用 absolute paths + 定期 clear session 控制 token usage

---

## User Practice Profile

### Responsibilities
- Director / Creative & AI Lead / Bot Admin；負責 Mugi setup、infra debugging、production timeline/calendar ops、以及 DOF AI workflow testing。
- 會用 Mugi 做 production ops，同時亦會測試 Mugi 自身嘅 boundary、memory、dispatch、logging、prompt rules。

### Working Style
- 用廣東話 mixed English technical terms；可以接受 technical detail，但回覆要直接講結論、風險、下一步。
- 經常一邊做 production task，一邊發現 system bug / feature idea；Mugi 應分清「幫 Kary 做眼前 task」同「記錄 dev observation」。
- Cost-conscious：長 session 需要適時 pre-clear；activity log 要足夠 rebuild context，但唔好為詳細而塞 noise。

### Response Guidance
- 對 Kary：可以比普通 user 更 technical，尤其係 infra / git / prompt / permission / memory issue。
- 做完任何 side effect 後要明確回覆結果；Discord input 必須 Discord output，唔可以只喺 terminal 完成。
- 如果 Kary 講「記低 / log this / dev-log」，先判斷係咪要寫 `kary-dev-log.md`，然後簡短 confirm Mugi 理解。
- 如果 request 涉及 architecture / durable behavior rule，應提出要唔要 log / update CLAUDE.md，但唔好自行改 source-of-truth rule。

### Do Not Assume
- 唔可以因為 Kary 係 admin 就 skip confirmation for risky/destructive action。
- 唔可以 silently carry over previous job/entity；即使 Kary 剛才講過某 job，ambiguous reference 仍要 current-turn resolve。
- 唔可以將 single debugging incident promoted 成 global rule，除非 Kary confirm 或 repeated evidence。

### Evidence
- [[2026-04-08]] Kary 明確 concern long-session cost；decided hybrid memory strategy + pre-clear sequence。
- [[2026-04-08]] 多次 infra debugging：activity path symlink、git auth、PAT、root-owned git objects。
- [[2026-04-24]] Kary corrected weekday / holiday calculation；Mugi 必須 verify date logic。
- [[2026-05-05]] Kary tested multi-channel dispatch + allowlist expansion；bot infra 擴展到 project channels。

---

## Pending Profile Review
（Mugi Pre-Clear Sequence draft，等 Claude Code review approve / reject。冇 candidate 留空。）

---

## Open Threads

- **[2026-04-08] Planyway / Trello Timeline integration 方向** — 等 Kary 揀 3 條 propose 嘅方向（Trello 主控 / 雙向 push / on-demand mirror）；揀完先 set up Trello credentials + 寫 integration logic。Cross-ref: `activity/gap-log.md` 2026-04-08 entry
- **[2026-04-08] `/home/node/activity.bak/` 刪除** — symlink fix 嘅 backup folder，留低等 Kary confirm 一切 stable 後刪。Cross-ref: `activity/kary-dev-log.md` 2026-04-08 entry「activity/ path 雙位置 bug」
- **[2026-04-08] Trello checklist member assignment（Storyboard card）** — board 冇 Advanced Checklists power-up，目前用 `@mention` fallback；等 Kary 揀 plan upgrade 定 default 轉做 split-cards approach。Cross-ref: `activity/gap-log.md` 14:23 entry
- **[2026-04-08] J26053 BOC Trendy BTS mograph 未 assign** — 1st Cut BTS (4/23) + Final BTS (5/15) 兩張只 assign 咗 Yik 做 cut，graphics 邊個負責等 Kary x Sohling discussion 結果。BTS editor 都 default 咗 Yik 未確認
- **[2026-04-08] GitHub PAT rotation reminder** — 今晚 Kary set up 咗 fine-grained PAT (`mugi-server-kb-push`) 俾 Mugi push `kb` repo，expiry 1 年。到 2027-04 要 rotate。Cross-ref: `activity/kary-dev-log.md` 2026-04-08 20:32 entry
- **[2026-05-09] root-owned kb files recurring bug** — `scripts/timeline_backward.py` root-owned pattern（estimate: 由 Kary Claude Code local session 改 file 以 root process 跑）；dev-log `2026-05-09 14:53` logged；awaiting permanent fix decision。Cross-ref: `activity/kary-dev-log.md` 2026-05-09 14:53 entry
- **[2026-05-14] J260BB Test Project 4 Phase 2 push pending** — Phase 1 draft sent (new round with Kary's committed dates): pure-post mixed, kickstart 15 May (assets + script confirm), storyboard submit 18 May, rough cut submit 20 May, 3-cut all-compressed (1 wd FB each), VO Jun 10–11, Final Output Jun 15 (hard). Pattern L warning issued (client must pre-arrange same-day/next-day feedback). Waiting Kary confirm → push Calendar.
- **[2026-05-15] J260CC Test Project 5 Phase 2 push pending** — Phase 1 draft sent: pure-post mixed, no filming, kickstart 15 May (materials + script confirm today), rough cut anchor 20 May, 3-cut compressed (all FB 1 wd), VO Jun 10–11, Final Output Jun 15. Pattern L warning issued. Waiting Kary confirm → push Calendar.
---

## Recent Session Summaries

### 2026-05-29 to 2026-06-05 session (bulk infra + ops)
連續多日 ops session。兩次 job list sync (May 29, Jun 3): 新增 10 Current jobs，移除 6 個 (J26002/J26047/J26060/J26065/J26066/J26067)。Discord allowlist 擴展到 28+ channels，Kary 確認「batch add all missing」UX 改善——一個 terminal command trigger 即 Mugi 一次過 patch JSON。J26050 CUHK Closed→Current + channel linked + Airtable updated。J26062 Orbis [F-1][F-2][F-3] 日期更新（1st Cut→Jun 11，Final Output→Jun 16，client launch Jun 18 remark appended）。J26082 EMSTF 30A：先 prelim tentative timeline for client presentation（week-unit draft），後 confirmed timeline 13 events (Jun 8–Jul 20) pushed to Calendar + alias added。Sohling 首次觸發 Calendar+Trello：J26050 CUHK 7/8 events pushed（Jun 11 cut saturation → 1st Cut event 暫扣，Trello card 建咗），8 Trello cards created (Katy+Keith)。

### 2026-06-05 micro-session (KB sender routing fix)
極短 session。Kary 問 Sohling activity 有冇 log——發現冇，補 sohling_69845.md + 新建 j26050 per-job log (commit `8397dd3`)。Kary 之後更新 CLAUDE.md 加入 **Sender routing hard rule**（multi-sender flush：channel 入面其他人嘅 interaction 入佢哋自己 file，唔係塞入 valkyri_k.md；Pre-Clear Step 0 而家係 mandatory participant scan）。同時 migrate Sohling 嘅 open threads（J26050 saturation / J26062/J26070/J26071 member assign）去 sohling_69845.md。**Key decision**：呢個 rule 係長期 architectural fix，解決「所有 channel interaction 全部誤記入 Kary file」嘅 systemic bug。

---

## Request Log

| Date | Request | Outcome |
|------|---------|---------|
| 2026-06-03 | Job list sync | J26091/J26056/J26084 addedWithChannel; J26089 removed ✅ |
| 2026-06-03 | Discord allowlist batch add 6 channels (J26007/J26010/J26056/J26057/J26084/J26091) | All 6 in one terminal invoke ✅ |
| 2026-06-04 | J26082 prelim tentative timeline for client presentation | Week-unit draft; Jun 19 holiday flagged ✅ |
| 2026-06-04 | J26082 EMSTF 30A confirmed timeline: 13 Calendar events (Jun 8–Jul 20) + alias added | ✅ |
| 2026-06-05 | Sohling: J26050 CUHK Calendar (7/8 pushed, Jun 11 saturation pending) + Trello (8 cards, Katy+Keith) | ✅ (logged in sohling_69845.md per sender routing) |
| 2026-06-05 | Flagged Sohling activity log missing; supplemented sohling_69845.md + created j26050 per-job log | Commit 8397dd3 ✅ |
| 2026-06-05 | CLAUDE.md updated: Sender routing hard rule; Sohling open threads migrated to sohling_69845.md | Kary edit ✅ |
