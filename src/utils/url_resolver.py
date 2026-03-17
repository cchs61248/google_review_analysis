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
    # 如果已經是完整的 Google Maps 網址，直接返回
    if "/maps/place/" in url or "google.com/maps" in url:
        logger.info(f"已是完整 Maps 網址，無需解析: {url[:80]}...")
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
            logger.info(f"URL 解析成功: {url[:50]}... -> {resolved_url[:80]}...")
            return resolved_url
        else:
            logger.warning(f"解析結果似乎無效: {resolved_url[:80]}，使用原始網址")
            return url
            
    except requests.RequestException as e:
        logger.warning(f"URL 解析失敗: {e}，使用原始網址")
        return url
