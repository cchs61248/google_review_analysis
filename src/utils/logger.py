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

    本地開發：寫入專案根目錄下的 log/ 並同時輸出到終端機。
    Vercel 等唯讀檔案系統：僅輸出到 stdout（可在 Vercel Dashboard 查看）。
    """
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    # Vercel 會設定 VERCEL=1；/var/task 為唯讀，不可建立 log 目錄
    on_vercel = bool(os.environ.get("VERCEL"))
    if not on_vercel:
        root_dir = Path(__file__).parent.parent.parent
        log_dir = root_dir / "log"
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            handlers.insert(
                0,
                logging.FileHandler(log_dir / log_file, encoding="utf-8"),
            )
        except OSError:
            # 其他唯讀環境（例如部分容器）同樣只打 stdout
            pass

    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=handlers,
        force=True,
    )
