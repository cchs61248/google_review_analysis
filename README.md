# Google Maps 評論分析器

透過 **SerpApi** 取得 Google Maps 評論，再以 **LLM** 產出推薦餐點、負評重點與整體分析。

支援 **Web**、**GUI（PySide6）** 與 **CLI**。

---

## 功能特色

- **SerpApi 取評論**：無需瀏覽器；支援分享連結、短網址、`/maps/place/` 等（自動跟轉址並解析查詢）
- **短網址**：`maps.app.goo.gl`、`share.google` 等會自動跟轉址
- **AI 分析**：Markdown 報告（推薦／不推薦、整體評價）
- **多介面**：Web、GUI、CLI

**注意**：SerpApi 依搜尋與分頁計費；評論內容以 API 回傳的 `snippet` 為主，可能比網頁略短。

---

## 專案結構（精簡）

```
google_map/
├── app.py                  # Flask API（完整分析）
├── gui.py / run.py         # GUI / CLI
├── requirements.txt
├── .env.example
├── templates/ , static/
└── src/
    ├── config.py           # OPENAI_*、SERPAPI_API_KEY
    ├── core/
    │   ├── scraper.py      # GoogleMapsScraper
    │   └── serpapi_reviews.py
    ├── utils/
    │   ├── url_to_query.py # 網址 → 查詢字串
    │   └── url_resolver.py
    ├── services/analyzer.py
    └── ui/
```

---

## 安裝

- Python 3.10+

```powershell
pip install -r requirements.txt
cp .env.example .env
```

`.env` 必填：

```env
SERPAPI_API_KEY=你的_SerpApi_Key
OPENAI_API_KEY=你的_LLM_Key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o
LOG_LEVEL=INFO
```

SerpApi 註冊：<https://serpapi.com/>

---

## 使用方式

### Web

```powershell
.\.venv\Scripts\python.exe app.py
```

瀏覽 <http://127.0.0.1:5000>

### GUI

```powershell
.\.venv\Scripts\python.exe gui.py
```

### CLI

```powershell
.\.venv\Scripts\python.exe run.py "https://maps.app.goo.gl/xxxxx" --limit 30
```

| 參數 | 說明 |
|------|------|
| `url` | Google Maps 或分享網址 |
| `--limit` | 評論則數（預設 30） |

---

## 常見問題

- **未設定 SERPAPI_API_KEY**：程式會直接提示，請寫入 `.env`。
- **找不到評論 / data_id**：換用 Google 分享連結，或確認店名在搜尋結果中可辨識。
- **AI 分析失敗**：檢查 `OPENAI_API_KEY` 與 `OPENAI_BASE_URL`、`LLM_MODEL`。

---

## 測試 SerpApi

```powershell
.\.venv\Scripts\python.exe test_headless.py
```

---

## 相依套件（主要）

| 套件 | 用途 |
|------|------|
| `serpapi` | Google Maps / 評論 API |
| `requests` | 轉址與網址解析 |
| `openai` | LLM |
| `Flask` / `gunicorn` | Web |
| `PySide6` | GUI（選用） |
| `python-dotenv` | `.env` |

---

## 部署

- **Railway / Render / 自架**：部署 `app.py`，環境變數設定 `SERPAPI_API_KEY`、`OPENAI_API_KEY`。`railway.json` 僅需 `pip install -r requirements.txt`（已移除 Playwright）。
- **Vercel**：靜態或輕量 `api/index.py` 僅示意；完整分析請用長運行服務執行 `app.py`。

詳見 [`commands/deploy_vercel.md`](commands/deploy_vercel.md)。
