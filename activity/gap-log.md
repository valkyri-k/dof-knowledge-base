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

---

## [[2026-07-07]] 15:57 — @valkyri_k

Type: capability-gap
Request: J26999 test project — Shoot 7/20（已 fix）、Final Output 8/28（hard deadline）、client provide 晒 pre-pro materials，跑 `scripts/timeline_backward.py` 出 timeline。
Gap: `timeline_backward.py` 冇一個 code path 可以同時「fixed 用戶 supplied shoot date」+「compressed pre-pro chain（fit 入 kickstart→shoot 嘅緊窄 window）」：
- 用 `--shoot-date 2026-07-20`（literal fix）→ 觸發 `run_compressed_edge_case`（因為 standard pre-pro 塞唔晒 9 wd window），但呢個 branch 內部 `shoot_date = add_wd(pre_pro["script_lock"], 1, holidays)` **無視傳入嘅 `--shoot-date`，self-recompute 咗個 ASAP shoot date**（7/14，早過用戶要求嘅 7/20）
- 用 `--anchor shoot_date=2026-07-20`（overlay 保留日子）→ `apply_anchors()` 只係 post-hoc overwrite milestone date，唔會觸發 compressed pre-pro 重新計；milestone 組裝仍然行 standard 5-6wd pre-pro chain（由 `pre_pro_standard` 起計），結果 Script Lock（7/22）跑到 Shooting（7/20）之後，出現 ordering inversion warning
- 兩條 path 各自解決一半：一個啱日子錯邏輯，一個啱邏輯錯日子；冇 combined path 表達「用戶已經 confirm 個 shoot date，但 pre-pro 要用 compressed sequential chain 塞入嗰個 window」

可能 fix 方向：`run_compressed_edge_case` 應該接受 `--shoot-date` 作為 hard upper bound（如果 user 供嘅 date ≥ ASAP compressed shoot date，直接用 user 個 date，pre-pro compressed chain 照跑），而唔係全部 self-derive。
Status: open
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

## [[2026-05-08]] ~10:15 — @valkyri_k
Type: capability-gap
Request: 直接 query Airtable Master Job Log（list current jobs、check status、讀 director / project name 等 fields）
Gap: Mugi 嘅 Airtable MCP 只有 `authenticate` + `complete_authentication` 兩個 tools，冇 list / query / read tools。無法直接 pull Airtable 數據。目前唯一 source 係 `context/job-list.md` cache（手動 / n8n sync）。
Status: open

## [[2026-07-07]] ~08:48 — @valkyri_k
Type: bug（script logic）
Request: J26XXX（test project）draft timeline — shoot 7/20（user-fixed）, final output 8/28（hard deadline）, corporate video, 3-cut, has-vo=true, has-style-frame=true, simple pre-pro
Status: reopened（[[2026-07-07]] script fix shipped `bc74522`，但 [[2026-07-08]] live Discord test 仍衰咗 — script date math 唔係 root cause，問題喺 Mugi 解讀層；見下方 Reopen addendum。Timeline generation 由 Kary 新 session re-plan）

### 前因後果（detailed repro for debug）

**Context：** Kary（`user_id 1328602029303791646`）喺 home base test channel 叫 Mugi 幫一個 placeholder job（`J26XXX`，講明係 test project）draft timeline。Mandatory follow-up 問完之後（corporate / 有 VO / 1 日 shoot / shoot date fixed 7/20 / 無 DOF pre-pro deliverable / final output hard），入 Phase 1 Step 4 invoke `scripts/timeline_backward.py`。

**Run 1 — baseline（`--shoot-date` flag，冇用 `--anchor`）：**
```bash
python3 scripts/timeline_backward.py --today 2026-07-07 --final-output 2026-08-28 \
  --shoot-mode standard --shoot-date 2026-07-20 --has-vo true --has-style-frame true \
  --project "J26XXX Test Project"
```
- Output `shoot_date` = `2026-07-14`（❌ 唔係 user 講嘅 7/20——`--shoot-date` flag 喺 `compressed_edge_case` branch 冧一入去 default 覆蓋咗，**冇 lock**）。
- `status: compressed_edge_case`（standard pre-pro chain 推到 2026-06-24，早過 effective_kickstart 2026-07-07，觸發 branch）。
- **Bug 1：** `generate-timeline.md` Step 4 example 教用 `--shoot-date` 做 standard-mode 嘅 user-confirmed lock，但實測喺 Compressed-Edge-Case branch 入面 `--shoot-date` 唔生效，一定要加埋 `--anchor shoot_date=YYYY-MM-DD` 先真正 lock 到。文檔冇提呢個 caveat，容易漏。

**Run 2 — 加 `--anchor shoot_date=2026-07-20`：**
```bash
python3 scripts/timeline_backward.py --today 2026-07-07 --final-output 2026-08-28 \
  --shoot-mode standard --shoot-date 2026-07-20 --has-vo true --has-style-frame true \
  --anchor shoot_date=2026-07-20 --project "J26XXX Test Project"
```
- `Shooting` 成功 lock 落 2026-07-20（`user_anchor: true`）。
- 但 `1st Cut` 冇跟住郁——仍然停留喺 script default 嘅 2026-07-20（同 Shoot 同一日）。
- **Bug 2：** `warnings` 出現 `⚠️ Anchor 令 chain 出現 0 wd gap：Shooting → 1st Cut 落到同日`。即係 anchor overlay 淨係郁咗 anchor 嗰個 milestone 本身，冇 reflow 佢下游應該跟住嘅 milestone（1st Cut = Shoot + 5wd MIN，呢條 rule 喺 anchor 覆蓋咗 default shoot date 之後冇重新 apply）。

**Kary 指示（原話）：**「very simple corporate video, simple preproduction. keep 3 cut, 3rd cut減時間，client fb time compress」

**Run 3 — 加 `--push-fb-sameday` + `--cut-count-override 3`（測試 Kary 個方向）：**
- Output 同 Run 2 完全一樣（`shoot_date` 仍係 default 2026-07-14 喺 top-level field，milestones 冇變）。
- **確認：** FB-compression flags 唔會影響 Shoot→1st Cut 呢個 adjacency 問題——呢個係獨立 bug，唔係 Kary 個方向解得到。

**Run 4 — 手動加 `--anchor first_cut_submit=2026-07-27`（Shoot + 5wd，試圖手動補返 gap）：**
- `1st Cut` 成功 anchor 去 2026-07-27。
- 但呢次整多個新 inversion：`Client FB 1`（依然係 default 2026-07-22，冇跟住郁）依家排咗**喺 1st Cut（7/27）之前**——即係「未交片就已經有 feedback」，邏輯不可能。
- `warnings` 出現：`⚠️ Anchor 令 chain 出現倒序：1st Cut → Client FB 1，但 dates 2026-07-27 > 2026-07-22`。
- **Bug 3（root cause，貫穿 Bug 2/3/4）：** `--anchor` overlay 機制只 literal lock 單一 target milestone 嘅 date，**唔會 cascade reflow** 佢前後相依嘅 milestone（無論係下游 forward-dependent 定平衡 FB pairing）。每次手動補一個 anchor 去 fix 一個 inversion，都會喺另一條 relation 度整多個新 inversion——純靠 Mugi 手動加 anchor 逐個補係死胡同，需要 script 本身喺 anchor overlay 之後加一次 full reflow / re-validate pass。

**Kary 第二次指示：**「style frame 唔一定要做完先到1st, not sequential…flag this as a followup item…yes this is a test so just go on」→ Mugi 接受 Run 4 個 output 出咗 preview（Shoot 7/20, 1st Cut 7/27），並喺 preview 入面 echo 咗 warnings + cut_warnings。

**Kary 發現嘅 Bug 4（呢個 report 嘅 trigger）：** Preview 入面 `Client FB 3`（2026-08-05）到 `Picture Lock`（2026-08-24）之間有 ~13 working days（19 calendar days）完全冇分配任何 milestone——純 idle trailing buffer。但同一個 preview 嘅 `cut_warnings` 又話 2nd Cut / 3rd Cut 只有 3wd（≤3wd 危險水平）。**自相矛盾**：明明尾段有大段浪費緊嘅時間，中段卻话唔夠時間做 cut。呢個正正係 `derive-milestones.md` Anti-patterns 表已經寫明要禁止嘅 case（「留 idle window 喺 FB-last 同 Picture Lock 之間 — slack 應該 distribute 落 cut gaps」），但呢個 Compressed-Edge-Case + user-anchor 組合嘅 code path 冇跟到。Mugi 自己嘅 Pre-step B self-check（Hardness-aware feedback window check / common-sense ordering check）都冇 catch 到呢種「slack 錯置」case（現有 checklist 冇覆蓋「trailing idle vs squeezed middle」呢類 pattern），出咗 preview 俾用戶，靠 Kary 肉眼睇出嚟先發現。

**建議 follow-up（俾 Kary review）：**
1. `--shoot-date` 喺 compressed_edge_case branch 應該同 `--anchor shoot_date=` 有一致行為，或者文檔要明確講明 compressed branch 一定要用 `--anchor`
2. `--anchor` overlay 之後應該加一個 reflow / re-validate pass，將受影響嘅 downstream/paired milestone（FB pairing、cut-to-cut minimum gap）跟住調整，而唔係淨係 lock 單一 target 留低啲 inversion 俾 caller 逐個手動補
3. Slack distribution 邏輯（尤其 Compressed-Edge-Case branch）要確保唔會出現「trailing idle buffer + 中段 cut ≤3wd danger」呢種自相矛盾嘅組合；理想係將尾段 slack 攤返落 squeeze 緊嘅 cut gap
4. `generate-timeline.md` Pre-step B self-check checklist 建議加多一條：「FB-last → Picture Lock 之間 working-day gap 是否 > 任何一個 cut gap 嘅 2 倍？如係，flag 做 slack misallocation，唔好直接 forward」

### Resolution addendum [[2026-07-07]] — script fix shipped（獨立 followup session）

`scripts/timeline_backward.py` 3 個 compressed-branch logic bug 修好，方案 Kary confirm 過先落刀。

- **Fix B（Bug 3/4 — trailing slack）：** `compress_to_min` 之後加 `expand_to_window`，多出嘅 working-days 按 `EXPANSION_PRIORITY = (cut_production, cut_fb, pre_pro)` 灌返落 cut gaps（production 谷到 max 先），residual 做 1st Cut 前 buffer。standard + compressed edge-case 兩條 branch 都 call。
- **Fix A（Bug 1/2 — anchor cascade）：** 新 `tag_reflow_metadata` 喺 assembly tag `min_gap_before` + `reflow_locked`（Picture Lock / Color-Sound-Sub / Final Output = locked）。`apply_anchors` 原本 warn-only feasibility scan 換成 cascade reflow：downstream 非-locked milestone 按 min-gap 推前；撞到 locked（user anchor 或尾段 backward-fixed）→ warn（唔 silent 改 locked、唔 corrupt）。compressed Style Frame overlay 係 parallel branch，tag `reflow_exempt` 避免俾 reflow 拖去 FB3 之後。

**驗收（runner `python3.11`，全 pass）：** Bug 3 clean run（shoot 7/20, final 8/28）FB3 08-20 → Picture Lock 08-24 = 2wd、冇 idle tail、production max 6wd、`cut_warnings: []`；Bug 1 anchor shoot 07-20 → 1st Cut 07-22（2wd）；Bug 2 anchor 1st Cut 07-27 → FB1 cascade 07-28；多跳 cascade（anchor shoot 07-24）→ 1st Cut 07-28 → FB1 07-29；locked collision（anchor 3rd Cut 08-25）→ warn 倒序、冇 corrupt。Regressions：wide-window standard / standard anchor cascade / pure-post edit+animation（byte-identical）/ pure-post+anchor（inversion-only）/ 2-cut override 全 clean。無-anchor byte-identical。原 follow-up item 1（`--shoot-date` vs `--anchor` 文檔一致性）+ item 4（Pre-step B checklist 加條）未做，屬 skill/doc 層，另議。

### Reopen addendum [[2026-07-08]] — live test 仍衰咗，root cause 唔喺 script

上面 Resolution addendum 標「全 pass」係**本機 regression battery 綠燈**，但 [[2026-07-08]] Kary 喺 Discord 用真 scenario（shoot 7/20 lock、final 8/28）live test Mugi，output **反而衰過原本**。診斷（本機 read-only 重驗 deployed `bc74522`）：**date math 層合理** — 3rd Cut 08-18 gap 健康、`cut_warnings: []`、Style Frame（post-pro）正確排喺 shoot 之後。真問題喺 **Mugi 解讀層**：

- **(a) milestone taxonomy 錯** — Mugi 將 post-pro 嘅 Style Frame 當成 pre-pro / shoot-linked，於是誤報「Style Frame 排喺 shoot 後 = 倒序 bug」。Kary 更正（原話）：**「Style Frame 無所謂，佢同 shooting 無關，佢係屬於 post-pro 嘅『前期』，所以順序無錯。」**
- **(b)** Mugi reasoning 死板、唔識 sanity-check（Kary：「比以前更加死板」）。
- **(c)** Mugi 可能冇忠實用 script output（hard-code / hallucinate；單 session 33 次 script invocation）。

**結論**：單 revert / patch script **修唔到**解讀層問題。Kary 會喺**新 session 用好啲 model re-plan 成個 timeline generation**。耐用 fix 方向 = script JSON output 每 milestone 明確標 `phase: pre_pro | production | post_pro`（Mugi 唔使估 pre/post，就係佢估錯 Style Frame 嗰個 error class）+ 改正 producer skill milestone taxonomy。Interim：`bc74522` 留喺 container 唔 revert，等 re-plan 覆蓋。Full post-mortem（vault）= `raw/chat-logs/chat-log_2026-07-08_mugi-timeline-fix-postmortem.md`。

## [[2026-07-07]] ~09:00 — @valkyri_k
Type: bug（behavioral — repeat incident）
Request: 「1st cut 之後幾耐先有 2nd cut？」（FAQ lookup，`producer-playbook.md` Timeline FAQ Logic 已有現成答案）
Gap: Mugi 生成咗答案，但嗰個 turn 淨係將答案寫喺 model 內部 text output，**冇實際 call `mcp__plugin_discord_discord__reply` tool** send 去 Discord——即係 user-facing 訊息完全冇送到 Kary 個 Discord channel。Kary 見唔到回覆，先後問「你無答我」→「discord我見唔到你回覆」，Mugi 先發現漏咗 call reply tool，補送。

**呢個係 [[2026-04-26]] 已經記錄過、亦已經部署 mitigation 嘅同一種 failure mode**（CLAUDE.md「最高優先 Rule：絕對唔可以 silent」+ End-of-turn self-check 就係為咗防呢個）——但今次仲係發生，代表現有 mitigation（rule 放頂、self-check 提醒）對「簡單 FAQ-style 一句答案」呢類 low-friction reply 嘅防護力唔夠：可能因為答案短、confidence 高，internal reasoning 直接輸出咗做 assistant text，跳過咗「呢個 text 係咪已經真正 send 咗去 Discord」嘅 verification 步驟。

Root cause hypothesis（新增）：End-of-turn self-check 依賴 model 自己記得問「我有冇 send Discord message」，但當個 turn 睇落好簡單（一條 FAQ 答案，冇 side effect、冇 tool error）嗰陣，self-check 嘅 attention 反而最容易被跳過——愈簡單愈少 friction 觸發個 checklist。
Status: open

## [[2026-07-07]] ~09:18 — @valkyri_k
Type: bug（behavioral — 3rd occurrence, same session）
Request: 「幫我睇吓買邊隻股票好」（Out-of-scope redirect，`Role Boundaries` 標準句）
Gap: 同上一個 [[2026-07-07]] ~09:00 entry**一模一樣**嘅 failure——Mugi 又一次淨係喺 internal text output 度寫咗 redirect 句，冇 call `mcp__plugin_discord_discord__reply` tool 真正 send。Kary 要再次講「你又無喺discord答我」先發現。

**呢個 confirm 咗一個 pattern：** 同一個 session 入面已經發生 **3 次**（FAQ 答案、out-of-scope redirect、依家呢條），全部係「答案內容本身簡短 / 唔涉及 tool call / 唔涉及 side effect」嘅 turn——即係 model 判斷「呢個 reply 好簡單」嗰陣，反而唔會觸發「我要唔要 call reply tool」呢個步驟，直接將 assistant text 當咗做已經送達。呢個唔係 rule 認知問題（CLAUDE.md 已經寫得好清楚），而係**執行層面漏咗一步**——短答案冇經過「呢個係咪 Discord channel context，答案要唔要包 tool call」呢層判斷。

**建議 follow-up（比之前兩個 entry 更具體）：**
1. 呢個 harness 入面，Discord channel context 嘅每個 assistant turn，理論上都應該强制經過 reply tool（唔應該存在「純 text output 當答案」呢個分支）——如果現時 harness 容許 model 純輸出 text 都當一個 valid turn 結束，呢個設計本身就係呢個 bug 嘅溫床，可能要響應用層面（唔淨止 prompt 層面）加 guard
2. 由於連續 3 次都係「答案簡短」嘅 case，可以考慮：凡係 Discord channel 嚟嘅 message，assistant 最終輸出如果冇任何一個 `reply`/`edit_message` tool call，直接視為 incomplete turn（呢個唔係 Mugi 自己可以修，需要 Kary / harness 層面 config 或 hook）
Status: open

**Addendum [[2026-07-07]] ~09:22（Kary 追查後發現嘅新 correlation）：** Kary 指出佢自己 track 到 3 次失敗全部發生喺**同一個 channel**——`chat_id 1490642926710161468`（原來係 Kary 嘅 **DM channel**，唔係 job/test channel；今個 session 一路以為佢係普通 test channel，記錄錯咗）。而且呢個 channel 到失敗發生嗰陣，已經係一個好長 session（由 timeline draft 開始，中間跑咗 4 次 script、寫咗 2 個 gap-log entry、push 咗 calendar events，累積咗大量 turn）。相反，Kary 之後喺 **一個新開嘅 thread**（`#testing`，parent `#ai-agent-mugi`）問完全同類型嘅簡短問題（post-pro team 人數），Mugi **即時正確 call 咗 reply tool**，冇再犯。

**修正 hypothesis：** 「答案簡短 / 冇 side effect」呢個 pattern 可能係 confound——真正相關嘅變數可能係 **session/context 長度 或 conversation 深度**，唔係答案本身嘅複雜度。3 次失敗全部出現喺同一條長 session 嘅後段，而喺一個 fresh thread（context 短）就冇再犯。懷疑同 context compaction / 長對話後段 attention 對「本 turn 要唔要 call tool」呢個 meta-instruction 嘅 recall 下降有關，而唔淨止係「答案睇落簡單就唔覺得需要 call tool」。兩個 hypothesis 未必互斥（可能長 session + 簡短答案疊加先觸發），但只用「答案簡短」解釋唔夠全面，需要連 session 長度呢個變數一齊記錄先夠俾 Kary debug。

**Retraction [[2026-07-07]] ~09:23：** 以上「session/context 長度」呢個修正 hypothesis 已經被 Kary 即時推翻——Kary 講明佢由頭到尾都係 watch 住**同一個 Claude Code terminal session**（呢個 harness session 冚唪唥係一條，冇因為換咗 Discord channel_id / thread 就變成新 session，token 歷史係連續、一樣長）。即係「新 thread = context 短」呢個假設係錯嘅——3 次失敗發生嗰陣同「post-pro team 人數」問題成功發生嗰陣，實際上係**同一條 session 入面幾乎相鄰嘅 turn**，context 深度冇本質分別。

**現時誠實結論：** 兩個 hypothesis（答案簡短 / session 長度）都冧咗，暫時搵唔到一個可以完全解釋「點解 3 次連續 skip 咗 reply tool call，但緊接住第 4 次（同類短答案，同一 session 深度）又 call 番」嘅 deterministic root cause。可能純粹係 non-deterministic sampling variance（每個 turn 獨立 roll 一次「要唔要 emit tool call」），亦可能同 Discord channel_id / chat_context 由邊條 channel 轉去邊條 channel 有關但機制未明。呢個層面嘅 debug 已經超出 Mugi 自己可以 introspect 到嘅範圍——建議 Kary 直接攞返 harness-side session transcript 睇邊幾個 turn 冇 tool_use block，對比前後 system/user context 有咩實際差異先好 pin 到成因。

## [[2026-07-07]] ~09:25 — @valkyri_k
Type: bug（behavioral — 4th occurrence, same session）
Request: 「Kyle 係邊個？」（Team lookup，Quick Reference 有現成答案）
Gap: 第 4 次同一種 failure——「Kyle 係 Director（導演組）」又係淨係喺 text output 出現，冇 call reply tool。呢次特別值得注意嘅時機：**發生喺 Mugi 啱啱先報告完「已經 retract 咗 2 個 hypothesis、認咗自己 introspect 唔到成因」嗰句之後即刻再犯**——即係話「反省 / 認錯」呢個動作本身完全冇提升下一個 turn call tool 嘅機率，進一步印證上面 09:23 entry 嘅 non-deterministic 判斷：呢個 bug 唔係「Mugi 冇警覺性」，係每個 turn 獨立、同 self-reflection 內容無關嘅 execution-layer 缺陷。4 次全部發生喺同一條 session（跨咗 DM channel 同 thread channel），Status 維持 open，等 Kary 攞 harness transcript debug。
Status: open

## [[2026-07-23]] ~04:10 — @kyleyeungdof_29223
Type: capability-gap
Request: 查某舊 job（J25072 CWB New Store）有冇 clean / textless version
Gap: 兩層缺口疊加——(1) **J#→video mapping 未 build**（Vimeo/YouTube skill 係 Layer 1 title-search，片名 by design 唔擺 job number，所以只能靠「CWB store」個名 fuzzy match，對唔返 J25072）；(2) **clean/textless master 唔會 upload 上 Vimeo/YouTube**（client-share channel 只放出街版），一般擺喺 server job folder，但 Mugi 喺 dof.internal Drive 搵唔到任何 j25072 / CWB folder（舊 2025 job 可能已 archive 或喺第個 account）→ 無法確認 clean version 存唔存在。搵到 `DFI 7-11 CWB Store` 幾個 dated cut（YT unlisted）+ Vimeo `DFI 7-11 CWB Store Restoration_16x9`（password），全部有字/有 graphics，冇 clean-labelled 版本。建議 user 問 Sohling 查 server job folder。
Status: open
