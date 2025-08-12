import os
import sys
import json
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button, Slider
import numpy as np
from typing import Optional
from cell_map_generator import CellBasedMap
from terrain_types import TerrainType, Cell


# WSL环境检测和配置
def setup_matplotlib_backend():
    """检测运行环境并配置matplotlib后端"""
    # 检查是否在WSL环境中
    is_wsl = (
        "microsoft" in os.uname().release.lower() if hasattr(os, "uname") else False
    )

    if is_wsl:
        print("检测到WSL环境，配置matplotlib后端...")

        # 检查DISPLAY环境变量
        if "DISPLAY" not in os.environ:
            print("❌ 错误: DISPLAY环境变量未设置")
            print("解决方案:")
            print("1. 安装Windows X11服务器 (推荐VcXsrv)")
            print("   下载: https://sourceforge.net/projects/vcxsrv/")
            print("2. 启动VcXsrv并设置环境变量:")
            print("   export DISPLAY=:0")
            print("3. 或者使用Windows终端中的WSL")
            # 强制使用Agg后端
            matplotlib.use("Agg")
            print("🔧 已设置为Agg后端 (无GUI模式)")
            return False

        # 尝试设置TkAgg后端
        try:
            matplotlib.use("TkAgg")
            print(f"✅ 已设置matplotlib后端: {matplotlib.get_backend()}")
        except Exception as e:
            print(f"❌ 无法设置TkAgg后端: {e}")
            print("尝试使用Agg后端（无GUI）")
            matplotlib.use("Agg")
            return False

    return True


# 在导入其他组件前配置后端
_gui_available = setup_matplotlib_backend()


class MapVisualizer:
    def __init__(
        self,
        width: int = 80,
        height: int = 64,
        headless: bool = False,
        output_dir: str = None,
        phase: int = None,
    ):
        self.width = width
        self.height = height
        self.phase = phase
        
        self.map_generator = CellBasedMap(width, height, phase=phase)
            
        self.current_seed = 42
        self.headless = headless or not _gui_available
        self.output_dir = output_dir

        if not self.headless:
            self.fig = plt.figure(figsize=(16, 8))
            # 创建网格布局：左侧地图，右侧统计信息
            gs = self.fig.add_gridspec(1, 2, width_ratios=[3, 1], hspace=0.3)
            self.ax = self.fig.add_subplot(gs[0, 0])
            self.stats_ax = self.fig.add_subplot(gs[0, 1])
            plt.subplots_adjust(bottom=0.25, right=0.95)
            self._setup_ui()

        self._generate_and_display()

    def _setup_ui(self):
        ax_generate = plt.axes([0.1, 0.1, 0.15, 0.04])
        self.btn_generate = Button(ax_generate, "Generate New")
        self.btn_generate.on_clicked(self._on_generate_clicked)

        ax_seed = plt.axes([0.3, 0.1, 0.4, 0.03])
        self.slider_seed = Slider(
            ax_seed, "Seed", 1, 1000, valinit=self.current_seed, valstep=1
        )
        self.slider_seed.on_changed(self._on_seed_changed)

        ax_export = plt.axes([0.75, 0.1, 0.15, 0.04])
        self.btn_export = Button(ax_export, "Export")
        self.btn_export.on_clicked(self._on_export_clicked)

    def _generate_and_display(self):
        # 重新创建生成器并生成地图
        self.map_generator = CellBasedMap(self.width, self.height, phase=self.phase)
        self.map_generator.generate_map(seed=self.current_seed)

        if self.headless:
            print(f"✅ 地图生成完成 (种子: {self.current_seed})")
            print(f"地图尺寸: {self.width}x{self.height} 格子")
            
            # 显示地形统计
            distribution = self.map_generator.get_terrain_distribution()
            print("\n地形分布:")
            total = sum(distribution.values())
            for terrain, count in distribution.items():
                percentage = (count / total) * 100
                print(f"  {terrain}: {count} ({percentage:.1f}%)")
            
            # 显示区域分析
            self.map_generator.print_region_analysis()
        else:
            self._display_map()

    def _get_color_mapping(self):
        """获取地形颜色映射，使用配置中的颜色"""
        from terrain_types import Cell, TerrainType

        terrain_color_map = Cell.get_color_map()

        # 动态创建颜色映射
        TerrainType.initialize_from_config()
        terrain_types = TerrainType.get_all_types()

        color_map = {}
        for i, terrain_str in enumerate(terrain_types):
            try:
                terrain_type = TerrainType.from_string(terrain_str)
                # 从配置加载的颜色映射中获取颜色
                color = terrain_color_map.get(terrain_type, [0.5, 0.5, 0.5])
                color_map[i] = color
            except (ValueError, KeyError):
                # 如果地形类型不存在或没有配置颜色，使用默认灰色
                color_map[i] = [0.5, 0.5, 0.5]

        return color_map

    def _display_map(self):
        self.ax.clear()
        self.stats_ax.clear()

        terrain_array = self.map_generator.to_array()

        # 使用统一的颜色映射
        color_map = self._get_color_mapping()

        colored_map = np.zeros((terrain_array.shape[0], terrain_array.shape[1], 3))
        for terrain_value, color in color_map.items():
            mask = terrain_array == terrain_value
            colored_map[mask] = color

        self.ax.imshow(colored_map, origin="upper", interpolation="nearest")

        # 动态生成图例
        from terrain_types import TerrainType

        TerrainType.initialize_from_config()
        terrain_types = TerrainType.get_all_types()

        legend_elements = []
        for i, terrain_str in enumerate(terrain_types):
            if i in color_map:
                # 将地形类型字符串首字母大写作为显示标签
                label = terrain_str.capitalize()
                legend_elements.append(patches.Patch(color=color_map[i], label=label))

        self.ax.legend(
            handles=legend_elements, loc="upper right", bbox_to_anchor=(1.02, 1)
        )

        self.ax.set_title(f"Generated Map (Seed: {self.current_seed})")
        self.ax.set_xlabel("X Coordinate")
        self.ax.set_ylabel("Y Coordinate")

        # 显示区域统计信息
        self._display_region_stats()

        self.fig.canvas.draw()

    def _display_region_stats(self):
        """在右侧面板显示区域统计信息"""
        self.stats_ax.clear()
        self.stats_ax.axis('off')  # 隐藏坐标轴
        
        # 获取区域分析数据
        regions = self.map_generator.analyze_regions()
        total_regions = sum(stats['region_count'] for stats in regions.values())
        
        # 获取地形描述
        terrain_descriptions = self.map_generator._get_terrain_descriptions()
        
        # 计算连贯性指标
        total_cells = sum(stats['total_cells'] for stats in regions.values())
        connectivity_score = (total_cells / total_regions) if total_regions > 0 else 0
        
        # 构建显示文本
        y_pos = 0.95
        y_step = 0.05
        
        # 标题
        self.stats_ax.text(0.05, y_pos, "Region Statistics", fontsize=14, fontweight='bold', 
                          transform=self.stats_ax.transAxes)
        y_pos -= y_step * 1.5
        
        # 总体信息
        self.stats_ax.text(0.05, y_pos, f"Total Regions: {total_regions}", fontsize=11,
                          transform=self.stats_ax.transAxes)
        y_pos -= y_step
        
        self.stats_ax.text(0.05, y_pos, f"Map Size: {self.width}×{self.height}", fontsize=11,
                          transform=self.stats_ax.transAxes)
        y_pos -= y_step
        
        self.stats_ax.text(0.05, y_pos, f"Coherence: {connectivity_score:.1f}", fontsize=11,
                          transform=self.stats_ax.transAxes)
        y_pos -= y_step * 1.5
        
        # 连贯性评价
        if connectivity_score >= 50:
            connectivity_text = "Excellent"
            color = 'green'
        elif connectivity_score >= 25:
            connectivity_text = "Good"
            color = 'orange'
        else:
            connectivity_text = "Poor"
            color = 'red'
            
        self.stats_ax.text(0.05, y_pos, connectivity_text, fontsize=10, color=color,
                          transform=self.stats_ax.transAxes)
        y_pos -= y_step * 2
        
        # 各地形详细信息
        for terrain, stats in regions.items():
            if stats['region_count'] > 0:
                description = terrain_descriptions.get(terrain, terrain)
                
                # 地形名称
                self.stats_ax.text(0.05, y_pos, f"{terrain.capitalize()}", 
                                  fontsize=12, fontweight='bold',
                                  transform=self.stats_ax.transAxes)
                y_pos -= y_step
                
                # 区域数量
                self.stats_ax.text(0.1, y_pos, f"Regions: {stats['region_count']}", 
                                  fontsize=10, transform=self.stats_ax.transAxes)
                y_pos -= y_step * 0.8
                
                # 总格子数和百分比
                percentage = (stats['total_cells'] / total_cells) * 100
                self.stats_ax.text(0.1, y_pos, f"Coverage: {percentage:.1f}% ({stats['total_cells']})", 
                                  fontsize=10, transform=self.stats_ax.transAxes)
                y_pos -= y_step * 0.8
                
                # 最大区域
                self.stats_ax.text(0.1, y_pos, f"Largest: {stats['largest_region']} cells", 
                                  fontsize=10, transform=self.stats_ax.transAxes)
                y_pos -= y_step * 0.8
                
                # 平均大小
                self.stats_ax.text(0.1, y_pos, f"Average: {stats['average_region_size']:.1f}", 
                                  fontsize=10, transform=self.stats_ax.transAxes)
                y_pos -= y_step * 0.8
                
                # 区域分布
                sizes = stats['region_sizes']
                if len(sizes) > 0:
                    small = sum(1 for s in sizes if s < 20)
                    medium = sum(1 for s in sizes if 20 <= s < 100)
                    large = sum(1 for s in sizes if s >= 100)
                    
                    self.stats_ax.text(0.1, y_pos, f"S:{small} M:{medium} L:{large}", 
                                      fontsize=9, color='gray',
                                      transform=self.stats_ax.transAxes)
                    y_pos -= y_step * 1.5
                else:
                    y_pos -= y_step
                    
        # 设置统计面板标题
        self.stats_ax.set_title("Region Analysis", fontsize=12, pad=20)


    def _on_generate_clicked(self, event):
        self.current_seed = np.random.randint(1, 1000)
        self.slider_seed.set_val(self.current_seed)
        self._generate_and_display()

    def _on_seed_changed(self, val):
        self.current_seed = int(val)
        self._generate_and_display()

    def _on_export_clicked(self, event):
        self._export_map()

    def _export_map(self):
        import json
        import os
        from datetime import datetime

        # 获取输出目录路径
        if self.output_dir and self.output_dir != ".":
            # 用户指定了非默认目录
            output_dir = self.output_dir
        else:
            # 默认或者"."都使用output目录（特别是无GUI模式）
            current_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(current_dir)
            output_dir = os.path.join(project_root, "output")

        # 确保output目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 获取当前时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        export_data = {
            "width": self.width,
            "height": self.height,
            "seed": self.current_seed,
            "generation_timestamp": timestamp,
            "terrain_data": [],
            "generation_type": "cell_based"
        }

        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = self.map_generator.get_cell(x, y)
                row.append(str(cell.terrain_type) if cell else "plain")
            export_data["terrain_data"].append(row)

        # 文件名格式: timestamp_seed_XXXX
        filename = os.path.join(output_dir, f"{timestamp}_seed_{self.current_seed}.json")
        with open(filename, "w") as f:
            json.dump(export_data, f, indent=2)

        # 创建图像用于导出
        if self.headless:
            # 无GUI模式：创建新的figure而不是使用self.fig
            fig, ax = plt.subplots(figsize=(10, 8))
        else:
            # GUI模式：使用plt.figure
            plt.figure(figsize=(10, 8))
            ax = plt.gca()

        terrain_array = self.map_generator.to_array()

        # 使用统一的颜色映射
        color_map = self._get_color_mapping()

        colored_map = np.zeros((terrain_array.shape[0], terrain_array.shape[1], 3))
        for terrain_value, color in color_map.items():
            mask = terrain_array == terrain_value
            colored_map[mask] = color

        if self.headless:
            ax.imshow(colored_map, origin="upper", interpolation="nearest")
            ax.set_title(f"Generated Map (Seed: {self.current_seed}, {timestamp})")
            ax.axis("off")
        else:
            plt.imshow(colored_map, origin="upper", interpolation="nearest")
            plt.title(f"Exported Map (Seed: {self.current_seed})")
            plt.axis("off")

        # PNG文件名也使用相同的时间戳格式
        image_filename = os.path.join(output_dir, f"{timestamp}_seed_{self.current_seed}.png")

        if self.headless:
            fig.savefig(image_filename, dpi=150, bbox_inches="tight")
            plt.close(fig)
        else:
            plt.savefig(image_filename, dpi=150, bbox_inches="tight")
            plt.close()

        print(f"Map exported as {os.path.basename(filename)} and {os.path.basename(image_filename)}")

    def show(self):
        if self.headless:
            print("在无GUI模式下运行，生成地图并保存...")
            self._export_map()
        else:
            try:
                plt.show()
            except Exception as e:
                print(f"GUI显示失败: {e}")
                print("切换到无GUI模式，生成地图并保存...")
                self._export_map()


if __name__ == "__main__":
    visualizer = MapVisualizer()
    visualizer.show()
