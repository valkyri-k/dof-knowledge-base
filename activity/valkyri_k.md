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
- **[2026-05-15] Trello member assignment — Sohling's sync jobs** — Calendar→Trello sync 跑完，但 J26062 Orbis、J26070 EMSD Farewell May、J26071 InvestHK 三個 job 嘅新 cards 冇 assign member（Sohling 未 specify 負責人）。等 Sohling confirm 邊個人處理先 assign。
- **[2026-06-05] J26050 CUHK 1st Cut Jun 11 saturation** — Jun 11 已有 4 cut events，加 CUHK 1st Cut 會係第 5 個。Jun 12 係 Client FB day 唔適合。Trello card 已建，Calendar event 暫扣。等 Sohling confirm (a) keep Jun 11 or (b) choose different date。

---

## Recent Session Summaries

### 2026-05-05 evening session
今晚主力測試 multi-channel dispatch（text v1 + OCR v2）。Text dispatch 兩輪跑得順（Orbis + BOC channel 各 tag 正確 assignees）。OCR v2 首次觸發：Kary post 手寫 note 圖，有 2 個 job block（快問快答 + 好E工）。Mugi 按舊版 skill file 拒絕（"1 image = 1 job" constraint），Kary 指出 skill file 已更新，constraint 已移除——Mugi re-read 後跑出 dry-run preview（2 block 全 resolve，快問快答→J26066/Katy，好E工→J26067/Sohling）。Kary 喺 confirm 前 clear，dispatch 未執行，留 open thread。另外：J26067 加咗 alias「好E工」（commit `3b3ddcd`）；Smart E status query 仍 ambiguous（J26060 vs J26065）未解。**Key lesson**：skill file 更新後 Mugi 必須 re-read，唔好 assume 記憶係最新版本。

### 2026-05-05 afternoon session
今日主要係兩個 status queries + bot infra 擴展。Kary 查 好醫工大賽（J26067）同快問快答（J26066）status，兩個都搵到。好醫工大賽 Calendar 只有 Shoot + Final，中間缺 cut milestones，Mugi 主動 surface 問係咪要補，Kary 未回應——留 open thread。快問快答確認係 J26066 quiz component，Final Output Quiz 後天（May 7）交。

主要 infra work：Kary 做 multi-channel dispatch test，先發現 channel 1489235328442302604 未 allowlist，Mugi 指示 Kary run `/discord:access group add`，加完即時 test 成功。之後 Kary 一次過 bulk add 14 條 channel（全部係 job-list 入面嘅 project channels），呢個係 production dispatch 功能嘅重要 milestone——Mugi 而家可以 push message 去任何 Current job 嘅 Discord channel。最後 Kary 叫 Mugi dispatch 提示去 J26065 CLP HKMA channel，confirm dispatch pipeline 端到端 work。

**Decision**：Multi-channel dispatch 係今日嘅重要里程碑，job-list.md 入面所有有 channel ID 嘅 job 而家全部可以 dispatch。Bot 基礎設施由「單一 #ai-agent channel」擴展到「全 project channels 覆蓋」。

### 2026-05-09 early morning session
主力係 J26071 Button InvestHK timeline full planning + J26053 BOC Trendy Together calendar add-ons。

J26071 方面：Kary post 咗 client schedule screenshot（pure post, motion graphics + footage, 1.5-2min, VO）。Phase 1 draft 係 8-milestone post-pro timeline（1st Cut May 26 → FO Jun 12，2-cut）。之後 Kary 大幅修訂：加入自訂 pre-pro milestones（Submit Script & STB May 14、Script Lock May 15）、Rough Cut（May 20）、兩個 client meeting events（May 11、May 13）、[16:9] cutdowns（Jun 18、Jun 26 TBC）、Submit Project Files SSD（Jun 30）——共 16 milestones。VO 做 Jun 10-11 multi-day event with "(1 Day)" remark。除 Final Output + SSD 外全部加 (TBC) prefix。Flag 咗 Jun 19 端午節（[16:9] 1st Cut 改去 Jun 18）。全部 16 events 一次過 push ✅。

J26053 方面：加 3rd Cut (#1) May 11 + (#2) May 12。另外喺 J26053 channel 加 Cover Design (#1 & 2) May 11——初次用 Banana (colorId 5)，Kary 即時 correct：Design 類應跟 Style Frame 用 Blueberry (colorId 9)。已更正並記入 memory。

**Key learning**：Design 類 deliverable → colorId 9 (Blueberry)，唔係 Banana。呢個係 Mugi 之前唔清楚嘅 color rule，而家固定落 memory。

**CLAUDE.md update（Kary 做）**：Per-job log 加咗 "Log-worthiness HARD RULE"——每一次互動（包括 identification reply、quick lookup）都要寫 entry，唔可以 skip。

### 2026-05-09 late afternoon session
J260YY Test Project 2 timeline planning + In-Discord Profile Correction Protocol test + root-owned files bug。

Timeline：Kary post 咗 client schedule image（MG + footage，1-day shoot，VO，Jun 15 deadline）。Mugi 攞 image → parse client schedule（Final Jun 15，filming window May 18-22）→ propose 3 shoot date candidates（May 18/20/22）→ Kary 揀 May 18 + 3-cut → `scripts/timeline_backward.py` 跑出 Compressed-Edge-Case 3-cut（effective kickstart May 12，Script Received May 11，shoot May 18，17 milestones）→ Phase 1 draft sent，pending confirm。期間 Kary 問點解 shoot date proposal step 用 inline Python 而唔係直接跑 script → 解釋：script 需要 `--shoot-date` argument，candidate proposal 係過渡計算，script 係 confirmed date 後先跑。Feature idea logged（dev-log）。

Profile Correction Protocol test：Kary 測試 add + remove test entry，兩步都成功。Remove 時 git push 失敗——`scripts/timeline_backward.py` root-owned，merge unlink 失敗。兩次 `sudo chown` 後 merge + push 成功（commit `2833b2d`）。Bug logged（dev-log）。

**Key learning**：root-owned kb files 係 recurring pattern（Apr 8 `.git/objects`，今次 `scripts/`），estimate 每次 Kary Claude Code session 改 kb files 以 root 跑。需要 permanent fix discussion。

### 2026-05-09 afternoon session
主力 test Phase 1 timeline generation workflow（Compressed-Edge-Case Branch）。J260ZZ Test Project 3：1 day shoot + VO + Jun 15 deadline。關鍵發現：May 9 = Saturday（唔係 Friday），effective_kickstart 正確移到 May 11。Standard pre-pro 唔 fit（Script Lock 需要 May 8 < kickstart May 11）→ Compressed-Edge-Case triggered。Compressed pre-pro (2 wd gaps) → Shoot May 19 (Tue)。Post-pro window = 14 wd，落入 14-19 wd range，flagged 2-cut vs 3-cut trade-off，Kary 揀 3-cut compressed（gaps 3+2+3+1+3+2 wd，FB2 = 1 wd 緊）。Phase 1 draft sent，等 confirm push Calendar（Phase 2 pending）。May 25 佛誕翌日 holiday + Saturday kickstart detection 兩個 date-handling checkpoints 都正確處理。

### 2026-05-09 night session
Fresh session after clear。主力係 J260YY Test Project 2 timeline test（兩輪），中間 Kary updated producer playbook。兩輪 setup 完全一樣：1-day shoot May 18，VO，style frame，Final Output Jun 15。兩次都跑出 Compressed-Edge-Case 3-cut（Script Received May 11，Shoot May 18，17 milestones，VO Jun 10-11，FO Jun 15），結果完全一致——playbook update 冇改變 script 輸出。Kary 兩次都確認「test passed, won't push」。值得記錄：Mugi 今晚 silent reply failure 一次——Working Style 答案打咗喺 terminal 但冇 send Discord reply，俾 Kary 發現（「你又做完嘢唔答我啦」）。**Lesson：Discord input 必須 Discord reply，唔可以只喺 terminal 完成，即使回覆已經喺 Claude Code output 入面。**

### 2026-05-09 post-night session
又一輪 Compressed-Edge-Case timeline test，今次係 J260AA Test Project 3（MG + footage, 1-day shoot, VO, style frame, Jun 15 deadline）。Flow 同 J260YY/J260ZZ 基本一樣：parse client schedule image → ask filming vs pure-post + shoot days → Kary confirm 1-day shoot + propose date + style frame → `timeline_backward.py` 跑出 Compressed-Edge-Case 3-cut (Script Received May 11, Shoot May 18, 17 milestones, VO Jun 10-11, FO Jun 15) → Phase 1 draft sent。Kary 即 clear，Phase 2 未執行。呢個 test pattern（新 session post-clear 馬上測同一 scenario）係 Kary 確認 playbook 更新後 script 輸出穩定嘅標準做法。

### 2026-05-09 evening session
Post-clear mini-session。Kary 喺 Discord 查詢 Pre-Clear Sequence 而家有幾多 step（答：7 steps）同 Step 5 係咩（Profile candidate detection）。跟住 Kary 指出頭先 pre-clear 冇跑足 7 steps——Steps 4+5 冇明確執行，只係 silent skip。Mugi 承認：Step 4（cross-update logs）is valid skip（冇 bug/gap），但冇記錄 skip 原因；Step 5（profile candidate detection）報「0」但冇 explicitly run 過 criteria check。**Decision：下次 pre-clear 必須明確 run + document 每個 step，即使 skip 都要講原因。**

### 2026-05-09 late night session (J26071 Trello assign verb test)
極短 session。Kary 喺 J26071 channel 發「assign Kary to send first cut tomorrow」測試 assign verb routing。Mugi 正確 route 去 Trello（唔係 Discord dispatch）——建立新 list「J26071 Button InvestHK」+ card「Send 1st Cut」，assigned Kary，due 2026-05-10，冇 label（director member + task 唔 match DIRECTOR_LABEL_MAP）。Kary 即確認係 test only → revert。Card archived，per-job log + user activity log entries 移除。**Observation：assign verb 喺 job channel context 正確 fall 去 Trello path（Skills Dispatch table），唔係 Discord dispatch path（Verb Routing table）——兩個 table 都有 assign keyword，Skills Dispatch 嘅 Trello trigger 覆蓋 Verb Routing 嘅 dispatch trigger，呢個 routing priority 係隱性嘅，日後如果有 conflict 可能要 clarify。**

### 2026-05-09 quick test session (J26071 remind verb)
Kary 喺 J26071 channel 測試 `remind` verb 行為。Mugi 落錯 path——直接 create Google Calendar event（「Remind: Send 1st Cut — InvestHK」2026-05-10 09:00 HKT），但按 kb/CLAUDE.md Verb Routing section，`remind` 係 reserved verb，應該 clarify 而唔係 fall through 去 Calendar。Kary 確認係 test only → 指示 revert。Calendar event deleted + activity log entries removed。Session 淨係 2 個 Discord messages + revert，冇實質 production change。**Key observation：Verb Routing section 喺 kb/CLAUDE.md 存在，但今次 session 嘅 system prompt 冇呢個 section（版本差異）——呢個係 test 嘅 context，唔係 Mugi violation。**

### 2026-05-10 evening session
J260BB 新一輪 — 主要發現同 fix 係 Discord reply tool 嘅 wrong param bug。Kary post 咗 client schedule image（Pre-pro→May15，Filming[no filming]，Post-pro May18-27，Review/Revisions May27-Jun12，Final Jun15，Remaining Jun30）+ 講明純後期、MG + footage edit、VO。Mugi parse image，識別 pure-post mixed mode，Jun 15 deadline。多次 Discord reply 嘗試全部 silent fail——root cause：Mugi 一直用 `content` / `message_id` param names，但 Discord plugin 要求 `text` / `reply_to`（Telegram convention 同 Discord convention 唔同）。React 成功（確認 channel ID valid）。CLAUDE.md 喺 session 中途由 Kary 更新，加入「Discord reply tool — args 命名」section 文件化正確 schema。用正確 `text` + `reply_to` params 重新 send → 成功。Send 咗 readiness gate questions（brief / alignment / materials / storyboard），等 Kary 答完先跑 script。**Key bug fixed：Discord reply tool schema 係 `text` + `reply_to`，唔係 `content` + `message_id`。**

### 2026-05-10 afternoon session
J260BB Test Project 4 pure-post timeline test。Kary post 咗 client schedule image（Pre-pro→May15，Post-pro starts May18，Final Jun 15，No filming）+ 講明 motion graphics + footage edit + VO。Mugi parse image → invoke `timeline_backward.py` (pure-post mixed, storyboard=none, kickstart May 11) → Phase 1 draft sent (Materials Ready May 11 → Final Output Jun 15, 3-cut, VO Jun 10-11)。關鍵發現：May 18 kickstart 會令 client FB 壓到 1 wd each (compressed floor)；May 11 kickstart 有 3 wd FB，但 materials 未必 ready 到 May 11（client pre-pro 仲未完）。Phase 2 pending confirm，同時 flag kickstart date 問題 + storyboard assumption。Single-Scenario Rule technically violated（跑咗兩次 script for kickstart comparison），但 judgment call：唔係為對比 standard/compressed，而係 resolve kickstart question；最終 reply 只 surface 一個 timeline（May 11）。

### 2026-05-10 morning session
本 session 係一系列純 behavior test，冇實質 production change。J260AA Test Project 3 timeline test：完整跑咗 image parse → clarify questions → candidate propose script → full timeline script，Compressed-Edge-Case 3-cut output 正常（Shoot May 18，17 milestones，VO Jun 10-11，FO Jun 15）；Phase 1 draft sent，Kary 即確認 test only → ignored。另外兩個快速 test：J26062 cross-job mention（@Mugi update J26071 timeline）→ Mugi 正確 detect cross-job + ask clarify intent；J26062 reminder verb test → Mugi 正確 trigger reserved-verb clarification flow。三個 test 全部 pass，無需 log 任何 architectural decision 或 capability gap。

### 2026-05-14 morning session (null)
Pre-clear 緊接上一個 session 再次觸發，中間冇新 work。Open threads 同上，冇新 entries。

### 2026-05-14 morning session (J26062 calendar ops + MCP bug fix)
今日主力係 J26062 calendar ops + 發現並修正 Google Calendar MCP bug。Kary 提供 Project Status Update docx（9 videos：C-series 6 + FVL F-series 3），job note 更新完成。然後批量加 F-series 9 events（[F-1/2/3] 1st Cut Jun 10 / 2nd Cut Jun 15 / Final Output Jun 17）——初次錯用 Google Calendar MCP，events 寫入 Kary 個人 calendar。Kary 指正後：刪走 9 個錯誤 events，用 service account 重建，再 patch colorId（cuts=`"7"` Peacock，Final Output=`"3"` Grape）。Root cause：由 MCP 轉 service account 嗰陣冇 re-read `technical/google-apis.md`。已儲 2 條 memory rule（no MCP + always apply colorId）。**Key learning**：Calendar ops 必須用 service account；colorId 係 mandatory，唔係 optional。

### 2026-05-10 to 2026-05-14 session
主要兩條工作線：J260BB timeline + J26062 calendar ops。

J260BB 方面：Kary 回答咗 readiness gate questions（DOF 寫 script + storyboard we-make，footage 預計 May 18 week，Jun 15 hard deadline）。跑 `timeline_backward.py`（pure-post mixed, storyboard=we-make, kickstart May 18）→ extreme squeeze（2 wd available，deficit 8 wd）。用 May 11 kickstart 重跑 → 仍然 extreme squeeze（7 wd，deficit 3 wd）。Mugi 按 playbook 發 extreme squeeze escalation 只列 3 個 post-side propositions，**Kary 即時指出 Mugi 冇建議壓縮 pre-pro 時間**——呢個係 Mugi behavior gap（跟足 script output 但冇獨立思考 pre-pro lever）。重跑 script with compressed pre-pro（script 2+2 wd, storyboard 3+1 wd, kickstart May 11）→ 可行（status pure_post_mode，kickstart May 21，12 wd post window，3-cut compressed feedback）。Phase 1 draft sent，Phase 2 pending confirm。

J26062 方面：Shooting Day 2 (Jun 2, all-day, 1-4pm in desc) ✅。然後 Kary 批量加 6 events：[C-1]/[C-2] 1st Cut May 21 + 2nd Cut May 27 + Final Output May 29（Orbis IG Reel，各有 video description）✅。Rules check 全 pass（三日都係 weekday，冇 holiday，saturation ≤ 3）。

**Key learning**：Extreme squeeze escalation 唔應只 relay script 嘅 3 post-side propositions——pre-pro compression 係獨立 lever，即使 playbook 冇 explicit mention 都要主動 surface。

### 2026-05-08 afternoon/evening session
今日兩個主要 work streams：job-list 擴展 + J26071 timeline。Job-list 方面：手動 patch 咗 J26071 Button InvestHK（Channel ID 1502220628424396821，Kary 係 Director），之後 Kary 自己喺 Airtable 做咗更大幅度更新——加 Director column + sync 晒所有 Current jobs，仲加咗 J26027 / J26075 / J26077 三條新 job，job-list 由 16 → 19 條。Kary 查 Airtable API 可用性：Mugi 只有 authenticate tools，冇 read/query tools，capability gap logged。

J26071 timeline：Kary 喺 #j26071 channel post 埋 client schedule（screenshot）+ 講明純後期、motion graphics + footage edit、無拍攝。OCR 攞到 client 嘅 phase dates，Final Output deadline = Jun 15。計算完：May 25 佛誕翌日係唯一假期影響排期；2-cut timeline（Option B）係唯一可以 hit Jun 15 deadline 嘅方案，3 cuts 最快都係 Jun 17+ miss deadline。Final Output = Jun 12，3 calendar day buffer。Saturation check 全 clear。Phase 1 draft sent，等 Kary confirm → push Calendar。

OCR dispatch 方面：今日成功執行兩輪 TEST dispatch（第一輪只有 task list，第二輪加埋 "submit by Wed 6 May" reminder）——兩輪都加咗 TEST label，正常 flow 通。May 5 嘅 open thread（dry-run pending）resolved。

### 2026-05-14 afternoon quick session
短 session，兩個 interactions：J26062 Timeline Schedule thread test message → auto-context 識別 reply；J26071 Submit Storyboard May 18 → Calendar event created (colorId 5 Banana，Mon weekday，唔係假期)。冇 architectural decision，冇 open threads 新增。

### 2026-05-15 afternoon session
今日兩條主線：J260CC timeline Phase 1 + Sohling 批量 Trello sync。

**J260CC Test Project 5**：Kary post 咗 client schedule image（no filming，motion graphics + footage edit，VO，hard deadline Jun 15）。Kary 補充：DOF 今日收 footage + assets，script confirm 預計今日，rough cut anchor May 20。Storyboard 係 internal progress update only，唔需要 milestone。Script 已 invoke `timeline_backward.py`（pure-post mixed，storyboard=none，kickstart May 15，rough_cut_submit=2026-05-20，has-vo=true，senior-approval-fb2-wd=2，deadline Jun 15）。Output：15 milestones（Materials Ready May 15 → Final Output Jun 15），3-cut all-compressed（all FB 1 wd），VO Jun 10–11。Pattern L triggered（window 16 wd，all client FBs forced to 1 wd）——must pre-arrange client same-day/next-day feedback。Phase 1 draft sent，Phase 2 pending confirm。

**Sohling Trello sync（4 requests）**：
1. HSUHK Batch 2 Calendar→Trello sync（Yik + Max）：scan J26016 Calendar events，compare vs existing Trello list，create missing cards。
2. EMSD GWIN Long version Calendar→Trello sync（Keith + Katy）：J26063 events → Trello cards。
3. Full job list Calendar→Trello comparison：掃 ALL current jobs，identify jobs 冇 Trello list / missing cards，batch create。J26062/J26070/J26071 有 cards created 但無 member 因 Sohling 未 specify。
4. Kary post-pro calendar gap check：識別 current jobs 喺 Calendar 冇 post-production milestone。

### 2026-05-29 to 2026-06-05 session (bulk infra + ops)
連續多日 ops session。兩次 job list sync (May 29, Jun 3): 新增 10 Current jobs，移除 6 個 (J26002/J26047/J26060/J26065/J26066/J26067)。Discord allowlist 擴展到 28+ channels，Kary 確認「batch add all missing」UX 改善——一個 terminal command trigger 即 Mugi 一次過 patch JSON。J26050 CUHK Closed→Current + channel linked + Airtable updated。J26062 Orbis [F-1][F-2][F-3] 日期更新（1st Cut→Jun 11，Final Output→Jun 16，client launch Jun 18 remark appended）。J26082 EMSTF 30A：先 prelim tentative timeline for client presentation（week-unit draft），後 confirmed timeline 13 events (Jun 8–Jul 20) pushed to Calendar + alias added。Sohling 首次觸發 Calendar+Trello：J26050 CUHK 7/8 events pushed（Jun 11 cut saturation → 1st Cut event 暫扣，Trello card 建咗），8 Trello cards created (Katy+Keith)。

---

## Request Log

| Date | Request | Outcome |
|------|---------|---------|
| 2026-05-05 | J26067 好醫工大賽 status query | Found Shoot Apr 27 + Final May 11; flagged missing cut milestones; Kary 未回應，留 open thread |
| 2026-05-05 | J26066 快問快答 status query | Confirmed quiz component: Shoot Quiz Apr 28 (done), Final Output Quiz May 7 (Thu), Farewell Party Shoot May 8 |
| 2026-05-05 | Multi-channel dispatch test: post to channel 1489235328442302604 | First attempt failed (not allowlisted); Kary ran `/discord:access group add`; retry succeeded ✅ |
| 2026-05-05 | Discord access: bulk add 14 project channels | All 14 job-list channels added to allowlist; Mugi can now dispatch to all Current jobs ✅ |
| 2026-05-05 | Dispatch reminder to Sohling in J26065 CLP HKMA channel | Sent to 1497160276196327424 ✅; end-to-end dispatch pipeline confirmed |
| 2026-05-05 | Smart E job status query | Ambiguous — resolved 2 candidates (J26060 CLP Smart E animation / J26065 CLP HKMA Smart E Living); asked Kary clarify |
| 2026-05-05 | Multi-channel dispatch: Orbis remind Sohling + BOC assign Kary & Sohling (dispatch test) | Sent to J26062 (#j26062) + J26053 (#j26053) ✅ |
| 2026-05-05 | Multi-channel dispatch round 2: Orbis remind Sohling find Kary + BOC assign Kary find Sohling | Sent to J26062 + J26053 ✅ |
| 2026-05-05 | OCR dispatch v2 triggered (2-job image, 快問快答 + 好E工) | Declined x2 (old constraint) → Kary corrected skill file update → re-read → dry-run preview sent; pending confirm before clear |
| 2026-05-05 | J26067 alias 「好E工」added to job-list.md | Commit 3b3ddcd ✅ |
| 2026-05-05 | OCR dispatch v2 TEST round 1 (快問快答→Kay / 好E工→Sohling, TEST label) | Sent to J26066 + J26067 ✅ |
| 2026-05-05 | OCR dispatch v2 TEST round 2 (same 2 blocks + "submit by Wed 6 May", TEST label) | Sent to J26066 + J26067 ✅ |
| 2026-05-08 | Add J26071 Button InvestHK to job-list (Channel 1502220628424396821, Director: Kary) | Commit 351f9c0 ✅ |
| 2026-05-08 | Query: job-list 有冇 Director column | 回覆冇，問係咪要加；Kary 自己 Airtable sync 更新 |
| 2026-05-08 | Job-list Director column + J26027/J26075/J26077 added (Kary direct edit) | Acknowledged ✅ |
| 2026-05-08 | Query: Airtable API 可用性 | 只有 auth tools，冇 read/query；gap logged |
| 2026-05-08 | Hello in J26016 channel | Replied ✅ |
| 2026-05-08 | J26071 timeline request (pure post, motion graphics + footage, VO, 15 Jun deadline) | Phase 1 draft sent: 8 milestones, 1st Cut May 26 → Final Output Jun 12, 2-cut Option B ✅ |
| 2026-05-09 | J26071 + J26062 job lookup queries | Answered both ✅ |
| 2026-05-09 | J26071 full timeline: 16 events incl. pre-pro, Rough Cut, client meetings, [16:9] cutdowns, SSD | All 16 pushed ✅ (May 11–Jun 30); flagged Jun 19 holiday → Jun 18 |
| 2026-05-09 | J26053 add 3rd Cut (#1) May 11 + (#2) May 12 | Created ✅ |
| 2026-05-09 | J26053 add Cover Design (#1 & 2) May 11 (wrong color Banana → corrected to Blueberry) | Created + colorId corrected ✅; Design color rule saved to memory |
| 2026-05-09 | J260ZZ Test Project 3 timeline planning (MG + footage, 1-day shoot, VO, Jun 15 deadline) | Phase 1 in progress — asked follow-ups re: filming vs pure-post + shoot days |
| 2026-05-09 | J260ZZ: confirmed 1-day shoot, propose date | Compressed-Edge-Case triggered (May 9=Sat → kickstart May 11); proposed Shoot May 19; flagged 2-cut vs 3-cut |
| 2026-05-09 | J260ZZ: Kary chose 3-cut | Full Phase 1 draft sent (17 milestones, 3-cut compressed, gaps 3+2+3+1+3+2 wd); awaiting confirm for Phase 2 |
| 2026-05-09 | Query: Pre-Clear Sequence 幾多 steps + Step 5 係咩 | 答：7 steps；Step 5 = Profile candidate detection，draft 入 Pending Profile Review，唔 self-promote |
| 2026-05-09 | Kary 指出 pre-clear Steps 4+5 冇明確執行 | 承認：Step 4 valid skip 但無記錄原因；Step 5 報「0」但未 explicitly run criteria check |
| 2026-05-09 | J260YY Test Project 2 Phase 1 timeline (1-day shoot, VO, style frame, Jun 15 FO) | Compressed-Edge-Case 3-cut sent (17 milestones, Shoot May 18); pending Kary confirm → Phase 2 |
| 2026-05-09 | Query: 點解 shoot date proposal 用 inline Python | Explained §5 needs confirmed --shoot-date; feature-idea logged dev-log `55bee33` |
| 2026-05-09 | Profile test: Working Style add "test entry — please remove" | Added ✅ (commit `9be29e4`) |
| 2026-05-09 | Profile test: Working Style remove "test entry — please remove" | Removed ✅ (commit `2833b2d` after 2x chown fix) |
| 2026-05-09 | root-owned scripts/timeline_backward.py bug (git merge unlink failed) | Logged dev-log `41e887f`; Kary ran 2x chown; merged + pushed `2833b2d` ✅ |
| 2026-05-09 | J260YY Test 1: timeline (fresh session, client schedule image, 1-day shoot, May 18) | Compressed-Edge-Case 3-cut Phase 1 draft sent; Kary: test passed, won't push |
| 2026-05-09 | Working Style query | Silent reply failure (terminal only); Kary caught it; resent Discord reply ✅ |
| 2026-05-09 | J260YY Test 2: playbook updated, re-run same parameters | Same output (Compressed-Edge-Case 3-cut, identical milestones); Kary: test passed, won't push |
| 2026-05-09 | J260AA Test Project 3 timeline (MG + footage, 1-day shoot, VO, style frame, Jun 15 deadline) | Parsed client schedule image (Pre-pro→May15, Filming May18-22, FO Jun 15); asked filming vs pure-post + shoot days |
| 2026-05-09 | J260AA: confirmed 1-day shoot + propose date + style frame = yes | Ran timeline_backward.py → Compressed-Edge-Case 3-cut (Shoot May 18, 17 milestones, VO Jun 10-11, FO Jun 15); Phase 1 draft sent; awaiting Kary confirm |
| 2026-05-09 | J26071 test: "remind Kary to send first cut tomorrow" | Mugi created Calendar reminder event (wrong path — should clarify per Verb Routing rule); Kary: test only → revert |
| 2026-05-09 | Revert test: delete Calendar event + activity log entries | Calendar event tgq8568jmv65lr5139fcv5rdq4 deleted; log entries removed ✅ |
| 2026-05-09 | J26071 Trello assign verb test: 「assign Kary to send first cut tomorrow」 | Routed to Trello: new list + card created → Kary: test only → card archived + log entries removed ✅ |
| 2026-05-09 | J260AA Test Project 3 timeline planning (client schedule image, MG + footage, 1-day shoot, VO, Jun 15 deadline) | Parsed image → asked shoot days → ran candidate+full timeline scripts (Compressed-Edge-Case 3-cut, Shoot May 18, 17 milestones) → Phase 1 draft sent → Kary: test only, ignore ✅ |
| 2026-05-09 | J26062 cross-job mention test: @Mugi update J26071 timeline | Detected cross-job, clarified intent → Kary: test only, ignore ✅ |
| 2026-05-09 | J26062 reminder verb test: 「remind Kary to send 1st cut tmr」 | Triggered reserved-verb clarify flow → Kary: test only, ignore ✅ |
| 2026-05-10 | J260BB Test Project 4 timeline re-request (new session, client schedule image, pure-post mixed, VO, Jun 15 deadline) | Identified pure-post mixed mode; multiple Discord reply attempts failed (wrong params `content`/`message_id`); CLAUDE.md updated mid-session with correct schema; finally sent readiness gate questions using `text`/`reply_to` ✅; waiting Kary answers |
| 2026-05-10 | J260BB: Kary answered readiness gate (DOF script+storyboard, footage ~May18, Jun 15 hard) | Ran script (kickstart May18) → extreme squeeze 2wd; re-ran (May11) → extreme squeeze 7wd; sent escalation |
| 2026-05-10 | J260BB: Kary direction — compress feedback + keep 3 rounds + 1st cut 3wd; pointed out Mugi missed pre-pro compression | Re-ran script with compressed pre-pro (script 2+2, storyboard 3+1) → feasible; Phase 1 draft sent ✅; Phase 2 pending |
| 2026-05-12 | J26062 add Shooting Day 2 - Orbis Future Vision Leader, Jun 2 all-day, 1-4pm in desc | Created ✅ (colorId 11) |
| 2026-05-14 | J26062 batch add 6 calendar events: [C-1]/[C-2] 1st Cut May 21, 2nd Cut May 27, Final Output May 29 (Orbis IG Reel) | All 6 created ✅; rules check pass (no holiday, no saturation) |
| 2026-05-14 | J26062 update video list from Project_Status_Update_Orbis_HK_2026_Campaign.docx | Job note updated: C-series 6 videos + FVL F-series 3 videos ✅ |
| 2026-05-14 | J26062 F-series 9 events: [F-1/2/3] 1st Cut Jun 10 / 2nd Cut Jun 15 / Final Output Jun 17 | Created via service account on DOF Internal calendar; colorId patched (cuts=7 Peacock, FO=3 Grape) ✅ |
| 2026-05-14 | Bug: Google Calendar MCP → wrote to personal calendar (9 events) | Deleted wrong events; recreated via service account; saved 2 memory rules (no MCP + always apply colorId) ✅ |
| 2026-05-14 | J26062 Timeline Schedule thread test message | Auto-context detected J26062 Orbis；Discord reply sent ✅ |
| 2026-05-14 | J26071 add Submit Storyboard May 18 to Calendar | Created event (colorId 5 Banana, Mon weekday, no holiday) ✅ |
| 2026-05-14 | J260BB Test Project 4 Phase 1 timeline (new round: client schedule image, pure-post mixed, VO, storyboard 18 May, rough cut 20 May, hard deadline 15 Jun) | Phase 1 draft sent: 15 milestones (kickstart 15 May → FO 15 Jun, 3-cut, all cut/FB windows 1-2 wd, VO Jun 10–11); 25 May 佛誕 holiday handled; Pattern L warning issued; Phase 2 pending Kary confirm |
| 2026-05-15 | J260CC Test Project 5 Phase 1 timeline (client schedule image, pure-post mixed, no filming, VO, hard deadline Jun 15, rough cut anchor May 20) | Phase 1 draft sent: 15 milestones (kickstart May 15 → FO Jun 15, 3-cut, all FB 1 wd compressed, VO Jun 10–11); Pattern L warning issued; Phase 2 pending Kary confirm |
| 2026-05-15 | Sohling: HSUHK Batch 2 Calendar→Trello sync (Yik + Max) | Scanned J26016 Calendar; created/updated missing Trello cards with Yik + Max members ✅ |
| 2026-05-15 | Sohling: EMSD GWIN Long version Calendar→Trello sync (Keith + Katy) | Scanned J26063 Calendar; created Trello cards with Keith + Katy members ✅ |
| 2026-05-15 | Sohling: full job list Calendar→Trello comparison + sync | Compared all current jobs; created missing cards; J26062/J26070/J26071 cards created without member (Sohling 未 specify) — open thread |
| 2026-05-15 | Kary: post-pro calendar gap check (which current jobs 冇 post-pro milestones in calendar) | Identified jobs with no post-production Calendar events; reported list to Kary |
| 2026-05-29 | Job list sync | 3 addedWithChannel (J26082/J26024/J26085), 4 addedNoChannel, 6 removed (J26002/J26047/J26060/J26065/J26066/J26067) ✅ |
| 2026-05-29 | Discord allowlist: 7 new channels added | J26082/J26024/J26085/J26058/J26089/J26081/J26020 ✅ |
| 2026-05-29 | J26050 CUHK: Airtable status→Current, discord channel set, job-list synced | ✅ |
| 2026-05-29 | J26050 Discord allowlist add (1509800199588020284) | ✅ |
| 2026-05-29 | J26062 Orbis [F-1][F-2][F-3] date update: 1st Cut→Jun 11, FO→Jun 16, launch remark appended | 6 events patched ✅ |
| 2026-06-03 | Job list sync | J26091/J26056/J26084 addedWithChannel; J26089 removed ✅ |
| 2026-06-03 | Discord allowlist batch add 6 channels (J26007/J26010/J26056/J26057/J26084/J26091) | All 6 in one terminal invoke ✅ |
| 2026-06-04 | J26082 prelim tentative timeline for client presentation | Week-unit draft; Jun 19 holiday flagged ✅ |
| 2026-06-04 | J26082 EMSTF 30A confirmed timeline: 13 Calendar events (Jun 8–Jul 20) + alias added | ✅ |
| 2026-06-05 | Sohling: J26050 CUHK Calendar (7/8 pushed, Jun 11 saturation pending) + Trello (8 cards, Katy+Keith) | ✅ |
