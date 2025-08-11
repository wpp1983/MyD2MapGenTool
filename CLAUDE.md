# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MyMapGenTool is a Python-based tile-based map generation tool inspired by Diablo 2's map generation system. It creates procedural game maps using a dynamic configuration-driven approach with intelligent edge matching algorithms. The system supports 5 terrain types (highland, cliff, plain, forest, slope) with sophisticated constraint validation and WSL environment support.

## Development Commands

### Setup and Installation
```bash
# Install poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Running the Application
```bash
# Main unified launcher (recommended)
poetry run python D2MapGenTool.py

# Using poetry scripts
poetry run D2MapGenTool    # Main launcher
poetry run editor          # Interactive editor

# Individual components (advanced usage)
poetry run python src/map_visualizer.py
poetry run python src/interactive_editor.py

# Or in activated shell
python D2MapGenTool.py
```

### Development Tools
```bash
# Code formatting
poetry run black .

# Linting
poetry run flake8 .

# Running tests
poetry run pytest                    # All tests
poetry run pytest -v                 # Verbose output
poetry run pytest -m unit            # Unit tests only
poetry run pytest -m integration     # Integration tests only
poetry run pytest -m "not slow"     # Skip slow tests
```

### Key Dependencies
- **matplotlib^3.5.0** - Visualization, GUI, and plotting
- **numpy^1.21.0** - Array operations and numerical computing
- **Development dependencies**: pytest (testing), black (formatting), flake8 (linting)
- **Python requirement**: ^3.8.1
- **Poetry scripts**: D2MapGenTool (main), editor (interactive editor)

## Architecture Overview

### Project Structure
```
MyMapGenTool/
├── D2MapGenTool.py           # Main unified launcher
├── config/                   # Configuration files
│   ├── templates_config.json # Terrain templates and rules
│   └── config.json          # Runtime configuration
├── src/                     # Core source code
│   ├── terrain_types.py     # Dynamic terrain/edge type system
│   ├── template_loader.py   # Configuration-based template loader
│   ├── map_generator.py     # Core map generation engine
│   ├── map_visualizer.py    # Visualization and GUI
│   ├── interactive_editor.py # Advanced editing capabilities
│   └── app_config.py        # Application configuration management
├── tests/                   # Comprehensive test suite (32 tests)
│   ├── test_cliff_constraints.py
│   ├── test_template_loader.py
│   ├── test_integration.py
│   └── ...
└── output/                  # Generated maps and exports
```

### Core Components

**src/terrain_types.py** - Dynamic terrain system:
- `TerrainType` class: Dynamic terrain types loaded from JSON config
- `EdgeType` class: Dynamic edge types with compatibility rules
- `TileTemplate` class: Template data structure with string-based edge matching
- `TerrainCell` class: Individual grid cell with configurable colors
- String-based system instead of enums for flexibility

**src/template_loader.py** - Configuration-driven template creation:
- `TemplateLoader` class: Loads all templates from JSON configuration
- Supports uniform terrain patterns and split patterns (horizontal/vertical)
- Handles terrain colors, edge compatibility, and generation rules
- Dynamic template creation based on configuration

**src/map_generator.py** - Core generation engine:
- `TileBasedMap` class: Main map generator with constraint validation
- Implements cliff constraint rules (requires plain AND highland neighbors)
- Smart template placement with configuration-based edge compatibility
- Weighted random selection using template weights from config
- Grid size: tile_width × tile_height tiles, each tile is 8×8 cells by default

**src/map_visualizer.py** - Visualization and export:
- `MapVisualizer` class: matplotlib-based GUI with WSL support
- Real-time parameter adjustment (seed slider)
- Export functionality (JSON data + PNG images)
- Headless mode for batch generation
- Automatic X11 configuration for WSL environments

**src/interactive_editor.py** - Advanced editing:
- `InteractiveMapEditor` class: Extends MapVisualizer with editing capabilities  
- Click-to-paint terrain modification
- Custom template saving from edited regions
- Edit history tracking with visual indicators

**src/app_config.py** - Runtime configuration:
- `AppConfig` class: Manages runtime behavior and settings
- WSL environment detection and X11 setup
- GUI/headless mode configuration
- Batch generation settings

**D2MapGenTool.py** - Unified launcher:
- Intelligent GUI/headless mode detection
- WSL environment configuration
- Automatic fallback from GUI to headless mode
- Batch generation with multiple seeds

### Tile System Architecture

The system uses a configuration-driven two-level hierarchy:
1. **Tile Level**: Large regions (8×8 cells) with JSON-defined patterns and edge types
2. **Cell Level**: Individual terrain cells within each tile

**Dynamic Configuration System**:
- All terrain types, edges, and templates loaded from `config/templates_config.json`
- String-based terrain system for flexibility and easy configuration
- Runtime initialization of terrain and edge types from configuration

**Edge Matching Rules**:
- Tiles connect based on compatible edge types (north/south/east/west)
- Configuration-based compatibility rules from `edge_compatibility` array
- Current compatibility: plain↔forest, slope↔plain, highland↔slope, etc.
- Exact matching or configured compatibility rules

**Template Weighting (configurable)**:
- Plain: 3.0 (most common)
- Forest: 2.0
- Highland: 1.5
- Slope: 1.0
- Cliff: 0.5 (rarest, with special constraints)

**Constraint System**:
- Advanced generation rules in `generation_rules` config section
- Cliff constraints: Must have both plain AND highland neighbors
- Extensible constraint system for other terrain types

### Data Flow

1. **Initialization**:
   - `AppConfig` loads runtime configuration from `config/config.json`
   - `TemplateLoader` loads terrain definitions from `config/templates_config.json`
   - `TerrainType` and `EdgeType` initialize dynamic type systems

2. **Template Creation**:
   - `TemplateLoader.create_templates()` generates all tile templates from config
   - Sets up edge compatibility rules and terrain colors
   - Applies constraint rules (e.g., cliff generation rules)

3. **Map Generation**:
   - `TileBasedMap.generate_map(seed)` creates empty tile grid
   - For each position, `get_valid_templates()` finds compatible templates
   - Applies constraint validation (cliff constraints)
   - `random.choices()` selects template using configured weights
   - `_apply_template()` converts tile template to individual terrain cells

4. **Visualization**:
   - `MapVisualizer` converts terrain grid to colored numpy array
   - WSL environment detection and X11 configuration
   - Real-time GUI updates or headless batch processing

5. **Export**:
   - Structured JSON export with metadata
   - PNG image export with configurable colors
   - Batch export for multiple seeds in headless mode

## Configuration System

### Main Configuration Files

**config/templates_config.json** - Core terrain and template definitions:
```json
{
  "templates": [          // Template definitions with patterns and edges
    {
      "name": "plain",
      "terrain_pattern": "plain",
      "edges": {"north": "plain", "south": "plain", ...},
      "weight": 3.0
    }
  ],
  "terrain_types": {      // Terrain type names and descriptions
    "plain": "平原", "forest": "森林", ...
  },
  "terrain_colors": {     // RGB color definitions
    "plain": [0.4, 0.8, 0.2], ...
  },
  "edge_compatibility": [ // Compatibility rules
    ["plain", "forest"], ["slope", "plain"], ...
  ],
  "generation_rules": {   // Constraint rules
    "cliff": {
      "required_neighbors": {"must_have": ["plain", "highland"]}
    }
  }
}
```

**config/config.json** - Runtime behavior settings:
```json
{
  "ui": {
    "enable_gui": true    // Enable/disable GUI mode
  }
}
```

### Export Formats

**JSON Map Export Structure**:
```json
{
  "width": 96,           // Total pixel width (tile_width * tile_size)
  "height": 80,          // Total pixel height  
  "tile_width": 12,      // Number of tiles horizontally
  "tile_height": 10,     // Number of tiles vertically
  "tile_size": 8,        // Cells per tile (8x8)
  "seed": 42,
  "terrain_data": [...]  // 2D array of terrain type strings
}
```

**Custom Template Format**:
```json
{
  "name": "custom_template_N",
  "size": [width, height],
  "pattern": [...],      // 2D terrain pattern
  "edited_cells": [...]  // List of modified coordinates
}
```

## Key Algorithms

**Dynamic Type System**: String-based terrain types loaded at runtime from JSON configuration
**Template Loading**: `TemplateLoader` creates templates from JSON patterns with support for uniform and split patterns
**Edge Compatibility**: Configuration-based compatibility rules with runtime validation
**Constraint Validation**: Sophisticated cliff placement rules requiring specific neighbor combinations
**Template Validation**: `TileTemplate.can_connect()` checks edge compatibility with configuration-based rules
**Generation Strategy**: Left-to-right, top-to-bottom placement ensures maximum constraint information
**WSL Support**: Automatic X11 configuration and backend selection for Windows Subsystem for Linux

## Testing Framework

### Test Structure
Comprehensive test suite with 32 test cases covering:
- **Unit Tests**: Template loader, dynamic type system, compatibility rules
- **Integration Tests**: End-to-end map generation, performance testing
- **Constraint Tests**: Cliff generation rules with parametrized seeds
- **Configuration Tests**: JSON loading, error handling, fallback behavior

### Test Commands
```bash
poetry run pytest                    # All tests
poetry run pytest -m unit            # Unit tests only
poetry run pytest -m integration     # Integration tests
poetry run pytest -m "not slow"     # Skip performance tests
poetry run pytest --cov=src         # Coverage report
```

### Test Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests  
- `@pytest.mark.slow` - Performance/slow tests

## WSL Environment Support

### Automatic Configuration
- WSL environment detection via kernel release string
- Automatic DISPLAY variable setup (defaults to :0)
- matplotlib backend selection (TkAgg vs Agg)
- X11 forwarding guidance and troubleshooting

### X11 Setup Instructions
1. Install VcXsrv Windows X Server
2. Configure: Multiple windows, Disable access control
3. Set environment: `export DISPLAY=:0`
4. Or disable GUI in config: `{"ui": {"enable_gui": false}}`

## Development Notes

- **Coordinate System**: (x, y) convention with origin at top-left
- **String-Based Types**: Terrain and edge types use strings for flexibility
- **Configuration-Driven**: All templates, colors, and rules loaded from JSON
- **Color Mapping**: Centralized in `TerrainCell.get_color_map()` from configuration
- **Template Storage**: numpy arrays with string dtype for terrain patterns
- **GUI Backend**: Automatic selection with WSL compatibility
- **Constraint System**: Extensible rule system for terrain placement validation