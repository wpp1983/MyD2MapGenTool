#!/usr/bin/env python3

from map_visualizer import MapVisualizer
import sys

def main():
    print("=" * 50)
    print("游戏地图制作工具 - 暗黑2风格")
    print("=" * 50)
    print("\n特性:")
    print("• 基于区块的地形生成算法")
    print("• 支持5种地形类型: 高地、悬崖、平原、森林、河流")
    print("• 智能边缘匹配系统")
    print("• 实时参数调节")
    print("• 导出功能 (JSON + PNG)")
    print("\n操作说明:")
    print("• 点击 'Generate New' 生成新地图")
    print("• 拖动 'Seed' 滑块调节随机种子")
    print("• 点击 'Export' 导出当前地图")
    print("• 黑色网格线显示区块边界")
    print("• 区块中心显示模板名称")
    
    try:
        print("\n启动可视化界面...")
        visualizer = MapVisualizer(tile_width=12, tile_height=10)
        visualizer.show()
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"\n错误: {e}")
        print("请确保已安装所需依赖: pip install matplotlib numpy")

if __name__ == "__main__":
    main()