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

class EdgeType(Enum):
    PLAIN_EDGE = "plain"
    FOREST_EDGE = "forest"
    HIGHLAND_EDGE = "highland"
    RIVER_EDGE = "river"
    CLIFF_EDGE = "cliff"

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
    def __init__(self, x: int, y: int, terrain_type: TerrainType):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
    
    def get_color(self) -> Tuple[float, float, float]:
        color_map = {
            TerrainType.HIGHLAND: (0.8, 0.6, 0.4),
            TerrainType.CLIFF: (0.5, 0.5, 0.5),
            TerrainType.PLAIN: (0.4, 0.8, 0.2),
            TerrainType.FOREST: (0.1, 0.4, 0.1),
            TerrainType.RIVER: (0.2, 0.4, 0.8)
        }
        return color_map.get(self.terrain_type, (0.5, 0.5, 0.5))