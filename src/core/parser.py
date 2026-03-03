"""
評論解析器
"""
import time
import logging
from typing import Dict, Optional, Tuple, Set
from playwright.sync_api import Page, Locator
from ..config import SELECTORS

logger = logging.getLogger(__name__)


class ReviewParser:
    """評論解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.seen_ids: Set[str] = set()
        self.seen_content: Set[Tuple[str, str]] = set()
        self.total_parsed = 0
        self.total_skipped_no_text = 0
        self.total_skipped_duplicate = 0
    
    def parse_review(self, element: Locator, index: int) -> Tuple[Optional[Dict], Optional[str]]:
        """
        解析單一評論元素
        
        Args:
            element: 評論元素
            index: 索引（用於日誌）
            
        Returns:
            (評論資料字典, 跳過原因)
            - 成功: (dict, None)
            - 重複: (None, 'dup')
            - 無內文: (None, 'no_text')
            - 錯誤: (None, None)
        """
        try:
            self.total_parsed += 1
            
            # 1. 展開「更多」按鈕
            self._expand_more_button(element)
            
            # 2. 解析評分
            rating = self._parse_rating(element)
            
            # 3. 解析評論文字
            text = self._parse_text(element)
            if not text:
                logger.warning(f"跳過評論 index={index}：無評論內容")
                self.total_skipped_no_text += 1
                return (None, "no_text")
            
            # 4. 解析建議餐點
            suggested_dishes = self._parse_suggested_dishes(element)
            
            # 5. 檢查是否重複
            content_key = (text, suggested_dishes or "")
            if content_key in self.seen_content:
                self.total_skipped_duplicate += 1
                return (None, "dup")
            
            self.seen_content.add(content_key)
            
            # 6. 組合結果
            item = {"rating": rating, "text": text}
            if suggested_dishes:
                item["suggested_dishes"] = suggested_dishes
            
            return (item, None)
            
        except Exception as e:
            logger.exception(f"解析評論 index={index} 時發生錯誤: {e}")
            return (None, None)
    
    def _expand_more_button(self, element: Locator) -> None:
        """展開「更多」按鈕以顯示完整評論"""
        for more_selector in SELECTORS["more_button"]:
            try:
                btn = element.locator(more_selector).first
                if btn.count() > 0:
                    btn.click(timeout=1000)
                    time.sleep(0.3)
                    break
            except Exception:
                pass
    
    def _parse_rating(self, element: Locator) -> str:
        """解析評分"""
        rating = "N/A"
        for sel in SELECTORS["rating"]:
            re_el = element.locator(sel).first
            if re_el.count() > 0:
                rating = re_el.get_attribute("aria-label") or "N/A"
                break
        return rating
    
    def _parse_text(self, element: Locator) -> str:
        """解析評論文字"""
        text = ""
        for selector in SELECTORS["review_text"]:
            te = element.locator(selector).first
            if te.count() > 0:
                text = te.inner_text().strip()
                if text:
                    break
        return text
    
    def _parse_suggested_dishes(self, element: Locator) -> str:
        """解析建議的餐點"""
        suggested_dishes = ""
        try:
            rf_spans = element.locator(SELECTORS["suggested_dishes"])
            n_rf = rf_spans.count()
            for i in range(n_rf):
                if "建議的餐點" in (rf_spans.nth(i).inner_text() or ""):
                    if i + 1 < n_rf:
                        suggested_dishes = rf_spans.nth(i + 1).inner_text().strip()
                    break
        except Exception:
            pass
        return suggested_dishes
    
    def is_review_seen(self, review_id: str) -> bool:
        """檢查評論是否已處理過"""
        if review_id in self.seen_ids:
            return True
        self.seen_ids.add(review_id)
        return False
    
    def get_statistics(self) -> Dict[str, int]:
        """取得解析統計資訊"""
        return {
            "total_parsed": self.total_parsed,
            "total_skipped_no_text": self.total_skipped_no_text,
            "total_skipped_duplicate": self.total_skipped_duplicate,
        }
