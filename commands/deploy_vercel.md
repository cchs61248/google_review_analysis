# Google Maps 評論分析器 - 部署指南

## 重要說明

由於本專案使用 **Playwright** 進行瀏覽器自動化，需要完整的瀏覽器環境，因此：

- ❌ **Vercel 不支援**：Vercel 的無伺服器函數（Serverless Functions）無法運行 Playwright
- ✅ **推薦使用 Railway**：Railway 提供完整的容器環境，支援 Playwright
- ✅ **其他選擇**：Render、Fly.io、自架伺服器等也可以

---

## 方案一：部署到 Railway（推薦）

Railway 提供免費額度，支援 Playwright，部署簡單。

### 步驟

#### 1. 準備專案

確保專案中包含以下文件（已建立）：

- `app.py` - Flask 應用主程式
- `requirements.txt` - Python 依賴套件
- `runtime.txt` - Python 版本
- `Procfile` - 啟動命令
- `railway.json` - Railway 配置
- `templates/` - 前端頁面
- `static/` - 靜態資源

#### 2. 推送到 Git 儲存庫

```powershell
# 初始化 Git（如果還沒有）
git init

# 添加所有檔案
git add .

# 提交變更
git commit -m "準備部署到 Railway"

# 推送到 GitHub（請先建立 GitHub 儲存庫）
git remote add origin https://github.com/你的帳號/google_map.git
git branch -M main
git push -u origin main
```

#### 3. 在 Railway 上部署

1. 前往 [Railway.app](https://railway.app/)
2. 使用 GitHub 帳號登入
3. 點擊 **"New Project"**
4. 選擇 **"Deploy from GitHub repo"**
5. 選擇你的 `google_map` 儲存庫
6. Railway 會自動偵測 Python 專案並開始部署

#### 4. 設定環境變數

在 Railway 專案的 **Variables** 頁面中，添加以下環境變數：

```
OPENAI_API_KEY=你的_OpenAI_API_Key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o
LOG_LEVEL=INFO
```

> **提示**：如果使用 Gemini，設定：
> - `OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/`
> - `OPENAI_API_KEY=你的_Gemini_API_Key`

#### 5. 完成部署

- Railway 會自動重新部署
- 部署完成後，點擊 **"Settings"** → **"Generate Domain"** 獲取公開網址
- 訪問該網址即可使用你的應用

### Railway 部署注意事項

1. **免費額度**：Railway 提供 $5/月的免費額度，足夠測試使用
2. **啟動時間**：首次啟動需要安裝 Playwright 瀏覽器，可能需要 2-3 分鐘
3. **超時設定**：已在 `Procfile` 中設定 300 秒超時，適合爬取大量評論
4. **記憶體**：建議至少 512MB RAM（Railway 免費方案提供）

---

## 方案二：本地運行（開發/測試）

如果只是本地使用或開發測試，可以直接在本機運行：

### 步驟

#### 1. 啟動虛擬環境

```powershell
.\.venv\Scripts\Activate.ps1
```

#### 2. 安裝依賴

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

#### 3. 設定環境變數

確保 `.env` 文件存在並包含：

```env
OPENAI_API_KEY=你的_API_Key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o
LOG_LEVEL=INFO
```

#### 4. 啟動應用

```powershell
.\.venv\Scripts\python.exe app.py
```

#### 5. 訪問應用

開啟瀏覽器，訪問：
- 電腦：http://127.0.0.1:5000
- 手機：http://你的電腦IP:5000（例如：http://192.168.1.100:5000）

> **如何查詢電腦 IP**：
> ```powershell
> ipconfig
> ```
> 找到「無線區域網路介面卡 Wi-Fi」的「IPv4 位址」

---

## 方案三：部署到 Render

Render 也是不錯的選擇，提供免費方案且支援 Playwright。

### 步驟

1. 前往 [Render.com](https://render.com/)
2. 註冊並登入
3. 點擊 **"New +"** → **"Web Service"**
4. 連接你的 GitHub 儲存庫
5. 設定：
   - **Name**: `google-maps-analyzer`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300`
6. 添加環境變數（與 Railway 相同）
7. 點擊 **"Create Web Service"**

---

## 方案四：使用 Docker 容器

如果你熟悉 Docker，可以建立 Dockerfile 部署到任何支援容器的平台。

### Dockerfile 範例

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 複製專案文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安裝 Playwright 瀏覽器
RUN playwright install chromium
RUN playwright install-deps chromium

# 複製應用程式
COPY . .

# 暴露端口
EXPOSE 5000

# 啟動命令
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "300"]
```

### 本地測試 Docker

```powershell
# 建立映像
docker build -t google-maps-analyzer .

# 運行容器
docker run -p 5000:5000 \
  -e OPENAI_API_KEY=你的_API_Key \
  -e OPENAI_BASE_URL=https://api.openai.com/v1 \
  -e LLM_MODEL=gpt-4o \
  google-maps-analyzer
```

---

## 響應式設計驗證

前端已使用響應式設計，支援：

### 電腦瀏覽器
- ✅ Chrome、Edge、Firefox、Safari
- ✅ 最佳顯示寬度：1000px+

### 手機瀏覽器
- ✅ iOS Safari
- ✅ Android Chrome
- ✅ 自動調整佈局，適配小螢幕

### 測試方式

1. **電腦測試**：直接訪問 http://127.0.0.1:5000
2. **手機測試**：
   - 確保手機與電腦在同一 Wi-Fi 網路
   - 查詢電腦 IP：`ipconfig`
   - 手機訪問：http://電腦IP:5000

---

## 常見問題

### Q1: Railway 部署失敗怎麼辦？

**A**: 檢查以下項目：
1. 確認 `requirements.txt` 包含所有依賴
2. 確認 `railway.json` 的 `buildCommand` 正確
3. 查看 Railway 的 **"Deployments"** 頁面的日誌，找出錯誤訊息
4. 確認環境變數已正確設定

### Q2: 爬蟲為什麼這麼慢？

**A**: 
- Playwright 需要啟動完整瀏覽器，首次啟動較慢
- 評論數量越多，爬取時間越長（通常 30 則評論需要 2-3 分鐘）
- 雲端伺服器的網路速度可能較慢

### Q3: 能不能部署到 Vercel？

**A**: 
- **不行**，Vercel 不支援 Playwright（無瀏覽器環境）
- 如果只需要前端展示，可以修改為純靜態網站部署到 Vercel
- 但爬蟲功能必須部署到支援容器的平台（Railway、Render 等）

### Q4: 如何減少成本？

**A**:
1. 使用免費方案：Railway $5/月、Render 免費方案
2. 優化爬取數量：減少每次爬取的評論數
3. 本地運行：完全免費，但需要電腦持續開機
4. 使用便宜的 LLM：改用 Gemini Flash（通常比 GPT-4 便宜）

### Q5: 手機能直接使用嗎？

**A**:
- ✅ 前端完全支援手機瀏覽器
- ✅ 響應式設計，自動調整佈局
- ✅ 支援觸控操作
- ⚠️ 手機直接爬取效能較差，建議使用雲端部署

---

## 總結

| 方案 | 優點 | 缺點 | 推薦程度 |
|------|------|------|----------|
| **Railway** | 簡單、免費額度、支援 Playwright | 免費額度有限 | ⭐⭐⭐⭐⭐ |
| **Render** | 免費、穩定 | 冷啟動較慢 | ⭐⭐⭐⭐ |
| **本地運行** | 完全免費、無限制 | 需要電腦開機 | ⭐⭐⭐ |
| **Docker** | 靈活、可移植 | 需要容器知識 | ⭐⭐⭐ |
| **Vercel** | 速度快、免費 | ❌ 不支援 Playwright | ❌ |

**建議**：新手直接使用 **Railway**，最簡單且效果最好！

---

## 需要幫助？

如有問題，請檢查：
1. 日誌文件：`log/scraper.log`
2. Railway 的 Deployment Logs
3. 瀏覽器開發者工具的 Console（F12）
