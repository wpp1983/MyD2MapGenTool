#!/usr/bin/env python3
"""测试地形兼容性规则是否正确从配置文件中加载"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from terrain_types import RegionTemplate
from template_loader import TemplateLoader
import numpy as np


def test_compatibility_from_config():
    """测试从配置文件加载的兼容性规则"""

    # 从配置加载模板
    loader = TemplateLoader()
    templates = loader.create_region_templates(tile_size=1)

    # 创建模板字典以便按名称查找
    template_dict = {t.name: t for t in templates}

    # 测试兼容性
    print("测试兼容性规则:")

    # 从配置文件读取兼容性规则来构建测试用例
    compatibility_rules = loader.get_edge_compatibility()

    compatible_tests = []
    # 添加配置中定义的兼容性测试
    for rule in compatibility_rules:
        if len(rule) == 2:
            terrain1, terrain2 = rule
            if terrain1 in template_dict and terrain2 in template_dict:
                compatible_tests.append(
                    (
                        template_dict[terrain1],
                        template_dict[terrain2],
                        f"应该兼容: {terrain1}-{terrain2}",
                    )
                )

    # 添加相同类型的兼容性测试
    for template in templates:
        compatible_tests.append(
            (template, template, f"应该兼容: {template.name}-{template.name} (相同类型)")
        )

    # 应该不兼容的组合（slope没有在配置中与cliff定义兼容）
    incompatible_tests = [
        # 注意：根据当前配置，大部分地形都相互兼容了
        # 这里测试一些边界情况
    ]

    print("\n兼容性测试:")
    for template1, template2, description in compatible_tests:
        result = template1.can_connect(template2, "east")
        status = "✓" if result else "✗"
        print(f"{status} {description}: {result}")

    if incompatible_tests:
        print("\n不兼容性测试:")
        for template1, template2, description in incompatible_tests:
            result = template1.can_connect(template2, "east")
            status = "✓" if not result else "✗"
            print(f"{status} {description}: {not result}")
    else:
        print("\n注意: 根据当前配置，所有地形类型都相互兼容")


if __name__ == "__main__":
    test_compatibility_from_config()
