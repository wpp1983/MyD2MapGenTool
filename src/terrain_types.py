from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List, Set, Dict, Any
import numpy as np
import json
import os

class TerrainTypeMeta(type):
    """元类用于动态创建TerrainType枚举"""
    _instance = None
    
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

class TerrainType:
    """动态地形类型类"""
    _terrain_map = {}
    _reverse_map = {}
    _initialized = False
    
    @classmethod
    def initialize_from_config(cls, config_path: str = None):
        """从配置文件初始化地形类型"""
        if cls._initialized:
            return
            
        if config_path is None:
            # 默认配置文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, "..", "config", "templates_config.json")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 从terrain_types配置中创建地形类型映射
            terrain_types_config = config.get("terrain_types", {})
            for terrain_key, terrain_name in terrain_types_config.items():
                cls._terrain_map[terrain_key] = terrain_key.upper()
                cls._reverse_map[terrain_key.upper()] = terrain_key
            
            cls._initialized = True
        except Exception as e:
            print(f"警告: 无法加载配置文件 {config_path}: {e}")
            # 使用默认地形类型
            cls._set_default_types()
    
    @classmethod
    def _set_default_types(cls):
        """设置默认地形类型"""
        default_types = ["highland", "cliff", "plain", "forest", "slope"]
        for terrain_type in default_types:
            cls._terrain_map[terrain_type] = terrain_type.upper()
            cls._reverse_map[terrain_type.upper()] = terrain_type
        cls._initialized = True
    
    @classmethod
    def get_all_types(cls):
        """获取所有地形类型"""
        if not cls._initialized:
            cls.initialize_from_config()
        return list(cls._terrain_map.keys())
    
    @classmethod
    def from_string(cls, terrain_str: str):
        """从字符串创建地形类型"""
        if not cls._initialized:
            cls.initialize_from_config()
        if terrain_str in cls._terrain_map:
            return cls._terrain_map[terrain_str]
        raise ValueError(f"未知的地形类型: {terrain_str}")
    
    @classmethod
    def to_string(cls, terrain_type: str):
        """将地形类型转换为字符串"""
        if not cls._initialized:
            cls.initialize_from_config()
        if terrain_type in cls._reverse_map:
            return cls._reverse_map[terrain_type]
        raise ValueError(f"未知的地形类型: {terrain_type}")

class EdgeType:
    """动态边缘类型类"""
    _edge_map = {}
    _reverse_map = {}
    _initialized = False
    
    @classmethod
    def initialize_from_config(cls, config_path: str = None):
        """从配置文件初始化边缘类型"""
        if cls._initialized:
            return
            
        if config_path is None:
            # 默认配置文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, "..", "config", "templates_config.json")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 从edge_types配置中创建边缘类型映射
            edge_types_config = config.get("edge_types", {})
            for terrain_key, edge_type in edge_types_config.items():
                edge_name = f"{terrain_key.upper()}_EDGE"
                cls._edge_map[terrain_key] = edge_name
                cls._reverse_map[edge_name] = terrain_key
            
            cls._initialized = True
        except Exception as e:
            print(f"警告: 无法加载配置文件 {config_path}: {e}")
            # 使用默认边缘类型
            cls._set_default_types()
    
    @classmethod
    def _set_default_types(cls):
        """设置默认边缘类型"""
        default_types = ["plain", "forest", "highland", "cliff", "slope"]
        for edge_type in default_types:
            edge_name = f"{edge_type.upper()}_EDGE"
            cls._edge_map[edge_type] = edge_name
            cls._reverse_map[edge_name] = edge_type
        cls._initialized = True
    
    @classmethod
    def get_all_types(cls):
        """获取所有边缘类型"""
        if not cls._initialized:
            cls.initialize_from_config()
        return list(cls._edge_map.keys())
    
    @classmethod
    def from_string(cls, edge_str: str):
        """从字符串创建边缘类型"""
        if not cls._initialized:
            cls.initialize_from_config()
        if edge_str in cls._edge_map:
            return cls._edge_map[edge_str]
        raise ValueError(f"未知的边缘类型: {edge_str}")
    
    @classmethod
    def to_string(cls, edge_type: str):
        """将边缘类型转换为字符串"""
        if not cls._initialized:
            cls.initialize_from_config()
        if edge_type in cls._reverse_map:
            return cls._reverse_map[edge_type]
        raise ValueError(f"未知的边缘类型: {edge_type}")

# 为了保持向后兼容性，我们创建一些常用的常量
def _get_terrain_constants():
    """获取地形类型常量"""
    TerrainType.initialize_from_config()
    constants = {}
    for terrain_str in TerrainType.get_all_types():
        constants[terrain_str.upper()] = TerrainType.from_string(terrain_str)
    return constants

def _get_edge_constants():
    """获取边缘类型常量"""
    EdgeType.initialize_from_config()
    constants = {}
    for edge_str in EdgeType.get_all_types():
        edge_name = f"{edge_str.upper()}_EDGE"
        constants[edge_name] = EdgeType.from_string(edge_str)
    return constants

@dataclass
class TileTemplate:
    name: str
    size: Tuple[int, int]
    terrain_pattern: np.ndarray
    north_edge: str  # 现在使用字符串而不是枚举
    south_edge: str
    east_edge: str
    west_edge: str
    weight: float = 1.0
    
    # 类级别的兼容性映射，将在运行时从配置文件加载
    _compatibility_map = None
    
    @classmethod
    def set_compatibility_map(cls, compatibility_config: List[List[str]]):
        """设置兼容性映射（从配置文件加载）"""
        cls._compatibility_map = set()
        
        # 确保边缘类型已初始化
        EdgeType.initialize_from_config()
        
        # 添加配置的兼容性对
        for pair in compatibility_config:
            if len(pair) == 2:
                edge1_str, edge2_str = pair
                try:
                    edge1 = EdgeType.from_string(edge1_str)
                    edge2 = EdgeType.from_string(edge2_str)
                    # 添加双向兼容性
                    cls._compatibility_map.add((edge1, edge2))
                    cls._compatibility_map.add((edge2, edge1))
                except ValueError:
                    print(f"警告: 未知的边缘类型 {edge1_str} 或 {edge2_str}")
    
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
    
    def _is_compatible_edge(self, edge1_str: str, edge2_str: str) -> bool:
        # 如果有配置文件的兼容性映射，使用它
        if self._compatibility_map is not None:
            return (edge1_str, edge2_str) in self._compatibility_map
        
        # 否则从配置文件中加载兼容性规则
        return self._load_compatibility_from_config(edge1_str, edge2_str)
    
    def _load_compatibility_from_config(self, edge1_str: str, edge2_str: str) -> bool:
        """从配置文件中加载兼容性规则"""
        try:
            # 获取配置文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, "..", "config", "templates_config.json")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 从边缘字符串中提取地形名称
            def extract_terrain_from_edge(edge_str):
                if edge_str.endswith('_EDGE'):
                    return edge_str[:-5].lower()
                return edge_str.lower()
            
            terrain1 = extract_terrain_from_edge(edge1_str)
            terrain2 = extract_terrain_from_edge(edge2_str)
            
            # 获取配置文件中的兼容性规则
            edge_compatibility = config.get("edge_compatibility", [])
            
            # 检查兼容性（双向检查）
            for pair in edge_compatibility:
                if len(pair) == 2:
                    t1, t2 = pair
                    if (terrain1 == t1 and terrain2 == t2) or (terrain1 == t2 and terrain2 == t1):
                        return True
            
            return False
            
        except Exception as e:
            print(f"警告: 无法从配置文件加载兼容性规则: {e}")
            # 如果配置文件读取失败，使用最基本的默认规则
            return terrain1 == terrain2

class TerrainCell:
    # 类级别的颜色映射，将在运行时从配置文件加载
    _color_map = None
    
    def __init__(self, x: int, y: int, terrain_type: str):  # 现在使用字符串
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
    
    @classmethod
    def set_color_map(cls, color_config: dict):
        """设置颜色映射（从配置文件加载）"""
        cls._color_map = {}
        TerrainType.initialize_from_config()
        
        for terrain_str, color in color_config.items():
            try:
                terrain_type = TerrainType.from_string(terrain_str)
                cls._color_map[terrain_type] = color
            except ValueError:
                print(f"警告: 未知的地形类型 {terrain_str}")
    
    @staticmethod
    def get_color_map():
        """获取统一的地形颜色映射"""
        if TerrainCell._color_map is None:
            # 如果没有从配置加载，尝试从配置文件加载颜色
            try:
                from template_loader import TemplateLoader
                loader = TemplateLoader()
                color_config = loader.get_terrain_colors()
                TerrainCell.set_color_map(color_config)
            except Exception as e:
                print(f"警告: 无法从配置文件加载颜色: {e}")
                # 如果配置加载失败，返回空映射，使用默认颜色
                TerrainCell._color_map = {}
        return TerrainCell._color_map
    
    def get_color(self) -> Tuple[float, float, float]:
        color_map = self.get_color_map()
        color = color_map.get(self.terrain_type, [0.5, 0.5, 0.5])
        return tuple(color)