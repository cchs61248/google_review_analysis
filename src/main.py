"""
主程式入口
"""
import sys
import logging
from pathlib import Path
from typing import List, Dict

# 確保可以 import src 模組
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import resolve_short_url, setup_logger
from src.core import GoogleMapsScraper
from src.services import ReviewAnalyzer

logger = logging.getLogger(__name__)


class Application:
    """應用程式主類別"""
    
    def __init__(self):
        """初始化應用程式"""
        setup_logger()
    
    def run(self, url: str, limit: int = 30, visible: bool = False, profile: str = None) -> None:
        """
        執行爬蟲與分析流程
        
        Args:
            url: Google Maps 餐廳網址
            limit: 要爬取的評論數量
            visible: 是否顯示瀏覽器視窗
            profile: 瀏覽器 profile 目錄路徑
        """
        try:
            # 1. 解析網址
            print(f"正在解析網址: {url}")
            full_url = resolve_short_url(url)
            print(f"完整網址: {full_url}")
            
            # 2. 爬取評論
            print(f"正在啟動爬蟲（這可能需要幾分鐘）...")
            reviews = self._scrape_reviews(full_url, limit, visible, profile)
            
            if not reviews:
                print("未找到評論或爬取失敗。請確認網址是否正確，或嘗試使用 --visible 模式除錯。")
                print("詳細錯誤與跳過原因請查看 log/scraper.log。")
                return
            
            print(f"成功爬取 {len(reviews)} 則評論。正在進行 AI 分析...")
            
            # 3. 分析評論
            self._analyze_reviews(reviews)
            
        except KeyboardInterrupt:
            print("\n\n程式已被使用者中斷。")
            logger.info("程式被使用者中斷")
        except Exception as e:
            print(f"發生未預期的錯誤: {e}")
            logger.exception(f"發生未預期的錯誤: {e}")
    
    def _scrape_reviews(
        self, url: str, limit: int, visible: bool, profile: str
    ) -> List[Dict]:
        """
        爬取評論
        
        Args:
            url: Google Maps 網址
            limit: 評論數量
            visible: 是否顯示瀏覽器
            profile: Profile 路徑
            
        Returns:
            評論列表
        """
        scraper = GoogleMapsScraper(
            headless=not visible,
            user_data_dir=profile,
        )
        return scraper.scrape_reviews(url, max_reviews=limit)
    
    def _analyze_reviews(self, reviews: List[Dict]) -> None:
        """
        分析評論並顯示結果
        
        Args:
            reviews: 評論列表
        """
        try:
            analyzer = ReviewAnalyzer()
            result = analyzer.analyze(reviews)
            
            # 顯示分析結果
            print("\n" + "=" * 30)
            print("分析報告")
            print("=" * 30 + "\n")
            print(result)
            
        except ValueError as e:
            print(f"錯誤: {e}")
            print("請檢查 .env 檔案是否已設定 OPENAI_API_KEY。")
        except Exception as e:
            print(f"發生未預期的錯誤: {e}")
            logger.exception(f"分析過程發生錯誤: {e}")


def main():
    """主程式入口函數（供 CLI 使用）"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Google Maps 餐廳評論分析器")
    parser.add_argument("url", help="Google Maps 餐廳網址（支援短網址）")
    parser.add_argument(
        "--limit", type=int, default=30, help="要爬取的評論數量（預設 30）"
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="顯示瀏覽器視窗（預設為隱藏，建議開啟以手動完成「我不是機器人」）",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default=None,
        help="瀏覽器 profile 目錄路徑，保留登入/驗證狀態，可減少再次被 reCAPTCHA 阻擋",
    )
    
    args = parser.parse_args()
    
    # 執行應用程式
    app = Application()
    app.run(
        url=args.url,
        limit=args.limit,
        visible=args.visible,
        profile=args.profile,
    )


if __name__ == "__main__":
    main()
