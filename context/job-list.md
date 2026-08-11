# DOF Job List

> Source of truth: Airtable Master Job Log (base `appld5YU1iZm3Hx5F`, table `Projects`)
> Scope: `status = Current` only（active production jobs）
> Last synced: 2026-08-11（auto-sync via `scripts/sync-job-list.js`）
> Sync mechanism: Stage 1 (n8n auto-sync) 待實作。期間如有新 Current job，手動 trigger re-sync 或 patch 此 file。

---

## Active Jobs

| Job No | Client | Project Name | Aliases | Status | Director | Discord Channel ID | Discord Channel Name |
|--------|--------|--------------|---------|--------|----------|---------------------|----------------------|
| J26007 | DFI | DFI Corporate video 2026 |  | Current | Benjy | 1501849664176132247 | j26007_dfi_corporate_video_2026 |
| J26010 | Cartier | Cartier Prince Building - the making of video |  | Current | Benjy;Atlas | 1504037605006770176 | j26010-cartier-prince-building_the-making-of-videography-production |
| J26050 | CUHK | CUHK Bid for IFOS 2030 Promotional video |  | Current | Kyle | 1509800199588020284 | j26050_cuhk-bid-for-ifos-2030-promotional-video |
| J26056 | DFI | DFI Own Brand H & B KV production |  | Current | Sohling | 1511303483716796557 | j26056_dfi-own-brand-h-and-b-kv-production |
| J26062 | Orbis | Orbis Future Vision Leader and From Blur to Clear Campaign |  | Current | Kary | 1493117424201891952 | j26062_orbis-future-vision-leader-and-from-blur-to-clear-campaign |
| J26076 | DFI | DFI DFIQ corporate video |  | Current | Benjy;Kyle;Kary | 1512390997894496367 | j26076-dfi-dfiq-corporate-video |
| J26079 | CLP | CLP Smart E Living revising QR code |  | Current | — | 1536289130273570836 | j26079_clp-smart-e-living-revising-qr-code |
| J26081 | Department of Health | MDD 10K Listing video |  | Current | Benjy;Atlas | 1509079387339751464 | j26081_mdd_10k_listing_video_cant_vers |
| J26084 | Department of Health | MDD 10K Listing video, English and Mandarin versions |  | Current | Benjy;Atlas | 1509079823383924747 | j26084_mdd_10k_listing_video_eng_mand_vers |
| J26085 | Minerals_Hang Seng | Minerals Hang Seng Facility Management Award | HS Facility Award | Current | Benjy | 1509112179339694212 | j26085_minerals_hang_seng_facility_management_award |
| J26091 | DFI_711 | DFI 7 eleven Trade show 2026 |  | Current | Kyle | 1509860999631470643 | j26091_dfi-711-trade-show-present-video |
| J26092 | Minerals_HSBC | Minerals HSBC new branch video |  | Current | Benjy | 1529001481729085511 | j26092_minerals-hsbc-new-branch-video |
| J26094 | DFI | DFI Own Brand KV adult diapers |  | Current | Sohling | — | — |
| J26099 | EMSD | EMSD Event production on 3 August 2026 |  | Current | Benjy | 1526064153696141372 | j26099_emsd-event-production-on-3-august-2026 |
| J26103 | Tsz Shan Monastery | Tsz Shan Monastery Councelling service video production |  | Current | Ki | 1526064232863498332 | j26103_tsz-shan-monastery-councelling-service-video-production |
| J26104 | CLP | CLP Chat with Joe Sept episode | CWJ | Current | Benjy;Atlas;Kary | 1525060802749399173 | j26104_chat_with_joe_sep |
| J26109 | John Swire & Sons (H.K.) | SD Forum opening video |  | Current | Benjy | 1536565494411296908 | j26109-sd-forum-opening-video |
| J26112 | John Swire & Sons (H.K.) | Swire Summer intern |  | Current | Kary | 1533995870914088990 | j26112_swire-summer-intern-social-video |

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
