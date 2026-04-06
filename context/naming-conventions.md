# DOF Naming Conventions

## Job Number 格式

```
J26001
```

- `J` = Job prefix
- `26` = 年份（2026）
- `001` = 當年流水號（三位數）

**例子：** J26001、J26015、J26051

---

## Quotation Number 格式

```
Q26051
Q26051R1   ← 第一次修訂
Q26051R2   ← 第二次修訂
```

- 後綴 `R1`、`R2` 代表 revision 版本

---

## Project Shorthand（簡稱）

每個 project 喺**開 job 時定好 shorthand**，之後所有系統（Calendar、Discord、Drive）統一使用。

**命名原則：**
- 用 Client name + project 描述，保持簡短
- 避免只用 job number（Calendar view 太細，job number 讀唔到意思）
- 由導演或 Kary 喺開 job 時確認

**例子：**
- `HSUHK Student` — HSUHK 學生向宣傳片
- `EMSD Railway Chris` — EMSD 鐵路 Chris 項目
- `CLP TK CEO Msg` — 中電 Towngas CEO Message

---

## Google Calendar Event 命名規則

### Title 格式
```
[Milestone] - [Project Shorthand]
```

**例子：**
```
1st Cut - HSUHK Student
Client FB 1 - EMSD Railway Chris
Final Output - CLP TK CEO Msg
Shoot - HKBU Orientation
Picture Lock - MTR Safety
```

**原則：**
- Milestone 名稱用標準 set（見下方）
- Project Shorthand 跟開 job 時定好的版本
- 唔把 job number 放 title（Calendar view 細，影響可讀性）

### Description 格式
```
J26016
Director: Kary
[其他備註，如有]
```

- Job number 放 Description（Google Calendar search 可以搵到 description 內容）
- Director 姓名

---

## 標準 Milestone 名稱

| Milestone | 用途 |
|-----------|------|
| `Shoot` | 拍攝日 |
| `1st Cut` | 第一版剪接交客 |
| `Client FB 1` | 客戶第一輪 Feedback deadline |
| `2nd Cut` | 第二版剪接交客 |
| `Client FB 2` | 客戶第二輪 Feedback deadline |
| `3rd Cut` | 第三版剪接交客 |
| `Client FB 3` | 客戶第三輪 Feedback deadline |
| `Picture Lock` | 畫面鎖定，之後唔改剪接 |
| `VO Recording` | 旁白錄音（如有） |
| `Final Output` | 最終成品交付 |

**重要：** 統一用呢套名稱。唔接受自由發揮（e.g. `1st cut EMSD`、`Feedback on 1st cut`）——會令 Calendar 亂、搵唔到。

---

## TBC Events

未確定日期嘅 milestone 可以先放 TBC（大概日期）並 mark 喺 event title 或 description 入面。例如：
```
1st Cut - HSUHK Student (TBC)
```

當日期確認後，remove `(TBC)` 並更新正確日期。
