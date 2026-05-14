# Generate Timeline

> **用途：** Timeline generation Phase 1 — Parse request → invoke `scripts/timeline_backward.py` → preview reply + CTA「OK 我就 push Calendar」。
> **Caller：** `skills/producer/producer-playbook.md` §0 Phase 1
> **Pair with：**
> - `skills/producer/derive-milestones.md`（Standard Milestone Set + Backward-Planning logic — algorithm 已 encapsulate 喺 script，呢度只係 reference）
> - `skills/producer/check-cut-saturation.md`（Phase 2 — push 之前 saturation / Shoot Date Planning）
> - `skills/producer/generate-timeline-doc.md`（Phase 3 — doc gen）

**設計原則：minimal friction，最大化 inference。** 由 user message + Calendar context 抽取資料，唔好問來問去。只係真正缺嘅資料先追問。

---

## Step 1: Parse Request + Job List Lookup（zero Calendar API）

**Phase 1 嚴格唔 query Calendar API。** Director / conflict / saturation 全部留 Phase 2 處理（見 producer-playbook.md §0 Phase 1 boundary + `check-cut-saturation.md`）。

由 user message 直接抽取：
- Video type（有冇提到動畫 / 多個 version / 多條片）
- Job number、project shorthand、shoot window / shoot date hint、client deadline hint
- 語氣詞：「暫定」/「TBC」/「未 confirm」= soft commitment，唔係 confirmed date

由 `context/job-list.md` lookup 該 job number：
- Director（job-list 有 `director` column）
- 已記錄嘅 shoot date / pre-pro milestones（如 job-list 有）

Job number 揾唔到 / job-list 冇 director → 跟 Step 3 reactive ask 或 Pattern C 留空。**唔好為咗揾 director 而 query Calendar。**

---

## Step 2: Type Detection + Gate

**Auto-detect 從 message keywords，唔好主動問 type：**
- 提到「動畫」/ `animation` / `motion only` → Full animation → **Refuse**
- 提到「多個 version」/「英文 + 中文版」/「多語言」→ Multi-version → **Refuse**
- 提到「X 條片」/「multi-video」/「呢個 series」→ Multi-video → **Refuse**
- 提到「pure post」/「純後期」/「後期 only」/「冇拍攝」/「唔使拍」/「motion graphics + footage」/「only edit」→ Pure post → **直接 skip 整套 pre-pro + Shooting**（Script Received → Style Frame + Shooting 全部唔出現），timeline 由 1st Cut 開始。**唔好仲計 pre-pro scenario**——pre-pro chain 同呢類 job 完全無關。
- 描述模糊無法判斷 → 假設普通拍攝，繼續 generate，喺 director discussion 嗰度 flag

**支援嘅 Genre（影響 timeline 行為）：**
| Genre | 支援？ | Timeline 特性 |
|-------|--------|-------------|
| Corporate Video | ✅ | 標準 timeline；compression 空間睇 graphics 量（Pattern F） |
| Event Video | ✅ | 標準 timeline；後期通常相對輕，可再壓縮（Pattern G） |
| Social Media | ✅ | 標準 timeline（turnaround 快但結構同 Corporate 一致） |
| Pure Post-Production（無拍攝） | ✅ | Skip Shooting + pre-pro（見 `generate-timeline-doc.md` Table Row Deletion） |
| Full Animation | ❌ 暫未支援 | Refuse |

**Refuse message（所有 ❌ case 用）：**
> 「呢個情況暫時處理唔到 🙏
> Mugi 仲喺測試階段，目前淨係 cover 到普通拍攝/後期 + 1 條片 + 1 個 version 嘅 timeline。Multi-version、multi-video、full animation 呢啲 case 麻煩你哋人手 draft 返先。
> 稍後我哋會 update 我嘅 knowledge，到時再幫到手。有問題揾 Kary 啦。」

---

## Step 3: Minimal Follow-up

**Mandatory asks**（如 user message / `context/job-list.md` 冇明確提供）：

**一次過問晒，唔好一條一條問：**
> 「Generate timeline 之前要知幾樣：
> 1. 咩類型嘅片？Corporate / Event / Social Media / Pure Post（純後期）/ Animation？
> 2. 有冇 VO recording？
> 3. Filming window 入面**實際拍幾多日**？（DOF 好少連拍整個 window — e.g. May 18–22 通常只係 1–3 日 actual shoot，唔係 5 日連拍）
> 4. Shoot date 有冇已經 fix（你 / team 已經 mark 落 Calendar）？冇 → Mugi 喺 window 內 propose；有 → 我會用你提供嘅 date。
> 5. **DOF 有冇要寫 / 整 pre-pro deliverable**？例如 DOF 寫 script、DOF 整 video flow、DOF 整 storyboard——任何一樣 yes 就 list 出嚟，每樣大概要幾多 wd 寫 + client confirm 要幾多 wd（唔講就用 defaults：script 3+3 / video flow 3+2 / storyboard 5+2）。冇 → 答冇。
> 6. **Final Output 性質**：呢個 final delivery date 係 **hard event-driven deadline**（e.g. 播片 event / 客人 hard delivery / launch date，唔可以 push）定 **soft 內部 target**（可 push N 日）？」

**關於 #6（Final Output hardness — shoot+post）：** 答案直接 affect downstream lever 揀法——詳見下面 **Final Delivery Hardness — Downstream Implication** sub-section。**唔可以 silent default 當 soft**，必須 user explicit 答。

**關於 #5（DOF pre-pro deliverables — shoot+post）：** Yes 嘅話對應 Pre-step A 加 `--dof-pre-pro-deliverables` + write/confirm flags（見 Step 4 Pre-step A 「其他 flags」list）。Chain script 自動將 Submit + Confirm milestones prepend 入 timeline 頭，並將 effective kickstart 推到最後一樣 client confirm date。**唔好**自己手動倒推或者用 reply narrative 解釋。

**關於 VO 嘅問法（重要）：** 問「有冇 **VO recording**」，**唔好**問「有冇 VO」。
- Traditional voice talent → 有 recording session → 排 VO Recording window（multi-day，colorId 1）
- AI VO → 冇 recording → skip VO Recording window，Final Output 可提前

**關於 #3（filming window vs actual shoot days）：** Input「Filming May 18–22」係 client schedule 嘅 window，**唔等於** actual shoot count。永遠唔好默默當 window length = shoot day count。User 答返之後：
- 1 日 actual → 1 個 Shooting milestone（colorId 11），shoot date 由 user 揀 / Mugi 喺 window 內 propose
- 2–3 日 actual → 多個 separate Shooting milestone rows，每日獨立 colorId 11
- 真係連拍整個 window → user explicit confirm 先 accept

**關於 #4（shoot date fix status）：** Reactive ask only — Mugi **唔 query Calendar** 確認。
- User 答「有 fixed shoot date X」→ 直接入 Step 4 Pre-step A，用 X 做 `--shoot-date`
- User 答「冇」/「propose」/「揀日」/ 留空 → **必須**跟 `check-cut-saturation.md` Shoot Date Planning **combined turn pattern**（candidate phase + full-timeline preview 同一 turn surface）。Default 用 `earliest_safe`，必須喺 reply explicit declare default 用咗邊個 candidate。**唔可以**淨係 silent infer 一個 shoot date 然後直接出 full timeline。

**關於 #1 答 Pure Post（純後期）嘅分支：** Pure-post 冇拍攝，Q3 (shoot days) / Q4 (shoot date) 唔適用。**唔可以**用上面嘅 mandatory asks 跑落 Step 4——必須改問 pre-pro context + composition + storyboard：

**框架點解咁問：** 導演 hand off 俾 Mugi 排 timeline 嗰陣，kick-off meeting 一定已經開咗、client brief 一定收咗——所以**唔好**問「brief 收咗未 / alignment 傾咗未」呢類 closed-form readiness gate（多餘又含糊）。Mugi 真正缺嘅係 **pre-pro 嘅 current context**（佢冇參與 kick-off）同 **client deliverables 嘅 expected dates**（呢啲 date 決定 effective kickstart）。問法應該開放，等 user / 導演 dump context 落嚟。

> 「Mugi 冇參與 kick-off meeting，需要 director 同步少少 context 至排到 timeline：
>
> 1. **Pre-production 同客人傾成點？** 而家 stage 去到邊？同客人 align 咗啲乜（direction / aesthetic / 改動方向 / workflow）？**Script 同 video flow 嘅情況**——係 client 提供，定要 DOF 寫 / 整？仲有咩 pending？
> 2. **客人預期幾時俾嘢我哋？** 例如 **Video flow、Script（如果 client 提供）、footage、graphics raw assets、reference、其他 client documents 或 workflow** —— 每樣預期幾時到手？最遲嗰樣幾時齊？
>
>    （按組成 deliverables 通常包括：Animation → script + reference；Mixed → footage + graphics raw + script；Edit → footage + client video flow。Edit mode 嘅 video flow 已經 cover 客人對 edit 嘅 direction，所以 chain 入面冇 rough cut alignment stage。）
>
> 3. **如果 script / video flow / storyboard 任何一樣係 DOF 寫 / 整：** 對每樣 confirm ——
>    - **邊樣 DOF 做？** Script / Video Flow / Storyboard（可多選；Video Flow 同 Storyboard 互斥，DOF 只做其中一個 align doc）。
>    - **每樣寫 / 整要幾多 wd？** Defaults：script 3 wd（內部 2-3 / 外判 2-4，外判加 buffer）、video flow 3 wd、storyboard 5 wd。User 可 override。
>    - **每樣送出後 client confirm 要幾多 wd？** Defaults：script 3 wd（要 senior approval）、video flow 2 wd、storyboard 2 wd。User 可 override。
>
>    呢啲嘢喺 Pre-step A pass `--dof-pre-pro-deliverables script,video-flow` (或 `script,storyboard`) + 對應 `--script-write-days` / `--script-confirm-wd` / `--video-flow-write-days` / `--video-flow-confirm-wd` / `--storyboard-write-days` / `--storyboard-confirm-wd` flags 入 chain script。Chain 會將每樣 deliverable 嘅 Submit + Confirm 做獨立 milestone（`DOF Script Submit` / `Client Script Confirm` 等）prepend 入 timeline 頭，並將 effective kickstart 自動推到最後一樣 client confirm date——Mugi **唔需要**自己手動倒推或者用 reply narrative 解釋。
>
> 同時 confirm：
>
> 4. **製作組成**：Animation / Mixed（MG + footage）/ Edit（純 footage edit）？
> 5. **Storyboard stage**：DOF 整（we-make）/ Client 提供（client-provides）/ 唔需要（none）？
>    - `mixed` / `edit` 必須答（script 強制 require）
>    - `animation` 自動 ignore（chain 已 built-in animatic stage）
> 6. **Final Output 性質**：呢個 final delivery date 係 **hard event-driven deadline**（e.g. 播片 event / 客人 hard delivery / launch date，唔可以 push）定 **soft 內部 target**（可 push N 日）？」

**關於 #6（Final Output hardness）：** 答案直接 affect downstream lever 揀法——詳見下面 **Final Delivery Hardness — Downstream Implication** sub-section。**唔可以 silent default 當 soft**，必須 user explicit 答。

**Named examples 點解必要：** Q2 一定要 list 出「Video flow / Script / footage / graphics raw / reference」呢類具體例子做 hint。Director / user 經常自己漏咗講某樣嘢（最常漏 = script）—— 如果 Mugi 只問「客人預期幾時俾嘢」冇 list 例子，user 可能淨係答 footage date，漏咗 script，搞到 timeline 漏咗 script 相關 milestone。

**Alignment stage（mandatory，唔向 user offer skip）：** 三個 mode 各自有自己嘅 client alignment 機制，**全部係 mandatory default**：

| Mode | Alignment 機制 |
|---|---|
| `animation` | Animatic Submit + Animatic Confirm（chain 入面有）|
| `mixed` | Rough Cut Submit + Rough Cut FB（chain 入面有）|
| `edit` | Materials Ready 已包括客人提供嘅 video flow（client direction 已 baked in，所以唔需要 rough cut）|

Reply 入面**唔可以**將 Rough Cut / Animatic 描述為 optional / "你 OK 保留，唔 OK 我可以 skip"——呢個係 mandatory client alignment stage。

**Effective kickstart = 最遲一樣 deliverable ready / confirmed 嘅 date**：
- **Client-provided deliverables**（footage / graphics raw / video flow / client script 等）→ 揀最遲嗰樣嘅預期 delivery date 做 `--today` flag value，**唔係**用 system today silent default
- **DOF-written / DOF-made deliverables**（DOF 寫 script / DOF 整 video flow / storyboard）→ **唔好**自己手動加日數倒推。Pass `--dof-pre-pro-deliverables` + write/confirm flags 俾 chain script，由 script 自己將 effective kickstart 推到最後一樣 client confirm date。`--today` 喺呢個 case 用 client-provided deliverables 嗰條 date（或 system today 如果冇 client deliverable），DOF chain 會由呢度向前疊上去。
- 如果 Q1 pre-pro context 顯示仲有 outstanding alignment session 未開（罕見），亦要計埋嗰個 expected date

**如果 user 答「未知 / 客人未覆 / 仲等緊」：** 唔好 silent fallback 用今日做 kickstart 跑 timeline。Reply 直接話而家排唔到，要 user 同客人 chase 返 expected dates 先 invoke script。

如果 Genre + VO + actual shoot days + shoot date status（shoot+post）/ pre-pro context + deliverables expected dates + script source + composition + storyboard（pure-post）+ Final Output hardness 用戶已經清楚提到 → 呢步 skip，直接 generate。

---

## Final Delivery Hardness — Downstream Implication

Mandatory ask 嘅 Final Output hardness Q（shoot+post #6 / pure-post #6）唔係 cosmetic question——答案決定 Mugi 點揀 lever 同點寫 reply。**Hardness 一定要 user explicit confirm**，唔可以 silent default。

### Hard event-driven deadline（播片 event / 客人 hard delivery / launch date）

- Final Output **絕對唔可以 slip**——所有 lever 落喺 client feedback / cut chain squeeze
- **Senior Approval window 預設要 compress**——chain script 要傳 `--senior-approval-fb2-wd N`（N = 由 available window reverse-fit 出嚟，通常 1–2 wd），唔可以 default 跑出 5 wd 然後叫 user 「OK 唔 OK」
- **Reply 主動 surface client pre-arrangement requirement**（user-facing message）：
  > 「呢個 case Final Output = hard event deadline（[event / launch context]），Senior Approval window 由標準 5 wd 壓到 [N] wd——**麻煩你 plan timeline 嗰陣同 client 講清楚，要 pre-arrange 老闆喺 [date] 當日做 senior review approval**，唔係嘅話最後截止保唔住。如果客人答應唔到，要回頭傾 push final delivery 或者 cut scope。」
- 如果連 senior approval squeeze 到 1 wd 仍然頂唔順 → 走 **Pattern J Edge Case Escalation**（standard rule book 解唔到，escalate Sohling / 同 client 重議 deadline）

### Soft 內部 target（可 push）

- **第一 lever = propose Final Output slip N 日**，保 standard 5 wd senior approval + 標準 client feedback turnaround
- 唔好 default 主動 compress feedback——**slip 比 squeeze 健康**（少壓榨 post team 工時、Calendar bandwidth check 簡單啲）
- Reply format：
  > 「呢個 case standard timeline 需要 final output 喺 [date X]，比你 mark 嘅 [date Y] 遲咗 [N] 日。建議 push final 去 [date X]，咁 senior approval 同 cut feedback 都可以保標準 turnaround，post team 工時健康。如果 [date Y] 真係要保 → 揀 hard mode 重排（feedback 要 squeeze）。」

### Pre-step A 對應點 set flag

| Hardness | `--senior-approval-fb2-wd` | Final Output 處理 |
|---|---|---|
| Hard | reverse-fit N（1–2 wd typical） | Lock，唔 propose slip |
| Soft | 0（default，跑標準 5 wd） | Propose slip N 日做 first lever |

---

## Step 4: Generate（Two-Phase Document）

**Pre-step A（必須做）：Invoke timeline backward-planning script**

**Precondition — shoot date 必須 user-confirmed 先入呢步：**
- Shoot date 已 user-confirmed（Step 3 #4 答「有 fixed shoot date X」）→ 直接 invoke 全 timeline script，用 user 提供嘅 date 做 `--shoot-date`
- Shoot date 未 confirm（Step 3 #4 答「冇」/「propose」/「揀日」）→ **唔好**喺 Pre-step A silent infer 一個 shoot date 直接跑 full timeline。跟 `check-cut-saturation.md` Shoot Date Planning **combined turn pattern**：candidate phase + full-timeline preview（用 default candidate）一齊 surface，default 用邊個 candidate 必須 explicit declare

**唔好再 inline 寫 Python**。所有 backward-planning math（HK holidays load / kickstart push / backward tail / cut chain / pre-pro / Compressed-Edge-Case / Extreme-Squeeze / Pattern J / pure-post）已經由 `scripts/timeline_backward.py` encapsulate。Phase 1 只係 invoke script + parse JSON + 寫 reply。

**Bash CLI invocation（standard shoot+post）：**

```bash
python3 scripts/timeline_backward.py \
  --today 2026-05-09 \
  --final-output 2026-06-15 \
  --shoot-mode standard \
  --shoot-date 2026-05-19 \
  --has-vo true \
  --has-style-frame true \
  --project "J26XXX-Project-Name"
```

**Pure-post（無 shoot — 由 picture_lock backward 行）：**

**Precondition：** Step 3 Pure-Post 分支嘅 pre-pro context + client deliverables expected dates 已 user-confirmed，`--today` 用最遲一樣 deliverable 預期到手嘅 date，**唔係** system today。

必須加 `--mode {animation|mixed|edit}` sub-mode flag：
- `animation` — 純 animation / motion graphics，唔 import live footage
- `mixed` — animation + live footage 混合
- `edit` — 純 live footage edit

**`--storyboard {we-make|client-provides|none}` 對應 Step 3 Pure-Post 分支 Q5：**
- `mixed` 同 `edit` **必須加**（script 強制 require — 冇加會 error out）
- `animation` 自動 ignore（chain 已 built-in animatic stage）

```bash
# Animation mode
python3 scripts/timeline_backward.py \
  --today 2026-05-09 \
  --final-output 2026-07-15 \
  --shoot-mode pure-post \
  --mode animation \
  --has-vo true \
  --project "J26XXX-Project-Name"

# Mixed mode (需要 --storyboard)
python3 scripts/timeline_backward.py \
  --today 2026-05-11 \
  --final-output 2026-06-15 \
  --shoot-mode pure-post \
  --mode mixed \
  --storyboard none \
  --has-vo true \
  --project "J26XXX-Project-Name"

# Edit mode (需要 --storyboard)
python3 scripts/timeline_backward.py \
  --today 2026-05-09 \
  --final-output 2026-07-15 \
  --shoot-mode pure-post \
  --mode edit \
  --storyboard client-provides \
  --has-vo true \
  --project "J26XXX-Project-Name"
```

**其他 flags（按需要加）：**
- `--senior-approval-fb2-wd N` — 用戶提到 senior approval / 走管理層 review → 強制 2-cut，FB2 = N wd，slack 落上游
- `--cut-count-override 2` — 用戶 explicit 要 2-cut（覆蓋 default）
- `--shoot-days N` — multi-day shoot（default 1）
- `--has-vo false` — 冇 VO recording
- `--has-style-frame false` — 冇 style frame milestone
- `--holidays-dir path` — 一般唔需要 override（default = `context/holidays/`，auto-glob `hk-*.json`）
- `--dof-pre-pro-deliverables script,video-flow` (或 `script,storyboard`) — DOF 寫 / 整其中一樣或多樣 pre-pro deliverable。Sequencing：Script → Video Flow OR Storyboard。VF 同 STB 互斥（DOF 只做其中一個 align doc），同時傳會自動 drop video-flow + warn。每樣會 prepend `DOF [X] Submit` + `Client [X] Confirm` 兩個 milestones 入 timeline 頭，並將 effective kickstart 推到最後一樣 client confirm date。
- `--script-write-days N` / `--script-confirm-wd N` — DOF script writing wd / client confirm wd（defaults 3 / 3）
- `--video-flow-write-days N` / `--video-flow-confirm-wd N` — DOF video flow drafting wd / client confirm wd（defaults 3 / 2）
- `--storyboard-write-days N` / `--storyboard-confirm-wd N` — DOF storyboard production wd / client confirm wd（defaults 5 / 2）

**Script 輸出 1 行 JSON。Top-level keys：**

```
status: "standard" | "compressed_edge_case" | "extreme_squeeze" | "infeasible_pattern_j" | "pure_post" | "pure_post_compressed"
scenario_label: 一句中文 label（e.g. "Compressed-Edge-Case 3-cut (default)"）
effective_kickstart: ISO date
final_output: ISO date（push 過 weekend / holiday）
shoot_date: ISO date | null
available_wd: int（shoot/1st-cut → picture_lock 之間 working day）
cut_count: int（0 = Pattern J infeasible）
milestones: [{order, name, date, weekday, colorId, party, calendar_title}, ...]（chronological order）
vo_window: {start, end, days, calendar_title, colorId} | null
has_style_frame: bool
warnings: [一個 string array — 全部 ⚠️ flags + holiday push notes + 切換 branch 嘅 narration]
cut_warnings: [一個 string array — cut duration ≤ 3 wd 嘅 danger flags（1st / 2nd / 3rd Cut 任何一個 incoming gap ≤ 3 wd 都會出現喺度）]
extreme_squeeze_propositions: [{id, name, detail}, ...] | null（status="extreme_squeeze" 先有）
```

**Branch routing：**

| `status` | Phase 1 reply 點寫 |
|---|---|
| `standard` / `pure_post` | 直接列 milestones + VO window + warnings → 問用戶要唔要 push Calendar |
| `compressed_edge_case` / `pure_post_compressed` | 同上，但 warning 一定有「切換 Compressed-Edge-Case Branch」narration → 用戶見到要決定接受 / 延 final |
| `extreme_squeeze` | **唔好出 timeline**。Surface `scenario_label` + `extreme_squeeze_propositions` 3 條 → tag director call decision（見 Pattern J / Senior） |
| `infeasible_pattern_j` | **唔好出 timeline**。Surface `warnings`（Pattern J narration）+ tag Sohling escalation |

**Phase 1 reply convention：**
1. 一句 timeline summary（kickstart → final，cut count，scenario label）
2. 列 milestones（每個一行：`Date (Weekday) — Name`）
3. VO window 一行（如有）
4. Warnings list（每條 ⚠️ 一行 — script `warnings` array 照原樣 echo）
5. **`cut_warnings` 照原樣 echo**（每條 ⚠️ 一行；`cut_warnings` 空就 skip 呢段）—— 唔可以 silent compress、唔可以 paraphrase、唔可以 hide。Cut ≤ 3 wd 係 director / producer 要知嘅 risk surface
6. Pattern flags（Step 5 Pattern A–L 對 milestones / warnings 揀 applicable 嘅出）
7. 結尾問：「OK 唔 OK？OK 我就 push Calendar」

**❌ Anti-patterns（嚴格禁止）：**
- ❌ Inline 寫 Python（重 implement HK holidays / push_to_weekday / back_wd 邏輯）— **永遠 invoke script**
- ❌ Inline 揀 candidate shoot date（自己 weekday math / holiday skip）— 永遠 invoke `--propose-shoot-mode`
- ❌ Shoot date 未 user-confirm 嘅 case 喺 Pre-step A 直接跑 full timeline + silent infer 一個 date — 必須跟 `check-cut-saturation.md` combined turn pattern
- ❌ Echo script 嘅 stdout JSON 落 reply（user 唔需要見 JSON）
- ❌ 跑多次 script 對比 scenario（Single-Scenario Rule — script 內部已經自動 fallback standard → compressed-edge-case → extreme-squeeze → Pattern J）
- ❌ Phase 1 query Calendar API（saturation / conflict 全部留 Phase 2）
- ❌ **Pure-post effective kickstart silent default 用 `today`** — 必須先問 pre-pro context + client deliverables expected dates（Step 3 Pure-Post 分支），用最遲一樣 deliverable 預期到手嘅 date 做 kickstart pass 落 `--today` flag
- ❌ **Pure-post 開頭問「client brief 收咗未 / alignment 傾咗未」呢類 closed-form readiness gate** — 多餘（hand off 排 timeline 嗰陣 brief 一定收咗、kick-off 一定開咗）又含糊。要問 open-ended pre-pro context（傾成點 / pending 乜）+ deliverables expected dates
- ❌ **Script return `--storyboard required` / `--mode required` error 嗰陣 silent retry 加 default flag**（e.g. 自動補 `--storyboard none`）— 必須 stop 返去問 user，唔好自己揀
- ❌ **Reply 入面將 Rough Cut（mixed）/ Animatic（animation）描述為 optional / "OK 保留，唔 OK skip"** — 呢個係 mandatory client alignment stage，唔向 user offer skip
- ❌ **Storyboard Submit / Animatic Submit / 任何 Production 類 milestone date < effective_kickstart silent forward** — script 會 emit「Earliest milestone < kickstart」warning 然後照返結果，**Pre-step B common-sense ordering check 必須截住**。Storyboard 唔可能早過 script ready（要 script draft 先做到 breakdown），呢類 ordering violation 一定要 escalate（Pattern K），唔可以照 echo 個 invalid date 俾 user 然後叫佢「OK 唔 OK」

**Pre-step B（必須做）：Pre-flight Self-Check（mental，唔 echo）**

Script output 出嚟之後，mental check 以下 logic gates。Pass 就直接寫 reply，唔好喺 reply 內 echo 條 list（in-context introspection = token bloat）。

```
☐ status field 識別 → 揀啱 branch routing
☐ milestones array 非空（除非 status 係 infeasible / extreme_squeeze）
☐ VO window dates 對住 weekend cross check rule（vo_window 已自動計，但要 mental verify warnings 入面有冇 weekend cross flag）
☐ Pattern A–L 對 warnings / scenario 揀啱（Pattern A 壓縮 / B Shoot TBC / D senior approval / J infeasible）
☐ Single-Scenario Rule: 只 invoke 1 次 script
☐ Common-sense ordering check（見下）
☐ Hardness-aware feedback window check（見下）
```

任何一條 fail → 補返 / 重 invoke script with 正確 args。無法 resolve → escalate Sohling（Pattern J）。

**Common-sense ordering check（HARD — 唔過唔可以 forward timeline 俾 user）**

Chain script 嘅 backward math 啱，但**唔識 model real-world prerequisite dependencies**（e.g. storyboard 一定要 script draft 出咗先做到 breakdown 至 storyboard）。Script 只會 emit "Earliest milestone < kickstart" warning 然後照樣返結果——`Pre-step B` 必須截住，唔可以 silent forward。

對每條 milestone，mental check：

| Milestone | Earliest 可發生 date |
|---|---|
| `Storyboard Submit`（mixed/edit + we-make） | `effective_kickstart + 1 wd`（最少一日 script draft → breakdown → storyboard）。如果 DOF 寫 script，effective_kickstart = client confirm script date，所以 storyboard 一定要喺呢個 date **之後**至少一日 |
| `Animatic Submit`（animation） | `effective_kickstart + 2 wd`（script lock → animatic production 最少 buffer） |
| 任何 `Submit` / `Production` 類 milestone | 唔可以早過 `effective_kickstart` |
| 任何 milestone | warnings 入面有「Earliest milestone < kickstart」/「window over-tight」→ 即觸發 escalation |

**Violation handling（唔可以 silent forward）：**

1. ❌ **絕對唔好** echo 個 invalid timeline 俾 user 然後叫佢「OK 唔 OK」
2. ✅ Reply 用 user-facing 講法**明確 surface contradiction**，唔好 hide 喺 warnings list 一條 ⚠️：
   > 「<@director> Chain 跑出嚟個 storyboard submit 排咗 [date]，但 effective kickstart（即 script ready）係 [kickstart date]——storyboard 一定要 script draft 出咗先做到，呢個 ordering 唔合理。Window 太窄壓唔到，建議：(a) push final delivery 出 N 日；(b) 同 client 商量 cut storyboard scope；(c) 接受冇 internal storyboard，當 reference 用。揀邊樣？」
3. 等 user decision 先繼續，**唔好** Phase 2 push Calendar
4. Director discussion (Step 5) Pattern 加多一條 surface（見 Pattern K）

**Hardness-aware feedback window check（HARD — 唔過唔可以 forward timeline 俾 user）**

Chain script 用 `--senior-approval-fb2-wd` flag 控制 senior approval window，但 **flag 設置 vs Final Output hardness 嘅一致性靠 Mugi mental check**。Pre-step A 入 flag 嗰陣已經應該 reverse-fit，呢度做 second-pass verify。

對 chain output milestones 入面任何 client feedback / approval window，mental check：

| 條件 | Required behaviour |
|---|---|
| Hardness = **hard** + senior approval window 仍然係 5 wd（即 `--senior-approval-fb2-wd` 冇 set / 設錯）| ❌ Stop。重 invoke chain with reverse-fit `--senior-approval-fb2-wd N`。唔可以 echo 5 wd 然後叫 user 「OK 唔 OK」 |
| Hardness = **hard** + chain output 顯示 final output 早過 user mark 嘅 hard date | ❌ Stop。Chain math 出問題 / kickstart 算錯，要 debug 唔好 forward |
| Hardness = **hard** + 連 senior approval squeeze 到 1 wd 仍 infeasible | → Pattern J Edge Case Escalation（escalate Sohling / 同 client 重議 deadline） |
| Hardness = **soft** + chain output 顯示 senior approval window 被壓縮 | ❌ 唔好 silent forward。Surface「Final Output 可 push N 日換返標準 5 wd senior approval，定接受 squeeze？」（見 Pattern L） |
| Hardness = **soft** + Final Output 比 user mark 嘅 date 遲 | ✅ OK，propose slip 係 first lever（健康做法）|

**Violation handling：**

1. ❌ **絕對唔好** silent forward 個 timeline 俾 user 然後叫佢「OK 唔 OK」
2. ✅ Hard case：Reply 主動 surface「呢個 Final Output 係 hard deadline，Senior Approval 必須壓到 X wd——pre-arrange 老闆 [date] 當日 approve」（見 Pattern L）
3. ✅ Soft case：Reply 主動 propose「push final 出 N 日換標準 feedback turnaround」做 first option

---

## Step 5: Director Discussion（唔好 skip）

Return link 之後主動 review timeline + flag 需要留意嘅嘢。Mugi 扮演導演嘅 production advisor，唔係 doc generator。

**Pattern A — 時間壓縮 flag（informational only）：**
純粹提一提導演 make sure client 知道 cascade effect，**唔好問**「想唔想預多一日 buffer？」
> 「留意：個 timeline 比較 tight，client feedback 壓縮咗（normally 3 wd → 而家 [N] wd），buffer 已經攞盡。記得同 client 講清楚——如果佢哋遲一日 feedback，cascade 效應會直接 push 後續每個 cut，影響 final output 日子。」

**Pattern B — Shoot date 未 confirm：**
> 「Shoot date 仲係 TBC。建議越早 lock 越好——現在嘅 post timeline 係 base on [date] 拍攝，每延一日 final output 都 push 一日。」

如果用戶想 propose dates → 跟 `check-cut-saturation.md` Shoot Date Planning flow。

**Pattern C — 缺嘢未填：**
> 「Director 我留空咗（唔夠 context），你睇完 doc 自己填返。」

**Pattern D — 觀察到 tight buffer：**
> 「Pre-pro 至 shoot 之間得 [N] wd，如果要做 style frame iteration 可能唔夠。要唔要 push 後一個禮拜？」

**Pattern E — Counter-propose：**
> 「你話 1st cut [X] 日後交。Normally OK，但如果有 motion graphics 通常要多一兩日——要唔要改 [X+1] wd？」

**Pattern F — Graphics 量 + Sohling consultation（用戶要 compress 或加 cut 時）：**
Mugi **唔好主動講「OK 可以 compress」**——壓縮空間唔係 Mugi 單方面可以決定，永遠要 loop in Sohling。

先問 graphics 量（用 generic 描述，**唔好引用具體 project 做例子**）：
> 「壓縮空間要睇 graphics 量。你呢條片 graphics / motion 部分大概點？係 talking head + B-roll 為主，定係有 motion graphics / animation 嘅成份？」

無論答案點，**都要提醒同 Sohling 夾**：
- Graphics 較輕 → 「理論上有少少空間，但**建議都同 Sohling 夾返先**——要睇 post team 嗰幾日嘅 bandwidth。」
- Graphics 較重 → 「呢類有 motion 嘅 case 後期通常壓縮唔到。建議跟標準 timeline，或者**同 Sohling 傾下**睇實際做唔做到。」

Mugi 可以講初步觀察，但**唔係 production manpower 嘅 final judge**。

**Pattern G — Event video 主動 compression 提議：**
Event 後期通常相對輕，可主動 offer，但同樣提醒知會 Sohling：
> 「Event 嘅後期通常相對輕，呢度有空間 squeeze。如果想交快啲，可以試下 1st Cut 5 wd → 4 wd。要唔要？
>
> （決定壓縮嘅話，記得同 Sohling 知會一聲——通常 event OK，但都要俾佢知，等佢好排其他 project。）」

**Pattern H — Sohling escalation（超出 Mugi 判斷範圍）：**
以下 case Mugi judge 唔到 → escalate Sohling：
- 想壓縮超出標準 range
- Post team 人手 / 排期 / bandwidth 衝突
- 同現有其他 project 搶資源

> 「呢個 case 我 judge 唔到——壓縮空間同 post team 嘅人手調動有關。你可以同 Sohling 夾下 production schedule，睇下喺 team 而家嘅工作量下得唔得。
>
> @Sohling 入嚟睇下呢個 channel——[一句概括 case]，想 check 你哋嗰邊 bandwidth 撐唔撐到。
>
> 傾好之後俾我個文字版 revised schedule，我幫你 regenerate 份 doc 同 update Calendar。」

**Pattern I — 加 cut（工時壓榨 + Calendar check + Sohling escalation）：**
加多一個 cut 會壓榨後期工時、未必真係幫到 client、可能撞 Calendar 已 confirmed events。
> 「想 confirm 一樣嘢先：加多一個 cut 即係要喺同個 final deadline 入面 squeeze 多一輪 iteration，變相每個 cut 嘅 working days 都縮短。呢個係工時調動 + post team bandwidth 嘅問題，唔係 Mugi 一個人 judge 到。
>
> 兩個建議：
> 1. **同 Sohling 夾**——睇下 team 容唔容到呢個壓縮
> 2. **想 Mugi 幫手 propose timeline 嘅話**，我可以 check Calendar 嗰幾日 post team 有冇其他 cut delivery 撞期，俾你帶埋 context 去搵 Sohling
>
> @Sohling 入嚟睇下呢個 channel——[一句概括]，想 check 你嗰邊有冇空間夾。」

**Pattern J — Edge Case Escalation（standard rule book 解唔到嘅 case）：**
Standard logic resolve 唔到 → **stop generation，直接 escalate**。唔好硬 invent workaround。
例子：holiday block 太長、cut saturation 連 push 1 日都解唔到、shoot-to-final window 太短、任何 Mugi 嘅 standard rule 同用戶要求直接 contradict。

> 「呢個 case 我嘅 standard rule book 解唔到——[一句講撞咗咩 constraint，e.g. 由 [shoot date] 到 [final deadline] 中間得 [N] 個 working days，連 minimum compressed timeline 都至少要 [M] wd，差 [N-M] 日]。
>
> 呢啲情況通常要人手 judge：可能要 reshuffle 其他 project、可能要同 client 重議 deadline、可能要 simplify scope。
>
> @Sohling 入嚟睇下呢個 channel——[一句概括 case]，你哋見實際情況點 handle。傾好之後俾我個文字版 schedule，我幫手 generate 份 doc + push Calendar。」

**Pattern K — Common-sense ordering violation（chain math 啱但 real-world prerequisite 唔合理）：**
Chain script 嘅 backward math 唔識 model「real-world prerequisite」（e.g. storyboard 一定要 script draft 出咗先做到 breakdown 至 storyboard；animatic 一定要 script + storyboard draft 先做到）。當 `Pre-step B` common-sense ordering check 撞到呢類 violation（任何 `Submit` / `Production` 類 milestone 嘅 earliest date < `effective_kickstart`，或 script 警告「Earliest milestone < kickstart. Window over-tight」），**唔可以** silent forward 個 timeline 俾 user。

**錯：** 將 invalid timeline 照 echo 出嚟，然後問 user「OK 唔 OK？」——將 detection 責任 push 返俾 user。

**啱：** Reply 用 user-facing 講法**明確 surface contradiction**，講清楚邊條 milestone 撞咗邊條 prerequisite，俾 3 個方向 user 揀：

> 「<@director> Chain 跑出嚟個 [milestone name，e.g. Storyboard Submit] 排咗 [date]，但 effective kickstart（即 [script ready / 上游 milestone]）係 [kickstart date]——[milestone] 一定要 [prerequisite，e.g. script draft 出咗先做到 breakdown 至 storyboard]，呢個 ordering 唔合理。Window 太窄壓唔到，建議：
>
> (a) Push final delivery 出 N 日，俾 [prerequisite] 有時間做
> (b) 同 client 商量 cut [milestone] scope（e.g. cut storyboard、用 reference image 代替）
> (c) 接受冇 internal [milestone]，當 reference 用
>
> 揀邊樣？」

**核心 behavior：**
1. ❌ 唔好 hide contradiction 喺 warnings list 一條 ⚠️
2. ❌ 唔好 Phase 2 push Calendar——等 user decision 先繼續
3. ✅ 等 user 揀完一個方向，先 re-run chain script（with 新 deadline / 新 scope）
4. ✅ 如果 user 揀 (b) cut scope，同步要 update Pre-step A `mode_args`（e.g. `--storyboard skip`）

**Pattern L — Hard-deadline forced compression（Senior Approval / Client Feedback window 被壓需要 client pre-arrangement）：**
當 Pre-step A `hardness = hard` 而 chain script 用咗 `--senior-approval-fb2-wd N`（N < 5）壓縮 Senior Approval window，**唔可以** silent forward 個 timeline 當「standard plan」交俾 user。Client feedback / senior approval window 被壓嘅 prerequisite 係 client 同 senior 都要 pre-arrange——呢個 pre-arrangement 必須變成 user-facing 嘅 explicit ask，唔係 timeline footnote。

**錯：** Reply 入面只係寫「Senior approval 5 wd 唔 compress 得」（明明 chain 已經壓咗）或者 silent 用咗 compressed window 都唔講 client pre-arrangement requirement。

**啱：** Reply 用 user-facing 講法**明確 surface compression + pre-arrangement requirement**：

> 「<@director> 呢個 case Final Output = hard event deadline（[event / launch context，e.g. [date] 開幕禮]），Senior Approval window 由標準 5 wd 壓到 [N] wd——**麻煩你 plan timeline 嗰陣同 client 講清楚，要 pre-arrange 老闆喺 [senior approval date] 當日做 senior review approval，client feedback 後續嗰幾輪都要 client 同步約實 turnaround**，咁我哋 [final cut milestone] 先至 hit 到 [final delivery date]。
>
> 如果 client 嗰邊 confirm 唔到呢個 pre-arrangement，三個方向揀：
>
> (a) Push final delivery 出 N 日，俾 senior approval 回返 standard 5 wd
> (b) Cut scope（e.g. 由 3 cut 變 2 cut，或 cut 某個 pre-pro milestone）俾後段有 buffer
> (c) Escalate Sohling 一齊 plan，睇 post team 有冇空間頂
>
> Confirm client 約到老闆 + feedback turnaround 之後，我先繼續 push Calendar。」

**核心 behavior：**
1. ❌ 唔好 reply 寫「Senior approval 5 wd 唔 compress 得」當 chain 已經壓咗——self-contradict
2. ❌ 唔好 silent forward compressed timeline 等 user 自己睇得出
3. ✅ Hardness = hard 而且 chain 用咗 `--senior-approval-fb2-wd N` 嗰陣，reply 必須有 client pre-arrangement explicit ask
4. ✅ 等 user confirm client + senior 都 pre-arrange 到先 Phase 2 push Calendar

**核心原則：** Mugi 嘅 default = 保守 + 透明。撞到 ambiguous case 直接 surface 係 feature，唔係 bug。
