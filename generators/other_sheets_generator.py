"""
其他副表生成器（全角色对照、全弧盘对照、材料合成、周本、经验书等）
"""
from config import Colors
from data.character_data import CHARACTER_MATERIAL_MAP, CHARACTER_LEVEL_COLUMNS
from data.arc_data import ARC_MATERIAL_MAP, ARC_LEVEL_COLUMNS
from data.material_data import (
    CRAFT_CONVERSION_DATA,
    CHAR_EXP_BOOK_DATA, ARC_EXP_BOOK_DATA, SKILL_LEVEL_DATA, SKILL_LEVEL_COLUMNS
)
from utils.styles import create_header_style, apply_dict_style
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

class OtherSheetsGenerator:
    """其他副表生成器"""

    def __init__(self, workbook):
        self.wb = workbook

    def generate_all(self):
        """生成所有副表"""
        self._generate_character_ref()
        self._generate_arc_ref()
        self._generate_craft_conversion()
        self._generate_char_exp_book()
        self._generate_arc_exp_book()
        self._generate_skill_material()

    def _generate_title(self, sheet_name, title_text, merge_end):
        """通用标题生成"""
        ws = self.wb.create_sheet(sheet_name)
        ws.merge_cells(f"A1:{merge_end}1")
        cell = ws["A1"]
        cell.value = title_text
        cell.font = Font(size=14, bold=True, color=Colors.TITLE_TEXT)
        cell.fill = PatternFill(start_color=Colors.TITLE_BG, end_color=Colors.TITLE_BG, fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 26
        return ws

    def _generate_character_ref(self):
        """全角色突破材料对照表"""
        ws = self._generate_title("全角色突破材料对照", "全角色突破材料类型对照表", "G")

        headers = ["角色名", "突破素材", "低级异像素材", "中级异像素材", "高级异像素材", "突破素材类型", "备注"]
        header_style = create_header_style(Colors.HEADER_CHAR_BG)
        for col, val in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col, value=val)
            apply_dict_style(cell, header_style)

        row = 4
        for char_name, data in CHARACTER_MATERIAL_MAP.items():
            for col, val in enumerate([char_name] + data, 1):
                cell = ws.cell(row=row, column=col, value=val)
                cell.border = header_style["border"]
                cell.alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[row].height = 22
            row += 1

        for c in range(1, 8):
            from openpyxl.utils import get_column_letter
            ws.column_dimensions[get_column_letter(c)].width = 22

    def _generate_arc_ref(self):
        """全弧盘突破材料对照表"""
        ws = self._generate_title("全弧盘突破材料对照", "全弧盘突破材料类型对照表", "H")

        headers = ["弧盘名", "类别", "低级异像素材", "中级异像素材", "高级异像素材", "低级弧盘素材", "中级弧盘素材", "高级弧盘素材"]
        header_style = create_header_style(Colors.HEADER_ARC_BG)
        for col, val in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col, value=val)
            apply_dict_style(cell, header_style)

        row = 4
        for arc_name, data in ARC_MATERIAL_MAP.items():
            for col, val in enumerate([arc_name] + data, 1):
                cell = ws.cell(row=row, column=col, value=val)
                cell.border = header_style["border"]
                cell.alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[row].height = 22
            row += 1

        for c in range(1, 9):
            from openpyxl.utils import get_column_letter
            ws.column_dimensions[get_column_letter(c)].width = 20

    def _generate_craft_conversion(self):
        """材料合成换算表"""
        ws = self._generate_title("材料合成换算表", "材料 3 合 1 合成换算表", "E")

        headers = ["材料类型", "低级素材", "中级素材", "高级素材", "合成比例"]
        header_style = create_header_style(Colors.HEADER_INPUT_BG)
        for col, val in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col, value=val)
            apply_dict_style(cell, header_style)

        row = 4
        for mat_type, data in CRAFT_CONVERSION_DATA.items():
            for col, val in enumerate([mat_type] + data, 1):
                cell = ws.cell(row=row, column=col, value=val)
                cell.border = header_style["border"]
                cell.alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[row].height = 22
            row += 1

        # 自动换算计算器
        ws.merge_cells(f"A{row+2}:E{row+2}")
        cell = ws.cell(row=row+2, column=1, value="自动换算计算器")
        cell.font = Font(bold=True, size=12)
        cell.alignment = Alignment(horizontal="center", vertical="center")

        calc_labels = [
            (row+4, "输入低级素材数量", "", "输入中级素材数量", ""),
            (row+5, "可合成中级", "=FLOOR(B{}/3,1)".format(row+4), "可合成高级", "=FLOOR(E{}/3,1)".format(row+4)),
            (row+6, "可合成高级", "=FLOOR(B{}/3,1)".format(row+5), "剩余中级", "=MOD(E{},3)".format(row+4)),
            (row+7, "剩余低级", "=MOD(B{},3)".format(row+4), "", ""),
        ]
        for r, l1, f1, l2, f2 in calc_labels:
            ws.cell(row=r, column=1, value=l1).border = header_style["border"]
            ws.cell(row=r, column=2, value=f1).border = header_style["border"]
            ws.cell(row=r, column=4, value=l2).border = header_style["border"]
            ws.cell(row=r, column=5, value=f2).border = header_style["border"]

        for c in range(1, 6):
            from openpyxl.utils import get_column_letter
            ws.column_dimensions[get_column_letter(c)].width = 20

    def _generate_char_exp_book(self):
        """人物经验书对照表"""
        ws = self._generate_title("人物经验书对照表", "人物经验书对照表", "B")

        header_style = create_header_style(Colors.HEADER_INPUT_BG)
        for col, val in enumerate(["材料名称", "提供经验(点)"], 1):
            cell = ws.cell(row=3, column=col, value=val)
            apply_dict_style(cell, header_style)

        row = 4
        for name, exp in CHAR_EXP_BOOK_DATA.items():
            ws.cell(row=row, column=1, value=name).border = header_style["border"]
            ws.cell(row=row, column=2, value=exp).border = header_style["border"]
            ws.cell(row=row, column=1).alignment = Alignment(horizontal="center", vertical="center")
            ws.cell(row=row, column=2).alignment = Alignment(horizontal="center", vertical="center")
            row += 1

        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 16

    def _generate_arc_exp_book(self):
        """弧盘经验书对照表"""
        ws = self._generate_title("弧盘经验书对照表", "弧盘经验书对照表", "B")

        header_style = create_header_style(Colors.HEADER_ARC_BG)
        for col, val in enumerate(["材料名称", "提供经验(点)"], 1):
            cell = ws.cell(row=3, column=col, value=val)
            apply_dict_style(cell, header_style)

        row = 4
        for name, exp in ARC_EXP_BOOK_DATA.items():
            ws.cell(row=row, column=1, value=name).border = header_style["border"]
            ws.cell(row=row, column=2, value=exp).border = header_style["border"]
            ws.cell(row=row, column=1).alignment = Alignment(horizontal="center", vertical="center")
            ws.cell(row=row, column=2).alignment = Alignment(horizontal="center", vertical="center")
            row += 1

        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 16

    def _generate_skill_material(self):
        """技能材料总表"""
        ws = self._generate_title("技能材料总表", "技能升级材料总表（累计值）", "G")

        header_style = create_header_style(Colors.HEADER_CHAR_BG)
        for col, val in enumerate(SKILL_LEVEL_COLUMNS, 1):
            cell = ws.cell(row=3, column=col, value=val)
            apply_dict_style(cell, header_style)

        row = 4
        for level, data in sorted(SKILL_LEVEL_DATA.items()):
            for col, val in enumerate([level] + data, 1):
                cell = ws.cell(row=row, column=col, value=val)
                cell.border = header_style["border"]
                cell.alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[row].height = 22
            row += 1

        ws.merge_cells(f"A{row+1}:G{row+1}")
        cell = ws.cell(row=row+1, column=1)
        cell.value = "注：以上为示例数据。技能A和技能B共用此表，如游戏内两技能材料不同，请复制此表分别命名。"
        cell.font = Font(italic=True, color="999999")

        for c in range(1, 8):
            from openpyxl.utils import get_column_letter
            ws.column_dimensions[get_column_letter(c)].width = 16
