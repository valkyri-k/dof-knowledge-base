# Director Playbook — Video Shot Breakdown

> **Mugi 收到「拆 shot / 分鏡 / shot breakdown / breakdown 條片」類 request（連 URL），必須先 read 呢份 file 由頭到尾一次，然後嚴格按 phase flow 做。**
>
> 呢份 playbook 係 **orchestrator**：所有 download / detect / extract / render / upload 嘅 heavy-lifting 已經寫死喺 top-level `scripts/breakdown_*.py`，Mugi 只負責 (1) 用 Bash CLI invoke script、(2) 中間用 native vision 讀 strip 填 10 欄、(3) parse JSON 出人類可讀 reply。中間 vision step 係**唯一**需要 Mugi reasoning 嘅部分。

team member 喺 Discord 丟一條**片 URL**（YouTube 或 Google Drive）→ Mugi 自動拆 shot、抽 trajectory strip、逐 shot 填 breakdown 欄、生成內嵌縮圖嘅 Excel 分鏡表、upload 去一個 per-job Drive folder、返條 share link。

= [[016-shotnest]] 本機 power-user 工具嘅後半段搬上 Mugi，等成隊 team 喺 Discord self-serve，唔使 Kary 本機跑。

---

> ## 🔒 NO-FALLBACK HARD RULES（違反 = REWRITE，係 contract，唔係 best practice）
>
> 1. **INVOKE SCRIPT，唔好 INLINE PYTHON / 自組 pipeline**：download、shot detection、frame extract、strip 砌圖、xlsx 砌、Drive folder + upload —— **全部**由 `scripts/breakdown_extract.py` + `scripts/breakdown_render.py` 做。Mugi **唔可以**自己 inline 寫 yt-dlp / scenedetect / ffmpeg / openpyxl / Drive API code，**唔可以**自組一條替代 pipeline。Script crash → surface error 俾 user，**唔好** fallback 落手寫版本。
> 2. **禁止用 CLOUD MCP**：唔可以用任何 `gdrive_*` / `gcal_*` / claude.ai 嘅 "Google Drive" / Gmail / Calendar MCP tool。所有 Drive I/O 行 `breakdown_gdrive.py`（dof.internal refresh-token OAuth）。理由見 [[reference_cloud_mcp_invisibility]] —— cloud MCP 會用 `karyto.dof@gmail.com` 身份，唔係 `dof.internal@gmail.com`。
> 3. **STRIP-NOT-VIDEO（anti-hallucination 核心）**：Mugi **冇睇過條片**。Mugi 只睇到 `breakdown_extract.py` 抽出嚟嘅 still trajectory strip（每 shot 一張橫條，左→右 = 時間）。填欄只可以描述 strip 上面**實際睇到嘅物理結果**，**唔可以**估 strip 之間發生咩、唔可以估意圖、唔可以當睇咗成段 video。temporal 欄（motion / transition）只可以由 strip 內 frame 之間嘅變化 infer，infer 唔到就寫 `uncertain` 唔好作。
> 4. **JSON 唔可以 ECHO 落 REPLY**：script stdout 係 1 行 JSON，Mugi 內部 parse；reply 只列人類可讀嘅 shot 數 / folder link / xlsx link / warning。**唔好 dump JSON 俾 user 睇。**
> 5. **CLEANUP 喺 RENDER 成功之後先做**：`breakdown_extract.py` 同 `breakdown_render.py` **都唔會**自己清 work dir（render 要 upload strips，extract 之後 vision step 要讀 strips）。work dir 只可以喺 Phase C upload 成功（`uploaded:true` + folder link 返到）**之後**先由 playbook `rm -rf` 清。render 未成功就清 = 災難。

---

## 0. Workflow Phases（開工前必讀）

拆 4 個 phase，每個 phase 有 gate。**唔 auto-proceed**——除咗 Phase A→B（同一 request 內自然連住做，唔需要 user 再 confirm）。Gate 主要喺最尾 cleanup 前 surface 結果。

ENV：`ZEABUR exec` 入 container 跑；script 喺 `/home/node/kb/scripts/`。container `cwd` 入到 `/home/node/kb` 先 invoke，等 `from breakdown_gdrive import ...` 嘅 sibling import work。

---

### Phase A — Extract（download → detect → strip）

**Trigger：** user 丟片 URL + 講「拆 shot / breakdown / 分鏡」。

**先做 auto-detect echo**（hard rule）：reply 第一句先 surface「收到，breakdown 緊 [URL]，detection sensitivity = normal（threshold 18），跑緊 extract…」，等 user 一眼睇到 input 啱。

**Invoke：**
```bash
cd /home/node/kb && python3 scripts/breakdown_extract.py "<URL>" \
  [-s coarse|normal|fine|max] [--source auto|youtube|drive] [--work-dir /tmp/bd_<jobtag>]
```
- 預設 `-s normal`（threshold 18）。User 嫌 shot 拆得太碎 → `coarse`（27）；嫌 merge 太多 shot → `fine`（10）/`max`（5）。
- `--source auto` 識別 youtube vs drive；識別唔到（短 link / 自訂 domain）先明確 `--source`。
- 揀一個固定 `--work-dir`（e.g. `/tmp/bd_<jobtag>`），因為 Phase C cleanup 要知條路徑。

**Parse output：** 1 行 JSON manifest = `{status, source{title,fps}, detection{n_shots,n_raw,phash_merge}, work_dir, manifest_path, shots[{shot,start_tc,end_tc,duration_sec,strip}]}`。

**Self-check（mental，pass 唔出聲）：**
- `status:"error"` → surface error，停。常見：`yt-dlp` 私片 / Drive file 未 share 俾 `dof.internal@gmail.com`。
- `detection.phash_merge:false` → imagehash 未裝（rebuild 未 land）→ reply 加一句 warning：「⚠️ 用緊 raw scenedetect boundaries，同一 shot 可能拆成幾段，quality 會差啲。」
- `n_shots` 異常（1 條 = 可能單 shot 片或 detect 唔到 cut；過多 = sensitivity 太敏）→ surface，問 user 要唔要換 sensitivity 重跑。

**Gate：** 冇 hard gate；直接落 Phase B（同一 request 連住做）。但若 `n_shots` 明顯唔合理，先問 user 換 sensitivity 至續。

---

### Phase B — Vision fill（Mugi 讀 strip 填 10 欄）⭐ 唯一 reasoning step

對 manifest `shots[]` 每一條，用 **native vision 讀 `shot["strip"]` 個 jpg**（Read tool 直接讀 strip 路徑），填以下 10 欄。**只描述 strip 睇到嘅嘢**（NO-FALLBACK Rule 3）。

#### Schema v8（audio cut = 10 欄）欄定義

| 欄 | rows.json key | 定義 |
|---|---|---|
| Shot # | —（manifest） | shot 序號 |
| Timecode(s) | —（manifest） | start → end + duration |
| Subject | `subject` | 極簡短名詞 indexing（e.g. `Older MJ`、`Four players`）。確保 character continuity。|
| Live Action Description | `live_action` | 具體物理動作 + 空間關係 + 走位。**必須明確邊個 subject 做緊乜**。嚴格照 strip 所見，**唔可以憑空想像動作結果**（入波定炒粉，照實寫；睇唔到結果寫 `result not visible in strip`）。|
| Framing, Angle & Motion | `framing` | 由下面 vocab 揀，結合三元素：`<景別> + <角度> + <運動>`（e.g. `WS + Low Angle + Dolly-in`）。Motion 只可由 strip 內 frame 變化 infer；infer 唔到寫 `Static (motion uncertain)`。|
| Editing effects | `editing` | 由 13-effect vocab 揀；冇 → `none`。strip 上睇唔到 post effect 就 `none`，唔好估。|
| VFX & Behavior | `vfx` | 特效名 + 動態描述（e.g. `Athletic Light Trails: 藍白發光線跟住球員勾出弧線`）；冇 → `none`。|
| MG, Text & Animation | `mg_text` | graphic / text 設計 + 出場動畫；冇 → `none`。|
| Transition out | `transition` | cut type + transition effect（由 cut-type vocab 揀）；睇唔到下一 shot 點接 → `Straight Cut (assumed)`。|
| Kary's Note | `note` | **AI 預設留空 `""`**，留俾 Kary 人手填。|

#### Distilled controlled vocabulary（揀詞必須喺呢度揀，唔好自創）

完整字典 = [[video-breakdown-vocabulary]]；以下係 paste-ready distilled set：

**景別 Framing**：ECU · CU · MCU · MS · Cowboy Shot · WS/Full · EWS · Two-Shot · Profile
**角度 Angle**：Eye-level · Low Angle · High Angle · Bird's Eye/Top-down · Worm's Eye · Dutch/Canted · OTS · POV
**運動 Motion**：Static · Pan · Whip Pan · Tilt · Push-in/Dolly-in · Pull-out/Dolly-out · Tracking/Trucking · Pedestal/Boom · Orbit/Arc · Crane/Swoop · Handheld · Steadicam/Gimbal · Zoom · Dolly Zoom(Zolly)
**速度 Speed（如適用，併入 Editing 或 Live Action）**：Speed Ramp · Speed Ramp into Slow-Motion · Slow-Motion · Time-lapse
**13 Editing effects**：1 Speed Ramp · 2 Slow-Motion · 3 Camera Shake/Vibration · 4 Digital Zoom Punch · 5 Frame Rotation · 6 Mirror/Symmetry · 7 White Bloom Flash · 8 Whip Pan · 9 Multi-Exposure Clone/Stroboscopic · 10 Zoom Pump · 11 Focus Pull/Rack Focus · 12 Motion Blur as Transition · 13 Lens Flare
**Cut types / Transition out**：Straight Cut · Match Cut · Action Cut · Jump Cut · L-cut/J-cut · Hidden/Invisible Cut · Fade/Crossfade

**Token discipline：** 唔好喺 reply echo 逐 shot 填咩；vision fill 係內部 step。砌好 `rows.json`（array，每 shot 一 object）寫入 work dir（e.g. `<work_dir>/rows.json`）就算，準備餵 Phase C。

**Gate：** 冇 gate；直接落 Phase C。

---

### Phase C — Render + Upload（xlsx + per-job Drive folder）

**Invoke：**
```bash
cd /home/node/kb && python3 scripts/breakdown_render.py \
  --manifest "<work_dir>/manifest.json" \
  --rows "<work_dir>/rows.json" \
  [--title "<片名>"] [--folder-name "<片名>"] [--parent <override-folder-id>]
```
- 唔加 `--no-upload` = 預設 create per-job folder + upload。`--parent` 唔指定 → upload 落 `GOOGLE_DRIVE_DOCGEN_FOLDER_ID`。
- script 自動：砌內嵌縮圖 xlsx → `create_folder(<片名>)` → upload xlsx + **全部 strips** + `manifest.json` 入 folder → 返 links。

**Parse output：** `{status, xlsx_path, n_shots, n_rows_filled, uploaded:true, folder{id,link}, xlsx{id,link}, uploaded_files[]}`。

**Self-check：** `status:"error"` 或 `uploaded:false` → surface error，**唔好清 work dir**，停。常見：openpyxl 未裝（rebuild 未 land）/ Drive quota。

**Reply（人類可讀，唔 dump JSON）：**
> ✅ Breakdown 搞掂 —— [N] 個 shot
> 📁 Folder（xlsx + 全部 contact sheet + manifest）：<folder link>
> 📊 Excel 分鏡表：<xlsx link>
> （folder 入面有埋 raw strip，要重 render / 微調 sensitivity 隨時嗌我）

**Gate：** reply 完，等 user 反應（OK / 要重拆 / 換 sensitivity）。

---

### Phase D — Cleanup（render 成功之後先做）

**只在** Phase C `uploaded:true` + folder link 返到之後：
```bash
rm -rf "<work_dir>"
```
清走 container 上嘅 download + frames + strips + embed tmp。**render 未成功 / error → skip cleanup**（保留 work dir 俾 debug / 重跑）。

---

### Anti-patterns（嚴格禁止）

- ❌ Inline 寫 yt-dlp / scenedetect / ffmpeg / openpyxl / Drive API（永遠 invoke deployed script — NO-FALLBACK Rule 1）
- ❌ Script crash 就落手寫一個替代版（surface error，停）
- ❌ 用 cloud MCP（gdrive / gcal / claude.ai Google Drive）做 Drive I/O（Rule 2）
- ❌ 填欄時當睇咗成段片 / 估 strip 之間發生咩 / 估動作結果（Rule 3 — strip-not-video）
- ❌ Framing / Editing / Cut 自創詞（必須喺 embedded vocab 揀）
- ❌ Dump script JSON 落 reply（user 睇 link + shot 數，唔睇 JSON — Rule 4）
- ❌ render 未 `uploaded:true` 就 `rm -rf` work dir（Rule 5 — 災難）
- ❌ `Kary's Note` 欄 AI 填嘢（永遠留空俾人手）
- ❌ phash_merge:false 唔 surface warning（quality 會差，要話俾 user 知）
- ❌ 為咗對比 sensitivity 一次過跑兩次 extract（先用 normal，user 嫌先換）

---

## Out of Scope（v1）

- Audio 欄（Speech / Audio Effects）→ phase 2 加 whisper（v1 已 cut，10 欄）
- Word doc → phase 2（v1 = Excel only）
- Local file upload（**只收 URL** — YouTube / Drive）
- Shotnest 本機版改動（凍結）

## Related

- Feature spec：`projects/007-agent-mugi/backlog/features/video-shot-breakdown.md`（vault）
- Schema：[[schema-v8]] · Vocab：[[video-breakdown-vocabulary]]
- Source idea：[[dreamlin76-codex-shot-breakdown-word-excel]]
- Scripts：`scripts/breakdown_extract.py`（Phase A）· `scripts/breakdown_render.py`（Phase C）· `scripts/breakdown_gdrive.py`（Drive I/O）
