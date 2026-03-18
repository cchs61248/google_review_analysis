from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import redis

from ..config import REDIS_DB, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT

logger = logging.getLogger(__name__)


ReviewRow = Dict[str, Any]


@dataclass(frozen=True)
class CachedReviews:
    reviews: List[ReviewRow]
    next_token: Optional[str]


def _redis_key(data_id: str) -> str:
    return f"gmaps:reviews:{data_id}"


def _is_review_row(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False
    return "text" in obj and "rating" in obj


class ReviewsCache:
    def __init__(self) -> None:
        self._client: Optional[redis.Redis] = None

    def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=2,
            )
        return self._client

    def get(self, data_id: str) -> Optional[CachedReviews]:
        try:
            raw = self._get_client().get(_redis_key(data_id))
            if not raw:
                return None
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                return None

            reviews = payload.get("reviews")
            next_token = payload.get("next_token")
            if not isinstance(reviews, list):
                return None
            if next_token is not None and not isinstance(next_token, str):
                return None

            cleaned: List[ReviewRow] = []
            for r in reviews:
                if _is_review_row(r):
                    cleaned.append(r)

            return CachedReviews(reviews=cleaned, next_token=next_token)
        except Exception:
            logger.debug("Redis 讀取失敗（視為 cache miss）", exc_info=True)
            return None

    def set(self, data_id: str, reviews: List[ReviewRow], next_token: Optional[str]) -> None:
        try:
            payload = {"reviews": reviews, "next_token": next_token}
            self._get_client().set(_redis_key(data_id), json.dumps(payload, ensure_ascii=False))
        except Exception:
            logger.debug("Redis 寫入失敗（忽略）", exc_info=True)


_CACHE_SINGLETON: Optional[ReviewsCache] = None


def get_reviews_cache() -> ReviewsCache:
    global _CACHE_SINGLETON
    if _CACHE_SINGLETON is None:
        _CACHE_SINGLETON = ReviewsCache()
    return _CACHE_SINGLETON
