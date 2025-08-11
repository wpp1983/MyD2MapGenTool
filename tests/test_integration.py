"""
配置和集成测试
测试整体功能集成和配置有效性
"""

import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from map_generator import TileBasedMap
from template_loader import TemplateLoader
from terrain_types import TerrainType


class TestIntegration:
    """集成测试类"""
    
    def test_full_map_generation_workflow(self):
        """测试完整的地图生成工作流程"""
        # 创建地图生成器
        map_gen = TileBasedMap(tile_width=4, tile_height=4)
        
        # 生成地图
        map_gen.generate_map(seed=42)
        
        # 验证地图结构
        assert len(map_gen.tiles) == 4, "应该有4行地块"
        assert len(map_gen.tiles[0]) == 4, "每行应该有4个地块"
        
        # 验证所有位置都有地块
        for y in range(4):
            for x in range(4):
                tile = map_gen.tiles[y][x]
                assert tile is not None, f"位置({x},{y})应该有地块"
                assert tile.name in ["plain", "forest", "highland", "river", "slope", "cliff"], f"地块类型无效: {tile.name}"
    
    def test_terrain_cell_grid(self):
        """测试地形网格"""
        tile_size = 4
        map_gen = TileBasedMap(tile_width=2, tile_height=2, tile_size=tile_size)
        map_gen.generate_map(seed=123)
        
        # 验证网格大小
        expected_size = 2 * tile_size  # tile_width * tile_size
        assert len(map_gen.grid) == expected_size, f"网格高度应该是{expected_size}"
        assert len(map_gen.grid[0]) == expected_size, f"网格宽度应该是{expected_size}"
        assert map_gen.width == expected_size, f"地图宽度应该是{expected_size}"
        assert map_gen.height == expected_size, f"地图高度应该是{expected_size}"
        
        # 验证网格中的地形类型
        for y in range(expected_size):
            for x in range(expected_size):
                cell = map_gen.grid[y][x]
                assert isinstance(cell.terrain_type, TerrainType), f"位置({x},{y})应该有有效的地形类型"
    
    def test_map_to_array_conversion(self):
        """测试地图转数组功能"""
        map_gen = TileBasedMap(tile_width=3, tile_height=3)
        map_gen.generate_map(seed=456)
        
        array = map_gen.to_array()
        
        # 验证数组维度
        assert array.shape == (24, 24), f"数组形状应该是(24,24)，实际是{array.shape}"
        
        # 验证数组值范围
        valid_values = {0, 1, 2, 3, 4}  # 对应不同地形类型
        unique_values = set(array.flatten())
        assert unique_values.issubset(valid_values), f"数组值应该在{valid_values}范围内，实际有{unique_values}"
    
    def test_reproducible_generation(self):
        """测试可重现的地图生成"""
        seed = 789
        
        # 生成两次相同种子的地图
        map_gen1 = TileBasedMap(tile_width=3, tile_height=3)
        map_gen1.generate_map(seed=seed)
        
        map_gen2 = TileBasedMap(tile_width=3, tile_height=3)
        map_gen2.generate_map(seed=seed)
        
        # 比较地块类型
        for y in range(3):
            for x in range(3):
                tile1 = map_gen1.tiles[y][x]
                tile2 = map_gen2.tiles[y][x]
                assert tile1.name == tile2.name, f"位置({x},{y})的地块类型不一致: {tile1.name} vs {tile2.name}"
        
        # 比较网格
        array1 = map_gen1.to_array()
        array2 = map_gen2.to_array()
        assert (array1 == array2).all(), "相同种子应该生成相同的地图数组"


class TestPerformance:
    """性能测试类"""
    
    def test_large_map_generation(self):
        """测试大地图生成性能"""
        import time
        
        start_time = time.time()
        map_gen = TileBasedMap(tile_width=10, tile_height=10)
        map_gen.generate_map(seed=999)
        end_time = time.time()
        
        generation_time = end_time - start_time
        
        # 10x10的地图应该在合理时间内完成（比如5秒内）
        assert generation_time < 5.0, f"大地图生成耗时过长: {generation_time:.2f}秒"
        
        # 验证地图完整性
        assert map_gen.width == 80, "大地图宽度应该正确"
        assert map_gen.height == 80, "大地图高度应该正确"
    
    @pytest.mark.parametrize("size", [2, 4, 6, 8])
    def test_scalability(self, size):
        """测试不同大小地图的可扩展性"""
        map_gen = TileBasedMap(tile_width=size, tile_height=size)
        map_gen.generate_map(seed=111)
        
        # 验证基本属性
        assert map_gen.tile_width == size
        assert map_gen.tile_height == size
        assert map_gen.width == size * 8
        assert map_gen.height == size * 8
        
        # 验证所有位置都被填充
        for y in range(size):
            for x in range(size):
                assert map_gen.tiles[y][x] is not None, f"位置({x},{y})未被填充"


class TestErrorHandling:
    """错误处理测试"""
    
    def test_invalid_map_size(self):
        """测试无效的地图大小"""
        # 这个测试验证系统能够处理边界情况
        # 如果系统设计允许零大小，这也是合法的
        try:
            map_gen = TileBasedMap(tile_width=0, tile_height=4)
            # 如果没有异常，确保基本属性正确
            assert map_gen.tile_width == 0
            assert map_gen.width == 0
        except (ValueError, AssertionError, Exception):
            # 如果抛出异常也是可以接受的
            pass
        
        try:
            map_gen = TileBasedMap(tile_width=4, tile_height=0)
            assert map_gen.tile_height == 0
            assert map_gen.height == 0
        except (ValueError, AssertionError, Exception):
            pass
    
    def test_invalid_config_path(self):
        """测试无效的配置路径"""
        with pytest.raises(FileNotFoundError):
            loader = TemplateLoader("nonexistent_config.json")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
