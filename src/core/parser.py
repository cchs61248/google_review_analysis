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
            # 若有「建議的餐點」，一併加入評論文字中（同時保留欄位以相容既有流程）
            merged_text = text
            if suggested_dishes:
                merged_text = f"{text}\n建議的餐點：{suggested_dishes}".strip()

            item = {"rating": rating, "text": merged_text}
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
                # 對於 OA1nbd 結構，需要排除只有「餐點/服務/氣氛」評分而沒有實際文字評論的情況
                if selector == "div.OA1nbd":
                    try:
                        # 透過 JS 取得移除評分區塊 (.zMjRQd) 後剩餘的文字內容
                        text_main = te.evaluate(
                            """el => {
                                const clone = el.cloneNode(true);
                                const blocks = clone.querySelectorAll('.zMjRQd');
                                blocks.forEach(b => b.remove());
                                return clone.textContent.trim();
                            }"""
                        ) or ""
                        text = text_main.strip()
                    except Exception:
                        text = te.inner_text().strip()
                else:
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

        # 新版結構：<div style="font-weight: 500;">建議的餐點</div>
        #          <div aria-label="香蕉花沙拉 258, 洛葉炒牛肉 298">香蕉花沙拉 258, 洛葉炒牛肉 298</div>
        if not suggested_dishes:
            try:
                # 盡量限制在評論內容區塊內，避免抓到「回應」工具列的提示文字
                label_div = element.locator(
                    'div.OA1nbd div[style*="font-weight: 500"]:has-text("建議的餐點")'
                ).first
                if label_div.count() > 0:
                    value = label_div.evaluate(
                        """el => {
                            const next = el.nextElementSibling;
                            if (!next) return '';
                            const raw = (next.getAttribute('aria-label') || next.textContent || '').trim();
                            return raw;
                        }"""
                    ) or ""

                    # 清理常見的雜訊字串
                    value = (value or "").replace("_", "").strip()
                    if value and "懸停即可回應" not in value:
                        suggested_dishes = value
            except Exception:
                pass

        # 最後再做一次防呆：避免把「回應」提示或空值當成餐點
        suggested_dishes = (suggested_dishes or "").replace("_", "").strip()
        if not suggested_dishes or "懸停即可回應" in suggested_dishes:
            return ""
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
