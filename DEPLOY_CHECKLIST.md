# 🚀 Railway 部署檢查清單

## ✅ 準備工作（已完成）

- [x] 代碼已推送到 GitHub
  - 儲存庫：`https://github.com/cchs61248/google_review_analysis`
  - 最新提交：`新增 Web 介面和 Railway 部署配置`

- [x] 必要文件已建立
  - [x] `app.py` - Flask 應用主程式
  - [x] `requirements.txt` - Python 依賴套件
  - [x] `runtime.txt` - Python 版本 (3.11.7)
  - [x] `Procfile` - 啟動命令
  - [x] `railway.json` - Railway 配置
  - [x] `templates/index.html` - 前端頁面
  - [x] `static/` - 靜態資源

- [x] 專案配置正確
  - [x] 已移除桌面 GUI 依賴 (PySide6)
  - [x] Gunicorn 設定 300 秒超時
  - [x] Playwright 設定為 headless 模式
  - [x] 響應式設計支援手機和電腦

---

## 📋 您需要做的事情（請按順序操作）

### 第 1 步：前往 Railway 並登入

- [ ] 開啟瀏覽器
- [ ] 前往 [https://railway.app/](https://railway.app/)
- [ ] 點擊 **"Login"** 按鈕
- [ ] 使用 GitHub 帳號登入

### 第 2 步：建立新專案

- [ ] 點擊 **"New Project"** 
- [ ] 選擇 **"Deploy from GitHub repo"**
- [ ] 授權 Railway 訪問您的 GitHub（如果是第一次）
- [ ] 選擇儲存庫：**`cchs61248/google_review_analysis`**
- [ ] 點擊 **"Deploy Now"**

### 第 3 步：設定環境變數（重要！）

#### 準備您的 API Key

**選項 A：使用 OpenAI (GPT-4)**

- [ ] 準備好您的 OpenAI API Key
- [ ] 前往 [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys) 建立（如果還沒有）

**選項 B：使用 Google Gemini（推薦，更便宜）**

- [ ] 準備好您的 Gemini API Key
- [ ] 前往 [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey) 建立（如果還沒有）

#### 在 Railway 中添加環境變數

- [ ] 在 Railway 專案頁面，點擊您的服務
- [ ] 進入 **"Variables"** 標籤
- [ ] 點擊 **"New Variable"** 添加以下變數：

**如果使用 OpenAI：**

```
變數名稱：OPENAI_API_KEY
變數值：sk-proj-xxxxxxxxxxxxxx（您的 OpenAI API Key）

變數名稱：OPENAI_BASE_URL
變數值：https://api.openai.com/v1

變數名稱：LLM_MODEL
變數值：gpt-4o

變數名稱：LOG_LEVEL
變數值：INFO
```

**如果使用 Gemini：**

```
變數名稱：OPENAI_API_KEY
變數值：AIzaSyxxxxxxxxxxxxxx（您的 Gemini API Key）

變數名稱：OPENAI_BASE_URL
變數值：https://generativelanguage.googleapis.com/v1beta/openai/

變數名稱：LLM_MODEL
變數值：gemini-2.0-flash-exp

變數名稱：LOG_LEVEL
變數值：INFO
```

### 第 4 步：等待部署完成

- [ ] 進入 **"Deployments"** 標籤
- [ ] 查看部署進度（預計 3-5 分鐘）
- [ ] 確認部署成功（狀態顯示綠色勾勾 ✓）

#### 檢查部署日誌：

- [ ] 點擊最新的部署記錄
- [ ] 查看 Build Logs，確認看到：
  ```
  Installing Playwright...
  ✓ Chromium installed successfully
  ```
- [ ] 查看 Deploy Logs，確認看到：
  ```
  Starting gunicorn...
  Booting worker with pid: xxx
  ```

### 第 5 步：取得並測試應用網址

- [ ] 進入 **"Settings"** 標籤
- [ ] 找到 **"Networking"** 區域
- [ ] 點擊 **"Generate Domain"** 按鈕
- [ ] 複製生成的網址（例如：`https://your-app.up.railway.app`）
- [ ] 在瀏覽器中開啟網址

### 第 6 步：測試功能

- [ ] 確認看到「Google Maps 評論分析器」頁面
- [ ] 測試健康檢查：訪問 `https://你的網址/api/health`
  - 應該看到：`{"status": "ok", "message": "..."}`
- [ ] 測試完整功能：
  1. [ ] 貼上一個 Google Maps 網址（例如：`https://maps.app.goo.gl/abc123`）
  2. [ ] 設定評論數量（建議先測試 10 則）
  3. [ ] 點擊「開始分析」按鈕
  4. [ ] 等待結果（約 2-3 分鐘）
  5. [ ] 確認看到評論列表和 AI 分析結果

---

## 🎉 完成！

- [ ] 應用已成功部署並運行
- [ ] 功能測試通過
- [ ] 記下您的應用網址：`_______________________________`

---

## 📱 分享應用

您現在可以：

- [ ] 在電腦瀏覽器使用
- [ ] 在手機瀏覽器使用
- [ ] 分享網址給他人

---

## 💡 額外設定（可選）

### 自訂網域名稱

- [ ] 進入 Railway **"Settings"** → **"Networking"**
- [ ] 點擊 **"Custom Domain"**
- [ ] 輸入您的網域名稱並設定 DNS

### 設定睡眠時間（節省費用）

- [ ] 進入 **"Settings"** → **"Sleep After"**
- [ ] 設定閒置後自動睡眠（例如：30 分鐘）

### 監控使用情況

- [ ] 定期查看 **"Metrics"** 標籤
- [ ] 檢查資源使用和費用

---

## ⚠️ 故障排除

如果遇到問題，請查看：

1. **部署失敗**
   - 檢查 Build Logs 找出錯誤訊息
   - 確認 `railway.json` 配置正確
   - 嘗試 **Redeploy**

2. **應用無法訪問**
   - 確認環境變數已設定
   - 檢查 Deploy Logs 是否有錯誤
   - 測試健康檢查端點

3. **爬蟲失敗**
   - 確認 Playwright 已安裝
   - 檢查記憶體是否足夠
   - 減少評論數量測試

4. **AI 分析失敗**
   - 檢查 API Key 是否正確
   - 確認 API 配額是否足夠
   - 測試 API Key 有效性

詳細說明請參考：`RAILWAY_DEPLOY_GUIDE.md`

---

**準備好了嗎？開始部署吧！** 🚀
