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
| `YOUTUBE_REFRESH_TOKEN` | `youtube.readonly` scope，consent 為 **dofofapple@gmail.com**（owner 先 list 到 unlisted 片） |

> ⚠️ **Account 分別：** unlisted 片喺 `dofofapple` account，唔係 `dof.internal`（Drive 嗰個）。所以 `YOUTUBE_*` 係獨立一套 env，唔好同 `GOOGLE_DRIVE_*` 撈亂。
>
> 🚫 **絕對禁止用任何 cloud MCP 或 connected tool 去打 YouTube**，就算 `claude mcp list` 顯示 ✓ Connected 都唔好用。interactive「Connected」唔保證 Discord-triggered headless turn 都喺度，亦違反 env-credential 原則。所有 search 必須行 `scripts/youtube-search.js`（內部用三個 env + REST + pagination）。冇例外。

Refresh token 點 generate（一次性）：本機跑 `python3 scripts/get-youtube-token.py`，browser login dofofapple → token 寫落 `~/.credentials/youtube/mugi-readonly-token.txt`（唔 print）→ copy 上 Zeabur。

---

## No-Fallback Rule（hard）

呢個 skill 嘅 search **只可以**經 `scripts/youtube-search.js` 做。**唔可以**：

- 自己 call 任何 YouTube / cloud MCP / connected tool 去 fetch
- 自己手寫 `fetch()` / `curl` 去打 YouTube API（script 已經做晒 OAuth refresh + pagination + privacy resolve）
- 估片名／編個 youtu.be link 出嚟（亂噏 link 會俾錯客戶）

撞到 script 行唔到（env 缺、OAuth error、API error、parse fail）→ **STOP，照原文 report error 俾用戶，唔好 improvise 一個 workaround**。

---

## Ops Flow

### Step 1 — 行 search script

喺 KB repo root 行（query term 用用戶講嘅 client / project / event 名）：

```bash
node scripts/youtube-search.js EMSD Dems Briefing
```

Script 會：OAuth refresh 攞 access token → 攞 channel uploads playlist → paginate 列晒全部上傳片（owner 身份，含 unlisted）→ 本機按片名 filter（**每個 query 字都要喺片名出現**，case-insensitive）→ `videos.list` 補 privacy + duration → 喺 stdout print `{ query, count, results[] }`，每個 result 有 `id` / `name` / `link`（`youtu.be/<id>`）/ `privacy` / `published` / `duration`。

如果 stdout 係 `YOUTUBE SEARCH FAILED: ...` 或 exit code 非 0 → 照 error report，停喺度（見 No-Fallback Rule）。

### Step 2 — 篩 + 整理結果

Filter 係「全部 query 字命中」，已經幾窄；但仲要睇 JSON 自己判斷：

- 有 `(Copy)` / `_Trailer` / 版本後綴嘅，照列但標清楚係邊條，唔好擅自當重複剔走。
- 字命中但明顯唔啱 context 嘅，提返用戶但唔好獨斷剔走。
- `privacy` 值要連埋講（見下面對照），因為影響條 link 俾出去啱唔啱。

如果 query 字太多／太死 filter 到冇 match，但你估片真係喺度 → 用少啲 keyword 重行，唔好亂估 link。

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
