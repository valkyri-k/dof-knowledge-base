# DOF Knowledge Base

Mugi（DOF AI Agent）嘅 context knowledge base。

## Structure

```
CLAUDE.md          — Mugi identity、rules、Calendar credentials 使用方式
context/
  production-pipeline.md   — 製作流程、timeline 標準、後期分工
  team-roles.md            — 團隊角色同職責
  naming-conventions.md    — Job number、Calendar event、Project shorthand 命名規則
  tools.md                 — DOF 使用中的工具同系統
```

## How Mugi Uses This

Claude Code 每個 session 開始時自動讀取 `CLAUDE.md`。`CLAUDE.md` 指示 Mugi 讀取 `context/` folder 內的所有文件作為背景知識。

## Maintenance

直接 edit 對應 `.md` file → commit → push。Zeabur server 需要 restart 或 git pull 後生效。
