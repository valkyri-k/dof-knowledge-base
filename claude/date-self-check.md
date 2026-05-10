# Schedule Output Self-Check

> Extracted from CLAUDE.md on [[2026-05-10]] to reduce context-bloat warning.
> **Read this full file when**: 即將 output 任何含日期 table 嘅內容（schedule、timeline、calendar proposal）→ run 以下 self-check Python script 之後先寫 reply。
>
> Hard rules（絕對禁止 / 強制使用 / Scope table）仲喺 CLAUDE.md「Date, Weekday & Holiday Handling」section，呢度只放執行 code。

---

## Schedule output self-check（強制）

喺 output 任何有日期 table（schedule、timeline、calendar proposal）**之前**，必須 run Python self-check：

```python
from datetime import datetime

# 1. Verify 每一 row 嘅 Date ↔ Day 一致
for row in schedule:
    expected_day = datetime.strptime(row["date"], "%Y-%m-%d").strftime("%A")
    assert row["day"] == expected_day, f"Day mismatch at {row['date']}"

# 2. Verify 無 milestone 撞 HK public holiday 或 Sunday
import json
holiday_dates = set()
for year in {row["date"][:4] for row in schedule}:
    with open(f"/home/node/kb/context/holidays/hk-{year}.json") as f:
        holiday_dates.update(h["date"] for h in json.load(f)["holidays"])
for row in schedule:
    d = datetime.strptime(row["date"], "%Y-%m-%d")
    assert row["date"] not in holiday_dates, f"{row['date']} is HK holiday"
    assert d.weekday() != 6, f"{row['date']} is Sunday"  # 6 = Sunday
```

Fail → **唔好 output schedule，regenerate 或報告 Kary**。

---

## Holiday cache 維護

- 每年年底更新下一年嘅 JSON（`hk-2026.json` → `hk-2027.json`）
- Source：gov.hk 官方 ICS feed / HTML page
- 格式見 `context/holidays/hk-YYYY.json` 內 schema
