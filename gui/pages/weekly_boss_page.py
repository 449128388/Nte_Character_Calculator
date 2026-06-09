"""
异环 NTE 养成计算器 - 角色突破材料页面
BOSS 清单，支持新增、编辑、删除、搜索、数据持久化
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QLineEdit, QPushButton, QDialog,
    QMessageBox, QFrame, QTextEdit
)
from PyQt6.QtCore import Qt
from data.boss_data import BOSS_MATERIAL_MAP, save_boss_data


class BossEditDialog(QDialog):
    """新增/编辑 BOSS 弹窗"""
    def __init__(self, parent=None, edit_data=None):
        super().__init__(parent)
        self.edit_data = edit_data
        self.setWindowTitle("编辑BOSS" if edit_data else "新增BOSS")
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
            }
            QLabel {
                color: #b0b0b0;
                font-size: 12px;
            }
            QLineEdit, QTextEdit {
                background-color: #3a3a3a;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px 10px;
                color: #e8e8e8;
                font-size: 14px;
                min-height: 20px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #4a9eff;
            }
            QTextEdit {
                min-height: 60px;
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

        title = QLabel("编辑BOSS" if self.edit_data else "新增BOSS")
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff;")
        layout.addWidget(title)

        form_widget = QFrame()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        self.inputs = {}

        # BOSS名称
        name_group = QVBoxLayout()
        name_group.setSpacing(4)
        name_label = QLabel("BOSS名称")
        name_group.addWidget(name_label)
        self.inputs["boss_name"] = QLineEdit()
        name_group.addWidget(self.inputs["boss_name"])
        form_layout.addLayout(name_group)

        # 所在位置
        loc_group = QVBoxLayout()
        loc_group.setSpacing(4)
        loc_label = QLabel("所在位置")
        loc_group.addWidget(loc_label)
        self.inputs["boss_location"] = QLineEdit()
        loc_group.addWidget(self.inputs["boss_location"])
        form_layout.addLayout(loc_group)

        # 对应角色（多行文本）
        char_group = QVBoxLayout()
        char_group.setSpacing(4)
        char_label = QLabel("对应角色（逗号分隔）")
        char_group.addWidget(char_label)
        self.inputs["related_chars"] = QTextEdit()
        char_group.addWidget(self.inputs["related_chars"])
        form_layout.addLayout(char_group)

        layout.addWidget(form_widget)

        if self.edit_data:
            self.inputs["boss_name"].setText(self.edit_data[0])
            self.inputs["boss_location"].setText(self.edit_data[1][0])
            self.inputs["related_chars"].setText(self.edit_data[1][1])

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
        if not self.inputs["boss_name"].text().strip():
            QMessageBox.warning(self, "提示", "请填写BOSS名称")
            return
        if not self.inputs["boss_location"].text().strip():
            QMessageBox.warning(self, "提示", "请填写所在位置")
            return
        if not self.inputs["related_chars"].toPlainText().strip():
            QMessageBox.warning(self, "提示", "请填写对应角色")
            return
        self.accept()

    def get_data(self):
        return {
            "boss_name": self.inputs["boss_name"].text().strip(),
            "boss_location": self.inputs["boss_location"].text().strip(),
            "related_chars": self.inputs["related_chars"].toPlainText().strip(),
        }


class WeeklyBossPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("角色突破材料")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # 工具栏
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("搜索BOSS名称或位置...")
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

        add_btn = QPushButton("新增BOSS")
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
        add_btn.clicked.connect(self._add_boss)
        toolbar.addWidget(add_btn)

        layout.addLayout(toolbar)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "序号", "BOSS名称", "所在位置", "对应角色", "操作"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 150)
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

        self.table.hideColumn(0)

    def _populate_table(self, filter_text=""):
        self.table.setRowCount(0)
        self.table.setRowCount(len(BOSS_MATERIAL_MAP))

        row = 0
        for boss_name, data in list(BOSS_MATERIAL_MAP.items()):
            location = data[0]
            characters = data[1]

            if filter_text:
                ft = filter_text.lower()
                match = (ft in boss_name.lower() or ft in location.lower() or ft in characters.lower())
                self.table.setRowHidden(row, not match)
            else:
                self.table.setRowHidden(row, False)

            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(boss_name))
            self.table.setItem(row, 2, QTableWidgetItem(location))
            self.table.setItem(row, 3, QTableWidgetItem(characters))

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
                QPushButton:hover { background-color: #36a449; }
            """)
            edit_btn.clicked.connect(lambda checked, r=row: self._edit_boss(r))
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
                QPushButton:hover { background-color: #d9363e; }
            """)
            delete_btn.clicked.connect(lambda checked, r=row: self._delete_boss(r))
            btn_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 4, btn_widget)

            row += 1

    def filter_table(self, text):
        self._populate_table(text)

    def _add_boss(self):
        dialog = BossEditDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            boss_name = data["boss_name"]
            if boss_name in BOSS_MATERIAL_MAP:
                QMessageBox.warning(self, "提示", f"BOSS「{boss_name}」已存在")
                return
            BOSS_MATERIAL_MAP[boss_name] = [data["boss_location"], data["related_chars"]]
            save_boss_data(BOSS_MATERIAL_MAP)
            self._populate_table(self.search_bar.text())

    def _edit_boss(self, row):
        old_name = self.table.item(row, 1).text()
        data = BOSS_MATERIAL_MAP[old_name]
        dialog = BossEditDialog(self, edit_data=(old_name, data))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            form = dialog.get_data()
            new_name = form["boss_name"]
            if new_name != old_name:
                del BOSS_MATERIAL_MAP[old_name]
            BOSS_MATERIAL_MAP[new_name] = [form["boss_location"], form["related_chars"]]
            save_boss_data(BOSS_MATERIAL_MAP)
            self._populate_table(self.search_bar.text())

    def _delete_boss(self, row):
        boss_name = self.table.item(row, 1).text()
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除BOSS「{boss_name}」吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            del BOSS_MATERIAL_MAP[boss_name]
            save_boss_data(BOSS_MATERIAL_MAP)
            self._populate_table(self.search_bar.text())
