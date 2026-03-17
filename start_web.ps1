# Google Maps 評論分析器 - Web 版啟動腳本
# 使用方式：在 PowerShell 中執行此腳本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Google Maps 評論分析器 - Web 版" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查虛擬環境
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "[1/4] 啟動虛擬環境..." -ForegroundColor Green
    & .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "[錯誤] 找不到虛擬環境，請先執行：python -m venv .venv" -ForegroundColor Red
    exit 1
}

# 檢查 .env 文件
if (Test-Path ".env") {
    Write-Host "[2/4] 環境變數配置已找到" -ForegroundColor Green
} else {
    Write-Host "[警告] 找不到 .env 文件，請從 .env.example 複製並設定 API Key" -ForegroundColor Yellow
}

# 檢查依賴套件
Write-Host "[3/4] 檢查依賴套件..." -ForegroundColor Green
$packages = @("Flask", "flask-cors", "playwright", "openai", "python-dotenv", "requests")
$missing = @()

foreach ($pkg in $packages) {
    $installed = & .\.venv\Scripts\python.exe -m pip show $pkg 2>$null
    if (-not $installed) {
        $missing += $pkg
    }
}

if ($missing.Count -gt 0) {
    Write-Host "缺少以下套件：$($missing -join ', ')" -ForegroundColor Yellow
    Write-Host "正在安裝..." -ForegroundColor Yellow
    & .\.venv\Scripts\python.exe -m pip install -r requirements.txt
}

# 啟動應用
Write-Host "[4/4] 啟動 Flask 應用..." -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "應用已啟動！" -ForegroundColor Green
Write-Host "電腦瀏覽器訪問：http://127.0.0.1:5000" -ForegroundColor White

# 獲取本機 IP
$ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias Wi-Fi* | Select-Object -First 1).IPAddress
if ($ip) {
    Write-Host "手機瀏覽器訪問：http://${ip}:5000" -ForegroundColor White
}

Write-Host ""
Write-Host "按 Ctrl+C 停止伺服器" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 啟動 Flask
& .\.venv\Scripts\python.exe app.py
