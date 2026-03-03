"""
GUI 啟動腳本
"""
import sys
from pathlib import Path

# 確保可以 import src 模組
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from src.ui import MainWindow
from src.utils import setup_logger


def main():
    """主程式入口"""
    # 設定日誌
    setup_logger()
    
    # 創建應用程式
    app = QApplication(sys.argv)
    app.setApplicationName("Google Maps 評論分析器")
    app.setOrganizationName("Google Maps Scraper")
    
    # 創建主視窗
    window = MainWindow()
    window.show()
    
    # 執行應用程式
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
