import numpy as np
import random
from typing import List, Tuple, Optional, Dict
from terrain_types import TerrainType, TerrainCell, TileTemplate, EdgeType
from template_loader import TemplateLoader

class TileBasedMap:
    def __init__(self, tile_width: int, tile_height: int, tile_size: int = 8, config_path: str = "templates_config.json"):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.tile_size = tile_size
        self.width = tile_width * tile_size
        self.height = tile_height * tile_size
        
        self.tiles: List[List[Optional[TileTemplate]]] = [[None for _ in range(tile_width)] for _ in range(tile_height)]
        self.grid: List[List[TerrainCell]] = []
        self.templates: List[TileTemplate] = []
        
        # 使用模板加载器
        self.template_loader = TemplateLoader()
        
        self._initialize_grid()
        self._load_templates_from_config()
        self._load_colors_from_config()
        self._load_compatibility_from_config()
    
    def _initialize_grid(self):
        self.grid = []  # 清空现有网格
        
        # 确保地形类型已初始化
        TerrainType.initialize_from_config()
        
        # 获取默认地形类型（通常是平原）
        try:
            default_terrain = TerrainType.from_string("plain")
        except ValueError:
            # 如果没有平原，使用第一个可用的地形类型
            terrain_types = TerrainType.get_all_types()
            default_terrain = TerrainType.from_string(terrain_types[0]) if terrain_types else "plain"
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = TerrainCell(x, y, default_terrain)
                row.append(cell)
            self.grid.append(row)
    
    def _load_templates_from_config(self):
        """从配置文件加载模板"""
        self.templates = self.template_loader.create_templates(self.tile_size)
    
    def _load_colors_from_config(self):
        """从配置文件加载颜色配置"""
        color_config = self.template_loader.get_terrain_colors()
        TerrainCell.set_color_map(color_config)
    
    def _load_compatibility_from_config(self):
        """从配置文件加载兼容性配置"""
        from terrain_types import TileTemplate
        compatibility_config = self.template_loader.get_edge_compatibility()
        TileTemplate.set_compatibility_map(compatibility_config)
    
    def get_template_info(self) -> List[Dict]:
        """获取模板信息"""
        return self.template_loader.get_template_info()
    
    def get_valid_templates(self, tile_x: int, tile_y: int) -> List[TileTemplate]:
        valid_templates = []
        
        for template in self.templates:
            if self._can_place_template(template, tile_x, tile_y):
                valid_templates.append(template)
        
        return valid_templates
    
    def _can_place_template(self, template: TileTemplate, tile_x: int, tile_y: int) -> bool:
        directions = [
            ('north', tile_x, tile_y - 1),
            ('south', tile_x, tile_y + 1),
            ('east', tile_x + 1, tile_y),
            ('west', tile_x - 1, tile_y)
        ]
        
        for direction, nx, ny in directions:
            if 0 <= nx < self.tile_width and 0 <= ny < self.tile_height:
                neighbor_tile = self.tiles[ny][nx]
                if neighbor_tile and not template.can_connect(neighbor_tile, direction):
                    return False
        
        # 检查模板特定的生成规则
        if not self._check_template_rules(template, tile_x, tile_y):
            return False
        
        # 检查放置这个模板是否会破坏相邻模板的约束
        if not self._check_neighbor_constraints_after_placement(template, tile_x, tile_y):
            return False
        
        return True
    
    def _check_neighbor_constraints_after_placement(self, new_template: TileTemplate, tile_x: int, tile_y: int) -> bool:
        """检查放置新模板后，相邻模板的约束是否仍然满足"""
        rules = self.template_loader.get_generation_rules()
        
        directions = [
            (tile_x, tile_y - 1),  # north
            (tile_x, tile_y + 1),  # south
            (tile_x + 1, tile_y),  # east
            (tile_x - 1, tile_y)   # west
        ]
        
        for nx, ny in directions:
            if 0 <= nx < self.tile_width and 0 <= ny < self.tile_height:
                neighbor_tile = self.tiles[ny][nx]
                if neighbor_tile and neighbor_tile.name in rules:
                    # 临时放置新模板
                    old_tile = self.tiles[tile_y][tile_x]
                    self.tiles[tile_y][tile_x] = new_template
                    
                    # 检查邻居的约束
                    neighbor_rules = rules[neighbor_tile.name]
                    if "required_neighbors" in neighbor_rules:
                        if not self._check_neighbor_requirements(neighbor_tile, nx, ny, neighbor_rules["required_neighbors"]):
                            # 恢复原状态
                            self.tiles[tile_y][tile_x] = old_tile
                            return False
                    
                    # 恢复原状态
                    self.tiles[tile_y][tile_x] = old_tile
        
        return True
    
    def _check_template_rules(self, template: TileTemplate, tile_x: int, tile_y: int) -> bool:
        """检查模板特定的生成规则"""
        rules = self.template_loader.get_generation_rules()
        
        if template.name not in rules:
            return True
        
        template_rules = rules[template.name]
        
        # 检查邻居要求规则
        if "required_neighbors" in template_rules:
            required_neighbors = template_rules["required_neighbors"]
            if not self._check_neighbor_requirements(template, tile_x, tile_y, required_neighbors):
                return False
        
        return True
    
    def _check_neighbor_requirements(self, template: TileTemplate, tile_x: int, tile_y: int, requirements: Dict) -> bool:
        """检查邻居要求"""
        directions = [
            ('north', tile_x, tile_y - 1),
            ('south', tile_x, tile_y + 1),
            ('east', tile_x + 1, tile_y),
            ('west', tile_x - 1, tile_y)
        ]
        
        # 检查是否必须有特定类型的邻居
        if "must_have" in requirements:
            must_have_types = requirements["must_have"]
            for must_have_type in must_have_types:
                has_must_have = False
                
                for direction, nx, ny in directions:
                    if 0 <= nx < self.tile_width and 0 <= ny < self.tile_height:
                        neighbor_tile = self.tiles[ny][nx]
                        if neighbor_tile and neighbor_tile.name == must_have_type:
                            has_must_have = True
                            break
                        elif neighbor_tile is None:
                            # 检查是否可以在空位置放置需要的类型
                            required_template = next((t for t in self.templates if t.name == must_have_type), None)
                            if required_template and self._can_place_template_at_position(required_template, nx, ny, excluding_pos=(tile_x, tile_y)):
                                has_must_have = True
                                break
                
                if not has_must_have:
                    return False
        
        return True
    
    def _validate_cliff_constraints(self) -> bool:
        """验证所有悬崖都满足约束条件"""
        rules = self.template_loader.get_generation_rules()
        if "cliff" not in rules:
            return True
            
        cliff_rules = rules["cliff"]
        if "required_neighbors" not in cliff_rules:
            return True
            
        neighbor_requirements = cliff_rules["required_neighbors"]
        
        # 检查所有悬崖地块
        for tile_y in range(self.tile_height):
            for tile_x in range(self.tile_width):
                tile = self.tiles[tile_y][tile_x]
                if tile and tile.name == "cliff":
                    directions = [
                        (tile_x, tile_y - 1),  # north
                        (tile_x, tile_y + 1),  # south
                        (tile_x + 1, tile_y),  # east
                        (tile_x - 1, tile_y)   # west
                    ]
                    
                    # 检查 must_have 要求
                    if "must_have" in neighbor_requirements:
                        must_have_types = neighbor_requirements["must_have"]
                        for must_have_type in must_have_types:
                            has_must_have = False
                            for nx, ny in directions:
                                if 0 <= nx < self.tile_width and 0 <= ny < self.tile_height:
                                    neighbor_tile = self.tiles[ny][nx]
                                    if neighbor_tile and neighbor_tile.name == must_have_type:
                                        has_must_have = True
                                        break
                            if not has_must_have:
                                return False
        
        return True
    
    def _can_place_template_at_position(self, template: TileTemplate, tile_x: int, tile_y: int, excluding_pos: Optional[Tuple[int, int]] = None) -> bool:
        """检查是否可以在指定位置放置模板，可以排除某个位置的考虑"""
        directions = [
            ('north', tile_x, tile_y - 1),
            ('south', tile_x, tile_y + 1),
            ('east', tile_x + 1, tile_y),
            ('west', tile_x - 1, tile_y)
        ]
        
        for direction, nx, ny in directions:
            # 跳过被排除的位置
            if excluding_pos and (nx, ny) == excluding_pos:
                continue
                
            if 0 <= nx < self.tile_width and 0 <= ny < self.tile_height:
                neighbor_tile = self.tiles[ny][nx]
                if neighbor_tile and not template.can_connect(neighbor_tile, direction):
                    return False
        
        return True
    
    def generate_map(self, seed: Optional[int] = None, max_retries: int = 50):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # 尝试生成满足约束的地图
        for attempt in range(max_retries):
            # 清空地图
            self.tiles = [[None for _ in range(self.tile_width)] for _ in range(self.tile_height)]
            self._initialize_grid()
            
            # 生成地图
            success = True
            for tile_y in range(self.tile_height):
                for tile_x in range(self.tile_width):
                    valid_templates = self.get_valid_templates(tile_x, tile_y)
                    
                    if valid_templates:
                        weights = [t.weight for t in valid_templates]
                        chosen_template = random.choices(valid_templates, weights=weights)[0]
                        self.tiles[tile_y][tile_x] = chosen_template
                        self._apply_template(chosen_template, tile_x, tile_y)
                    else:
                        default_template = self.templates[0]
                        self.tiles[tile_y][tile_x] = default_template
                        self._apply_template(default_template, tile_x, tile_y)
            
            # 验证约束条件
            if self._validate_cliff_constraints():
                break
            
            # 如果是最后一次尝试，输出警告但继续
            if attempt == max_retries - 1:
                print(f"警告: 经过 {max_retries} 次尝试，无法生成完全满足悬崖约束的地图")
                break
    
    def _apply_template(self, template: TileTemplate, tile_x: int, tile_y: int):
        start_x = tile_x * self.tile_size
        start_y = tile_y * self.tile_size
        
        for py in range(self.tile_size):
            for px in range(self.tile_size):
                terrain_value = template.terrain_pattern[py, px]
                # terrain_value现在是字符串，直接使用
                terrain_type = terrain_value
                
                grid_x = start_x + px
                grid_y = start_y + py
                
                if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
                    self.grid[grid_y][grid_x].terrain_type = terrain_type
    
    def get_cell(self, x: int, y: int) -> Optional[TerrainCell]:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None
    
    def to_array(self) -> np.ndarray:
        # 确保地形类型已初始化
        TerrainType.initialize_from_config()
        
        # 动态创建地形映射 - 使用字符串作为键
        terrain_map = {}
        terrain_types = TerrainType.get_all_types()
        
        # 为每种地形类型分配一个数值，使用原始字符串而不是转换后的
        for i, terrain_str in enumerate(terrain_types):
            terrain_map[terrain_str] = i
        
        result = np.zeros((self.height, self.width), dtype=int)
        for y in range(self.height):
            for x in range(self.width):
                result[y, x] = terrain_map.get(self.grid[y][x].terrain_type, 0)
        return result