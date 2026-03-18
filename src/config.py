"""
專案配置檔案
統一管理所有配置常數和環境變數
"""
import os
from pickle import FALSE
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# python-dotenv 會把「KEY = value」解析成 key 名稱尾端帶空白。
# 這裡做容錯讀取，避免因 .env 格式而讀不到設定。
def _getenv_stripped(key: str, default: str | None = None) -> str | None:
    v = os.getenv(key)
    if v is None:
        v = os.getenv(f"{key} ")
    if v is None:
        return default
    return str(v).strip().strip('"').strip("'")


# ==================== API 配置 ====================
OPENAI_API_KEY = _getenv_stripped("OPENAI_API_KEY")
OPENAI_BASE_URL = _getenv_stripped("OPENAI_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = _getenv_stripped("LLM_MODEL", "gemini-3-flash")
STREAM = False

# SerpApi（Google Maps 評論 API）
SERPAPI_API_KEY = _getenv_stripped("SERPAPI_API_KEY")

# ==================== Redis 配置（評論快取） ====================
REDIS_HOST = _getenv_stripped("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(_getenv_stripped("REDIS_PORT", "6379") or "6379")
REDIS_DB = int(_getenv_stripped("REDIS_DB", "1") or "1")
REDIS_PASSWORD = _getenv_stripped("REDIS_PASSWORD") or None

# ==================== 日誌配置 ====================
LOG_LEVEL = _getenv_stripped("LOG_LEVEL", "INFO")
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
