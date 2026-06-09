"""
异环 NTE 养成计算器 - 材料合成换算页面
按 HTML 设计重构：输入卡片 + 合成结果卡片（流程图/基础信息/产出/消耗/剩余）
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QFrame, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from data.material_data import CRAFT_CONVERSION_DATA


class CraftPage(QWidget):
    def __init__(self):
        super().__init__()
        # 构建所有材料列表（低级/中级/高级）
        self.all_materials = self._build_all_materials()
        # 构建材料系列查找表：材料名 -> (系列名, 级别, 下级材料, 上级材料)
        self.material_info = self._build_material_info()
        self.init_ui()

    def _build_all_materials(self):
        """构建所有可选材料列表（包含低/中/高级）"""
        materials = []
        for series_name, mats in CRAFT_CONVERSION_DATA.items():
            if len(mats) >= 3:
                materials.extend(mats[:3])
        return materials

    def _build_material_info(self):
        """构建材料信息查找表"""
        info = {}
        for series_name, mats in CRAFT_CONVERSION_DATA.items():
            if len(mats) >= 3:
                # 低级 -> 中级
                info[mats[0]] = {'series': series_name, 'level': '低级', 'next': mats[1], 'ratio': 3}
                # 中级 -> 高级
                info[mats[1]] = {'series': series_name, 'level': '中级', 'next': mats[2], 'ratio': 3}
                # 高级（无上级）
                info[mats[2]] = {'series': series_name, 'level': '高级', 'next': None, 'ratio': 0}
        return info

    def _get_low_for_mid(self, mid_name):
        """获取中级材料对应的低级材料"""
        for m, mi in self.material_info.items():
            if mi.get('next') == mid_name and mi['level'] == '低级':
                return m
        return None

    def _get_mid_for_high(self, high_name):
        """获取高级材料对应的中级材料"""
        for m, mi in self.material_info.items():
            if mi.get('next') == high_name and mi['level'] == '中级':
                return m
        return None

    def init_ui(self):
        self.setObjectName("craftPage")
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # ── 页面标题 ──
        title = QLabel("合成换算")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #ffffff; margin-bottom: 4px;")
        layout.addWidget(title)

        # ════════════════════════════════════════
        # 输入区卡片
        # ════════════════════════════════════════
        input_card = QFrame()
        input_card.setObjectName("cardFrame")
        input_card.setStyleSheet("""
            QFrame#cardFrame {
                background-color: #2d2d2d;
                border: 1px solid #383838;
                border-radius: 8px;
            }
        """)
        input_card_layout = QVBoxLayout(input_card)
        input_card_layout.setContentsMargins(16, 16, 16, 16)
        input_card_layout.setSpacing(12)

        # 卡片标题
        input_header = QLabel("材料选择与数量")
        input_header.setStyleSheet("font-size: 14px; color: #b0b0b0;")
        input_card_layout.addWidget(input_header)

        # 输入行
        input_row = QHBoxLayout()
        input_row.setSpacing(16)
        input_row.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # 材料选择
        mat_group = QVBoxLayout()
        mat_group.setSpacing(4)
        mat_label = QLabel("选择材料")
        mat_label.setStyleSheet("font-size: 12px; color: #b0b0b0;")
        mat_group.addWidget(mat_label)
        self.material_combo = QComboBox()
        self.material_combo.addItems(self.all_materials)
        self.material_combo.setMinimumWidth(200)
        self.material_combo.setStyleSheet("""
            QComboBox {
                background-color: #3a3a3a;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px 10px;
                color: #ffffff;
                font-size: 14px;
                min-height: 20px;
            }
            QComboBox:focus { border-color: #3a8eff; }
            QComboBox::drop-down { border: none; padding-right: 6px; }
            QComboBox QAbstractItemView {
                background-color: #3a3a3a;
                color: #ffffff;
                selection-background-color: #3a8eff;
                outline: none;
            }
        """)
        mat_group.addWidget(self.material_combo)
        input_row.addLayout(mat_group)

        # 数量输入
        count_group = QVBoxLayout()
        count_group.setSpacing(4)
        count_label = QLabel("输入数量")
        count_label.setStyleSheet("font-size: 12px; color: #b0b0b0;")
        count_group.addWidget(count_label)
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 99999)
        self.count_spin.setValue(20)
        self.count_spin.setMinimumWidth(120)
        self.count_spin.setStyleSheet("""
            QSpinBox {
                background-color: #3a3a3a;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px 10px;
                color: #ffffff;
                font-size: 14px;
                min-height: 20px;
            }
            QSpinBox:focus { border-color: #3a8eff; }
            QSpinBox::up-button, QSpinBox::down-button {
                border: none;
                width: 20px;
            }
        """)
        count_group.addWidget(self.count_spin)
        input_row.addLayout(count_group)

        # 计算按钮
        self.calc_btn = QPushButton("计算合成")
        self.calc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a8eff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #2b7be6;
            }
            QPushButton:pressed {
                background-color: #1a6ad4;
            }
        """)
        input_row.addWidget(self.calc_btn)

        # 弹簧
        input_row.addStretch()
        input_card_layout.addLayout(input_row)
        layout.addWidget(input_card)

        # ════════════════════════════════════════
        # 结果卡片
        # ════════════════════════════════════════
        self.result_card = QFrame()
        self.result_card.setObjectName("cardFrame")
        self.result_card.setStyleSheet("""
            QFrame#cardFrame {
                background-color: #2d2d2d;
                border: 1px solid #383838;
                border-radius: 8px;
            }
        """)
        self.result_layout = QVBoxLayout(self.result_card)
        self.result_layout.setContentsMargins(16, 16, 16, 16)
        self.result_layout.setSpacing(16)

        # 结果标题
        result_header = QLabel("合成路径预览")
        result_header.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff;")
        self.result_layout.addWidget(result_header)

        # ── 分隔线 ──
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #383838; max-height: 1px;")
        self.result_layout.addWidget(sep)

        # ── 内容容器（存放动态生成的内容） ──
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)
        self.result_layout.addWidget(self.content_widget)

        layout.addWidget(self.result_card)
        layout.addStretch()

        # ── 信号连接 ──
        self.calc_btn.clicked.connect(self.calculate)
        self.material_combo.currentTextChanged.connect(self.calculate)
        self.count_spin.valueChanged.connect(self.calculate)

        # 初始计算
        self.calculate()

    def clear_content(self):
        """清空结果内容"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _make_section_title(self, text, color="#b0b0b0"):
        """创建段标题"""
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 14px; color: {color};")
        return lbl

    def _make_result_item(self, label, value, value_color="#cccccc"):
        """创建结果行 label: value"""
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(8)
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 14px; color: #b0b0b0;")
        val = QLabel(value)
        val.setStyleSheet(f"font-size: 14px; color: {value_color}; font-weight: 500;")
        lay.addWidget(lbl)
        lay.addWidget(val)
        lay.addStretch()
        return w

    def _make_section_divider(self):
        """创建段分隔线"""
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet("background-color: #383838; max-height: 1px;")
        return f

    def calculate(self):
        """计算合成路径并展示"""
        self.clear_content()

        material_name = self.material_combo.currentText()
        if not material_name:
            return

        count = self.count_spin.value()
        info = self.material_info.get(material_name)
        if not info:
            return

        level = info['level']
        series = info['series']
        next_mat = info['next']
        ratio = info.get('ratio', 3)

        # 获取同级材料（用于流程图显示）
        mats_in_series = []
        for s_name, mlist in CRAFT_CONVERSION_DATA.items():
            if s_name == series and len(mlist) >= 3:
                mats_in_series = mlist[:3]
                break

        # ──── 1. 合成流程图 ────
        flow_widget = QWidget()
        flow_widget.setStyleSheet("background: transparent;")
        flow_lay = QHBoxLayout(flow_widget)
        flow_lay.setContentsMargins(0, 4, 0, 4)
        flow_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flow_lay.setSpacing(12)

        # 找到当前材料在系列中的索引
        try:
            idx = mats_in_series.index(material_name)
        except ValueError:
            idx = 0

        # 从当前级别开始，显示可合成的路径
        current_idx = idx
        max_steps = min(3 - current_idx, 3)
        step_items = []
        for i in range(current_idx, min(current_idx + 3, 3)):
            m = mats_in_series[i]
            if i == current_idx:
                step_items.append(m)
            else:
                craft_ratio = ratio ** (i - current_idx)
                step_items.append(f"{m}")

        # 构建流程图：当前材料数量
        flow_lay.addWidget(self._make_flow_step(f"{material_name} ×{count}"))

        if level == "低级":
            mid_count = count // 3
            high_count = count // 9
            remain = count % 3

            if mid_count > 0:
                arrow1 = QLabel("→")
                arrow1.setStyleSheet("color: #3a8eff; font-size: 20px;")
                flow_lay.addWidget(arrow1)
                flow_lay.addWidget(self._make_flow_step(f"{next_mat} ×{mid_count}"))

                if high_count > 0:
                    # 查找高级材料
                    mid_info = self.material_info.get(next_mat)
                    if mid_info and mid_info['next']:
                        high_mat = mid_info['next']
                        arrow2 = QLabel("→")
                        arrow2.setStyleSheet("color: #3a8eff; font-size: 20px;")
                        flow_lay.addWidget(arrow2)
                        flow_lay.addWidget(self._make_flow_step(f"{high_mat} ×{high_count}"))

        elif level == "中级":
            high_count = count // 3
            if high_count > 0:
                arrow1 = QLabel("→")
                arrow1.setStyleSheet("color: #3a8eff; font-size: 20px;")
                flow_lay.addWidget(arrow1)
                flow_lay.addWidget(self._make_flow_step(f"{next_mat} ×{high_count}"))

        elif level == "高级":
            # 高级不合成
            pass

        self.content_layout.addWidget(flow_widget)

        # ──── 2. 基础信息 ────
        info_section = QWidget()
        info_section.setStyleSheet("background: transparent;")
        info_lay = QVBoxLayout(info_section)
        info_lay.setContentsMargins(0, 0, 0, 0)
        info_lay.setSpacing(4)
        info_lay.addWidget(self._make_section_title("📦 基础信息"))
        info_lay.addWidget(self._make_result_item("选择材料", f"{material_name} ×{count}", "#3a8eff"))
        info_lay.addWidget(self._make_result_item("材料等级", level))
        self.content_layout.addWidget(info_section)

        # ──── 3. 产出材料 ────
        self.content_layout.addWidget(self._make_section_divider())

        output_section = QWidget()
        output_section.setStyleSheet("background: transparent;")
        output_lay = QVBoxLayout(output_section)
        output_lay.setContentsMargins(0, 0, 0, 0)
        output_lay.setSpacing(4)

        if level == "低级":
            mid_count = count // 3
            high_count = count // 9
            remain = count % 3

            if mid_count > 0:
                output_lay.addWidget(self._make_section_title("✨ 可合成中级材料"))
                output_lay.addWidget(self._make_result_item(next_mat, f"×{mid_count}", "#3a8eff"))

                if high_count > 0:
                    mid_info = self.material_info.get(next_mat)
                    if mid_info and mid_info['next']:
                        high_mat = mid_info['next']
                        output_lay.addWidget(self._make_section_title("✨ 可合成高级材料"))
                        output_lay.addWidget(self._make_result_item(high_mat, f"×{high_count}", "#3a8eff"))
            else:
                output_lay.addWidget(QLabel("数量不足以合成中级材料"))

        elif level == "中级":
            high_count = count // 3
            if high_count > 0:
                output_lay.addWidget(self._make_section_title("✨ 可合成高级材料"))
                output_lay.addWidget(self._make_result_item(next_mat, f"×{high_count}", "#3a8eff"))
            else:
                output_lay.addWidget(QLabel("数量不足以合成高级材料"))

        elif level == "高级":
            output_lay.addWidget(QLabel("高级材料无法继续向上合成"))

        self.content_layout.addWidget(output_section)

        # ──── 4. 消耗材料明细 ────
        self.content_layout.addWidget(self._make_section_divider())

        consume_section = QWidget()
        consume_section.setStyleSheet("background: transparent;")
        consume_lay = QVBoxLayout(consume_section)
        consume_lay.setContentsMargins(0, 0, 0, 0)
        consume_lay.setSpacing(4)
        consume_lay.addWidget(self._make_section_title("📤 消耗材料明细"))

        if level == "低级":
            mid_count = count // 3
            high_count = count // 9
            remain = count % 3

            if mid_count > 0:
                consume_lay.addWidget(
                    self._make_result_item("合成中级材料消耗", f"{material_name} ×{mid_count * 3}", "#b0b0b0"))

                if high_count > 0:
                    mid_info = self.material_info.get(next_mat)
                    if mid_info and mid_info['next']:
                        high_mat = mid_info['next']
                        consume_lay.addWidget(
                            self._make_result_item("合成高级材料消耗（含中级）",
                                                   f"{material_name} ×{high_count * 9}\n{next_mat} ×{high_count * 3}",
                                                   "#b0b0b0"))

        elif level == "中级":
            high_count = count // 3
            if high_count > 0:
                consume_lay.addWidget(
                    self._make_result_item("合成高级材料消耗", f"{material_name} ×{high_count * 3}", "#b0b0b0"))
                # 补充低级材料
                low_mat = self._get_low_for_mid(material_name)
                if low_mat:
                    total_low = high_count * 3 * 3
                    consume_lay.addWidget(
                        self._make_result_item("折合低级材料", f"{low_mat} ×{total_low}", "#b0b0b0"))

        elif level == "高级":
            # 补充下级
            mid_mat = self._get_mid_for_high(material_name)
            low_mat = self._get_low_for_mid(mid_mat) if mid_mat else None
            if mid_mat:
                consume_lay.addWidget(
                    self._make_result_item("折合中级材料", f"{mid_mat} ×{count * 3}", "#b0b0b0"))
            if low_mat:
                consume_lay.addWidget(
                    self._make_result_item("折合低级材料", f"{low_mat} ×{count * 9}", "#b0b0b0"))

        self.content_layout.addWidget(consume_section)

        # ──── 5. 剩余材料 ────
        self.content_layout.addWidget(self._make_section_divider())

        remain_section = QWidget()
        remain_section.setStyleSheet("background: transparent;")
        remain_lay = QVBoxLayout(remain_section)
        remain_lay.setContentsMargins(0, 0, 0, 0)
        remain_lay.setSpacing(4)
        remain_lay.addWidget(self._make_section_title("📥 剩余材料"))

        has_remain = False

        if level == "低级":
            remain = count % 3
            if remain > 0:
                remain_lay.addWidget(
                    self._make_result_item(material_name, f"×{remain}", "#888888"))
                has_remain = True

            mid_count = count // 3
            if mid_count > 0:
                mid_remain = mid_count % 3
                if mid_remain > 0:
                    remain_lay.addWidget(
                        self._make_result_item(next_mat, f"×{mid_remain}", "#888888"))
                    has_remain = True

        elif level == "中级":
            high_count = count // 3
            remain = count % 3
            if remain > 0:
                remain_lay.addWidget(
                    self._make_result_item(material_name, f"×{remain}", "#888888"))
                has_remain = True

        elif level == "高级":
            remain_lay.addWidget(QLabel("高级材料无法继续合成"))
            has_remain = True

        if not has_remain:
            remain_lay.addWidget(QLabel("无剩余材料", objectName="secondaryText"))

        self.content_layout.addWidget(remain_section)

    def _make_flow_step(self, text):
        """创建流程图步骤块"""
        w = QFrame()
        w.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-radius: 6px;
                padding: 12px 16px;
            }
        """)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(12, 8, 12, 8)
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 14px; color: #ffffff;")
        lay.addWidget(lbl)
        return w
