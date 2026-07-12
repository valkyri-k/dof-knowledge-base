# Mugi — Architecture & Restart Checklist

> **Canonical copy**（[[2026-07-08]] 由 DOF_Build vault `projects/007-agent-mugi/architecture.md` 遷入；vault 嗰邊留 pointer）。
> Technical reference。唔係日常工作 context。最新項目狀態 → vault `projects/007-agent-mugi/status.md`

---

## Architecture Notes

- **Container 架構**：Zeabur Terminal 係直接連入 container（唔係 host），唔需要 `crictl`。[[2026-04-24]] 確認：`crictl` not found 係正常，直接喺 Zeabur Terminal 操作即可
- **System prompt 機制**：Mugi runtime 以 `cwd = /home/node/kb` 開 session —— **repo root `CLAUDE.md` 由 harness 直接 auto-load 做 system prompt**（symlink `/home/node/CLAUDE.md` 係 2026-07-06 cwd 改動前嘅機制，而家係 rebuild checklist 嘅 belt-and-braces）。Skill files 按 request type lazy-load（skills dispatch table）
- **CLAUDE.md split（[[2026-04-08]]）**：原 74.5KB → 3 files：`CLAUDE.md`（lean，hard rules + dispatch）、`skills/producer/producer-playbook.md`（timeline generation + calendar rules + document generation）、`technical/google-apis.md`（Calendar SA + Drive OAuth2 boilerplate）
- **Knowledge base**：GitHub repo `valkyri-k/dof-knowledge-base`，clone 到 `/home/node/kb/`，CLAUDE.md + context/ 用 symlink
- **Knowledge base 本地路徑**：`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/DOF-knowledge-base`（iCloud sync 兩部機；user 名唔同，用 `~` 相對）
- **Knowledge base 更新 workflow**：本地 edit → git push → `scripts/kb-pull.sh`（commit-before-pull）→ Discord message Mugi「請 re-read 最新 CLAUDE.md」→ done（唔需要 restart）
- **Dev workflow**：branch rule、plans、dev session 入口 → [dev-guide.md](dev-guide.md)。**Repo root 唔准擺 dev CLAUDE.md / `.claude/` / `AGENTS.md`**（Mugi cwd = repo root 會食咗佢哋）
- **Container symlinks**：需要 4 個：`CLAUDE.md`、`context/`、`skills/`、`technical/`（[[2026-04-08]] 新加後兩個）
- **Calendar API**：SA 已 migrate 到新 GCP project `agent-mugi`（`agent-mugi@agent-mugi.iam.gserviceaccount.com`），`GOOGLE_CALENDAR_CREDENTIALS` updated in Zeabur
- **Drive / Docs / Sheets API**：OAuth2 as `dof.internal@gmail.com`——`GOOGLE_DRIVE_CLIENT_ID` / `_SECRET` / `_REFRESH_TOKEN` 全部 set in Zeabur。Calendar SA 同 Drive OAuth2 並存，互唔干擾。Scopes：`drive` + `documents` + `spreadsheets`（[[2026-04-08]] re-consented）
- **Drive Folder Convention**：dof.internal Drive root 入面有兩個 reserved folders——`Templates/`（by-name template lookup，命名 `[DocType]_Template`）、`Archive/`（唔 delete，move 過嚟）
- **Document Generation naming rule**：`[DocType]_[Job Number]_[Project Title]_[YYYY-MM-DD]_[version]`（e.g. `Timeline_J26015_HSUHK Student_2026-04-07_r2`）
- **Secrets 管理**：全部走 Zeabur Variables（env vars），唔落 disk，container restart 後自動注入
- **Calendar API 呼叫方式**：Mugi 用 Python code execution（`google-api-python-client`）呼叫，唔需要獨立 MCP server
- **⚠️ gcal MCP 禁用原因（[[2026-04-07]] 發現）**：Mugi 嘅 Claude Code instance 係以 `karyto.dof@gmail.com` 登入，`gcal_*` tools → event 顯示「Created by Kary」而唔係 Service Account。CLAUDE.md 已加入明確禁令。
- **Channel access 管理**：喺 Web Terminal（Claude Code session）用 `/discord:access` commands 管理
- **Filesystem persistence（[[2026-04-07]] 確認）**：Server "reset" 係 **process restart**，唔係 full container rebuild——`/home/node/kb/` 同 memory folder **兩者都唔受影響**。只有 full container rebuild 先會清空。

---

## External-Service Access Pattern（durable principle）

**Mugi 一律唔用 cloud MCP 接外部 service —— 一致行 env-credential + 直接 API / script。** 呢個唔限於 Google，係跨所有 service 嘅 architecture 原則。

- **點解**：Mugi 嘅 Claude Code instance 以 `karyto.dof@gmail.com` 登入 claude.ai，會 **silently 繼承 claude.ai 嗰邊 connected 嘅 cloud MCP**（gcal、Gmail、Airtable 等），即使 local `mcpServers` 空。`claude mcp list` 喺 interactive session 會見到佢哋「✓ Connected」。咬過兩次（[[2026-05-09]] gcal write 入 Kary personal account）。詳見 Claude memory `reference_cloud_mcp_invisibility`。
- **規則來源**：CLAUDE.md root-level（~line 90–107）有 hard rule——撞到自己想 call `mcp__*` / `gcal_*` prefix tool → **STOP**，切返 Python / API boilerplate。放 root level（唔靠 skill file），因為冇 visible code anchor 嘅 prose 禁令 agent 易 fall back 去 cloud MCP default。
- **硬封鎖（[[2026-07-06]] P0-1 deployed）**：`/home/node/.claude/settings.json` 加咗 `"permissions": { "deny": ["mcp__claude_ai_*"] }` —— wildcard 封晒所有 claude.ai cloud connector tools（實測：deny 咗嘅 server 啲 tools 連 ToolSearch 都搵唔到，`--dangerously-skip-permissions` 下照生效；discord plugin tools 唔受影響）。將來新 connector 自動封。之前試過 `--strict-mcp-config` —— **唔用得**，會連 plugin MCP tools（discord reply 等 5 個）一齊殺。上面嘅 prose 禁令仍然保留做第二層。
- **Airtable（[[2026-05-29]] 確認）**：container `claude mcp list` 顯示 `claude.ai Airtable: ✓ Connected`，但**一致地唔用佢**。任何要 read/write Master Job Log（base `appld5YU1iZm3Hx5F`）嘅 skill，行 read-only PAT（Zeabur env var）+ `scripts/` REST fetch，mirror Google pattern。原因同上：interactive「Connected」唔保證 Discord-triggered turn 都喺度，且唔好做第一個違反原則嘅 case。

## Skill 機制（how Mugi skills work）

- **Skill file 格式**：每個 skill 係一個 markdown file 喺 `skills/<category>/<name>.md`（現有 category：`producer/`、`trello/`）。File 內容係俾 Mugi 讀嘅 op-level instruction + boilerplate，唔係 code module。
- **Dispatch table**（CLAUDE.md §385「Skills Dispatch」）：一張 table，每行 = `收到呢類 request | MUST read 邊個 skill file | 觸發 keywords`。Mugi 收到 match 嘅 keyword → **唔可以靠記憶答，必須先 read 對應 skill file** 先做嘢。
- **Loading order**（CLAUDE.md §402）：Quick Reference 有答案就直接答 → 冇就 read context files → 再冇就 read skill files。Skill files lazy-load，唔係 startup 全載，慳 context。
- **加新 skill = 兩步**：(1) 寫 `skills/<category>/<name>.md`；(2) 喺 CLAUDE.md §385 dispatch table 加一行 trigger keyword → 指去個 file。冇加 dispatch row，Mugi 唔會知幾時 read 個 skill。
- **No-fallback rule**（Claude memory `feedback_skill_no_fallback_rule`）：SKILL.md 要明文禁止 agent 自己 construct workflow / bypass deployed script，否則 orchestrator 會 self-improvise。

---

## Observability — Mac-side session-transcript 觀察法（[[2026-07-07]] 建立）

Discord interface 睇唔到 Mugi 內部 process（thinking / loading / 有冇 call reply tool）。Mac-side 可以直接讀 Mugi 嘅 Claude Code session transcript，睇到每一個 tool call + text output + timestamp + token usage。**golden regression run 就係靠呢個 score**（Kary Discord 發 prompt → Mac-side parse transcript 逐條驗行為）。

- **Transcript 位置**：container `/home/node/.claude/projects/-home-node-kb/*.jsonl`，一個 session 一個 file，**latest 由 mtime 揀**（`sorted(glob, key=os.path.getmtime)[-1]`）。每行一個 JSON event：`type` = `user`（含 `tool_result` blocks）/ `assistant`（含 `tool_use` + `text` blocks + `usage`）。
- **讀法**：`npx -y zeabur@latest service exec --id 69d3781093577fe0061de8d5 -i=false -- sh -c '<python>'`（service id `…d5` = container exec endpoint；project dof-agent = `…d4`）。Parse 出 `ts | tag | text` timeline：`TOOL:<name>` / `SAY`（text output）/ `RESULT-ERR` / `usage`（`cache_read` + `output_tokens`）。
- **base64-shipping**（避免 nested-shell quote mangling）：本機寫好 python script → `B64=$(base64 < f.py | tr -d '\n')` → `sh -c "echo $B64 | base64 -d | python3"`。
- **實錘用途**：(1) P0-1 verify — 見到 SA calendar Python boilerplate + discord reply tool、**冇** `claude_ai` calendar tool = cloud MCP 真封；(2) **silent-reply failure 診斷** — 見到 `SAY`（答案出咗 text）但同一 turn **冇** discord reply `TOOL` call = Discord 收唔到（[[2026-07-07]] baseline run ×4 復現，non-deterministic）；(3) 量度 pre-clear 需時（首末 timestamp）+ 首 turn context（`cache_read` + `cache_creation`）。
- **⚠️ 長任務 EOF**：`zeabur service exec` 直行耗時 command 會斷線 —— 讀 transcript 係快 op 冇事，但如果 exec 入面觸發 headless claude 之類就要 nohup detach + poll（見 Restart Checklist）。

---

## Silent-Reply Guard — Stop hook（[[2026-07-07]] P1 deployed）

**問題**：Mugi 有時答案出咗 text 但**冇** call discord `reply` tool → sender Discord 收唔到（transcript text 永遠唔會自動送去 Discord，`server.ts:453`）。KB-layer prose 提醒實測無效（baseline run ×4 silent-reply）。

**解法**：第二個 Stop hook `reply_guard.py` —— turn 完結時檢查「最後一個 Discord inbound 之後有冇任何 outbound tool（`reply` / `edit_message` / `react`）」，冇就 emit `{"decision":"block","reason":...}` 迫 model 補送。

- **判斷邏輯（三個條件齊先 BLOCK）**：(1) transcript 有 `<channel source="plugin:discord:discord">` inbound（呢個 turn 預期要回覆）；(2) 最後 inbound 之後冇 outbound tool；(3) `stop_hook_active` 唔係 true（loop guard，最多迫一次 retry）。非 Discord-triggered turn（冇 inbound）→ 永不 block。
- **點解冇 false-positive**：全 36 條 channel 都 `requireMention:true`，每個 delivered message 都係 directed at Mugi、合理預期回覆 → 冇 ambient log-only turn 會誤中。Offline validation（baseline transcript 91cdafb8）：flag 中 5/28 = 全部 4 個已知 silent-reply incident + 1 個真實連環漏答，23 個正常回覆 turn **零** false-positive。Live smoke test（[[2026-07-07]] restart 後）：正常 Q → Mugi call `reply` → guard log `pass`，無誤 block。
- **檔案位置**：live = `/home/node/.claude/hooks/reply_guard.py`（`node:node` +x）；canonical = KB repo `infra/hooks/reply_guard.py`（commit `1d363de`，rebuild 靠 git pull 恢復）。
- **Wiring**：`/home/node/.claude/settings.json` `hooks.Stop` **第二個 block**（第一個 = kb-chown）：`{ "matcher": "", "hooks": [{ "type": "command", "command": "python3 /home/node/.claude/hooks/reply_guard.py" }] }`。分開兩個 block（唔同 kb-chown 合併）→ block-decision stdout 唔會同 chown log 撈埋。
- **Log**：`/tmp/reply-guard-$(id -u).log`，每 turn 一行 `pass` / `BLOCK` / `skip`（loop guard）。
- **殘留 edge（低風險）**：hook 用 stdin `transcript_path`（Claude Code 永遠提供）為準；glob fallback 只喺 transcript_path 缺失時觸發，理論上可讀到舊 checkpoint transcript 而誤 block —— 實際上 Claude Code 唔會漏傳 transcript_path，故未 harden。將來若見到無故 block，先查係咪 fallback。

---

## Restart Checklist

### 甚麼情況下要跑？

| 情況 | kb repo | memory folder | 需要跑 Checklist？ |
|------|---------|---------------|-------------------|
| Restart service（Zeabur dashboard）| ✅ 保留 | ✅ 保留 | **唔需要** |
| Full container rebuild（image rebuild）| ❌ 清空 | ❌ 清空 | **需要** |
| 唔確定 | — | — | 跑 step 1 先 check |

**日常 CLAUDE.md 更新流程（最常用）：** `git pull`（喺 container 入面）→ Discord message Mugi 叫佢 re-read CLAUDE.md → done。唔需要 restart service。

> ⚠️ **第三種情況：platform 靜靜 recreate（上表冇覆蓋）** — 平台自動 re-pull `latest` image（image update / host 遷移）唔係 user 按 dashboard「Restart service」嗰種 process-restart，而係 **RECREATE** container（writable layer reset）。真 entrypoint `/opt/startup.sh` 唯讀、**唔 auto-start Mugi agent** → Kary 見到嘅只係「Mugi 突然冇反應」，唔知發生咗 restart。Volume-mounted path（kb / memory）survive，但行緊嘅 agent process + writable-layer 改動（`.profile`、pip 裝嘅 dep）冇咗。下面 auto-recover + watcher 兩件套 close 呢個 loop。

### Silent restart — auto-recover + 外部 watcher（[[2026-07-12]]）

**Part 1 — login-gated auto-recover（container 側，`/home/node/.profile`）**
Web terminal 一 login（non-TMUX shell）就檢查有冇 agent 行緊，冇就喺 tmux `main` session 重啟。實際 block（加喺 `.profile` 尾）：

```sh
# mugi agent autostart — auto-recover Claude Code agent on web-terminal login.
if [ -z "$TMUX" ]; then
  if ! pgrep -f "claude --dangerously-skip-permissions" >/dev/null 2>&1; then
    tmux kill-session -t main 2>/dev/null
    tmux new-session -d -s main "exec env DISCORD_BOT_TOKEN='$DISCORD_BOT_TOKEN' claude --dangerously-skip-permissions --channels plugin:discord@claude-plugins-official"
    echo "  [mugi] Claude Code agent auto-started in tmux session 'main'"
  fi
fi
```
- `pgrep` guard：agent 已行就唔重啟（避免 double-launch）。用 `kill-session` + `new-session` 而唔用 `tmux new -As main -- claude`，因為後者遇到已存在嘅空 `main` session 會 no-op（净係 attach，唔 launch）。
- ⚠️ `.profile` 喺 **writable layer** → full rebuild / recreate 會清走，要重加（見 Full Rebuild Checklist step 8.5）。同場 `kb/mugi-status/launch.sh` monitor autostart（2026-06-09 加）一樣 login-gated。

**Part 2 — 外部 restart watcher（home Mac mini 側）**
Login-gated 有 gap：Kary 要**知道**發生咗 restart 先會去開 terminal。Watcher 補呢個 signal：home Mac mini launchd（`com.kary.mugi-restart-watch`，每 5 分鐘）`zeabur service exec` poll container **PID 1 start time**（`stat -c %Y /proc/1`）→ 一變 = container recreate → POST Discord webhook（#mugi-status）叫 Kary 去開 web terminal 觸發 Part 1。連續 3 次探唔到（~15min）另發 warning。
- **Signal 揀 PID 1 唔用 `/proc/uptime`**：`/proc/uptime` = **host kernel** uptime（container 共享 host kernel，顯示成日，冇用）；PID 1 start epoch 先反映 container recreate。
- **點解 host 揀 home mini 唔用 n8n**：Discord 冇 REST presence API（online/offline 净係 Gateway WebSocket，n8n 維持唔到）；`zeabur service exec` 又要 zeabur CLI + auth（n8n on Railway 冇）→ 得 home mini（always-on + CLI + auth）做到。
- **Caveats**：home mini 要長開；zeabur CLI auth 過期會出 false「探唔到」alert（`zeabur profile info` check）。
- Machine-scoped detail（script path / launchd plist / webhook secret）留喺 Mac 側，唔入 KB repo。

**真 durable fix（未做）**：bake deps + agent auto-start 入 image / startup hook，令 login-gated recover + 外部 watcher 兩者都唔再需要 → vault Project 007 Open Question「Container Python deps provisioning gap」。

### In-place 重啟 Mugi（改咗 settings.json / launch flags 先需要）

Settings（`/home/node/.claude/settings.json`）改動要 claude process 重啟先食到。唔使 restart Zeabur service —— 喺 container 入面（以 node user）重啟 tmux session 就得：

```bash
# 全部以 node user 行（root 行 claude 會整污糟 credentials，見下面 ⚠️）
su node -s /bin/sh -c '
tmux kill-session -t main
cd /home/node/kb && tmux new -d -s main -- /home/node/.local/bin/claude --dangerously-skip-permissions --channels plugin:discord@claude-plugins-official
'
```

- **cwd 必須係 `/home/node/kb`**（[[2026-07-06]] 實測：由 `/home/node` 起會 hit 未 trust 嘅 folder-trust prompt，Mugi 會 hang 喺 dialog 度唔 connect Discord；而且 project-level MCP config 係掛喺 `/home/node/kb`）
- tmux server 由 `mugi-status` session 頂住，kill `main` 唔會冧成個 server
- 重啟後 verify：`ps aux | grep "discord/0.0"` 見到 bun plugin child process = Discord channel 接返；再 `tmux capture-pane -t main -p` 睇 pane 有冇 dialog 卡住（feature promo / trust prompt），有就 send-keys Escape 或處理
- Trust flags 已寫入 `/home/node/.claude.json`（`projects./home/node` 同 `.../kb` 嘅 `hasTrustDialogAccepted: true`，[[2026-07-06]]）——正常唔會再彈 trust prompt
- **`zeabur service exec` 長任務會 EOF**：直行（`-i=false -- sh -c '...'`）跑耗時 command（例如 headless claude verify task）會喺完成前斷線。改用 nohup detach + poll：command 尾加 `nohup ... > /tmp/out.log 2>&1 &`，之後另開 exec `cat /tmp/out.log` poll 結果

> ⚠️ **唔准以 root 行任何 `claude` command**（包括 `claude mcp list` / `claude --help`）。Container `HOME=/home/node` hardcoded，root 行 claude 觸發 OAuth token refresh 會將 `/home/node/.claude/.credentials.json` 重寫成 root:root 600，搞死 node user（即 Mugi）下次 token refresh（[[2026-07-06]] 中過一次）。一律 `su node -s /bin/sh -c "claude ..."`；萬一中咗：`chown node:node /home/node/.claude/.credentials.json` + `find /home/node -user root -exec chown -h node:node {} +` sweep。

### Full Rebuild Checklist（真係清空先用）

前置條件：Zeabur Variables 已設定 `GITHUB_PAT`（scope: `repo`）。

```bash
# 1. 開 Zeabur Terminal（直接入 container，唔需要 crictl）
# Zeabur dashboard → Service → Terminal tab

# 2. Clone knowledge base
cd /home/node
git clone https://valkyri-k:$GITHUB_PAT@github.com/valkyri-k/dof-knowledge-base.git kb
git config --global --add safe.directory /home/node/kb

# 3. Symlinks
ln -s /home/node/kb/CLAUDE.md /home/node/CLAUDE.md
ln -s /home/node/kb/context /home/node/context
ln -s /home/node/kb/skills /home/node/skills
ln -s /home/node/kb/technical /home/node/technical

# 4. Git config（令 Mugi 可以 commit + push activity files）
cd /home/node/kb
git config user.name "valkyri-k"
git config user.email "karyto.dof@gmail.com"
git remote set-url origin https://valkyri-k:$GITHUB_PAT@github.com/valkyri-k/dof-knowledge-base.git

# 5. 喺 Web Terminal 嘅 Claude Code session：
/discord:access group add 1490653458280353922

# 6. KB root-owned files auto-chown Stop hook（[[2026-05-10]] deployed）
# 確保 root user (Zeabur web terminal / Mac-side `zeabur service exec`) Claude Code session 完結時
# 自動 chown KB folder 返 node:node，避免 Mugi git ops 撞 root-owned file。
# Merge 落 /home/node/.claude/settings.json 嘅 hooks.Stop schema：
#   command: { date -Iseconds; if [ "$(id -u)" = "0" ]; then chown -R node:node /home/node/kb/ 2>&1; echo "chown exit=$?"; else echo "skipped (uid=$(id -u))"; fi; } >> /tmp/kb-chown-hook-$(id -u).log 2>&1
# 寫完要 chown node:node + chmod 644 settings.json。詳見 vault `projects/007-agent-mugi/archive/done/kb-repo-root-owned-files-recurring.md`

# 7. Silent-reply guard Stop hook（[[2026-07-07]] P1 deployed）——hook 檔喺 KB repo，settings.json 唔喺
mkdir -p /home/node/.claude/hooks
cp /home/node/kb/infra/hooks/reply_guard.py /home/node/.claude/hooks/reply_guard.py
chmod +x /home/node/.claude/hooks/reply_guard.py
chown -R node:node /home/node/.claude/hooks

# 8. Cloud MCP 硬封鎖（[[2026-07-06]] P0-1）+ 上面 step 6 chown hook + step 7 reply_guard——settings.json 唔喺 KB repo，rebuild 後必須重建
# /home/node/.claude/settings.json 完整內容（Stop 兩個 block：kb-chown + reply_guard）：
#   {
#     "model": "sonnet",
#     "hooks": { "Stop": [
#       { "matcher": "", "hooks": [ ...step 6 kb-chown hook... ] },
#       { "matcher": "", "hooks": [ { "type": "command", "command": "python3 /home/node/.claude/hooks/reply_guard.py" } ] }
#     ] },
#     "enabledPlugins": { "telegram@claude-plugins-official": true, "discord@claude-plugins-official": true, "fakechat@claude-plugins-official": true },
#     "effortLevel": "low",
#     "skipDangerousModePermissionPrompt": true,
#     "permissions": { "deny": [ "mcp__claude_ai_*" ] }
#   }
# wildcard 封晒 claude.ai cloud connectors（Gmail/gcal/Airtable/...），新 connector 自動封；
# 唔可以改用 --strict-mcp-config（會殺埋 discord plugin tools）。
# 兩個 Stop block 分開（唔合併）→ reply_guard 嘅 block-decision stdout 唔會同 chown log 撈埋。
# 寫完 chown node:node + chmod 644 settings.json。當前 container backup：/home/node/.claude/settings.json.bak-2026-07-07

# 8.5 Login auto-recover — 重加 /home/node/.profile 尾嘅 mugi agent autostart block（writable layer，rebuild 清走）。
# 完整 block 見上面 Restart Checklist「Silent restart」section。冇呢個 block，之後 platform 靜靜 recreate container，
# login 唔會自動重啟 agent，Kary 只會見到 Mugi 靜靜死。

# 9. 啟動 Mugi（tmux，cwd 必須 /home/node/kb —— 見上面 In-place 重啟 section）
su node -s /bin/sh -c 'cd /home/node/kb && tmux new -d -s main -- /home/node/.local/bin/claude --dangerously-skip-permissions --channels plugin:discord@claude-plugins-official'
```

> ⚠️ Full rebuild 唯一無法自動恢復嘅係 **memory folder**。kb 靠 git pull 恢復，memory 就真係冇——但 CLAUDE.md 入面嘅 rules 會 cover 大部分行為。

> **Container quirk**：`HOME=/home/node` hardcoded 即使 `whoami=root`。Claude Code 永遠 read `/home/node/.claude/settings.json`，唔會睇 `/root/.claude/`。Mac-side 經 `zeabur service exec --id 69d3781093577fe0061de8d5` 入 container 都係呢個 user model。
