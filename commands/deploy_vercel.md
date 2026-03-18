# Railway 部署檢查清單

## 部署前準備

### 1. 環境變數設定
在 Railway 專案設定中，確認以下環境變數已正確設定：

```bash
# 必須設定
SERPAPI_API_KEY=your_serpapi_key_here
OPENAI_API_KEY=your_openai_api_key_here

# 可選設定
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gemini-3-flash
LOG_LEVEL=INFO
```

### 2. 確認檔案已推送
確保以下檔案都已經提交到 Git 並推送：
- `railway.json` - Railway 建置和部署配置
- `requirements.txt` - Python 依賴套件
- `app.py` - 主程式
- `src/` 目錄下的所有原始碼
- `templates/` 目錄（如果有前端頁面）

## 部署步驟

1. **推送程式碼到 GitHub**
   ```bash
   git add .
   git commit -m "修正 Railway 部署問題"
   git push
   ```

2. **在 Railway 中觸發部署**
   - Railway 會自動檢測到程式碼變更
   - 或在 Railway Dashboard 手動觸發部署

3. **監控建置日誌**
   - 確認 `pip install -r requirements.txt` 成功（已無需安裝瀏覽器）

## 部署後測試

### 1. 健康檢查
```bash
curl https://你的-railway-domain.railway.app/api/health
```

預期回應：
```json
{
  "status": "ok",
  "message": "Google Maps 評論分析器 API 運行中"
}
```

### 2. 除錯資訊檢查
```bash
curl https://你的-railway-domain.railway.app/api/debug
```

檢查以下資訊：
- `is_railway`: 應該是 `true`
- `has_serpapi_key`: 應該是 `true`
- `has_openai_key`: 應該是 `true`

### 3. 功能測試
使用 Postman 或 curl 測試評論分析功能：

```bash
curl -X POST https://你的-railway-domain.railway.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "你的Google Maps網址",
    "limit": 10
  }'
```

## 常見問題排除

### 問題 1: SerpApi 找不到地點或無評論
**可能原因**: 網址無法還原店名、搜尋結果多筆誤判、SerpApi 額度用盡。

**解決方法**: 改用 Google 分享連結；確認 `SERPAPI_API_KEY`；檢查 SerpApi 儀表板用量。

### 問題 2: 記憶體不足
**症狀**: 容器崩潰或 OOM 錯誤

**解決方法**:
1. 升級 Railway 方案以獲得更多記憶體
2. 減少 `max_reviews` 數量
3. 確認 `railway.json` 中只使用 1 個 worker

## 本地測試 SerpApi

```powershell
.\.venv\Scripts\python.exe test_headless.py
```

確認能取得評論後再部署。

## 最佳化建議

- 減少單次 `limit` 可降低 SerpApi 呼叫次數與費用。
- 分享連結通常比僅座標的 Maps URL 更容易對到正確地點。

## 監控建議

1. **定期檢查日誌**
   - 在 Railway Dashboard 查看應用程式日誌
   - 注意警告和錯誤訊息

2. **設定警報**
   - 在 Railway 設定健康檢查失敗警報
   - 監控應用程式回應時間

3. **效能監控**
   - 記錄每次請求的處理時間
   - 監控記憶體使用情況

## 更新紀錄

### 2026-03-17 修正項目
1. ✅ 改善 URL 解析邏輯（使用 GET 而非 HEAD，增加驗證）
2. ✅ 增加無頭模式等待時間
3. ✅ 改善評論分頁切換容錯處理
4. ✅ 改善排序按鈕容錯處理
5. ✅ 新增 Railway 環境檢測
6. ✅ 新增除錯端點 `/api/debug`
7. ✅ 新增本地無頭模式測試腳本
