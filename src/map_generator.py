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
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = TerrainCell(x, y, TerrainType.PLAIN)
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
        
        return True
    
    def generate_map(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
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
    
    def _apply_template(self, template: TileTemplate, tile_x: int, tile_y: int):
        start_x = tile_x * self.tile_size
        start_y = tile_y * self.tile_size
        
        for py in range(self.tile_size):
            for px in range(self.tile_size):
                terrain_value = template.terrain_pattern[py, px]
                terrain_type = TerrainType(terrain_value)
                
                grid_x = start_x + px
                grid_y = start_y + py
                
                if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
                    self.grid[grid_y][grid_x].terrain_type = terrain_type
    
    def get_cell(self, x: int, y: int) -> Optional[TerrainCell]:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None
    
    def to_array(self) -> np.ndarray:
        terrain_map = {
            TerrainType.HIGHLAND: 4,
            TerrainType.CLIFF: 3,
            TerrainType.PLAIN: 2,
            TerrainType.FOREST: 1,
            TerrainType.RIVER: 0
        }
        
        result = np.zeros((self.height, self.width), dtype=int)
        for y in range(self.height):
            for x in range(self.width):
                result[y, x] = terrain_map[self.grid[y][x].terrain_type]
        return result