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

### [[2026-09-03]] afternoon
- entry: Kary 落 batch / shared-state write（timeline push、KB 改、sync cache）時，鍾意 Mugi **先 draft / hold 住等 explicit「push」/「confirm」先執行**，唔好自作主張 commit；佢用好簡短 rapid 指令回（「a/b」「push」「done」「yes」「only this case」）。Mugi 應 hold draft + surface flag，等佢一個字 confirm。
  category: response-guidance
  confidence: medium
  source: observed
  evidence:
    - [[2026-09-02]] 全日多次 KB 改動 Mugi draft 完等「push」先 commit；Kyle 離職 downstream 逐條 a/b 快答
    - [[2026-08-26]] PAT scope KB correction：draft → 「yes」→ 「push」
    - [[2026-08-27]] J26062 saturation flag → Kary「Sep-11 照入」一句 confirm 先 push
  proposed_visibility: team-shared
  status: pending-review
  drafted_by: mugi
  drafted_at: 2026-09-03
- entry: Kary expects Mugi 誠實即時更正自己嘅 over-claim / 誤判，唔好為咗顯得肯定而 assert 未 verify 嘅 root cause；佢會親自數據糾正，Mugi 應該 retract + log 教訓。
  category: response-guidance
  confidence: medium
  source: corrected
  evidence:
    - [[2026-09-03]] Mugi 誤判 DM「approved/ file = confirmed root cause」，Kary 通返後 Mugi 主動 retract + gap-log correction
    - [[2026-08-25]] Kary 更正 Kyle no-reply 係 login/downtime 唔係 silent-reply bug；[[2026-09-02]] 更正 container 早已 fix（trigger gap 唔係 downtime）
  proposed_visibility: team-shared
  status: pending-review
  drafted_by: mugi
  drafted_at: 2026-09-03

---

## Open Threads

- [2026-07-07] `skills/trello/trello-agent.md` style frame default assignee 已拆除（Kay 離開） — waiting on Kary + Sohling 夾新負責人，之後叫 Mugi 補返 default
- [2026-07-07] Silent-reply bug（4 次同 session 內 skip 咗 Discord reply tool call，root cause 未定）— cross-ref: gap-log.md [[2026-07-07]] ~09:00 / ~09:18 / ~09:25 三個 entry；建議 Kary 攞 harness-side transcript debug。**又疑似 recur [[2026-07-23]]**：Kary 02:47 講「clear」後隔咗約 1 個鐘冇任何 Discord reply，Kary 03:55 chase「做完未？有又無喺discord覆我」先觸發處理——未能確定係 Mugi skip reply 定 harness 冇 invoke，但 pattern 同已知 bug 一致
- [2026-07-07] `scripts/timeline_backward.py` anchor overlay + slack-distribution bugs（0wd gap / inversion / trailing idle vs squeezed cut）— cross-ref: gap-log.md [[2026-07-07]] ~08:48 entry，Kary 話會之後 review 成條 timeline planning logic
- [2026-07-20] Vimeo skill example fix — offered 更新 `skills/integration/vimeo-search.md` Step 3 example 用帶 privacy-hash 嘅 full link（而家係 bare `vimeo.com/<id>`，unlisted 片會甩 hash 開唔到）；Kary 未答，低優先
- [2026-07-23] Clean-version handling rule（clean/textless 從來唔上 YT/Vimeo，喺 DOF server，直接叫 user 自己揾）— 暫時淨喺 Mugi memory（feedback-clean-version-on-server）+ gap-log；Kary 講「will review later using gap log」再決定使唔使 promote 入 KB（CLAUDE.md / context/）做 canonical rule。cross-ref: gap-log.md [[2026-07-23]] ~04:10
- [2026-08-06] J26016 HSUHK shoot-day naming — Batch 1 兩個拍攝日 Calendar title 係「Day 1 / Day 2 - HSUHK Student Excellence」（唔係「Shoot」字眼），Mugi 按 desc 判斷係 shoot day。等 Kary confirm 呢 2 日算唔算 shoot day（低優先，純 interpretation 確認）
- [2026-09-03] Meeting room booking sheet — ✅ read access confirmed（Drive export；「Meeting Room Reservation」，owner chunyatchi@gmail.com，dof.internal canEdit）。⚠️ write blocked：OAuth token 冇 `spreadsheets` scope（refresh 帶 spreadsheets → invalid_scope）。**Kary 話自己喺 local Claude 搞** re-consent。搞掂後俾 booking 詳情（room/date/time/name）Mugi 先可以填。Sheet 結構=月 tab × 週 grid，cell="名 HHMM-HHMM"（day×Small/Large Room）
- [2026-08-26] ⚠️ AIRTABLE_PAT write scope 收尾（低優先，可選）— KB 已加行為層 gate（Master Job Log write = Kary-only，pushed 26930f3）。殘留可選項：Kary 若想連底層 PAT scope 都收窄做真 read-only on Projects（defense in depth），要自己去 Airtable PAT settings 拆 write scope（Mugi 做唔到）。cross-ref: gap-log [[2026-08-26]]
- [2026-09-03] Inbound trigger-gap taxonomy（3 類 silent，取代舊 silent-reply thread 部分）— (A) agent down/re-login（冇 running，e.g. Kyle 8/25）；(B) agent UP 但 inbound 冇 trigger turn（Sohling 9/2 confirmed、疑似 Keith 8/21）；(C) agent UP 有 turn 但 skip reply tool（7/7 ×4）。B 類最危險（Mugi 冇 turn 唔知有 msg）。等 Kary 由 harness / Discord plugin 側 check inbound webhook / turn-trigger log。cross-ref: gap-log [[2026-09-02]] + [[2026-07-07]]

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

### 2026-07-25 to 08-06 session (light multi-channel ops, 3 senders)
橫跨多日嘅輕量 ops session，冇 architectural work，主要係 quick queries + 一個 calendar add，橫跨 3 個 sender（跟 sender routing 各自 flush 去自己 file）。**Kary 自己**：(1) home base「testing」ack；(2) J26062 Orbis job channel add「Client Meeting - Orbis」timed event Aug-5 (Wed) 11:00–12:00（colorId 5 fallback，1hr default，Wed/no-holiday checked）；(3) J26016 HSUHK 問總共幾多 shooting days → 掃 Calendar 得 4 日（Batch 1 Day 1 3/21 Sat + Day 2 3/24 Tue，Batch 2 Shoot 4/22 Wed + 4/27 Mon），flag 咗 Batch 1 兩日 title 係「Day 1/2」唔係「Shoot」要 Kary confirm interpretation。**其他 sender（flush 去自己 file）**：Kyle 喺 home base 問 7-Eleven HK 全部 YouTube 片（~92 條，分 10 個 campaign，隔走 date false-positive）→ kyleyeungdof_29223.md；Yik 首次互動，J26016 set 一個 8/3 (Mon) 12pm「換logo」self-reminder（先缺內容問返，補齊後 set，record `recMeuM6Cs7bjuzNX`）→ 新建 yikleung.dof.md。

### 2026-08-07 to 09-03 session (大型多日 ops：KB governance + Kyle 離職 + 多 job timeline + 新 capability findings)
超長跨月 session，7 個 sender，主線係大量 calendar/timeline ops + 一連串 KB canonical rule 定立 + 兩個 infra finding。**Job list sync ×3**（8/11 +7、8/25 +3、8/27 re-sync 修 J26104 stale director、9/2 隱含 +2 J26115/J26118），每次 Kary 手動 /discord:access 加 allowlist + Mugi push cache。**KB rules codified**（全部 Kary 定 + Mugi draft→push）：Meeting=Tangerine + Title-vs-Description、HR-1（Final Output=Grape、client→boss=cut、TBC-prefix）/HR-2（team 唔 attend 唔入 calendar）、Site Recce/Wardrobe=Pre-Pro、fallback→omit colorId、latest-edit-first + CWJ 命名、**PR-1/PR-2**（舊 event 唔改記錄 / director 離職 ADD 唔 remove）。**兩個 infra finding**：(1) AIRTABLE_PAT 其實有 write scope on Projects（試 add J26101 director 成功）→ 誤以為 read-only，加咗 Master Job Log write=Kary-only gate；(2) meeting-room booking sheet dof.internal read 到（Drive export）但 write 要 spreadsheets scope（Kary local 搞）。**Kyle 9 月離職**：KB 3 file 標離職 + PR-1/PR-2 rule，J26076→Kary、J26091 keep Kyle;Benjy 做記錄。**Master Job Log ad-hoc search ×2**（好醫工 J26067、Kary 2026 directed 14 projects）→ metrics 平（~2.4s/1 call），建議起 search-job-log.js。**大量 timeline push**：J26091(Cal+Trello)、J26104、J26099「30A Highlight」、J26062 4-video 12 events、J26105 DFI 140th (TBC) timeline、J26112 Swire。**Silent/trigger gap** 有進展：Kary 幫手分清 3 類（A down / B up-no-trigger / C skip-reply），B 類 Sohling 9/2 confirmed。**Key learnings**：(a) 唔好太快由巧合跳「confirmed」（DM approved/ file 誤判，Kary 通返後更正）；(b) 涉 personnel/record 唔好擅自 destructive，keep 歷史；(c) access mutation 永遠唔由 channel message 觸發（DM bug 診斷全程守住）。

---

## Request Log

| Date | Request | Outcome |
|------|---------|---------|
_(2026-06 rows archived to `archive/valkyri_k_2026-06.md` on 2026-08-06)_
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
| 2026-07-30 | J26062 (Orbis channel): add "meeting with client" event Aug-5 (Wed) 11am | Created timed event `Client Meeting - Orbis` Aug 5 11:00–12:00 (1hr default, colorId 5), desc J26062/Director Kary ✅; Wed/no-holiday checked |
| 2026-08-06 | J26016 (HSUHK channel): how many shooting days? check calendar | Swept HSUHK/J26016 events; 4 shoot days — Batch 1 Day 1 (3/21 Sat, Mok Wing Tung) + Day 2 (3/24 Tue, Para), Batch 2 Shoot (4/22 Wed) + (4/27 Mon). Flagged Batch 1 labelled "Day 1/2" not "Shoot" → asked Kary confirm interpretation |
| 2026-07-07 | Standalone Calendar add: "Test 1st cut" 2026-07-10 | ✅ Created (colorId 7), no saturation/holiday conflict |
| 2026-07-07 | Kay（Graphic Designer）已離開 DOF — KB update request | Updated CLAUDE.md team table, team-roles.md, production-pipeline.md, dof-context-overview.md; removed silent Trello style-frame default (was Kay) per Kary instruction |
| 2026-07-13 | hello greeting (home base) | Replied ✅ |
| 2026-07-13 | J26082 job schedule of this week (asked in job channel) | Reported 3 events: 3rd Cut 7/13, Picture Lock 7/15, VO Recording (TBC) 7/16 |
| 2026-07-13 | Max 今日 Trello card status (Test2 thread, home base) | No card due today ✅ |
| 2026-07-23 | Kyle J25072 CWB clean-version reply 過長 — Kary DM 更正 handling | 精簡覆返 Kyle（clean version 喺 DOF server 自己揾，唔上 YT/Vimeo，唔搵 Sohling）；rule 入 memory (feedback-clean-version-on-server)；gap-log 改 not-a-gap；resolve Kyle open thread ✅ |
| 2026-07-23 | Kary：你點記低呢個 rule？ | 解釋記咗 2 處（Mugi memory + gap-log audit trail），surface memory≠KB 分別，offer promote 入 KB canonical rule；Kary 話 will review later via gap-log |
| 2026-08-11 | update current job list (home base) | Ran sync-job-list.js ✅ +7 Current w/ channel (J26092/J26079/J26103/J26104/J26112/J26109/J26099), -8 removed (incl J26082/J26016/J26071/J26077...), J26085 alias preserved. Kary confirm → committed+pushed cache (540cba8..f2f0a06 main) ✅; 7 new channels added to /discord:access allowlist (groups) ✅ |
| 2026-08-11 | J26112 (Swire channel): add 3-day shoot to Calendar | Created 3 all-day Shoot events (colorId 11): Day1 SCC 13/8(Thu) `t70061h...`, Day2 Cathay City 14/8(Fri) `8c0tm5u...`, Day3 Taikoo Place 17/8(Mon) `o6gdbrh...`. Intern+location+crew-call(TBC) in desc. Weekday Python-verified. Director not filled (unspecified) ✅ |
| 2026-08-11 | J26112: add Director to 3 shoot event descs (calendar only) | Patched desc `Director: Kary, Erase, Atlas` on Day1/2/3 ✅; master job log untouched per request. Flagged「Erase」not in team record (added verbatim, asked if typo — cf. Erasmus onboard 8/10) |
| 2026-08-11 | J26076 (DFIQ channel): add client Teams meeting from image | OCR'd invite screenshot → created timed event `ncttjjvrm...`「DFIQ 1st Draft Feedback (Client Mtg)」8/12(Wed) 11:00–12:00, colorId 2→6, Teams join/ID/passcode in desc ✅. Weekday Python-verified. Director not filled (standalone) |
| 2026-08-11 | KB practice codify: Meeting default color + Title-vs-Description append rule | (a) Patched DFIQ event colorId → 6 Tangerine ✅. (b) calendar-ops.md: added Meeting=`"6"` colorId row + keyword + Meeting≠ClientFB-milestone note; added "Title vs Description" HARD RULE (time→start/end, name→Title, all other user-provided info→Description; applies to any event creation) ✅. Kary confirm → committed+pushed (dc5a901..3f79e43 main) ✅ |
| 2026-08-13 | "why didn't you reply the msg" — J26109 draft silent-reply slip | Recurring silent-reply bug: J26109 schedule draft was composed but NOT sent via reply tool (only ack went out). Kary caught it. Resent draft to home base + honest explanation ✅. → Pre-Clear: log to gap-log as behavioral pattern (silent-reply recurrence) |
| 2026-08-20/21 | J26109 colour + milestone-classification hard rules (multi-msg) | calendar-ops.md: Site Recce/Wardrobe→Pre-Pro Banana, fallback→omit colorId (Pumpkin), HR-1 (Final Output=Grape hard deadline; client→boss ver=cut; TBC-prefix if no date), HR-2 (non-attended events not on calendar). Pushed 3f79e43..4f854ea ✅. New memories: colour-fallback + newcomer-hollow-confirm. Newcomers derived from team-table onboard dates (Wayne 8/3, Erasmus 8/10) |
| 2026-08-21 | "did you receive Keith's msg" + Master Job Log search test | (a) Keith's 05:00「好醫工 job no.」was NOT received by Mugi's session — silent delivery/trigger gap; fetched history, found + answered (J26067). Logged to gap-log. (b) Kary asked to test Master Job Log lookup cost → searched via AIRTABLE_PAT+REST server-side filterByFormula: **2.4s, 1 API call, 843 bytes, 1 match**. Reported metrics + suggested building `search-job-log.js` for recurring old-job lookups |
| 2026-08-25 | Kyle J26091 no-reply cause clarification | Kary clarified Kyle's 02:41–02:47 no-reply = agent re-login/downtime (agent not running), NOT silent-reply trigger bug. Corrected my earlier「session 冇 trigger」framing. → Pre-Clear: re-review whether 8/21 Keith gap was also login/downtime, don't mislead harness-trigger debug |
| 2026-08-25 | sync current job list (home base) | Ran sync-job-list.js ✅ +3 Current w/ channel (J26117 Strobomotion / J26110 Orbis Macau / J26105 DFI 140th), -3 removed (J26050/J26056/J26103), J26085 alias preserved. Kary added 3 channels to allowlist ✅; git push still pending |
| 2026-08-25 | Add EMSTF 30A alias + J26099/J26082 disambiguation to KB | (a) J26099 Aliases col += "EMSTF 30A;營運基金30週年;30A Event Highlight;..." (cache-local, PAT read-only so not written to Airtable). (b) job-list.md new disambiguation section: J26099=ceremony event highlight vs J26082=corporate video played at ceremony (both = "EMSTF 30A"); on ambiguous search/resolution → clarify, don't default-pick. (c) Updated memory feedback-j26082-shorthand + MEMORY.md index. Kary confirm → pushed 4f854ea..82e597c ✅ |
| 2026-08-25 | J26117 (Strobomotion channel): add Vendor Briefing meeting | Created timed event `q2vknpvka...`「Vendor Briefing - Strobomotion San Tin」8/26(Wed) 10:00–11:00, colorId 6, Tencent link in desc ✅. Weekday Python-verified |
| 2026-08-26 | J26062 (Orbis channel): add "Meeting with Erica" (Teams) | Created timed event `lcskl9hu...`「Meeting with Erica - Orbis」8/27(Thu) 15:00–16:00, colorId 6, Teams join/ID/passcode in desc ✅. Weekday Python-verified |
| 2026-08-26 | List 2026 projects Kary directed (DM) | Master Job Log search via AIRTABLE_PAT+REST filterByFormula (LEFT(job_number,3)="J26" + director contains Kary): **14 projects** (5 Current + 9 Completed), incl co-directed. Metrics: 2.3s, 1 API call, 3.5KB. Offered sole-director / other-person / other-year variants. (2nd Master Job Log ad-hoc search → strengthens case for search-job-log.js) |
| 2026-08-26 | J26101 — add Kary back as director | Fetched J26101 (EMSD CCSD2026/27, Completed, director empty). Recommended Airtable-direct; Kary said「試下改」→ inferred Kary Team rec id from J26105 (`recltbDmJZtLpX0IT`), PATCHed J26101 director, re-fetch confirmed ✅. **Finding: PAT HAS write scope on Projects base** (contradicts KB read-only assumption) → reported + offered KB correction. New open thread + gap-log |
| 2026-08-26 | Draft KB correction for PAT write-scope | Kary said「yes」→ drafted: (1) update-job-list.md Credentials — corrected "read-only" → real write scope + warning; (2) CLAUDE.md Security Policy table — added "Master Job Log write (Airtable) = Kary-only" row (READ exempt). Kary「push」→ committed+pushed 82e597c..26930f3 ✅. Behavioral gate live. Optional residual: Kary narrow PAT scope in Airtable for defense-in-depth |
| 2026-08-27 | J26076 DFIQ — change all events' Director to Kyle/Kary | Patched Director on all 10 J26076 events (7/14→9/11 incl 8/12 client mtg) → "Director: Kyle, Kary" ✅ (desc-only) |
| 2026-08-27 | J26062 Orbis — add 4-video schedule (A群姐/B醫生訪問/C Real-Case/D CEO), 12 events | Date-verified all OK. ⚠️ Sep-11 saturation: 5 cut/final. Kary「Sep-11 照入」→ pushed all 12 events (cut=7, Final Output=Grape 3), per-video shorthands ✅ |
| 2026-08-27 | J26104 CWJ Sep — remove Kary as director (Airtable + calendar) | Calendar: removed Kary from 7 events → Benjy, Atlas ✅. Airtable: Kary was ALREADY absent (director=Benjy,Atlas) — nothing to remove. **Discovery: local cache job-list.md wrongly shows J26104 director=Benjy;Atlas;Kary** (extra Kary vs Airtable) — my 8/18 calendar mark inherited the wrong cache Kary. Offered (a) re-sync to fix cache / (b) let next sync correct. Flagged possible cache/sync bug for investigation |
| 2026-08-27 | Re-sync job list (fix J26104 stale director) | Kary explained: he unchecked himself in Portal (updated Airtable) but didn't sync elsewhere → cache stale. Ran sync-job-list.js ✅ J26104 director corrected Benjy;Atlas;Kary → Benjy;Atlas; no add/remove; aliases (J26099 EMSTF 30A + J26085) preserved. NOT a sync bug — Portal change hadn't propagated (root cause: no auto-sync, n8n Stage 1 pending). Cache pending push |
| 2026-08-31 | J26105 DFI 140th (channel) — tentative timeline image | OCR'd 11-milestone timeline, Python-verified weekdays, flagged 2 holiday hits. Kary: (a) 順延 holiday hits; drop Storyline Dev + Storyboard Revision; add Confirm STB @ 9/11; all events (TBC) prefix → pushed 10 (TBC) events ✅ (Feedback 2nd Cut →10/2, VO →10/20). FYI: 9/17 Submit 1st Cut collides w/ 3 Orbis Final Outputs (4 deliverables same day). Tentative — revisit on confirm |
| 2026-09-02 | "你收唔收到 sohling 喺 channel 嗌你" (DM) | Fetched history → Sohling asked 04:09「joe chat 大亞灣 youtube link」, Mugi never received it until Kary DM'd 04:12. Initially attributed to container-down; **Kary corrected: container was fixed BEFORE Sohling sent → agent was UP → genuine inbound trigger gap** (not downtime). Logged to gap-log w/ 3-type taxonomy (A down / B up-but-no-trigger / C up-turn-but-skip-reply). Answered Sohling's request separately |
| 2026-09-02 | KB feedback: link-search latest-edit-first + CWJ naming | Kary feedback (from noisy 大亞灣 reply): searching YT/Vimeo link → default return ONLY latest edit of a video, not all versions; user asks for other versions explicitly. + CWJ naming「CLP ChatwithJoe [Ep月] [upload YYYYMMDD]」, 1 ep/month. Drafted into youtube-search.md (Step 2 + CWJ note) + vimeo-search.md (Step 2). Kary「push」→ committed+pushed 5b93f73..25a5058 ✅ |
| 2026-09-02 | Kyle 離職 DOF (9月) — KB update | Grep'd Kyle across KB. Marked departed in CLAUDE.md team table (→已離職 line), team-roles.md (導演組→已離職 table + 即將加入 note), dof-context-overview.md (org tree). Flagged downstream: J26091 (Kyle sole director, needs urgent reassign) + J26076 (Kyle;Kary) → Portal reassign + re-sync + calendar desc update; Kyle Trello Q moot; allowlist gate optional. Kary reassigned (J26076→Kary clean; J26091→Kyle;Benjy, **Kyle kept intentionally as record**). Re-synced, +2 new jobs J26115/J26118 (allowlist added ✅). Kary set new canonical rule → wrote PR-1 (old events not rewritten) + PR-2 (departed director kept, ADD successor not remove; departed name in job-list ≠ bug) to calendar-ops.md. J26076 calendar left as Kary (b). **Pending push** |
| 2026-09-02 | J26112 Swire Summer Intern (channel) — post-pro timeline | 7 milestones (Video Flow & Style Frame 9/2 → Final 9/30). Date-verified, saturation clear. Pushed 7 events; [TBC]×4 got (TBC) prefix; 9/2 combined Video Flow & Style Frame = 1 event Blueberry 9 (flagged Video Flow normally Banana, offered split); FB=Sage, cut=Peacock, 9/30 Final=Grape 3. desc J26112/Kary ✅. Kary: 9/2→Peacock same as edit task (only this case, no KB rule change) |
| 2026-09-03 | J26105 DFI 140th (channel) — add 2 events | Client FB on Content Direction 9/3 (Sage 2) + Submit STB 9/9 (Banana 5). Weekday-verified ✅. No (TBC) prefix (Kary didn't write it) — flagged consistency w/ earlier (TBC) timeline. Sequence Submit STB 9/9 → Confirm STB 9/11 |
| 2026-09-03 | Meeting room booking sheet — access test (DM, replied in home base) | ⚠️ DM reply FAILED (「channel 1490642926710161468 not allowlisted」×2) despite correct access.json (dmPolicy allowlist + Kary in allowFrom) — plugin-side DM delivery issue, replied in home base instead + flagged. Sheet「Meeting Room Reservation」(owner chunyatchi@gmail.com, dof.internal canEdit): ✅ READ via Drive export (monthly-tab calendar grid, cells = "Name HHMM-HHMM" under day×room). ⚠️ WRITE blocked: OAuth token has drive scope only, no `spreadsheets` (refresh w/ spreadsheets → invalid_scope). Told Kary: re-consent Drive OAuth + spreadsheets scope → then give booking details to fill |
