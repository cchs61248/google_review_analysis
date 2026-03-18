"""
Google Maps 評論取得（SerpApi，無瀏覽器）
"""
import logging
from typing import Callable, Dict, List, Optional

from ..config import SERPAPI_API_KEY
from ..utils.url_to_query import url_to_search_query
from .serpapi_reviews import fetch_reviews

logger = logging.getLogger(__name__)

OptionalStopCheck = Optional[Callable[[], bool]]


class GoogleMapsScraper:
    """透過 SerpApi 取得 Google Maps 評論"""

    def __init__(
        self,
        headless: bool = True,
        user_data_dir: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Args:
            headless: 已廢棄，保留僅為相容舊呼叫。
            user_data_dir: 已廢棄，保留僅為相容舊呼叫。
            api_key: SerpApi Key，預設讀取環境變數 SERPAPI_API_KEY。
        """
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.should_stop = False
        self._api_key = (api_key or SERPAPI_API_KEY or "").strip()
        if not self._api_key:
            raise ValueError(
                "未設定 SerpApi Key。請在 .env 中設定 SERPAPI_API_KEY。"
            )

    def stop(self) -> None:
        self.should_stop = True
        logger.info("收到停止指令")

    def scrape_reviews(self, url: str, max_reviews: int = 50) -> List[Dict]:
        """
        從 Google Maps / 分享網址取得評論。

        Args:
            url: 地點或分享連結
            max_reviews: 最多幾則

        Returns:
            每則含 text, rating, suggested_dishes
        """
        logger.info("開始以 SerpApi 取得評論: %s", url[:80])
        self.should_stop = False
        try:
            query = url_to_search_query(url)
            logger.info("搜尋查詢: %s", query[:100])
        except ValueError as e:
            logger.warning("%s", e)
            return []

        try:
            reviews = fetch_reviews(
                self._api_key,
                query,
                max_reviews,
                stop_check=lambda: self.should_stop,
            )
        except ValueError as e:
            logger.warning("%s", e)
            return []
        except Exception:
            logger.exception("SerpApi 取得評論失敗")
            return []

        logger.info("共取得 %s 則評論", len(reviews))
        return reviews
