# 游戏地图制作工具 (MyMapGenTool)

基于区块拼接算法的游戏地图生成工具，参考暗黑破坏神2的地图生成机制。

## 项目结构

```
MyMapGenTool/
├── D2MapGenTool.py     # 主程序入口
├── src/                # 源代码文件夹
│   ├── __init__.py
│   ├── app_config.py          # 配置加载器
│   ├── map_generator.py       # 地图生成核心
│   ├── map_visualizer.py      # 地图可视化
│   ├── terrain_types.py       # 地形类型定义
│   ├── template_loader.py     # 模板加载器
│   └── interactive_editor.py  # 交互式编辑器
├── config/             # 配置文件夹
│   ├── config.json            # 主配置文件
│   └── templates_config.json  # 地形模板配置
├── output/             # 输出文件夹
│   └── README.md              # 输出说明
├── pyproject.toml      # Poetry项目配置
└── README.md           # 项目说明
```

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


## 快速开始

### 基础演示
```bash
# 使用 Poetry (推荐)
poetry run python D2MapGenTool.py

# 或在激活的虚拟环境中
python D2MapGenTool.py
```

程序会自动：
- 检测运行环境 (WSL/标准系统)
- 配置合适的matplotlib后端
- 根据配置文件选择GUI/无GUI模式
- 在GUI失败时自动回退到无GUI模式

### 交互式编辑器
```bash
# 使用 Poetry
poetry run python src/interactive_editor.py

# 或在激活的虚拟环境中
python src/interactive_editor.py
```

## 配置文件

### config/config.json
程序使用 `config/config.json` 进行简单配置：

```json
{
  "ui": {
    "enable_gui": true   // true: 启用GUI模式, false: 强制无GUI模式
  }
}
```

- **GUI模式** (`enable_gui: true`): 显示交互界面，支持实时调整参数
- **无GUI模式** (`enable_gui: false`): 批量生成地图并自动保存文件

其他设置已优化为智能默认值：
- 自动检测WSL环境
- 自动配置DISPLAY环境变量  
- GUI失败时自动回退到无GUI模式
- 默认地图大小: 12x10瓦片
- 无GUI模式默认生成3个地图 (种子: 42, 123, 456)

### templates_config.json
地形模板和游戏规则配置：

```json
{
  "templates": [...],              // 地形模板定义
  "terrain_types": {...},          // 地形类型映射
  "terrain_colors": {...},         // 地形颜色配置
  "edge_types": {...},             // 边缘类型配置
  "edge_compatibility": [...]      // 边缘兼容性规则
}
```

## WSL环境配置

### 自动配置
程序会自动检测WSL环境并进行配置，但如果GUI无法启动，请按以下步骤配置：

### 手动X11配置
1. **安装X11服务器**
   - 下载VcXsrv: https://sourceforge.net/projects/vcxsrv/
   - 或者Xming: https://sourceforge.net/projects/xming/

2. **启动X11服务器**
   - 运行VcXsrv，选择"Multiple windows"
   - 勾选"Disable access control"
   - 完成配置并启动

3. **设置环境变量**
   ```bash
   export DISPLAY=:0
   # 可以添加到 ~/.bashrc 中永久生效
   echo 'export DISPLAY=:0' >> ~/.bashrc
   ```

4. **安装依赖**
   ```bash
   sudo apt install x11-apps python3-tk
   ```

5. **测试**
   ```bash
   xeyes  # 测试X11是否工作
   poetry run python D2MapGenTool.py  # 运行程序
   ```

### 强制无GUI模式
如果不需要GUI，可以在 `config.json` 中设置：
```json
{
  "ui": {
    "enable_gui": false
  }
}
```

### 核心组件

### 1. D2MapGenTool.py
- **主程序入口**，基于配置文件的智能启动
- 自动环境检测和后端配置
- 支持GUI/无GUI模式切换

### 2. app_config.py
- 配置文件加载和管理
- 支持默认配置和用户配置
- 提供便捷的配置访问方法

### 3. config.json
- **应用配置文件**，控制程序行为
- UI模式配置、显示设置、导出选项等

### 4. terrain_types.py
- 地形类型枚举 (TerrainType)
- 边缘类型定义 (EdgeType)  
- 区块模板类 (TileTemplate)
- 地形格子类 (TerrainCell)

### 5. map_generator.py
- 基于区块的地图生成器 (TileBasedMap)
- 随机拼接算法
- 区块连接规则验证

### 6. template_loader.py
- 模板配置文件加载器
- 支持JSON格式的模板定义
- 灵活的模板模式创建

### 7. templates_config.json
- 模板配置文件
- 定义所有区块模板的地形模式和属性
- 支持单一地形、分割模式等多种模板类型

### 8. map_visualizer.py
- 地图可视化界面
- 实时参数调节
- 地图导出功能
- 区块网格显示

### 9. interactive_editor.py
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

- **修改模板配置**: 编辑 `templates_config.json` 文件添加新模板
- **自定义地形模式**: 支持单一地形、水平/垂直分割、河流等模式
- **调整模板权重**: 通过权重控制不同地形的出现概率
- **添加新的地形类型**: 扩展 `TerrainType` 和 `EdgeType` 枚举
- **创建复杂连接规则**: 实现更复杂的边缘匹配逻辑
- **添加高度信息和路径寻找**: 为游戏引擎集成做准备

### 模板配置示例

**基本模板配置**:
```json
{
  "name": "custom_river",
  "description": "自定义河流模板", 
  "terrain_pattern": {
    "type": "river_horizontal",
    "base": "plain",
    "width": 3
  },
  "edges": {
    "north": "plain",
    "south": "plain", 
    "east": "river",
    "west": "river"
  },
  "weight": 1.0
}
```

**颜色配置**:
```json
{
  "terrain_colors": {
    "plain": [0.4, 0.8, 0.2],
    "forest": [0.1, 0.4, 0.1],
    "highland": [0.8, 0.6, 0.4],
    "cliff": [0.5, 0.5, 0.5],
    "river": [0.2, 0.4, 0.8]
  }
}
```

**兼容性配置**:
```json
{
  "edge_compatibility": [
    ["plain", "forest"],
    ["plain", "highland"], 
    ["plain", "river"]
  ]
}
```

**调试配置**:
```json
{
  "debug": {
    "show_template_names": false,
    "show_grid_lines": true,
    "export_debug_info": true
  }
}
```

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