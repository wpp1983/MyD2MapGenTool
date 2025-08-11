#!/usr/bin/env python3
"""
游戏地图制作工具 - 统一入口
基于配置文件的智能启动脚本
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from app_config import AppConfig

def setup_matplotlib_backend(config: AppConfig):
    """根据配置设置matplotlib后端"""
    import matplotlib
    
    # 检查是否启用GUI
    if not config.is_gui_enabled():
        matplotlib.use('Agg')
        if config.is_verbose_output():
            print("🔧 配置禁用GUI，使用Agg后端")
        return False
    
    # 自动检测WSL环境
    is_wsl = 'microsoft' in os.uname().release.lower() if hasattr(os, 'uname') else False
    
    if is_wsl and config.is_verbose_output():
        print("🔍 检测到WSL环境，配置matplotlib后端...")
    
    # 检查DISPLAY环境变量
    has_display = 'DISPLAY' in os.environ and os.environ['DISPLAY']
    
    if not has_display and config.should_auto_set_display():
        display_value = config.get_default_display()
        os.environ['DISPLAY'] = display_value
        if config.is_verbose_output():
            print(f"🔧 自动设置 DISPLAY={display_value}")
        has_display = True
    
    # 根据环境选择后端
    if has_display:
        try:
            matplotlib.use('TkAgg')
            if config.is_verbose_output():
                print(f"✅ 已设置matplotlib后端: {matplotlib.get_backend()}")
            return True
        except Exception as e:
            if config.is_verbose_output():
                print(f"❌ 无法设置TkAgg后端: {e}")
                print("🔧 切换到Agg后端 (无GUI模式)")
            matplotlib.use('Agg')
            return False
    else:
        matplotlib.use('Agg')
        if config.is_verbose_output():
            print("🔧 无DISPLAY环境变量，使用Agg后端 (无GUI模式)")
        return False

def print_banner(config: AppConfig):
    """打印程序横幅"""
    if not config.is_verbose_output():
        return
        
    print("==================================================")
    print("游戏地图制作工具 - 暗黑2风格")
    print("==================================================")
    print()
    print("特性:")
    print("• 基于区块的地形生成算法")
    print("• 支持5种地形类型: 高地、悬崖、平原、森林、斜坡")
    print("• 智能边缘匹配系统")
    print("• 实时参数调节 (GUI模式)")
    print("• 导出功能 (JSON + PNG)")
    print("• 简化配置")
    print()

def get_user_choice(config: AppConfig) -> str:
    """获取用户运行模式选择"""
    if not config.should_show_user_choice():
        return '1'  # 默认GUI模式
    
    print("选择运行模式:")
    print("1. GUI界面模式 (交互式)")
    print("2. 无GUI模式 (批量生成)")
    print()
    
    try:
        choice = input("请选择 (1/2) [默认: 1]: ").strip()
        return choice if choice in ['1', '2'] else '1'
    except (KeyboardInterrupt, EOFError):
        print("\n使用默认GUI模式...")
        return '1'

def run_gui_mode(config: AppConfig):
    """运行GUI模式"""
    from map_visualizer import MapVisualizer
    
    tile_width, tile_height = config.get_default_map_size()
    
    if config.is_verbose_output():
        print("启动GUI界面...")
    
    try:
        visualizer = MapVisualizer(tile_width=tile_width, tile_height=tile_height)
        visualizer.show()
    except Exception as e:
        if config.is_verbose_output():
            print(f"❌ GUI启动失败: {e}")
            print("可能的原因:")
            print("- X11服务器未运行")
            print("- WSL的X11转发配置有问题")
            print("- 缺少必要的GUI库")
        
        if config.should_fallback_to_headless():
            if config.is_verbose_output():
                print("🔄 自动切换到无GUI模式...")
            run_headless_mode(config)
        else:
            if config.is_verbose_output():
                print("程序退出")
            sys.exit(1)

def run_headless_mode(config: AppConfig):
    """运行无GUI模式"""
    from map_visualizer import MapVisualizer
    
    if config.is_verbose_output():
        print()
        print("=== 无GUI模式 ===")
    
    seeds = config.get_headless_batch_seeds()
    tile_width, tile_height = config.get_default_map_size()
    
    if config.is_verbose_output():
        print(f"将生成{len(seeds)}个不同种子的地图并自动保存")
        print()
    
    for i, seed in enumerate(seeds, 1):
        if config.is_verbose_output():
            print(f"[{i}/{len(seeds)}] 生成地图 (种子: {seed})...")
        
        visualizer = MapVisualizer(tile_width=tile_width, tile_height=tile_height, headless=True)
        visualizer.current_seed = seed
        visualizer._generate_and_display()
        
        if config.should_auto_export_headless():
            visualizer._export_map()
        
        if config.is_verbose_output():
            print()
    
    if config.is_verbose_output():
        print("✅ 所有地图已生成完成!")
        print("文件保存在当前目录:")
        print("  • map_seed_*.json (地图数据)")
        print("  • map_seed_*.png (地图图像)")
        
        # 显示WSL配置提示
        is_wsl = 'microsoft' in os.uname().release.lower() if hasattr(os, 'uname') else False
        if is_wsl:
            print()
            print("WSL GUI配置提示:")
            print("1. 安装Windows X11服务器:")
            print("   https://sourceforge.net/projects/vcxsrv/")
            print("2. 启动VcXsrv并配置:")
            print("   - 选择 'Multiple windows'")
            print("   - 勾选 'Disable access control'")
            print("3. 设置环境变量:")
            print("   export DISPLAY=:0")
            print("4. 或修改config.json设置 'ui.enable_gui': false")

def main():
    """主函数"""
    # 加载配置
    config = AppConfig()
    
    # 打印横幅
    print_banner(config)
    
    # 设置matplotlib后端
    gui_available = setup_matplotlib_backend(config)
    
    # 决定运行模式
    if not config.is_gui_enabled():
        if config.is_verbose_output():
            print("🔧 配置禁用GUI，运行无GUI模式")
        run_headless_mode(config)
    elif not gui_available:
        if config.is_verbose_output():
            print("🔧 GUI不可用，运行无GUI模式")
        run_headless_mode(config)
    else:
        # GUI可用，询问用户选择
        choice = get_user_choice(config)
        
        if choice == '2':
            if config.is_verbose_output():
                print("用户选择无GUI模式...")
            run_headless_mode(config)
        else:
            run_gui_mode(config)

if __name__ == "__main__":
    main()