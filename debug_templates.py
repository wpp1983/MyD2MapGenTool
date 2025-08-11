#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from map_generator import TileBasedMap

def debug_templates():
    print("创建地图生成器...")
    map_gen = TileBasedMap(4, 3)
    
    print(f"\n已加载 {len(map_gen.templates)} 个模板:")
    for i, template in enumerate(map_gen.templates):
        print(f"  {i}: {template.name} (权重: {template.weight})")
        print(f"      边缘: N={template.north_edge}, S={template.south_edge}, E={template.east_edge}, W={template.west_edge}")
    
    # 测试第一个位置的有效模板
    print(f"\n位置 (0,0) 的有效模板:")
    valid_templates = map_gen.get_valid_templates(0, 0)
    print(f"找到 {len(valid_templates)} 个有效模板:")
    for template in valid_templates:
        print(f"  - {template.name} (权重: {template.weight})")
    
    # 生成地图并检查瓦片
    print(f"\n生成地图...")
    map_gen.generate_map(seed=123)
    
    print(f"\n生成的瓦片:")
    for y in range(map_gen.tile_height):
        for x in range(map_gen.tile_width):
            tile = map_gen.tiles[y][x]
            if tile:
                print(f"  ({x},{y}): {tile.name}")
            else:
                print(f"  ({x},{y}): None")

if __name__ == "__main__":
    debug_templates()
