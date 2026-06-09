"""
异环 NTE 养成计算器 - 弧盘材料对照页面
全弧盘材料对照，支持新增、编辑、删除、搜索
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QLineEdit, QPushButton, QDialog,
    QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from data.arc_data import ARC_MATERIAL_MAP, save_arc_data


class ArcEditDialog(QDialog):
    """新增/编辑弧盘弹窗"""
    def __init__(self, parent=None, edit_data=None):
        super().__init__(parent)
        self.edit_data = edit_data
        self.setWindowTitle("编辑弧盘" if edit_data else "新增弧盘")
        self.setMinimumWidth(550)
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
            }
            QLabel {
                color: #b0b0b0;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #3a3a3a;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px 10px;
                color: #e8e8e8;
                font-size: 14px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #4a9eff;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #e8e8e8;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 标题
        title = QLabel("编辑弧盘" if self.edit_data else "新增弧盘")
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff;")
        layout.addWidget(title)

        # 表单网格（2列）
        form_widget = QFrame()
        form_layout = QHBoxLayout(form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        # 左列
        left_col = QVBoxLayout()
        left_col.setSpacing(12)
        left_fields = [
            ("弧盘名", "arc_name"),
            ("类别", "category"),
            ("低级异像", "low_yixiang"),
            ("中级异像", "mid_yixiang"),
        ]
        self.inputs = {}
        for label, key in left_fields:
            col = QVBoxLayout()
            col.setSpacing(4)
            lbl = QLabel(label)
            col.addWidget(lbl)
            inp = QLineEdit()
            self.inputs[key] = inp
            col.addWidget(inp)
            left_col.addLayout(col)

        # 右列
        right_col = QVBoxLayout()
        right_col.setSpacing(12)
        right_fields = [
            ("高级异像", "high_yixiang"),
            ("低级弧盘素材", "low_arc"),
            ("中级弧盘素材", "mid_arc"),
            ("高级弧盘素材", "high_arc"),
        ]
        for label, key in right_fields:
            col = QVBoxLayout()
            col.setSpacing(4)
            lbl = QLabel(label)
            col.addWidget(lbl)
            inp = QLineEdit()
            self.inputs[key] = inp
            col.addWidget(inp)
            right_col.addLayout(col)

        form_layout.addLayout(left_col)
        form_layout.addLayout(right_col)
        layout.addWidget(form_widget)

        # 如果有编辑数据，填充
        if self.edit_data:
            self.inputs["arc_name"].setText(self.edit_data[0])
            self.inputs["category"].setText(self.edit_data[1][0])
            self.inputs["low_yixiang"].setText(self.edit_data[1][1])
            self.inputs["mid_yixiang"].setText(self.edit_data[1][2])
            self.inputs["high_yixiang"].setText(self.edit_data[1][3])
            self.inputs["low_arc"].setText(self.edit_data[1][4])
            self.inputs["mid_arc"].setText(self.edit_data[1][5])
            self.inputs["high_arc"].setText(self.edit_data[1][6])

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a8eff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2b7be6;
            }
        """)
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _on_save(self):
        """保存数据"""
        for key, inp in self.inputs.items():
            if not inp.text().strip():
                QMessageBox.warning(self, "提示", f"请填写{key}")
                return
        self.accept()

    def get_data(self):
        """获取表单数据"""
        return {
            "arc_name": self.inputs["arc_name"].text().strip(),
            "category": self.inputs["category"].text().strip(),
            "low_yixiang": self.inputs["low_yixiang"].text().strip(),
            "mid_yixiang": self.inputs["mid_yixiang"].text().strip(),
            "high_yixiang": self.inputs["high_yixiang"].text().strip(),
            "low_arc": self.inputs["low_arc"].text().strip(),
            "mid_arc": self.inputs["mid_arc"].text().strip(),
            "high_arc": self.inputs["high_arc"].text().strip(),
        }


class ArcRefPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # 页面标题
        title = QLabel("弧盘对照")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # 工具栏
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("搜索弧盘名...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e8e8e8;
                font-size: 14px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #4a9eff;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_table)
        toolbar.addWidget(self.search_bar)

        add_btn = QPushButton("新增弧盘")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a8eff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2b7be6;
            }
        """)
        add_btn.clicked.connect(self._add_arc)
        toolbar.addWidget(add_btn)

        layout.addLayout(toolbar)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "序号", "弧盘名", "类别", "低级异像", "中级异像", "高级异像",
            "低级弧盘素材", "中级弧盘素材", "高级弧盘素材", "操作"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(9, 150)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                border: 1px solid #383838;
                border-radius: 8px;
                gridline-color: #383838;
            }
            QTableWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #383838;
                color: #e8e8e8;
            }
            QHeaderView::section {
                background-color: #252525;
                color: #b0b0b0;
                padding: 10px 12px;
                border: none;
                border-bottom: 1px solid #383838;
                font-weight: 500;
                font-size: 13px;
            }
        """)

        self._populate_table()
        layout.addWidget(self.table)

        self.table.hideColumn(0)  # 隐藏序号列

    def _populate_table(self, filter_text=""):
        """填充表格数据"""
        self.table.setRowCount(0)
        self.table.setRowCount(len(ARC_MATERIAL_MAP))

        row = 0
        for arc_name, materials in list(ARC_MATERIAL_MAP.items()):
            if filter_text and filter_text.lower() not in arc_name.lower():
                self.table.setRowHidden(row, True)
            else:
                self.table.setRowHidden(row, False)

            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(arc_name))
            self.table.setItem(row, 2, QTableWidgetItem(materials[0]))
            self.table.setItem(row, 3, QTableWidgetItem(materials[1]))
            self.table.setItem(row, 4, QTableWidgetItem(materials[2]))
            self.table.setItem(row, 5, QTableWidgetItem(materials[3]))
            self.table.setItem(row, 6, QTableWidgetItem(materials[4]))
            self.table.setItem(row, 7, QTableWidgetItem(materials[5]))
            self.table.setItem(row, 8, QTableWidgetItem(materials[6]))

            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_layout.setSpacing(8)

            edit_btn = QPushButton("编辑")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #40c057;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 12px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #36a449;
                }
            """)
            edit_btn.clicked.connect(lambda checked, r=row: self._edit_arc(r))
            btn_layout.addWidget(edit_btn)

            delete_btn = QPushButton("删除")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff4d4f;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 12px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #d9363e;
                }
            """)
            delete_btn.clicked.connect(lambda checked, r=row: self._delete_arc(r))
            btn_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 9, btn_widget)

            row += 1

    def filter_table(self, text):
        """过滤表格内容"""
        self._populate_table(text)

    def _add_arc(self):
        """新增弧盘"""
        dialog = ArcEditDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            arc_name = data["arc_name"]
            if arc_name in ARC_MATERIAL_MAP:
                QMessageBox.warning(self, "提示", f"弧盘「{arc_name}」已存在")
                return
            ARC_MATERIAL_MAP[arc_name] = [
                data["category"],
                data["low_yixiang"],
                data["mid_yixiang"],
                data["high_yixiang"],
                data["low_arc"],
                data["mid_arc"],
                data["high_arc"],
            ]
            save_arc_data(ARC_MATERIAL_MAP)
            self._populate_table(self.search_bar.text())

    def _edit_arc(self, row):
        """编辑弧盘"""
        old_name = self.table.item(row, 1).text()
        materials = ARC_MATERIAL_MAP[old_name]
        dialog = ArcEditDialog(self, edit_data=(old_name, materials))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            new_name = data["arc_name"]
            # 如果名字变更，移除旧的键
            if new_name != old_name:
                del ARC_MATERIAL_MAP[old_name]
            ARC_MATERIAL_MAP[new_name] = [
                data["category"],
                data["low_yixiang"],
                data["mid_yixiang"],
                data["high_yixiang"],
                data["low_arc"],
                data["mid_arc"],
                data["high_arc"],
            ]
            save_arc_data(ARC_MATERIAL_MAP)
            self._populate_table(self.search_bar.text())

    def _delete_arc(self, row):
        """删除弧盘"""
        arc_name = self.table.item(row, 1).text()
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除弧盘「{arc_name}」吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            del ARC_MATERIAL_MAP[arc_name]
            save_arc_data(ARC_MATERIAL_MAP)
            self._populate_table(self.search_bar.text())
