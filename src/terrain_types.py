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
    def initialize_from_config(cls, config_path: str = None, phase: int = None):
        """从配置文件初始化地形类型"""
        if cls._initialized:
            return

        if config_path is None:
            # 默认配置文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(
                current_dir, "..", "config", "templates_config.json"
            )

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # 确定使用的阶段
            if phase is None:
                phase = config.get("metadata", {}).get("current_phase", 1)
            
            # 加载指定阶段的配置（含继承）
            terrain_types_config = cls._load_phase_terrain_types(config, phase)
            
            for terrain_key, terrain_name in terrain_types_config.items():
                cls._terrain_map[terrain_key] = terrain_key.upper()
                cls._reverse_map[terrain_key.upper()] = terrain_key

            cls._initialized = True
        except Exception as e:
            print(f"警告: 无法加载配置文件 {config_path}: {e}")
            # 使用默认地形类型
            cls._set_default_types()

    @classmethod
    def _load_phase_terrain_types(cls, config: dict, phase: int) -> dict:
        """加载指定阶段的地形类型（处理继承关系）"""
        phases = config.get("phases", {})
        phase_str = str(phase)
        
        if phase_str not in phases:
            # 如果阶段不存在，返回空字典
            return {}
        
        phase_config = phases[phase_str]
        terrain_types = {}
        
        # 如果有继承关系，先加载基础阶段
        if "extends_phase" in phase_config:
            base_phase = phase_config["extends_phase"]
            terrain_types = cls._load_phase_terrain_types(config, base_phase)
        
        # 添加当前阶段的地形类型
        current_types = phase_config.get("cell_types", {})
        terrain_types.update(current_types)
        
        # 添加额外的地形类型
        additional_types = phase_config.get("additional_cell_types", {})
        terrain_types.update(additional_types)
        
        return terrain_types

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








class Cell:
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
        if Cell._color_map is None:
            # 如果没有从配置加载，尝试从配置文件加载颜色
            try:
                from template_loader import TemplateLoader

                loader = TemplateLoader()
                color_config = loader.get_terrain_colors()
                Cell.set_color_map(color_config)
            except Exception as e:
                print(f"警告: 无法从配置文件加载颜色: {e}")
                # 如果配置加载失败，返回空映射，使用默认颜色
                Cell._color_map = {}
        return Cell._color_map

    def get_color(self) -> Tuple[float, float, float]:
        color_map = self.get_color_map()
        color = color_map.get(self.terrain_type, [0.5, 0.5, 0.5])
        return tuple(color)
