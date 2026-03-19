# UGV A* Pathfinding Simulation

A comprehensive Python simulation of an Unmanned Ground Vehicle (UGV) navigating a battlefield grid using the A* pathfinding algorithm with pygame visualization.

## Overview

This project implements a complete A* search algorithm from scratch on a 70×70 km grid where:
- Each cell represents 1 km²
- Cell value 0 = free space, 1 = obstacle
- Start position: top-left (0,0)
- Goal position: bottom-right (69,69)

## Features

### Algorithm Implementation
- **A* Search**: Optimal pathfinding using f(n) = g(n) + h(n)
  - g(n): actual cost from start node
  - h(n): Euclidean distance heuristic to goal
- **8-Directional Movement**: Cardinal (cost 1.0 km) + Diagonal (cost √2 km)
- **Data Structures**: Min-heap priority queue via `heapq`, tracked open/closed lists
- **Path Reconstruction**: Parent map tracking for efficient path recovery

### Grid & Obstacles
- **Random Generation**: Fixed seed for reproducibility, regenerate with new seed via 'R' key
- **Three Density Levels**:
  - LOW: 15% obstacle density
  - MEDIUM: 35% obstacle density
  - HIGH: 55% obstacle density with automatic corridor carving to guarantee paths
- **Guaranteed Start/Goal**: Always ensure start and goal cells are free

### Measures of Effectiveness (MoE)

All metrics are computed and displayed in real-time:

1. **Path Length (km)**: Sum of actual edge costs traversed
2. **Straight-line Distance (km)**: Euclidean distance from start to goal
3. **Tortuosity Ratio**: Path length / straight-line distance (1.0 = optimal)
4. **Nodes Expanded**: Size of closed list at termination
5. **Open List Size**: Frontier nodes remaining when search ends
6. **Computation Time (ms)**: Wall-clock execution time
7. **Peak Memory**: Maximum combined size of open + closed lists during search
8. **Path Smoothness**: Average turn angle (degrees) between consecutive path steps
9. **Success/Failure**: Binary indicator with failure reason if applicable

### Visualization

- **Grid Display**: White = free cell, Dark gray = obstacle
- **Start/Goal**: Green circle (start), Red circle (goal)
- **Exploration**: Pale blue fill shows visited nodes during animation
- **Final Path**: Bright orange line drawn over the grid
- **Sidebar Panel**: Real-time MoE metrics, grid info, and controls
- **Animated Search**: Frame-by-frame visualization of A* frontier expansion

### Interactive Controls

| Key | Action |
|-----|--------|
| **1** | Switch to LOW density grid |
| **2** | Switch to MEDIUM density grid |
| **3** | Switch to HIGH density grid |
| **R** | Regenerate obstacles with new random seed |
| **SPACE** | Pause/Resume animation |
| **+** | Speed up animation (up to 500 steps/frame) |
| **-** | Slow down animation (minimum 1 step/frame) |
| **C** | Run comparison across all three density levels |
| **Q** | Quit application |

## Installation

### Requirements
```
Python 3.7+
numpy
pygame
```

### Setup
```bash
# Install dependencies
pip install numpy pygame

# Run the simulation
python ugv_astar.py
```

## Usage

### Start Simulation
```bash
python ugv_astar.py
```

The program will:
1. Initialize the pygame window
2. Display a 70×70 grid with randomly distributed obstacles
3. Show current grid seed and density level in the sidebar
4. Await your key press to begin A* search

### Running a Search

1. Press **1**, **2**, or **3** to select density and start search
2. Watch the animation progress as A* explores the grid
3. Control animation speed with **+** and **-** keys
4. Pause search with **SPACE** to examine details
5. After search completes, MoE values appear in sidebar and terminal

### Comparison Analysis

Press **C** to automatically:
1. Run A* on all three density levels sequentially
2. Print formatted comparison table showing all MoE across densities
3. Calculate how performance metrics change with obstacle density

### Terminal Output

After each search, a formatted MoE table prints to the console:

```
==================================================
SEARCH COMPLETE - Density: LOW
Grid Seed: 123456
==================================================
Path Found                YES
Path Length (km)          45.32
Straight-line Distance (km) 37.48
Tortuosity Ratio          1.210
Nodes Expanded            3450
Open List Size            245
Computation Time (ms)     125.34
Peak Memory (cells)       3695
Path Smoothness (deg)     32.45
==================================================
```

When running a comparison with **C**, a side-by-side table appears:

```
COMPARISON TABLE: A* Performance Across Density Levels
=====================================================...
Metric                     LOW                   MEDIUM                HIGH
Path Found                 YES                   YES                   YES
Path Length (km)           45.32                 52.18                 68.74
Straight-line (km)        37.48                 37.48                 37.48
Tortuosity Ratio          1.210                 1.391                 1.834
Nodes Expanded            3450                  8234                  15670
...
```

## Code Structure

### Classes

#### `MoE` (dataclass)
Stores all Measures of Effectiveness metrics with formatted output methods.

#### `Grid`
- Generates and manages the obstacle map
- Handles seed-based random generation with three density levels
- Implements corridor carving for high-density guarantee
- Methods: `__init__`, `_generate_obstacles()`, `_carve_corridor()`, `is_free()`, `regenerate()`

#### `AStar`
- Complete A* algorithm implementation
- Uses min-heap priority queue for open list
- Tracks g, h, f values and parent relationships
- Methods:
  - `run()`: Execute complete search immediately
  - `step()`: Single expansion step for animation
  - `step_iterator()`: Generator yielding animation frames
  - `_heuristic()`: Euclidean distance
  - `_reconstruct_path()`: Build path from parent map
  - `_calculate_path_smoothness()`: Compute average turn angles
  - `get_metrics()`: Generate MoE report

#### `Visualiser`
- Pygame rendering and event handling
- Grid visualization with explored nodes
- Real-time MoE panel display
- Animation frame control
- Comparison runner
- Methods:
  - `draw()`: Render complete scene
  - `draw_panel()`: Sidebar MoE display
  - `update_animation()`: Advance A* steps
  - `handle_events()`: Keyboard control processing
  - `run_comparison()`: Run all densities and print table
  - `run()`: Main loop (60 FPS)

#### `main()`
Initialization function setting up Grid and Visualiser, then starts the application.

## Algorithm Details

### A* Search Process

1. **Initialize**: Start node in open list with f = h(start)
2. **Loop**: While open list not empty:
   - Pop node with minimum f value
   - If goal reached, return reconstructed path
   - Mark as closed, expand all valid neighbors
   - For each neighbor:
     - Calculate tentative g value (current g + edge cost)
     - If lower than previous g, update parent and add to open list
3. **Termination**: Return path or None if goal unreachable

### Cost Calculation

- Cardinal moves (N, S, E, W): 1.0 km per cell
- Diagonal moves (NE, NW, SE, SW): √2 km per cell
- Total path cost: sum of all edge costs

### Heuristic

Euclidean distance from position to goal:
$$h(n) = \sqrt{(n_{row} - goal_{row})^2 + (n_{col} - goal_{col})^2}$$

## Performance Characteristics

### Observation Patterns

**Low Density (15%)**
- Fewest obstacles provide shortest paths
- Low tortuosity ratio (path close to straight line)
- Fewer nodes expanded
- Fastest computation time

**Medium Density (35%)**
- Moderate obstacle placement
- Balanced path length and exploration cost
- Increased nodes expanded vs low density

**High Density (55%)**
- Corridor carving may constrain paths
- Higher tortuosity ratio
- Significantly more nodes expanded
- Longer computation times

## Constraints & Libraries

**Allowed Libraries Only**:
- `heapq`: Priority queue implementation
- `numpy`: Grid storage and operations
- `pygame`: Visualization and rendering
- `dataclasses`: MoE structure
- `math`: Distance calculations (sqrt, atan2, degrees)
- `time`: Computation timing
- `random`: Obstacle generation
- `sys`: System utilities

**No External Pathfinding Libraries**: Pure A* implementation from scratch.

## Example Run

```bash
$ python ugv_astar.py
======================================================================
UGV A* PATHFINDING SIMULATION
======================================================================

Initializing 70x70 km grid with A* search algorithm...
pygame version: 2.1.3

Press any key (1/2/3) to start, or Q to quit
```

[Pygame window opens showing 70×70 grid]

Press **2** → Search on MEDIUM density starts animating

Press **SPACE** → Animation pauses

Press **C** → Comparison runs across all densities and prints results

Press **Q** → Application closes gracefully

## Future Enhancements

- Different heuristics (Manhattan, Chebyshev)
- Bidirectional A* search
- Jump Point Search (JPS) optimization
- Theta* for smooth paths
- Real-time obstacle updates
- Pathfinding for multiple simultaneous agents
- Different movement cost models (terrain difficulty)

## Author Notes

This implementation prioritizes clarity and educational value while maintaining algorithmic correctness. All MoE calculations can be verified by examining terminal output and visual confirmation of path properties.

The corridor carving for high-density maps uses a simple diagonal approach from start to goal, ensuring at least one guaranteed path exists while maintaining high obstacle density for realistic scenarios.
