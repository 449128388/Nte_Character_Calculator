"""
异环 NTE 养成计算器 - 计算引擎
替代 Excel 的 SUMIF/VLOOKUP 公式
"""
from data.character_data import CHARACTER_LEVEL_UP_DATA, CHARACTER_MATERIAL_MAP, YIXIANG_SERIES_MAP
from data.arc_data import ARC_LEVEL_UP_DATA, ARC_MATERIAL_MAP
from data.material_data import CRAFT_CONVERSION_DATA

# 构建材料合成映射表（用于快速查找）
MATERIAL_CRAFT_MAP = {}
for series_name, materials in CRAFT_CONVERSION_DATA.items():
    if len(materials) >= 3:
        # 低级材料: [中级材料, 合成比例]
        MATERIAL_CRAFT_MAP[materials[0]] = {
            'count': 3,
            'next': materials[1],
            'material': materials[1]
        }
        # 中级材料: [高级材料, 合成比例]
        MATERIAL_CRAFT_MAP[materials[1]] = {
            'count': 3,
            'next': materials[2],
            'material': materials[2]
        }
        # 高级材料无下级
        MATERIAL_CRAFT_MAP[materials[2]] = {
            'count': 0,
            'next': None,
            'material': None
        }


class Calculator:
    """养成缺口计算引擎"""

    def _get_total_exp(self, curr_level, target_level):
        """计算当前等级到目标等级所需的总经验值
        
        经验值在表中以分段值存储，需累加各段（如1→20:119000, 20→30:219000, ...）
        """
        if curr_level >= target_level:
            return 0
        
        # 所有等级断点（排序）
        levels = sorted(CHARACTER_LEVEL_UP_DATA.keys())
        
        total_exp = 0
        for lvl in levels:
            if lvl > curr_level and lvl <= target_level:
                data = CHARACTER_LEVEL_UP_DATA.get(lvl, [0] * 11)
                total_exp += data[8]  # 累计经验（分段值）
        
        return total_exp

    def calc_character_gap(self, curr_level, target_level):
        """计算角色等级突破缺口

        替代 Excel 公式:
        =SUMIF(角色等级突破材料总表!$A:$A,"<="&D5,角色等级突破材料总表!$E:$E)
         -SUMIF(角色等级突破材料总表!$A:$A,"<="&C5,角色等级突破材料总表!$E:$E)
        
        攻略书数量根据总经验值动态计算，优先使用高级攻略：
        - 特级攻略: 20000经验点
        - 资深攻略: 5000经验点
        - 新锐攻略: 1000经验点
        """
        if curr_level >= target_level:
            return {
                'break_material': 0,
                'low_yixiang': 0,
                'mid_yixiang': 0,
                'high_yixiang': 0,
                'exp_low': 0,
                'exp_mid': 0,
                'exp_high': 0,
                'gold': 0
            }

        total = CHARACTER_LEVEL_UP_DATA.get(target_level, [0] * 11)
        current = CHARACTER_LEVEL_UP_DATA.get(curr_level, [0] * 11)

        # 1. 材料类（累计值，直接相减）
        result = {
            'break_material': total[3] - current[3],
            'low_yixiang': total[0] - current[0],
            'mid_yixiang': total[1] - current[1],
            'high_yixiang': total[2] - current[2],
            'gold': total[7] - current[7],
        }

        # 2. 攻略书（基于总经验值动态最优分配）
        total_exp = self._get_total_exp(curr_level, target_level)
        
        # 优先使用特级攻略（20000经验）
        exp_high = total_exp // 20000
        remainder = total_exp % 20000
        
        # 再使用资深攻略（5000经验）
        exp_mid = remainder // 5000
        remainder = remainder % 5000
        
        # 最后使用新锐攻略（1000经验）
        exp_low = remainder // 1000
        remainder = remainder % 1000
        
        # 如果还有剩余经验不足1000，需要1本新锐攻略
        if remainder > 0:
            exp_low += 1

        result['exp_high'] = exp_high
        result['exp_mid'] = exp_mid
        result['exp_low'] = exp_low

        return result

    def _get_total_arc_exp(self, curr_level, target_level):
        """计算当前弧盘等级到目标等级所需的总经验值
        
        经验值在表中以分段值存储（index 10），需累加各段
        """
        if curr_level >= target_level:
            return 0
        
        levels = sorted(ARC_LEVEL_UP_DATA.keys())
        
        total_exp = 0
        for lvl in levels:
            if lvl > curr_level and lvl <= target_level:
                data = ARC_LEVEL_UP_DATA.get(lvl, [0] * 13)
                total_exp += data[10]  # 累计经验（分段值）
        
        return total_exp

    def calc_arc_gap(self, curr_level, target_level):
        """计算弧盘强化缺口"""
        if curr_level >= target_level:
            return {
                'low_arc': 0,
                'mid_arc': 0,
                'high_arc': 0,
                'low_yixiang': 0,
                'mid_yixiang': 0,
                'high_yixiang': 0,
                'dye_light': 0,
                'dye_colorless': 0,
                'dye_chaos': 0,
                'gold': 0,
            }

        total = ARC_LEVEL_UP_DATA.get(target_level, [0] * 13)
        current = ARC_LEVEL_UP_DATA.get(curr_level, [0] * 13)

        # 1. 材料类（累计值，直接相减）
        result = {
            'low_arc': total[0] - current[0],
            'mid_arc': total[1] - current[1],
            'high_arc': total[2] - current[2],
            'low_yixiang': total[3] - current[3],
            'mid_yixiang': total[4] - current[4],
            'high_yixiang': total[5] - current[5],
            'gold': total[9] - current[9],
        }

        # 2. 染剂（基于总经验值动态最优分配）
        total_exp = self._get_total_arc_exp(curr_level, target_level)
        
        # 优先使用混沌染剂（10000经验）
        dye_chaos = total_exp // 10000
        remainder = total_exp % 10000
        
        # 再使用无彩染剂（2500经验）
        dye_colorless = remainder // 2500
        remainder = remainder % 2500
        
        # 最后使用淡色染剂（500经验）
        dye_light = remainder // 500
        remainder = remainder % 500
        
        # 如果还有剩余经验不足500，需要1份淡色染剂
        if remainder > 0:
            dye_light += 1

        result['dye_chaos'] = dye_chaos
        result['dye_colorless'] = dye_colorless
        result['dye_light'] = dye_light

        return result

    def get_character_materials(self, char_name):
        """获取角色材料名称（替代 VLOOKUP）"""
        data = CHARACTER_MATERIAL_MAP.get(char_name)
        if not data:
            return None
        return {
            'break_material': data[0],
            'low_yixiang': data[1],
            'mid_yixiang': data[2],
            'high_yixiang': data[3],
            'boss': data[4],
            'boss_location': data[5],
        }

    def get_arc_materials(self, arc_name):
        """获取弧盘材料名称（替代 VLOOKUP）"""
        data = ARC_MATERIAL_MAP.get(arc_name)
        if not data:
            return None
        return {
            'category': data[0],
            'low_yixiang': data[1],
            'mid_yixiang': data[2],
            'high_yixiang': data[3],
            'low_arc': data[4],
            'mid_arc': data[5],
            'high_arc': data[6],
        }

    def calc_craft_conversion(self, material_name, target_count):
        """计算材料合成换算"""
        result = []
        current_material = material_name
        current_count = target_count

        while current_material:
            craft_info = MATERIAL_CRAFT_MAP.get(current_material)
            if not craft_info or not craft_info.get('next'):
                break

            result.append({
                'material': current_material,
                'count': current_count,
                'cost': craft_info['count'] * current_count  # 合成所需的下级材料数量
            })

            current_count = craft_info['count'] * current_count
            current_material = craft_info.get('next')

        return result

    def calc_yixiang_conversion(self, yixiang_name, target_count):
        """计算异像素材升级换算"""
        result = []
        current_material = yixiang_name
        current_count = target_count

        while current_material:
            series_info = YIXIANG_SERIES_MAP.get(current_material)
            if not series_info or not series_info['next']:
                break

            craft_info = MATERIAL_CRAFT_MAP.get(current_material)
            if craft_info:
                result.append({
                    'material': current_material,
                    'count': current_count,
                    'cost': craft_info['cost'] * current_count,
                    'next': series_info['next']
                })

            current_count = craft_info['count'] * current_count if craft_info else 0
            current_material = series_info['next']

        return result

    def get_all_characters(self):
        """获取所有角色名"""
        return list(CHARACTER_MATERIAL_MAP.keys())

    def get_all_arcs(self):
        """获取所有弧盘名"""
        return list(ARC_MATERIAL_MAP.keys())
