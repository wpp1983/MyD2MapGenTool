"""
模板加载器测试
测试配置文件加载和模板生成功能
"""

import pytest
import sys
import os
import json

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from template_loader import TemplateLoader


class TestTemplateLoader:
    """模板加载器测试类"""

    def test_config_loading(self):
        """测试配置文件加载"""
        loader = TemplateLoader()

        # 检查配置是否正确加载
        assert loader.config is not None, "配置应该被加载"
        assert "region_templates" in loader.config, "配置应该包含region_templates字段"
        assert "cell_types" in loader.config, "配置应该包含cell_types字段"
        # 检查terrain_types中包含颜色信息
        terrain_types = loader.config.get("cell_types", {})
        for terrain_name, terrain_data in terrain_types.items():
            if isinstance(terrain_data, dict):
                assert "color" in terrain_data, f"{terrain_name} 应该包含颜色信息"

    def test_template_creation(self):
        """测试模板创建"""
        loader = TemplateLoader()
        templates = loader.create_region_templates(tile_size=8)

        # 检查模板数量
        assert len(templates) > 0, "应该创建至少一个模板"

        # 检查模板是否与配置中的模板对应
        template_names = [t.name for t in templates]
        config_template_names = [
            template["name"] for template in loader.config["region_templates"]
        ]

        for expected in config_template_names:
            assert expected in template_names, f"应该包含 {expected} 模板"

    def test_generation_rules_loading(self):
        """测试生成规则加载"""
        loader = TemplateLoader()
        rules = loader.get_generation_rules()

        # 在新架构中，region级别只有plain和highland，所以不应该有复杂的生成规则
        # 检查规则加载功能正常（可能为空或只包含cell级别的规则）
        assert isinstance(rules, dict), "生成规则应该是字典"
        # 不再强制要求cliff规则，因为cliff现在是cell级别的过渡地形

    def test_terrain_colors(self):
        """测试地形颜色配置"""
        loader = TemplateLoader()
        colors = loader.get_terrain_colors()

        # 检查所有地形都有颜色配置
        expected_terrains = list(loader.config["cell_types"].keys())

        for terrain in expected_terrains:
            assert terrain in colors, f"{terrain} 应该有颜色配置"
            color = colors[terrain]
            assert isinstance(color, list), f"{terrain} 颜色应该是列表"
            assert len(color) == 3, f"{terrain} 颜色应该有3个分量(RGB)"

            # 检查颜色值范围
            for component in color:
                assert 0 <= component <= 1, f"{terrain} 颜色分量应该在0-1范围内"

    def test_edge_compatibility(self):
        """测试边缘兼容性配置"""
        loader = TemplateLoader()
        compatibility = loader.get_edge_compatibility()

        assert isinstance(compatibility, list), "兼容性配置应该是列表"
        assert len(compatibility) > 0, "应该有兼容性规则"

        # 检查悬崖和平原的兼容性
        cliff_plain_compatible = False
        for rule in compatibility:
            if set(rule) == {"cliff", "plain"}:
                cliff_plain_compatible = True
                break

        assert cliff_plain_compatible, "悬崖和平原应该兼容"

    def test_template_info(self):
        """测试模板信息获取"""
        loader = TemplateLoader()
        info = loader.get_template_info()

        assert isinstance(info, list), "模板信息应该是列表"
        assert len(info) > 0, "应该有模板信息"

        # 检查第一个模板信息的结构
        first_template = info[0]
        required_fields = ["name", "description", "weight", "edges"]

        for field in required_fields:
            assert field in first_template, f"模板信息应该包含 {field} 字段"


class TestConfigValidation:
    """配置验证测试"""

    def test_config_file_exists(self):
        """测试配置文件是否存在"""
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "config", "templates_config.json"
        )
        assert os.path.exists(config_path), "配置文件应该存在"

    def test_config_json_valid(self):
        """测试配置文件JSON格式有效性"""
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "config", "templates_config.json"
        )

        with open(config_path, "r", encoding="utf-8") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"配置文件JSON格式无效: {e}")

        # 检查必需的顶级字段
        required_fields = [
            "region_templates",
            "cell_types",
            "edge_types",
            "edge_compatibility",
        ]
        for field in required_fields:
            assert field in config, f"配置文件应该包含 {field} 字段"

        # 检查cell_types结构
        terrain_types = config.get("cell_types", {})
        for terrain_name, terrain_data in terrain_types.items():
            if isinstance(terrain_data, dict):
                assert "color" in terrain_data, f"{terrain_name} 应该包含颜色信息"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
