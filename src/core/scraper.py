"""
Google Maps 評論爬蟲
"""
import logging
from typing import List, Dict, Optional
from .browser import BrowserManager, PageNavigator
from .maps_page import MapsPageHandler
from .parser import ReviewParser
from .scroller import ReviewScroller
from ..config import DEFAULT_HEADLESS

logger = logging.getLogger(__name__)


class GoogleMapsScraper:
    """Google Maps 評論爬蟲"""
    
    def __init__(
        self,
        headless: bool = DEFAULT_HEADLESS,
        user_data_dir: Optional[str] = None,
    ):
        """
        初始化爬蟲
        
        Args:
            headless: 是否使用無頭模式
            user_data_dir: 持久化 profile 目錄路徑
        """
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.should_stop = False  # 停止標誌
    
    def stop(self):
        """停止爬蟲"""
        self.should_stop = True
        logger.info("收到停止指令")
    
    def scrape_reviews(self, url: str, max_reviews: int = 50) -> List[Dict]:
        """
        爬取 Google Maps 評論
        
        Args:
            url: Google Maps 地點網址
            max_reviews: 預計爬取的評論數量
            
        Returns:
            評論資料列表，每項包含 text, rating 等欄位
        """
        logger.info(f"開始爬取: {url}")
        reviews_data = []
        
        try:
            with BrowserManager(self.headless, self.user_data_dir) as browser_manager:
                page = browser_manager.new_page()
                
                # 1. 導航到目標頁面
                PageNavigator.goto_url(page, url)
                
                # 2. 處理 Cookie 同意視窗
                PageNavigator.handle_cookie_consent(page)

                # 3. 優先從地點摘要區塊的「X 則 Google 評論」進入評論頁
                opened_from_summary = MapsPageHandler.open_reviews_from_summary(
                    page, headless=self.headless
                )

                # 4. 若找不到摘要中的「Google 評論」按鈕，才使用舊的評論分頁切換邏輯
                if not opened_from_summary:
                    MapsPageHandler.switch_to_reviews_tab(page, headless=self.headless)

                # 5. 設定排序為「最新」
                MapsPageHandler.sort_by_newest(page, headless=self.headless)
                
                # 6. 等待評論載入
                if not MapsPageHandler.wait_for_reviews(page, headless=self.headless):
                    logger.warning("未找到評論")
                    return []
                
                # 7. 滾動並收集評論
                parser = ReviewParser()
                scroller = ReviewScroller(page, parser)
                
                # 傳遞停止檢查函數給滾動器
                scroller.set_stop_check(lambda: self.should_stop)
                reviews_data = scroller.scroll_and_collect(max_reviews)
                
                if self.should_stop:
                    logger.info("爬蟲已被中斷")
                    return reviews_data  # 返回已收集的評論
                
        except Exception as e:
            logger.exception(f"爬取過程發生錯誤: {e}")
        
        logger.info(f"爬取完成，共取得 {len(reviews_data)} 則評論")
        return reviews_data
