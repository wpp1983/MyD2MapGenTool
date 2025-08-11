"""
模板加载器测试
测试配置文件加载和模板生成功能
"""

import pytest
import sys
import os
import json

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from template_loader import TemplateLoader


class TestTemplateLoader:
    """模板加载器测试类"""
    
    def test_config_loading(self):
        """测试配置文件加载"""
        loader = TemplateLoader()
        
        # 检查配置是否正确加载
        assert loader.config is not None, "配置应该被加载"
        assert "templates" in loader.config, "配置应该包含templates字段"
        assert "terrain_types" in loader.config, "配置应该包含terrain_types字段"
        assert "terrain_colors" in loader.config, "配置应该包含terrain_colors字段"
    
    def test_template_creation(self):
        """测试模板创建"""
        loader = TemplateLoader()
        templates = loader.create_templates(tile_size=8)
        
        # 检查模板数量
        assert len(templates) > 0, "应该创建至少一个模板"
        
        # 检查基本模板是否存在
        template_names = [t.name for t in templates]
        expected_names = ["plain", "forest", "highland", "slope", "cliff"]
        
        for expected in expected_names:
            assert expected in template_names, f"应该包含 {expected} 模板"
    
    def test_generation_rules_loading(self):
        """测试生成规则加载"""
        loader = TemplateLoader()
        rules = loader.get_generation_rules()
        
        # 检查悬崖规则
        assert "cliff" in rules, "应该包含悬崖生成规则"
        cliff_rules = rules["cliff"]
        assert "required_neighbors" in cliff_rules, "悬崖规则应该包含required_neighbors"
        
        neighbor_rules = cliff_rules["required_neighbors"]
        assert "must_have" in neighbor_rules, "应该包含must_have规则"
        
        must_have_types = neighbor_rules["must_have"]
        assert "plain" in must_have_types, "悬崖必须有平原邻居"
        assert "highland" in must_have_types, "悬崖必须有高地邻居"
    
    def test_terrain_colors(self):
        """测试地形颜色配置"""
        loader = TemplateLoader()
        colors = loader.get_terrain_colors()
        
        # 检查所有地形都有颜色配置
        expected_terrains = ["plain", "forest", "highland", "cliff", "slope"]
        
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
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'templates_config.json')
        assert os.path.exists(config_path), "配置文件应该存在"
    
    def test_config_json_valid(self):
        """测试配置文件JSON格式有效性"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'templates_config.json')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"配置文件JSON格式无效: {e}")
        
        # 检查必需的顶级字段
        required_fields = ["templates", "terrain_types", "terrain_colors", "edge_types", "edge_compatibility", "generation_rules"]
        for field in required_fields:
            assert field in config, f"配置文件应该包含 {field} 字段"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
