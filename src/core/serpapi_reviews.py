"""
透過 SerpApi 取得 Google Maps 評論（取代 Playwright 爬頁）。
"""
from __future__ import annotations

import logging
import math
from collections import Counter
from typing import Any, Callable, Dict, List, Optional

import serpapi

from ..utils.review_cache import get_reviews_cache

logger = logging.getLogger(__name__)

OptionalStopCheck = Optional[Callable[[], bool]]


def _text_to_vector(text: str) -> Counter:
    words = [w.lower() for w in text.split() if w]
    return Counter(words)


def _cosine_similarity(a: str, b: str) -> float:
    va = _text_to_vector(a)
    vb = _text_to_vector(b)
    if not va or not vb:
        return 0.0
    common = set(va.keys()) & set(vb.keys())
    dot = sum(va[w] * vb[w] for w in common)
    na = math.sqrt(sum(c * c for c in va.values()))
    nb = math.sqrt(sum(c * c for c in vb.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _resolve_data_id(client: serpapi.Client, query: str) -> str:
    results = client.search(
        {
            "engine": "google_maps",
            "type": "search",
            "q": query,
            "google_domain": "google.com",
            "hl": "zh-tw",
            "gl": "tw",
        }
    )

    data_id = None
    try:
        place = results.get("place_results") or {}
        if isinstance(place, dict) and place.get("data_id"):
            data_id = place["data_id"]
    except Exception:
        pass

    if not data_id:
        local_results = results.get("local_results") or []
        if not isinstance(local_results, list):
            local_results = []
        best_score = 0.0
        best_id = None
        for local_result in local_results:
            if not isinstance(local_result, dict):
                continue
            title = local_result.get("title", "") or ""
            score = _cosine_similarity(title, query)
            if score > best_score:
                best_score = score
                best_id = local_result.get("data_id")
        if best_id:
            data_id = best_id

    if not data_id:
        raise ValueError(
            "SerpApi 找不到對應地點的 data_id，請確認網址或改用更明確的分享連結。"
        )
    return str(data_id)


def _review_to_dict(review: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    snippet = (review.get("snippet") or "").strip()
    rating = review.get("rating", "")
    details = review.get("details") or {}
    suggested = ""
    if isinstance(details, dict):
        suggested = (details.get("建議的餐點") or "").strip()

    if not snippet and not suggested:
        return None

    text = snippet if snippet else f"（推薦餐點：{suggested}）" if suggested else ""
    return {
        "text": text,
        "rating": rating,
        "suggested_dishes": suggested or None,
    }


def fetch_reviews(
    api_key: str,
    query: str,
    limit: int,
    stop_check: OptionalStopCheck = None,
    force_refresh: bool = False,
) -> List[Dict[str, Any]]:
    """
    以查詢字串（店名或 Maps URL）取得評論列表。

    每則包含：text, rating, suggested_dishes（與舊 Playwright 輸出對齊）。
    """
    if limit <= 0:
        return []

    client = serpapi.Client(api_key=api_key)
    data_id = _resolve_data_id(client, query)
    logger.info("已取得 data_id，開始拉取評論（目標 %s 則）", limit)

    review_list: List[Dict[str, Any]] = []
    next_token: Optional[str] = None

    cache = get_reviews_cache()
    cached = None if force_refresh else cache.get(data_id)
    if cached:
        review_list = list(cached.reviews)
        next_token = cached.next_token
        if len(review_list) >= limit:
            logger.info("review_list 數量大於等於 limit，直接返回 review_list[:limit]")
            return review_list[:limit]

    def consume_page(reviews_raw: Any) -> None:
        nonlocal review_list
        if not isinstance(reviews_raw, list):
            return
        for review in reviews_raw:
            if len(review_list) >= limit:
                break
            if not isinstance(review, dict):
                continue
            row = _review_to_dict(review)
            if row:
                review_list.append(row)

    if not cached:
        if force_refresh:
            logger.info("已啟用 force_refresh，略過 redis 讀取並開始拉取評論")
        else:
            logger.info("redis 中沒有 data_id，開始拉取評論")
        results = client.search(
            {
                "engine": "google_maps_reviews",
                "data_id": data_id,
                "hl": "zh-tw",
                "sort_by": "newestFirst",
            }
        )
        consume_page(results.get("reviews") or [])

    while len(review_list) < limit:
        if stop_check and stop_check():
            logger.info("已收到停止信號，中斷評論分頁")
            break

        try:
            pag = results.get("serpapi_pagination") or {}
            if not isinstance(pag, dict):
                break
            next_token = pag.get("next_page_token")
        except:
            logger.info("review_list數量不足，開始補足評論")
            if not next_token:
                break

        results = client.search(
            {
                "engine": "google_maps_reviews",
                "data_id": data_id,
                "hl": "zh-tw",
                "sort_by": "newestFirst",
                "next_page_token": next_token,
                "num": 20,
            }
        )
        consume_page(results.get("reviews") or [])

    pag = results.get("serpapi_pagination") or {}
    next_token = pag.get("next_page_token")

    cache.set(data_id, review_list, next_token)
    return review_list[:limit]
