# sohling_69845 (Sohling)

- **Discord ID:** 1489108444475686943
- **Role:** Post-Pro Supervisor (統籌後期、QC)
- **Common requests:** Trello list / card setup for new post-pro projects, cross-referencing Calendar with Trello
- **Notes:** First interaction 2026-04-08. 用廣東話。Quick / on-the-go style instructions.

---

## User Practice Profile

### Responsibilities
- Post-Pro Supervisor：統籌後期、QC、Calendar ↔ Trello post-pro coordination。
- 常見 request 係將 project timeline / Calendar events 轉成 Trello lists/cards，並 assign post-pro teammates。

### Working Style
- 用廣東話，instruction 通常 quick / on-the-go。
- 會直接講 job / client / project shorthand；Mugi 應先用 `job-list.md` / Calendar / Trello context resolve，ambiguous 就問清楚。
- 會補充或修正 job number / assignee / card logic；Mugi 應將 correction 當成 current truth，但唔好自動 apply 到其他 job。

### Response Guidance
- 回覆保持短而清楚：做咗乜、改咗邊個 list/card/event、仲有咩等佢決定。
- 如果 assignee 未講明，唔好估；先 create neutral item，然後 surface「未 assign」俾 Sohling 決定。
- 如果 Calendar / Trello naming mismatch（例如 display name vs DOF nickname），要直接 surface，方便 Sohling 即時修正。

### Do Not Assume
- 唔可以因為 Sohling 過往多次處理 post-pro，就 assume 今次 target job / target channel。
- 唔可以 assume assignee；即使常見係 Yik / Keith / Katy，都要按今次 instruction 或 project context確認。
- 唔可以 skip job ambiguity check；job reference 必須 current-turn resolve。

### Evidence
- [[2026-04-08]] First interaction：Calendar EMSD QA events → Trello list/cards；冇 assign member時主動 surface。
- [[2026-04-08]] 多次 follow-up correction：J26054 / J26048 job number correction、assignee changes、naming mismatch surfaced。
- [[2026-05-03]] 多個 Calendar → Trello sync request：J26069、J26065、J26066。

---

## Pending Profile Review
（Mugi Pre-Clear Sequence draft，等 Claude Code review approve / reject。冇 candidate 留空。）

---

## Open Threads
（pending items，resolved 即時刪）

（closed 2026-06-05 by Kary: J26062/J26070/J26071 Trello member assign — ignore；J26050 saturation — ignore，如有問題再 flag）
- [2026-08-20] 「恆生嘅片」— resolve 到 J26085 Minerals Hang Seng Facility Award，但 Sohling 未答要邊種（Vimeo / YouTube / server 片檔）+ 邊個 cut。等佢回覆（低優先，可能已無需要）
- [2026-09-02] 「Joe Chat 大亞灣 YouTube link」— CWJ 片名淨用日期冇 topic（e.g.「CLP ChatwithJoe Sept 20260827」），title-search 對唔到「大亞灣」。已列最近 CWJ 集 + 問 Sohling 大亞灣嗰集大約邊個月/日期。等佢俾返日期先鎖定 link

---

## Recent Session Summaries
（每次 clear 前寫一段 narrative，新嘅放底）

### 2026-06-05 afternoon session
J26050 CUHK IFOS 2030 post-pro setup。Sohling 喺 J26050 channel 要求加 Calendar + sync Trello，Katy 同 Keith 負責。8 milestones：1st Cut Jun 11 / Client FB Jun 16 / 2nd Cut Jun 19 / Client FB 2 Jun 24 / Picture Lock Jun 26 / VO Jun 30–Jul 1 / Final Output Jul 7。Calendar push 7/8 events——Jun 11 1st Cut 暫扣因為 cut saturation（當日已有 4 個 cut events，加埋係第 5 個），Trello card 已建。8 Trello cards 全 created（Katy + Keith）。Jun 11 issue 已 surface，等 Sohling 決定。

### 2026-04-08 afternoon session
First-ever Sohling interaction. Request: 喺 Calendar 4月內 search EMSD QA events，create Trello list `J26054 EMSD QA` + cards mirror events. Mugi 搵到 4 條 events（Shooting 4/8 / 1st Cut 4/16 / 2nd Cut 4/23 / Final 4/29），create 咗新 list + 4 cards 連 due dates + labels（Shooting / cut / cut / final）。冇 assign member（Sohling 冇講），喺 reply 主動 surface 等佢決定。Trello list create 第一次 fail——`idBoard` 用咗 short ID `gThmFbyu`，要用 full board ID `682c30d662d5a52cc721cb04`，retry OK。Learned: Trello create-list endpoint 唔接受 short ID。

### 2026-05-15 afternoon session
（2026-06-05 由 valkyri_k.md migrate — 原本誤記入 Kary file，按 §Sender routing 修正。Sohling 喺 channel 做嘅，唔係 Kary。）批量 Calendar→Trello sync 3 個 request：(1) HSUHK Batch 2 Calendar→Trello sync（J26016，assign Yik + Max）——scan Calendar events，compare existing Trello list，補 missing cards；(2) EMSD GWIN Long version Calendar→Trello sync（J26063，assign Keith + Katy）——events → cards；(3) full job list Calendar→Trello comparison——掃 ALL current jobs，identify 冇 Trello list / missing cards 嘅 job，batch create。J26062 / J26070 / J26071 有 cards created 但無 member，因 Sohling 未 specify 負責人（留 open thread 等佢決定）。

### 2026-08-20 to 09-02 session (2 asset lookups, both unresolved)
Sohling 呢個 session 兩個 asset lookup（都喺 home base，非 Trello ops）。(1) **8/20「我想要恆生嘅片」**——resolve 到 J26085 Minerals Hang Seng Facility Award，但問返要邊種（Vimeo / YouTube / server 片檔）+ 邊個 cut，Sohling 未答（open thread）。(2) **9/2「joe chat 大亞灣 youtube link」**——⚠️ 呢條 04:09 send 但 Mugi 冇即時收到（inbound trigger gap，agent up；Kary 04:12 chase 先觸發），gap-log B 類。youtube-search 發現 **CWJ 片名淨用日期冇 topic**（「CLP ChatwithJoe Sept 20260827」= 9月集 upload 8/27），對唔到「大亞灣」→ 列咗最近 CWJ 集 + 問 Sohling 大亞灣係邊個月（等佢答，open thread）。同日 Kary 定咗 **latest-edit-first** rule（搵 link 只俾最新 edit，唔 dump 晒 version）+ CWJ 命名入咗 youtube-search.md。

---

## Request Log
| Date | Request | Outcome |
|------|---------|---------|
| 2026-04-08 | Search Calendar 4月 EMSD QA events + create Trello J26054 EMSD QA list/cards | Found 4 events, created list `69d616c67c8f22a1d9f96062` + 4 cards (Shooting/1st Cut/2nd Cut/Final) ✅ |
| 2026-04-08 | Assign Katy + Keith to all 4 J26054 cards | Done ✅ |
| 2026-04-08 | Unassign Katy + assign Yik to all 4 J26054 cards | Done ✅; surfaced naming mismatch (Trello display 'YL' vs CLAUDE.md 'Yik') |
| 2026-04-08 | Job number correction: J26054 是 EMSD CSC, EMSD QA 應該係 J26048 | Renamed existing QA list `J26054 → J26048`; created new `J26054 EMSD CSC` + 7 cards (Yik+Keith) ✅ |
| 2026-04-08 | J26054 CSC: Comment cards unassign Yik+Keith, assign Benjy | Done on Client Feedback 1 + 2 ✅ |
| 2026-04-08 | Calendar 4月 HKTB HKCA → add to existing J26041 list, comment→Kary, others→Yik+Keith | Added 6 cards; flagged judgment call on 4/9 "Confirmed by Client" (treated as Kary) ✅ |
| 2026-04-14 | Add Calendar + Trello for CLP SmartE animation: 1st cut today, final cut Fri, director Sohling | Calendar created (1st Cut 4/14, Final Output 4/18) ✅; Trello pending job number |
| 2026-04-28 | J26057 HKTB Playbook: add Calendar + Trello (5 events, 1st Cut→Final May 13) | Done ✅; Katy→cut cards, Keith→final assigned on May 3 follow-up |
| 2026-05-03 | J26069 CLP Speech: 8 events Calendar + Trello (Shoot May 5 → Final Output Short May 28) | Done ✅; Hall of Fame card created then archived per Sohling request |
| 2026-05-03 | J26065 CLP HKMA: 6 events Calendar + Trello (Tentative, Apr 29–May 8, May 2 Sat kept per Sohling) | Done ✅; all cards assigned to Sohling |
| 2026-05-03 | J26066 EMSD Farewell Party: sync Calendar → Trello, assign Keith + Katy | Found 3 Calendar events; created list + 3 cards ✅ |
| 2026-05-15 | HSUHK Batch 2 Calendar→Trello sync (J26016, Yik + Max) | Scanned Calendar, compared existing Trello list, created missing cards ✅ (migrated from valkyri_k.md 2026-06-05) |
| 2026-05-15 | EMSD GWIN Long version Calendar→Trello sync (J26063, Keith + Katy) | Events → Trello cards ✅ (migrated from valkyri_k.md 2026-06-05) |
| 2026-05-15 | Full job list Calendar→Trello comparison — batch create missing cards across all current jobs | Done ✅; J26062/J26070/J26071 cards created without member (Sohling 未 specify) → open thread (migrated from valkyri_k.md 2026-06-05) |
| 2026-06-05 | J26050 CUHK IFOS 2030: Calendar + Trello (Katy + Keith), 8 milestones | 7/8 Calendar events pushed (1st Cut Jun 11 held — saturation, 5th cut that day); 8 Trello cards created ✅; Jun 11 pending Sohling confirm |
| 2026-08-20 | 恆生嘅片 (home base) | Resolved 恆生 → J26085 Minerals Hang Seng Facility Award; asked which format (Vimeo/YT/server) + which cut. Sohling never replied → open thread |
| 2026-09-02 | Joe Chat 大亞灣 YouTube link (home base) | ⚠️ Msg sent 04:09 but Mugi didn't receive until Kary DM'd at 04:12 (trigger gap, agent up). youtube-search: CWJ titles date-based only, 大亞灣 not in any title → can't isolate. Listed recent CWJ episodes + asked Sohling for the date. Open thread |
