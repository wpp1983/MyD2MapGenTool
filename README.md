# 游戏地图制作工具 (MyMapGenTool)

基于区块拼接算法的游戏地图生成工具，参考暗黑破坏神2的地图生成机制。

## 特性

- **基于区块的地形生成**: 采用预制区块模板 + 随机拼接算法
- **5种地形类型**: 高地、悬崖、平原、森林、河流
- **智能边缘匹配**: 区块间的智能连接验证系统
- **实时可视化**: 交互式地图显示和参数调节
- **导出功能**: 支持JSON数据和PNG图片导出
- **交互式编辑**: 手动编辑地形，保存自定义模板

## 安装依赖

### 使用 Poetry (推荐)
```bash
# 安装 Poetry (如果尚未安装)
curl -sSL https://install.python-poetry.org | python3 -

# 安装项目依赖
poetry install

# 激活虚拟环境
poetry shell
```

### 使用 pip (传统方式)
```bash
pip install -r requirements.txt
```

## 快速开始

### 基础演示
```bash
# 使用 Poetry
poetry run python demo.py

# 或在激活的虚拟环境中
python demo.py
```

### 交互式编辑器
```bash
# 使用 Poetry
poetry run python interactive_editor.py

# 或在激活的虚拟环境中
python interactive_editor.py
```

## 核心组件

### 1. terrain_types.py
- 地形类型枚举 (TerrainType)
- 边缘类型定义 (EdgeType)  
- 区块模板类 (TileTemplate)
- 地形格子类 (TerrainCell)

### 2. map_generator.py
- 基于区块的地图生成器 (TileBasedMap)
- 预制模板创建
- 区块连接规则验证
- 随机拼接算法

### 3. map_visualizer.py
- 地图可视化界面
- 实时参数调节
- 地图导出功能
- 区块网格显示

### 4. interactive_editor.py
- 交互式编辑功能
- 手动地形编辑
- 自定义模板保存
- 编辑历史跟踪

## 使用方法

1. **生成新地图**: 点击 "Generate New" 按钮
2. **调节种子**: 拖动 "Seed" 滑块改变随机种子
3. **导出地图**: 点击 "Export" 导出JSON和PNG文件
4. **编辑模式**: 启用编辑模式，手动修改地形
5. **保存模板**: 将编辑后的区域保存为自定义模板

## 算法原理

### 区块系统
- 地图由 M×N 个固定大小的区块组成
- 每个区块都有预定义的地形模式
- 区块边缘带有类型标识用于匹配

### 拼接规则
- 相邻区块的边缘类型必须兼容
- 支持完全匹配和兼容匹配两种模式
- 河流、森林等有特殊的连接规则

### 权重系统
- 每个模板都有权重值影响选择概率
- 平原权重最高，悬崖权重最低
- 通过权重调节控制地形分布

## 输出文件

### JSON格式
```json
{
  "width": 96,
  "height": 80,
  "tile_width": 12,
  "tile_height": 10,
  "seed": 42,
  "terrain_data": [...]
}
```

### PNG图片
- 彩色地形图
- 高分辨率输出
- 适合游戏引擎导入

## 扩展功能

- 添加新的地形类型
- 创建更多区块模板
- 实现更复杂的连接规则
- 添加高度信息和路径寻找

## 技术架构

- **Python 3.7+**
- **Poetry**: 依赖管理和包管理
- **NumPy**: 数组操作和数值计算
- **Matplotlib**: 可视化和用户界面
- **面向对象设计**: 模块化和可扩展性

## 开发工具

```bash
# 代码格式化
poetry run black .

# 代码检查
poetry run flake8 .

# 运行测试
poetry run pytest
```