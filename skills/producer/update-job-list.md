# Update Job List

> **用途：** 由 Airtable Master Job Log 刷新本地 `context/job-list.md` 嘅 active job cache（`status = Current` rows）。收到「update / sync / refresh job list」類 request 用呢份。
> **Callers：**
> - 用戶直接話「update current job list」/「sync job list」/「refresh 下個 job list」
> - 新 job 開咗、status 轉咗、Discord channel link 咗之後想對返 cache
>
> 純 lookup（「J26XXX 係邊個 client」/「呢個 channel 對應邊個 job」）唔屬呢度——直接 read `context/job-list.md` 答即可，唔使 sync。

---

## Credentials

Airtable 操作用 **read-only PAT**（Zeabur env var `AIRTABLE_PAT`）+ 直接 REST。Base `appld5YU1iZm3Hx5F`、table `Projects`。

> 🚫 **絕對禁止用任何 Airtable MCP tool**（`mcp__*airtable*`、claude.ai 嘅 "Airtable" connected tool 全部唔得，就算 `claude mcp list` 顯示 ✓ Connected 都唔好用）。
> 原因同 Calendar 一樣：Mugi 嘅 Claude Code 以 `karyto.dof@gmail.com` 登入 claude.ai，會 silently 繼承 cloud MCP，但 interactive「Connected」唔保證 Discord-triggered headless turn 都喺度，而且唔好做第一個違反 env-credential 原則嘅 case。
> 所有 fetch 必須行 `/home/node/kb/scripts/sync-job-list.js`（內部用 PAT + REST + pagination）。冇例外。**用絕對路徑** —— Mugi cwd 係 `/home/node`，relative `scripts/...` 會搵唔到。

---

## No-Fallback Rule（hard）

呢個 skill 嘅 fetch + merge + write **只可以**經 `/home/node/kb/scripts/sync-job-list.js` 做。**唔可以**：

- 自己 call Airtable MCP / connected tool 去 fetch records
- 自己手寫 `fetch()` / `curl` 去打 Airtable API（script 已經做晒 pagination + field resolve + merge）
- 自己直接改 `context/job-list.md` 個 table（會破壞 merge logic，wipe 走 manual aliases 同「— (no channel by design)」annotation）

撞到 script 行唔到（env 缺、API error、parse fail）→ **STOP，照原文 report error 俾用戶，唔好 improvise 一個 workaround**。

---

## Ops Flow

### Step 1 — 行 sync script

行（絕對路徑，cwd 無關）：

```bash
node /home/node/kb/scripts/sync-job-list.js
```

Script 會：fetch 所有 `status = Current` rows → merge 入現有 `context/job-list.md`（保留 manual aliases + no-channel annotation）→ rewrite Active Jobs table + 更新 `Last synced` line → 喺 stdout print 一個 JSON diff summary。

如果 stdout 係 `SYNC FAILED: ...` 或 exit code 非 0 → 照 error report，停喺度（見 No-Fallback Rule）。

### Step 2 — 讀 diff summary，做判斷

Script 只做 deterministic file op。**所有 judgment 喺呢度由你（Mugi）做**，逐個 field 睇 JSON diff：

| diff field | 意思 | 你要做咩 |
|---|---|---|
| `addedWithChannel` | 新 Current job，Airtable 已有 Discord channel | **Flag 做 `/discord:access` allowlist candidate**（見 Step 3）。呢啲 channel 未加入 allowlist 之前，outbound dispatch 會 silent fail。 |
| `addedNoChannel` | 新 Current job，冇 channel | **Channel coverage 判斷**：呢個 job 需唔需要 post-pro 協調 channel？需要 → 提 Kary／Benjy 開 channel。pre-pro / shoot-only job 本身就唔需要 channel（by design，唔係「漏咗」）——係嘅話喺 cache 手動標 `— (no channel by design)`。 |
| `removed` | Cache 有但 Airtable 已唔係 Current（completed / closed / on hold） | 正常 churn，已經自動由 table 移除。一句 report 即可，唔使 action。 |
| `channelDrift` | Airtable channel 變空但 cache 有 real channel | **唔好當垃圾**：可能係 Airtable 嗰邊手誤清咗。Flag 出嚟叫 Kary check Airtable，cache 暫時保留咗舊 channel。 |
| `aliasMerged` | Cache-local manual alias 被保留入 union | 正常，report 一句即可（確認 manual alias 冇被 wipe）。 |

### Step 3 — 新 channel job 嘅 3-step allowlist flow

`addedWithChannel` 入面每個 job，要完整行呢三步先收得工（單做 cache update 唔夠，outbound dispatch 仲係會 silent fail）：

1. **Airtable row** — 已經有 channel（係呢個 case 嘅前提），冇嘢要做。
2. **Cache update + push + container pull** — `sync-job-list.js` 已寫入 cache；本地 commit + push KB repo → container `git pull` → 叫 Mugi re-read。**（push 係 shared state，要 Kary confirm 先 push。）**
3. **`/discord:access` allowlist add** — 喺 Web Terminal Claude Code session 加返個新 channel 入 allowlist：
   ```
   /discord:access channel add <discord_channel_id>
   ```
   冇呢步，Mugi 派唔到嘢落個新 channel。

> 詳見 memory `feedback_new_current_job_dispatch_allowlist`：加 job 入 cache **唔等於**完成，`/discord:access` allowlist 唔加，outbound dispatch silently fail。

### Step 4 — Report

一段精簡 report 俾用戶。範例：

> ✅ Job list synced（N 個 Current job）。
> - 新增有 channel（要加 allowlist）：J26082 Buttons_BOC、J26085 ...
> - 新增冇 channel（要決定 coverage）：J26024 ...
> - 移除（唔再 Current）：J26002、J26047 ...
> - ⚠️ Channel drift（Airtable 清空咗，cache 暫保留）：J26XXX — 麻煩 check 返 Airtable

所有 list 都係空就講「冇變動」。
