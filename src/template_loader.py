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
    
    def _terrain_str_to_enum(self, terrain_str: str) -> TerrainType:
        """将字符串转换为地形类型枚举"""
        terrain_map = {
            "plain": TerrainType.PLAIN,
            "forest": TerrainType.FOREST,
            "highland": TerrainType.HIGHLAND,
            "cliff": TerrainType.CLIFF,
            "river": TerrainType.RIVER,
            "slope": TerrainType.SLOPE
        }
        if terrain_str not in terrain_map:
            raise ValueError(f"未知的地形类型: {terrain_str}")
        return terrain_map[terrain_str]
    
    def _edge_str_to_enum(self, edge_str: str) -> EdgeType:
        """将字符串转换为边缘类型枚举"""
        edge_map = {
            "plain": EdgeType.PLAIN_EDGE,
            "forest": EdgeType.FOREST_EDGE,
            "highland": EdgeType.HIGHLAND_EDGE,
            "cliff": EdgeType.CLIFF_EDGE,
            "river": EdgeType.RIVER_EDGE,
            "slope": EdgeType.SLOPE_EDGE
        }
        if edge_str not in edge_map:
            raise ValueError(f"未知的边缘类型: {edge_str}")
        return edge_map[edge_str]
    
    def _create_terrain_pattern(self, pattern_config: Any, tile_size: int) -> np.ndarray:
        """根据配置创建地形模式"""
        if isinstance(pattern_config, str):
            # 单一地形类型
            terrain_type = self._terrain_str_to_enum(pattern_config)
            return np.full((tile_size, tile_size), terrain_type.value, dtype='U8')
        
        elif isinstance(pattern_config, dict):
            pattern_type = pattern_config.get("type")
            
            if pattern_type == "split_horizontal":
                # 水平分割
                top_terrain = self._terrain_str_to_enum(pattern_config["top"])
                bottom_terrain = self._terrain_str_to_enum(pattern_config["bottom"])
                
                pattern = np.full((tile_size, tile_size), bottom_terrain.value, dtype='U8')
                pattern[:tile_size//2, :] = top_terrain.value
                return pattern
            
            elif pattern_type == "split_vertical":
                # 垂直分割
                left_terrain = self._terrain_str_to_enum(pattern_config["left"])
                right_terrain = self._terrain_str_to_enum(pattern_config["right"])
                
                pattern = np.full((tile_size, tile_size), right_terrain.value, dtype='U8')
                pattern[:, :tile_size//2] = left_terrain.value
                return pattern
            
            elif pattern_type == "river_horizontal":
                # 水平河流（河流穿过平原）
                base_terrain = self._terrain_str_to_enum(pattern_config.get("base", "plain"))
                river_terrain = self._terrain_str_to_enum("river")
                
                pattern = np.full((tile_size, tile_size), base_terrain.value, dtype='U8')
                mid = tile_size // 2
                river_width = pattern_config.get("width", 3)
                start = mid - river_width // 2
                end = start + river_width
                pattern[start:end, :] = river_terrain.value
                return pattern
            
            elif pattern_type == "river_vertical":
                # 垂直河流（河流穿过平原）
                base_terrain = self._terrain_str_to_enum(pattern_config.get("base", "plain"))
                river_terrain = self._terrain_str_to_enum("river")
                
                pattern = np.full((tile_size, tile_size), base_terrain.value, dtype='U8')
                mid = tile_size // 2
                river_width = pattern_config.get("width", 3)
                start = mid - river_width // 2
                end = start + river_width
                pattern[:, start:end] = river_terrain.value
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
        return self.config.get("terrain_colors", {})
    
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
