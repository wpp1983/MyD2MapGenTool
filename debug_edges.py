#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from map_generator import TileBasedMap
from terrain_types import EdgeType, TileTemplate

def debug_edges():
    print("检查边缘类型...")
    EdgeType.initialize_from_config()
    print("可用边缘类型:", EdgeType.get_all_types())
    
    # 测试边缘转换
    for terrain in ['plain', 'forest', 'highland']:
        try:
            edge = EdgeType.from_string(terrain)
            print(f"{terrain} -> {edge}")
        except ValueError as e:
            print(f"{terrain} -> ERROR: {e}")
    
    print("\n创建地图生成器...")
    map_gen = TileBasedMap(4, 3)
    
    # 检查模板兼容性
    plain_template = None
    forest_template = None
    
    for template in map_gen.templates:
        if template.name == 'plain':
            plain_template = template
        elif template.name == 'forest':
            forest_template = template
    
    if plain_template and forest_template:
        print(f"\n测试兼容性:")
        print(f"Plain边缘: {plain_template.north_edge}")
        print(f"Forest边缘: {forest_template.north_edge}")
        
        can_connect = plain_template.can_connect(forest_template, 'north')
        print(f"Plain可以连接Forest (向北): {can_connect}")
        
        can_connect_rev = forest_template.can_connect(plain_template, 'south')
        print(f"Forest可以连接Plain (向南): {can_connect_rev}")

if __name__ == "__main__":
    debug_edges()
