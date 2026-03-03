"""
評論滾動載入器
"""
import time
import logging
from typing import List, Dict
from playwright.sync_api import Page
from .parser import ReviewParser
from ..config import (
    SELECTORS,
    MIN_SCROLL_ROUNDS,
    NO_CHANGE_THRESHOLD,
    SCROLL_WAIT_TIME,
)

logger = logging.getLogger(__name__)


class ReviewScroller:
    """評論滾動載入器"""
    
    def __init__(self, page: Page, parser: ReviewParser):
        """
        初始化滾動載入器
        
        Args:
            page: Playwright 頁面對象
            parser: 評論解析器
        """
        self.page = page
        self.parser = parser
        self.stop_check = None  # 停止檢查函數
    
    def set_stop_check(self, check_func):
        """
        設定停止檢查函數
        
        Args:
            check_func: 返回 True 表示應該停止的函數
        """
        self.stop_check = check_func
    
    def scroll_and_collect(self, max_reviews: int) -> List[Dict]:
        """
        滾動並收集評論
        
        Args:
            max_reviews: 最大收集數量
            
        Returns:
            評論資料列表
        """
        logger.info(f"開始滾動並收集最多 {max_reviews} 則評論")
        
        reviews_data = []
        no_change_rounds = 0
        scroll_rounds = 0
        
        while len(reviews_data) < max_reviews:
            # 檢查是否應該停止
            if self.stop_check and self.stop_check():
                logger.info(f"收到停止信號，已收集 {len(reviews_data)} 則評論")
                break
            
            # 滾動
            self._scroll_review_area()
            scroll_rounds += 1
            time.sleep(SCROLL_WAIT_TIME)
            
            # 再次檢查停止（滾動後）
            if self.stop_check and self.stop_check():
                logger.info(f"收到停止信號，已收集 {len(reviews_data)} 則評論")
                break
            
            # 解析當前可見的評論
            review_elements = self.page.locator(SELECTORS["review_item"]).all()
            added_this_round = 0
            
            for idx, element in enumerate(review_elements):
                if len(reviews_data) >= max_reviews:
                    break
                
                # 檢查是否已處理過此評論
                review_id = element.get_attribute("data-review-id")
                if review_id and self.parser.is_review_seen(review_id):
                    continue
                
                # 解析評論
                item, skip_reason = self.parser.parse_review(element, idx)
                if item:
                    item["number"] = len(reviews_data) + 1
                    reviews_data.append(item)
                    added_this_round += 1
            
            # 檢查是否需要提前結束
            if added_this_round == 0:
                no_change_rounds += 1
                if scroll_rounds >= MIN_SCROLL_ROUNDS and no_change_rounds >= NO_CHANGE_THRESHOLD:
                    logger.info("已滾動多輪且無新評論，提前結束")
                    break
            else:
                no_change_rounds = 0
            
            if len(reviews_data) >= max_reviews:
                break
        
        # 確保編號正確
        reviews_data = reviews_data[:max_reviews]
        for i, item in enumerate(reviews_data, start=1):
            item["number"] = i
        
        # 記錄統計資訊
        stats = self.parser.get_statistics()
        logger.info(
            f"收集完成：共解析 {stats['total_parsed']} 則，"
            f"成功 {len(reviews_data)} 則，"
            f"無內文跳過 {stats['total_skipped_no_text']} 則，"
            f"重複跳過 {stats['total_skipped_duplicate']} 則"
        )
        
        return reviews_data
    
    def _scroll_review_area(self) -> None:
        """滾動評論區域"""
        self.page.evaluate("""() => {
            const el = document.querySelector('div[data-review-id]');
            if (!el) return;
            let p = el.parentElement;
            while (p && p !== document.body) {
                const s = getComputedStyle(p);
                if (/(auto|scroll)/.test(s.overflow + s.overflowY)) {
                    p.scrollTop = p.scrollHeight;
                    return;
                }
                p = p.parentElement;
            }
            window.scrollBy(0, 600);
        }""")
