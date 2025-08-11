#!/usr/bin/env python3

import json
import os
import numpy as np
from typing import List, Dict, Any
from terrain_types import TerrainType, EdgeType, TileTemplate

class TemplateLoader:
    def __init__(self, config_path: str = None):
        if config_path is None:
            # 获取项目根目录的config文件夹路径
            current_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(current_dir)
            config_path = os.path.join(project_root, "config", "templates_config.json")
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}")
    
    def _terrain_str_to_enum(self, terrain_str: str) -> str:
        """将字符串转换为地形类型"""
        # 确保地形类型已初始化
        TerrainType.initialize_from_config()
        
        try:
            return TerrainType.from_string(terrain_str)
        except ValueError:
            raise ValueError(f"未知的地形类型: {terrain_str}")
    
    def _edge_str_to_enum(self, edge_str: str) -> str:
        """将字符串转换为边缘类型"""
        # 确保边缘类型已初始化
        EdgeType.initialize_from_config()
        
        try:
            return EdgeType.from_string(edge_str)
        except ValueError:
            raise ValueError(f"未知的边缘类型: {edge_str}")
    
    def _create_terrain_pattern(self, pattern_config: Any, tile_size: int) -> np.ndarray:
        """根据配置创建地形模式"""
        if isinstance(pattern_config, str):
            # 单一地形类型
            terrain_type_str = self._terrain_str_to_enum(pattern_config)
            # 现在terrain_type_str是字符串，直接使用原始字符串
            return np.full((tile_size, tile_size), pattern_config, dtype='U8')
        
        elif isinstance(pattern_config, dict):
            pattern_type = pattern_config.get("type")
            
            if pattern_type == "split_horizontal":
                # 水平分割
                top_terrain_str = pattern_config["top"]
                bottom_terrain_str = pattern_config["bottom"]
                
                pattern = np.full((tile_size, tile_size), bottom_terrain_str, dtype='U8')
                pattern[:tile_size//2, :] = top_terrain_str
                return pattern
            
            elif pattern_type == "split_vertical":
                # 垂直分割
                left_terrain_str = pattern_config["left"]
                right_terrain_str = pattern_config["right"]
                
                pattern = np.full((tile_size, tile_size), right_terrain_str, dtype='U8')
                pattern[:, :tile_size//2] = left_terrain_str
                return pattern
            
            else:
                raise ValueError(f"未知的模式类型: {pattern_type}")
        
        else:
            raise ValueError(f"无效的模式配置: {pattern_config}")
    
    def create_templates(self, tile_size: int = 8) -> List[TileTemplate]:
        """根据配置创建所有模板"""
        templates = []
        
        for template_config in self.config["templates"]:
            # 创建地形模式
            terrain_pattern = self._create_terrain_pattern(
                template_config["terrain_pattern"], 
                tile_size
            )
            
            # 创建边缘类型
            edges = template_config["edges"]
            north_edge = self._edge_str_to_enum(edges["north"])
            south_edge = self._edge_str_to_enum(edges["south"])
            east_edge = self._edge_str_to_enum(edges["east"])
            west_edge = self._edge_str_to_enum(edges["west"])
            
            # 创建模板
            template = TileTemplate(
                name=template_config["name"],
                size=(tile_size, tile_size),
                terrain_pattern=terrain_pattern,
                north_edge=north_edge,
                south_edge=south_edge,
                east_edge=east_edge,
                west_edge=west_edge,
                weight=template_config["weight"]
            )
            
            templates.append(template)
        
        return templates
    
    def get_terrain_colors(self) -> Dict[str, List[float]]:
        """获取地形颜色配置"""
        colors = {}
        terrain_types = self.config.get("terrain_types", {})
        for terrain_name, terrain_data in terrain_types.items():
            if isinstance(terrain_data, dict) and "color" in terrain_data:
                colors[terrain_name] = terrain_data["color"]
        return colors
    
    def get_debug_config(self) -> Dict[str, Any]:
        """获取调试配置"""
        return self.config.get("debug", {})
    
    def get_edge_compatibility(self) -> List[List[str]]:
        """获取边缘兼容性配置"""
        return self.config.get("edge_compatibility", [])
    
    def get_template_info(self) -> List[Dict[str, Any]]:
        """获取模板信息（用于调试或显示）"""
        info = []
        for template_config in self.config["templates"]:
            info.append({
                "name": template_config["name"],
                "description": template_config["description"],
                "weight": template_config["weight"],
                "edges": template_config["edges"]
            })
        return info
    
    def get_generation_rules(self) -> Dict[str, Dict[str, Any]]:
        """获取地形生成规则配置"""
        rules = {}
        terrain_types = self.config.get("terrain_types", {})
        for terrain_name, terrain_data in terrain_types.items():
            if isinstance(terrain_data, dict) and "generation_rules" in terrain_data:
                rules[terrain_name] = terrain_data["generation_rules"]
        return rules
