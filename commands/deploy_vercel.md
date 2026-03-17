# Railway 部署檢查清單

## 部署前準備

### 1. 環境變數設定
在 Railway 專案設定中，確認以下環境變數已正確設定：

```bash
# 必須設定
OPENAI_API_KEY=your_openai_api_key_here

# 可選設定
OPENAI_BASE_URL=https://api.openai.com/v1  # 如果使用其他 API endpoint
LLM_MODEL=gemini-3-flash                    # 你使用的模型名稱
LOG_LEVEL=INFO                              # 日誌級別
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
   - 檢查 Playwright 安裝是否成功
   - 確認所有依賴套件都正確安裝

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
- `playwright_installed`: 應該是 `true`
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

### 問題 1: 找不到評論分頁
**症狀**: 日誌顯示「無法自動切換到評論分頁」

**可能原因**:
- URL 解析錯誤
- 頁面載入不完整
- Google Maps 頁面結構變更

**解決方法**:
1. 檢查日誌中的 URL 解析結果是否正確
2. 確認解析後的 URL 包含 `/maps/place/` 或 `/maps/`
3. 如果是短網址問題，嘗試使用完整的 Google Maps URL

### 問題 2: 找不到排序按鈕
**症狀**: 日誌顯示「找不到排序按鈕」

**影響**: 輕微，程式會使用預設排序繼續執行

**說明**:
- 在無頭模式下，如果找不到排序按鈕，程式會自動使用預設排序
- 不會中斷爬取流程

### 問題 3: Playwright 安裝失敗
**症狀**: 建置日誌顯示 Playwright 相關錯誤

**解決方法**:
1. 確認 `railway.json` 中的 buildCommand 正確
2. 檢查是否有網路連線問題
3. 嘗試重新部署

### 問題 4: 記憶體不足
**症狀**: 容器崩潰或 OOM 錯誤

**解決方法**:
1. 升級 Railway 方案以獲得更多記憶體
2. 減少 `max_reviews` 數量
3. 確認 `railway.json` 中只使用 1 個 worker

## 本地測試無頭模式

在部署到 Railway 前，可以先在本地測試無頭模式：

```bash
# 啟動虛擬環境
.venv\Scripts\Activate.ps1

# 執行無頭模式測試
.venv\Scripts\python.exe test_headless.py
```

輸入測試 URL 後，確認：
1. URL 解析正確
2. 可以成功切換到評論分頁
3. 可以抓取到評論資料

## 最佳化建議

### 1. 調整超時時間
如果 Railway 環境較慢，可以在 `src/config.py` 中增加超時時間：

```python
TIMEOUT_PAGE_LOAD = 90000  # 從 60000 增加到 90000
TIMEOUT_SELECTOR = 15000   # 從 12000 增加到 15000
```

### 2. 增加等待時間
在 `src/core/maps_page.py` 中的無頭模式等待時間已經增加，如果還是有問題可以進一步調整。

### 3. 使用更穩定的 URL
建議使用完整的 Google Maps URL 而非短網址，格式如：
```
https://www.google.com/maps/place/店家名稱/@經度,緯度,zoom/...
```

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
