# YouTube Edit (privacy / description / title)

> **用途：** 改 DOF **dofofapple** YouTube channel 一條片嘅 **privacy**（public / unlisted / private）、**description** 或 **title**。最常見：客睇完想我哋**收返條片做 `private`**；其次修 description / title。收到「幫我收返條 X 做 private」/「set X to private」/「改 X 個 description」類 request 用呢份。
> **Callers：**
> - 用戶話「收返條 X 做 private」/「set X back to private」/「unpublish X」
> - 「改 X 個 YouTube description / title」
>
> **背景：** 同 [[youtube-search]] **共用**同一套 credentials（同一個 refresh token，`youtube` manage scope）。Edit 要先有 video id —— 通常先用 [[youtube-search]] 搵到條片攞 id，再用呢份改。
>
> **Scope：** 淨係改**單一片**嘅 metadata（privacy / description / title）。**唔做**批量、唔 delete 片、唔改 channel 設定。

---

## Credentials

同 [[youtube-search]] 完全一樣 —— 三個 Zeabur env var（`YOUTUBE_CLIENT_ID` / `YOUTUBE_CLIENT_SECRET` / `YOUTUBE_REFRESH_TOKEN`），refresh token consent 為 **dofofapple@gmail.com**，scope `youtube`（manage，已 cover read + write）。

> 🚫 **絕對禁止用任何 cloud MCP 或 connected tool 去改 YouTube**，就算 `claude mcp list` 顯示 ✓ Connected 都唔好用。所有 edit 必須行 `scripts/youtube-edit.js`（內部用三個 env + OAuth refresh + `videos.update`）。冇例外。

---

## ⚠️ Confirm-before-write（hard rule）

呢個係**寫操作，改緊 client-facing 嘅片**。改錯 = 客即刻開唔到條 link，或者唔小心將 private 片放出去。所以**每一次寫之前必須**：

1. **確認係邊條片** —— 先唔帶任何 flag 行一次 `scripts/youtube-edit.js <id>`（read-only），攞返**片名 + 當前 privacy + link**，畀用戶睇實係咪嗰條。
2. **覆述改乜** —— 同用戶講清楚「`<片名>`：privacy `unlisted` → `private`」（或 description / title 改成點），等佢**明確 confirm** 先行寫。
3. **一次一條** —— 唔可以一個 request 自動 loop 改多條。每條都要行 step 1–2。
4. **改完 report before→after** —— 將 script 出嘅 `changes` 原原本本講返。

唔肯定 id 邊條 / 用戶得個片名 → 先去 [[youtube-search]] 搵，**唔好估 id**。

---

## No-Fallback Rule（hard）

呢個 skill 嘅 edit **只可以**經 `scripts/youtube-edit.js` 做。**唔可以**：

- 自己 call 任何 YouTube / cloud MCP / connected tool 去改
- 自己手寫 `fetch()` / `curl` 打 `videos.update`（script 已做晒 OAuth refresh + GET-merge-PUT，避免 reset 其他 field）
- 估片 id

撞到 script 行唔到（env 缺、OAuth error、API error、`No video found`）→ **STOP，照原文 report error，唔好 improvise**。

---

## Ops Flow

### Step 1 — 讀當前狀態（confirm 用，唔寫）

```bash
node scripts/youtube-edit.js dQw4w9WgXcQ
```

出 `{ id, mode: "read", current: { name, privacy, description, link } }`。攞嚟同用戶 confirm。

### Step 2 — 改（用戶 confirm 後先行）

```bash
# 收返做 private
node scripts/youtube-edit.js dQw4w9WgXcQ --privacy private

# 改 description（記得用引號包住成段）
node scripts/youtube-edit.js dQw4w9WgXcQ --description "Final delivery cut — 2026 campaign"

# 一次過改埋 title + privacy
node scripts/youtube-edit.js dQw4w9WgXcQ --title "ClientX Brand Film (Final)" --privacy unlisted
```

`--privacy` 只接受 `public` / `unlisted` / `private`。Script 會 GET 當前 snippet+status → 只覆寫你指定嗰幾項（其餘 writable field 照搬，唔會 reset）→ PUT `videos.update`。

出 `{ id, mode: "write", changes: { privacy?: {from,to}, description?: {...}, title?: {...} }, before, after }`。

如果 stdout 係 `YOUTUBE EDIT FAILED: ...` 或 exit code 非 0 → 照 error report，停喺度（見 No-Fallback Rule）。

### Step 3 — Report

逐項講返改咗乜，例如：

> 改好喇 —— `ClientX Brand Film`（https://youtu.be/dQw4w9WgXcQ）：privacy `unlisted` → **`private`**。客而家用條 link 開唔到喇。

**Privacy 值對照**（YouTube `status.privacyStatus`）：

| `privacy` | 意思 |
|---|---|
| `public` | 公開，任何人搜尋／開到 |
| `unlisted` | 唔公開搜尋／淨係持 link 嘅人開到（DOF client-share 片預設）|
| `private` | 淨係 account owner 開到 —— 客就算有 link 都開唔到（「收返做 private」即係呢個）|
