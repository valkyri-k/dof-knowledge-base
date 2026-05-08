# DOF Job List

> Source of truth: Airtable Master Job Log (base `appld5YU1iZm3Hx5F`, table `Projects`)
> Scope: `status = Current` only（active production jobs）
> Last synced: 2026-05-08（manual patch — J26071 added）
> Sync mechanism: Stage 1 (n8n auto-sync) 待實作。期間如有新 Current job，手動 trigger re-sync 或 patch 此 file。

---

## Active Jobs

| Job No | Client | Project Name | Aliases | Status | Discord Channel ID | Discord Channel Name |
|--------|--------|--------------|---------|--------|---------------------|----------------------|
| J26002 | CLP | CLP CLPP Hall of Fame Award Sharing video production |  | Current | 1492110996653740083 | #j26002-clpp-hall-of-fame-award-sharing-video |
| J26007 | DFI | DFI Corporate video 2026 |  | Current | 1500690941638479893 | #j26007-dfi-corporate-video-2026 |
| J26010 | Cartier | Cartier Prince Building - the making of video |  | Current | — (no channel by design) | — (no channel by design) |
| J26016 | HSUHK | HSUHK Student Excellence Video Production_Final |  | Current | 1489144435869483059 | #j26016_hsuhk-student-excellence-video-series |
| J26027 | EMSD | EMSD 15th National Games for CS Outstanding Awards video production | NG15;全運會 | Current | 1501787539642650706 | #j26027_emsd_15th_national_game_for_cs_award |
| J26047 | CLP | CLP Chat with Joe April 2026 |  | Current | 1491279980447928380 | #j26047-clp-chat-with-joe-apr |
| J26053 | Buttons_BOC | button BOC Trendy Together 22 IG videos |  | Current | 1489112803397603348 | #j26053_button-boc-trendytogether-ig-reels |
| J26057 | HKTB | HKTB Incentive Playbook all-in-one Fam video update |  | Current | 1494549516337283154 | #j26057-hktb-incentive-playbook-all-in-one-fam-video-update |
| J26060 | CLP | CLP Smart E animation |  | Current | 1493155958162198658 | #j26060-clp-smarte_animation |
| J26062 | Orbis | Orbis Future Vision Leader and From Blur to Clear Campaign |  | Current | 1493117424201891952 | #j26062_orbis-future-vision-leader-and-from-blur-to-clear-campaign |
| J26063 | EMSD | EMSD HKMA GWIN |  | Current | 1493811545497538560 | #j26063_emsd-hkma-gwin |
| J26064 | Megaworks | Megaworks Private Birthday Party event video and photo service |  | Current | — (no channel by design) | — (no channel by design) |
| J26065 | CLP | CLP HKMA Smart E Living |  | Current | 1497160276196327424 | #j26065-clp-hkma-smart-e-living |
| J26066 | EMSD | EMSD Quiz challenge video for Farewell event | 快問快答 | Current | 1496037652825112657 | #j26066_emsd_quiz_of_farewell_party |
| J26067 | EMSD | EMSD QUOHSD1KC20060046 好醫工大賽 | Best CE Award;好E工 | Current | 1500764253181972480 | #j26067_emsd_best_ce_award_competition_video |
| J26069 | CLP | CLP MD aand COO speech event |  | Current | 1501043831829954570 | #j26069-clp-md-aand-coo-speech-event |
| J26070 | EMSD | EMSD CCSD2026-19 Farewell party on May | Farewell event highlight shooting | Current | 1501043894433874120 | #j26070-emsd-ccsd2026-19-farewell-party-on-may |
| J26071 | Buttons_InvestHK | Button InvestHK Motion graphic videos production |  | Current | 1502220628424396821 | #j26071-button-investhk-motion-graphic-videos |
| J26077 | CLP | CLP Chat with Joe June 2026 | Joe Chat | Current | 1500803244144721970 | #j26077_chat_with_joe_ep_june |

---

## Field Reference

- **Job No** — DOF job number `J{YY}{NNN}`. Primary key.
- **Client** — Brand identifier from Airtable `brand` linked field. May contain underscores（e.g. `Buttons_BOC` = Button agency × BOC client）。
- **Project Name** — Formal project title from Airtable `project_title`.
- **Aliases** — `;`-separated alternative names（spoken shorthand、cross-vocabulary descriptors）。Default 空，reactive maintenance only — see Mugi Resolution Rules in `CLAUDE.md`.
- **Status** — Airtable `status` singleSelect。Cache 只入 `Current`。
- **Discord Channel ID** — Snowflake ID（dispatch source of truth）。`— (no channel by design)` = 呢個 job 唔需要 Discord channel（見下面 Channel coverage）。
- **Discord Channel Name** — Human reference only，跟 Channel ID 同步。

---

## Channel coverage（DOF 規則）

DOF Discord channel **唔係每個 Current job 都有**。Channel 只 cover 需要 cross-team coordination（特別係後期 cycle）嘅 job。以下情況 by design 唔開 channel：

- **長拍 / 仲喺 shooting 階段、未入後期** — e.g. J26010 Cartier Prince Building（拍一年嘅 project，still shooting）
- **Shooting only，冇後期** — e.g. J26064 Megaworks Private Birthday Party（event video + photo service，no post involved）

Mugi 仍可用 J# / Client / Project Name / Alias 做 resolution（cache row 完整），但呢類 job **唔可以 dispatch**（physically 冇 channel）。如 user trigger dispatch 到呢類 J#，reply：「呢個 job 冇 Discord channel（[原因，e.g. 仲喺 shooting / 冇後期]），唔可以 dispatch。」
