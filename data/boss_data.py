"""
异环 NTE 角色突破材料（BOSS）数据
来源：从角色材料对照表推导 BOSS 分组
支持从 JSON 文件加载和保存（数据持久化）
"""
import os
import json
from data.character_data import CHARACTER_MATERIAL_MAP

# ==================== 数据文件路径 ====================
_USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_data")
_BOSS_JSON_PATH = os.path.join(_USER_DATA_DIR, "boss_data.json")


def _build_default_boss_data():
    """从 CHARACTER_MATERIAL_MAP 推导默认 BOSS 数据"""
    boss_map = {}
    for char_name, materials in CHARACTER_MATERIAL_MAP.items():
        boss_name = materials[4]
        boss_location = materials[5]
        if boss_name not in boss_map:
            boss_map[boss_name] = {
                "location": boss_location,
                "characters": []
            }
        boss_map[boss_name]["characters"].append(char_name)
    
    # 转为有序列表格式
    result = {}
    # 按原始 BOSS 出现顺序排列
    seen = []
    for char_name, materials in CHARACTER_MATERIAL_MAP.items():
        boss_name = materials[4]
        if boss_name not in seen:
            seen.append(boss_name)
    for boss_name in seen:
        data = boss_map[boss_name]
        result[boss_name] = [
            data["location"],
            ", ".join(data["characters"])
        ]
    return result


def load_boss_data():
    """从 JSON 文件加载 BOSS 数据，不存在则从角色数据推导"""
    if os.path.exists(_BOSS_JSON_PATH):
        try:
            with open(_BOSS_JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 验证格式
                validated = {}
                for key, value in data.items():
                    if isinstance(value, list) and len(value) >= 2:
                        validated[key] = [value[0], value[1]]
                    else:
                        validated[key] = value
                return validated
        except (json.JSONDecodeError, OSError) as e:
            print(f"读取 BOSS 数据文件失败: {e}，使用推导数据")
    
    return _build_default_boss_data()


def save_boss_data(data_map):
    """保存 BOSS 数据到 JSON 文件"""
    os.makedirs(_USER_DATA_DIR, exist_ok=True)
    try:
        with open(_BOSS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data_map, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"保存 BOSS 数据文件失败: {e}")


def rebuild_from_character_map():
    """从角色材料对照表重建 BOSS 数据并保存"""
    data = _build_default_boss_data()
    save_boss_data(data)
    return data


# ==================== 模块级变量（供其他模块导入使用） ====================
BOSS_MATERIAL_MAP = load_boss_data()
