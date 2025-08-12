#!/usr/bin/env python3

import numpy as np
import random
import math
from typing import List, Tuple, Optional, Dict, Set
from terrain_types import TerrainType, Cell
from template_loader import TemplateLoader


class CellBasedMap:
    """基于单格子的地图生成器"""
    
    def __init__(
        self,
        width: int,
        height: int,
        config_path: str = "templates_config.json",
        phase: int = None,
    ):
        self.width = width
        self.height = height
        self.phase = phase
        
        self.grid: List[List[Optional[Cell]]] = []
        
        # 使用模板加载器获取配置
        self.template_loader = TemplateLoader(phase=phase)
        
        self._initialize_grid()
        self._load_colors_from_config()
        self._load_terrain_config()
        
    def _initialize_grid(self):
        """初始化空网格"""
        # 确保地形类型已初始化
        TerrainType.initialize_from_config(phase=self.phase)
        
        self.grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(None)  # 开始时所有格子都是空的
            self.grid.append(row)
            
    def _load_colors_from_config(self):
        """从配置文件加载颜色配置"""
        color_config = self.template_loader.get_terrain_colors()
        Cell.set_color_map(color_config)
        
    def _load_terrain_config(self):
        """从配置加载地形配置"""
        # 获取基础地形权重
        self.terrain_weights = self.template_loader.get_terrain_weights()
        self.terrain_types = set(self.terrain_weights.keys())
            
        # 获取兼容性规则
        self.compatibility_rules = set()
        compatibility_config = self.template_loader.get_edge_compatibility()
        for pair in compatibility_config:
            if len(pair) == 2:
                terrain1, terrain2 = pair
                self.compatibility_rules.add((terrain1, terrain2))
                self.compatibility_rules.add((terrain2, terrain1))
                
        # 获取生成规则
        self.generation_rules = self.template_loader.get_generation_rules()
        
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """获取邻居坐标（4邻域）"""
        neighbors = []
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # 上下左右
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append((nx, ny))
        return neighbors
        
    def get_neighbor_terrains(self, x: int, y: int) -> Dict[str, int]:
        """获取邻居地形统计"""
        neighbor_count = {}
        
        for nx, ny in self.get_neighbors(x, y):
            cell = self.grid[ny][nx]
            if cell is not None:
                terrain = cell.terrain_type
                neighbor_count[terrain] = neighbor_count.get(terrain, 0) + 1
                
        return neighbor_count
        
    def is_compatible(self, terrain1: str, terrain2: str) -> bool:
        """检查两个地形是否兼容"""
        if terrain1 == terrain2:
            return True
        return (terrain1, terrain2) in self.compatibility_rules
        
    def calculate_terrain_weights(self, x: int, y: int) -> Dict[str, float]:
        """计算当前位置各地形的权重"""
        base_weights = self.terrain_weights.copy()
        neighbor_terrains = self.get_neighbor_terrains(x, y)
        
        # 邻居影响权重调整
        neighbor_influence = 1.8  # 邻居影响强度
        compatibility_boost = 1.3  # 兼容地形加成
        
        for terrain in base_weights:
            # 相同地形的邻居增加权重
            if terrain in neighbor_terrains:
                same_neighbor_count = neighbor_terrains[terrain]
                base_weights[terrain] *= (neighbor_influence ** same_neighbor_count)
                
            # 兼容地形也增加权重（但影响较小）  
            for neighbor_terrain, count in neighbor_terrains.items():
                if neighbor_terrain != terrain and self.is_compatible(terrain, neighbor_terrain):
                    base_weights[terrain] *= (compatibility_boost ** (count * 0.5))
                    
        # 添加噪声引导
        noise_weights = self._get_noise_bias(x, y)
        for terrain in base_weights:
            if terrain in noise_weights:
                base_weights[terrain] *= noise_weights[terrain]
                
        return base_weights
        
    def _get_noise_bias(self, x: int, y: int) -> Dict[str, float]:
        """使用噪声函数引导大尺度地形分布"""
        # 简单的伪噪声函数（可以替换为真正的Perlin噪声）
        def simple_noise(x, y, scale, seed_offset=0):
            return (math.sin(x / scale + seed_offset) * math.cos(y / scale + seed_offset) + 1) / 2
            
        noise_bias = {}
        
        # 不同地形使用不同的噪声尺度和偏移
        if "highland" in self.terrain_types:
            highland_noise = simple_noise(x, y, 25, 0)
            noise_bias["highland"] = 0.5 + highland_noise * 1.5
            
        if "forest" in self.terrain_types:
            forest_noise = simple_noise(x, y, 20, 100)  
            noise_bias["forest"] = 0.5 + forest_noise * 1.2
            
        if "plain" in self.terrain_types:
            plain_noise = simple_noise(x, y, 30, 200)
            noise_bias["plain"] = 0.8 + plain_noise * 0.8  # 平原稍微更常见
            
        if "slope" in self.terrain_types:
            slope_noise = simple_noise(x, y, 15, 300)
            noise_bias["slope"] = 0.6 + slope_noise * 1.0
            
        if "cliff" in self.terrain_types:
            cliff_noise = simple_noise(x, y, 40, 400)  
            noise_bias["cliff"] = 0.3 + cliff_noise * 0.7  # 悬崖比较稀少
            
        return noise_bias
        
    def validate_terrain_constraints(self, terrain: str, x: int, y: int) -> bool:
        """验证地形约束条件"""
        if terrain not in self.generation_rules:
            return True
            
        rules = self.generation_rules[terrain]
        
        # 检查必须拥有的邻居类型
        if "required_neighbors" in rules:
            neighbor_requirements = rules["required_neighbors"]
            if "must_have" in neighbor_requirements:
                must_have_types = neighbor_requirements["must_have"]
                neighbor_terrains = self.get_neighbor_terrains(x, y)
                
                for required_type in must_have_types:
                    if required_type not in neighbor_terrains:
                        # 检查是否可以通过未来放置满足要求
                        if not self._can_satisfy_requirement(required_type, x, y):
                            return False
                            
        return True
        
    def _can_satisfy_requirement(self, required_terrain: str, x: int, y: int) -> bool:
        """检查是否能通过未来的格子满足约束要求"""
        for nx, ny in self.get_neighbors(x, y):
            if self.grid[ny][nx] is None:  # 空格子
                # 检查这个空格子是否可能放置需要的地形
                empty_neighbor_terrains = self.get_neighbor_terrains(nx, ny)
                # 简化检查：如果需要的地形与现有邻居兼容，认为可以满足
                compatible = True
                for existing_terrain in empty_neighbor_terrains:
                    if not self.is_compatible(required_terrain, existing_terrain):
                        compatible = False
                        break
                if compatible:
                    return True
        return False
        
    def get_valid_terrains(self, x: int, y: int) -> List[str]:
        """获取当前位置可放置的地形类型"""
        valid_terrains = []
        
        neighbor_terrains = self.get_neighbor_terrains(x, y)
        
        for terrain in self.terrain_types:
            # 检查与所有邻居的兼容性
            compatible_with_all = True
            for neighbor_terrain in neighbor_terrains:
                if not self.is_compatible(terrain, neighbor_terrain):
                    compatible_with_all = False
                    break
                    
            if not compatible_with_all:
                continue
                
            # 检查约束条件
            if not self.validate_terrain_constraints(terrain, x, y):
                continue
                
            valid_terrains.append(terrain)
            
        return valid_terrains
        
    def generate_map(self, seed: Optional[int] = None, max_retries: int = 10):
        """生成地图"""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        # 尝试生成满足约束的地图
        for attempt in range(max_retries):
            # 清空网格
            self._initialize_grid()
            success = True
            
            # 按行列顺序生成
            for y in range(self.height):
                for x in range(self.width):
                    valid_terrains = self.get_valid_terrains(x, y)
                    
                    if not valid_terrains:
                        # 如果没有有效地形，使用最常见的地形
                        default_terrain = max(self.terrain_weights.items(), key=lambda x: x[1])[0]
                        chosen_terrain = default_terrain
                    else:
                        # 根据权重选择地形
                        weights = self.calculate_terrain_weights(x, y)
                        valid_weights = [weights.get(terrain, 0.1) for terrain in valid_terrains]
                        
                        if sum(valid_weights) == 0:
                            chosen_terrain = valid_terrains[0]
                        else:
                            chosen_terrain = random.choices(valid_terrains, weights=valid_weights)[0]
                    
                    # 放置地形
                    self.grid[y][x] = Cell(x, y, chosen_terrain)
                    
            # 验证最终约束
            if self._validate_final_constraints():
                break
                
            if attempt == max_retries - 1:
                print(f"警告: 经过 {max_retries} 次尝试，可能存在未满足的约束")
                
    def _validate_final_constraints(self) -> bool:
        """验证最终约束条件"""
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell and cell.terrain_type in self.generation_rules:
                    if not self.validate_terrain_constraints(cell.terrain_type, x, y):
                        return False
        return True
        
    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        """获取指定位置的格子"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None
        
    def to_array(self) -> np.ndarray:
        """转换为numpy数组用于可视化"""
        # 确保地形类型已初始化
        TerrainType.initialize_from_config(phase=self.phase)
        
        # 创建地形映射
        terrain_map = {}
        terrain_types = TerrainType.get_all_types()
        
        for i, terrain_str in enumerate(terrain_types):
            terrain_map[terrain_str] = i
            
        result = np.zeros((self.height, self.width), dtype=int)
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell:
                    result[y, x] = terrain_map.get(cell.terrain_type, 0)
                    
        return result
        
    def get_terrain_distribution(self) -> Dict[str, int]:
        """获取地形分布统计"""
        distribution = {}
        total_cells = 0
        
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell:
                    terrain = cell.terrain_type
                    distribution[terrain] = distribution.get(terrain, 0) + 1
                    total_cells += 1
                    
        return distribution