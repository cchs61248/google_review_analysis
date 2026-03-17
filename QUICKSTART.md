# 快速開始指南

## 🚀 3 分鐘快速啟動

### 前置需求
- ✅ Python 3.10 或更高版本
- ✅ 已安裝虛擬環境（`.venv` 資料夾存在）
- ✅ OpenAI API Key（或相容的 LLM API）

### 步驟 1：設定環境變數

複製環境變數範本：
```powershell
Copy-Item .env.example .env
```

編輯 `.env` 文件，填入你的 API Key：
```env
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-your-api-key-here
LLM_MODEL=gpt-4o
LOG_LEVEL=INFO
```

> 💡 **使用 Gemini？** 改用以下設定：
> ```env
> OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
> OPENAI_API_KEY=your-gemini-api-key
> LLM_MODEL=gemini-1.5-flash
> ```

### 步驟 2：啟動應用

**選項 A：使用啟動腳本（推薦）**
```powershell
.\start_web.ps1
```

**選項 B：手動啟動**
```powershell
# 啟動虛擬環境
.\.venv\Scripts\Activate.ps1

# 安裝依賴（首次）
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 啟動 Flask
.\.venv\Scripts\python.exe app.py
```

### 步驟 3：開啟瀏覽器

應用啟動後，你會看到類似的訊息：
```
* Running on http://127.0.0.1:5000
* Running on http://192.168.2.190:5000
```

**電腦訪問：** http://127.0.0.1:5000

**手機訪問：** http://192.168.2.190:5000（你的實際 IP）

---

## 📱 手機使用設定

### 方法 1：同一 Wi-Fi 網路

1. 確保手機和電腦連接**同一個 Wi-Fi**
2. 在電腦執行：
   ```powershell
   ipconfig
   ```
3. 找到「無線區域網路介面卡 Wi-Fi」的「IPv4 位址」（例如：192.168.1.100）
4. 手機瀏覽器輸入：`http://192.168.1.100:5000`

### 方法 2：雲端部署（建議）

參考 `commands/deploy_vercel.md` 部署到 Railway，獲得公開網址。

---

## 🎯 第一次使用

### 測試用 Google Maps 網址

你可以使用以下範例餐廳進行測試：
```
https://maps.app.goo.gl/TmqvSvnwcGhFRFhE7
```

### 操作流程

1. **貼上網址**：在輸入框中貼上 Google Maps 餐廳網址
2. **設定數量**：選擇要爬取的評論數量（建議先測試 10-20 則）
3. **開始分析**：點擊「開始分析」按鈕
4. **等待完成**：爬取與分析通常需要 1-3 分鐘
5. **查看結果**：切換「AI 分析報告」或「原始評論」分頁

---

## ⚠️ 常見問題

### Q1: 啟動失敗「找不到模組」
**解決方法：**
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Q2: 手機無法連線
**檢查清單：**
- [ ] 手機和電腦在同一 Wi-Fi
- [ ] 使用正確的電腦 IP
- [ ] Windows 防火牆允許 5000 埠
- [ ] 電腦沒有開啟 VPN

**臨時關閉防火牆（測試用）：**
```powershell
# 以管理員身份執行 PowerShell
New-NetFirewallRule -DisplayName "Flask Dev" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

### Q3: 爬取失敗「未找到評論」
**可能原因：**
- Google Maps 網址無效
- Playwright 瀏覽器未安裝
- 被 Google reCAPTCHA 阻擋

**解決方法：**
```powershell
# 安裝 Playwright 瀏覽器
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe -m playwright install-deps chromium
```

### Q4: AI 分析失敗
**檢查清單：**
- [ ] `.env` 文件存在且設定正確
- [ ] `OPENAI_API_KEY` 有效
- [ ] API 額度充足
- [ ] 網路連線正常

---

## 🛠️ 三種使用模式

### 1. Web 介面（本指南）
- 適合：日常使用、手機訪問
- 優點：視覺化、響應式、易用
- 啟動：`python app.py` 或 `.\start_web.ps1`

### 2. GUI 圖形介面
- 適合：桌面應用、離線使用
- 優點：完整功能、不需瀏覽器
- 啟動：`python gui.py`

### 3. CLI 命令列
- 適合：腳本自動化、批次處理
- 優點：輕量、可整合
- 啟動：`python run.py <網址> --limit 30`

---

## 📚 更多資訊

- **完整部署指南**：`commands/deploy_vercel.md`
- **Web 介面說明**：`commands/WEB_INTERFACE.md`
- **專案完成總結**：`PROJECT_COMPLETION.md`
- **主要文檔**：`README.md`

---

## 💡 實用技巧

### 加速分析
- 減少評論數量（10-20 則適合測試）
- 使用 Gemini Flash（比 GPT-4 快且便宜）

### 避免被封鎖
- 不要短時間內爬取大量評論
- 每次爬取間隔至少 1-2 分鐘
- 使用瀏覽器 Profile 保留登入狀態

### 節省成本
- 本地運行（完全免費）
- Railway 免費額度（$5/月）
- 使用開源 LLM（如 Ollama）

---

## 🎉 開始使用吧！

現在你已經準備好了，打開瀏覽器開始分析 Google Maps 餐廳評論吧！

有問題？查看日誌文件：`log/scraper.log`
