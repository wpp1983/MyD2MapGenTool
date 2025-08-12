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
        
        # 获取区域生成配置
        self.region_config = self.template_loader.get_region_generation_config()
        
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
        neighbor_terrains = self.get_neighbor_terrains(x, y)
        
        # 如果有邻居地形，强烈倾向于使用邻居地形
        if neighbor_terrains:
            weights = {}
            for terrain in self.terrain_types:
                weights[terrain] = 0.01  # 给非邻居地形很小的基础权重
            
            # 大幅增强邻居地形的权重
            neighbor_influence = 50.0  # 大幅提高邻居影响强度
            for terrain, count in neighbor_terrains.items():
                if terrain in weights:
                    weights[terrain] = self.terrain_weights.get(terrain, 1.0) * (neighbor_influence ** count)
            
            return weights
        else:
            # 如果没有邻居，使用原始权重（但此情况在填充阶段很少见）
            base_weights = self.terrain_weights.copy()
            
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
        
        # 使用更大的噪声尺度来创建大片区域
        if "highland" in self.terrain_types:
            highland_noise = simple_noise(x, y, 80, 0)
            noise_bias["highland"] = 0.6 + highland_noise * 1.0  # 降低影响强度
            
        if "forest" in self.terrain_types:
            forest_noise = simple_noise(x, y, 70, 100)  
            noise_bias["forest"] = 0.6 + forest_noise * 0.8
            
        if "plain" in self.terrain_types:
            plain_noise = simple_noise(x, y, 100, 200)  # 最大尺度，创建大片平原
            noise_bias["plain"] = 0.8 + plain_noise * 0.6  # 平原更常见且稳定
            
        if "slope" in self.terrain_types:
            slope_noise = simple_noise(x, y, 60, 300)
            noise_bias["slope"] = 0.5 + slope_noise * 0.8
            
        if "cliff" in self.terrain_types:
            cliff_noise = simple_noise(x, y, 120, 400)  # 更大尺度，形成大片悬崖区域
            noise_bias["cliff"] = 0.3 + cliff_noise * 0.5  # 悬崖比较稀少
            
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
        
    def _place_region_seeds(self) -> List[Tuple[int, int, str]]:
        """在地图上放置区域种子点（固定数量，优化分布）"""
        seeds = []
        
        # 从配置获取参数
        target_count = self.region_config.get("target_region_count", 7)
        min_distance_ratio = self.region_config.get("min_region_distance", 0.15)
        max_attempts = self.region_config.get("max_placement_attempts", 100)
        
        # 计算实际最小距离
        map_diagonal = math.sqrt(self.width ** 2 + self.height ** 2)
        min_distance = map_diagonal * min_distance_ratio
        
        # 地形类型列表
        terrain_list = list(self.terrain_types)
        terrain_weights = [self.terrain_weights[t] for t in terrain_list]
        
        # 边缘留白
        margin = min(self.width // 10, self.height // 10, 8)
        safe_width = self.width - 2 * margin
        safe_height = self.height - 2 * margin
        
        # 尝试放置种子点
        for seed_idx in range(target_count):
            best_pos = None
            best_distance = 0
            
            # 多次尝试找到最佳位置
            for attempt in range(max_attempts):
                # 使用分层网格优化分布
                if seed_idx == 0:
                    # 第一个种子点放在中心附近
                    x = margin + safe_width // 2 + random.randint(-safe_width//4, safe_width//4)
                    y = margin + safe_height // 2 + random.randint(-safe_height//4, safe_height//4)
                else:
                    # 后续种子点尽量分散
                    x = margin + random.randint(0, safe_width - 1)
                    y = margin + random.randint(0, safe_height - 1)
                
                # 确保在有效范围内
                x = max(margin, min(self.width - margin - 1, x))
                y = max(margin, min(self.height - margin - 1, y))
                
                # 计算与现有种子点的最小距离
                min_dist_to_existing = float('inf')
                for existing_x, existing_y, _ in seeds:
                    dist = math.sqrt((x - existing_x) ** 2 + (y - existing_y) ** 2)
                    min_dist_to_existing = min(min_dist_to_existing, dist)
                
                # 如果是第一个种子点或距离足够远
                if len(seeds) == 0 or min_dist_to_existing >= min_distance:
                    best_pos = (x, y)
                    break
                elif min_dist_to_existing > best_distance:
                    # 记录当前最好的位置
                    best_pos = (x, y)
                    best_distance = min_dist_to_existing
            
            # 如果找到合适位置，添加种子点
            if best_pos:
                x, y = best_pos
                # 根据权重选择地形类型
                terrain = random.choices(terrain_list, weights=terrain_weights)[0]
                seeds.append((x, y, terrain))
            else:
                print(f"警告: 无法为第 {seed_idx + 1} 个种子点找到合适位置，跳过")
        
        print(f"成功放置 {len(seeds)} 个种子点，目标是 {target_count} 个")
        return seeds
        
    def _grow_regions_from_seeds(self, seeds: List[Tuple[int, int, str]]):
        """从种子点开始生长区域"""
        # 首先放置种子点
        for x, y, terrain in seeds:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.grid[y][x] = Cell(x, y, terrain)
        
        # 使用队列进行广度优先搜索式的区域生长
        growth_queue = []
        
        # 将所有种子点加入生长队列
        for x, y, terrain in seeds:
            if 0 <= x < self.width and 0 <= y < self.height:
                for nx, ny in self.get_neighbors(x, y):
                    if self.grid[ny][nx] is None:  # 只考虑空格子
                        growth_queue.append((nx, ny, terrain, 1.0))  # (x, y, terrain, strength)
        
        # 随机打乱队列，避免过于规整的生长模式
        random.shuffle(growth_queue)
        
        # 逐步生长区域
        while growth_queue:
            current_queue = growth_queue.copy()
            growth_queue = []
            
            for x, y, terrain, strength in current_queue:
                if self.grid[y][x] is not None:  # 已被占用
                    continue
                    
                # 检查是否可以放置该地形
                if not self._can_place_terrain_at(x, y, terrain):
                    continue
                
                # 根据强度决定是否在此处生长（使用配置参数）
                base_growth_strength = self.region_config.get("growth_strength", 0.95)
                growth_probability = strength * base_growth_strength
                if random.random() < growth_probability:
                    self.grid[y][x] = Cell(x, y, terrain)
                    
                    # 将邻居加入下一轮生长队列（使用配置参数）
                    decay_rate = self.region_config.get("growth_decay", 0.95)
                    growth_threshold = self.region_config.get("growth_threshold", 0.05)
                    new_strength = strength * decay_rate
                    if new_strength > growth_threshold:
                        for nx, ny in self.get_neighbors(x, y):
                            if (0 <= nx < self.width and 0 <= ny < self.height and 
                                self.grid[ny][nx] is None):
                                growth_queue.append((nx, ny, terrain, new_strength))
    
    def _can_place_terrain_at(self, x: int, y: int, terrain: str) -> bool:
        """检查是否可以在指定位置放置地形"""
        neighbor_terrains = self.get_neighbor_terrains(x, y)
        
        # 检查与所有邻居的兼容性
        for neighbor_terrain in neighbor_terrains:
            if not self.is_compatible(terrain, neighbor_terrain):
                return False
        
        # 检查约束条件
        return self.validate_terrain_constraints(terrain, x, y)

    def generate_map(self, seed: Optional[int] = None, max_retries: int = 10):
        """生成地图"""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        # 尝试生成满足约束的地图
        for attempt in range(max_retries):
            # 清空网格
            self._initialize_grid()
            
            # 第一阶段：区域生长
            seeds = self._place_region_seeds()
            self._grow_regions_from_seeds(seeds)
            
            # 第二阶段：填充剩余空格
            for y in range(self.height):
                for x in range(self.width):
                    if self.grid[y][x] is not None:  # 已经有地形
                        continue
                        
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
    
    def _flood_fill_region(self, start_x: int, start_y: int, terrain_type: str, visited: Set[Tuple[int, int]]) -> int:
        """使用flood fill算法计算连通区域大小"""
        if (start_x, start_y) in visited:
            return 0
            
        stack = [(start_x, start_y)]
        region_size = 0
        
        while stack:
            x, y = stack.pop()
            
            # 检查边界和访问状态
            if (x < 0 or x >= self.width or y < 0 or y >= self.height or 
                (x, y) in visited):
                continue
                
            cell = self.grid[y][x]
            if not cell or cell.terrain_type != terrain_type:
                continue
                
            # 标记为已访问
            visited.add((x, y))
            region_size += 1
            
            # 添加4个邻居到栈中
            stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])
            
        return region_size
    
    def analyze_regions(self) -> Dict[str, Dict[str, any]]:
        """分析地形区域，返回每种地形的区域数量和大小分布"""
        visited = set()
        terrain_regions = {}
        
        # 初始化每种地形的统计
        for terrain in self.terrain_types:
            terrain_regions[terrain] = {
                'region_count': 0,
                'region_sizes': [],
                'total_cells': 0,
                'largest_region': 0,
                'average_region_size': 0
            }
        
        # 遍历所有格子，找到未访问的区域
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in visited:
                    continue
                    
                cell = self.grid[y][x]
                if not cell:
                    continue
                    
                terrain_type = cell.terrain_type
                region_size = self._flood_fill_region(x, y, terrain_type, visited)
                
                if region_size > 0:
                    stats = terrain_regions[terrain_type]
                    stats['region_count'] += 1
                    stats['region_sizes'].append(region_size)
                    stats['total_cells'] += region_size
                    stats['largest_region'] = max(stats['largest_region'], region_size)
        
        # 计算平均区域大小
        for terrain, stats in terrain_regions.items():
            if stats['region_count'] > 0:
                stats['average_region_size'] = stats['total_cells'] / stats['region_count']
            else:
                stats['average_region_size'] = 0
                
        return terrain_regions
    
    def _get_terrain_descriptions(self) -> Dict[str, str]:
        """获取地形描述"""
        descriptions = {}
        phase_config = self.template_loader.phase_config
        cell_types = phase_config.get("cell_types", {})
        
        for terrain_name, terrain_data in cell_types.items():
            if isinstance(terrain_data, dict) and "description" in terrain_data:
                descriptions[terrain_name] = terrain_data["description"]
            else:
                descriptions[terrain_name] = terrain_name
                
        return descriptions
    
    def print_region_analysis(self):
        """打印区域分析结果"""
        regions = self.analyze_regions()
        total_regions = sum(stats['region_count'] for stats in regions.values())
        
        print(f"\n=== 地形区域分析 ===")
        print(f"总区域数量: {total_regions}")
        print(f"地图尺寸: {self.width}x{self.height} ({self.width * self.height} 格子)")
        
        # 获取地形描述
        terrain_descriptions = self._get_terrain_descriptions()
        
        for terrain, stats in regions.items():
            if stats['region_count'] > 0:
                description = terrain_descriptions.get(terrain, terrain)
                print(f"\n{terrain} ({description}):")
                print(f"  区域数量: {stats['region_count']}")
                print(f"  总格子数: {stats['total_cells']}")
                print(f"  最大区域: {stats['largest_region']} 格子")
                print(f"  平均区域大小: {stats['average_region_size']:.1f} 格子")
                
                # 区域大小分布
                sizes = stats['region_sizes']
                if len(sizes) > 1:
                    sizes.sort(reverse=True)
                    print(f"  前5大区域: {sizes[:5]}")
                    
                    # 统计小、中、大区域
                    small = sum(1 for s in sizes if s < 20)
                    medium = sum(1 for s in sizes if 20 <= s < 100)
                    large = sum(1 for s in sizes if s >= 100)
                    print(f"  区域分布: 小型(<20格): {small}, 中型(20-99格): {medium}, 大型(≥100格): {large}")
        
        # 计算区域连贯性指标
        total_cells = sum(stats['total_cells'] for stats in regions.values())
        if total_cells > 0:
            connectivity_score = (total_cells / total_regions) if total_regions > 0 else 0
            print(f"\n连贯性指标: {connectivity_score:.1f} (平均每个区域的格子数，越大越连贯)")
            
            if connectivity_score >= 50:
                print("✅ 区域连贯性: 很好 (大片区域)")
            elif connectivity_score >= 25:
                print("🔶 区域连贯性: 中等")
            else:
                print("❌ 区域连贯性: 较差 (过于碎片化)")