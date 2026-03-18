"""
主程式入口
"""
import sys
import logging
from pathlib import Path
from typing import List, Dict

# 確保可以 import src 模組
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import setup_logger
from src.core import GoogleMapsScraper
from src.services import ReviewAnalyzer

logger = logging.getLogger(__name__)


class Application:
    """應用程式主類別"""

    def __init__(self):
        setup_logger()

    def run(self, url: str, limit: int = 30) -> None:
        """
        執行評論取得與分析流程

        Args:
            url: Google Maps 地點或分享網址
            limit: 要取得的評論數量
        """
        try:
            print(f"目標網址: {url}")
            print("正在透過 SerpApi 取得評論（請確認已設定 SERPAPI_API_KEY）...")
            reviews = self._scrape_reviews(url, limit)

            if not reviews:
                print("未找到評論或取得失敗。請確認網址、SERPAPI_API_KEY 與 SerpApi 額度。")
                print("詳細請查看 log/scraper.log。")
                return

            print(f"成功取得 {len(reviews)} 則評論。正在進行 AI 分析...")
            self._analyze_reviews(reviews)

        except KeyboardInterrupt:
            print("\n\n程式已被使用者中斷。")
            logger.info("程式被使用者中斷")
        except ValueError as e:
            print(f"設定錯誤: {e}")
        except Exception as e:
            print(f"發生未預期的錯誤: {e}")
            logger.exception("發生未預期的錯誤: %s", e)

    def _scrape_reviews(self, url: str, limit: int) -> List[Dict]:
        scraper = GoogleMapsScraper()
        return scraper.scrape_reviews(url, max_reviews=limit)

    def _analyze_reviews(self, reviews: List[Dict]) -> None:
        try:
            analyzer = ReviewAnalyzer()
            result = analyzer.analyze(reviews)
            print("\n" + "=" * 30)
            print("分析報告")
            print("=" * 30 + "\n")
            print(result)
        except ValueError as e:
            print(f"錯誤: {e}")
            print("請檢查 .env 是否已設定 OPENAI_API_KEY。")
        except Exception as e:
            print(f"發生未預期的錯誤: {e}")
            logger.exception("分析過程發生錯誤: %s", e)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Google Maps 餐廳評論分析器（SerpApi）")
    parser.add_argument("url", help="Google Maps 地點或分享網址（支援短網址）")
    parser.add_argument(
        "--limit", type=int, default=30, help="要取得的評論數量（預設 30）"
    )
    args = parser.parse_args()
    Application().run(url=args.url, limit=args.limit)


if __name__ == "__main__":
    main()
