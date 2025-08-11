import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons
import numpy as np
from map_visualizer import MapVisualizer
from terrain_types import TerrainType

class InteractiveMapEditor(MapVisualizer):
    def __init__(self, tile_width: int = 10, tile_height: int = 8):
        self.edit_mode = False
        self.selected_terrain_str = 'plain'  # 使用字符串而不是枚举
        
        super().__init__(tile_width, tile_height)
        self._setup_edit_ui()
        
        self.fig.canvas.mpl_connect('button_press_event', self._on_click)
    
    def _setup_edit_ui(self):
        plt.subplots_adjust(bottom=0.35, right=0.85)
        
        ax_edit = plt.axes([0.1, 0.16, 0.15, 0.04])
        self.btn_edit = Button(ax_edit, 'Edit Mode')
        self.btn_edit.on_clicked(self._toggle_edit_mode)
        
        ax_radio = plt.axes([0.88, 0.3, 0.1, 0.4])
        terrain_labels = ['Plain', 'Forest', 'Highland', 'Cliff', 'Slope']
        self.radio_terrain = RadioButtons(ax_radio, terrain_labels)
        self.radio_terrain.on_clicked(self._on_terrain_selected)
        
        ax_clear = plt.axes([0.3, 0.16, 0.15, 0.04])
        self.btn_clear = Button(ax_clear, 'Clear Edits')
        self.btn_clear.on_clicked(self._clear_edits)
        
        ax_save_template = plt.axes([0.5, 0.16, 0.2, 0.04])
        self.btn_save_template = Button(ax_save_template, 'Save as Template')
        self.btn_save_template.on_clicked(self._save_as_template)
        
        self.edited_cells = set()
    
    def _toggle_edit_mode(self, event):
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.btn_edit.label.set_text('Exit Edit')
            self.ax.set_title(f'Edit Mode - Click to paint {self.selected_terrain_str}')
        else:
            self.btn_edit.label.set_text('Edit Mode')
            self.ax.set_title(f'Generated Map (Seed: {self.current_seed})')
        self.fig.canvas.draw()
    
    def _on_terrain_selected(self, label):
        terrain_map = {
            'Plain': 'plain',
            'Forest': 'forest',
            'Highland': 'highland',
            'Cliff': 'cliff',
            'Slope': 'slope'
        }
        self.selected_terrain_str = terrain_map[label]
        
        if self.edit_mode:
            self.ax.set_title(f'Edit Mode - Click to paint {self.selected_terrain_str}')
            self.fig.canvas.draw()
    
    def _on_click(self, event):
        if not self.edit_mode or event.inaxes != self.ax:
            return
        
        if event.xdata is None or event.ydata is None:
            return
        
        x = int(event.xdata)
        y = int(event.ydata)
        
        if 0 <= x < self.map_generator.width and 0 <= y < self.map_generator.height:
            cell = self.map_generator.get_cell(x, y)
            if cell:
                cell.terrain_type = self.selected_terrain_str  # 现在使用字符串
                self.edited_cells.add((x, y))
                self._display_map()
    
    def _clear_edits(self, event):
        self._generate_and_display()
        self.edited_cells.clear()
    
    def _save_as_template(self, event):
        if not self.edited_cells:
            print("No edits to save as template")
            return
        
        min_x = min(x for x, y in self.edited_cells)
        max_x = max(x for x, y in self.edited_cells)
        min_y = min(y for x, y in self.edited_cells)
        max_y = max(y for x, y in self.edited_cells)
        
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        
        template_data = []
        for y in range(min_y, max_y + 1):
            row = []
            for x in range(min_x, max_x + 1):
                cell = self.map_generator.get_cell(x, y)
                row.append(cell.terrain_type if cell else 'plain')  # 现在是字符串
            template_data.append(row)
        
        template_dict = {
            'name': f'custom_template_{len(self.edited_cells)}',
            'size': [width, height],
            'pattern': template_data,
            'edited_cells': list(self.edited_cells)
        }
        
        import json
        filename = f'custom_template_{self.current_seed}.json'
        with open(filename, 'w') as f:
            json.dump(template_dict, f, indent=2)
        
        print(f"Template saved as {filename}")
    
    def _display_map(self):
        super()._display_map()
        
        if self.edited_cells:
            for x, y in self.edited_cells:
                circle = plt.Circle((x, y), 0.3, color='red', alpha=0.6, fill=False, linewidth=2)
                self.ax.add_patch(circle)
        
        if self.edit_mode:
            instruction_text = f"Edit Mode: Click to paint {self.selected_terrain_str}\nEdited cells: {len(self.edited_cells)}"
            self.ax.text(0.02, 0.98, instruction_text, transform=self.ax.transAxes, 
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))

if __name__ == "__main__":
    editor = InteractiveMapEditor(tile_width=12, tile_height=10)
    editor.show()