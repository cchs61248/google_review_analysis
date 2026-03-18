"""
測試 SerpApi 取得評論（需 .env 內 SERPAPI_API_KEY）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils import setup_logger
from src.core import GoogleMapsScraper

setup_logger()


def test_serpapi_reviews(url: str, max_reviews: int = 10) -> bool:
    print(f"\n{'=' * 60}")
    print("SerpApi 評論測試")
    print(f"{'=' * 60}\n")
    print(f"URL: {url}\n")
    try:
        scraper = GoogleMapsScraper()
        reviews = scraper.scrape_reviews(url, max_reviews=max_reviews)
        print(f"取得 {len(reviews)} 則評論\n")
        for i, r in enumerate(reviews[:3], 1):
            print(f"#{i} 評分={r.get('rating')} 內容={str(r.get('text', ''))[:80]}...")
        return bool(reviews)
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    u = input("請輸入 Google Maps / 分享網址: ").strip()
    if not u:
        print("請提供 URL")
        sys.exit(1)
    sys.exit(0 if test_serpapi_reviews(u, 10) else 1)
