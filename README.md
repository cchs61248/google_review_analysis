# Google Maps 評論分析器

自動爬取 Google Maps 餐廳評論，並透過 LLM（大型語言模型）進行 AI 分析，產出推薦餐點、不推薦餐點與整體評價報告。

支援 **Web 介面**、**圖形介面（GUI）** 與 **命令列（CLI）** 三種使用方式。

---

## 功能特色

- **自動爬取評論**：使用 Playwright 控制 Chromium 瀏覽器，自動切換到評論分頁、按最新排序、滾動載入更多評論
- **短網址支援**：自動解析 `maps.app.goo.gl` 短網址為完整 Google Maps 網址
- **反偵測機制**：隱藏 WebDriver 特徵、自訂 User-Agent 與語言設定，降低被 Google 封鎖的風險
- **持久化 Profile**：可指定瀏覽器 Profile 目錄，保留登入狀態以減少 reCAPTCHA 驗證
- **AI 分析報告**：爬取完成後自動呼叫 LLM API，輸出 Markdown 格式的分析報告，包含：
  - 推薦餐點（含好評原因）
  - 不推薦餐點（含負評原因）
  - 整體評價與適合客群
- **多種介面**：
  - **Web 介面**：響應式網頁，支援電腦與手機瀏覽器訪問
  - **圖形介面**：基於 PySide6 的 GUI，支援深色/淺色主題切換
  - **命令列**：輕量化 CLI 工具

---

## 專案結構

```
google_map/
├── app.py                  # Flask Web API 入口
├── gui.py                  # GUI 啟動入口
├── run.py                  # CLI 啟動入口
├── requirements.txt        # 相依套件
├── Procfile                # Railway/Heroku 部署配置
├── railway.json            # Railway 專用配置
├── runtime.txt             # Python 版本指定
├── .env                    # 環境變數（請自行建立，不納入版本控制）
├── .env.example            # 環境變數範本
├── templates/              # Web 前端頁面
│   └── index.html
├── static/                 # 靜態資源
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── log/
│   └── scraper.log         # 執行日誌
└── src/
    ├── config.py           # 全域設定（API、爬蟲參數、選擇器等）
    ├── main.py             # CLI 應用程式主類別與 argparse 入口
    ├── core/               # 爬蟲核心模組
    │   ├── browser.py      # 瀏覽器管理（BrowserManager、PageNavigator）
    │   ├── maps_page.py    # Google Maps 頁面操作（切分頁、排序）
    │   ├── parser.py       # 評論元素解析（評分、文字、推薦餐點）
    │   ├── scroller.py     # 自動滾動與評論收集
    │   └── scraper.py      # 爬蟲主類別（GoogleMapsScraper）
    ├── services/
    │   └── analyzer.py     # AI 分析服務（ReviewAnalyzer，呼叫 LLM API）
    ├── ui/
    │   ├── main_window.py  # GUI 主視窗（PySide6）
    │   ├── worker.py       # GUI 背景工作執行緒（ScraperWorker）
    │   ├── theme.py        # 深色/淺色主題樣式
    │   └── log_handler.py  # GUI 日誌處理器
    └── utils/
        ├── url_resolver.py # 短網址解析
        └── logger.py       # 日誌系統初始化
```

---

## 安裝方式

### 前置需求

- Python 3.10+

### 步驟

**1. 安裝相依套件**

```bash
pip install -r requirements.txt
```

**2. 安裝 Playwright 瀏覽器**

```bash
playwright install chromium
```

**3. 建立環境變數檔案**

複製範本並填入你的 API Key：

```bash
cp .env.example .env
```

編輯 `.env`：

```env
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=你的_API_Key
LLM_MODEL=gpt-4o
LOG_LEVEL=INFO
```

> **支援相容 OpenAI 介面的服務**，例如 Gemini（透過 AI Studio API）、Azure OpenAI、或本地端的 Ollama，只需修改 `OPENAI_BASE_URL` 與 `LLM_MODEL` 即可。

---

## 使用方式

### 方式一：Web 介面（推薦）

**本地運行：**

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe app.py
```

啟動後訪問：
- 電腦：http://127.0.0.1:5000
- 手機：http://你的電腦IP:5000（例如：http://192.168.1.100:5000）

**雲端部署：**

詳見 `commands/deploy_vercel.md` 部署指南，推薦使用 Railway 平台。

**特色：**
- ✅ 響應式設計，支援電腦與手機瀏覽器
- ✅ 現代化 UI，操作直覺
- ✅ 即時顯示爬取進度與分析結果
- ✅ 支援分頁切換查看原始評論與 AI 報告

### 方式二：圖形介面（GUI）

```bash
python gui.py
```

介面說明：

| 區域 | 說明 |
|------|------|
| 餐廳資訊 | 輸入 Google Maps 網址（支援短網址），設定爬取評論數量 |
| 進階設定 | 勾選「顯示瀏覽器視窗」可觀察爬取過程或手動處理驗證碼；可選擇 Profile 目錄保留登入狀態 |
| 執行日誌 | 即時顯示爬取進度與系統訊息 |
| 評論內容 | 顯示收集到的原始評論（含評分星級與推薦餐點） |
| AI 分析報告 | LLM 產生的 Markdown 格式分析結果，爬取完成後自動切換至此分頁 |

### 方式三：命令列（CLI）

```bash
python run.py <Google Maps 網址> [選項]
```

**參數說明：**

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `url` | Google Maps 餐廳網址（必填，支援短網址） | — |
| `--limit` | 爬取評論數量 | `30` |
| `--visible` | 顯示瀏覽器視窗（建議遇到驗證碼時開啟） | 隱藏 |
| `--profile` | 瀏覽器 Profile 目錄路徑，保留登入/驗證狀態 | 無 |

**使用範例：**

```bash
# 基本用法
python run.py "https://maps.app.goo.gl/xxxxx"

# 爬取 50 則評論，顯示瀏覽器視窗
python run.py "https://maps.app.goo.gl/xxxxx" --limit 50 --visible

# 使用 Profile 保留登入狀態（減少 reCAPTCHA）
python run.py "https://maps.app.goo.gl/xxxxx" --limit 100 --profile "./browser_profile"
```

---

## 常見問題

### 遇到「我不是機器人」驗證

加上 `--visible` 參數（CLI）或勾選「顯示瀏覽器視窗」（GUI），在瀏覽器跳出驗證時手動完成即可。

也建議搭配 `--profile`（CLI）或在 GUI 選擇 Profile 目錄，讓瀏覽器記住已通過的驗證狀態。

### 爬取到的評論數量少於預期

Google Maps 頁面採動態載入，程式會自動滾動直到：
- 達到指定的評論數量，或
- 連續多輪滾動後沒有新評論出現（已到達頁面底部）

### AI 分析失敗

確認 `.env` 中已正確設定 `OPENAI_API_KEY`，並確認所選模型的 API 可正常連線。

---

## 技術細節

### 反偵測機制

- 在每個新頁面注入 JavaScript 腳本，移除 `navigator.webdriver` 等自動化特徵
- 使用真實 Chrome User-Agent 與 `zh-TW` 語言設定
- 無頭模式下套用額外的 Chromium 啟動參數，避免被識別

### 評論收集邏輯

- 以 `data-review-id` 屬性作為評論去重依據
- 自動點擊「更多」按鈕展開截斷的評論
- 解析評分、評論內文與「建議的餐點」欄位
- 若連續 `NO_CHANGE_THRESHOLD`（預設 8）輪滾動無新評論，提前結束

### GUI 執行緒架構

- 爬蟲與 AI 分析在獨立的 `QThread` 中執行，避免阻塞 UI
- 透過 Qt Signal 機制回傳進度、日誌、評論資料與分析結果
- 支援中途停止，爬蟲收到停止信號後會結束目前週期並回傳已收集的評論

---

## 相依套件

| 套件 | 版本 | 用途 |
|------|------|------|
| `playwright` | 1.58.0 | 瀏覽器自動化（Chromium） |
| `openai` | 2.24.0 | 呼叫 LLM API（相容 OpenAI 介面） |
| `PySide6` | 6.10.2 | 圖形介面框架 |
| `Flask` | 3.0.0 | Web 應用框架 |
| `flask-cors` | 4.0.0 | 跨域請求支援 |
| `gunicorn` | 21.2.0 | WSGI HTTP 伺服器（生產環境） |
| `requests` | 2.32.5 | 短網址解析 |
| `python-dotenv` | 1.2.2 | 讀取 `.env` 環境變數 |

---

## 部署指南

詳細的部署步驟請參考 **[`commands/deploy_vercel.md`](commands/deploy_vercel.md)**

支援的部署平台：
- ✅ **Railway**（推薦）：免費額度，支援 Playwright
- ✅ **Render**：免費方案，支援容器
- ✅ **Docker**：可移植到任何支援容器的平台
- ⚠️ **本地運行**：完全免費，需要電腦持續開機
- ❌ **Vercel**：不支援 Playwright（無瀏覽器環境）
