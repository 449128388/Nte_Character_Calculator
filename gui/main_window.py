"""
异环 NTE 养成计算器 - 主窗口
参考 ok-nte 风格：紧凑左侧导航 + 顶部标题栏 + 卡片式内容区
支持侧边栏收缩/展开功能
"""
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon


class NavButton(QPushButton):
    """自定义导航按钮"""
    def __init__(self, icon_text, label, parent=None):
        super().__init__(parent)
        self.icon_text = icon_text
        self.label = label
        self.setText(f"  {icon_text}  {label}")
        self.setObjectName("navButton")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(40)
        self.setStyleSheet("text-align: left;")
    
    def set_compact_mode(self, compact):
        """设置紧凑模式：只显示图标"""
        if compact:
            self.setText(self.icon_text)
            self.setStyleSheet("text-align: center;")
        else:
            self.setText(f"  {self.icon_text}  {self.label}")
            self.setStyleSheet("text-align: left;")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("异环 NTE 养成计算器")
        self.setMinimumSize(1000, 600)
        self.resize(1400, 900)
        
        # 设置窗口图标（确保任务栏正确显示）
        ico_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mint_icon.ico")
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))
        
        # 侧边栏状态
        self.sidebar_expanded = True
        self.sidebar_expanded_width = 180
        self.sidebar_collapsed_width = 56
        
        # 加载样式
        self.setStyleSheet(self._load_style())
        
        # 中央部件
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        
        self.main_layout = QHBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 左侧导航栏
        self._init_sidebar(self.main_layout)
        
        # 右侧内容区
        self._init_content_area(self.main_layout)
        
        # 默认选中
        self.switch_page("calculator")
    
    def _load_style(self):
        """加载 QSS 样式"""
        import os
        style_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'gui', 'styles', 'dark_theme.qss'
        )
        if os.path.exists(style_path):
            with open(style_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def _init_sidebar(self, layout):
        """初始化左侧导航栏 - 支持收缩/展开"""
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(self.sidebar_expanded_width)
        
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(8, 16, 8, 16)
        self.sidebar_layout.setSpacing(4)
        
        # Logo/标题区域
        self.logo_frame = QFrame()
        self.logo_frame.setObjectName("logoFrame")
        self.logo_layout = QHBoxLayout(self.logo_frame)
        self.logo_layout.setContentsMargins(8, 0, 8, 0)
        
        self.logo_icon = QLabel("🎮")
        self.logo_icon.setStyleSheet("font-size: 20px;")
        self.logo_layout.addWidget(self.logo_icon)
        
        self.logo_text = QLabel("异环 NTE")
        self.logo_text.setStyleSheet("font-size: 14px; font-weight: bold; color: #e8e8e8;")
        self.logo_layout.addWidget(self.logo_text)
        self.logo_layout.addStretch()
        
        self.sidebar_layout.addWidget(self.logo_frame)
        self.sidebar_layout.addSpacing(8)
        
        # 收缩按钮（放在导航按钮上方）
        self.collapse_btn = QPushButton("◀")
        self.collapse_btn.setObjectName("collapseButton")
        self.collapse_btn.setFixedHeight(32)
        self.collapse_btn.clicked.connect(self.toggle_sidebar)
        self.sidebar_layout.addWidget(self.collapse_btn)
        
        self.sidebar_layout.addSpacing(8)
        
        # 导航按钮
        self.nav_buttons = {}
        nav_items = [
            ("calculator", "📊", "计算器"),
            ("character", "👤", "角色对照"),
            ("arc", "💿", "弧盘对照"),
            ("craft", "⚗", "合成换算"),
            ("boss", "👹", "角色突破材料"),
        ]
        
        for key, icon, label in nav_items:
            btn = NavButton(icon, label)
            btn.clicked.connect(lambda checked, k=key: self.switch_page(k))
            self.sidebar_layout.addWidget(btn)
            self.nav_buttons[key] = btn
        
        self.sidebar_layout.addStretch()
        
        # 底部信息
        self.version_label = QLabel("v1.0.0")
        self.version_label.setStyleSheet("color: #666; font-size: 11px; padding-left: 12px;")
        self.sidebar_layout.addWidget(self.version_label)
        
        layout.addWidget(self.sidebar)
    
    def _init_content_area(self, layout):
        """初始化右侧内容区域"""
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 顶部标题栏
        header = QFrame()
        header.setObjectName("headerBar")
        header.setFixedHeight(56)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        self.page_title = QLabel("计算器")
        self.page_title.setObjectName("headerTitle")
        header_layout.addWidget(self.page_title)
        
        header_layout.addStretch()
        
        content_layout.addWidget(header)
        
        # 页面内容区（使用滚动区域）
        scroll = QScrollArea()
        scroll.setObjectName("contentScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)  # 按需显示垂直滚动条（功能保留）
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 0; }
            QScrollBar::handle:vertical { width: 0; }
        """)
        
        self.stack = QStackedWidget()
        self.stack.setObjectName("pageStack")
        self.pages = {}
        
        # 延迟导入页面
        from gui.pages.calculator_page import CalculatorPage
        from gui.pages.character_ref_page import CharacterRefPage
        from gui.pages.arc_ref_page import ArcRefPage
        from gui.pages.craft_page import CraftPage
        from gui.pages.weekly_boss_page import WeeklyBossPage
        
        self.pages["calculator"] = CalculatorPage()
        self.pages["character"] = CharacterRefPage()
        self.pages["arc"] = ArcRefPage()
        self.pages["craft"] = CraftPage()
        self.pages["boss"] = WeeklyBossPage()
        
        for key, page in self.pages.items():
            self.stack.addWidget(page)
        
        scroll.setWidget(self.stack)
        content_layout.addWidget(scroll)
        
        layout.addWidget(content_widget)
    
    def toggle_sidebar(self):
        """切换侧边栏展开/收缩状态"""
        self.sidebar_expanded = not self.sidebar_expanded
        
        if self.sidebar_expanded:
            # 展开状态
            self.sidebar.setFixedWidth(self.sidebar_expanded_width)
            self.collapse_btn.setText("◀")
            self.logo_text.show()
            for btn in self.nav_buttons.values():
                btn.set_compact_mode(False)
            self.version_label.show()
            self.logo_layout.addWidget(self.logo_text)
            self.logo_layout.addStretch()
        else:
            # 收缩状态
            self.sidebar.setFixedWidth(self.sidebar_collapsed_width)
            self.collapse_btn.setText("▶")
            self.logo_text.hide()
            for btn in self.nav_buttons.values():
                btn.set_compact_mode(True)
            self.version_label.hide()
            # 移除logo_text和stretch
            while self.logo_layout.count() > 1:
                item = self.logo_layout.takeAt(1)
                if item.widget():
                    item.widget().hide()
    
    def switch_page(self, key):
        """切换页面"""
        page_titles = {
            "calculator": "计算器",
            "character": "角色对照",
            "arc": "弧盘对照",
            "craft": "合成换算",
            "boss": "角色突破材料",
        }
        
        # 更新导航按钮状态
        for k, btn in self.nav_buttons.items():
            btn.setChecked(k == key)
        
        # 切换页面
        if key in self.pages:
            self.stack.setCurrentWidget(self.pages[key])
            self.page_title.setText(page_titles.get(key, ""))
