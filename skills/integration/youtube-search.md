# YouTube Search (by title)

> **用途：** 由 DOF **dofofapple** YouTube channel 用**片名文字**搵片（**包括 unlisted**），返 `youtu.be` link + privacy。收到「俾我 X 嘅 YouTube link」/「搵 YouTube X」/「客睇嗰條 X 喺 YouTube 邊」類 request 用呢份。
> **Callers：**
> - 用戶話「give me the YouTube link of X」/「搵下 YouTube 有冇 X」/「X 條 client-share 片個 link」
> - 任何「用 client / project / event 名搵 YouTube 片」嘅 lookup
>
> **背景：** DOF share 片俾客睇有兩個 host — Vimeo + YouTube（dofofapple，unlisted）。搵 Vimeo 用 [[vimeo-search]]；呢份搵 YouTube。唔肯定喺邊個 → 兩個都行。
>
> **Scope（Layer 1 only）：** 淨係做 **title-text search**——client / project / event 名通常已經喺片名入面。**唔掂 Job Number**（YouTube 片名 by design 唔擺 Job#）。撞到 Job# request → 同用戶講要片名／client／project 名嚟搵。

---

## Credentials

YouTube Data API v3 冇 personal access token，行 **Google OAuth**（同 Google Drive 一樣 pattern）。三個 Zeabur env var：

| Env var | 內容 |
|---|---|
| `YOUTUBE_CLIENT_ID` | dofofapple OAuth client（GCP project `youtube-api-492515`） |
| `YOUTUBE_CLIENT_SECRET` | 同上 |
| `YOUTUBE_REFRESH_TOKEN` | `youtube`（manage）scope，consent 為 **dofofapple@gmail.com**（owner 先 list 到 unlisted 片）|

> ⚠️ **Account 分別：** unlisted 片喺 `dofofapple` account，唔係 `dof.internal`（Drive 嗰個）。所以 `YOUTUBE_*` 係獨立一套 env，唔好同 `GOOGLE_DRIVE_*` 撈亂。
>
> 🔑 **同一個 token 兩用：** scope 係 `youtube`（manage，readonly 嘅 superset），所以呢個 search skill 同 [[youtube-edit]]（改 privacy / description）**共用**同一套三個 env + 同一個 refresh token。search 唔需要 write 權，但 manage scope 一樣讀得到。
>
> 🚫 **絕對禁止用任何 cloud MCP 或 connected tool 去打 YouTube**，就算 `claude mcp list` 顯示 ✓ Connected 都唔好用。interactive「Connected」唔保證 Discord-triggered headless turn 都喺度，亦違反 env-credential 原則。所有 search 必須行 `/home/node/kb/scripts/youtube-search.js`（內部用三個 env + REST + pagination）。冇例外。**用絕對路徑** —— Mugi cwd 係 `/home/node`，relative `scripts/...` 會搵唔到。

Refresh token 點 generate（一次性）：本機跑 `python3 scripts/get-youtube-token.py`，browser login dofofapple → token 寫落 `~/.credentials/youtube/mugi-token.txt`（唔 print）→ copy 上 Zeabur。

---

## No-Fallback Rule（hard）

呢個 skill 嘅 search **只可以**經 `/home/node/kb/scripts/youtube-search.js` 做。**唔可以**：

- 自己 call 任何 YouTube / cloud MCP / connected tool 去 fetch
- 自己手寫 `fetch()` / `curl` 去打 YouTube API（script 已經做晒 OAuth refresh + pagination + privacy resolve）
- 估片名／編個 youtu.be link 出嚟（亂噏 link 會俾錯客戶）

撞到 script 行唔到（env 缺、OAuth error、API error、parse fail）→ **STOP，照原文 report error 俾用戶，唔好 improvise 一個 workaround**。

---

## Ops Flow

### Step 1 — 行 search script

行（絕對路徑，cwd 無關；query term 用用戶講嘅 client / project / event 名）：

```bash
node /home/node/kb/scripts/youtube-search.js EMSD Dems Briefing
```

Script 會：OAuth refresh 攞 access token → 攞 channel uploads playlist → **本機 title cache 取 / 增量補新**（見下）→ 本機按片名 filter（**每個 query 字都要喺片名出現**，case-insensitive substring）→ `videos.list` 補 privacy + duration（**每次即時，唔 cache**）→ 喺 stdout print `{ query, mode, scanned, count, results[] }`，每個 result 有 `id` / `name` / `link`（`youtu.be/<id>`）/ `privacy` / `published` / `duration`。

**Title cache（efficiency）：** channel 有成 ~15,500 條片，每次重新 paginate 全 channel 要 ~3.5 分鐘 = unusable。所以 id+title list cache 落 disk（`$YOUTUBE_CACHE_PATH`，預設 `~/.cache/dof-youtube-titles.json`）。uploads playlist 係 newest-first，每次 search 只 page 到撞到已 cache 嘅片就停（通常 1 page），新上傳即時補入 → **warm cache search ~7 秒**。`mode` 欄會講用咗邊條 path：

| `mode` | 意思 |
|---|---|
| `cache` | 用咗本機 cache + 增量補新（快，正常情況）|
| `full-build` | cache 唔存在（第一次行 / container 啱 deploy 完 / cache file 俾清咗）→ 全 channel scan 一次（~3.5 分鐘，慢，正常）|
| `rebuild` | 手動 `--rebuild` 強制全 scan |

> **Privacy 永遠係即時 fetch**，唔會 cache —— 所以就算用 cache，report 出嘅 `unlisted`/`private` 都係當下真實狀態（[[youtube-edit]] 啱啱改完都即刻反映到）。

**`--rebuild` flag：** 如果懷疑 cache 壞咗 / 片名對唔上 / 數量明顯唔啱，可加 `--rebuild`（或 `--full`）強制重 scan 全 channel：

```bash
node /home/node/kb/scripts/youtube-search.js --rebuild EMSD Dems Briefing
```

正常唔需要 —— cache 會自動 self-heal（file 缺 / corrupt → 自動 full-build）。Read-only fs 都 OK（淨係冇咗加速，search 照行）。

如果 stdout 係 `YOUTUBE SEARCH FAILED: ...` 或 exit code 非 0 → 照 error report，停喺度（見 No-Fallback Rule）。

### Step 2 — 篩 + 整理結果

Filter 係「全部 query 字命中」，已經幾窄；但仲要睇 JSON 自己判斷：

- **⭐ Latest-edit-first（預設，2026-09-02 Kary 定）：** DOF 交 edit 俾 client 會 upload **好多個 version** 上 YouTube（同一條片會有 V2 / Ver2 / 唔同 upload date 嘅重複 edit）。當 user 淨係話「俾我 X 個 link」→ **預設只揀嗰條片嘅最新 edit（by upload / published date，最新嗰條）俾佢，唔好一次過 dump 晒所有 version**。User 再問「有冇其他 version / 舊版」先至列其餘。目的：避免好似 [[gap-log]] 2026-09-02 咁 reply 一堆重複緊同一集嘅 link。
  - 點分「同一條片嘅 version」vs「唔同片」：片名 base 一樣、淨係後綴 / date / V2 唔同 = version（收埋淨俾最新）；base 名唔同（唔同 client / event / 集數）= 唔同片（各自俾最新 edit 一條）。
- 字命中但明顯唔啱 context 嘅，提返用戶但唔好獨斷剔走。
- `privacy` 值要連埋講（見下面對照），因為影響條 link 俾出去啱唔啱。

如果 query 字太多／太死 filter 到冇 match，但你估片真係喺度 → 用少啲 keyword 重行，唔好亂估 link。

#### CWJ（Chat with Joe）片名命名（2026-09-02 Kary）

CWJ 片名格式 = **`CLP ChatwithJoe [Ep月份] [upload YYYYMMDD]`**，e.g.「CLP ChatwithJoe Sept 20260827」= **9 月嗰集**、upload date 係 **2026-08-27**（後面串 YYYYMMDD 係 upload date，唔係集數月份）。

- **每月一集**（有啲月份會 skip 或 rename，唔齊唔緊要，唔使當漏）。
- 所以**同一個「Ep月份」token 出現多條 = 嗰集嘅唔同 edit version** → 按 Latest-edit-first 只俾最新 upload date 嗰條。
- ⚠️ 片名**淨係用月份 + upload date，唔擺 topic**（e.g.「大亞灣」呢類內容主題唔會喺片名）。所以 user 用 topic 搵某集 → title-search 對唔到，要問返 user 邊個**月份**（= 邊集），再俾嗰集最新 edit。

### Step 3 — Report

逐條列 **片名 → link（→ privacy）**。範例：

> 搵到 N 條同「EMSD Dems Briefing」相關（YouTube / dofofapple）：
> - EMSD_DEMS_Briefing Event 2024 → https://youtu.be/xxxxxxxxxxx （unlisted）
> - EMSD_DEMS_Briefing_Trailer → https://youtu.be/yyyyyyyyyyy （unlisted）

冇 match → 直接講「YouTube search `<query>` 冇 match」，唔好亂估／唔好 fallback 去第二個 source（除非用戶另外叫你搵 Vimeo / Drive / Doji）。

**Privacy 值對照**（YouTube `status.privacyStatus`，影響 link 可分享性，report 時要 flag）：

| `privacy` | 意思 |
|---|---|
| `public` | 公開，任何人搜尋／開到 |
| `unlisted` | 唔公開搜尋／淨係持 link 嘅人開到——可以俾 link 但提返「呢條唔好公開散」（DOF client-share 片預設呢個） |
| `private` | 淨係 account owner 開到——條 link 俾出去客戶開唔到，report 出嚟但提返呢條 access 唔到 |
