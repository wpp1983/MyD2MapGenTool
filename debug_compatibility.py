#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from map_generator import TileBasedMap
from terrain_types import EdgeType, TileTemplate
from template_loader import TemplateLoader

def debug_compatibility():
    print("加载模板配置...")
    loader = TemplateLoader()
    compatibility_config = loader.get_edge_compatibility()
    print(f"边缘兼容性配置: {compatibility_config}")
    
    print("\n设置兼容性映射...")
    TileTemplate.set_compatibility_map(compatibility_config)
    print(f"兼容性映射大小: {len(TileTemplate._compatibility_map) if TileTemplate._compatibility_map else 0}")
    
    if TileTemplate._compatibility_map:
        print("兼容性映射内容:")
        for pair in list(TileTemplate._compatibility_map)[:10]:  # 只显示前10个
            print(f"  {pair}")
    
    # 测试具体的边缘
    EdgeType.initialize_from_config()
    plain_edge = EdgeType.from_string("plain")
    forest_edge = EdgeType.from_string("forest")
    
    print(f"\nPlain边缘: {plain_edge}")
    print(f"Forest边缘: {forest_edge}")
    
    if TileTemplate._compatibility_map:
        is_compatible = (plain_edge, forest_edge) in TileTemplate._compatibility_map
        print(f"Plain和Forest兼容: {is_compatible}")

if __name__ == "__main__":
    debug_compatibility()
