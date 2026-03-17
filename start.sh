#!/bin/bash
# Railway 部署啟動腳本

echo "安裝 Playwright 瀏覽器..."
playwright install chromium
playwright install-deps chromium

echo "啟動 Flask 應用..."
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300
