# ⚡ 快速部署到 Railway

## 🔗 重要連結

- **GitHub 儲存庫**：https://github.com/cchs61248/google_review_analysis
- **Railway 官網**：https://railway.app/
- **OpenAI API Keys**：https://platform.openai.com/api-keys
- **Gemini API Keys**：https://aistudio.google.com/apikey

---

## 📝 必需的環境變數

### 使用 OpenAI (GPT-4)

| 變數名稱 | 變數值 |
|---------|--------|
| `OPENAI_API_KEY` | 您的 OpenAI API Key |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` |
| `LLM_MODEL` | `gpt-4o` |
| `LOG_LEVEL` | `INFO` |

### 使用 Gemini（推薦，更便宜）

| 變數名稱 | 變數值 |
|---------|--------|
| `OPENAI_API_KEY` | 您的 Gemini API Key |
| `OPENAI_BASE_URL` | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| `LLM_MODEL` | `gemini-2.0-flash-exp` |
| `LOG_LEVEL` | `INFO` |

---

## 🚀 三步驟快速部署

### 第 1 步：前往 Railway
1. 開啟 https://railway.app/
2. 用 GitHub 帳號登入

### 第 2 步：部署專案
1. 點擊 **"New Project"**
2. 選擇 **"Deploy from GitHub repo"**
3. 選擇 **`cchs61248/google_review_analysis`**
4. 點擊 **"Deploy Now"**

### 第 3 步：設定環境變數
1. 點擊服務 → **"Variables"** 標籤
2. 添加上面表格中的 4 個環境變數
3. 等待部署完成（3-5 分鐘）
4. **"Settings"** → **"Generate Domain"** 取得網址

---

## ✅ 快速測試

部署完成後：

1. 訪問生成的網址
2. 測試健康檢查：`https://你的網址/api/health`
3. 貼上 Google Maps 網址測試完整功能

---

## 📚 詳細文檔

- **詳細部署指南**：`RAILWAY_DEPLOY_GUIDE.md`
- **檢查清單**：`DEPLOY_CHECKLIST.md`
- **通用部署說明**：`commands/deploy_vercel.md`

---

**就是這麼簡單！** 🎉
