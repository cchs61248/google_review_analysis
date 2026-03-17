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

# ==================== 日誌配置 ====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ==================== 爬蟲配置 ====================
# 瀏覽器啟動參數（降低被偵測為自動化）
BROWSER_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage",
    "--disable-infobars",
    "--window-size=1920,1080",
    "--no-first-run",
    "--no-default-browser-check",
]

# 無頭模式額外參數（防止 Google 偵測）
BROWSER_ARGS_HEADLESS = BROWSER_ARGS + [
    "--disable-gpu",
    "--disable-software-rasterizer",
    "--disable-extensions",
    "--disable-background-networking",
    "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding",
    "--disable-backgrounding-occluded-windows",
    "--disable-ipc-flooding-protection",
    "--no-sandbox",
    "--ignore-certificate-errors",
]

# 預設爬取設定
DEFAULT_MAX_REVIEWS = 30
DEFAULT_HEADLESS = False
DEFAULT_LOCALE = "zh-TW"
DEFAULT_VIEWPORT = {"width": 1280, "height": 900}
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

# 滾動與解析設定
MIN_SCROLL_ROUNDS = 15
NO_CHANGE_THRESHOLD = 8
SCROLL_WAIT_TIME = 2  # 秒

# ==================== 選擇器配置 ====================
# Google Maps 頁面選擇器
SELECTORS = {
    "cookie_accept": "button[name='全部接受']",
    "maps_place_link": 'a[href*="/maps/place/"]',
    "review_tab_labels": ["評論", "Reviews"],
    "sort_button": "排序",
    "sort_newest": ["最新", "Newest"],
    # 評論外層容器（含頭像、名稱、星數、時間與文字等）
    "review_item": 'div.bwb7ce',
    # 展開完整評論的「更多」按鈕／連結
    "more_button": [
        'a.MtCSLb[role="button"]',                 # e.g. <a class="MtCSLb" ...>更多</a>
        'button[aria-label^="查看更多"]',
        'button[aria-label*="More"]',
        'button:has-text("更多")',
        'a[role="button"]:has-text("更多")',
    ],
    # 評分：優先使用你提供的 div 結構，再退回舊的 aria-label 星星
    "rating": [
        'div.k0Ysuc div.dHX2k[role="img"]',  # e.g. aria-label="獲評為 5.0 顆星 (最高 5 顆星)"
        'span[role="img"][aria-label*="星"]',
        'span[role="img"][aria-label*="star"]',
    ],
    # 評論文字：你提供的 OA1nbd 結構已在這裡
    "review_text": ["div.OA1nbd", "span.wiI7pd"],
    "suggested_dishes": "span.RfDO5c",
}

# ==================== 超時設定 ====================
TIMEOUT_PAGE_LOAD = 60000  # 毫秒
TIMEOUT_SELECTOR = 12000
TIMEOUT_CLICK = 5000
TIMEOUT_SHORT = 2000
TIMEOUT_URL_RESOLVE = 10  # 秒
