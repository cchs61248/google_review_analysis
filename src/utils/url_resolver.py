"""
URL 解析工具
"""
import requests
import logging
from ..config import TIMEOUT_URL_RESOLVE

logger = logging.getLogger(__name__)


def resolve_short_url(url: str) -> str:
    """
    解析 Google Maps 短網址為完整網址

    Args:
        url: Google Maps 網址

    Returns:
        解析後的完整網址，若發生錯誤則回傳原始網址
    """
    # 對於 Google Maps 的標準網址或短網址，直接讓 Playwright 的瀏覽器去處理
    # 因為 Playwright 有完整的 JS 引擎，能完美處理 Google 的重新導向邏輯
    # 使用 requests.get 反而容易被 Google 降級導向到一般的搜尋頁面
    known_domains = [
        "/maps/place/",
        "google.com/maps",
        "maps.app.goo.gl",
        "share.google",
        "g.page"
    ]

    if any(domain in url for domain in known_domains):
        # 對於 share.google，我們還是讓 requests 去解析，因為 headless 模式下的 playwright
        # 直接開 share.google 很容易被導向到 google.com/search，反而失去地圖資訊
        if "share.google" not in url:
            logger.info(f"網址將交由瀏覽器直接解析: {url[:80]}...")
            return url

    try:
        # 使用 GET 請求而非 HEAD，某些短網址服務對 HEAD 請求的處理不同
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        response = requests.get(
            url,
            allow_redirects=True,
            timeout=TIMEOUT_URL_RESOLVE,
            headers=headers
        )
        resolved_url = response.url

        # 驗證解析後的網址是否有效
        if "google.com" in resolved_url and ("/maps/" in resolved_url or "/search" in resolved_url):
            logger.info(f"URL 解析成功: {url} -> {resolved_url}")
            return resolved_url
        else:
            logger.warning(f"解析結果似乎無效: {resolved_url[:80]}，使用原始網址")
            return url

    except requests.RequestException as e:
        logger.warning(f"URL 解析失敗: {e}，使用原始網址")
        return url
