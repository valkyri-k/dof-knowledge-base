# Derive Milestones — Reference (Algorithm Spec)

> **Phase 1 hot path 唔需要呢個 file。** Algorithm 已完整實作喺 `scripts/timeline_backward.py`，呢度只係 spec 供 troubleshoot / explain rationale 用。
> **Caller：** 罕見 case — 導演 / Kary 問「點解 timeline 咁排」需要展開 rationale；或者 debug script output。
> **Pair with：** `skills/producer/derive-milestones.md`（hot path — milestone naming + prerequisites + completeness rule）

---

## Pre-Pro → Shoot 最關鍵 dependency

Shoot date − Script Lock = **7 wd**

由 shoot date **back-calculate** pre-pro chain（**default = standard，唔好同時計 compressed**）：
```
Shoot date
  ↓ -7 wd
Script Lock (#4)
  ↓ -5 wd
Submit Video Flow (#2)
  ↓ -5~6 wd
Script Received (#1, T0)
```
Pre-pro total：T0 → Shoot ≈ **17–18 wd (~3.5 週)**

---

## VO Recording Window 詳細 logic

**VO recording 唔可以單日 schedule。**

| Field | Logic |
|-------|-------|
| Window 開始 | Picture Lock + 1 wd |
| Window 長度 | 2 wd（standard） |
| Latest end | Final Output - 2 wd |
| Working day cross check | Window 入面每一日都唔可以撞 weekend / public holiday。任一日撞 → shift 整個 window 後；後面頂唔順 → shift 前；都唔得 → @Sohling |
| Preview + doc display 格式 | Date column: `May 21–22`；Day column: `Thu–Fri` |
| Calendar push | 一個 multi-day all-day event（`end.date` = 最後一日 + 1，end exclusive），colorId `1` |

---

## Pre-Pro Chain Reasoning（rationale，script 已實作）

- **Script Received → Submit Video Flow（5–6 wd）：** DOF 需要時間將 script breakdown 成 visual treatment + graphic reference。Compressed 可收縮至 3–4 wd 但唔建議。
- **Submit Video Flow → Script Lock（5 wd）：** Client 通常要做 internal review，可能涉及 senior approval。Compressed min 3 wd。
- **Script Lock → Shoot（7 wd standard / 3 wd min）：** Props、location confirm、crew briefing、shotlist finalize。壓縮到 3 wd 會影響 prep quality。
- **Graphics Ref bundle with Video Flow：** Default 同日 submit + 同日 confirm，費事 client 分開 approve。Calendar 入面係獨立 events——post team（Keith、Wayne）需要分開 track。

**Script Lock 嘅 semantics：** Script Lock = Confirm Video Flow（同一回事，一個 milestone）。Script 至少 90% firm，之後「飛紙仔」係允許的但唔影響 structure。

**Submit / Confirm bundling rule：**
- Client-facing：同日 submit / 同日 confirm（兩對各一日）
- Calendar：4 separate events
- Doc / preview：4 independent rows

---

## Post-Production Backward-Planning from Final Delivery Anchor（script 已實作）

**核心原則：Final Delivery Date 係 HARD ANCHOR，永遠唔向前 pull。**

當 client 有明確 final delivery date（e.g.「6月15日交片」），呢個 date 就係 anchor：
- ✅ 由 Final Output 倒推返 C/S → VO → Picture Lock
- ✅ 多出嚟嘅時間擺去 cut iterations / cut gaps（俾 post team buffer）
- ❌ **唔可以**因為 timeline 寬鬆／壓到 2 cuts 就 pull Final Output 早過 client deadline
- ❌ **唔可以**「forward-chain from Shoot」噉計到 Final Output = 6月11日（早過 client 6月15日）

**冇 client deadline 嘅情況（必須主動問）：**
> 「Client 嗰邊有冇 confirm final delivery date？呢個係 anchor，timeline 由佢倒推。冇 confirm 嘅話我可以用 default forward-chain 計，但建議你 check 返先。」

### Backward-Planning Algorithm（適用 standard shoot+post + pure-post）

**Step 0 — Anchor Kickstart Date**
`kickstart_date = today`（default）/ user-stated date。如果 `today` 落 weekend / HK holiday → `effective_kickstart_date = next weekday + non-holiday`（見 producer-playbook.md §0 Kickstart Anchor）。Backward chain 推出嚟嘅 milestones 全部要 ≥ `effective_kickstart_date`，否則觸發 Step F。

**Step A — Anchor Final Output**
`final_output_date = client_deadline`（hard anchor，唔郁）。

**Step B — Backward tail（fixed-duration milestones 反推）**
1. `cs_subtitle_date = final_output - 1 wd`（Color/Sound/Subtitle）
2. 如有 VO Recording window：
   - `vo_window_latest_end = cs_subtitle_date - 1 wd`（即 final - 2 wd）
   - `vo_window_length = 2 wd`
   - `vo_window_start = vo_window_latest_end - 2 wd + 1 day`
   - `picture_lock_date = vo_window_start - 1 wd`
3. 冇 VO：`picture_lock_date = cs_subtitle_date - 1 wd`

**Step C — Forward minimum from Shoot anchor**（standard shoot+post only — pure-post 用獨立 sub-mode chains，由 `--mode` flag dispatch，唔行呢個 step）
由 Shoot date forward chain 出最少需要嘅 cut chain（用 standard MIN gap 3 wd 計）：
- `min_1st_cut = shoot + 5 wd`
- `min_fb_1 = min_1st_cut + 3 wd`
- 3 cuts: `min_picture_lock_3cut = min_1st_cut + (3+3+3+3+3) wd = min_1st_cut + 15 wd`
- 2 cuts: `min_picture_lock_2cut = min_1st_cut + (3+3+3) wd = min_1st_cut + 9 wd`

**Step D — Decide cut count（基於 available window，standard shoot+post only）**

`available_window = picture_lock_date - shoot_date`

| `available_window`（從 Step B 反推到 picture_lock 起算） | Decision |
|---|---|
| ≥ 20 wd | **3 cuts standard**——slack distribute 落 cut gaps（cap 4–5 wd per gap） |
| 14–19 wd | **2 cuts standard**（穩陣，slack 寬鬆）/ 或 **3 cuts compressed**（gap 3 wd MIN，feedback 1 wd）—— Mugi flag trade-off + 問用戶（見下） |
| 10–13 wd | **2 cuts compressed**（Shoot→1st Cut 4 wd，FB 1 wd，2nd Cut gap 3 wd）—— flag tight + 同 client 講明 feedback 收緊 |
| < 10 wd | 連 2-cut compressed 都頂唔順 → **Pattern J，escalate Sohling** |

> **Note — Compressed-Edge-Case Branch 仍 default 3-cut。** Step F 觸發 Compressed 嗰陣，cut count drop **唔係** first lever；先 squeeze cut gap + feedback time。Drop 落 2-cut **only when** Senior Approval Rule explicit trigger。連 3-cut compressed 都頂唔順 → 走 **Extreme-Squeeze Tier**（見下文 sub-section），由導演 call。

**Senior approval exception：** 用戶 / client 明講「2nd cut 之後要 senior approval / 走管理層 review，FB2 最少 X wd」 → 即使 window ≥ 20 wd 都行 **2 cuts**，FB2 攞到 X wd，剩餘 slack 落 1st cut → FB1 / FB1 → 2nd cut。

**3-cut compressed vs 2-cut full slack 嘅 trade-off：**
Window 14–19 wd 嗰下 Mugi 主動 flag，**唔好默默 silent decide**：
> 「依家 Shoot 到 final delivery 中間有 [N] working days。
> - 行 **3 cuts compressed**：每個 cut gap 3 wd MIN、feedback 1 wd。Iteration 多但 client feedback 時間少。
> - 行 **2 cuts**：cut gap 拎到 [M] wd、feedback 3 wd 寬鬆。Iteration 少但每輪夠時間。
>
> 你想點？」

**Step E — Distribute slack（cut-priority，per-mode caps）**

`slack = available_window - min_required_for_chosen_cut_count`

**Distribution 優先級（嚴格按次序 fill 到 cap）：**
1. **1st Cut（Shoot → 1st Cut）** — DOF post team 真實 production time，最緊要俾足
2. **2nd Cut（FB1 → 2nd Cut）**
3. **3rd Cut（FB2 → 3rd Cut）**
4. **FB1（1st Cut → FB1）**
5. **FB2（2nd Cut → FB2）**
6. **FB3（3rd Cut → FB3）**

**Per-mode caps（max gap = MIN + extra）：**

| Mode | Shoot→1st Cut | Cut→Cut（2nd / 3rd） | FB（1 / 2 / 3） |
|---|---|---|---|
| Standard | 5 + 3 = **8 wd** | 3 + 5 = **8 wd** | 3 + 2 = **5 wd** |
| Compressed | 4 + 2 = **6 wd** | 3 + 3 = **6 wd** | 1 + 2 = **3 wd** |
| Extreme（Compressed-Edge-Case 用）| 2 + 3 = **5 wd** | 2 + 3 = **5 wd** | 1 + 2 = **3 wd** |

**Algorithm：** 由 priority order 第 1 項開始，每個 slot 填到 cap，剩 slack 滾去下一個。所有 slot 填到 cap 仲有剩 → **留喺最後一個 cut gap**（最 conservative），**唔可以** pull Final Output 早。

**Danger flag — Cut duration ≤ 3 wd：**
任何一個 cut（1st / 2nd / 3rd）嘅 incoming gap（Shoot → 1st、FB1 → 2nd、FB2 → 3rd）≤ 3 wd 一律 flag 落 `cut_warnings` array。Mugi reply 必須照原樣 echo 出嚟，唔可以 silent compress。Threshold ≤ 3 wd 嘅理由：post team 真係頂唔順，呢個 level 要 director / producer review 條 cut 嘅 scope。

**點解 1st Cut first：** 1st Cut 係整條 post chain 最 foundational 嘅交付。1st Cut 嘅 production time 直接決定條片嘅 baseline quality（rough cut → music → pacing → first impression）。後面 cuts 主要係 iterate 1st Cut，1st Cut squeeze = 後面冇得追。Compressing feedback = client-facing trade-off，client 自己決定；compressing cut production = 直接 burn out post team。

**Step F — Past-milestone Detection（feasibility gate）**

行完 Step B + Step E 之後，逐個 backward-derived milestone（C/S、VO window start、Picture Lock、3rd/2nd/1st Cut、pre-pro chain：Confirm/Submit Style Frame、Confirm/Submit Graphics Ref、Script Lock、Submit Video Flow、Script Received）對住 `effective_kickstart_date` check：

```
IF any backward-derived milestone < effective_kickstart_date:
  → Timeline INFEASIBLE under standard logic
  → Trigger Compressed-Edge-Case Branch（見下面 sub-section）
ELSE:
  → Standard output，繼續 generate-timeline.md Step 4 enumerate
```

**❌ 唔可以**默默喺 past-milestone 行加 `[已過]` tag——backward-derived date 早過今日**唔等於**嗰個 milestone 已經完成。除非用戶 explicit override（見 producer-playbook.md §0 Kickstart Anchor），一律當未開始 → infeasibility。

---

## Compressed-Edge-Case Branch（Step F triggered）

當 Step F detect 到 past-milestone（backward chain 撞穿 kickstart）→ Standard logic 已經頂唔順，行呢個 branch。**比下面 Compression Rules 更激進**——pre-pro chain 縮短但仍 sequential、Style Frame 移後、cut count **仍 default 3-cut**（squeeze cut gap + feedback time，唔好 first lever drop cut count）、cut gap / feedback 壓到 minimum。

| 改動 | Standard | Compressed-Edge-Case |
|---|---|---|
| Shoot date | client-stated 或 backward-derived | **ASAP = effective_kickstart + 1–2 wd prep**（props / location confirm minimum） |
| Style Frame | Pre-shoot deliverable（Submit + Confirm Style Frame 喺 Shoot 前 confirm） | **並行 1st Cut**（夾喺 1st Cut 俾 client review，唔再 block shoot；接受 style 改返工 risk） |
| Pre-pro chain | Script → Submit Video Flow → Submit Graphics Ref → Script Lock → Confirm Graphics Ref sequential（standard gaps）| **Sequential with 1–2 wd minimum gap**（default **2 wd**，floor **1 wd**）。**唔係 zero-gap parallel**——收到 script 同日 submit video flow / graphics ref 唔 realistic。例：Mon (Script Received) → Wed (Submit Video Flow + Submit Graphics Ref) → Fri (Script Lock + Confirm Graphics Ref) → next Mon (Shoot) |
| Cut count | Step D 邏輯（≥20 wd = 3 / 14–19 = flag / 10–13 = 2 compressed） | **Default 3-cut**（squeeze cut gap + feedback time，唔好 first lever drop cut count）。1st Cut compressed min **2–3 wd**。**2-cut only when** Senior Approval Rule explicit trigger（用戶／client 明講 senior approval round 要乜時間）。連 3-cut compressed 都頂唔順 → 走 **Extreme-Squeeze Tier**（見下）|
| Slack distribution | Step E cut-gap-first（cap 4–5 wd） | Cut gap + feedback time 全部壓到 minimum；buffer 0–1 wd |

**Cut count rationale（點解 default 3-cut，drop cut 唔係 first lever）：**
- 1st cut = working-level flow alignment（draft，DOF post + director 對 cut）
- 2nd cut = senior approval round（client side 拎上去俾 senior review）
- 3rd cut = client final tweaks（99% project required）

Drop 3rd cut = 跳過 client final tweaks，去到 final delivery 風險高過 squeeze gap。Squeeze cut gap + feedback time 先係 first lever。

**Output 必須含 explicit ⚠️ warning（唔係 optional）：**

```
⚠️ Timeline INFEASIBLE under standard logic
Effective kickstart → client deadline = [N working days]
Standard pre-pro chain 需要 [M working days]，超出 available window。

以下 schedule 採用 Compressed-Edge-Case：
  - Shoot ASAP（[date]，effective_kickstart + [1–2] wd prep）
  - Style Frame 並行 1st Cut（唔再 pre-shoot confirm，接受 style 改返工 risk）
  - Pre-pro chain sequential 1–2 wd gap（default 2 wd / floor 1 wd）
  - Default 3-cut（1st cut compressed min 2–3 wd；cut gap + feedback 壓到 minimum）

Recommend client 二選一：
  (a) Negotiate deadline extension to [date]（standard logic 可行嘅 minimum）
  (b) Confirm aggressive schedule below + accept style frame 改返工 risk
```

**Style Frame scope rule：** Style Frame parallel-with-1st-cut **只准** Compressed-Edge-Case Branch 用。Standard timeline 仍然 pre-shoot confirm（避免 style 改返工 cost）。

---

## Extreme-Squeeze Tier（Compressed 仍頂唔順）

**Trigger：** Compressed-Edge-Case 嘅最 aggressive 配置（Default 3-cut + 1st cut min 2–3 wd + pre-pro sequential 1 wd floor + buffer 0 wd）**仍然撞 deadline**。例：CLP 純後期 case，total window 兩星期（包 storyboard），標準 + compressed 都做唔到。

**Mugi 嘅 behavior：唔自動 plan，唔自動 push calendar。** 呢類 case 變數太多（director availability、post bandwidth、條片複雜度、client feedback turnaround），唔係 Mugi standard rule book judge 到。Mugi 將 3 個 specific propositions surface 俾**導演**決定，等導演 call 完先 push calendar。

**Mugi 必出嘅 escalation message（template）：**

```
⚠️ Extreme tier — standard + Compressed-Edge-Case 都頂唔順呢個 deadline

Effective kickstart → client deadline = [N working days]
Compressed branch min（3-cut + 1 wd pre-pro gap + 1st cut 2 wd）需要 [M working days]，仲超 [M-N] wd。

呢個 case 變數太多，Mugi judge 唔到，建議交俾導演 call。
有以下 3 個方向可以 squeeze：

1. **壓縮 client feedback 時間** — pre-arrange senior viewing day（e.g. 同 client 約定下晝某時間做 senior review），feedback turnaround 由標準 1–3 wd 壓到 same-day / next morning
2. **同 client 傾轉數** — 真係要 3 rounds？2 rounds 得唔得？或者其他 hybrid 做法（e.g. 1st cut + senior approval combined）
3. **壓縮 1st cut 時間** — 由標準 2–3 wd → 1 day。視乎 [director] availability + post team bandwidth + 條片複雜度

@[director] 入嚟睇下:你想行邊個方向？決定咗我會跟住 push 上 calendar。
```

**Escalation target：導演（job director），唔係 Sohling。** 理由：Pattern J / Sohling escalation 處理 post saturation（calendar 撞）；Extreme-Squeeze 係 creative + production trade-off 決定（cut count / feedback turnaround / 1st cut squeeze），呢類 call 由導演做。

**Mugi role：** 提供 planning options，等導演決定，然後 push calendar。**唔可以**自己 force 一個 Compressed branch 出嚟當 final answer。

---

## Compression Rules（**only when explicitly triggered**）

**Default 計 timeline = standard。唔好預先同時計 compressed。** Compressed 數字得喺以下 trigger 滿足先行用。

**Post-production 嘅 fallback sequence（嚴格按次序試）：**
1. **Try 3-cut standard**（gap MIN 3 wd，slack distribute cut-gap-first cap 5 wd）
2. **Drop to 2-cut**（如 3-cut min 都頂唔順 available window）
3. **Compress edges**（用下面 Compressed minimums 表 — Shoot→1st Cut 4 wd / FB 1 wd 等）—— 只喺 2-cut standard 都頂唔順先試
4. **Pattern J，escalate Sohling**（連 2-cut compressed 都 miss final deadline）

⚠️ **永遠唔好** pull Final Output 早過 client deadline 嚟「fit」cut chain——drop cut / compress edge / escalate，三個之中揀一個。

Compressed 數字得喺以下 trigger 滿足先行用：

| Trigger | Compressed minimums |
|---------|---------------------|
| 用戶明確要求壓縮（「tight 啲」/「壓返一個禮拜」/「快啲交」）| 見下表 |
| Standard timeline 計完 miss final deadline | 見下表 |
| Pattern F / G / I 場景（graphics 量輕 / event / 加 cut）+ 用戶 confirm | 見下表 |

**Compressed minimums（淨喺 trigger fired 先用）：**

| Edge | Standard | Compressed min |
|------|----------|----------------|
| Script Received → Submit Video Flow | 5–6 wd | 3–4 wd |
| Submit Video Flow → Script Lock | 5 wd | 3 wd |
| Script Lock → Shoot | 7 wd | 3 wd |
| Submit Style Frame → Confirm Style Frame | 1–2 wd | 1 wd |
| Shoot → 1st Cut | 5 wd | 4 wd |
| 1st Cut → FB 1 | 3 wd | 1 wd |
| 2nd Cut → FB 2 | 3 wd | 1 wd |
| FB 2 → 3rd Cut | 3 wd | 2 wd |

**Single-Scenario Rule：** 一個 timeline request **只計一個 scenario**。先計 standard → 撞 deadline 至 fall back compressed → 仲撞至走 Pattern J（escalate Sohling）。**禁止同時 enumerate standard + compressed 兩個 Python script 對比**——係用 token + thinking time，唔係 producer judgment。

Compressed pre-pro total（reference only）：T0 → Shoot ≈ 9–10 wd (~2 週)。
