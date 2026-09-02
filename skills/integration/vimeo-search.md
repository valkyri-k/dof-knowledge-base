# Vimeo Search (by title)

> **用途：** 由 DOF Vimeo account 用**片名文字**搵片，返 share link + privacy。收到「俾我 X 嘅 Vimeo link」/「搵 Vimeo X」類 request 用呢份。
> **Callers：**
> - 用戶話「give me Vimeo links of X」/「搵下 Vimeo 有冇 X」/「X 條片個 link」
> - 任何「用 client / project / event 名搵 Vimeo 片」嘅 lookup
>
> **Scope（Layer 1 only）：** 呢個 skill 淨係做 **title-text search**——client / project / event 名通常已經喺片名入面。**唔掂 Job Number**：Vimeo 片名 by design 唔擺 Job#（client-facing portfolio constraint），所以「J26XXX 條片個 link」呢類 Job# → video 嘅 lookup 做唔到，要等 Layer 2（Airtable linked sub-table，未起）。撞到 Job# request → 同用戶講要片名／client／project 名嚟搵，或者話 Job# join 仲未 build。

---

## Credentials

Vimeo 操作用 **personal access token**（Zeabur env var `VIMEO_TOKEN`，`private` scope 先 list 到 unlisted / password 片）+ 直接 REST（API v3.4）。

> 🚫 **絕對禁止用任何 cloud MCP 或 connected tool 去打 Vimeo**，就算 `claude mcp list` 顯示 ✓ Connected 都唔好用。
> 原因同 Calendar / Airtable 一樣：Mugi 嘅 Claude Code 以 `karyto.dof@gmail.com` 登入 claude.ai 會 silently 繼承 cloud MCP，但 interactive「Connected」唔保證 Discord-triggered headless turn 都喺度，亦唔好違反 env-credential 原則。
> 所有 search 必須行 `/home/node/kb/scripts/vimeo-search.js`（內部用 `VIMEO_TOKEN` + REST + pagination）。冇例外。**用絕對路徑** —— Mugi cwd 係 `/home/node`，relative `scripts/...` 會搵唔到。

---

## No-Fallback Rule（hard）

呢個 skill 嘅 search **只可以**經 `/home/node/kb/scripts/vimeo-search.js` 做。**唔可以**：

- 自己 call 任何 Vimeo / cloud MCP / connected tool 去 fetch
- 自己手寫 `fetch()` / `curl` 去打 Vimeo API（script 已經做晒 pagination + field resolve）
- 估片名／編個 vimeo.com link 出嚟（private 片條 link 有 privacy hash，估唔到；亂噏 link 會俾錯客戶）

撞到 script 行唔到（env 缺、API error、parse fail）→ **STOP，照原文 report error 俾用戶，唔好 improvise 一個 workaround**。

---

## Ops Flow

### Step 1 — 行 search script

行（絕對路徑，cwd 無關；query term 用用戶講嘅 client / project / event 名）：

```bash
node /home/node/kb/scripts/vimeo-search.js EMSD Dems Briefing
```

Script 會：用 Vimeo 原生 `query` title search → paginate 攞晒 match → 喺 stdout print 一個 JSON `{ query, count, results[] }`，每個 result 有 `id` / `name` / `link` / `privacy` / `created` / `duration`。

如果 stdout 係 `VIMEO SEARCH FAILED: ...` 或 exit code 非 0 → 照 error report，停喺度（見 No-Fallback Rule）。

### Step 2 — 篩 + 整理結果

Vimeo `query` 係 broad title match，會帶埋鬆散嘅 hit。睇 JSON 自己收窄：

- **⭐ Latest-edit-first（預設，2026-09-02 Kary 定）：** DOF 交 edit 俾 client 會 upload 多個 version（同一條片有 V2 / date / 版本後綴嘅重複 edit）。User 淨係話「俾我 X 個 link」→ **預設只揀嗰條片最新 edit（by `created` date，最新嗰條）俾佢，唔好一次過 dump 晒所有 version**。User 再問先列其餘 version。
  - 同一條片嘅 version（base 名一樣、淨後綴/date/V2 唔同）= 收埋淨俾最新；base 名唔同（唔同 client / event / 集數）= 唔同片，各自俾最新一條。
- 用戶講嘅 keyword 全部命中嘅排先（e.g.「EMSD Dems Briefing」→ 片名同時有 EMSD + Dems + Briefing）。
- `privacy` 值要連埋講（見下面 privacy 對照），因為影響條 link 俾出去啱唔啱。

### Step 3 — Report

逐條列 **片名 → link（→ privacy）**。範例：

> 搵到 N 條同「EMSD Dems Briefing」相關：
> - EMSD_DEMS_Briefing Event 2024 → https://vimeo.com/1103377505 （anybody）
> - EMSD_DEMS_Briefing Event 2023 → https://vimeo.com/1035078315 （password）
> - EMSD_DemsBriefing2024_Trailer → https://vimeo.com/1043102897 （disable）

冇 match → 直接講「Vimeo search `<query>` 冇 match」，唔好亂估／唔好 fallback 去第二個 source（除非用戶另外叫你搵 Drive / Doji）。

**Privacy 值對照**（影響 link 可分享性，report 時要 flag）：

| `privacy.view` | 意思 |
|---|---|
| `anybody` | 公開，任何人開到 |
| `password` | 要密碼先入到——俾 link 之餘要提返密碼喺邊 |
| `unlisted` / `nobody` | 唔公開搜尋／淨係持 link 嘅人——可以俾 link 但提返「呢條唔好公開散」 |
| `disable` | 已停用，條 link 開唔到——report 出嚟但提返呢條 access 唔到 |
