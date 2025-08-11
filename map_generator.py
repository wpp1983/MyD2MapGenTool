import numpy as np
import random
from typing import List, Tuple, Optional, Dict
from terrain_types import TerrainType, TerrainCell, TileTemplate, EdgeType

class TileBasedMap:
    def __init__(self, tile_width: int, tile_height: int, tile_size: int = 8):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.tile_size = tile_size
        self.width = tile_width * tile_size
        self.height = tile_height * tile_size
        
        self.tiles: List[List[Optional[TileTemplate]]] = [[None for _ in range(tile_width)] for _ in range(tile_height)]
        self.grid: List[List[TerrainCell]] = []
        self.templates: List[TileTemplate] = []
        
        self._initialize_grid()
        self._create_default_templates()
    
    def _initialize_grid(self):
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = TerrainCell(x, y, TerrainType.PLAIN)
                row.append(cell)
            self.grid.append(row)
    
    def _create_default_templates(self):
        self.templates = [
            self._create_plain_template(),
            self._create_forest_template(),
            self._create_highland_template(),
            self._create_river_horizontal_template(),
            self._create_river_vertical_template(),
            self._create_mixed_plain_forest_template(),
            self._create_highland_cliff_template()
        ]
    
    def _create_plain_template(self) -> TileTemplate:
        pattern = np.full((self.tile_size, self.tile_size), TerrainType.PLAIN.value, dtype='U8')
        return TileTemplate(
            name="plain",
            size=(self.tile_size, self.tile_size),
            terrain_pattern=pattern,
            north_edge=EdgeType.PLAIN_EDGE,
            south_edge=EdgeType.PLAIN_EDGE,
            east_edge=EdgeType.PLAIN_EDGE,
            west_edge=EdgeType.PLAIN_EDGE,
            weight=3.0
        )
    
    def _create_forest_template(self) -> TileTemplate:
        pattern = np.full((self.tile_size, self.tile_size), TerrainType.FOREST.value, dtype='U8')
        return TileTemplate(
            name="forest",
            size=(self.tile_size, self.tile_size),
            terrain_pattern=pattern,
            north_edge=EdgeType.FOREST_EDGE,
            south_edge=EdgeType.FOREST_EDGE,
            east_edge=EdgeType.FOREST_EDGE,
            west_edge=EdgeType.FOREST_EDGE,
            weight=2.0
        )
    
    def _create_highland_template(self) -> TileTemplate:
        pattern = np.full((self.tile_size, self.tile_size), TerrainType.HIGHLAND.value, dtype='U8')
        return TileTemplate(
            name="highland",
            size=(self.tile_size, self.tile_size),
            terrain_pattern=pattern,
            north_edge=EdgeType.HIGHLAND_EDGE,
            south_edge=EdgeType.HIGHLAND_EDGE,
            east_edge=EdgeType.HIGHLAND_EDGE,
            west_edge=EdgeType.HIGHLAND_EDGE,
            weight=1.5
        )
    
    def _create_river_horizontal_template(self) -> TileTemplate:
        pattern = np.full((self.tile_size, self.tile_size), TerrainType.PLAIN.value, dtype='U8')
        mid = self.tile_size // 2
        pattern[mid-1:mid+2, :] = TerrainType.RIVER.value
        
        return TileTemplate(
            name="river_horizontal",
            size=(self.tile_size, self.tile_size),
            terrain_pattern=pattern,
            north_edge=EdgeType.PLAIN_EDGE,
            south_edge=EdgeType.PLAIN_EDGE,
            east_edge=EdgeType.RIVER_EDGE,
            west_edge=EdgeType.RIVER_EDGE,
            weight=0.8
        )
    
    def _create_river_vertical_template(self) -> TileTemplate:
        pattern = np.full((self.tile_size, self.tile_size), TerrainType.PLAIN.value, dtype='U8')
        mid = self.tile_size // 2
        pattern[:, mid-1:mid+2] = TerrainType.RIVER.value
        
        return TileTemplate(
            name="river_vertical",
            size=(self.tile_size, self.tile_size),
            terrain_pattern=pattern,
            north_edge=EdgeType.RIVER_EDGE,
            south_edge=EdgeType.RIVER_EDGE,
            east_edge=EdgeType.PLAIN_EDGE,
            west_edge=EdgeType.PLAIN_EDGE,
            weight=0.8
        )
    
    def _create_mixed_plain_forest_template(self) -> TileTemplate:
        pattern = np.full((self.tile_size, self.tile_size), TerrainType.PLAIN.value, dtype='U8')
        pattern[:self.tile_size//2, :] = TerrainType.FOREST.value
        
        return TileTemplate(
            name="mixed_plain_forest",
            size=(self.tile_size, self.tile_size),
            terrain_pattern=pattern,
            north_edge=EdgeType.FOREST_EDGE,
            south_edge=EdgeType.PLAIN_EDGE,
            east_edge=EdgeType.FOREST_EDGE,
            west_edge=EdgeType.FOREST_EDGE,
            weight=1.2
        )
    
    def _create_highland_cliff_template(self) -> TileTemplate:
        pattern = np.full((self.tile_size, self.tile_size), TerrainType.HIGHLAND.value, dtype='U8')
        pattern[self.tile_size//2:, :] = TerrainType.CLIFF.value
        
        return TileTemplate(
            name="highland_cliff",
            size=(self.tile_size, self.tile_size),
            terrain_pattern=pattern,
            north_edge=EdgeType.HIGHLAND_EDGE,
            south_edge=EdgeType.CLIFF_EDGE,
            east_edge=EdgeType.HIGHLAND_EDGE,
            west_edge=EdgeType.HIGHLAND_EDGE,
            weight=0.5
        )
    
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