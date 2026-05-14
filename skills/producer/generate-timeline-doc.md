# Generate Timeline Doc

> **用途：** Phase 3 — Push Calendar 完成後，generate Timeline / Callsheet / Video_Flow document 嘅做法（Table Row Deletion two-phase pattern、Naming、Output Location、Adding New Document Types）。
> **Caller：** `skills/producer/producer-playbook.md` §0 Phase 3
> **Pair with：** `skills/producer/calendar-ops.md`（Calendar event write 唔同 doc write）

---

## Table Row Deletion

Optional milestone 唔需要時，**正確做法係 delete 嗰行，唔係 mark「—」或「skipped」**。

**Two-Phase Pattern（必須跟從）：**

**Phase 1：寫入所有 data（唔 delete）**
用 `BatchUpdateDocument` fill 所有 cells / placeholders（包括最終要 delete 嗰行）。**Phase 1 唔好 delete 任何 row**——delete 會令 index shift，破壞後續 write 操作。

**Phase 2：Delete optional rows（所有 write 完成後先做）**
**Phase 2 內部仍然要 bottom-up delete**：由下面先 delete（rowIndex 較大嘅先），上面一行嘅 index 唔受影響。

```python
# Phase 1: 寫入晒所有 data
docs_service.documents().batchUpdate(
    documentId=copy_id,
    body={"requests": [...all_write_requests...]}
).execute()

# Phase 2: Delete optional rows（bottom-up）
docs_service.documents().batchUpdate(
    documentId=copy_id,
    body={"requests": [
        # 由下面先 delete（rowIndex 較大嘅先）
        {"deleteTableRow": {"tableCellLocation": {
            "tableStartLocation": {"index": TABLE_START_INDEX},
            "rowIndex": 14, "columnIndex": 0
        }}},
        {"deleteTableRow": {"tableCellLocation": {
            "tableStartLocation": {"index": TABLE_START_INDEX},
            "rowIndex": 13, "columnIndex": 0
        }}},
    ]}
).execute()
```

**Common delete scenarios：**
| 情況 | 要 delete 嘅 rows |
|------|-----------------|
| VO 唔錄 / AI VO | VO Recording row |
| Option B（2 cut 夠） | 3rd Cut + Client FB 3 |
| 完全冇 graphics（純拍攝） | Submit Graphics Ref + Confirm Graphics Ref + Submit Style Frame + Confirm Style Frame |
| 有 graphics 但冇 motion（e.g. 簡單 lower third） | Submit Style Frame + Confirm Style Frame（保留 Graphics Ref） |
| Pure post job（冇拍攝） | Script Received + Submit Video Flow + Submit Graphics Ref + Script Lock + Confirm Graphics Ref + Shooting |

**⚠️ 唔好 delete 嘅 row：**
- **Color/Sound/Subtitle**——呢個係 Kary 特登放入 template 俾客睇嘅 transparency row，doc 一定要保留，**就算用戶話「俾我簡潔啲」都唔好 delete 呢行**

---

## Document Naming + Output Location

**命名規則：**
```
[DocType]_[Job Number]_[Project Title]_[YYYY-MM-DD]_[version optional]
```
- `DocType`：`Timeline` / `Callsheet` / `Video_Flow`（同 template prefix 一致）
- `Job Number`：`J26015` 格式
- `Project Title`：project shorthand（e.g. `HSUHK Student`）
- `YYYY-MM-DD`：generation date（今日）
- `version`：optional，只係修訂版本先加（`r2`、`r3`）

**Output Location：全部 generated documents 放 dof.internal Drive root。**
唔自動 move 去 project folder——命名規則已包含 job number + title + date，Drive search 一定揾到。

**Template Field Semantics：**
| Field | 點 fill | 例子 ✅ | 反例 ❌ |
|-------|---------|--------|---------|
| Director | DOF director 名——由 channel context（`job-list.md` Director column）自動拎；該 column 冇 value 先留空 | `Kary` / `Benjy` | 留空（job-list.md 有 value 但冇填入 doc） |
| Job Number | J-number | `J26015` | `26015` |
| Project Name | Project shorthand | `HSUHK Student` | `Recruitment Video` |

---

## Adding New Document Types

當需要支援新 document type（e.g. callsheet）：

1. **Kary 喺 `Templates` folder drop 一個 template file**，命名 `[DocType]_Template`（e.g. `Callsheet_Template`）
2. **無需 redeploy、無需加 env var、無需改 CLAUDE.md**——Mugi 下次收到 request 自動 by-name lookup 揾到
3. 唯一例外：如果新文件類型需要特殊 placeholder mapping 邏輯，就要喺呢份 playbook 加 sub-section 講嗰個 type 嘅 generation 流程
