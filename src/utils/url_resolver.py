"""
URL 解析（可選）：將短鏈跟隨至最終網址。
評論取得流程已改由 url_to_query.url_to_search_query 處理。
"""
import logging

import requests

from ..config import DEFAULT_USER_AGENT, TIMEOUT_URL_RESOLVE

logger = logging.getLogger(__name__)


def resolve_short_url(url: str) -> str:
    """
    跟隨 HTTP 轉址至最終 URL（除錯或顯示用）。
    """
    try:
        headers = {
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        response = requests.get(
            url,
            allow_redirects=True,
            timeout=TIMEOUT_URL_RESOLVE,
            headers=headers,
        )
        resolved = response.url
        if "google.com" in resolved:
            logger.info("URL 解析: %s -> ...", url[:60])
            return resolved
        return url
    except requests.RequestException as e:
        logger.warning("URL 解析失敗: %s", e)
        return url
