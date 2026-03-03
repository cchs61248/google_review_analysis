"""
程式入口點
直接執行此檔案啟動應用程式
"""
import sys
from pathlib import Path

# 將專案根目錄加入 PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from src.main import main

if __name__ == "__main__":
    main()
