#!/usr/bin/env python3

import json
import os
import numpy as np
from typing import List, Dict, Any
from terrain_types import TerrainType


class TemplateLoader:
    def __init__(self, config_path: str = None, phase: int = None):
        if config_path is None:
            # 获取项目根目录的config文件夹路径
            current_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(current_dir)
            config_path = os.path.join(project_root, "config", "templates_config.json")
        self.config_path = config_path
        self.config = self._load_config()
        
        # 设置当前阶段
        if phase is None:
            self.current_phase = self.config.get("metadata", {}).get("current_phase", 1)
        else:
            self.current_phase = phase
            
        # 加载当前阶段的配置
        self.phase_config = self._load_phase_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}")
    
    def _load_phase_config(self) -> Dict[str, Any]:
        """加载当前阶段的配置"""
        phases = self.config.get("phases", {})
        
        if str(self.current_phase) not in phases:
            raise ValueError(f"阶段 {self.current_phase} 不存在")
        
        # 获取当前阶段配置
        phase_config = phases[str(self.current_phase)]
        
        # 如果有 extends_phase，需要合并配置
        if "extends_phase" in phase_config:
            base_phase = str(phase_config["extends_phase"])
            if base_phase in phases:
                base_config = self._load_phase_config_recursive(base_phase, phases)
                # 合并配置
                merged_config = self._merge_phase_configs(base_config, phase_config)
                return merged_config
        
        return phase_config
    
    def _load_phase_config_recursive(self, phase_str: str, phases: Dict) -> Dict[str, Any]:
        """递归加载阶段配置（处理继承关系）"""
        phase_config = phases[phase_str]
        
        if "extends_phase" in phase_config:
            base_phase = str(phase_config["extends_phase"])
            if base_phase in phases:
                base_config = self._load_phase_config_recursive(base_phase, phases)
                return self._merge_phase_configs(base_config, phase_config)
        
        return phase_config
    
    def _merge_phase_configs(self, base_config: Dict, extension_config: Dict) -> Dict[str, Any]:
        """合并阶段配置"""
        merged = base_config.copy()
        
        # 合并基本属性
        for key in ["name", "description"]:
            if key in extension_config:
                merged[key] = extension_config[key]
        
        # 注意: region_templates 已废弃，不再需要合并
        
        # 合并 cell_types
        if "cell_types" not in merged:
            merged["cell_types"] = {}
        if "additional_cell_types" in extension_config:
            merged["cell_types"].update(extension_config["additional_cell_types"])
        
        # 合并 edge_types
        if "edge_types" not in merged:
            merged["edge_types"] = {}
        if "additional_edge_types" in extension_config:
            merged["edge_types"].update(extension_config["additional_edge_types"])
        
        # 合并 edge_compatibility
        if "edge_compatibility" not in merged:
            merged["edge_compatibility"] = []
        if "additional_compatibility" in extension_config:
            merged["edge_compatibility"].extend(extension_config["additional_compatibility"])
        
        return merged


    def get_terrain_colors(self) -> Dict[str, List[float]]:
        """获取地形颜色配置"""
        colors = {}
        terrain_types = self.phase_config.get("cell_types", {})
        for terrain_name, terrain_data in terrain_types.items():
            if isinstance(terrain_data, dict) and "color" in terrain_data:
                colors[terrain_name] = terrain_data["color"]
        return colors

    def get_debug_config(self) -> Dict[str, Any]:
        """获取调试配置"""
        return self.config.get("debug", {})

    def get_edge_compatibility(self) -> List[List[str]]:
        """获取边缘兼容性配置"""
        return self.phase_config.get("edge_compatibility", [])

    def get_terrain_weights(self) -> Dict[str, float]:
        """获取地形权重配置"""
        weights = {}
        terrain_types = self.phase_config.get("cell_types", {})
        for terrain_name, terrain_data in terrain_types.items():
            if isinstance(terrain_data, dict) and "weight" in terrain_data:
                weights[terrain_name] = terrain_data["weight"]
            else:
                # 默认权重
                weights[terrain_name] = 1.0
        return weights

    def get_generation_rules(self) -> Dict[str, Dict[str, Any]]:
        """获取地形生成规则配置"""
        rules = {}
        terrain_types = self.phase_config.get("cell_types", {})
        for terrain_name, terrain_data in terrain_types.items():
            if isinstance(terrain_data, dict) and "generation_rules" in terrain_data:
                rules[terrain_name] = terrain_data["generation_rules"]
        return rules
    
    def get_current_phase(self) -> int:
        """获取当前阶段号"""
        return self.current_phase
    
    def get_phase_info(self) -> Dict[str, Any]:
        """获取当前阶段信息"""
        return {
            "phase": self.current_phase,
            "name": self.phase_config.get("name", f"Phase {self.current_phase}"),
            "description": self.phase_config.get("description", "")
        }
    
    def get_available_phases(self) -> List[int]:
        """获取所有可用阶段"""
        phases = self.config.get("phases", {})
        return [int(phase) for phase in phases.keys()]
    
    def get_region_generation_config(self) -> Dict[str, Any]:
        """获取区域生成配置"""
        return self.config.get("region_generation", {
            "target_region_count": 7,
            "min_region_distance": 0.15,
            "growth_strength": 0.95,
            "growth_decay": 0.95,
            "growth_threshold": 0.05,
            "max_placement_attempts": 100
        })
