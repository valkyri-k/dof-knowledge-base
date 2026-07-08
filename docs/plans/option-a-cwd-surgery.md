# Option A — Container cwd Surgery — Implementation Plan

> Branch: claude/mugi-option-a-lean-plan-48da11 · Written: 2026-07-08 · Against commit: 267977d
> Vault item: 冇獨立 backlog item —— WHAT/WHY = `projects/007-agent-mugi/status.md`「Mugi dev workflow SHIPPED」In Progress entry（Option A deferred 記錄）+ `docs/architecture.md`「Architecture Notes」system-prompt 機制
> Context recovery: 讀呢個 file + `docs/dev-guide.md` + `docs/architecture.md`「Restart Checklist」就夠開工。Trust ticked boxes — 唔好 re-verify。
> ⚠️ Approach 已 Kary confirm（2026-07-08）：**investigate-first**。Phase 0 read-only ground-truth 係硬 gate；prompt 位置（relocate vs symlink）+ wrapper 去留兩個 design decision **park 到 Phase 0 出數之後**先傾，唔喺呢份 plan 預設。

## Goal（WHAT/WHY）

改 Mugi container 嘅 working directory，令 KB repo root `CLAUDE.md` 唔再單純因為「喺 cwd」而被 harness auto-load 做 live system prompt。斬斷「repo root = system prompt」呢個 coupling 之後，repo root 先有得放 dev `.claude/` / `AGENTS.md`（潛在 payoff = retire dev wrapper），system-prompt surface 亦可控。**Deferred 原因**：Option B（wrapper）已 ship 解咗 dev isolation，Option A 屬 container 手術有 runtime 風險，Kary 決定同 lean-claude-md 一批做。

**四條要答清嘅 sub-question（Phase 1 交付）**：cwd 而家喺邊 → 改去邊 → 邊個 file 先係 Mugi 真正應該讀嘅 prompt → rebuild/deploy 點 propagate。

## 關鍵 grounding（落筆前已知，唔使重查）

- **harness 機制**：Mugi runtime 以 `cwd = /home/node/kb` 開 session，harness **auto-load `<cwd>/CLAUDE.md` 做 system prompt** → 而家即 repo root `CLAUDE.md`。（`docs/architecture.md` Architecture Notes）
- **已做過一次 cwd 手術**：2026-07-06 由 `/home/node` → `/home/node/kb`。原因（`docs/architecture.md` Restart Checklist line ~100）：`/home/node` 起 session hit **未 trust 嘅 folder-trust prompt → Mugi hang 喺 dialog 唔 connect Discord**；且 **project-level MCP config 掛喺 `/home/node/kb`**。⇒ 任何再搬 cwd 走嘅方案**必須同時重解 trust flags + project MCP config**，否則翻炒 hang。
- **`/home/node/CLAUDE.md` symlink** = 2026-07-06 cwd 改動前嘅舊機制，而家淨係 rebuild checklist 嘅 belt-and-braces。
- **settings.json / symlink / trust flags 唔喺 KB repo** → kb-pull 帶唔到。Option A 落地一定要改 **rebuild checklist**（`docs/architecture.md`）先 propagate，merge main ≠ deploy。
- **三條鐵律嘅命運**：「唔准改名/取代 repo root CLAUDE.md、唔准加 `.claude/` 落 root」正正因為 root = system prompt。Option A 斬斷 coupling 後呢兩條要重寫 → 屬 Phase 3 propagation，唔可以靜靜雞改。

## File map（會掂到嘅 files + 每個做乜）

**Repo-side（呢個 plan session 之後嘅 executor sessions 會改）**
- `docs/architecture.md` — Restart Checklist（In-place + Full Rebuild）+ Architecture Notes system-prompt 段：Phase 3 更新新 cwd / symlink / trust / MCP 步驟
- `docs/dev-guide.md` — 三條鐵律：Phase 3 重寫（root 解封後）
- `CLAUDE.md`（repo root）— **視乎 Phase 1 decision** 可能 relocate 去 `runtime/CLAUDE.md`；未定前唔郁

**Container-side（唔喺 repo，靠 rebuild checklist 記錄，Phase 2 落手）**
- tmux launch line（cwd 參數）
- `/home/node/.claude.json`（trust flags：新 cwd 要 pre-trust）
- `/home/node/*` symlinks（`CLAUDE.md` / `context` / `skills` / `technical`）
- project-level MCP config（discord plugin）掛載位置
- `/home/node/.claude/settings.json`（Stop hooks；確認唔受 cwd 影響）

## Phase 0 — Live-container ground-truth（⚠ read-only spike，硬 gate）

Goal: 唔改任何嘢，先攞齊 container 實況，令 Phase 1 design 有數落。全部經 `zeabur service exec --id 69d3781093577fe0061de8d5 -i=false`（read-only command），**零 mutation**。

- [ ] tmux `main` session 嘅實際 launch line + cwd（`ps aux | grep claude` / `tmux capture-pane`）
- [ ] `/home/node/.claude.json` 現有 trust flags（邊啲 path `hasTrustDialogAccepted: true`）
- [ ] `/home/node` 現有 symlinks（`ls -la /home/node`，確認 `CLAUDE.md` / `context` / `skills` / `technical` 指去邊）
- [ ] project-level MCP config **實際掛喺邊個 path**（discord plugin）——確認係咪真係綁死 `/home/node/kb`，定係跟 cwd move 得
- [ ] `/home/node/.claude/settings.json` 現狀（Stop hooks × 2、permissions.deny）+ 確認佢 read path 唔受 cwd 影響（container quirk：`HOME=/home/node` hardcoded）
- [ ] 確認 harness 攞 system prompt 嘅實際規則：淨係 `<cwd>/CLAUDE.md`？定有其他 fallback（`/home/node/CLAUDE.md` symlink 仲有冇作用）？——實測，唔靠文檔推斷
- [ ] latest transcript 首 turn `cache_read` + `cache_creation`（量 system-prompt surface baseline，Phase 3 對比用）

Verification: 出一份 ground-truth note（可暫擺 `docs/plans/` 旁或貼返 Discord/vault），七項全部有實測答案。**未齊唔准入 Phase 1。**

## Phase 1 — Design decision（唔掂 container）

Goal: 憑 Phase 0 實測，答齊四條 sub-question + 定 target 設計。**呢度先傾兩個 parked decision**（帶 Phase 0 數俾 Kary 揀，唔喺 plan 預設）：
- **D1 — prompt 位置**：canonical prompt (a) relocate 去 repo `runtime/CLAUDE.md`（root 全騰空，payoff 大、改動大）定 (b) 留 repo root 靠新 cwd symlink 指返（低風險、root 仍被佔）
- **D2 — wrapper 去留**：Option A landing 後 retire `DOF-knowledge-base-dev/` 定保留（Kary 2026-07-08：兩條 thread 做完再睇 → 呢度只出 recommendation，唔強逼定案）

- [ ] target cwd 定案（新 dedicated dir vs 其他）+ 點 pre-trust（`.claude.json` flags）
- [ ] project MCP config 跟去新 cwd 嘅具體做法（視 Phase 0 結果）
- [ ] prompt resolution 機制（跟 D1）
- [ ] 出更新版 Restart Checklist **draft**（In-place + Full Rebuild 新步驟）+ rollback 步驟
- [ ] 列明 Phase 3 要改嘅 doc（三條鐵律新版文字草稿）

Verification: 一份 design decision doc（四條 sub-question 有答案 + D1/D2 recommendation + rollback plan），Kary go/no-go 先入 Phase 2。

## Phase 2 — Execute on container（⚠ strong model · container ops · 需 Kary confirm 開工）

Goal: 落實新 cwd。**破壞性 → 先 backup、有 rollback、逐步 verify。**

- [ ] Backup：`/home/node/.claude/settings.json`、`/home/node/.claude.json`、記低現有 tmux launch line
- [ ] 建新 cwd dir + 擺 prompt（跟 D1）+ set trust flags + 搬/接 project MCP config
- [ ] 改 tmux launch line 用新 cwd，in-place restart（`su node -s /bin/sh -c ...`，**唔准以 root 行 claude**）
- [ ] Verify 接返 Discord：`ps aux | grep "discord/0.0"` 見 plugin child + `tmux capture-pane` 無 trust/promo dialog 卡住
- [ ] Golden subset smoke（≥3 條，含一條 job-channel dispatch + 一條 timeline）確認行為冇 regress
- [ ] Fail → rollback（還原 tmux launch + settings + trust flags，restart 返舊 cwd）

Verification: Discord live smoke（Kary 發真 prompt）Mugi 正常 connect + reply；golden subset pass；transcript 見到正常 tool path。

## Phase 3 — Propagate & doc（收尾）

Goal: 令新設計唔會 rebuild 就冧 + 更新受影響文檔。

- [ ] `docs/architecture.md` Restart Checklist（In-place + Full Rebuild 9 steps）改到反映新 cwd / symlink / trust / MCP
- [ ] `docs/dev-guide.md` 三條鐵律重寫（root 解封後邊啲仲成立、邊啲改）
- [ ] 跟 D2 結果處理 wrapper（retire → 記 migration；保留 → 記點解共存）
- [ ] Vault sync（boundary 時經 `/wrap`）：status.md + changelog + `plan-execution-workflow` decision 更新

Verification: 一次 full-rebuild dry-read（唔真 rebuild，逐步對 checklist）確認步驟自洽；受影響 doc 冇殘留舊機制描述。

## Deploy & verify（Mugi 特有）

- **Phase 0**：純 read-only exec，零 deploy。
- **Phase 2 = 真 deploy 界線**：直接掂 live runtime（改 tmux launch + restart）。行前 Kary confirm，行後 golden smoke + transcript check。**唔經 kb-pull**（呢 phase 改嘅係 container-side non-repo 嘢）。
- **Phase 3**：repo doc 改動 → feature branch → Kary go/no-go merge main → 下次 kb-pull 自然帶落 container（doc 零 runtime 影響）。

## Known issues / constraints

- 2026-07-06 cwd move 係為修 folder-trust hang + project MCP config —— 新 cwd 唔 pre-trust / MCP 接唔返 = Mugi 唔 connect Discord（最痛 failure mode）
- `zeabur service exec` 長任務會 EOF —— Phase 0/2 耗時 command 要 nohup detach + poll（`docs/architecture.md` Restart Checklist）
- **唔准以 root 行 `claude`**（觸發 OAuth refresh 將 `.credentials.json` 重寫 root:root，搞死 node-user token refresh）——一律 `su node -s /bin/sh -c`
- `HOME=/home/node` hardcoded 即使 `whoami=root` → settings.json 永遠 read `/home/node/.claude/`
- Container full rebuild 唯一無法自動恢復 = memory folder（同 Option A 無關但 rebuild 時記住）

## Do NOT

- 唔准喺 Phase 0 改任何 container 狀態（純觀察）
- 未過 Phase 1 Kary go/no-go 唔准掂 container（Phase 2）
- **未定 D1 前唔准 relocate / rename repo root `CLAUDE.md`**（現行三條鐵律仍生效直到 Phase 3 正式改）
- 唔准加 `.claude/` / `AGENTS.md` / `GEMINI.md` 落 repo root（Option A landing + 三條鐵律重寫之前，呢條照守）
- 唔准以 root 行任何 `claude` command
- 唔准 `git add .` / `-A`（explicit pathspec only）

## Progress log
<!-- executor 每 session append 一行: YYYY-MM-DD Phase N done — note -->
- 2026-07-08 Plan written（investigate-first framing，Kary confirmed）— 未執行任何 phase

## → Vault（boundary 時 sync 落 vault，唔喺 dev session 寫）
<!-- 執行途中彈出嘅 WHAT/WHY-level 嘢先擺呢度，一行一個，boundary 開 vault session 由 /project-sync 讀走 -->
- [decision] D1（prompt relocate vs symlink）+ D2（wrapper retire vs 保留）Phase 1 定案後入 `00-System/decisions/`
- [scope] 若 D2 = retire wrapper → 影響 `plan-execution-workflow` Mugi variant + repo-skills index
- [decision] 2026-07-08 Kary 定 priority：timeline re-plan（operation 優先）行先；Option A cwd surgery + lean-claude-md 屬修補，押後。plan 寫好 park 住等 timeline 完先執行
