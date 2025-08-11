from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List, Set
import numpy as np

class TerrainType(Enum):
    HIGHLAND = "highland"
    CLIFF = "cliff" 
    PLAIN = "plain"
    FOREST = "forest"
    RIVER = "river"
    SLOPE = "slope"

class EdgeType(Enum):
    PLAIN_EDGE = "plain"
    FOREST_EDGE = "forest"
    HIGHLAND_EDGE = "highland"
    RIVER_EDGE = "river"
    CLIFF_EDGE = "cliff"
    SLOPE_EDGE = "slope"

@dataclass
class TileTemplate:
    name: str
    size: Tuple[int, int]
    terrain_pattern: np.ndarray
    north_edge: EdgeType
    south_edge: EdgeType
    east_edge: EdgeType
    west_edge: EdgeType
    weight: float = 1.0
    
    # 类级别的兼容性映射，将在运行时从配置文件加载
    _compatibility_map = None
    
    @classmethod
    def set_compatibility_map(cls, compatibility_config: List[List[str]]):
        """设置兼容性映射（从配置文件加载）"""
        cls._compatibility_map = set()
        
        # 将字符串转换为EdgeType枚举
        edge_str_to_enum = {
            "plain": EdgeType.PLAIN_EDGE,
            "forest": EdgeType.FOREST_EDGE,
            "highland": EdgeType.HIGHLAND_EDGE,
            "cliff": EdgeType.CLIFF_EDGE,
            "river": EdgeType.RIVER_EDGE
        }
        
        # 添加配置的兼容性对
        for pair in compatibility_config:
            if len(pair) == 2:
                edge1_str, edge2_str = pair
                if edge1_str in edge_str_to_enum and edge2_str in edge_str_to_enum:
                    edge1 = edge_str_to_enum[edge1_str]
                    edge2 = edge_str_to_enum[edge2_str]
                    # 添加双向兼容性
                    cls._compatibility_map.add((edge1, edge2))
                    cls._compatibility_map.add((edge2, edge1))
    
    def can_connect(self, other: 'TileTemplate', direction: str) -> bool:
        edge_connections = {
            'north': (self.north_edge, other.south_edge),
            'south': (self.south_edge, other.north_edge),
            'east': (self.east_edge, other.west_edge),
            'west': (self.west_edge, other.east_edge)
        }
        
        if direction not in edge_connections:
            return False
            
        my_edge, other_edge = edge_connections[direction]
        return my_edge == other_edge or self._is_compatible_edge(my_edge, other_edge)
    
    def _is_compatible_edge(self, edge1: EdgeType, edge2: EdgeType) -> bool:
        # 如果有配置文件的兼容性映射，使用它
        if self._compatibility_map is not None:
            return (edge1, edge2) in self._compatibility_map
        
        # 否则使用默认的兼容性规则
        compatible_pairs = {
            (EdgeType.PLAIN_EDGE, EdgeType.FOREST_EDGE),
            (EdgeType.FOREST_EDGE, EdgeType.PLAIN_EDGE),
            (EdgeType.HIGHLAND_EDGE, EdgeType.PLAIN_EDGE),
            (EdgeType.PLAIN_EDGE, EdgeType.HIGHLAND_EDGE),
            (EdgeType.RIVER_EDGE, EdgeType.PLAIN_EDGE),
            (EdgeType.PLAIN_EDGE, EdgeType.RIVER_EDGE)
        }
        return (edge1, edge2) in compatible_pairs

class TerrainCell:
    # 类级别的颜色映射，将在运行时从配置文件加载
    _color_map = None
    
    def __init__(self, x: int, y: int, terrain_type: TerrainType):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
    
    @classmethod
    def set_color_map(cls, color_config: dict):
        """设置颜色映射（从配置文件加载）"""
        cls._color_map = {}
        for terrain_str, color in color_config.items():
            terrain_type = cls._terrain_str_to_enum(terrain_str)
            cls._color_map[terrain_type] = color
    
    @staticmethod
    def _terrain_str_to_enum(terrain_str: str) -> TerrainType:
        """将字符串转换为地形类型枚举"""
        terrain_map = {
            "plain": TerrainType.PLAIN,
            "forest": TerrainType.FOREST,
            "highland": TerrainType.HIGHLAND,
            "cliff": TerrainType.CLIFF,
            "river": TerrainType.RIVER
        }
        return terrain_map.get(terrain_str, TerrainType.PLAIN)
    
    @staticmethod
    def get_color_map():
        """获取统一的地形颜色映射"""
        if TerrainCell._color_map is None:
            # 如果没有从配置加载，使用默认颜色
            return {
                TerrainType.HIGHLAND: [0.8, 0.6, 0.4],  # 高地 - 棕色
                TerrainType.CLIFF: [0.5, 0.5, 0.5],     # 悬崖 - 灰色
                TerrainType.PLAIN: [0.4, 0.8, 0.2],     # 平原 - 浅绿色
                TerrainType.FOREST: [0.1, 0.4, 0.1],    # 森林 - 深绿色
                TerrainType.RIVER: [0.2, 0.4, 0.8]      # 河流 - 蓝色
            }
        return TerrainCell._color_map
    
    def get_color(self) -> Tuple[float, float, float]:
        color_map = self.get_color_map()
        color = color_map.get(self.terrain_type, [0.5, 0.5, 0.5])
        return tuple(color)