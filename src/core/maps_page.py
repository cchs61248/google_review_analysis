"""
Google Maps 頁面操作工具
"""
import time
import logging
from playwright.sync_api import Page
from ..config import SELECTORS, TIMEOUT_CLICK, TIMEOUT_SHORT

logger = logging.getLogger(__name__)


class MapsPageHandler:
    """Google Maps 頁面處理器"""

    @staticmethod
    def _wait_for_page_ready(page: Page, headless: bool = False) -> None:
        """等待頁面完全就緒，無頭模式下給予更多時間"""
        page.wait_for_load_state("domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        wait_sec = 4 if headless else 2
        time.sleep(wait_sec)

    @staticmethod
    def switch_to_reviews_tab(page: Page, headless: bool = False) -> bool:
        """
        切換到評論分頁
        
        Args:
            page: Playwright 頁面對象
            headless: 是否為無頭模式
            
        Returns:
            是否成功切換
        """
        try:
            MapsPageHandler._wait_for_page_ready(page, headless)
            
            tab_clicked = False
            
            # 策略 A: role=tab 且 aria-label 包含關鍵字
            for label_part in SELECTORS["review_tab_labels"]:
                tabs = page.locator(f'[role="tab"][aria-label*="{label_part}"]')
                if tabs.count() > 0:
                    tab = tabs.first
                    tab.scroll_into_view_if_needed(timeout=3000)
                    time.sleep(0.5)
                    tab.click(timeout=TIMEOUT_CLICK, force=True)
                    tab_clicked = True
                    break
            
            # 策略 B: get_by_role
            if not tab_clicked:
                for tab_name in SELECTORS["review_tab_labels"]:
                    tab = page.get_by_role("tab", name=tab_name)
                    if tab.count() > 0:
                        tab.first.scroll_into_view_if_needed(timeout=3000)
                        tab.first.click(timeout=TIMEOUT_CLICK, force=True)
                        tab_clicked = True
                        break
            
            # 策略 C: 在 tablist 內找
            if not tab_clicked:
                tablist = page.locator('[role="tablist"]')
                if tablist.count() > 0:
                    for text in SELECTORS["review_tab_labels"]:
                        tab = tablist.get_by_role("tab", name=text)
                        if tab.count() > 0:
                            tab.first.scroll_into_view_if_needed(timeout=3000)
                            tab.first.click(timeout=TIMEOUT_CLICK, force=True)
                            tab_clicked = True
                            break
            
            # 策略 D: 文字完全匹配（最後手段）
            if not tab_clicked:
                for text in SELECTORS["review_tab_labels"]:
                    link = page.get_by_text(text, exact=True).first
                    if link.count() > 0:
                        link.scroll_into_view_if_needed(timeout=3000)
                        link.click(timeout=TIMEOUT_CLICK, force=True)
                        tab_clicked = True
                        break

            # 策略 E: 無頭模式下嘗試透過 URL 直接導向評論頁
            if not tab_clicked and headless:
                current_url = page.url
                if "/maps/place/" in current_url and "/reviews" not in current_url:
                    reviews_url = current_url.split("?")[0].rstrip("/") + "/reviews"
                    logger.info(f"無頭模式備援：直接導向評論 URL: {reviews_url[:80]}")
                    page.goto(reviews_url, timeout=30000)
                    MapsPageHandler._wait_for_page_ready(page, headless)
                    tab_clicked = True
            
            if tab_clicked:
                logger.info("成功切換到評論分頁")
                wait_sec = 3 if headless else 2
                time.sleep(wait_sec)
                return True
            else:
                logger.warning("無法自動切換到評論分頁")
                return False
                
        except Exception as e:
            logger.warning(f"切換評論分頁時發生錯誤: {e}")
            return False
    
    @staticmethod
    def sort_by_newest(page: Page, headless: bool = False) -> bool:
        """
        將評論排序設為「最新」
        
        Args:
            page: Playwright 頁面對象
            headless: 是否為無頭模式
            
        Returns:
            是否成功設定排序
        """
        try:
            # 無頭模式下多等一點讓元素渲染
            if headless:
                time.sleep(1)

            sort_btn = None
            for selector in [
                f'button:has-text("{SELECTORS["sort_button"]}")',
                f'[data-value="sort"] button',
                f'button[aria-label*="{SELECTORS["sort_button"]}"]',
            ]:
                loc = page.locator(selector)
                if loc.count() > 0:
                    sort_btn = loc.first
                    break

            if sort_btn is None:
                sort_btn_by_text = page.get_by_text(SELECTORS["sort_button"], exact=True)
                if sort_btn_by_text.count() > 0:
                    sort_btn = sort_btn_by_text.first

            if sort_btn is None:
                logger.warning("找不到排序按鈕")
                return False
            
            sort_btn.scroll_into_view_if_needed(timeout=3000)
            sort_btn.click(timeout=TIMEOUT_CLICK, force=True)
            time.sleep(1.5 if headless else 1)
            
            # 嘗試選擇「最新」選項
            newest_clicked = False
            for newest_text in SELECTORS["sort_newest"]:
                for selector in [
                    f'[role="menuitemradio"]:has-text("{newest_text}")',
                    f'div.mLuXec:has-text("{newest_text}")',
                    f'div[role="menuitemradio"] >> text={newest_text}',
                ]:
                    opt = page.locator(selector).first
                    if opt.count() > 0:
                        opt.scroll_into_view_if_needed(timeout=TIMEOUT_SHORT)
                        opt.click(timeout=3000, force=True)
                        newest_clicked = True
                        break
                if newest_clicked:
                    break
            
            # 備援方案
            if not newest_clicked:
                for newest_text in SELECTORS["sort_newest"]:
                    newest = page.get_by_role("menuitemradio", name=newest_text)
                    if newest.count() > 0:
                        newest.first.click(timeout=3000, force=True)
                        newest_clicked = True
                        break
            
            if newest_clicked:
                logger.info("成功設定排序為「最新」")
                time.sleep(2.5 if headless else 2)
                return True
            else:
                logger.warning("無法設定排序為「最新」")
                return False
                
        except Exception as e:
            logger.warning(f"設定排序時發生錯誤: {e}，使用預設排序")
            return False
    
    @staticmethod
    def wait_for_reviews(page: Page, headless: bool = False) -> bool:
        """
        等待評論區塊載入
        
        Args:
            page: Playwright 頁面對象
            headless: 是否為無頭模式
            
        Returns:
            是否成功載入評論
        """
        from ..config import TIMEOUT_SELECTOR
        
        timeout = TIMEOUT_SELECTOR * 2 if headless else TIMEOUT_SELECTOR
        
        try:
            page.wait_for_selector(SELECTORS["review_item"], timeout=timeout)
            logger.info("評論區塊已載入")
            return True
        except Exception:
            # 備援：嘗試其他評論容器選擇器
            for fallback in ['div.jftiEf', 'div[jsaction*="review"]', 'div.fontBodyMedium']:
                try:
                    page.wait_for_selector(fallback, timeout=5000)
                    logger.info(f"評論區塊已載入（備援選擇器: {fallback}）")
                    return True
                except Exception:
                    continue
            logger.warning("未找到評論區塊")
            return False
