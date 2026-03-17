# Railway 部署指南

✅ **代碼已成功推送到 GitHub！**

現在請按照以下步驟在 Railway 上部署您的應用：

---

## 第 1 步：登入 Railway

1. 前往 [Railway.app](https://railway.app/)
2. 點擊右上角的 **"Login"** 或 **"Start a New Project"**
3. 使用您的 GitHub 帳號登入（推薦）

---

## 第 2 步：建立新專案

1. 登入後，點擊 **"New Project"** 按鈕
2. 選擇 **"Deploy from GitHub repo"**
3. 如果是第一次使用，Railway 會要求您授權訪問 GitHub
4. 授權後，選擇儲存庫：**`cchs61248/google_review_analysis`**
5. 點擊 **"Deploy Now"** 或 **"Add variables"**

---

## 第 3 步：設定環境變數（重要！）

在專案頁面，點擊您的服務（service），然後進入 **"Variables"** 標籤頁。

### 必需的環境變數：

#### 如果使用 OpenAI (GPT-4)：

```
OPENAI_API_KEY=你的_OpenAI_API_Key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o
LOG_LEVEL=INFO
```

#### 如果使用 Google Gemini（推薦，更便宜）：

```
OPENAI_API_KEY=你的_Gemini_API_Key
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LLM_MODEL=gemini-2.0-flash-exp
LOG_LEVEL=INFO
```

### 如何添加環境變數：

1. 點擊 **"New Variable"** 按鈕
2. 輸入 **Variable Name**（例如：`OPENAI_API_KEY`）
3. 輸入 **Variable Value**（您的 API Key）
4. 點擊 **"Add"**
5. 重複以上步驟添加所有環境變數

---

## 第 4 步：等待部署完成

1. 環境變數設定完成後，Railway 會自動開始部署
2. 您可以在 **"Deployments"** 標籤查看部署進度
3. 首次部署需要：
   - 下載 Python 和依賴套件
   - 安裝 Playwright 瀏覽器（Chromium）
   - **預計時間：3-5 分鐘**

### 如何查看部署日誌：

- 點擊最新的部署記錄
- 查看 **"Build Logs"** 和 **"Deploy Logs"**
- 確認看到類似訊息：
  ```
  ✓ Playwright installed successfully
  ✓ Starting Gunicorn server
  ```

---

## 第 5 步：取得應用網址

部署成功後：

1. 點擊 **"Settings"** 標籤
2. 找到 **"Networking"** 區域
3. 點擊 **"Generate Domain"** 按鈕
4. Railway 會自動生成一個公開網址，例如：
   ```
   https://google-review-analysis-production.up.railway.app
   ```
5. 複製這個網址並在瀏覽器中打開

---

## 第 6 步：測試應用

1. 開啟生成的網址
2. 您應該會看到「Google Maps 評論分析器」的介面
3. 測試功能：
   - 貼上一個 Google Maps 地點網址
   - 點擊「開始分析」
   - 等待爬取和分析完成（約 2-3 分鐘）

### 測試網址範例：

```
https://maps.app.goo.gl/abc123xyz
```

---

## 常見問題排查

### ❌ 問題 1：部署失敗

**可能原因**：
- Playwright 安裝失敗
- 記憶體不足

**解決方法**：
1. 檢查 **Deploy Logs** 找出錯誤訊息
2. 確認 `railway.json` 中的 `buildCommand` 正確
3. 嘗試重新部署：在 Deployments 頁面點擊 **"Redeploy"**

---

### ❌ 問題 2：應用啟動後無法訪問

**可能原因**：
- 環境變數未設定
- PORT 環境變數問題

**解決方法**：
1. 確認所有環境變數已正確設定（特別是 `OPENAI_API_KEY`）
2. 檢查 **"Deploy Logs"** 是否有錯誤
3. 訪問健康檢查端點：`https://你的網址/api/health`

---

### ❌ 問題 3：爬蟲執行失敗

**可能原因**：
- Playwright 瀏覽器未正確安裝
- 記憶體不足

**解決方法**：
1. 確認 Build Logs 中有 `playwright install chromium` 成功訊息
2. 升級 Railway 方案以獲得更多記憶體（如果使用免費方案）
3. 減少爬取的評論數量（例如從 50 改為 20）

---

### ❌ 問題 4：AI 分析失敗

**可能原因**：
- API Key 錯誤或過期
- API 配額用盡

**解決方法**：
1. 檢查 `OPENAI_API_KEY` 是否正確
2. 確認 `OPENAI_BASE_URL` 設定正確
3. 測試 API Key 是否有效：
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer 你的_API_Key"
   ```

---

## Railway 免費額度說明

- **免費額度**：$5 USD/月
- **包含**：
  - 512 MB RAM
  - 1 GB 磁碟空間
  - 共享 CPU
  - 無限頻寬

- **適合**：測試和輕度使用
- **不足時**：可升級到 Hobby 方案（$5/月起）

---

## 成本優化建議

1. **使用 Gemini 而非 GPT-4**：
   - Gemini Flash 通常更便宜
   - 效果相近

2. **限制評論數量**：
   - 預設爬取 30 則評論
   - 如果只需要大致了解，10-15 則即可

3. **按需使用**：
   - Railway 按使用時間計費
   - 不用時可以暫停專案（Settings → Sleep After）

---

## 下一步

✅ 部署完成後，您可以：

1. **分享應用**：將網址分享給他人使用
2. **手機訪問**：在手機瀏覽器中打開網址
3. **自訂網域**：在 Railway Settings 中設定自己的網域名稱
4. **監控使用**：在 Railway 儀表板查看資源使用情況

---

## 需要協助？

如果遇到問題：

1. 查看 Railway 的 Deploy Logs
2. 查看應用的日誌（在 Railway 專案頁面）
3. 檢查本專案的 `commands/deploy_vercel.md` 文檔
4. 參考 Railway 官方文檔：https://docs.railway.app/

---

**祝您部署順利！** 🚀
