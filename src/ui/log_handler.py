"""
日誌處理器 - GUI 專用
將 Python logging 訊息轉發到 Qt Signal
"""
import logging
from PySide6.QtCore import QObject, Signal


class QtLogHandler(logging.Handler):
    """Qt 日誌處理器"""
    
    def __init__(self, signal: Signal):
        super().__init__()
        self.signal = signal
    
    def emit(self, record):
        """發送日誌訊息"""
        try:
            msg = self.format(record)
            self.signal.emit(msg)
        except Exception:
            self.handleError(record)


class LogManager(QObject):
    """日誌管理器"""
    
    log_signal = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._handler = None
    
    def setup(self):
        """設定日誌處理器"""
        # 創建處理器
        self._handler = QtLogHandler(self.log_signal)
        self._handler.setLevel(logging.INFO)
        
        # 設定格式
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        self._handler.setFormatter(formatter)
        
        # 添加到根日誌記錄器
        root_logger = logging.getLogger()
        root_logger.addHandler(self._handler)
    
    def cleanup(self):
        """清理日誌處理器"""
        if self._handler:
            root_logger = logging.getLogger()
            root_logger.removeHandler(self._handler)
            self._handler = None
