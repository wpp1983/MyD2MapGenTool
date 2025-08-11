#!/usr/bin/env python3
"""测试地形兼容性规则是否正确从配置文件中加载"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from terrain_types import TileTemplate
import numpy as np

def test_compatibility_from_config():
    """测试从配置文件加载的兼容性规则"""
    
    # 创建测试模板
    plain_template = TileTemplate(
        name="plain_test",
        size=(1, 1),
        terrain_pattern=np.array([["plain"]]),
        north_edge="PLAIN_EDGE",
        south_edge="PLAIN_EDGE", 
        east_edge="PLAIN_EDGE",
        west_edge="PLAIN_EDGE"
    )
    
    forest_template = TileTemplate(
        name="forest_test",
        size=(1, 1),
        terrain_pattern=np.array([["forest"]]),
        north_edge="FOREST_EDGE",
        south_edge="FOREST_EDGE",
        east_edge="FOREST_EDGE", 
        west_edge="FOREST_EDGE"
    )
    
    highland_template = TileTemplate(
        name="highland_test",
        size=(1, 1),
        terrain_pattern=np.array([["highland"]]),
        north_edge="HIGHLAND_EDGE",
        south_edge="HIGHLAND_EDGE",
        east_edge="HIGHLAND_EDGE",
        west_edge="HIGHLAND_EDGE"
    )
    
    cliff_template = TileTemplate(
        name="cliff_test", 
        size=(1, 1),
        terrain_pattern=np.array([["cliff"]]),
        north_edge="CLIFF_EDGE",
        south_edge="CLIFF_EDGE",
        east_edge="CLIFF_EDGE",
        west_edge="CLIFF_EDGE"
    )
    
    # 测试兼容性
    print("测试兼容性规则:")
    
    # 应该兼容的组合（根据配置文件）
    compatible_tests = [
        (plain_template, forest_template, "应该兼容: plain-forest"),
        (plain_template, highland_template, "应该兼容: plain-highland"),
        (highland_template, cliff_template, "应该兼容: highland-cliff"),
        (forest_template, cliff_template, "应该兼容: forest-cliff"),
        (plain_template, cliff_template, "应该兼容: plain-cliff"),
        (plain_template, plain_template, "应该兼容: plain-plain (相同类型)"),
        (forest_template, forest_template, "应该兼容: forest-forest (相同类型)"),
    ]
    
    # 应该不兼容的组合（slope没有在配置中与cliff定义兼容）
    incompatible_tests = [
        # 注意：根据当前配置，大部分地形都相互兼容了
        # 这里测试一些边界情况
    ]
    
    print("\n兼容性测试:")
    for template1, template2, description in compatible_tests:
        result = template1.can_connect(template2, 'east')
        status = "✓" if result else "✗"
        print(f"{status} {description}: {result}")
    
    if incompatible_tests:
        print("\n不兼容性测试:")
        for template1, template2, description in incompatible_tests:
            result = template1.can_connect(template2, 'east')
            status = "✓" if not result else "✗"
            print(f"{status} {description}: {not result}")
    else:
        print("\n注意: 根据当前配置，所有地形类型都相互兼容")

if __name__ == "__main__":
    test_compatibility_from_config()
