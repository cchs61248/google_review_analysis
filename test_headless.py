"""
無頭模式測試腳本
用於在本地模擬 Railway 環境測試
"""
import os
import sys
from pathlib import Path

# 確保可以 import src 模組
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import resolve_short_url, setup_logger
from src.core import GoogleMapsScraper

# 設定日誌
setup_logger()

def test_headless_scraping(url: str, max_reviews: int = 10):
    """
    測試無頭模式爬蟲
    
    Args:
        url: Google Maps URL
        max_reviews: 最大評論數
    """
    print(f"\n{'='*60}")
    print("開始測試無頭模式爬蟲")
    print(f"{'='*60}\n")
    
    # 1. 解析 URL
    print(f"原始 URL: {url}\n")
    full_url = resolve_short_url(url)
    print(f"解析後 URL: {full_url}\n")
    
    # 2. 使用無頭模式爬取
    print(f"使用無頭模式爬取評論（最多 {max_reviews} 則）...\n")
    
    try:
        scraper = GoogleMapsScraper(headless=True, user_data_dir=None)
        reviews = scraper.scrape_reviews(full_url, max_reviews=max_reviews)
        
        print(f"\n{'='*60}")
        print(f"成功爬取 {len(reviews)} 則評論")
        print(f"{'='*60}\n")
        
        # 顯示前 3 則評論
        for i, review in enumerate(reviews[:3], 1):
            print(f"評論 #{i}:")
            print(f"  評分: {review.get('rating', 'N/A')}")
            print(f"  內容: {review.get('text', 'N/A')[:100]}...")
            print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 測試 URL（請替換成你要測試的 URL）
    test_url = input("請輸入 Google Maps URL: ").strip()
    
    if not test_url:
        print("❌ 請提供有效的 URL")
        sys.exit(1)
    
    success = test_headless_scraping(test_url, max_reviews=10)
    sys.exit(0 if success else 1)
