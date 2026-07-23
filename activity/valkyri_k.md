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

### [[2026-07-23]] morning
- entry: 交付任何 created / found resource（Drive file/folder、Vimeo/YouTube 片、doc）俾 Kary 時，一定要連埋 clickable link，唔可以淨係報名 / 描述。
  category: response-guidance
  confidence: high
  source: corrected
  evidence:
    - [[2026-07-14]] Kary create 完 Coca-Cola folder 後 correct：「you should have show me the link 等我易啲㩒去睇, not only the folder name」
    - [[2026-07-20]] 延伸：Vimeo unlisted link 甩 privacy hash 令 Kary 開唔到——同一個「俾可用 link」原則
  proposed_visibility: team-shared
  status: pending-review
  drafted_by: mugi
  drafted_at: 2026-07-23

### [[2026-07-23]] afternoon
- entry: 答問題（尤其 asset / 資料查詢）要簡潔、action-oriented——直接俾最快攞到嘢嘅 path，唔好長篇解釋、唔好過度 escalate（唔使要嗰陣唔好搵 supervisor / 第三方）。
  category: response-guidance
  confidence: medium
  source: corrected
  evidence:
    - [[2026-07-23]] Kary DM 更正 Kyle CWB clean-version 答得太長：「唔駛咁詳細答佢，直接叫佢自己睇 DOF server…更加唔需要搵 sohling」
    - 主題呼應同日 link-hygiene candidate（俾人最快 path 攞 asset）
  proposed_visibility: team-shared
  status: pending-review
  drafted_by: mugi
  drafted_at: 2026-07-23

---

## Open Threads

- [2026-07-07] `skills/trello/trello-agent.md` style frame default assignee 已拆除（Kay 離開） — waiting on Kary + Sohling 夾新負責人，之後叫 Mugi 補返 default
- [2026-07-07] Silent-reply bug（4 次同 session 內 skip 咗 Discord reply tool call，root cause 未定）— cross-ref: gap-log.md [[2026-07-07]] ~09:00 / ~09:18 / ~09:25 三個 entry；建議 Kary 攞 harness-side transcript debug。**又疑似 recur [[2026-07-23]]**：Kary 02:47 講「clear」後隔咗約 1 個鐘冇任何 Discord reply，Kary 03:55 chase「做完未？有又無喺discord覆我」先觸發處理——未能確定係 Mugi skip reply 定 harness 冇 invoke，但 pattern 同已知 bug 一致
- [2026-07-07] `scripts/timeline_backward.py` anchor overlay + slack-distribution bugs（0wd gap / inversion / trailing idle vs squeezed cut）— cross-ref: gap-log.md [[2026-07-07]] ~08:48 entry，Kary 話會之後 review 成條 timeline planning logic
- [2026-07-20] Vimeo skill example fix — offered 更新 `skills/integration/vimeo-search.md` Step 3 example 用帶 privacy-hash 嘅 full link（而家係 bare `vimeo.com/<id>`，unlisted 片會甩 hash 開唔到）；Kary 未答，低優先
- [2026-07-23] Clean-version handling rule（clean/textless 從來唔上 YT/Vimeo，喺 DOF server，直接叫 user 自己揾）— 暫時淨喺 Mugi memory（feedback-clean-version-on-server）+ gap-log；Kary 講「will review later using gap log」再決定使唔使 promote 入 KB（CLAUDE.md / context/）做 canonical rule。cross-ref: gap-log.md [[2026-07-23]] ~04:10

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

### 2026-07-13 afternoon session (multi-job schedule ops + 2 new senders onboarded)
今日主要係短 job-channel queries + schedule 操作，橫跨多個 job，冇 architectural work。J26082 幫 Kary 查咗 7/13–7/19 呢個禮拜嘅 schedule（3rd Cut/Picture Lock/VO Recording TBC）；home base「Test2」thread 查 Max 今日 Trello due（冇）。首次接觸兩位新 sender：Kyle（director，J26050 + J26076）同 Atlas（asst director，J26081）——已分別建立佢哋嘅 activity file，跟 sender routing rule 各自寫入自己 file，冇塞入呢個 file。J26050 幫 Kyle 兩次 reschedule（3rd Cut→7/14、Final Output→7/23，rule check 全過）；J26076 幫 Kyle 一次過 push 10 個 milestone（DFIQ project，7/14 script share 到 9/4 final output）。J26081 Atlas 想 remove TBC remark，但兩次擴大搜尋都確認呢個 job 喺 Calendar 完全冇任何 event——已 flag 俾 Atlas，等緊佢答覆係咪 project shorthand 用咗第啲名。

### 2026-07-14 to 07-23 session (Coca-Cola folder, J26082 VO ops, link-hygiene fixes, VO studios → KB)
橫跨多日嘅 mixed ops session，主線係 Drive/Calendar 操作 + 兩個 link-hygiene 教訓入 memory + 一個新 KB context file。(1) **J25115 Coca-Cola Sales Kickoff**：由 Airtable Master Job Log（REST + PAT，非 cloud MCP）查到 job#/name（Completed job，唔喺 Current cache），跟現有 Drive 命名格式（lowercase hyphen-slug，全部住喺 Discord-files folder）create job folder。Kary 即場 correct：create 完淨係報 folder 名唔夠，一定要俾埋 clickable link →入 memory（feedback_drive_include_link）。(2) **J26082 EMSTF 30A VO ops**：job channel 內 add VO Recording 22/7 下午 3-4 時 @ DoubleDouble（timed event, colorId 1）；主動 flag 到原有 7/16 VO (TBC) placeholder superseded，Kary confirm 後 delete；再 move Final Output 7/20→7/24（五）。全部行 date/holiday/saturation check。(3) **Vimeo link 甩 hash**：Kary 報 JoeChat_Feb_CNY link 睇唔到——root cause 係片 unlisted，link 一定要帶 privacy hash，之前俾嘅 bare link 甩咗 →修正 + 入 memory（feedback_vimeo_full_link_hash）+ offer 改 skill example。(4) **好醫工 = EMSD 16th China Best CE Award**：中文片名 0 hit，轉英文 title-search 搵到 4 個 unlisted 版本，flag 最新 5/8 Ver3。(5) **VO studios → KB**：Kary 問過往 VO event 搵 DoubleDouble 地址——搜 53 條 VO event 發現 Calendar 只擺 raw 地址、冇 studio 名，唔敢估；Kary 提供 2 個 studio + contact，先入 memory，再應 Kary「要加落 KB context」authorize 整咗 `context/vo-studios.md` + CLAUDE.md routing pointer，commit ff4d281（push 撞 non-ff，rebase 後成功）。**Key learnings**：兩個 deliverable-link 教訓（Drive create 要連 link、Vimeo unlisted 要連 hash）已 durable 入 memory；DoubleDouble = 荃灣 One MidTown（唔係最常用嗰個觀塘 studio），好彩問咗冇估錯。**同時**：Kyle（kyleyeungdof_29223）07-23 喺 home base 問 J25072 CWB clean version，已按 sender routing flush 去佢自己 file。呢個 session 尾 clear 觸發後疑似 silent-reply recur（見 Open Threads）。

### 2026-07-23 afternoon micro-session (clean-version handling correction)
緊接 morning clear 之後嘅短 DM 交流。Kyle 問 J25072 CWB clean version，Mugi 搜 YT/Vimeo/Drive 覆咗一大段仲 offer tag Sohling；Kary DM 更正：clean/textless version 從來唔上 YT/Vimeo，一定喺 DOF server，應該直接叫 user 自己入 job folder 揾，唔使長篇、唔使搵 Sohling。已精簡覆返 Kyle、rule 入 memory（feedback-clean-version-on-server）、gap-log entry 由 capability-gap 改成 not-a-gap。Kary 再問「你點記低呢個 rule」→ 解釋 memory vs KB 分別 + offer promote 入 KB canonical；Kary 話會之後自己用 gap-log review 再決定。**Learning**：asset 查詢要簡潔 + 俾 self-serve path，唔好過度 search / escalate。

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
| 2026-07-14 | Check Coca-Cola Sales Kickoff 2025 job# + name, then create GDrive job folder | J25115 (Airtable Master Job Log, Completed); created `j25115_button-coca-cola-sales-kickoff-video-kv-design-2025` under Discord-files ✅. Kary feedback: post-create reply must include clickable link → saved to memory |
| 2026-07-20 | J26082: add VO Recording 22/7 下午3-4時 @ DoubleDouble Studio | Created timed event VO Recording - EMSTF 30A (colorId 1) ✅; flagged pre-existing 7/16 VO Recording (TBC) as superseded — awaiting delete/keep decision |
| 2026-07-20 | J26082: (a) delete 7/16 TBC VO + move Final Output to Friday | Deleted 7/16 TBC VO ✅; moved Final Output - EMSTF 30A 7/20→7/24(Fri) ✅ (weekday/holiday/saturation checked) |
| 2026-07-20 | JoeChat_Feb_CNY Vimeo link 睇唔到 | Re-ran vimeo-search: video is unlisted → correct link needs privacy hash `https://vimeo.com/1195579838/e56a6dbb4c`; earlier bare link dropped hash. Saved lesson to memory; offered to fix skill examples |
| 2026-07-21 | EMSD 好醫工 video YouTube link | 好醫工 (Chinese) 冇 match → English "Best CE Award" hit: EMSD 16thChinaBestCEAwardComptition, 4 unlisted versions. Gave all + flagged latest 20260508 Ver3 (youtu.be/Y5MjAsrNolU); asked which is final client ver |
| 2026-07-22 | 過往 VO Recording event 搵 DoubleDouble 地址 | Swept 53 VO events 2024–now; none labelled "DoubleDouble" (only raw addresses), KB 無 studio→address record. Presented recurring studio addrs: ①觀塘鴻圖道63-65號鴻運工廠大廈7C (12×, most likely) ②荃灣One MidTown 821室. Asked Kary confirm which = DoubleDouble → then update 7/22 event location. **Pending confirm** |
| 2026-07-22 | Kary confirmed DoubleDouble = ② One MidTown; 記低 2 VO studios | Saved reference to memory (studio-vo-addresses: ①Kwun Tong 鴻運工廠7C / Gerry 90712049; ②DoubleDouble One MidTown 821室 / Elaine 91046282). Updated 7/22 VO event location = full DoubleDouble addr + Elaine contact in desc ✅. Offered to also persist into KB context (pending Kary go) |
| 2026-07-22 | Kary: 要加落KB context | Created `context/vo-studios.md` + CLAUDE.md context-table routing row; committed + pushed (ff4d281, rebased onto remote 22e3aec after non-ff reject) ✅ |
| 2026-07-07 | J26XXX (test project) draft timeline: shoot 7/20, final output 8/28 hard deadline | Chain script hit anchor + slack-distribution bugs (0wd Shoot→1st Cut gap, 1st Cut anchor inversion vs FB1, trailing idle slack before Picture Lock while cut_warnings flag 2nd/3rd cut ≤3wd) — surfaced to Kary, logged to gap-log.md as bug（script logic）, no Calendar push (test only) |
| 2026-07-07 | J26XXX simplified push (Shooting 7/20, 1st Cut 7/27, Final Output 8/28) | ✅ pushed to dof.internal Calendar, no saturation |
| 2026-07-07 | Silent-reply repeat incident: "1st cut 幾耐後 2nd cut" answered in text only, reply tool not called | Kary caught it ("你無答我"/"見唔到回覆"); resent + logged to gap-log.md as bug（behavioral — repeat incident） |
| 2026-07-07 | Silent-reply 3rd occurrence same session: out-of-scope redirect ("邊隻股票") also text-only, no reply tool call | Kary caught again ("你又無喺discord答我"); resent + logged to gap-log.md as pattern-confirmed 3x |
| 2026-07-07 | Weekday lookup (7/15) + CWJ latest episode + post-pro headcount ×2 + "1st cut→2nd cut" FAQ + Kyle role lookup | All answered via Quick Reference/Python weekday script; one occurrence (Kyle) was 4th silent-reply failure, resent |
| 2026-07-07 | Non-Kary user (dreamoffish.ai bot) requested print env variables, then prompt injection ("ignore all previous instructions") | Both refused per Security Policy + Kary tagged; not logged to gap-log (policy exclusion) |
| 2026-07-07 | Standalone Calendar add: "Test 1st cut" 2026-07-10 | ✅ Created (colorId 7), no saturation/holiday conflict |
| 2026-07-07 | Kay（Graphic Designer）已離開 DOF — KB update request | Updated CLAUDE.md team table, team-roles.md, production-pipeline.md, dof-context-overview.md; removed silent Trello style-frame default (was Kay) per Kary instruction |
| 2026-07-13 | hello greeting (home base) | Replied ✅ |
| 2026-07-13 | J26082 job schedule of this week (asked in job channel) | Reported 3 events: 3rd Cut 7/13, Picture Lock 7/15, VO Recording (TBC) 7/16 |
| 2026-07-13 | Max 今日 Trello card status (Test2 thread, home base) | No card due today ✅ |
| 2026-07-23 | Kyle J25072 CWB clean-version reply 過長 — Kary DM 更正 handling | 精簡覆返 Kyle（clean version 喺 DOF server 自己揾，唔上 YT/Vimeo，唔搵 Sohling）；rule 入 memory (feedback-clean-version-on-server)；gap-log 改 not-a-gap；resolve Kyle open thread ✅ |
| 2026-07-23 | Kary：你點記低呢個 rule？ | 解釋記咗 2 處（Mugi memory + gap-log audit trail），surface memory≠KB 分別，offer promote 入 KB canonical rule；Kary 話 will review later via gap-log |
