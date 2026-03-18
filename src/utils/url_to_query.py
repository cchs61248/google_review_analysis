"""
從 Google Maps / 分享連結等網址取得 SerpApi 搜尋用查詢字串。
"""
from __future__ import annotations

import logging
import re
from typing import Optional
from urllib.parse import urlparse, parse_qs, unquote

import requests

from ..config import DEFAULT_USER_AGENT, TIMEOUT_URL_RESOLVE

logger = logging.getLogger(__name__)

_REQUEST_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}


def extract_q_from_search_url(search_url: str) -> str:
    """從 Google Search URL 擷取 q 參數並解碼。"""
    parsed = urlparse(search_url)
    params = parse_qs(parsed.query)
    raw_q = params.get("q", [""])[0]
    return unquote(raw_q).replace("+", " ").strip()


def _place_name_from_maps_url(url: str) -> Optional[str]:
    """從 /maps/place/<名稱>/ 路徑擷取店名。"""
    if "/maps/place/" not in url:
        return None
    try:
        after = url.split("/maps/place/", 1)[1]
        after = after.split("?", 1)[0]
        segment = after.split("/")[0]
        segment = segment.strip()
        if not segment or segment.startswith("@"):
            return None
        # 座標開頭如 @22.9,120.2 表示沒有可讀店名
        if re.match(r"^[\d.\-+,]+$", segment):
            return None
        return unquote(segment.replace("+", " ")).strip()
    except (IndexError, ValueError):
        return None


def url_to_search_query(url: str) -> str:
    """
    將使用者輸入的網址轉成可用於 SerpApi google_maps 的查詢字串。

    支援：
    - share.google / maps.app.goo.gl / g.page 等（跟轉址後處理）
    - 轉到 google.com/search?q=... → 用 q
    - /maps/place/店名/... → 用路徑店名
    - 其餘若仍為 maps 相關連結 → 以完整 URL 作為 q（SerpApi 常可辨識）
    """
    url = (url or "").strip()
    if not url:
        raise ValueError("請提供有效的 Google Maps 或分享網址")

    try:
        response = requests.get(
            url,
            allow_redirects=True,
            timeout=TIMEOUT_URL_RESOLVE,
            headers=_REQUEST_HEADERS,
        )
    except requests.RequestException as e:
        raise ValueError(f"無法連線解析網址: {e}") from e

    final = response.url
    logger.info("URL 轉址結果: %s...", final[:120])

    parsed = urlparse(final)
    host = (parsed.netloc or "").lower()

    if "google." in host and "/search" in (parsed.path or ""):
        q = extract_q_from_search_url(final)
        if q:
            return q
        raise ValueError(
            "轉址後為 Google 搜尋頁但無法讀取搜尋關鍵字，請改用其他分享連結。"
        )

    name = _place_name_from_maps_url(final)
    if name:
        return name

    if "/maps/" in final or "maps.google" in host or "google.com/maps" in final:
        # 僅座標、ftid 等：整段 URL 給 SerpApi
        return final.strip()

    raise ValueError(
        "無法從此網址取得店家資訊。請使用 Google Maps 地點連結或 Google 分享連結。"
    )
