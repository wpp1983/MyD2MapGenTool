import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button, Slider
import numpy as np
from typing import Optional
from map_generator import TileBasedMap
from terrain_types import TerrainType

class MapVisualizer:
    def __init__(self, tile_width: int = 10, tile_height: int = 8):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.map_generator = TileBasedMap(tile_width, tile_height)
        self.current_seed = 42
        
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        plt.subplots_adjust(bottom=0.25)
        
        self._setup_ui()
        self._generate_and_display()
    
    def _setup_ui(self):
        ax_generate = plt.axes([0.1, 0.1, 0.15, 0.04])
        self.btn_generate = Button(ax_generate, 'Generate New')
        self.btn_generate.on_clicked(self._on_generate_clicked)
        
        ax_seed = plt.axes([0.3, 0.1, 0.4, 0.03])
        self.slider_seed = Slider(ax_seed, 'Seed', 1, 1000, valinit=self.current_seed, valstep=1)
        self.slider_seed.on_changed(self._on_seed_changed)
        
        ax_export = plt.axes([0.75, 0.1, 0.15, 0.04])
        self.btn_export = Button(ax_export, 'Export')
        self.btn_export.on_clicked(self._on_export_clicked)
    
    def _generate_and_display(self):
        self.map_generator = TileBasedMap(self.tile_width, self.tile_height)
        self.map_generator.generate_map(seed=self.current_seed)
        self._display_map()
    
    def _display_map(self):
        self.ax.clear()
        
        terrain_array = self.map_generator.to_array()
        
        color_map = {
            0: [0.2, 0.4, 0.8],  # River - blue
            1: [0.1, 0.4, 0.1],  # Forest - dark green
            2: [0.4, 0.8, 0.2],  # Plain - light green
            3: [0.5, 0.5, 0.5],  # Cliff - gray
            4: [0.8, 0.6, 0.4]   # Highland - brown
        }
        
        colored_map = np.zeros((terrain_array.shape[0], terrain_array.shape[1], 3))
        for terrain_value, color in color_map.items():
            mask = terrain_array == terrain_value
            colored_map[mask] = color
        
        self.ax.imshow(colored_map, origin='upper')
        
        self._draw_tile_grid()
        
        legend_elements = [
            patches.Patch(color=color_map[0], label='River'),
            patches.Patch(color=color_map[1], label='Forest'),
            patches.Patch(color=color_map[2], label='Plain'),
            patches.Patch(color=color_map[3], label='Cliff'),
            patches.Patch(color=color_map[4], label='Highland')
        ]
        self.ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
        
        self.ax.set_title(f'Generated Map (Seed: {self.current_seed})')
        self.ax.set_xlabel('X Coordinate')
        self.ax.set_ylabel('Y Coordinate')
        
        self.fig.canvas.draw()
    
    def _draw_tile_grid(self):
        tile_size = self.map_generator.tile_size
        
        for i in range(self.tile_width + 1):
            x = i * tile_size - 0.5
            self.ax.axvline(x, color='black', alpha=0.3, linewidth=1)
        
        for i in range(self.tile_height + 1):
            y = i * tile_size - 0.5
            self.ax.axhline(y, color='black', alpha=0.3, linewidth=1)
        
        for ty in range(self.tile_height):
            for tx in range(self.tile_width):
                tile_template = self.map_generator.tiles[ty][tx]
                if tile_template:
                    center_x = tx * tile_size + tile_size // 2
                    center_y = ty * tile_size + tile_size // 2
                    self.ax.text(center_x, center_y, tile_template.name[:4], 
                               ha='center', va='center', fontsize=8, 
                               color='white', weight='bold',
                               bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.7))
    
    def _on_generate_clicked(self, event):
        self.current_seed = np.random.randint(1, 1000)
        self.slider_seed.set_val(self.current_seed)
        self._generate_and_display()
    
    def _on_seed_changed(self, val):
        self.current_seed = int(val)
        self._generate_and_display()
    
    def _on_export_clicked(self, event):
        self._export_map()
    
    def _export_map(self):
        import json
        
        export_data = {
            'width': self.map_generator.width,
            'height': self.map_generator.height,
            'tile_width': self.tile_width,
            'tile_height': self.tile_height,
            'tile_size': self.map_generator.tile_size,
            'seed': self.current_seed,
            'terrain_data': []
        }
        
        for y in range(self.map_generator.height):
            row = []
            for x in range(self.map_generator.width):
                cell = self.map_generator.get_cell(x, y)
                row.append(cell.terrain_type.value if cell else 'plain')
            export_data['terrain_data'].append(row)
        
        filename = f'map_seed_{self.current_seed}.json'
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        plt.figure(figsize=(10, 8))
        terrain_array = self.map_generator.to_array()
        color_map = {
            0: [0.2, 0.4, 0.8],
            1: [0.1, 0.4, 0.1],
            2: [0.4, 0.8, 0.2],
            3: [0.5, 0.5, 0.5],
            4: [0.8, 0.6, 0.4]
        }
        
        colored_map = np.zeros((terrain_array.shape[0], terrain_array.shape[1], 3))
        for terrain_value, color in color_map.items():
            mask = terrain_array == terrain_value
            colored_map[mask] = color
        
        plt.imshow(colored_map, origin='upper')
        plt.title(f'Exported Map (Seed: {self.current_seed})')
        plt.axis('off')
        
        image_filename = f'map_seed_{self.current_seed}.png'
        plt.savefig(image_filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"Map exported as {filename} and {image_filename}")
    
    def show(self):
        plt.show()

if __name__ == "__main__":
    visualizer = MapVisualizer()
    visualizer.show()