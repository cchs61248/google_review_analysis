"""
主視窗 UI
"""
import logging
from typing import Optional, List, Dict
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QSpinBox, QPushButton, QTextEdit,
    QLabel, QGroupBox, QProgressBar,
    QTabWidget, QMessageBox, QSplitter,
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSettings
from PySide6.QtGui import QFont, QTextCursor, QIcon

from .theme import ThemeManager
from .worker import ScraperWorker


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """主視窗"""
    
    def __init__(self):
        super().__init__()
        self.worker: Optional[ScraperWorker] = None
        self.thread: Optional[QThread] = None
        self.is_dark_theme = True
        self.settings = QSettings("Google Maps Scraper", "Google Maps 評論分析器")
        
        self.init_ui()
        self.load_settings()
        self.apply_theme()
    
    def init_ui(self):
        """初始化使用者介面"""
        self.setWindowTitle("Google Maps 評論分析器")
        self.setMinimumSize(1200, 800)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主佈局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 標題與主題切換
        title_layout = QHBoxLayout()
        title_label = QLabel("🗺️ Google Maps 評論分析器")
        title_label.setObjectName("titleLabel")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        self.theme_button = QPushButton("🌙 深色模式")
        self.theme_button.setMaximumWidth(150)
        self.theme_button.clicked.connect(self.toggle_theme)
        title_layout.addWidget(self.theme_button)
        
        main_layout.addLayout(title_layout)
        
        # 分隔器（上下兩部分）
        splitter = QSplitter(Qt.Vertical)
        
        # === 上半部：輸入與控制 ===
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setSpacing(12)
        
        # 輸入區
        input_group = QGroupBox("📍 餐廳資訊")
        input_layout = QVBoxLayout()
        
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Google Maps 網址:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("請輸入 Google Maps 餐廳網址（支援短網址）")
        url_layout.addWidget(self.url_input)
        input_layout.addLayout(url_layout)
        
        limit_layout = QHBoxLayout()
        limit_layout.addWidget(QLabel("評論數量:"))
        self.limit_spinbox = QSpinBox()
        self.limit_spinbox.setMinimum(1)
        self.limit_spinbox.setMaximum(500)
        self.limit_spinbox.setValue(30)
        self.limit_spinbox.setSingleStep(1)  # 設定每次增減的步進值
        self.limit_spinbox.setSuffix(" 則")
        self.limit_spinbox.setMaximumWidth(150)
        self.limit_spinbox.setButtonSymbols(QSpinBox.UpDownArrows)  # 確保顯示上下箭頭
        limit_layout.addWidget(self.limit_spinbox)
        limit_layout.addStretch()
        input_layout.addLayout(limit_layout)
        
        input_group.setLayout(input_layout)
        top_layout.addWidget(input_group)
        
        settings_group = QGroupBox("⚙️ 說明")
        settings_layout = QVBoxLayout()
        hint = QLabel(
            "評論資料來自 SerpApi（請在 .env 設定 SERPAPI_API_KEY）。\n"
            "AI 分析需設定 OPENAI_API_KEY。"
        )
        hint.setWordWrap(True)
        settings_layout.addWidget(hint)
        settings_group.setLayout(settings_layout)
        top_layout.addWidget(settings_group)
        
        # 控制按鈕
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.start_button = QPushButton("▶ 開始分析")
        self.start_button.setMinimumHeight(45)
        self.start_button.setMinimumWidth(150)
        self.start_button.clicked.connect(self.start_scraping)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("⏹ 停止")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setMinimumHeight(45)
        self.stop_button.setMinimumWidth(120)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_scraping)
        button_layout.addWidget(self.stop_button)
        
        button_layout.addStretch()
        top_layout.addLayout(button_layout)
        
        # 進度條
        progress_layout = QVBoxLayout()
        self.status_label = QLabel("就緒")
        self.status_label.setObjectName("statusLabel")
        progress_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        top_layout.addLayout(progress_layout)
        
        splitter.addWidget(top_widget)
        
        # === 下半部：結果顯示 ===
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        result_group = QGroupBox("📊 執行結果")
        result_layout = QVBoxLayout()
        
        # 分頁顯示
        self.tab_widget = QTabWidget()
        
        # 日誌分頁
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        self.tab_widget.addTab(self.log_text, "📝 執行日誌")
        
        # 評論分頁
        self.review_text = QTextEdit()
        self.review_text.setReadOnly(True)
        self.tab_widget.addTab(self.review_text, "💬 評論內容")
        
        # 分析報告分頁
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.tab_widget.addTab(self.analysis_text, "📈 AI 分析報告")
        
        result_layout.addWidget(self.tab_widget)
        
        # 清除按鈕
        clear_button_layout = QHBoxLayout()
        clear_button_layout.addStretch()
        self.clear_button = QPushButton("🗑 清除結果")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.setMaximumWidth(150)
        self.clear_button.clicked.connect(self.clear_results)
        clear_button_layout.addWidget(self.clear_button)
        result_layout.addLayout(clear_button_layout)
        
        result_group.setLayout(result_layout)
        bottom_layout.addWidget(result_group)
        
        splitter.addWidget(bottom_widget)
        
        # 設定分隔器比例
        splitter.setSizes([400, 400])
        
        main_layout.addWidget(splitter)
        
        # 狀態列
        self.statusBar().showMessage("就緒")
    
    def apply_theme(self):
        """套用主題"""
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        
        if self.is_dark_theme:
            ThemeManager.apply_dark_theme(app)
            self.theme_button.setText("☀️ 淺色模式")
        else:
            ThemeManager.apply_light_theme(app)
            self.theme_button.setText("🌙 深色模式")
    
    def toggle_theme(self):
        """切換主題"""
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()
    
    def start_scraping(self):
        """開始爬取"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "輸入錯誤", "請輸入 Google Maps 網址")
            return
        
        # 準備參數
        limit = self.limit_spinbox.value()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.url_input.setEnabled(False)
        self.limit_spinbox.setEnabled(False)
        
        # 清除舊結果
        self.clear_results()
        
        # 創建工作執行緒
        self.thread = QThread()
        self.worker = ScraperWorker(url, limit)
        self.worker.moveToThread(self.thread)
        
        # 連接信號
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.append_log)
        self.worker.reviews.connect(self.display_reviews)
        self.worker.analysis.connect(self.display_analysis)
        self.worker.finished.connect(self.scraping_finished)
        self.worker.error.connect(self.scraping_error)
        
        # 啟動執行緒
        self.thread.start()
        
        self.log_message("開始執行爬蟲任務...")
    
    def stop_scraping(self):
        """停止爬取"""
        if self.worker:
            self.worker.stop()
            self.log_message("正在停止任務...")
            self.stop_button.setEnabled(False)
            self.stop_button.setText("⏹ 停止中...")
            
            # 設定一個超時計時器，如果 5 秒內沒有停止，強制終止
            # 改為 5 秒以給予足夠時間完成當前滾動週期
            QTimer.singleShot(5000, self.force_stop_if_needed)
    
    def scraping_finished(self):
        """爬取完成"""
        self.cleanup_worker()
        self.log_message("任務完成！")
        self.statusBar().showMessage("任務完成")
        QMessageBox.information(self, "完成", "評論分析已完成！")
    
    def scraping_error(self, error_msg: str):
        """爬取錯誤"""
        self.cleanup_worker()
        self.log_message(f"錯誤: {error_msg}")
        self.statusBar().showMessage("發生錯誤")
        
        # 如果是使用者中斷，不顯示錯誤對話框
        if "使用者中斷" in error_msg or "中斷任務" in error_msg:
            self.log_message("任務已被使用者中斷")
            self.statusBar().showMessage("任務已中斷")
        else:
            QMessageBox.critical(self, "錯誤", f"執行過程發生錯誤:\n{error_msg}")
    
    def cleanup_worker(self):
        """清理工作執行緒"""
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        
        self.thread = None
        self.worker = None
        
        # 恢復 UI 狀態
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.stop_button.setText("⏹ 停止")  # 恢復按鈕文字
        self.url_input.setEnabled(True)
        self.limit_spinbox.setEnabled(True)
    
    def force_stop_if_needed(self):
        """如果執行緒仍在運行，強制終止"""
        if self.thread and self.thread.isRunning():
            self.log_message("⚠️ 執行緒未正常停止，正在強制終止...")
            self.thread.terminate()
            self.thread.wait()
            self.cleanup_worker()
            self.log_message("任務已強制終止")
            self.statusBar().showMessage("任務已強制終止")
    
    def update_progress(self, value: int, message: str):
        """更新進度"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        self.statusBar().showMessage(message)
    
    def append_log(self, message: str):
        """新增日誌"""
        self.log_text.append(message)
        self.log_text.moveCursor(QTextCursor.End)
    
    def log_message(self, message: str):
        """記錄訊息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append_log(f"[{timestamp}] {message}")
    
    def display_reviews(self, reviews: List[Dict]):
        """顯示評論"""
        self.review_text.clear()
        self.review_text.append(f"共收集到 {len(reviews)} 則評論\n")
        self.review_text.append("=" * 60 + "\n")
        
        for i, review in enumerate(reviews, 1):
            self.review_text.append(f"評論 #{i}")
            
            # 處理評分（可能是字串 "5 星" 或數字）
            rating = review.get('rating', 'N/A')
            if isinstance(rating, str):
                # 從字串中提取數字
                import re
                match = re.search(r'(\d+)', rating)
                if match:
                    rating_num = int(match.group(1))
                    self.review_text.append(f"評分: {'⭐' * rating_num} ({rating})")
                else:
                    self.review_text.append(f"評分: {rating}")
            else:
                self.review_text.append(f"評分: {'⭐' * int(rating)}")
            
            # 顯示評論內容
            text = review.get('text', '無文字內容')
            self.review_text.append(f"內容: {text}")
            
            # 處理推薦餐點（可能是字串或列表）
            suggested_dishes = review.get('suggested_dishes')
            if suggested_dishes:
                if isinstance(suggested_dishes, list):
                    dishes = ", ".join(suggested_dishes)
                else:
                    dishes = suggested_dishes
                self.review_text.append(f"推薦餐點: {dishes}")
            
            self.review_text.append("-" * 60 + "\n")
        
        self.review_text.moveCursor(QTextCursor.Start)
    
    def display_analysis(self, analysis: str):
        """顯示分析報告"""
        self.analysis_text.clear()
        self.analysis_text.append(analysis)
        self.analysis_text.moveCursor(QTextCursor.Start)
        
        # 自動切換到分析報告分頁
        self.tab_widget.setCurrentIndex(2)
    
    def clear_results(self):
        """清除結果"""
        self.log_text.clear()
        self.review_text.clear()
        self.analysis_text.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("就緒")
        self.statusBar().showMessage("就緒")
    
    def save_settings(self):
        """儲存使用者設定"""
        self.settings.setValue("url", self.url_input.text())
        self.settings.setValue("limit", self.limit_spinbox.value())
        self.settings.setValue("dark_theme", self.is_dark_theme)
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("window_state", self.saveState())

    def load_settings(self):
        """載入上次的使用者設定"""
        url = self.settings.value("url", "")
        self.url_input.setText(url)

        limit = self.settings.value("limit", 30, type=int)
        self.limit_spinbox.setValue(limit)

        self.is_dark_theme = self.settings.value("dark_theme", True, type=bool)

        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        window_state = self.settings.value("window_state")
        if window_state:
            self.restoreState(window_state)

    def closeEvent(self, event):
        """關閉視窗事件"""
        if self.thread and self.thread.isRunning():
            reply = QMessageBox.question(
                self,
                "確認關閉",
                "爬蟲任務正在執行中，確定要關閉嗎？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.stop_scraping()
                self.thread.quit()
                self.thread.wait()
                self.save_settings()
                event.accept()
            else:
                event.ignore()
        else:
            self.save_settings()
            event.accept()
