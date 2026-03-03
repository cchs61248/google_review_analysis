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
        url: Google Maps 短網址 (例如 https://maps.app.goo.gl/...)
        
    Returns:
        解析後的完整網址，若發生錯誤則回傳原始網址
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=TIMEOUT_URL_RESOLVE)
        resolved_url = response.url
        logger.info(f"URL 解析成功: {url[:50]}... -> {resolved_url[:80]}...")
        return resolved_url
    except requests.RequestException as e:
        logger.warning(f"URL 解析失敗: {e}，使用原始網址")
        return url
