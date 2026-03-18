"""
專案配置檔案
統一管理所有配置常數和環境變數
"""
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# ==================== API 配置 ====================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3-flash")

# SerpApi（Google Maps 評論 API）
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# ==================== 日誌配置 ====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ==================== 爬蟲配置 ====================
DEFAULT_MAX_REVIEWS = 30
DEFAULT_LOCALE = "zh-TW"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

# ==================== 超時設定 ====================
TIMEOUT_URL_RESOLVE = 10  # 秒
