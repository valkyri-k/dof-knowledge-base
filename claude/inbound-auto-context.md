# Inbound Auto-Context — Detailed Steps + Edge Cases

> Extracted from CLAUDE.md on [[2026-05-10]] to reduce context-bloat warning.
> **Read this full file when**:
> - 第一次處理 job-channel mention 想記返完整 hit / miss flow + reply phrasing
> - 遇到 cross-job mention（user 喺 J26065 channel 講「順手做埋 J26071」）
> - User 報告話「我 @ 咗你但你冇覆」→ check missing allowlist edge case
> - 唔記得 sticky entity carry-over rule 點同 Job Resolution session entity 互動
>
> CLAUDE.md 入面留咗：trigger、lookup key、「Reply 第一句必須 surface auto-detect 結果」hard rule、miss case 一句 fallback。詳細 example phrasing + edge case 全部喺呢度。

---

## Step 2a — Hit（channel ID 喺 list）

Resolve 出 J# / Project Name / Client / Director / Status，inject 入 reasoning context。**唔需要 user 重複講 job**，直接處理 user request。

Reply 第一句**必須先 surface auto-detect 結果**先做嘢——phrasing 由你 LLM-natural 揀，但呢條 rule 係 hard requirement，唔可以 silent assume。例：

> 收到，呢個 channel 係 J26065 CLP HKMA Smart E Living（Director: Sohling）。要我...

唔可以跳過 surface step 直接 plan timeline / dispatch task / 答嘢——即使 user 嘅 request 完全唔涉及 job ambiguity 都要寫呢一句，俾 user 一眼睇到你 detect 啱左 job。

## Step 2b — Miss（channel ID 唔喺 list）

唔做任何 dispatch / planning / timeline work。Reply：

> 我 current job list 入面冇呢個 channel（ID: `<channel_id>`）。請問你想做咩 task？需要先 confirm 係邊個 job。

呢個 case supposedly 唔應該 trigger（因為 plugin allowlist 已經 gate 入站，即係 channel ID 已經喺 allowlist 但唔喺 job list = 罕見 mismatch）。仍然要寫明，避免 silent fail。

## Step 3 — Reply destination

**Reply 入返同一 channel**——明確覆蓋 Channel Policy 嘅「冇明確 dispatch context 嘅 reply 都喺 home base」default。Job channel inbound 一律喺 trigger channel reply，唔 DM 去 `#ai-agent-mugi`。

例外：Multi-channel dispatch 嘅 outbound 部分（即派去**第三個** channel）跟返 dispatch rule，但**confirmation reply** 仍然喺 trigger channel（即收到 mention 嗰個 channel）。

## Edge Cases

- **`#ai-agent-mugi` 本身**：呢個 channel 唔屬任何 job → auto-context rule **唔 apply**，維持現狀（user 自己 type job context，行 5-layer fuzzy lookup）
- **Cross-job mention**：user 喺 J26065 channel 但講「順手做埋 J26071」→ **explicit J# wins over channel auto-detect**。處理 J26071，但 reply 必須 confirm cross-job intent，例：「你而家喺 J26065 channel，要我 dispatch 去 J26071 channel？」唔可以 silent 派去 J26071
- **Channel ID 喺 KB job-list 但唔喺 plugin allowlist**：你根本收唔到 mention（plugin gate 喺 inbound 之前），呢條 rule 用唔上。如 user 報告話「我 @ 咗你但你冇覆」→ tag Kary 講 missing allowlist
- **Sticky entity carry-over（cross-rule dependency）**：channel auto-resolve 咗 J26065 之後，**下一條 message** 如果 user 講「Smart E」唔可以 silent assume 同一 job——跟 `Job Resolution` 嘅 Session entity carry-over rule（explicit disclose 或重行 5-layer resolution + Layer 5 ambiguity check）。Channel auto-detect 只 set 當前 message 嘅 default context，唔 lock 後續 message
