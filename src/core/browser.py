"""
瀏覽器操作相關工具
"""
import time
import logging
from typing import Optional
from playwright.sync_api import Page, sync_playwright
from ..config import (
    BROWSER_ARGS,
    BROWSER_ARGS_HEADLESS,
    DEFAULT_HEADLESS,
    DEFAULT_LOCALE,
    DEFAULT_VIEWPORT,
    DEFAULT_USER_AGENT,
    TIMEOUT_PAGE_LOAD,
    TIMEOUT_SHORT,
)

logger = logging.getLogger(__name__)

# 隱藏 webdriver 特徵的初始化腳本
_STEALTH_SCRIPT = """
() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    Object.defineProperty(navigator, 'languages', { get: () => ['zh-TW', 'zh', 'en-US', 'en'] });
    window.chrome = { runtime: {} };
}
"""


class BrowserManager:
    """瀏覽器管理器"""

    def __init__(self, headless: bool = DEFAULT_HEADLESS, user_data_dir: Optional[str] = None):
        """
        初始化瀏覽器管理器

        Args:
            headless: 是否使用無頭模式
            user_data_dir: 持久化 profile 目錄路徑
        """
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.playwright = None
        self.browser = None
        self.context = None

    def __enter__(self):
        """進入上下文管理器"""
        self.playwright = sync_playwright().start()

        args = BROWSER_ARGS_HEADLESS if self.headless else BROWSER_ARGS

        if self.user_data_dir:
            import os
            os.makedirs(self.user_data_dir, exist_ok=True)
            self.context = self.playwright.chromium.launch_persistent_context(
                self.user_data_dir,
                headless=self.headless,
                locale=DEFAULT_LOCALE,
                viewport=DEFAULT_VIEWPORT,
                user_agent=DEFAULT_USER_AGENT,
                args=args,
            )
            self.browser = None
        else:
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=args,
            )
            self.context = self.browser.new_context(
                locale=DEFAULT_LOCALE,
                viewport=DEFAULT_VIEWPORT,
                user_agent=DEFAULT_USER_AGENT,
            )

        # 注入反偵測腳本（對所有後續頁面生效）
        self.context.add_init_script(_STEALTH_SCRIPT)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def new_page(self) -> Page:
        """創建新頁面"""
        if self.context.pages:
            return self.context.pages[0]
        return self.context.new_page()


class PageNavigator:
    """頁面導航工具"""

    @staticmethod
    def goto_url(page: Page, url: str) -> None:
        """
        導航到指定 URL

        Args:
            page: Playwright 頁面對象
            url: 目標 URL
        """
        logger.info(f"導航至: {url}")

        # 驗證 URL 是否有效
        if not url or not url.startswith("http"):
            raise ValueError(f"無效的 URL: {url}")

        try:
            page.goto(url, timeout=TIMEOUT_PAGE_LOAD, wait_until="domcontentloaded")
        except Exception as e:
            logger.error(f"導航失敗: {e}")
            raise

    @staticmethod
    def handle_cookie_consent(page: Page) -> None:
        """處理 Cookie 同意視窗"""
        try:
            page.get_by_role("button", name="全部接受").click(timeout=TIMEOUT_SHORT)
            logger.info("已處理 Cookie 同意視窗")
        except Exception:
            pass

    @staticmethod
    def redirect_from_search_to_maps(page: Page) -> None:
        """
        如果當前在搜尋結果頁，自動跳轉到 Maps 商家頁

        Args:
            page: Playwright 頁面對象
        """
        from urllib.parse import urljoin, urlparse, parse_qs
        import urllib.parse

        current_url = page.url
        if "google.com/search" not in current_url and "google.com.tw/search" not in current_url:
            return

        try:
            maps_url = None

            # 優先找商家專頁連結
            for selector in [
                'a[href*="/maps/place/"]',
                'a[href*="google.com/maps"]',
                'a[data-url*="/maps/place/"]'
            ]:
                loc = page.locator(selector)
                if loc.count() > 0:
                    maps_url = loc.first.get_attribute("href") or loc.first.get_attribute("data-url")
                    if maps_url:
                        break
            
            if maps_url and "/maps/" in maps_url:
                maps_url_abs = urljoin(current_url, maps_url)
                logger.info(f"從搜尋結果頁跳轉到 Maps: {maps_url_abs}")
                page.goto(maps_url_abs, timeout=TIMEOUT_PAGE_LOAD)
                time.sleep(3)
                return

            # 備援方案：如果找不到地圖連結，提取搜尋關鍵字並直接構造 Google Maps 搜尋網址
            logger.info("未找到直接的地圖連結，嘗試從 URL 提取查詢參數...")
            parsed_url = urlparse(current_url)
            query_params = parse_qs(parsed_url.query)

            # 從你的 Log 發現，某些 Google 搜尋的關鍵字是放在 q 裡面
            # 另外也可以嘗試抓取搜尋框的內容
            query_str = None
            if 'q' in query_params:
                query_str = query_params['q'][0]
            else:
                # 嘗試從畫面的搜尋框抓取
                search_box = page.locator('textarea[name="q"], input[name="q"]')
                if search_box.count() > 0:
                    query_str = search_box.first.input_value()

            if query_str:
                # 將關鍵字編碼並構造 maps search URL
                encoded_query = urllib.parse.quote(query_str)
                maps_search_url = f"https://www.google.com/maps/search/{encoded_query}"

                logger.info(f"透過關鍵字跳轉至 Maps: {maps_search_url[:80]}...")
                page.goto(maps_search_url, timeout=TIMEOUT_PAGE_LOAD)

                # 等待跳轉完成並可能是搜尋結果列表，或是直接進入店家
                # 若進入搜尋結果列表，點擊第一個結果
                time.sleep(3)
                if "/maps/search/" in page.url:
                    logger.info("嘗試點擊第一個搜尋結果")
                    first_result = page.locator('a[href*="/maps/place/"]').first
                    if first_result.count() > 0:
                        first_result.click(timeout=TIMEOUT_CLICK)
                        time.sleep(3)

                return

            logger.warning("無法從搜尋結果頁找到跳轉 Maps 的方法，且無查詢參數。")

        except Exception as e:
            logger.warning(f"無法從搜尋結果頁跳轉: {e}")
