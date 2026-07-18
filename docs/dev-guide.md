# DOF KB Repo — Dev Guide（Mugi development workflow）

> Canonical dev rules for this repo。Added: 2026-07-08。
> Dev session 入口 = `../DOF-knowledge-base-dev/`（wrapper folder）——**唔好直接喺 repo root 開 Claude Code dev session**，原因見下。

---

## ⚠️ 點解 dev session 唔可以開喺 repo root

Mugi runtime 以 `cwd = /home/node/kb` 行 Claude Code，即係：

- **Repo root 嘅 `CLAUDE.md` 就係 Mugi 嘅 system prompt**（harness auto-load）
- Repo root 嘅 `.claude/`（skills / settings）會直接 load 入 Mugi runtime

所以三條鐵律：

1. **唔准改名 / 取代 root `CLAUDE.md`** 做 dev instructions —— Mugi 下次 restart 會讀錯 system prompt
2. **唔准加 `.claude/`、`AGENTS.md`、`GEMINI.md` 落 repo root** —— 會漏入 Mugi runtime
3. Dev session 開喺 wrapper folder（`../DOF-knowledge-base-dev/`）—— 嗰度先有 dev CLAUDE.md + `/park` `/wrap` skills

`docs/` 呢個 folder 對 Mugi runtime 零影響（冇 dispatch row 指過嚟，Mugi 唔會 load），所以 dev docs / plans 放呢度安全。

---

## Branch rule

| 改動類型 | 例子 | Branch |
|---|---|---|
| Context 小改 | jobs、team、context files、job-list cache | 直落 `main` |
| 行為改動 | `CLAUDE.md`、`skills/`、`infra/hooks/`、`scripts/` | Feature branch + `docs/plans/<feature>.md`，Kary go/no-go 先 merge `main` |
| Runtime writes | container 自己 commit 嘅 `activity/` logs | `main` only（container 只識 main）|

**`main` = deploy 界線**：乜嘢上咗 main，下次 kb-pull 就會落 Mugi container。半熟嘅行為改動唔准上 main —— 留喺 feature branch。

---

## Deploy

- 一律 `scripts/kb-pull.sh`（commit-before-pull，經 `zeabur service exec`）。**NEVER** stash→pull→pop。
- `CLAUDE.md` / context 更新唔使 restart：pull 完喺 Discord 叫 Mugi re-read 對應 file 即可。
- Settings / hooks / launch flags 改動先需要 in-place restart —— 程序 + container ops 詳情（root-claude ban、observability、rebuild checklist）→ [architecture.md](architecture.md)
- Deploy = 掂 live runtime —— 行 kb-pull / restart 之前同 Kary confirm 一次。

---

## Entry reads（開新 dev session 先讀）

1. 呢份 dev-guide
2. [architecture.md](architecture.md) — container 架構 + restart checklist
3. 做緊嘅 `docs/plans/<feature>.md`（如有）
4. 要改 `CLAUDE.md` 行為 → 先讀相關 section 全文，唔好憑印象

---

## Plans

- 位置：`docs/plans/<feature>.md`，由 wrapper `/park` skill 產生，commit 落 feature branch
- Vault（DOF_Build `projects/007-agent-mugi/`）管 WHAT/WHY；plan file 管 HOW —— 唔好 duplicate，link
- Plan 未 commit = 唔存在（第二部機睇唔到）
