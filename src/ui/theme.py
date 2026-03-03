"""
主題管理器
提供深色和淺色主題
"""
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication


class ThemeManager:
    """主題管理器"""
    
    @staticmethod
    def apply_light_theme(app: QApplication):
        """套用淺色主題"""
        palette = QPalette()
        
        # 主要顏色
        palette.setColor(QPalette.Window, QColor(240, 240, 245))
        palette.setColor(QPalette.WindowText, QColor(30, 30, 30))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(248, 248, 250))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(30, 30, 30))
        palette.setColor(QPalette.Text, QColor(30, 30, 30))
        palette.setColor(QPalette.Button, QColor(255, 255, 255))
        palette.setColor(QPalette.ButtonText, QColor(30, 30, 30))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(66, 133, 244))
        palette.setColor(QPalette.Highlight, QColor(66, 133, 244))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        app.setPalette(palette)
        app.setStyleSheet(ThemeManager._get_light_stylesheet())
    
    @staticmethod
    def apply_dark_theme(app: QApplication):
        """套用深色主題"""
        palette = QPalette()
        
        # 主要顏色
        palette.setColor(QPalette.Window, QColor(30, 30, 35))
        palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.Base, QColor(40, 40, 45))
        palette.setColor(QPalette.AlternateBase, QColor(35, 35, 40))
        palette.setColor(QPalette.ToolTipBase, QColor(50, 50, 55))
        palette.setColor(QPalette.ToolTipText, QColor(220, 220, 220))
        palette.setColor(QPalette.Text, QColor(220, 220, 220))
        palette.setColor(QPalette.Button, QColor(50, 50, 55))
        palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
        palette.setColor(QPalette.BrightText, QColor(255, 100, 100))
        palette.setColor(QPalette.Link, QColor(100, 180, 255))
        palette.setColor(QPalette.Highlight, QColor(66, 133, 244))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        app.setPalette(palette)
        app.setStyleSheet(ThemeManager._get_dark_stylesheet())
    
    @staticmethod
    def _get_light_stylesheet() -> str:
        """取得淺色主題樣式表"""
        return """
            QMainWindow {
                background-color: #f0f0f5;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e5;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: #4285f4;
            }
            
            QLineEdit, QSpinBox, QTextEdit {
                border: 2px solid #e0e0e5;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
                selection-background-color: #4285f4;
            }
            
            QLineEdit:focus, QSpinBox:focus, QTextEdit:focus {
                border-color: #4285f4;
            }
            
            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #e0e0e5;
                border-top-right-radius: 4px;
                background-color: #f5f5f5;
            }
            
            QSpinBox::up-button:hover {
                background-color: #4285f4;
            }
            
            QSpinBox::up-button:pressed {
                background-color: #3275e4;
            }
            
            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                border-left: 1px solid #e0e0e5;
                border-bottom-right-radius: 4px;
                background-color: #f5f5f5;
            }
            
            QSpinBox::down-button:hover {
                background-color: #4285f4;
            }
            
            QSpinBox::down-button:pressed {
                background-color: #3275e4;
            }
            
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background-color: #5294ff;
            }
            
            QPushButton:pressed {
                background-color: #3275e4;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
            
            QPushButton#stopButton {
                background-color: #ea4335;
            }
            
            QPushButton#stopButton:hover {
                background-color: #f55545;
            }
            
            QPushButton#clearButton {
                background-color: #fbbc04;
                color: #333;
            }
            
            QPushButton#clearButton:hover {
                background-color: #ffcc14;
            }
            
            QProgressBar {
                border: 2px solid #e0e0e5;
                border-radius: 8px;
                text-align: center;
                background-color: white;
                height: 24px;
            }
            
            QProgressBar::chunk {
                background-color: #34a853;
                border-radius: 6px;
            }
            
            QCheckBox {
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #e0e0e5;
                border-radius: 4px;
                background-color: white;
            }
            
            QCheckBox::indicator:checked {
                background-color: #4285f4;
                border-color: #4285f4;
                image: url(none);
            }
            
            QTabWidget::pane {
                border: 2px solid #e0e0e5;
                border-radius: 8px;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #f0f0f5;
                border: 2px solid #e0e0e5;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            
            QTabBar::tab:hover {
                background-color: #fafafa;
            }
            
            QScrollBar:vertical {
                background-color: #f0f0f5;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #c0c0c5;
                min-height: 20px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a5;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QLabel#statusLabel {
                color: #5f6368;
                font-size: 12px;
            }
            
            QLabel#titleLabel {
                color: #4285f4;
                font-size: 16px;
                font-weight: bold;
            }
        """
    
    @staticmethod
    def _get_dark_stylesheet() -> str:
        """取得深色主題樣式表"""
        return """
            QMainWindow {
                background-color: #1e1e23;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3a3a3f;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #28282d;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: #64b4ff;
            }
            
            QLineEdit, QSpinBox, QTextEdit {
                border: 2px solid #3a3a3f;
                border-radius: 6px;
                padding: 8px;
                background-color: #28282d;
                color: #dcdcdc;
                selection-background-color: #4285f4;
            }
            
            QLineEdit:focus, QSpinBox:focus, QTextEdit:focus {
                border-color: #64b4ff;
            }
            
            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #3a3a3f;
                border-top-right-radius: 4px;
                background-color: #3a3a3f;
            }
            
            QSpinBox::up-button:hover {
                background-color: #4285f4;
            }
            
            QSpinBox::up-button:pressed {
                background-color: #3275e4;
            }
            
            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                border-left: 1px solid #3a3a3f;
                border-bottom-right-radius: 4px;
                background-color: #3a3a3f;
            }
            
            QSpinBox::down-button:hover {
                background-color: #4285f4;
            }
            
            QSpinBox::down-button:pressed {
                background-color: #3275e4;
            }
            
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background-color: #5294ff;
            }
            
            QPushButton:pressed {
                background-color: #3275e4;
            }
            
            QPushButton:disabled {
                background-color: #444444;
                color: #888888;
            }
            
            QPushButton#stopButton {
                background-color: #ea4335;
            }
            
            QPushButton#stopButton:hover {
                background-color: #f55545;
            }
            
            QPushButton#clearButton {
                background-color: #fbbc04;
                color: #1e1e23;
            }
            
            QPushButton#clearButton:hover {
                background-color: #ffcc14;
            }
            
            QProgressBar {
                border: 2px solid #3a3a3f;
                border-radius: 8px;
                text-align: center;
                background-color: #28282d;
                color: #dcdcdc;
                height: 24px;
            }
            
            QProgressBar::chunk {
                background-color: #34a853;
                border-radius: 6px;
            }
            
            QCheckBox {
                spacing: 8px;
                color: #dcdcdc;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #3a3a3f;
                border-radius: 4px;
                background-color: #28282d;
            }
            
            QCheckBox::indicator:checked {
                background-color: #4285f4;
                border-color: #4285f4;
            }
            
            QTabWidget::pane {
                border: 2px solid #3a3a3f;
                border-radius: 8px;
                background-color: #28282d;
            }
            
            QTabBar::tab {
                background-color: #1e1e23;
                border: 2px solid #3a3a3f;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 4px;
                color: #dcdcdc;
            }
            
            QTabBar::tab:selected {
                background-color: #28282d;
                border-bottom-color: #28282d;
            }
            
            QTabBar::tab:hover {
                background-color: #323237;
            }
            
            QScrollBar:vertical {
                background-color: #1e1e23;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #4a4a4f;
                min-height: 20px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #5a5a5f;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QLabel#statusLabel {
                color: #9aa0a6;
                font-size: 12px;
            }
            
            QLabel#titleLabel {
                color: #64b4ff;
                font-size: 16px;
                font-weight: bold;
            }
        """
