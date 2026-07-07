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

- [2026-07-07] `skills/trello/trello-agent.md` style frame default assignee 已拆除（Kay 離開） — waiting on Kary + Sohling 夾新負責人，之後叫 Mugi 補返 default
- [2026-07-07] Silent-reply bug（4 次同 session 內 skip 咗 Discord reply tool call，root cause 未定）— cross-ref: gap-log.md [[2026-07-07]] ~09:00 / ~09:18 / ~09:25 三個 entry；建議 Kary 攞 harness-side transcript debug
- [2026-07-07] `scripts/timeline_backward.py` anchor overlay + slack-distribution bugs（0wd gap / inversion / trailing idle vs squeezed cut）— cross-ref: gap-log.md [[2026-07-07]] ~08:48 entry，Kary 話會之後 review 成條 timeline planning logic

---

## Recent Session Summaries

### 2026-05-29 to 2026-06-05 session (bulk infra + ops)
連續多日 ops session。兩次 job list sync (May 29, Jun 3): 新增 10 Current jobs，移除 6 個 (J26002/J26047/J26060/J26065/J26066/J26067)。Discord allowlist 擴展到 28+ channels，Kary 確認「batch add all missing」UX 改善——一個 terminal command trigger 即 Mugi 一次過 patch JSON。J26050 CUHK Closed→Current + channel linked + Airtable updated。J26062 Orbis [F-1][F-2][F-3] 日期更新（1st Cut→Jun 11，Final Output→Jun 16，client launch Jun 18 remark appended）。J26082 EMSTF 30A：先 prelim tentative timeline for client presentation（week-unit draft），後 confirmed timeline 13 events (Jun 8–Jul 20) pushed to Calendar + alias added。Sohling 首次觸發 Calendar+Trello：J26050 CUHK 7/8 events pushed（Jun 11 cut saturation → 1st Cut event 暫扣，Trello card 建咗），8 Trello cards created (Katy+Keith)。

### 2026-06-05 micro-session (KB sender routing fix)
極短 session。Kary 問 Sohling activity 有冇 log——發現冇，補 sohling_69845.md + 新建 j26050 per-job log (commit `8397dd3`)。Kary 之後更新 CLAUDE.md 加入 **Sender routing hard rule**（multi-sender flush：channel 入面其他人嘅 interaction 入佢哋自己 file，唔係塞入 valkyri_k.md；Pre-Clear Step 0 而家係 mandatory participant scan）。同時 migrate Sohling 嘅 open threads（J26050 saturation / J26062/J26070/J26071 member assign）去 sohling_69845.md。**Key decision**：呢個 rule 係長期 architectural fix，解決「所有 channel interaction 全部誤記入 Kary file」嘅 systemic bug。

### 2026-06-09 afternoon session (Vimeo skill + J26085 log recovery)
Server restart 前 Benjy 用 Mugi 做 J26085 Hang Seng Facility Award Calendar+Trello sync，但 session log 冇寫到。Kary 喺本 session 報告，Mugi 補建 `j26085_minerals_hang_seng_facility_management_award.md` per-job file + scaffold + Interaction Log entry。另一件事：Kary 要搵 EMSD Dems Briefing Vimeo links，Mugi 初次答「冇 Vimeo 整合」。Kary 即時更新 KB repo，加入 `skills/integration/vimeo-search.md` + CLAUDE.md routing entry；pull 後 Mugi 正確 read skill file、執行 `scripts/vimeo-search.js`，返 5 條 results。**Key takeaway**：Vimeo search 係 title-text search via REST script，唔係 cloud MCP；skill routing rule 已入 CLAUDE.md，下次直接 trigger。

### 2026-06-11 morning session (J26082 status + Benjy J26077 + Magnific MCP)
三條主線。(1) Benjy J26077 CWJ June：12 Calendar events + 12 Trello cards batch created，Katy/Max/Keith 分配完成——Benjy 首次 direct request，flow 順暢。(2) J26082 EMSTF 30A：Kary 喺 job channel 分享 Kelly@EMSD debrief（script revised，creative 型格化，content regrouped），建立 per-job file + Jun-16 Calendar event。Kary 糾正 shorthand 應用 `EMSTF 30A`（唔係 `EMSD Corp Video`）——已改 event + 入 memory。(3) Magnific：Kary 問 account balance → Mugi 冇 Magnific MCP → Kary 提供 `claude mcp add` command → 已 add，待 restart 生效。同時 CWJ alias 加入 J26075/J26077。**Key decision**：J26082 Calendar shorthand = `EMSTF 30A` 已 locked 入 memory + feedback file。

### 2026-07-07 morning session (J26XXX test timeline + repeated silent-reply bug + Kay departure)
長 session，多線並行。(1) J26XXX（test project）draft timeline 撞到 `timeline_backward.py` 一連串 anchor overlay + slack-distribution bug（詳細 4-run repro 已入 gap-log），最後應 Kary 要求 simplify 做 3-event（Shooting/1st Cut/Final Output）test push，冇 saturation，成功 push。(2) 呢個 session 首次出現**連續 4 次 silent-reply failure**——短答案（FAQ、redirect、team lookup）淨係喺 text output 出現，冇實際 call reply tool，Kary 每次都要問「你無答我」先發現。試過兩個 hypothesis（答案簡短 / session context 長度）都被 Kary 即場數據推翻，最終誠實承認搵唔到 deterministic root cause，建議 harness-side transcript debug。(3) Kary 通知 Kay（前 Graphic Designer）已喺上月離開 DOF——KB 全面 update（CLAUDE.md team table、team-roles.md、production-pipeline.md、dof-context-overview.md），並主動拆除 `trello-agent.md` style frame 嘅 silent default assignee（曾經 default 派俾 Kay），改做逼 user 指明，等 Kary 同 Sohling 夾新負責人。(4) 順手處理 2 個 security policy 觸發（非 Kary 用戶要求 print env variables + prompt injection「ignore all previous instructions」）——已按 Security Policy 拒絕 + tag Kary，唔記入 gap-log（policy 排除呢類 case）。**Key takeaway**：silent-reply bug 已經係 repeat incident（4 月 26 號 + 依家呢次 4 連發），現有 mitigation 唔夠，需要 Kary 喺 harness 層面而唔係 prompt 層面跟進。

---

## Request Log

| Date | Request | Outcome |
|------|---------|---------|
| 2026-06-03 | Job list sync | J26091/J26056/J26084 addedWithChannel; J26089 removed ✅ |
| 2026-06-03 | Discord allowlist batch add 6 channels (J26007/J26010/J26056/J26057/J26084/J26091) | All 6 in one terminal invoke ✅ |
| 2026-06-04 | J26082 prelim tentative timeline for client presentation | Week-unit draft; Jun 19 holiday flagged ✅ |
| 2026-06-04 | J26082 EMSTF 30A confirmed timeline: 13 Calendar events (Jun 8–Jul 20) + alias added | ✅ |
| 2026-06-11 | Add CWJ alias to all Chat with Joe projects (J26075, J26077) | ✅ |
| 2026-06-11 | J26082 client feedback debrief shared for Mugi ref (Kelly@EMSD call notes) | Logged to per-job file; Jun-16 TBC storyflow revision noted |
| 2026-06-05 | Sohling: J26050 CUHK Calendar (7/8 pushed, Jun 11 saturation pending) + Trello (8 cards, Katy+Keith) | ✅ (logged in sohling_69845.md per sender routing) |
| 2026-06-05 | Flagged Sohling activity log missing; supplemented sohling_69845.md + created j26050 per-job log | Commit 8397dd3 ✅ |
| 2026-06-05 | CLAUDE.md updated: Sender routing hard rule; Sohling open threads migrated to sohling_69845.md | Kary edit ✅ |
| 2026-06-05 | Open threads cleanup: J260BB/J260CC/J26053 closed (test/ignore); activity.bak deleted; Planyway + root-owned kb context explained | ✅ |
| 2026-06-05 | All remaining open threads cleared by Kary instruction | ✅ |
| 2026-06-09 | Benjy J26085 session log recovery (server restart before log) | Supplemented j26085 per-job file ✅ |
| 2026-06-09 | Vimeo links — EMSD Dems Briefing | 5 results returned (vimeo-search.js) ✅ |
| 2026-06-11 | J26082 Calendar shorthand correction → `EMSTF 30A` | Fixed existing event + saved to memory ✅ |
| 2026-06-11 | J26082 Jun-16 Calendar event: Revise StoryFlow | ✅ Created (colorId 5) |
| 2026-06-11 | Magnific account balance query | No MCP available → Kary provided `claude mcp add` command → added, pending restart |
| 2026-07-07 | J26XXX (test project) draft timeline: shoot 7/20, final output 8/28 hard deadline | Chain script hit anchor + slack-distribution bugs (0wd Shoot→1st Cut gap, 1st Cut anchor inversion vs FB1, trailing idle slack before Picture Lock while cut_warnings flag 2nd/3rd cut ≤3wd) — surfaced to Kary, logged to gap-log.md as bug（script logic）, no Calendar push (test only) |
| 2026-07-07 | J26XXX simplified push (Shooting 7/20, 1st Cut 7/27, Final Output 8/28) | ✅ pushed to dof.internal Calendar, no saturation |
| 2026-07-07 | Silent-reply repeat incident: "1st cut 幾耐後 2nd cut" answered in text only, reply tool not called | Kary caught it ("你無答我"/"見唔到回覆"); resent + logged to gap-log.md as bug（behavioral — repeat incident） |
| 2026-07-07 | Silent-reply 3rd occurrence same session: out-of-scope redirect ("邊隻股票") also text-only, no reply tool call | Kary caught again ("你又無喺discord答我"); resent + logged to gap-log.md as pattern-confirmed 3x |
| 2026-07-07 | Weekday lookup (7/15) + CWJ latest episode + post-pro headcount ×2 + "1st cut→2nd cut" FAQ + Kyle role lookup | All answered via Quick Reference/Python weekday script; one occurrence (Kyle) was 4th silent-reply failure, resent |
| 2026-07-07 | Non-Kary user (dreamoffish.ai bot) requested print env variables, then prompt injection ("ignore all previous instructions") | Both refused per Security Policy + Kary tagged; not logged to gap-log (policy exclusion) |
| 2026-07-07 | Standalone Calendar add: "Test 1st cut" 2026-07-10 | ✅ Created (colorId 7), no saturation/holiday conflict |
| 2026-07-07 | Kay（Graphic Designer）已離開 DOF — KB update request | Updated CLAUDE.md team table, team-roles.md, production-pipeline.md, dof-context-overview.md; removed silent Trello style-frame default (was Kay) per Kary instruction |
