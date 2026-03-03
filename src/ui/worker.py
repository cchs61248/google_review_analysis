"""
背景工作執行緒
"""
import logging
from typing import Optional, List, Dict
from PySide6.QtCore import QObject, Signal

from src.utils import resolve_short_url
from src.core import GoogleMapsScraper
from src.services import ReviewAnalyzer


logger = logging.getLogger(__name__)


class ScraperWorker(QObject):
    """爬蟲工作執行緒"""
    
    # 信號定義
    progress = Signal(int, str)  # 進度值, 狀態訊息
    log = Signal(str)  # 日誌訊息
    reviews = Signal(list)  # 評論資料
    formatted_reviews = Signal(str)  # 格式化的評論文字（用於 AI 分析）
    analysis = Signal(str)  # 分析報告
    finished = Signal()  # 完成
    error = Signal(str)  # 錯誤訊息
    
    def __init__(self, url: str, limit: int, visible: bool, profile: Optional[str]):
        super().__init__()
        self.url = url
        self.limit = limit
        self.visible = visible
        self.profile = profile
        self.should_stop = False
        self.scraper: Optional[GoogleMapsScraper] = None
    
    def stop(self):
        """停止執行"""
        self.should_stop = True
        self.log.emit("收到停止指令，正在中斷任務...")
        
        # 如果爬蟲正在運行，通知它停止
        if self.scraper:
            try:
                self.scraper.stop()
            except:
                pass
    
    def run(self):
        """執行爬蟲任務"""
        try:
            # 步驟 1: 解析網址 (10%)
            self.progress.emit(10, "正在解析網址...")
            self.log.emit(f"原始網址: {self.url}")
            
            full_url = resolve_short_url(self.url)
            self.log.emit(f"完整網址: {full_url}")
            
            if self.should_stop:
                self.log.emit("任務已在解析階段被中斷")
                self.error.emit("使用者中斷任務")
                return
            
            # 步驟 2: 初始化爬蟲 (20%)
            self.progress.emit(20, "正在初始化瀏覽器...")
            self.log.emit("正在啟動 Playwright 瀏覽器...")
            
            self.scraper = GoogleMapsScraper(
                headless=not self.visible,
                user_data_dir=self.profile,
            )
            
            if self.should_stop:
                self.log.emit("任務已在初始化階段被中斷")
                self.error.emit("使用者中斷任務")
                return
            
            # 步驟 3: 爬取評論 (20% -> 70%)
            self.progress.emit(30, f"正在爬取評論（目標: {self.limit} 則）...")
            self.log.emit(f"開始爬取，目標數量: {self.limit} 則")
            self.log.emit("此過程可能需要幾分鐘，請耐心等待...")
            
            # 在爬取過程中定期檢查停止標誌
            reviews = self.scrape_with_cancel_check(full_url, self.limit)
            
            if self.should_stop:
                self.log.emit("任務已在爬取階段被中斷")
                self.error.emit("使用者中斷任務")
                return
            
            if not reviews:
                self.error.emit("未找到評論或爬取失敗。請確認網址是否正確。")
                return
            
            self.progress.emit(70, f"成功爬取 {len(reviews)} 則評論")
            self.log.emit(f"✓ 成功收集到 {len(reviews)} 則評論")
            
            # 格式化評論為文字（與 UI 顯示相同的格式）
            formatted_text = self._format_reviews_for_display(reviews)
            
            # 發送評論資料和格式化文字
            self.reviews.emit(reviews)
            self.formatted_reviews.emit(formatted_text)
            
            if self.should_stop:
                self.log.emit("任務已在準備分析階段被中斷")
                self.error.emit("使用者中斷任務")
                return
            
            # 步驟 4: 分析評論 (70% -> 90%)
            self.progress.emit(80, "正在進行 AI 分析...")
            self.log.emit("正在呼叫 AI 模型進行分析...")
            
            # 使用格式化的文字進行分析
            analyzer = ReviewAnalyzer()
            analysis_result = analyzer.analyze_formatted_text(formatted_text)
            
            if self.should_stop:
                return
            
            self.progress.emit(90, "分析完成")
            self.log.emit("✓ AI 分析完成")
            
            # 發送分析結果
            self.analysis.emit(analysis_result)
            
            # 步驟 5: 完成 (100%)
            self.progress.emit(100, "所有任務完成")
            self.log.emit("=" * 60)
            self.log.emit("所有任務已完成！")
            self.finished.emit()
            
        except ValueError as e:
            error_msg = f"配置錯誤: {str(e)}\n請檢查 .env 檔案是否已設定 OPENAI_API_KEY"
            self.log.emit(f"✗ {error_msg}")
            self.error.emit(error_msg)
            
        except Exception as e:
            error_msg = f"發生未預期的錯誤: {str(e)}"
            self.log.emit(f"✗ {error_msg}")
            logger.exception("Worker 執行失敗")
            self.error.emit(error_msg)
        
        finally:
            # 清理資源
            if self.scraper:
                try:
                    # 這裡可以加入清理爬蟲資源的邏輯
                    pass
                except:
                    pass
    
    def _format_reviews_for_display(self, reviews: List[Dict]) -> str:
        """
        將評論格式化為與 UI 顯示相同的文字格式
        
        Args:
            reviews: 評論資料列表
            
        Returns:
            格式化的評論文字
        """
        import re
        
        lines = []
        lines.append(f"共收集到 {len(reviews)} 則評論\n")
        lines.append("=" * 60 + "\n")
        
        for i, review in enumerate(reviews, 1):
            lines.append(f"評論 #{i}")
            
            # 處理評分
            rating = review.get('rating', 'N/A')
            if isinstance(rating, str):
                match = re.search(r'(\d+)', rating)
                if match:
                    rating_num = int(match.group(1))
                    lines.append(f"評分: {'⭐' * rating_num} ({rating})")
                else:
                    lines.append(f"評分: {rating}")
            else:
                lines.append(f"評分: {'⭐' * int(rating)}")
            
            # 顯示評論內容
            text = review.get('text', '無文字內容')
            lines.append(f"內容: {text}")
            
            # 處理推薦餐點
            suggested_dishes = review.get('suggested_dishes')
            if suggested_dishes:
                if isinstance(suggested_dishes, list):
                    dishes = ", ".join(suggested_dishes)
                else:
                    dishes = suggested_dishes
                lines.append(f"推薦餐點: {dishes}")
            
            lines.append("-" * 60 + "\n")
        
        return "\n".join(lines)
    
    def scrape_with_cancel_check(self, url: str, max_reviews: int) -> list:
        """
        執行爬取並定期檢查取消標誌
        
        Args:
            url: 目標網址
            max_reviews: 最大評論數
            
        Returns:
            評論列表（如果被取消則返回空列表）
        """
        try:
            if self.should_stop:
                return []
            
            # 直接調用爬蟲，爬蟲內部會檢查停止標誌
            reviews = self.scraper.scrape_reviews(url, max_reviews=max_reviews)
            return reviews if reviews else []
            
        except KeyboardInterrupt:
            self.log.emit("爬取被鍵盤中斷")
            return []
        except Exception as e:
            if self.should_stop or (self.scraper and self.scraper.should_stop):
                self.log.emit("爬取過程中收到停止信號")
                return []
            raise
