# 异环 NTE 全角色养成计算器 (Python版)

基于 openpyxl 的 Excel 自动生成工具，用于异环(NTE)角色养成材料缺口计算。

## 功能特性

- **自动匹配材料**：录入角色名/弧盘名，自动从对照表匹配材料名称
- **缺口自动计算**：输入当前等级→目标等级，自动计算所需材料数量
- **多角色汇总**：支持10个角色批量录入，一键汇总全队缺口
- **联动副表**：角色突破材料总表、弧盘强化总表、全角色/弧盘材料对照、材料合成换算等

## 项目结构

```
nte_calculator_project/
├── main.py                          # 主入口
├── config.py                        # 全局配置（颜色、路径、样式）
├── data/
│   ├── character_data.py            # 角色突破材料数据
│   ├── arc_data.py                  # 弧盘强化材料数据
│   └── material_data.py             # 材料合成/周本/经验书数据
├── generators/
│   ├── calculator_generator.py      # 养成计算器主表生成
│   ├── character_sheet_generator.py # 角色等级突破材料总表
│   ├── arc_sheet_generator.py       # 弧盘强化总表
│   └── other_sheets_generator.py    # 其他副表（周本/合成/对照等）
├── utils/
│   ├── styles.py                    # Excel样式工具
│   └── formula_builder.py           # 公式构建工具
├── requirements.txt
└── README.md
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python main.py
```

生成的 Excel 文件将保存在 `output/` 目录下。

## 数据维护

所有材料数据集中在 `data/` 目录下的 Python 文件中，当游戏版本更新时，直接修改对应数据字典即可，无需改动生成逻辑。

## 颜色规范

| 颜色 | 区域 | 含义 |
|------|------|------|
| 🟨 黄色 | 录入区 | 手动填写角色名、等级等 |
| 🟦 浅蓝 | 名称区 | VLOOKUP自动匹配的材料名称 |
| 🟩 绿色 | 计算区 | SUMIF自动计算的缺口数量 |
| 🟧 橙色 | 汇总区 | 总金币、总异像素材等汇总 |
| 🟥 红色 | 汇总行 | 全队10个角色的SUM汇总 |

## 作者
兔唧唧的萝卜酱
