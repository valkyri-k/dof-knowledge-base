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
pip install google-generativeai pillow
```

`pillow` 用嚟 load image（Vision use case）。純 text generation 唔需要。

---

## Vision Boilerplate（image → structured JSON）

呢個 pattern 適用：OCR、screenshot 解析、image content extraction。

```python
import os
import json
import google.generativeai as genai
from PIL import Image

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel(
    "gemini-2.0-flash",
    generation_config={
        "response_mime_type": "application/json",
        "temperature": 0.1,
    },
)

img = Image.open("/path/to/image.png")

prompt = """
[describe what to extract; specify JSON schema in prompt]

Return JSON only, no prose. If a field is unclear, use empty string or empty list.

Example:
{"field_a": "...", "field_b": [...]}
"""

response = model.generate_content([prompt, img])
data = json.loads(response.text)
```

### Model choice
- `gemini-2.0-flash` — default for OCR / structured extraction（fast、cheap、JSON mode 支援好）
- `gemini-2.5-pro` — 用喺需要 deeper reasoning 嘅 vision task（e.g. layout analysis、chart understanding），先確認 fast 唔夠用

### Temperature
- `0.1` for structured extraction（OCR、JSON output）
- 唔好用 default `1.0`，會增加 hallucination risk

### JSON mode
`response_mime_type: "application/json"` — 強制 model output 純 JSON，唔會夾雜 prose。`json.loads(response.text)` 直接 parse。

---

## Text Boilerplate（text-only generation）

```python
import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

response = model.generate_content("Your prompt here")
print(response.text)
```

---

## Error Handling

常見 error：
- `429` — rate limit 或 quota exceeded → 等 30s retry，超過 3 次 fail tag Kary
- `400` — prompt 或 image invalid → 報錯，唔好 silent retry
- JSON parse fail → 即係 model output 唔係 valid JSON，先 log raw `response.text` 再 fail

```python
try:
    response = model.generate_content([prompt, img])
    data = json.loads(response.text)
except json.JSONDecodeError as e:
    print(f"Gemini returned non-JSON: {response.text}")
    raise
except Exception as e:
    print(f"Gemini API error: {e}")
    raise
```

---

## 唔用 MCP

同 Calendar / Drive 一樣，**禁止用 MCP tool 操作 Gemini**。Cloud MCP 連 Kary 嘅個人帳號，行為 + billing 都唔對。永遠用上面 boilerplate + `GEMINI_API_KEY` env var。
