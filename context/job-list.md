# DOF Job List

> Source of truth: Airtable Master Job Log (base `appld5YU1iZm3Hx5F`, table `Projects`)
> Scope: `status = Current` only（active production jobs）
> Last synced: 2026-06-04（auto-sync via `scripts/sync-job-list.js`）
> Sync mechanism: Stage 1 (n8n auto-sync) 待實作。期間如有新 Current job，手動 trigger re-sync 或 patch 此 file。

---

## Active Jobs

| Job No | Client | Project Name | Aliases | Status | Director | Discord Channel ID | Discord Channel Name |
|--------|--------|--------------|---------|--------|----------|---------------------|----------------------|
| J26007 | DFI | DFI Corporate video 2026 |  | Current | Benjy | 1501849664176132247 | j26007_dfi_corporate_video_2026 |
| J26010 | Cartier | Cartier Prince Building - the making of video |  | Current | Benjy | 1504037605006770176 | j26010-cartier-prince-building_the-making-of-videography-production |
| J26016 | HSUHK | HSUHK Student Excellence Video Production_Final |  | Current | Kary | 1489144435869483059 | j26016_hsuhk-student-excellence-video-series |
| J26020 | EMSD | EMSD Engineer & Technician Trainee Graduation Ceremony event with director blog video production |  | Current | — | 1509779734777696266 | j26020_emsd-engineer-technician-trainee-graduation-ceremony-event-with-director-blog-video-productio |
| J26024 | DFI_Mannings | DFI Own Brand H&B 2026 Strategy Video APAC |  | Current | Sohling | 1506247763975733298 | j26024-dfi-own-brand-apac |
| J26027 | EMSD | EMSD 15th National Games for CS Outstanding Awards video production | NG15;全運會 | Current | Benjy | 1501787539642650706 | j26027_emsd_15th_national_game_for_cs_award |
| J26050 | CUHK | CUHK Bid for IFOS 2030 Promotional video |  | Current | Kary | 1509800199588020284 | j26050_cuhk-bid-for-ifos-2030-promotional-video |
| J26053 | Buttons_BOC | button BOC Trendy Together 22 IG videos |  | Current | Kary | 1489112803397603348 | j26053_button-boc-trendytogether-ig-reels |
| J26056 | DFI | DFI Own Brand H & B KV production |  | Current | — | 1511303483716796557 | j26056_dfi-own-brand-h-and-b-kv-production |
| J26057 | HKTB | HKTB Incentive Playbook all-in-one Fam video update |  | Current | Sohling | 1493606268449984642 | j26057_hktb_incentive_playbook_all-in-one_fam_video_update |
| J26058 | Hong Kong Productivity Council | HKPC 60th anniversary staff photos for all employees |  | Current | Ki | 1509778703750533282 | j26058_hkpc-60th-anniversary-staff-photos-for-all-employees |
| J26062 | Orbis | Orbis Future Vision Leader and From Blur to Clear Campaign |  | Current | Kary | 1493117424201891952 | j26062_orbis-future-vision-leader-and-from-blur-to-clear-campaign |
| J26063 | EMSD | EMSD HKMA GWIN |  | Current | Benjy | 1493811545497538560 | j26063_emsd-hkma-gwin |
| J26064 | Megaworks | Megaworks Private Birthday Party event video and photo service |  | Current | Ki | — (no channel by design) | — (no channel by design) |
| J26069 | CLP | CLP MD aand COO speech event |  | Current | Benjy | 1501043831829954570 | j26069-clp-md-aand-coo-speech-event |
| J26070 | EMSD | EMSD CCSD2026-19 Farewell party on May | Farewell event highlight shooting | Current | Benjy | 1501043894433874120 | j26070-emsd-ccsd2026-19-farewell-party-on-may |
| J26071 | Buttons | Button InvestHK Motion graphic videos production |  | Current | Kary | 1502220628424396821 | j26071-button-investhk-motion-graphic-videos-production |
| J26075 | CLP | CLP Chat With Joe May episode external version | Joe Chat | Current | Benjy | 1502249491296817314 | j26075-clp-chat-with-joe-may-ep-external-ver |
| J26077 | CLP | CLP Chat with Joe June 2026 | Joe Chat | Current | Benjy | 1500803244144721970 | j26077_chat_with_joe_ep_june |
| J26081 | Department of Health | MDD 10K Listing video |  | Current | — | 1509079387339751464 | j26081_mdd_10k_listing_video_cant_vers |
| J26082 | EMSD | EMSD Corporate Video 2026 | EMSTF 30A | Current | — | 1503674382030209094 | j26082_emsd_corporate_video_2026 |
| J26084 | Department of Health | MDD 10K Listing video, English and Mandarin versions |  | Current | — | 1509079823383924747 | j26084_mdd_10k_listing_video_eng_mand_vers |
| J26085 | — | Minerals Hang Seng Facility Management Award | HS Facility Award | Current | — | 1509112179339694212 | j26085_minerals_hang_seng_facility_management_award |
| J26091 | DFI_711 | DFI 7 eleven Trade show 2026 |  | Current | — | 1509860999631470643 | j26091_dfi-711-trade-show-present-video |
| J26XXX | — | Test Project |  | Current | — | — | — |

---

## Field Reference

- **Job No** — DOF job number `J{YY}{NNN}`. Primary key.
- **Client** — Brand identifier from Airtable `brand` linked field. May contain underscores（e.g. `Buttons_BOC` = Button agency × BOC client）。
- **Project Name** — Formal project title from Airtable `project_title`.
- **Aliases** — `;`-separated alternative names（spoken shorthand、cross-vocabulary descriptors）。Default 空，reactive maintenance only — see Mugi Resolution Rules in `CLAUDE.md`.
- **Status** — Airtable `status` singleSelect。Cache 只入 `Current`。
- **Director** — Airtable `director` linked field（→ Team table）。一個 job 通常一個 director；多個用 `;` 分隔。`—` = Airtable 未填。
- **Discord Channel ID** — Snowflake ID（dispatch source of truth）。`— (no channel by design)` = 呢個 job 唔需要 Discord channel（見下面 Channel coverage）。
- **Discord Channel Name** — Human reference only，跟 Channel ID 同步。

---

## Channel coverage（DOF 規則）

DOF Discord channel **唔係每個 Current job 都有**。Channel 只 cover 需要 cross-team coordination（特別係後期 cycle）嘅 job。以下情況 by design 唔開 channel：

- **長拍 / 仲喺 shooting 階段、未入後期** — e.g. J26010 Cartier Prince Building（拍一年嘅 project，still shooting）
- **Shooting only，冇後期** — e.g. J26064 Megaworks Private Birthday Party（event video + photo service，no post involved）

Mugi 仍可用 J# / Client / Project Name / Alias 做 resolution（cache row 完整），但呢類 job **唔可以 dispatch**（physically 冇 channel）。如 user trigger dispatch 到呢類 J#，reply：「呢個 job 冇 Discord channel（[原因，e.g. 仲喺 shooting / 冇後期]），唔可以 dispatch。」
