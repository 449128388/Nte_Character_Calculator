"""
折叠面板组件 (Accordion Panel)
可展开/折叠的内容区域
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal


class AccordionPanel(QWidget):
    """折叠面板组件"""
    
    toggled = pyqtSignal(bool)  # 展开/折叠状态变化信号
    
    def __init__(self, title, expanded=False, parent=None):
        super().__init__(parent)
        self._expanded = expanded
        self._title_text = title
        self.init_ui()
    
    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 标题按钮
        self.header_btn = QPushButton()
        self.header_btn.setObjectName("accordionHeader")
        self.header_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header_btn.clicked.connect(self.toggle)
        self.header_btn.setStyleSheet("""
            QPushButton#accordionHeader {
                background-color: #2d2d2d;
                color: #e8e8e8;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton#accordionHeader:hover {
                background-color: #353535;
            }
        """)
        self.update_header_text()
        self.main_layout.addWidget(self.header_btn)
        
        # 内容容器
        self.content_widget = QFrame()
        self.content_widget.setObjectName("accordionContent")
        self.content_widget.setStyleSheet("""
            QFrame#accordionContent {
                background-color: transparent;
                border: none;
            }
        """)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 12, 0, 0)
        self.content_layout.setSpacing(0)
        
        self.main_layout.addWidget(self.content_widget)
        
        # 设置初始状态
        self.content_widget.setVisible(self._expanded)
    
    def update_header_text(self):
        """更新标题文本"""
        icon = "▼" if self._expanded else "▶"
        self.header_btn.setText(f"{icon}  {self._title_text}")
    
    def toggle(self):
        """切换展开/折叠状态"""
        self._expanded = not self._expanded
        self.content_widget.setVisible(self._expanded)
        self.update_header_text()
        self.toggled.emit(self._expanded)
    
    def set_expanded(self, expanded):
        """设置展开状态"""
        if self._expanded != expanded:
            self._expanded = expanded
            self.content_widget.setVisible(self._expanded)
            self.update_header_text()
            self.toggled.emit(self._expanded)
    
    def is_expanded(self):
        """获取当前展开状态"""
        return self._expanded
    
    def content_layout(self):
        """获取内容布局，用于添加子控件"""
        return self.content_layout
    
    def add_widget(self, widget):
        """向内容区添加控件"""
        self.content_layout.addWidget(widget)
