# Railway 環境變數設定範本

## 📋 複製此範本用於 Railway Variables

### 方案 A：使用 OpenAI (GPT-4)

```
OPENAI_API_KEY
您的_OpenAI_API_Key（請替換為實際的 Key）

OPENAI_BASE_URL
https://api.openai.com/v1

LLM_MODEL
gpt-4o

LOG_LEVEL
INFO
```

### 方案 B：使用 Gemini（推薦，更便宜）

```
OPENAI_API_KEY
您的_Gemini_API_Key（請替換為實際的 Key）

OPENAI_BASE_URL
https://generativelanguage.googleapis.com/v1beta/openai/

LLM_MODEL
gemini-2.0-flash-exp

LOG_LEVEL
INFO
```

---

## 🔑 如何取得 API Key

### OpenAI API Key

1. 前往：https://platform.openai.com/api-keys
2. 點擊 **"Create new secret key"**
3. 複製產生的 Key（格式：`sk-proj-xxxxxx...`）
4. ⚠️ **重要**：只會顯示一次，請妥善保存

### Gemini API Key

1. 前往：https://aistudio.google.com/apikey
2. 點擊 **"Create API key"**
3. 選擇或建立 Google Cloud 專案
4. 複製產生的 Key（格式：`AIzaSyxxxxxx...`）

---

## 📝 在 Railway 中設定

### 步驟：

1. 在 Railway 專案頁面，點擊您的服務
2. 進入 **"Variables"** 標籤
3. 點擊 **"New Variable"** 按鈕
4. 逐一添加以上 4 個環境變數：
   - 輸入「變數名稱」（例如：`OPENAI_API_KEY`）
   - 輸入「變數值」（您的實際值）
   - 點擊 **"Add"**
5. 重複直到添加完所有 4 個變數

---

## ✅ 檢查清單

設定完成後，請確認：

- [ ] `OPENAI_API_KEY` 已設定（實際的 API Key，不是佔位符）
- [ ] `OPENAI_BASE_URL` 已設定（正確的端點 URL）
- [ ] `LLM_MODEL` 已設定（模型名稱）
- [ ] `LOG_LEVEL` 已設定（通常設為 INFO）
- [ ] Railway 顯示 4 個環境變數已設定

---

## 🔒 安全注意事項

⚠️ **請勿**將 API Key 提交到 Git 儲存庫！

- API Key 應該只存在於 Railway 的環境變數中
- 不要在代碼中硬編碼 API Key
- 不要將 `.env` 文件提交到 Git（已在 `.gitignore` 中排除）

---

## 💰 成本比較

| 服務 | 模型 | 約略成本 (每 1K tokens) | 推薦用途 |
|------|------|------------------------|---------|
| OpenAI | gpt-4o | $0.005 (input) / $0.015 (output) | 高品質分析 |
| Google | gemini-2.0-flash-exp | $0.00 (目前免費) | 測試和日常使用 |

💡 **建議**：先使用 Gemini 測試，確認功能正常後再考慮是否需要 GPT-4。

---

## 🧪 測試 API Key 是否有效

### 測試 OpenAI API Key

在 PowerShell 中執行：

```powershell
$headers = @{
    "Authorization" = "Bearer 您的_OpenAI_API_Key"
}
Invoke-RestMethod -Uri "https://api.openai.com/v1/models" -Headers $headers
```

### 測試 Gemini API Key

在 PowerShell 中執行：

```powershell
Invoke-RestMethod -Uri "https://generativelanguage.googleapis.com/v1beta/models?key=您的_Gemini_API_Key"
```

如果 API Key 有效，應該會返回可用的模型列表。

---

## ❓ 常見問題

### Q: Railway 的環境變數何時生效？

**A**: 添加或修改環境變數後，Railway 會自動重新部署應用。通常需要 2-3 分鐘。

### Q: 可以稍後修改環境變數嗎？

**A**: 可以！隨時在 Variables 標籤中修改。修改後會自動重新部署。

### Q: 我的 API Key 會被其他人看到嗎？

**A**: 不會。環境變數只有專案擁有者可以查看。Railway 會安全地儲存這些敏感資訊。

### Q: 可以使用其他 LLM 服務嗎？

**A**: 可以！只要該服務提供 OpenAI 相容的 API，調整 `OPENAI_BASE_URL` 和 `LLM_MODEL` 即可。

---

**設定完成後，就可以開始使用您的應用了！** 🎉
