"""
异环 NTE 养成计算器 - 计算器页面 (折叠面板版)
核心界面，替代 Excel 主表
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QMessageBox, QFrame,
    QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt
from core.calculator import Calculator
from data.character_data import CHARACTER_MATERIAL_MAP
from data.arc_data import ARC_MATERIAL_MAP
from gui.components.accordion_panel import AccordionPanel
from functools import partial


class ResultCard(QFrame):
    """结果统计卡片"""
    def __init__(self, title, value="0", parent=None):
        super().__init__(parent)
        self.setObjectName("cardFrame")
        self.setMinimumWidth(160)
        self.setMinimumHeight(80)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)  # 卡片内边距 20px
        layout.setSpacing(8)  # 标签与数字间距 8px
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #999999; font-size: 12px;")
        layout.addWidget(self.title_label)
        
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: #4a9eff; font-size: 24px; font-weight: bold;")
        layout.addWidget(self.value_label)
    
    def set_value(self, value):
        self.value_label.setText(str(value))


class DetailResultCard(QFrame):
    """详细结果卡片"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cardFrame")
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # 标题行：角色名 + 等级范围
        self.header_label = QLabel()
        self.header_label.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.header_label)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #404040; max-height: 1px;")
        layout.addWidget(line)
        
        # 材料信息网格
        self.content_layout = QGridLayout()
        self.content_layout.setSpacing(8)
        self.content_layout.setVerticalSpacing(10)
        self.content_layout.setColumnStretch(0, 1)
        self.content_layout.setColumnStretch(1, 1)
        layout.addLayout(self.content_layout)
        
        self.materials = {}
    
    def set_data(self, char_name, curr_level, target_level, materials, arc_name="", arc_curr_level="", arc_target_level=""):
        """设置卡片数据"""
        arc_part = f"    {arc_name}  {arc_curr_level}级 → {arc_target_level}级" if arc_name else ""
        self.header_label.setText(f"{char_name}  {curr_level}级 → {target_level}级{arc_part}")
        
        # 清空现有内容
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        row = 0
        
        # 1. 突破素材（整行）
        if materials.get("break_material"):
            self._add_material_item(row, 0, "突破素材", materials["break_material"], colspan=2)
            row += 1
        
        # 2. 低级异像 | 低级弧盘素材
        low_text = ""
        if materials.get("low_yixiang", 0) > 0:
            low_text = f"{materials['low_yixiang_name']} ×{materials['low_yixiang']}"
        if materials.get("arc_low_yixiang", 0) > 0:
            arc_low_part = f"{materials.get('arc_low_yixiang_name', '')} ×{materials['arc_low_yixiang']}"
            low_text = f"{low_text} + {arc_low_part}" if low_text else f"弧盘{arc_low_part}"
        if low_text:
            self._add_material_item(row, 0, "低级异像", low_text)
        
        low_arc_text = ""
        if materials.get("low_arc_name") and materials.get("low_arc_count", 0) > 0:
            low_arc_text = f"{materials['low_arc_name']} ×{materials['low_arc_count']}"
        if low_arc_text:
            self._add_material_item(row, 1, "低级弧盘素材", low_arc_text)
        if low_text or low_arc_text:
            row += 1
        
        # 3. 中级异像 | 中级弧盘素材
        mid_text = ""
        if materials.get("mid_yixiang", 0) > 0:
            mid_text = f"{materials['mid_yixiang_name']} ×{materials['mid_yixiang']}"
        if materials.get("arc_mid_yixiang", 0) > 0:
            arc_mid_part = f"{materials.get('arc_mid_yixiang_name', '')} ×{materials['arc_mid_yixiang']}"
            mid_text = f"{mid_text} + {arc_mid_part}" if mid_text else f"弧盘{arc_mid_part}"
        if mid_text:
            self._add_material_item(row, 0, "中级异像", mid_text)
        
        mid_arc_text = ""
        if materials.get("mid_arc_name") and materials.get("mid_arc_count", 0) > 0:
            mid_arc_text = f"{materials['mid_arc_name']} ×{materials['mid_arc_count']}"
        if mid_arc_text:
            self._add_material_item(row, 1, "中级弧盘素材", mid_arc_text)
        if mid_text or mid_arc_text:
            row += 1
        
        # 4. 高级异像 | 高级弧盘素材
        high_text = ""
        if materials.get("high_yixiang", 0) > 0:
            high_text = f"{materials['high_yixiang_name']} ×{materials['high_yixiang']}"
        if materials.get("arc_high_yixiang", 0) > 0:
            arc_high_part = f"{materials.get('arc_high_yixiang_name', '')} ×{materials['arc_high_yixiang']}"
            high_text = f"{high_text} + {arc_high_part}" if high_text else f"弧盘{arc_high_part}"
        if high_text:
            self._add_material_item(row, 0, "高级异像", high_text)
        
        high_arc_text = ""
        if materials.get("high_arc_name") and materials.get("high_arc_count", 0) > 0:
            high_arc_text = f"{materials['high_arc_name']} ×{materials['high_arc_count']}"
        if high_arc_text:
            self._add_material_item(row, 1, "高级弧盘素材", high_arc_text)
        if high_text or high_arc_text:
            row += 1
        
        # 5. 新锐猎人攻略 | 淡色染剂
        exp_low = materials.get("exp_low", 0)
        if exp_low > 0:
            self._add_material_item(row, 0, "新锐猎人攻略", f"×{exp_low}")
        if materials.get("dye_light", 0) > 0:
            self._add_material_item(row, 1, "淡色染剂", f"×{materials['dye_light']}")
        if exp_low > 0 or materials.get("dye_light", 0) > 0:
            row += 1
        
        # 6. 资深猎人攻略 | 无彩染剂
        exp_mid = materials.get("exp_mid", 0)
        if exp_mid > 0:
            self._add_material_item(row, 0, "资深猎人攻略", f"×{exp_mid}")
        if materials.get("dye_colorless", 0) > 0:
            self._add_material_item(row, 1, "无彩染剂", f"×{materials['dye_colorless']}")
        if exp_mid > 0 or materials.get("dye_colorless", 0) > 0:
            row += 1
        
        # 7. 特级猎人攻略 | 混沌染剂
        exp_high = materials.get("exp_high", 0)
        if exp_high > 0:
            self._add_material_item(row, 0, "特级猎人攻略", f"×{exp_high}")
        if materials.get("dye_chaos", 0) > 0:
            self._add_material_item(row, 1, "混沌染剂", f"×{materials['dye_chaos']}")
        if exp_high > 0 or materials.get("dye_chaos", 0) > 0:
            row += 1
        
        # 8. 角色突破金币 | 弧盘强化金币
        char_gold = materials.get("char_gold", 0)
        arc_gold = materials.get("arc_gold", 0)
        if char_gold > 0:
            self._add_material_item(row, 0, "角色突破金币", f"{char_gold:,}")
        if arc_gold > 0:
            self._add_material_item(row, 1, "弧盘强化金币", f"{arc_gold:,}")
    
    def _add_material_item(self, row, col, label, value, colspan=1):
        """添加材料项"""
        text = f"{label}：{value}"
        label_widget = QLabel(text)
        label_widget.setStyleSheet("color: #cccccc; font-size: 13px;")
        label_widget.setWordWrap(True)
        self.content_layout.addWidget(label_widget, row, col, 1, colspan)


class CharacterCard(QFrame):
    """角色养成配置卡片（模仿 HTML 风格）"""
    
    def __init__(self, card_id, on_delete, on_calc, parent=None):
        super().__init__(parent)
        self.card_id = card_id
        self.on_delete_callback = on_delete
        self.on_calc_callback = on_calc
        self.setObjectName("characterCard")
        self.setStyleSheet("""
            QFrame#characterCard {
                background-color: #2d2d2d;
                border: 1px solid #383838;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # === 卡片头部 ===
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # 序号圆圈
        self.index_label = QLabel(str(card_id))
        self.index_label.setFixedSize(24, 24)
        self.index_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.index_label.setStyleSheet("""
            background-color: #3a8eff;
            color: white;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        """)
        header_layout.addWidget(self.index_label)
        
        # 标题
        self.title_label = QLabel(f"角色 {card_id}")
        self.title_label.setStyleSheet("color: #b0b0b0; font-size: 14px;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # 删除按钮
        self.delete_btn = QPushButton("删除")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4f;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #d9363e;
            }
        """)
        self.delete_btn.clicked.connect(self._on_delete)
        header_layout.addWidget(self.delete_btn)
        
        layout.addLayout(header_layout)
        
        # === 表单行 ===
        form_layout = QHBoxLayout()
        form_layout.setSpacing(12)
        
        # 角色名
        char_group = QVBoxLayout()
        char_group.setSpacing(4)
        char_label = QLabel("角色名")
        char_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        char_group.addWidget(char_label)
        self.char_combo = QComboBox()
        self.char_combo.addItems(list(CHARACTER_MATERIAL_MAP.keys()))
        self.char_combo.setEditable(True)
        self.char_combo.setCurrentText("")
        self.char_combo.lineEdit().setPlaceholderText("请选择")
        self.char_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.char_combo.setMinimumWidth(110)
        self.char_combo.setStyleSheet("""
            QComboBox {
                background-color: #3a3a3a;
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                color: #e8e8e8;
                font-size: 13px;
                min-height: 28px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 6px;
            }
            QComboBox QAbstractItemView {
                background-color: #3a3a3a;
                color: #e8e8e8;
                selection-background-color: #4a9eff;
            }
        """)
        char_group.addWidget(self.char_combo)
        form_layout.addLayout(char_group)
        
        # 当前等级
        curr_lvl_group = QVBoxLayout()
        curr_lvl_group.setSpacing(4)
        curr_lvl_label = QLabel("当前等级")
        curr_lvl_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        curr_lvl_group.addWidget(curr_lvl_label)
        self.curr_lvl = QComboBox()
        LEVEL_OPTIONS = ["1", "20", "30", "40", "50", "60", "70", "80"]
        self.curr_lvl.addItems(LEVEL_OPTIONS)
        self.curr_lvl.setCurrentText("1")
        self.curr_lvl.setMinimumWidth(80)
        self.curr_lvl.setStyleSheet("""
            QComboBox {
                background-color: #3a3a3a;
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                color: #e8e8e8;
                font-size: 13px;
                min-height: 28px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 6px;
            }
        """)
        curr_lvl_group.addWidget(self.curr_lvl)
        form_layout.addLayout(curr_lvl_group)
        
        # 目标等级
        target_lvl_group = QVBoxLayout()
        target_lvl_group.setSpacing(4)
        target_lvl_label = QLabel("目标等级")
        target_lvl_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        target_lvl_group.addWidget(target_lvl_label)
        self.target_lvl = QComboBox()
        self.target_lvl.addItems(LEVEL_OPTIONS)
        self.target_lvl.setCurrentText("80")
        self.target_lvl.setMinimumWidth(80)
        self.target_lvl.setStyleSheet("""
            QComboBox {
                background-color: #3a3a3a;
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                color: #e8e8e8;
                font-size: 13px;
                min-height: 28px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 6px;
            }
        """)
        target_lvl_group.addWidget(self.target_lvl)
        form_layout.addLayout(target_lvl_group)
        
        # 弧盘名
        arc_group = QVBoxLayout()
        arc_group.setSpacing(4)
        arc_label = QLabel("弧盘名")
        arc_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        arc_group.addWidget(arc_label)
        self.arc_combo = QComboBox()
        self.arc_combo.addItems(list(ARC_MATERIAL_MAP.keys()))
        self.arc_combo.setEditable(True)
        self.arc_combo.setCurrentText("")
        self.arc_combo.lineEdit().setPlaceholderText("请选择")
        self.arc_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.arc_combo.setMinimumWidth(110)
        self.arc_combo.setStyleSheet("""
            QComboBox {
                background-color: #3a3a3a;
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                color: #e8e8e8;
                font-size: 13px;
                min-height: 28px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 6px;
            }
            QComboBox QAbstractItemView {
                background-color: #3a3a3a;
                color: #e8e8e8;
                selection-background-color: #4a9eff;
            }
        """)
        arc_group.addWidget(self.arc_combo)
        form_layout.addLayout(arc_group)
        
        # 当前弧盘等级
        arc_curr_group = QVBoxLayout()
        arc_curr_group.setSpacing(4)
        arc_curr_label = QLabel("当前弧盘等级")
        arc_curr_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        arc_curr_group.addWidget(arc_curr_label)
        self.arc_curr = QComboBox()
        ARC_LEVEL_OPTIONS = ["1", "20", "30", "40", "50", "60", "70", "80"]
        self.arc_curr.addItems(ARC_LEVEL_OPTIONS)
        self.arc_curr.setCurrentText("1")
        self.arc_curr.setMinimumWidth(80)
        self.arc_curr.setStyleSheet("""
            QComboBox {
                background-color: #3a3a3a;
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                color: #e8e8e8;
                font-size: 13px;
                min-height: 28px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 6px;
            }
        """)
        arc_curr_group.addWidget(self.arc_curr)
        form_layout.addLayout(arc_curr_group)
        
        # 目标弧盘等级
        arc_target_group = QVBoxLayout()
        arc_target_group.setSpacing(4)
        arc_target_label = QLabel("目标弧盘等级")
        arc_target_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        arc_target_group.addWidget(arc_target_label)
        self.arc_target = QComboBox()
        self.arc_target.addItems(ARC_LEVEL_OPTIONS)
        self.arc_target.setCurrentText("80")
        self.arc_target.setMinimumWidth(80)
        self.arc_target.setStyleSheet("""
            QComboBox {
                background-color: #3a3a3a;
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                color: #e8e8e8;
                font-size: 13px;
                min-height: 28px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 6px;
            }
        """)
        arc_target_group.addWidget(self.arc_target)
        form_layout.addLayout(arc_target_group)
        
        # 计算按钮
        btn_group = QVBoxLayout()
        btn_group.setSpacing(4)
        btn_spacer = QLabel("")
        btn_spacer.setFixedHeight(16)  # 与标签对齐
        btn_group.addWidget(btn_spacer)
        self.calc_btn = QPushButton("计算")
        self.calc_btn.setObjectName("primaryButton")
        self.calc_btn.setFixedSize(72, 32)
        self.calc_btn.clicked.connect(self._on_calc)
        btn_group.addWidget(self.calc_btn)
        form_layout.addLayout(btn_group)
        
        layout.addLayout(form_layout)
    
    def _on_delete(self):
        """删除卡片回调"""
        if self.on_delete_callback:
            self.on_delete_callback(self.card_id)
    
    def _on_calc(self):
        """计算回调"""
        if self.on_calc_callback:
            self.on_calc_callback(self.card_id)
    
    def set_card_id(self, new_id):
        """更新卡片序号"""
        self.card_id = new_id
        self.index_label.setText(str(new_id))
        self.title_label.setText(f"角色 {new_id}")


class CalculatorPage(QWidget):
    def __init__(self):
        super().__init__()
        self.calc = Calculator()
        self.characters = []
        self.detail_cards = {}  # 存储详细结果卡片
        self.char_cards = []  # 存储角色卡片列表
        self.next_card_id = 1
        self.init_ui()

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(24)  # 卡片之间间距 24px
        main_layout.setContentsMargins(24, 24, 24, 24)  # 页面边距 24px

        # 页面标题
        title_layout = QVBoxLayout()
        title = QLabel("养成计算器")
        title.setObjectName("pageTitle")
        title_layout.addWidget(title)
        
        subtitle = QLabel("突破 + 弧盘 联动版")
        subtitle.setObjectName("pageSubtitle")
        title_layout.addWidget(subtitle)
        main_layout.addLayout(title_layout)

        # ========== 折叠面板 1: 角色养成配置（默认展开）==========
        self.input_panel = AccordionPanel("角色养成配置", expanded=True)
        
        # 输入卡片容器
        input_container = QFrame()
        input_container.setObjectName("cardFrame")
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(20, 20, 20, 20)  # 卡片内边距 20px
        input_layout.setSpacing(16)
        
        # 卡片列表区域
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(12)
        input_layout.addWidget(self.cards_container)
        
        # 添加角色按钮
        self.add_card_btn = QPushButton("+ 添加角色")
        self.add_card_btn.setStyleSheet("""
            QPushButton {
                background-color: #383838;
                color: #e8e8e8;
                border: 1px dashed #555;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        self.add_card_btn.clicked.connect(self._add_card)
        input_layout.addWidget(self.add_card_btn)
        
        self.input_panel.add_widget(input_container)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setContentsMargins(0, 24, 0, 0)  # 按钮与表格间距 24px
        self.calc_all_btn = QPushButton("🚀 一键计算全队缺口")
        self.calc_all_btn.setObjectName("primaryButton")
        self.calc_all_btn.clicked.connect(self.calc_all)
        btn_layout.addWidget(self.calc_all_btn)

        self.save_btn = QPushButton("💾 保存")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #52c41a;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a818;
            }
        """)
        self.save_btn.clicked.connect(self.save_config)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addStretch()
        
        btn_container = QWidget()
        btn_container.setLayout(btn_layout)
        self.input_panel.add_widget(btn_container)
        
        main_layout.addWidget(self.input_panel)

        # ========== 折叠面板 2: 全队缺口汇总（默认折叠）==========
        self.summary_panel = AccordionPanel("全队缺口汇总", expanded=False)
        
        summary_container = QFrame()
        summary_container.setObjectName("cardFrame")
        summary_layout = QVBoxLayout(summary_container)
        summary_layout.setContentsMargins(20, 20, 20, 20)
        summary_layout.setSpacing(16)
        
        self.result_cards = {}
        card_configs = [
            ("总金币", "0"),
            ("总经验书", "0"),
            ("总染剂", "0"),
            ("总突破素材", "0"),
            ("总低级异像", "0"),
            ("总中级异像", "0"),
            ("总高级异像", "0"),
            ("总低级弧盘材料", "0"),
            ("总中级弧盘材料", "0"),
            ("总高级弧盘材料", "0"),
        ]
        
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(16)
        for title, default in card_configs[:5]:
            card = ResultCard(title, default)
            row1_layout.addWidget(card)
            self.result_cards[title] = card
        
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(16)
        for title, default in card_configs[5:]:
            card = ResultCard(title, default)
            row2_layout.addWidget(card)
            self.result_cards[title] = card
        
        summary_layout.addLayout(row1_layout)
        summary_layout.addLayout(row2_layout)
        self.summary_panel.add_widget(summary_container)
        main_layout.addWidget(self.summary_panel)

        # ========== 折叠面板 3: 详细结果（默认折叠）==========
        self.detail_panel = AccordionPanel("详细结果", expanded=False)
        
        self.detail_cards_container = QWidget()
        self.detail_cards_layout = QGridLayout(self.detail_cards_container)
        self.detail_cards_layout.setSpacing(16)
        self.detail_cards_layout.setContentsMargins(0, 0, 0, 0)
        self.detail_cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.detail_cards_layout.setColumnStretch(0, 1)
        self.detail_cards_layout.setColumnStretch(1, 1)
        
        self.detail_panel.add_widget(self.detail_cards_container)
        main_layout.addWidget(self.detail_panel)
        
        main_layout.addStretch()
        
        # 从 JSON 加载配置或创建默认卡片
        self.load_config()
    
    def showEvent(self, event):
        """页面显示时刷新角色列表"""
        super().showEvent(event)
        self.refresh_character_lists()
    
    def refresh_character_lists(self):
        """刷新所有角色和弧盘下拉框（角色对照页面可能已修改数据）"""
        for card in self.char_cards:
            # 保存当前选择
            current_char = card.char_combo.currentText()
            current_arc = card.arc_combo.currentText()
            
            # 刷新角色列表
            card.char_combo.blockSignals(True)
            card.char_combo.clear()
            card.char_combo.addItems(list(CHARACTER_MATERIAL_MAP.keys()))
            card.char_combo.setEditable(True)
            card.char_combo.lineEdit().setPlaceholderText("请选择")
            card.char_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            if current_char in CHARACTER_MATERIAL_MAP:
                card.char_combo.setCurrentText(current_char)
            else:
                card.char_combo.setCurrentText("")
            card.char_combo.blockSignals(False)
            
            # 刷新弧盘列表
            card.arc_combo.blockSignals(True)
            card.arc_combo.clear()
            card.arc_combo.addItems(list(ARC_MATERIAL_MAP.keys()))
            card.arc_combo.setEditable(True)
            card.arc_combo.lineEdit().setPlaceholderText("请选择")
            card.arc_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            if current_arc and current_arc in ARC_MATERIAL_MAP:
                card.arc_combo.setCurrentText(current_arc)
            else:
                card.arc_combo.setCurrentText("")
            card.arc_combo.blockSignals(False)

    def load_config(self):
        """从 JSON 文件加载角色养成配置"""
        import json
        import os

        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data", "user_data", "character_config.json"
        )

        loaded = False
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    configs = json.load(f)
                if isinstance(configs, list) and len(configs) > 0:
                    for cfg in configs:
                        self._add_card()
                        card = self.char_cards[-1]
                        # 设置角色名
                        char_name = cfg.get("char_name", "")
                        if char_name in CHARACTER_MATERIAL_MAP:
                            card.char_combo.setCurrentText(char_name)
                        # 设置等级
                        card.curr_lvl.setCurrentText(cfg.get("curr_lvl", "1"))
                        card.target_lvl.setCurrentText(cfg.get("target_lvl", "80"))
                        # 设置弧盘
                        arc_name = cfg.get("arc_name", "")
                        if arc_name in ARC_MATERIAL_MAP:
                            card.arc_combo.setCurrentText(arc_name)
                        # 设置弧盘等级
                        card.arc_curr.setCurrentText(cfg.get("arc_curr", "1"))
                        card.arc_target.setCurrentText(cfg.get("arc_target", "80"))
                    loaded = True
            except (json.JSONDecodeError, OSError) as e:
                print(f"加载角色配置失败: {e}")

        if not loaded:
            self._add_card()

    def _add_card(self):
        """添加一张角色卡片"""
        card_id = self.next_card_id
        self.next_card_id += 1
        
        card = CharacterCard(
            card_id=card_id,
            on_delete=self._delete_card,
            on_calc=self._on_card_calc
        )
        self.char_cards.append(card)
        self.cards_layout.addWidget(card)

    def _delete_card(self, card_id):
        """删除角色卡片"""
        if len(self.char_cards) <= 1:
            QMessageBox.warning(self, "提示", "至少保留一条数据")
            return
        
        for i, card in enumerate(self.char_cards):
            if card.card_id == card_id:
                self.cards_layout.removeWidget(card)
                card.deleteLater()
                self.char_cards.pop(i)
                break
        
        # 重新编号
        self._reindex_cards()

    def _reindex_cards(self):
        """重新编号所有卡片"""
        for i, card in enumerate(self.char_cards):
            new_id = i + 1
            card.set_card_id(new_id)
        self.next_card_id = len(self.char_cards) + 1

    def _on_card_calc(self, card_id):
        """单个卡片计算回调"""
        for card in self.char_cards:
            if card.card_id == card_id:
                self._calc_single_card(card)
                break

    def _calc_single_card(self, card):
        """计算单个角色卡片的缺口"""
        char_name = card.char_combo.currentText()
        if not char_name:
            return

        curr_lvl_val = int(card.curr_lvl.currentText())
        target_lvl_val = int(card.target_lvl.currentText())
        
        if curr_lvl_val >= target_lvl_val:
            return

        char_gap = self.calc.calc_character_gap(curr_lvl_val, target_lvl_val)
        char_materials = self.calc.get_character_materials(char_name)

        arc_name = card.arc_combo.currentText()
        arc_gap = {}
        arc_materials = {}
        if arc_name:
            arc_gap = self.calc.calc_arc_gap(
                int(card.arc_curr.currentText()),
                int(card.arc_target.currentText())
            )
            arc_materials = self.calc.get_arc_materials(arc_name)

        # 创建或更新详细结果卡片
        self._update_detail_card(card.card_id, char_name, curr_lvl_val, target_lvl_val, 
                                char_gap, char_materials, arc_gap, arc_materials,
                                arc_name, card.arc_curr.currentText(), card.arc_target.currentText())
        
        # 自动展开详细结果面板
        self.detail_panel.set_expanded(True)

    def calc_single(self, row):
        """（兼容旧接口）计算单个角色"""
        pass

    def calc_all(self):
        """计算全队缺口"""
        self._clear_detail_cards()
        
        total_gold = 0
        total_exp_book = 0
        total_dye = 0
        total_break_material = 0
        total_low_yixiang = 0
        total_mid_yixiang = 0
        total_high_yixiang = 0
        total_low_arc = 0
        total_mid_arc = 0
        total_high_arc = 0

        for card in self.char_cards:
            char_name = card.char_combo.currentText()
            if not char_name:
                continue

            curr_lvl_val = int(card.curr_lvl.currentText())
            target_lvl_val = int(card.target_lvl.currentText())
            
            if curr_lvl_val >= target_lvl_val:
                continue

            char_gap = self.calc.calc_character_gap(curr_lvl_val, target_lvl_val)
            char_materials = self.calc.get_character_materials(char_name)

            arc_name = card.arc_combo.currentText()
            arc_gap = {}
            arc_materials = {}
            if arc_name:
                arc_gap = self.calc.calc_arc_gap(
                    int(card.arc_curr.currentText()),
                    int(card.arc_target.currentText())
                )
                arc_materials = self.calc.get_arc_materials(arc_name)

            total_gold += char_gap.get("gold", 0) + arc_gap.get("gold", 0)
            total_exp_book += (char_gap.get("exp_low", 0) + char_gap.get("exp_mid", 0) + char_gap.get("exp_high", 0))
            total_dye += (arc_gap.get("dye_light", 0) + arc_gap.get("dye_colorless", 0) + arc_gap.get("dye_chaos", 0))
            total_break_material += char_gap.get("break_material", 0)
            total_low_yixiang += max(0, char_gap.get("low_yixiang", 0)) + arc_gap.get("low_yixiang", 0)
            total_mid_yixiang += max(0, char_gap.get("mid_yixiang", 0)) + arc_gap.get("mid_yixiang", 0)
            total_high_yixiang += max(0, char_gap.get("high_yixiang", 0)) + arc_gap.get("high_yixiang", 0)
            total_low_arc += arc_gap.get("low_arc", 0)
            total_mid_arc += arc_gap.get("mid_arc", 0)
            total_high_arc += arc_gap.get("high_arc", 0)

            self._update_detail_card(card.card_id, char_name, curr_lvl_val, target_lvl_val,
                                    char_gap, char_materials, arc_gap, arc_materials,
                                    arc_name, card.arc_curr.currentText(), card.arc_target.currentText())

        self.result_cards["总金币"].set_value(str(total_gold))
        self.result_cards["总经验书"].set_value(str(total_exp_book))
        self.result_cards["总染剂"].set_value(str(total_dye))
        self.result_cards["总突破素材"].set_value(str(total_break_material))
        self.result_cards["总低级异像"].set_value(str(total_low_yixiang))
        self.result_cards["总中级异像"].set_value(str(total_mid_yixiang))
        self.result_cards["总高级异像"].set_value(str(total_high_yixiang))
        self.result_cards["总低级弧盘材料"].set_value(str(total_low_arc))
        self.result_cards["总中级弧盘材料"].set_value(str(total_mid_arc))
        self.result_cards["总高级弧盘材料"].set_value(str(total_high_arc))
        
        self.summary_panel.set_expanded(True)
        self.detail_panel.set_expanded(True)
        
        self.updateGeometry()
        if self.parent():
            min_h = self.minimumSizeHint().height()
            viewport_h = self.parent().height() if self.parent() else 0
            if min_h > viewport_h:
                self.parent().setMinimumHeight(min_h)
            self.parent().updateGeometry()

    def _update_detail_card(self, row, char_name, curr_level, target_level, 
                           char_gap, char_materials, arc_gap, arc_materials,
                           arc_name="", arc_curr_level="", arc_target_level=""):
        """更新或创建详细结果卡片"""
        materials = {
            "break_material": f"{char_materials.get('break_material', '')} ×{char_gap.get('break_material', 0)}" if char_gap.get('break_material', 0) > 0 else "",
            "low_yixiang": char_gap.get('low_yixiang', 0),
            "low_yixiang_name": char_materials.get('low_yixiang', '低级异像'),
            "mid_yixiang": char_gap.get('mid_yixiang', 0),
            "mid_yixiang_name": char_materials.get('mid_yixiang', '中级异像'),
            "high_yixiang": char_gap.get('high_yixiang', 0),
            "high_yixiang_name": char_materials.get('high_yixiang', '高级异像'),
            "low_arc_name": arc_materials.get('low_arc', ''),
            "low_arc_count": arc_gap.get('low_arc', 0),
            "mid_arc_name": arc_materials.get('mid_arc', ''),
            "mid_arc_count": arc_gap.get('mid_arc', 0),
            "high_arc_name": arc_materials.get('high_arc', ''),
            "high_arc_count": arc_gap.get('high_arc', 0),
            "arc_low_yixiang": arc_gap.get('low_yixiang', 0),
            "arc_low_yixiang_name": arc_materials.get('low_yixiang', '') if arc_materials else '',
            "arc_mid_yixiang": arc_gap.get('mid_yixiang', 0),
            "arc_mid_yixiang_name": arc_materials.get('mid_yixiang', '') if arc_materials else '',
            "arc_high_yixiang": arc_gap.get('high_yixiang', 0),
            "arc_high_yixiang_name": arc_materials.get('high_yixiang', '') if arc_materials else '',
            "exp_low": char_gap.get('exp_low', 0),
            "exp_mid": char_gap.get('exp_mid', 0),
            "exp_high": char_gap.get('exp_high', 0),
            "dye_light": arc_gap.get('dye_light', 0),
            "dye_colorless": arc_gap.get('dye_colorless', 0),
            "dye_chaos": arc_gap.get('dye_chaos', 0),
            "char_gold": char_gap.get('gold', 0),
            "arc_gold": arc_gap.get('gold', 0),
        }
        
        if row in self.detail_cards:
            card = self.detail_cards[row]
            card.set_data(char_name, curr_level, target_level, materials, arc_name, arc_curr_level, arc_target_level)
        else:
            card = DetailResultCard()
            card.set_data(char_name, curr_level, target_level, materials, arc_name, arc_curr_level, arc_target_level)
            self.detail_cards[row] = card
            grid_row = (len(self.detail_cards) - 1) // 2
            grid_col = (len(self.detail_cards) - 1) % 2
            self.detail_cards_layout.addWidget(card, grid_row, grid_col)
    
    def _clear_detail_cards(self):
        for card in self.detail_cards.values():
            self.detail_cards_layout.removeWidget(card)
            card.deleteLater()
        self.detail_cards.clear()

    def on_char_changed(self, row, char_name):
        """角色选择变化时更新材料显示"""
        pass

    def save_config(self):
        """保存角色养成配置到 JSON 文件"""
        configs = []
        for card in self.char_cards:
            config = {
                "char_name": card.char_combo.currentText(),
                "curr_lvl": card.curr_lvl.currentText(),
                "target_lvl": card.target_lvl.currentText(),
                "arc_name": card.arc_combo.currentText(),
                "arc_curr": card.arc_curr.currentText(),
                "arc_target": card.arc_target.currentText(),
            }
            configs.append(config)
        
        import json
        import os
        
        save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "user_data")
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, "character_config.json")
        
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(configs, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "保存成功", f"角色养成配置已保存到:\n{save_path}")
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"保存配置时出错:\n{e}")
