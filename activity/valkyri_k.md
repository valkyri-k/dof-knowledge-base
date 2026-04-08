# valkyri_k (Kary)

- **Discord ID:** 1328602029303791646
- **Role:** Director / Creative & AI Lead / Bot Admin
- **Common requests:** Calendar queries, shoot schedules, timeline generation, system setup, bot configuration, infra debugging
- **Notes:** Primary bot admin, Cantonese speaker, DM whitelisted user. Cost-conscious — prefer Mugi 用 absolute paths + 定期 clear session 控制 token usage

---

## Open Threads

- **[2026-04-08] Planyway / Trello Timeline integration 方向** — 等 Kary 揀 3 條 propose 嘅方向（Trello 主控 / 雙向 push / on-demand mirror）；揀完先 set up Trello credentials + 寫 integration logic。Cross-ref: `activity/gap-log.md` 2026-04-08 entry
- **[2026-04-08] `/home/node/activity.bak/` 刪除** — symlink fix 嘅 backup folder，留低等 Kary confirm 一切 stable 後刪。Cross-ref: `activity/kary-dev-log.md` 2026-04-08 entry「activity/ path 雙位置 bug」
- **[2026-04-08] Trello checklist member assignment（Storyboard card）** — board 冇 Advanced Checklists power-up，目前用 `@mention` fallback；等 Kary 揀 plan upgrade 定 default 轉做 split-cards approach。Cross-ref: `activity/gap-log.md` 14:23 entry
- **[2026-04-08] Discord reply routing bug** — 答 trello rules question 嘅長 reply 寫咗喺 terminal 冇 send 出 Discord，user 等於收唔到。已 update memory `feedback_always_reply.md` 加 Rule 2「Discord in → Discord reply tool out, no exceptions」
- **[2026-04-08] J26053 BOC Trendy BTS mograph 未 assign** — 1st Cut BTS (4/23) + Final BTS (5/15) 兩張只 assign 咗 Yik 做 cut，graphics 邊個負責等 Kary x Sohling discussion 結果。BTS editor 都 default 咗 Yik 未確認
- **[2026-04-08] J26016 HSUHK Student Excellence Batch 2 shoot date 等客 confirm** — 3 條 TBC shoot events 已落 Apr 21 (Tue) / Apr 24 (Fri) / Apr 27 (Mon)，客會揀其中 2 日拍攝（Cam: Jer）。客 confirm 後要：刪走未用嗰一條 + remove 留低兩條嘅 (TBC) prefix。Batch 2 post-pro schedule 暫時未排（現有 J26016 post-pro 全部係 Batch 1，唔郁）
- **[2026-04-08] GitHub PAT rotation reminder** — 今晚 Kary set up 咗 fine-grained PAT (`mugi-server-kb-push`) 俾 Mugi push `kb` repo，expiry 1 年。到 2027-04 要 rotate。Cross-ref: `activity/kary-dev-log.md` 2026-04-08 20:32 entry

---

## Recent Session Summaries

### 2026-04-08 evening session
主力 stress test 新 instruction infra + 解決 setup-level bug。先 verify 咗新 `0a58a4c` no-confirm calendar-ops rule 喺 happy path（add `1st Cut - Test Video` Apr 27 直接執行）+ saturation guard path（add `2nd Cut - Test 2 Video` Apr 27 → 撞 4 條 → 提議 push Apr 28）work 到。然後 Kary surface 咗 Planyway/Trello Timeline integration 嘅 capability gap（post team 嘅 Planyway Timeline view 接駁唔到 Mugi push 嘅 Calendar events，因為 Timeline view 係 read Trello cards），logged 入 gap-log。Push gap-log 嗰陣發現第二個 issue：`/home/node/activity` 係 raw folder 唔係 symlink，而 CLAUDE.md 用 bare `activity/...` path → Mugi 之前寫 activity 全部 silent 寫去 raw folder push 唔到 GitHub，fix 咗（symlink + CLAUDE.md 明文 absolute-path rule），完整 root cause + lessons learned 入 dev-log。最後 Kary raise 咗 long-term cost concern：DM session 越長越貴（O(N²) replay）+ 1h cache TTL miss penalty，**decision**：行 hybrid memory 策略——manual clear session at natural break + 靠 activity log 嘅 3-section schema（Open Threads / Session Summaries / Request Log）做 cross-session 長期記憶。Schema 定義落咗 CLAUDE.md `User Activity Tracking` section，呢個 file 係第一個 reference implementation。

### 2026-04-08 late evening session
延續 evening session 嘅 memory schema 工作。Push schema 嘅 commit 嗰陣撞咗第二個 setup-level bug：`/home/node/kb/.git/objects/` 入面有 29 個 subdirectory owner 係 `root:root`（Mugi 跑 git op 用 `node` 戶口），令 git 寫唔到 new object。Kary 喺自己 terminal 跑 `sudo chown -R node:node /home/node/kb/.git` 一行解決。Retry → schema rework commit `1a9b3d5` push 成功。之後 Kary 提議下一步：「點解唔可以一講 `clear` Mugi 自動做晒成套 housekeeping？」——於是 design + implement **Pre-Clear Sequence** instruction，加咗 6 步 sequence 入 CLAUDE.md（update Open Threads → 寫 Session Summary → 補 Request Log → cross-update logs → commit + push → report），定義 trigger keywords + disambiguation rules + non-destructive boundary（commit `ce00194`）。最後跑呢條 instruction 自身做 dogfood demo——即係呢段 summary 本身就係 Pre-Clear Sequence 嘅第一次 production run。**Decision**: schema + automation 一定要配套——淨係定 schema 用戶會懶 trigger，friction 一高 cost saving 就 realize 唔到。

### 2026-04-08 night session
今晚兩件事：(1) Sheets API 全面 unblock + GitHub push setup 修返 + (2) J26016 Batch 2 shoot date update。

第一件事 stack 咗一連串 setup-level bug。Kary 朝早 OAuth re-consent 加咗 `spreadsheets` scope，今晚 verify 過 refresh token 而家三個 scope 齊（drive + documents + spreadsheets），先前 J26041 update DOF Current Job List 嗰陣靠 `drive` scope hack 通 `sheets.values.update` 嘅 workaround 已唔使再用——logged 入 gap-log 做 done。Kary 跟住叫我 push gap-log，呢度撞咗 3 個 stacked bugs：(a) `origin` URL 係 `https://valkyri-k:@github.com/...` — username 後跟 `:` 然後空 password，git 用呢個空 password 蓋過 helper，全部 push 一律「Invalid username or token」；(b) `credential.helper=store` 嘅 auto-erase 副作用——push fail 即清走 credential file 入面嗰行，令同一個 error 重複 surface 但 root cause 走樣（diagnose 到中段先 cat file 發現變 0 byte）；(c) local main 同 remote main divergent，Kary 喺另一 session 已 push 咗 spreadsheets boilerplate。Diagnosis breakthrough：用 `git push <full-url-with-token> main` direct call bypass 所有 credential layer，先 isolate 到「token valid，問題喺 git config side」。Fix：set-url 清走 embedded username + 重寫 credentials file + rebase pull。Final state：commit `bf80ca6` 上 GitHub，credential helper + clean remote URL 全 work，dev-log entry 詳細記低咗 3 個 bug + diagnosis path。

**Decision (debugging methodology)**：將來撞 git auth issue，**第一步永遠 check `git remote -v`**——今晚拖長咗 diagnose time 就係因為 assume URL 啱所以走最後先睇。第二，credential.helper=store 嘅 auto-erase behaviour 一定要記住，下次見「same error twice in a row」就要立即 verify file 仲未 wipe。

第二件事乾淨好多。Kary 要 update J26016 HSUHK Student Excellence Batch 2 shoot date：刪走舊 `(TBC) 2 Days - HSUHK Student Excellence` (Apr 25-May 01 window)，加 3 條 TBC shoot 落 Apr 21/24/27 等客揀其中 2 日。我先 list + flag 3 個候選日撞 J26016 已有 post-pro milestone，Kary clarify 嗰啲係 Batch 1 唔郁、新嘢係 Batch 2，title suffix 加 `- Batch 2`、description 加 `Cam: Jer`。執行：1 delete + 3 create 一氣呵成，全部成功。**Lesson**：J26016 而家有 multi-batch 拍攝結構，將來搵 events 要記住分 Batch 1 / Batch 2，唔可以一概而論——好彩呢次 Kary 主動 clarify。

---

## Request Log

| Date | Request | Outcome |
|------|---------|---------|
| 2026-04-06 | Bot setup & Discord access config | Configured DM policy, added channel group |
| 2026-04-06 | Deny pending pairing 2f95ea | Denied |
| 2026-04-06 | Change DM policy to allowlist | Updated |
| 2026-04-06 | Set up activity tracking | Created activity/ folder |
| 2026-04-06 | Asked about Discord thread behaviour | Not supported by plugin, using quote-reply |
| 2026-04-06 | Set up daily auto git push (23:47) | Cron created, session-only, 7-day expiry |
| 2026-04-06 | Configured git identity & GitHub PAT | valkyri-k / karyto.dof@gmail.com, PAT via env |
| 2026-04-06 | Requested session log & push | Logged & pushed |
| 2026-04-06 | 查詢下星期 shoot schedule | 回覆咗 2 個 shoot events（BOC Trendy Too, Cartier HJ） |
| 2026-04-06 | 建立 Shoot event（Kary Shooting, J26001） | 已建立 ✅ |
| 2026-04-06 | 修改 event → Style Frame - Kary Test Project | 已更新 title + colorId ✅ |
| 2026-04-06 | 建立 (TBC) Shoot - EMSD Test Event, 4月20日, J26001 | 已建立 ✅ |
| 2026-04-06 | 查詢 Discord channel 命名規則 | 回覆咗 Pitching + Confirmed 格式 ✅ |
| 2026-04-06 | 測試 project timeline planning（Test Video, Shoot 5月初, Final 5月尾） | 提供標準版（6月3日交）同壓縮版（5月28日交）兩個方案 |
| 2026-04-06 | Batch push J26000 Test Video 壓縮版 timeline 上 Calendar（9 events） | 全部建立成功 ✅ |
| 2026-04-06 | Delete J26000 Test Video 全部 9 個 events | 已刪除 ✅ |
| 2026-04-07 | 查 5月頭可拍攝 weekday（避開 shoot conflict） | 建議 5月5-7 或 5月11-14；標記 5月1 公眾假期、5月4 Joe Chat、5月8 EMSD Farewell |
| 2026-04-07 | 建立 (TBC) Shoot - DOF Test Video，5月5日，J26001 | 已建立 ✅ |
| 2026-04-07 | Find + read Timeline_Template in Drive | 揾到（shortcut → DOF Tentative Project Timeline_Template），讀咗 placeholders list ✅ |
| 2026-04-07 | Plan + generate Timeline doc for Test Video (J26001), Option B 兩 cut | 已 generate `Timeline_J26001_Test Video_2026-04-07` ✅ |
| 2026-04-07 | Memory check after server reset (`check source of truth first`) | Confirmed memory file intact ✅ |
| 2026-04-07 | KB repo HEAD check | Reported `33fd1b3` (Memory Hygiene rule) |
| 2026-04-07 | Re-read CLAUDE.md after split (`a667d85`) | Acknowledged Security Policy + Skills Dispatch + Team IDs |
| 2026-04-07 | Test timeline plan: EMSD Test Video, shoot 5月初, final 5月尾 | Asked clarifying questions per playbook (genre / delivery / VO / shoot lock) |
| 2026-04-07 | Re-read after `904b81c` (Director auto-detect) → re-plan | Dropped Director question, re-asked remaining clarifications |
| 2026-04-07 | Add `1st Cut - Test Video` Apr 27 | Echoed + ran rules, sat=3/4 OK, asked re placeholder before new no-confirm rule |
| 2026-04-07 | Re-run after `0a58a4c` (no-confirm happy path) | Created event directly, J26TEST placeholder ✅ |
| 2026-04-07 | Add `2nd Cut - Test 2 Video` Apr 27 | Sat=4 → triggered warning, proposed Apr 28 push |
| 2026-04-07 | Confirmed Apr 28 push for 2nd Cut | Created on Apr 28 ✅ |
| 2026-04-08 | Raised Planyway/Trello Timeline integration problem | Proposed 3 directions + flagged capability gaps |
| 2026-04-08 | Log issue to gap-log | Appended entry to `activity/gap-log.md` ✅ |
| 2026-04-08 | Push gap-log to GitHub | Commit `7bbba62`, pushed to origin/main ✅ |
| 2026-04-08 | Push local `/home/node/activity/valkyri_k.md` | 發現有 2 份 file（local + repo），merged + pushed `d48160a`，flag 兩個 path 並存問題 |
| 2026-04-08 | Diagnose activity/ path 雙位置 root cause | Layer 1 missing symlink + Layer 2 bare relative path in CLAUDE.md → logged kary-dev-log |
| 2026-04-08 | Fix A (symlink) + Fix B (CLAUDE.md absolute-path rule) | Backup → rm raw folder → ln -s; CLAUDE.md edit; commit `2872b2a` ✅ |
| 2026-04-08 | Discuss long-term memory + cost optimization (Max plan quota concern) | Decided 3-section hybrid schema (Open Threads / Session Summaries / Request Log) |
| 2026-04-08 | Implement schema in CLAUDE.md + reference impl in valkyri_k.md | First commit blocked by root-owned git objects (chown bug surfaced) |
| 2026-04-08 | Surface root-owned `.git/objects` permission bug | Kary fixed via `sudo chown -R node:node /home/node/kb/.git` |
| 2026-04-08 | Retry schema rework commit | `1a9b3d5` pushed ✅ (CLAUDE.md + valkyri_k.md + kary-dev-log.md, +197/-10) |
| 2026-04-08 | Add Pre-Clear Sequence instruction | Commit `ce00194` — 6-step auto-housekeeping on `clear` keyword ✅ |
| 2026-04-08 | First Pre-Clear Sequence dogfood run | This entry — Mugi auto-ran the sequence after Kary said "clear" |
| 2026-04-08 | Trello: 加 Style Frame card 入 J26016 HSUHK，assign Kay Chan，due today | Created `ojly9L7l` ✅ (first Trello write op via trello-agent skill) |
| 2026-04-08 | Trello: 加 Revise name tag card 入 J26039 British Council，assign Max，due today | Created `FFOaz2OU` ✅ |
| 2026-04-08 | Trello: Kary manual delete `FFOaz2OU` 後 request recreate | Recreated as `eJRu5PSD` ✅ (in project channel) |
| 2026-04-08 | Trello: Kary 提示要 assign label，re-fetched labels list (10 labels), applied `mograph` to BC card; HSUHK card 404 (Kary deleted) | Learned label IDs, BC card label set ✅ |
| 2026-04-08 | Trello: delete BC card `eJRu5PSD` for fresh test | Deleted ✅ |
| 2026-04-08 | Trello: copy all 10 cards from `[Pre-Pro] Template` → J26053 BOC Trendy Too IG Reels, assign Kary | All 10 copied via idCardSource + post-add member ✅ |
| 2026-04-08 | Trello: 加 checklist 落 Storyboard card，Video 1 assign Max / Video 2 assign Keith | Checklist created; member assignment silent-ignored (board 冇 Advanced Checklists power-up) → fallback 用 @mention in item name; logged gap-log |
| 2026-04-08 | Trello: archive 4 完成 project lists (J26035 / J26036 / J26027 / J26034) | All closed ✅ |
| 2026-04-08 | Drive: cleanup root, keep Archive/Templates/OLD Drive Files + DOF Current Job List, move 其他舊 files 入 OLD Drive Files | Listed 54 candidates (incl. flagged 2 recent timeline test docs) → Kary confirm → moved 54/54 ✅ |
| 2026-04-08 | Calendar: confirm BOC Trendy Too shoot Apr-15 | Found `[TBC] (1 day) BOC Trendy Too IG Reel` already on 4/15 → renamed to `Shoot - BOC Trendy Too`, colorId 11, J26053 desc ✅ |
| 2026-04-08 | Verify OAuth refresh token spreadsheets scope (post re-consent) | Tested live — 3 scopes confirmed: drive + documents + spreadsheets ✅ |
| 2026-04-08 | Log J26041 sheets-scope workaround → gap-log (status done) | Appended entry; commit `a7d2996` (later rebased to `3fe752c`) |
| 2026-04-08 | Push gap-log → GitHub | Failed initially — diagnosed 3 stacked bugs (embedded empty pwd in remote URL, helper auto-erase, divergent main); fixed all + pushed `3fe752c` ✅ |
| 2026-04-08 | Walk Kary through Option A (deploy key) vs Option B (PAT) for git auth | Kary chose Option B; provided fine-grained PAT setup steps |
| 2026-04-08 | Set up PAT credential helper + fix remote URL | `git remote set-url` cleaned `valkyri-k:@`, re-stored `~/.git-credentials`, validated push ✅ |
| 2026-04-08 | Log GitHub push setup bugs → kary-dev-log | Commit `bf80ca6` pushed (validates new git setup end-to-end) ✅ |
| 2026-04-08 | J26016 HSUHK Student Excellence Batch 2 shoot update | Deleted `(TBC) 2 Days` event; created 3 TBC shoots Apr 21/24/27 with `- Batch 2` suffix + `Cam: Jer` desc; Batch 1 post-pro untouched ✅ |
