# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MyMapGenTool is a Python-based tile-based map generation tool inspired by Diablo 2's map generation system. It creates procedural game maps using pre-defined tile templates with intelligent edge matching algorithms.

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
# Using poetry run (recommended)
poetry run python demo.py
poetry run python interactive_editor.py
poetry run python map_visualizer.py

# Or using poetry scripts (if configured)
poetry run demo
poetry run editor

# Or in activated shell
python demo.py
python interactive_editor.py
python map_visualizer.py
```

### Development Tools
```bash
# Code formatting
poetry run black .

# Linting
poetry run flake8 .

# Running tests (when available)
poetry run pytest
```

### Key Dependencies
- matplotlib^3.5.0 (visualization and GUI)
- numpy^1.21.0 (array operations and numerical computing)
- Development dependencies: pytest, black, flake8

## Architecture Overview

### Core Components

**terrain_types.py** - Foundation module defining:
- `TerrainType` enum: HIGHLAND, CLIFF, PLAIN, FOREST, RIVER
- `EdgeType` enum: Edge compatibility definitions for tile connections
- `TileTemplate` class: Template data structure with edge matching logic
- `TerrainCell` class: Individual grid cell with terrain type and color mapping

**map_generator.py** - Core generation engine:
- `TileBasedMap` class: Main map generator using tile-based approach
- Implements 7 predefined tile templates (plain, forest, highland, river variants, mixed templates)
- Smart template placement with edge compatibility validation
- Weighted random selection for terrain distribution
- Grid size: tile_width × tile_height tiles, each tile is 8×8 cells by default

**map_visualizer.py** - Visualization and export:
- `MapVisualizer` class: matplotlib-based interactive GUI
- Real-time parameter adjustment (seed slider)
- Export functionality (JSON data + PNG images)
- Tile grid overlay showing template boundaries and names

**interactive_editor.py** - Advanced editing:
- `InteractiveMapEditor` class: Extends MapVisualizer with editing capabilities  
- Click-to-paint terrain modification
- Custom template saving from edited regions
- Edit history tracking with visual indicators

### Tile System Architecture

The system uses a two-level hierarchy:
1. **Tile Level**: Large regions (8×8 cells) with predefined patterns and edge types
2. **Cell Level**: Individual terrain cells within each tile

**Edge Matching Rules**:
- Tiles connect based on compatible edge types (north/south/east/west)
- Supports exact matching and compatibility rules (e.g., PLAIN_EDGE ↔ FOREST_EDGE)
- River tiles require RIVER_EDGE connections on flow direction
- Mixed templates enable gradual terrain transitions

**Template Weighting**:
- Plain: 3.0 (most common)
- Forest: 2.0
- Highland: 1.5  
- Mixed templates: 1.2
- Rivers: 0.8
- Highland-cliff: 0.5 (rarest)

### Data Flow

1. `TileBasedMap.generate_map(seed)` creates empty tile grid
2. For each tile position, `get_valid_templates()` finds compatible templates based on neighbors
3. `random.choices()` selects template using weights
4. `_apply_template()` converts tile template to individual terrain cells
5. `MapVisualizer` converts terrain grid to colored numpy array for display
6. Export functions save both structured JSON and visual PNG output

## File I/O Formats

### JSON Export Structure
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

### Custom Template Format
```json
{
  "name": "custom_template_N",
  "size": [width, height],
  "pattern": [...],      // 2D terrain pattern
  "edited_cells": [...]  // List of modified coordinates
}
```

## Key Algorithms

**Template Validation**: `TileTemplate.can_connect()` checks edge compatibility in all four directions before placement
**Generation Strategy**: Left-to-right, top-to-bottom placement ensures each new tile has maximum constraint information
**Export Processing**: `to_array()` method converts TerrainType enums to integer values for efficient numpy operations

## Development Notes

- All coordinates use (x, y) convention with origin at top-left
- matplotlib visualization uses 'upper' origin to match array indexing
- Template patterns are stored as numpy arrays for efficient processing
- Color mapping is centralized in TerrainCell.get_color() method
- GUI components use matplotlib widgets for cross-platform compatibility