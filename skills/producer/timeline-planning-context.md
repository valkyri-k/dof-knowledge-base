# Timeline Planning Considerations — Job-Level Decision Framework

> Audience: Mugi (producer skill) — load when user hands off a new job for timeline planning.
> Purpose: per-job decision framework. Decide chain mode + DOF-made deliverable + dimension to confirm before generating timeline.
> Companion: `producer-playbook.md`（per-step instructions）+ `calendar-and-timeline-philosophy`（per-step reasoning, vault-side）.

---

## What

呢份 doc 係 **job-level decision framework**——當一個 job 嚟到，要排 timeline 嘅時候，要 decide 咩 chain mode、咩 DOF-made deliverable、咩 dimension 要 confirm 先動手。

| Doc | Layer | 例子 |
|---|---|---|
| `calendar-and-timeline-philosophy`（vault） | **Per-step reasoning** — 每條 timeline rule 點解係呢個 wd count、點解要呢個 sequence | 「Submit Video Flow 點解係 5–6 wd？」 |
| `timeline-planning-context.md`（呢份） | **Per-job decision framework** — 一個 job 嚟到要 decide 咩 mode / deliverable / dimension | 「呢個 job 應該揀 pure-post 定 standard？要唔要做 storyboard？」 |
| `producer-playbook.md` | **Per-step execution** — Mugi 點問、點 detect、點 reply | 「Step 3 Q5 點問 DOF pre-pro deliverable」 |

---

## Why

排 timeline 嘅錯通常唔係 wd count 計錯，而係 **case classification 揀錯** 或者 **dimension 漏問**。常見 fail mode：

- Chain script 嘅 backward math 啱，但 effective_kickstart 攞錯（用 client 嘅 wishful date 而唔係 real ready date）
- Storyboard / video flow 排咗喺 script 之前（real-world ordering violation）
- Final delivery hardness 冇問清楚 → 拖 final 定 squeeze feedback 揀錯
- DOF-made pre-pro deliverable（script / video flow / storyboard）冇 model 入 chain，timeline 表面上 hit deadline 但實際 invisible 段落 burn 緊時間

呢啲全部係 **decision-layer error**，唔係 calculation error。Calculation 啱晒，answer 都會錯。

---

## 1. Job Classification（揀啱 chain mode）

每個 job 落手排 timeline 之前要先 classify。Classification 決定 chain mode + 預期 deliverable matrix。

### Mode matrix

| Mode | Production scope | 典型例子 | DOF-made pre-pro deliverable |
|---|---|---|---|
| **Pure post** | 純後期，冇拍攝 | Re-edit existing footage、event highlight from raw footage、subtitle/translation only | 通常無（client 已俾 brief / footage） |
| **Standard shoot+post** | 拍攝 + 後期 | Corporate video, talking head, KOL content, product video | Script（如 DOF 寫）+ Video Flow（通常）|
| **Animation (full)** | Full animation production | 2D / motion graphics 主導嘅 explainer | Script（如 DOF 寫）+ Storyboard（必須） |
| **Mixed (live+animation)** | Hybrid live action + animation | Hybrid corporate, animated intro + interview | Script + Storyboard 或 Video Flow（睇主導 medium） |
| **Edit-only** | Re-edit + minor adjustment, 純剪接工作 | 客俾 picture lock 想加 subtitle / re-version / 再剪 | 無（brief 已齊） |
| **Event highlight** | Event 拍攝後快速剪 highlight | Conference recap, gala highlight | 無（唔需要詳細 break down，pace 太快） |

### 點分？

睇兩條問題：

1. **要唔要拍攝？**
   - 要 → Standard shoot+post / Mixed / Animation（如 hybrid）
   - 唔要 → Pure post / Edit-only / Animation（如純動畫無拍攝）

2. **點 align visual content 同 client？**
   - 用 storyboard（charged item、tender 列明、或 full animation 必須） → 揀 Animation 類，or Standard 加 storyboard flag
   - 用 video flow（corporate shoot 嘅 default align tool） → Standard shoot+post
   - 唔需要 align（brief 已齊 / event 太 fast-paced） → Edit-only / Event highlight / Pure post

---

## 2. Pre-Timeline-Planning Checklist（要 confirm 嘅 dimension）

Mode 揀好之後，落手排之前要 confirm 嘅 dimension。**呢個 list 唔係建議，係 mandatory pre-flight check**——任何一個 dimension 漏咗，timeline 出嚟都會有 systemic bug。

| Dimension | Question to ask | 影響 |
|---|---|---|
| **Materials ready date** | Footage / graphics raw assets 幾時齊？仲有 pending 嗎？ | Effective kickstart 嘅 component |
| **Final delivery hardness** | Final Output 係 hard event-driven deadline（e.g. launch day, gala）定 soft 內部 target？ | Compression lever 揀法（hard = lock final + squeeze feedback；soft = first lever 係 propose final slip） |
| **DOF-made deliverable scope** | Script 邊個寫（client / DOF internal / DOF outsourced）？要唔要 storyboard / video flow？ | Effective kickstart 計法 + chain 加新 stage（見 §3） |
| **Storyboard charged?** | 如果要 storyboard，client 同意比錢？tender 列明？ | 如冇付費 confirm，唔可以 default 加 storyboard stage |
| **Compression appetite** | Standard timeline 定 compressed？compression 接受到咩 trade-off？ | Pre-step A flag（mode_args, senior approval compression） |
| **Holiday / blocked dates** | Window 內有冇 PH / 客 unavailable / DOF 內部 block？ | Working day calendar adjustment |
| **VO scope** | 有冇 VO recording？AI VO / 純配樂 / 對白？ | VO Recording milestone 出唔出 |
| **Cut count** | 2 cut 定 3 cut？（Option B = tight schedule 接受 2 cut） | 3rd Cut + FB 3 出唔出 |

**Mugi 嘅 default**：以上任何一個 dimension 用戶 hand off 入面冇 explicit 講 → mandatory ask，唔可以 silent default。

---

## 3. DOF-Made Pre-Pro Deliverables（chain 點 model）

### 三種 deliverable

DOF 喺 pre-pro 階段可能要做嘅嘢，每個都係 **DOF 整 → submit 俾 client → client confirm** 嘅 cycle：

| Deliverable | 出現條件 | DOF write days (range / default) | Client confirm wd (range / default) |
|---|---|---|---|
| **Script (DOF-written)** | client 唔提供 script，DOF internal / 外判寫 | Internal 2–3 wd / 外判 2–4 wd（外國 writer rush 唔到）；**default 3 wd** | 2–4 wd（要老闆 approve）；**default 3 wd** |
| **Video Flow** | Standard shoot+post 嘅 default align tool（無 storyboard 時） | 1–3 wd / **default 3 wd** | 1–3 wd / **default 2 wd** |
| **Storyboard** | Client 加錢 / tender 列明 / full animation 必須 | 3–6 wd / **default 5 wd**（mixed extreme case 可低至 1–2 wd；full animation min 3 wd） | 1–3 wd / **default 2 wd** |

### Mutual exclusion rule

**Video Flow 同 Storyboard 唔會兩個都做晒**——係 align tool 嘅 alternative，唔係 stack：

- **Animation**：淨係做 Storyboard，唔做 Video Flow（storyboard 已 cover align 需求）
- **Edit-only / Re-edit / Event highlight**：兩者都唔會出現（client brief 已齊，唔需要再 align）
- **Standard shoot+post**：通常 Video Flow（除非 client 加錢要 Storyboard）

### Sequencing rule（real-world prerequisite）

```
client brief
  ↓
[Script (DOF write + client confirm)]    ← if --script-source != client
  ↓
[Video Flow OR Storyboard (DOF write + client confirm)]    ← if applicable, mutually exclusive
  ↓
effective_kickstart
  ↓
... 原本 chain 接落去（Style Frame → Shoot → Post → Final Delivery）
```

**Key reasoning：**

1. **Script 永遠最先**——Video Flow 同 Storyboard 都 based on script。冇 script，後兩者起唔到。

2. **Video Flow / Storyboard 跟 script 之後**——script confirm 之後先做。如果 chain script 將 storyboard 排喺 script confirm 之前，呢個係 **real-world ordering violation**（Pattern K case）。

3. **Effective kickstart = max(materials_ready_date, last_pre_pro_confirm_date)**——任何一個 prerequisite 未 ready，就唔可以開正式 production。Materials 齊咗但 storyboard 未 confirm 都係 zero-progress。

### CLI surface

`timeline_backward.py` 提供以下 flags model 呢個 chain：

- `--dof-pre-pro-deliverables script,video-flow`（或 `script,storyboard`，逗號分隔）
- `--script-write-days N` / `--script-confirm-wd N`（defaults 3 / 3）
- `--video-flow-write-days N` / `--video-flow-confirm-wd N`（defaults 3 / 2）
- `--storyboard-write-days N` / `--storyboard-confirm-wd N`（defaults 5 / 2）

Chain script 會自動：
- 加 `DOF X Submit` + `Client X Confirm` milestones（每個 deliverable 一對）
- Enforce canonical ordering（script → video-flow/storyboard）+ mutual exclusion（video-flow XOR storyboard）
- 將 effective_kickstart push 去 `max(today push to wd, last pre-pro confirm date)`

### Failure mode（if NOT using these flags）

歷史上 chain script 假設 effective_kickstart = materials_ready_date。當 DOF 寫 script，呢個假設破裂：

- Mugi 用 client 講嘅 kickstart 做 effective_kickstart
- Storyboard 倒推到 kickstart 前幾日
- 但嗰幾日連 script draft 都未出，storyboard 起唔到
- Chain math 啱，real world 唔可能執行

Mandatory ask 規定咗都唔夠保險——所以而家 chain script native model `--dof-pre-pro-deliverables`，effective_kickstart 自動由 last pre-pro confirm date 決定，唔再靠 Mugi 手動調 `--today`。

---

## 4. Compression Levers + Hardness Implication

Final delivery hardness 決定 compression lever priority。

### Hard event-driven deadline

Final Output = absolute lock（launch day / gala / event date 唔可以 push）。

**Lever priority：**
1. Squeeze internal review windows（senior approval `--senior-approval-fb2-wd N`，N = 1–2 wd）
2. Compress feedback turnaround（要 client pre-arrange）
3. Cut scope（drop 3rd cut, drop optional milestone）
4. Escalate Sohling 加 post resource

**Mandatory user-facing ask：** 如果 senior approval 壓到 < 5 wd，**必須** explicit 同 user 講要 client pre-arrange 老闆 approval 同 client feedback turnaround。唔可以 silent forward。（已 codify 入 producer-playbook Pattern L）

### Soft internal target

Final Output 可以 push 幾日。

**Lever priority：**
1. **Propose final delivery slip first**（保留 standard review windows）
2. Squeeze internal review（only if user reject slip）
3. Cut scope

（已 codify 入 producer-playbook Final Delivery Hardness sub-section）

---

## 5. Common Pitfalls（observed bugs）

| Pitfall | Trigger | Fix |
|---|---|---|
| **Effective kickstart 攞錯** | 用 client 講嘅 kickstart 做 anchor，唔 account 真實 prerequisite ready date | §2 mandatory check：materials ready date + DOF deliverable scope |
| **Storyboard / video flow before script** | Chain 假設 effective_kickstart = materials ready，DOF 寫 script 嘅情況下倒推到 script 仲未做就要交 storyboard | §3 native chain modelling（`--dof-pre-pro-deliverables`） |
| **Silent compression of senior approval** | Hard deadline + 自動壓 senior approval window，但 reply 入面寫「5 wd 唔 compress 得」（self-contradict） | §4 mandatory user-facing ask + playbook Pattern L |
| **Hardness 冇問** | Reply 直接出 timeline，未 confirm hardness | §2 mandatory dimension + playbook Q6 |
| **Silent default cut count / VO scope** | 用戶冇明講就 default 3 cut + VO，未 confirm 客側 scope | §2 mandatory check + playbook §3 Step 3 |
| **將 contradiction hide 入 ⚠️ flags** | Detect 到 ordering violation 但放入 flags 一條，繼續 propose timeline | Pattern K：stop generation, surface user-facing 3 options |

---

## Cross-references

- **Per-step execution**: `producer-playbook.md`
- **Per-step reasoning（vault-side）**: `calendar-and-timeline-philosophy`
- **Chain script**: `scripts/timeline_backward.py`
