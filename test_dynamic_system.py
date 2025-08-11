#!/usr/bin/env python3
"""
简单测试脚本来验证动态类型系统是否正常工作
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from terrain_types import TerrainType, EdgeType
from template_loader import TemplateLoader
from map_generator import TileBasedMap

def test_dynamic_types():
    """测试动态类型系统"""
    print("🧪 测试动态类型系统...")
    
    # 初始化类型系统
    TerrainType.initialize_from_config()
    EdgeType.initialize_from_config()
    
    print(f"✅ 地形类型: {TerrainType.get_all_types()}")
    print(f"✅ 边缘类型: {EdgeType.get_all_types()}")
    
    # 测试类型转换
    for terrain_str in TerrainType.get_all_types():
        terrain_type = TerrainType.from_string(terrain_str)
        print(f"   {terrain_str} -> {terrain_type}")
    
    print("✅ 动态类型系统正常工作")

def test_template_loading():
    """测试模板加载"""
    print("\n🧪 测试模板加载...")
    
    loader = TemplateLoader()
    templates = loader.create_templates(tile_size=8)
    
    print(f"✅ 成功加载 {len(templates)} 个模板")
    for template in templates:
        print(f"   模板: {template.name}, 边缘: N={template.north_edge}, S={template.south_edge}, E={template.east_edge}, W={template.west_edge}")
    
    print("✅ 模板加载正常工作")

def test_map_generation():
    """测试地图生成"""
    print("\n🧪 测试地图生成...")
    
    map_gen = TileBasedMap(tile_width=3, tile_height=3)
    map_gen.generate_map(seed=42)
    
    print(f"✅ 成功生成 {map_gen.tile_width}x{map_gen.tile_height} 地图")
    
    # 检查地形类型
    terrain_types_found = set()
    for y in range(map_gen.height):
        for x in range(map_gen.width):
            cell = map_gen.grid[y][x]
            terrain_types_found.add(cell.terrain_type)
    
    print(f"✅ 发现地形类型: {list(terrain_types_found)}")
    
    # 测试数组转换
    array = map_gen.to_array()
    print(f"✅ 数组转换成功，形状: {array.shape}")
    
    print("✅ 地图生成正常工作")

def main():
    """主函数"""
    print("=" * 50)
    print("动态地形类型系统测试")
    print("=" * 50)
    
    try:
        test_dynamic_types()
        test_template_loading()
        test_map_generation()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试通过！动态类型系统工作正常！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
