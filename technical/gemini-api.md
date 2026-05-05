# Gemini API — Credentials + Boilerplate

> 呢份 file 存放 Gemini API（Vision、text generation）嘅 credentials 用法同 Python boilerplate。
> Mugi 需要 call Gemini 時 read 呢度攞正確嘅 code pattern。

---

## Credentials

API key 存放喺環境變數 `GEMINI_API_KEY`（Zeabur env var，已 provisioned）。

⚠️ **唔好 hardcode API key 入 script。** 永遠用 `os.environ["GEMINI_API_KEY"]`。

---

## Install

```bash
pip install google-genai pillow
```

> ⚠️ **舊 package `google-generativeai` 已 deprecated，唔再更新。** 永遠用 `google-genai`（新 SDK）。

`pillow` 用嚟 load image（Vision use case）。純 text generation 唔需要。

---

## Vision Boilerplate（image → structured JSON）

呢個 pattern 適用：OCR、screenshot 解析、image content extraction。

```python
import os
import json
from google import genai
from google.genai import types
import PIL.Image

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

img = PIL.Image.open("/path/to/image.png")

prompt = """
[describe what to extract; specify JSON schema in prompt]

Return JSON only, no prose. If a field is unclear, use empty string or empty list.

Example:
{"field_a": "...", "field_b": [...]}
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[img, prompt],
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.1,
    ),
)
data = json.loads(response.text)
```

### Model choice
- **`gemini-2.5-flash`** — **DEFAULT** for OCR / structured extraction（fast、cheap、JSON mode 支援好）
- `gemini-2.5-pro` — escalate 用：2.5-flash quality 唔夠（e.g. 手寫太花、layout 太複雜、reasoning 唔夠深）
- ⚠️ **`gemini-2.0-flash` 已 sunset** — 官方 2026-06-01 停用，`gemini-2.0-flash-001` 已 404 NOT_FOUND。新 code 一律用 2.5-flash

### Temperature
- `0.1` for structured extraction（OCR、JSON output）
- 唔好用 default `1.0`，會增加 hallucination risk

### JSON mode
`response_mime_type="application/json"` — 強制 model output 純 JSON，唔會夾雜 prose。`json.loads(response.text)` 直接 parse。

---

## Text Boilerplate（text-only generation）

```python
import os
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Your prompt here",
)
print(response.text)
```

---

## Error Handling

常見 error：
- `429` — rate limit 或 quota exceeded → 等 30s retry，超過 3 次 fail tag Kary
- `400` — prompt 或 image invalid → 報錯，唔好 silent retry
- `404` — model ID 唔 available（e.g. `gemini-2.0-flash` 系列 2026-06-01 起停用）→ 用 `gemini-2.5-flash`
- JSON parse fail → 即係 model output 唔係 valid JSON，先 log raw `response.text` 再 fail

```python
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[img, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )
    data = json.loads(response.text)
except json.JSONDecodeError:
    print(f"Gemini returned non-JSON: {response.text}")
    raise
except Exception as e:
    print(f"Gemini API error: {e}")
    raise
```

---

## 唔用 MCP

同 Calendar / Drive 一樣，**禁止用 MCP tool 操作 Gemini**。Cloud MCP 連 Kary 嘅個人帳號，行為 + billing 都唔對。永遠用上面 boilerplate + `GEMINI_API_KEY` env var。
