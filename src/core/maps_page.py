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
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        
        # 無頭模式下（尤其是 Railway）需要更多時間讓 JavaScript 渲染
        wait_sec = 5 if headless else 2
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
            
            # 先檢查是否已經在評論頁面
            current_url = page.url
            if "/reviews" in current_url or "reviews" in current_url.lower():
                logger.info("已在評論頁面，無需切換")
                time.sleep(2)
                return True
            
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
            
            # 策略 D: 文字完全匹配
            if not tab_clicked:
                for text in SELECTORS["review_tab_labels"]:
                    link = page.get_by_text(text, exact=True).first
                    if link.count() > 0:
                        link.scroll_into_view_if_needed(timeout=3000)
                        link.click(timeout=TIMEOUT_CLICK, force=True)
                        tab_clicked = True
                        break
                        
            # 策略 E: 特殊 class 選擇器 (針對手機版或新版無頭介面)
            if not tab_clicked:
                for text in SELECTORS["review_tab_labels"]:
                    # 尋找 span 且包含 class aSAiSd 並有指定文字，或其父元素
                    for selector in [
                        f'div:has(span.aSAiSd:has-text("{text}"))',
                        f'span.aSAiSd:has-text("{text}")',
                        f'//div[contains(@class, "aep93e")]//span[text()="{text}"]',
                        f'div.aep93e:has-text("{text}")' # 根據最新的 log 結構新增
                    ]:
                        element = page.locator(selector)
                        if element.count() > 0:
                            # 對於這個特定的 div，可能需要點擊它內部可點擊的部分，或者直接點擊 div
                            element.first.scroll_into_view_if_needed(timeout=3000)
                            element.first.click(timeout=TIMEOUT_CLICK, force=True)
                            tab_clicked = True
                            break
                    if tab_clicked:
                        break
            
            # 策略 F: 尋找任何包含「評論」文字的可點擊 div
            if not tab_clicked:
                for text in SELECTORS["review_tab_labels"]:
                    # 在特定情境下（特別是行動版或 headless 時），按鈕可能只是一個普通的 div
                    elements = page.locator(f'div:has-text("{text}")')
                    count = elements.count()
                    for i in range(count):
                        el = elements.nth(i)
                        # 檢查這個 div 是不是按鈕或分頁標籤（透過 class name 特徵或是 aria-role 等判斷太嚴格，
                        # 我們可以嘗試尋找 class name 中包含 button 或 tab 相關的特徵，或者直接點擊最內層的元素）
                        # 為了安全起見，我們只嘗試點擊那些相對獨立的區域
                        try:
                            # 檢查它是否可見且可點擊
                            if el.is_visible():
                                class_name = el.get_attribute("class") or ""
                                # 常見的點擊元素 class 可能會有的特徵
                                if "tab" in class_name.lower() or "button" in class_name.lower() or "aep93e" in class_name:
                                    el.scroll_into_view_if_needed(timeout=1000)
                                    el.click(timeout=2000, force=True)
                                    tab_clicked = True
                                    break
                        except Exception:
                            continue
                    if tab_clicked:
                        break

            # 策略 F: 無頭模式下嘗試透過 URL 直接導向評論頁
            if not tab_clicked and headless:
                if "/maps/place/" in current_url:
                    # 移除 query string 並添加 /reviews
                    base_url = current_url.split("?")[0].rstrip("/")
                    reviews_url = base_url + "/reviews"
                    logger.info(f"無頭模式備援：直接導向評論 URL: {reviews_url[:80]}")
                    page.goto(reviews_url, timeout=30000)
                    MapsPageHandler._wait_for_page_ready(page, headless)
                    tab_clicked = True
            
            if tab_clicked:
                logger.info("成功切換到評論分頁")
                wait_sec = 4 if headless else 2
                time.sleep(wait_sec)
                return True
            else:
                logger.warning("無法自動切換到評論分頁")
                # 在無頭模式下，即使找不到 tab，也嘗試繼續（可能頁面結構不同）
                if headless:
                    logger.info("無頭模式：嘗試繼續處理...")
                    time.sleep(3)
                    return True
                return False
                
        except Exception as e:
            logger.warning(f"切換評論分頁時發生錯誤: {e}")
            # 無頭模式下容錯處理
            if headless:
                logger.info("無頭模式：忽略錯誤，嘗試繼續...")
                time.sleep(3)
                return True
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
                time.sleep(2)

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
                # 無頭模式下，即使找不到排序按鈕也繼續（可能預設就是最新排序）
                if headless:
                    logger.info("無頭模式：繼續使用預設排序...")
                    return True
                return False
            
            sort_btn.scroll_into_view_if_needed(timeout=3000)
            sort_btn.click(timeout=TIMEOUT_CLICK, force=True)
            time.sleep(2 if headless else 1)
            
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
                time.sleep(3 if headless else 2)
                return True
            else:
                logger.warning("無法設定排序為「最新」")
                # 無頭模式下容錯
                if headless:
                    logger.info("無頭模式：繼續使用預設排序...")
                    return True
                return False
                
        except Exception as e:
            logger.warning(f"設定排序時發生錯誤: {e}，使用預設排序")
            return headless  # 無頭模式下返回 True 以繼續執行
    
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
