#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from map_generator import TileBasedMap

def test_map_generation():
    print("创建地图生成器...")
    map_gen = TileBasedMap(4, 3)
    
    print("生成地图...")
    map_gen.generate_map(seed=123)
    
    print("转换为数组...")
    array = map_gen.to_array()
    
    print(f'地图数组形状: {array.shape}')
    print('地图数组内容:')
    print(array)
    print(f'唯一值: {sorted(set(array.flatten()))}')
    
    # 检查一些地形类型
    print("\n地形统计:")
    unique, counts = np.unique(array, return_counts=True)
    for val, count in zip(unique, counts):
        print(f"地形 {val}: {count} 个单元格")

if __name__ == "__main__":
    import numpy as np
    test_map_generation()
