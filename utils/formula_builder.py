"""
Excel 公式构建工具
自动生成复杂的 SUMIF / VLOOKUP 公式字符串
"""
from openpyxl.utils import get_column_letter

class FormulaBuilder:
    """公式构建器"""

    @staticmethod
    def vlookup(lookup_value, table_range, col_index, exact_match=True):
        """构建 VLOOKUP 公式，带 IFERROR 包装"""
        match = "FALSE" if exact_match else "TRUE"
        return f'IFERROR(VLOOKUP({lookup_value},{table_range},{col_index},{match}),"未找到")'

    @staticmethod
    def sumif_diff(sheet_name, criteria_col, criteria_max, criteria_min, sum_col):
        """构建 SUMIF 相减公式（目标累计 - 当前累计）"""
        return (
            f'SUMIF({sheet_name}!${criteria_col}:${criteria_col},'
            f'"<="&{criteria_max},{sheet_name}!${sum_col}:${sum_col})-'
            f'SUMIF({sheet_name}!${criteria_col}:${criteria_col},'
            f'"<="&{criteria_min},{sheet_name}!${sum_col}:${sum_col})'
        )

    @staticmethod
    def conditional_formula(condition, true_value, false_value='""'):
        """构建 IF 条件公式"""
        return f'=IF({condition},{true_value},{false_value})'

    @staticmethod
    def or_empty(*cells):
        """构建 OR 空值判断条件"""
        conditions = [f'{cell}=""' for cell in cells]
        return f'OR({",".join(conditions)})'

    @staticmethod
    def sum_range(col_letter, start_row, end_row):
        """构建 SUM 范围公式"""
        return f'SUM({col_letter}{start_row}:{col_letter}{end_row})'

    @staticmethod
    def character_break_material_num(data_row, sheet_ref="角色等级突破材料总表"):
        """角色突破素材数量公式（突破素材列）"""
        condition = f'OR(B{data_row}="",C{data_row}="",D{data_row}="")'
        formula = FormulaBuilder.sumif_diff(sheet_ref, "A", f"D{data_row}", f"C{data_row}", "E")
        return FormulaBuilder.conditional_formula(condition, f'""', formula)

    @staticmethod
    def character_low_yixiang_num(data_row, sheet_ref="角色等级突破材料总表"):
        """角色低级异像数量公式"""
        condition = f'OR(B{data_row}="",C{data_row}="",D{data_row}="")'
        formula = FormulaBuilder.sumif_diff(sheet_ref, "A", f"D{data_row}", f"C{data_row}", "B")
        return FormulaBuilder.conditional_formula(condition, f'""', formula)

    @staticmethod
    def character_mid_yixiang_num(data_row, sheet_ref="角色等级突破材料总表"):
        """角色中级异像数量公式"""
        condition = f'OR(B{data_row}="",C{data_row}="",D{data_row}="")'
        formula = FormulaBuilder.sumif_diff(sheet_ref, "A", f"D{data_row}", f"C{data_row}", "C")
        return FormulaBuilder.conditional_formula(condition, f'""', formula)

    @staticmethod
    def character_high_yixiang_num(data_row, sheet_ref="角色等级突破材料总表"):
        """角色高级异像数量公式"""
        condition = f'OR(B{data_row}="",C{data_row}="",D{data_row}="")'
        formula = FormulaBuilder.sumif_diff(sheet_ref, "A", f"D{data_row}", f"C{data_row}", "D")
        return FormulaBuilder.conditional_formula(condition, f'""', formula)

    @staticmethod
    def arc_material_num(data_row, col_name, sheet_ref="弧盘强化总表"):
        """弧盘素材数量公式（通用）"""
        condition = f'OR(E{data_row}="",F{data_row}="",G{data_row}="")'
        formula = FormulaBuilder.sumif_diff(sheet_ref, "A", f"G{data_row}", f"F{data_row}", col_name)
        return FormulaBuilder.conditional_formula(condition, f'""', formula)

    @staticmethod
    def character_material_name(data_row, col_index, sheet_ref="全角色突破材料对照"):
        """角色材料名称 VLOOKUP 公式"""
        condition = f'B{data_row}=""'
        vlookup = FormulaBuilder.vlookup(f"B{data_row}", f"{sheet_ref}!$A:$E", col_index)
        return FormulaBuilder.conditional_formula(condition, f'""', vlookup)

    @staticmethod
    def arc_material_name(data_row, col_index, sheet_ref="全弧盘突破材料对照"):
        """弧盘材料名称 VLOOKUP 公式"""
        condition = f'E{data_row}=""'
        vlookup = FormulaBuilder.vlookup(f"E{data_row}", f"{sheet_ref}!$A:$H", col_index)
        return FormulaBuilder.conditional_formula(condition, f'""', vlookup)

    @staticmethod
    def total_gold(data_row):
        """总金币 = 角色突破金币 + 弧盘强化金币"""
        return f'=IF(B{data_row}="","",T{data_row}+AJ{data_row})'

    @staticmethod
    def total_dye_exp(data_row):
        """总染剂经验 = 淡色×500 + 无彩×2500 + 混沌×10000"""
        return f'=IF(B{data_row}="","",AG{data_row}*500+AH{data_row}*2500+AI{data_row}*10000)'

    @staticmethod
    def total_low_yixiang(data_row):
        """总低级异像 = 角色低级 + 弧盘低级"""
        return f'=IF(B{data_row}="","",L{data_row}+AB{data_row})'

    @staticmethod
    def total_mid_yixiang(data_row):
        """总中级异像 = 角色中级 + 弧盘中级"""
        return f'=IF(B{data_row}="","",N{data_row}+AD{data_row})'

    @staticmethod
    def total_high_yixiang(data_row):
        """总高级异像 = 角色高级 + 弧盘高级"""
        return f'=IF(B{data_row}="","",P{data_row}+AF{data_row})'
