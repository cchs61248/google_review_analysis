"""
背景工作執行緒
"""
import logging
from typing import Optional, List, Dict

from PySide6.QtCore import QObject, Signal

from src.core import GoogleMapsScraper
from src.services import ReviewAnalyzer


logger = logging.getLogger(__name__)


class ScraperWorker(QObject):
    """爬蟲工作執行緒（SerpApi）"""

    progress = Signal(int, str)
    log = Signal(str)
    reviews = Signal(list)
    formatted_reviews = Signal(str)
    analysis = Signal(str)
    finished = Signal()
    error = Signal(str)

    def __init__(self, url: str, limit: int):
        super().__init__()
        self.url = url
        self.limit = limit
        self.should_stop = False
        self.scraper: Optional[GoogleMapsScraper] = None

    def stop(self):
        self.should_stop = True
        self.log.emit("收到停止指令，正在中斷任務...")
        if self.scraper:
            try:
                self.scraper.stop()
            except Exception:
                pass

    def run(self):
        try:
            self.progress.emit(10, "準備取得評論...")
            self.log.emit(f"原始網址: {self.url}")

            if self.should_stop:
                self.error.emit("使用者中斷任務")
                return

            self.progress.emit(25, "正在連線 SerpApi...")
            self.log.emit("正在透過 SerpApi 取得 Google Maps 評論...")

            try:
                self.scraper = GoogleMapsScraper()
            except ValueError as e:
                self.error.emit(str(e))
                return

            if self.should_stop:
                self.error.emit("使用者中斷任務")
                return

            self.progress.emit(35, f"取得評論中（目標 {self.limit} 則）...")
            self.log.emit(f"目標數量: {self.limit} 則")

            reviews = self.scrape_with_cancel_check(self.url, self.limit)

            if self.should_stop:
                self.error.emit("使用者中斷任務")
                return

            if not reviews:
                self.error.emit(
                    "未找到評論或取得失敗。請確認網址、SERPAPI_API_KEY 與 SerpApi 額度。"
                )
                return

            self.progress.emit(70, f"成功取得 {len(reviews)} 則評論")
            self.log.emit(f"✓ 已收集 {len(reviews)} 則評論")

            formatted_text = self._format_reviews_for_display(reviews)
            self.reviews.emit(reviews)
            self.formatted_reviews.emit(formatted_text)

            if self.should_stop:
                self.error.emit("使用者中斷任務")
                return

            self.progress.emit(80, "正在進行 AI 分析...")
            self.log.emit("正在呼叫 AI 模型進行分析...")

            analyzer = ReviewAnalyzer()
            analysis_result = analyzer.analyze_formatted_text(formatted_text)

            if self.should_stop:
                return

            self.progress.emit(90, "分析完成")
            self.log.emit("✓ AI 分析完成")
            self.analysis.emit(analysis_result)
            self.progress.emit(100, "所有任務完成")
            self.log.emit("=" * 60)
            self.log.emit("所有任務已完成！")
            self.finished.emit()

        except ValueError as e:
            error_msg = f"配置錯誤: {str(e)}\n請檢查 .env（OPENAI_API_KEY、SERPAPI_API_KEY）"
            self.log.emit(f"✗ {error_msg}")
            self.error.emit(error_msg)
        except Exception as e:
            error_msg = f"發生未預期的錯誤: {str(e)}"
            self.log.emit(f"✗ {error_msg}")
            logger.exception("Worker 執行失敗")
            self.error.emit(error_msg)

    def _format_reviews_for_display(self, reviews: List[Dict]) -> str:
        import re

        lines = []
        lines.append(f"共收集到 {len(reviews)} 則評論\n")
        lines.append("=" * 60 + "\n")

        for i, review in enumerate(reviews, 1):
            lines.append(f"評論 #{i}")
            rating = review.get("rating", "N/A")
            if isinstance(rating, str):
                match = re.search(r"(\d+)", str(rating))
                if match:
                    rating_num = int(match.group(1))
                    lines.append(f"評分: {'⭐' * rating_num} ({rating})")
                else:
                    lines.append(f"評分: {rating}")
            else:
                lines.append(f"評分: {'⭐' * int(rating)}")
            text = review.get("text", "無文字內容")
            lines.append(f"內容: {text}")
            suggested_dishes = review.get("suggested_dishes")
            if suggested_dishes:
                dishes = (
                    ", ".join(suggested_dishes)
                    if isinstance(suggested_dishes, list)
                    else suggested_dishes
                )
                lines.append(f"推薦餐點: {dishes}")
            lines.append("-" * 60 + "\n")
        return "\n".join(lines)

    def scrape_with_cancel_check(self, url: str, max_reviews: int) -> list:
        try:
            if self.should_stop:
                return []
            return self.scraper.scrape_reviews(url, max_reviews=max_reviews) or []
        except KeyboardInterrupt:
            self.log.emit("爬取被鍵盤中斷")
            return []
        except Exception:
            if self.should_stop or (self.scraper and self.scraper.should_stop):
                self.log.emit("取得評論過程中收到停止信號")
                return []
            raise
