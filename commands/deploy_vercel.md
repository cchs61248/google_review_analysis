# Vercel 部署指南

## 部署前準備

### 1. 環境變數設定

在 Vercel 專案設定中，到 **Settings → Environment Variables** 新增：

| 變數名稱 | 必填 | 說明 |
|----------|------|------|
| `SERPAPI_API_KEY` | ✅ | SerpApi API Key，用於取得 Google Maps 評論 |
| `OPENAI_API_KEY` | ✅ | OpenAI API Key，用於 AI 分析 |
| `OPENAI_BASE_URL` | 選填 | 預設 `https://api.openai.com/v1` |
| `LLM_MODEL` | 選填 | 預設 `gpt-4o`，可改為 `gemini-3-flash` 等 |
| `LOG_LEVEL` | 選填 | 預設 `INFO` |

### 2. 確認專案檔案

以下檔案需在 Git 內並推送至遠端：

- `vercel.json` - Vercel 設定
- `.python-version` - Python 3.12
- `requirements.txt` - 依賴
- `app.py` - Flask 主程式
- `src/` - 原始碼
- `templates/` - 前端頁面
- `static/` - CSS/JS 靜態檔

---

## 部署方式

### 方式一：透過 Vercel 網站（推薦）

1. 前往 [vercel.com](https://vercel.com) 並登入。
2. 點 **Add New → Project**，選擇 **Import Git Repository**。
3. 選擇此專案的 GitHub/GitLab/Bitbucket 倉庫，點 **Import**。
4. **Framework Preset** 保持自動偵測（會辨識為 Flask）。
5. 在 **Environment Variables** 加入上述變數（或之後到專案 Settings 補填）。
6. 點 **Deploy**，等待建置完成。
7. 之後每次 `git push` 會自動觸發重新部署。

### 方式二：使用 Vercel CLI

1. 安裝 CLI（若尚未安裝）：
   ```powershell
   npm i -g vercel
   ```

2. 在專案根目錄登入並部署：
   ```powershell
   cd c:\Users\dqaiot\Documents\aaron\google_map
   vercel login
   vercel
   ```
   依提示選擇或建立專案、連結 Git。

3. 正式環境部署：
   ```powershell
   vercel --prod
   ```

### 本地預覽（可選）

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
vercel dev
```

---

## 部署後檢查

### 1. 健康檢查

```powershell
curl https://你的專案.vercel.app/api/health
```

預期回應：

```json
{
  "status": "ok",
  "message": "Google Maps 評論分析器 API 運行中"
}
```

### 2. 除錯資訊

```powershell
curl https://你的專案.vercel.app/api/debug
```

確認 `has_openai_key`、`has_serpapi_key` 為 `true`（若已設定環境變數）。

### 3. 功能測試

用瀏覽器開啟 `https://你的專案.vercel.app/` 使用介面，或：

```powershell
curl -X POST https://你的專案.vercel.app/api/analyze -H "Content-Type: application/json" -d "{\"url\": \"你的Google Maps網址\", \"limit\": 10}"
```

---

## 常見問題

### 建置失敗：找不到模組

確認 `src/` 目錄與 `app.py` 一併提交，且專案根目錄有 `requirements.txt`。

### 環境變數未生效

- 在 Vercel 專案 **Settings → Environment Variables** 檢查變數名稱是否與程式一致（區分大小寫）。
- 若在部署後才新增變數，需在 **Deployments** 對最新部署點 **Redeploy** 才會套用。

### 回應逾時或 504

SerpApi 與 OpenAI 呼叫可能較久，Vercel 免費方案有執行時間上限（約 10–60 秒）。若常逾時，可考慮：

- 降低單次 `limit`（例如 10）。
- 升級 Vercel 方案以取得更長逾時。

### 靜態檔（CSS/JS）載入失敗

本專案使用 Flask 的 `static/` 目錄，由 Flask 在執行期提供，無需額外設定。若仍異常，檢查 `templates/index.html` 中 `url_for('static', ...)` 路徑是否正確。

---

## 專案設定說明

- **vercel.json**：僅設定 `installCommand` 使用 `pip install -r requirements.txt`，其餘依 Vercel 預設。
- **.python-version**：指定 Python 3.12，供 Vercel 建置時使用。
- Vercel 會自動偵測根目錄的 `app.py` 並將其中的 `app` 視為 Flask 應用程式。

---

## 更新紀錄

- 初版：新增 Vercel 部署設定與本說明（`vercel.json`、`.python-version`、`commands/deploy_vercel.md`）。
