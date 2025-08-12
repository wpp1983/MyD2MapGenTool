"""
悬崖生成规则测试
测试悬崖必须同时有平原和高地邻居的约束条件
"""

import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from map_generator import RegionBasedMap


class TestCliffConstraints:
    """悬崖约束测试类"""

    def test_cliff_basic_constraints(self):
        """测试基本的悬崖约束条件"""
        map_gen = RegionBasedMap(tile_width=6, tile_height=6)
        map_gen.generate_map(seed=1337)

        # 检查是否有悬崖生成
        cliff_count = 0
        for tile_y in range(map_gen.tile_height):
            for tile_x in range(map_gen.tile_width):
                tile = map_gen.regions[tile_y][tile_x]
                if tile and tile.name == "cliff":
                    cliff_count += 1

        # 至少应该有一些悬崖（使用已知种子）
        assert cliff_count > 0, "应该生成至少一个悬崖"

    def test_cliff_neighbor_requirements(self):
        """测试悬崖邻居要求"""
        map_gen = RegionBasedMap(tile_width=6, tile_height=6)
        map_gen.generate_map(seed=1337)

        violations = []

        for tile_y in range(map_gen.tile_height):
            for tile_x in range(map_gen.tile_width):
                tile = map_gen.regions[tile_y][tile_x]
                if tile and tile.name == "cliff":
                    # 检查邻居
                    has_plain = False
                    has_highland = False

                    directions = [
                        (tile_x, tile_y - 1),  # north
                        (tile_x, tile_y + 1),  # south
                        (tile_x + 1, tile_y),  # east
                        (tile_x - 1, tile_y),  # west
                    ]

                    for nx, ny in directions:
                        if (
                            0 <= nx < map_gen.tile_width
                            and 0 <= ny < map_gen.tile_height
                        ):
                            neighbor_tile = map_gen.regions[ny][nx]
                            if neighbor_tile:
                                if neighbor_tile.name == "plain":
                                    has_plain = True
                                if neighbor_tile.name == "highland":
                                    has_highland = True

                    if not (has_plain and has_highland):
                        violations.append(
                            f"悬崖位置({tile_x}, {tile_y}) - 平原:{has_plain}, 高地:{has_highland}"
                        )

        assert len(violations) == 0, f"悬崖约束违反: {violations}"

    @pytest.mark.parametrize(
        "seed", [42, 123, 456, 789, 999, 1337, 2021, 555, 777, 888]
    )
    def test_cliff_constraints_multiple_seeds(self, seed):
        """测试多个种子下的悬崖约束"""
        map_gen = RegionBasedMap(tile_width=6, tile_height=6)
        map_gen.generate_map(seed=seed)

        cliff_count = 0
        valid_cliffs = 0

        for tile_y in range(map_gen.tile_height):
            for tile_x in range(map_gen.tile_width):
                tile = map_gen.regions[tile_y][tile_x]
                if tile and tile.name == "cliff":
                    cliff_count += 1

                    # 检查是否满足约束
                    has_plain = False
                    has_highland = False

                    directions = [
                        (tile_x, tile_y - 1),  # north
                        (tile_x, tile_y + 1),  # south
                        (tile_x + 1, tile_y),  # east
                        (tile_x - 1, tile_y),  # west
                    ]

                    for nx, ny in directions:
                        if (
                            0 <= nx < map_gen.tile_width
                            and 0 <= ny < map_gen.tile_height
                        ):
                            neighbor_tile = map_gen.regions[ny][nx]
                            if neighbor_tile:
                                if neighbor_tile.name == "plain":
                                    has_plain = True
                                if neighbor_tile.name == "highland":
                                    has_highland = True

                    if has_plain and has_highland:
                        valid_cliffs += 1

        # 如果有悬崖，所有悬崖都必须满足约束
        if cliff_count > 0:
            assert (
                valid_cliffs == cliff_count
            ), f"种子{seed}: {cliff_count}个悬崖中只有{valid_cliffs}个满足约束"

    def test_cliff_validation_method(self):
        """测试悬崖验证方法"""
        map_gen = RegionBasedMap(tile_width=6, tile_height=6)
        map_gen.generate_map(seed=1337)

        # 验证方法应该返回True（所有约束都满足）
        assert map_gen._validate_cliff_constraints(), "悬崖约束验证应该通过"


class TestMapGeneration:
    """地图生成基本功能测试"""

    def test_map_creation(self):
        """测试地图创建"""
        map_gen = RegionBasedMap(tile_width=4, tile_height=4)

        assert map_gen.tile_width == 4
        assert map_gen.tile_height == 4
        assert map_gen.width == 32  # 4 * 8
        assert map_gen.height == 32  # 4 * 8

    def test_map_generation_with_seed(self):
        """测试使用种子生成地图"""
        map_gen1 = RegionBasedMap(tile_width=4, tile_height=4)
        map_gen2 = RegionBasedMap(tile_width=4, tile_height=4)

        map_gen1.generate_map(seed=42)
        map_gen2.generate_map(seed=42)

        # 相同种子应该生成相同的地图
        for y in range(map_gen1.tile_height):
            for x in range(map_gen1.tile_width):
                tile1 = map_gen1.regions[y][x]
                tile2 = map_gen2.regions[y][x]
                assert tile1.name == tile2.name, f"位置({x},{y})的地块类型不匹配"

    def test_template_loading(self):
        """测试模板加载"""
        map_gen = RegionBasedMap(tile_width=4, tile_height=4)

        # 应该加载了所有模板
        template_names = [t.name for t in map_gen.region_templates]
        # 从配置中获取预期的模板名称
        from template_loader import TemplateLoader

        loader = TemplateLoader()
        expected_region_templates = [
            template["name"] for template in loader.config["region_templates"]
        ]

        for expected in expected_region_templates:
            assert expected in template_names, f"模板 {expected} 未加载"

    def test_valid_region_templates_selection(self):
        """测试有效模板选择"""
        map_gen = RegionBasedMap(tile_width=4, tile_height=4)

        # 在空地图的第一个位置，应该有有效的模板选择
        valid_region_templates = map_gen.get_valid_region_templates(0, 0)
        assert len(valid_region_templates) > 0, "应该有至少一个有效模板"


if __name__ == "__main__":
    # 如果直接运行此文件，执行测试
    pytest.main([__file__, "-v"])
