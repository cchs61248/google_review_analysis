"""
日誌工具模組
"""
import os
import logging
from pathlib import Path
from ..config import LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT


def setup_logger(log_file: str = "scraper.log") -> None:
    """
    設定日誌系統
    
    Args:
        log_file: 日誌檔案名稱，預設為 scraper.log
    """
    # 取得專案根目錄，日誌寫入 /log 資料夾
    root_dir = Path(__file__).parent.parent.parent
    log_dir = root_dir / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / log_file
    
    # 設定日誌
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )
