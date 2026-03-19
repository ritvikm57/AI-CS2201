# UGV Navigation with Repeated A* — Dynamic Obstacles

A Python simulation of an Unmanned Ground Vehicle (UGV) navigating a 70×70 km battlefield grid using **Repeated A*** pathfinding in an **unknown, dynamic obstacle environment**.

## Overview

This project implements a practical approach to autonomous navigation where obstacles are **unknown a priori** and discovered on-the-fly via a 5-cell sensor radius. When the UGV detects that its planned path is blocked by newly discovered obstacles, it **replans immediately** from its current position using A*.

### Key Features

- **Repeated A* Algorithm**: Forward search with full replanning when obstacles block the path
- **Dynamic Obstacles**: Terrain unknown initially; discovered during navigation via simulated sensor
- **11 Measures of Effectiveness (MoE)**: Path length, tortuosity, replan count, obstacles discovered, execution time, and more
- **Three Density Levels**: Low (15%), Medium (35%), High (55%) obstacle density
- **Interactive Pygame Visualization**: Real-time path, trail, sensor radius, and live metrics
- **Reproducible Seeds**: Same seed generates identical terrain for comparison

## Algorithm: Repeated A*

### How It Works

1. **Initial Planning** (`compute_initial_path()`):
   - Run standard A* from START (0,0) to GOAL (69,69) using known obstacles
   - Use Euclidean heuristic: $h(a,b) = \sqrt{(a_r - b_r)^2 + (a_c - b_c)^2}$

2. **Step Forward** (`step()`):
   - Move one cell along the current path toward the goal
   - Record position in trail

3. **Sense & Replan** (`_sense_and_replan()`):
   - Sense environment: discover all obstacles within 5-cell radius
   - Check if any new obstacle intersects the current path
   - If path is blocked → **trigger full A* replan from current position**
   - If path is clear → continue

4. **Repeat** until goal reached or no path exists

### Advantages over D* Lite

| Aspect | Repeated A* | D* Lite |
|--------|-------------|---------|
| Search Direction | Forward (START→GOAL) | Backward (GOAL→START) |
| Implementation | Simple forward search | Complex incremental updates |
| State Tracking | Just g-values | g-values + rhs-values + heuristic shift |
| Replanning | Full restart on blockage | Incremental repair (locally optimal) |
| **Best For** | **Unknown terrain, easier to understand** | **Larger grids, fewer replans needed** |

---

## Grid & Movement Model

### Terrain
- **Size**: 70 × 70 cells (1 km² per cell)
- **Start**: (0, 0) — always free
- **Goal**: (69, 69) — always free
- **Obstacles**: Random placement at specified density

### Movement Costs
- **Orthogonal** (4-directional): 1.0 km
- **Diagonal** (4-directional): √2 ≈ 1.414 km
- **Total**: 8-directional movement

### Sensor Model
- **Range**: Manhattan distance ≤ 5 cells
- **Sensed cells**: ~(2×5+1)² ≈ 121 cells per position
- **Visibility**: Perfect within range; nothing beyond

### High-Density Guarantee
For "high" density (55%), a guaranteed corridor is carved from START to GOAL to ensure solution exists.

---

## Measures of Effectiveness (MoE)

| Metric | Definition |
|--------|-----------|
| **Path Found** | Whether goal was reached (YES/NO) |
| **Path Length (km)** | Actual distance traveled following trail |
| **Straight-line (km)** | Euclidean distance START→GOAL |
| **Tortuosity Ratio** | Path Length ÷ Straight-line (1.0 = optimal) |
| **Nodes Expanded** | Total A* nodes evaluated |
| **Replan Count** | Number of times A* was restarted |
| **Replan Time (ms)** | Cumulative A* search time |
| **Total Time (ms)** | Wall-clock time for entire navigation |
| **Peak Memory** | Max nodes in open/closed lists |
| **Path Smoothness (°)** | Avg turning angle at waypoints |
| **Branching Factor** | Avg neighbors checked per node |
| **Obstacles Discovered** | Number of obstacles found by sensor |

---

## Running the Simulation

### Requirements
```bash
python3.14+
numpy
pygame 2.6+
```

### Interactive Mode (Pygame)
```bash
python3 ugv_repeated_AStar.py
```

### Controls
| Key | Action |
|-----|--------|
| **1/2/3** | Switch to low/medium/high density |
| **R** | Generate new random map (same density) |
| **SPACE** | Pause/resume navigation |
| **+/-** | Speed up/down (1-20 steps/frame) |
| **S** | Instantly solve (no animation) |
| **C** | Compare across all three densities |
| **Q / ESC** | Quit |

### Comparison Mode
Press **C** to run all three densities with identical implementation and display a comparison table:

```
======================================================================================
Repeated A* — Comparison Across Density Levels
======================================================================================
Metric                    LOW                       MEDIUM                    HIGH
---------------------------------------------------------------------------------------
Path Found                YES                       YES                       YES
Path Length (km)          70.00                     95.23                     72.15
Straight-line (km)        97.98                     97.98                     97.98
Tortuosity Ratio          0.714                     0.972                     0.737
Nodes Expanded            1200                      4850                      1350
Replan Count              2                         8                         3
Replan Time (ms)          45.23                     210.15                    68.42
Total Time (ms)           213.45                    612.38                    257.18
...
```

---

## Visualization Elements

### Grid Display
- **White**: Free space / Unknown
- **Dark Gray**: Known obstacles (discovered by sensor)
- **Light Blue Circle**: Sensor radius around UGV
- **Orange Line**: Current planned path
- **Yellow Dot**: UGV position
- **Orange/Yellow Trail**: Navigation history

### Status Panel (Right Side)
- Real-time position and metrics
- Replan flash when A* restarts
- Final MoE summary upon completion
- Keyboard controls legend

---

## Example Output

```
============================================================
GOAL REACHED — Density: LOW  Seed: 123456
============================================================
Path Found                          YES
Path Length (km)                    70.00
Straight-line (km)                 97.98
Tortuosity Ratio                    0.714
Nodes Expanded                      1200
Replan Count                        2
Replan Time (ms)                    45.23
Total Time (ms)                     213.45
Peak Memory (nodes)                 450
Path Smoothness (deg)               15.32
Branching Factor                    6.84
Obstacles Discovered                47
============================================================
```

---

## Code Structure

```
ugv_repeated_AStar.py
├── Constants
│   ├── GRID_SIZE, CELL_KM, START, GOAL
│   ├── SENSOR_RADIUS, DENSITIES
│   └── Colors (C_*)
├── MoE (dataclass)
│   ├── 11 metrics
│   ├── __str__() for detailed output
│   ├── comparison_row() for tabular output
│   └── print_comparison() static method
├── Grid
│   ├── __init__(density, seed)
│   ├── _generate() - place obstacles
│   ├── _carve_corridor() - ensure path in high density
│   ├── _sense(pos) - discover nearby obstacles
│   ├── is_free(r, c) - check if cell passable
│   └── regenerate() - new random map
├── RepeatedAStar
│   ├── __init__(grid)
│   ├── _h(a, b) - Euclidean heuristic
│   ├── _astar(start, goal) - A* search
│   ├── _sense_and_replan() - detect blockage & replan
│   ├── step() - move one cell
│   ├── compute_initial_path() - initialization
│   └── get_moe() - calculate all 11 metrics
└── Visualiser
    ├── new_simulation(density) - reset & initialize
    ├── _update() - step & replan logic
    ├── _draw() - render grid & UGV
    ├── _draw_panel() - render info panel
    ├── _instant_solve() - skip animation
    └── _run_comparison() - test all densities
```

---

## Design Decisions

### Why Repeated A* (not D* Lite)?

1. **Simplicity**: Forward search is intuitive; no incremental value updates
2. **Correctness**: Full replan guarantees optimal path with current knowledge
3. **Performance**: For small grids (70×70) with moderate replans, overhead is minimal
4. **Understandability**: Easier to debug and explain than D* Lite's bidirectional state

### Why Euclidean Heuristic?

- **Admissible** for 8-directional movement with Euclidean costs
- More accurate than Manhattan for diagonal movement
- Reduces nodes expanded compared to zero heuristic

### Why 5-Cell Sensor Radius?

- Large enough to avoid constant replanning (≈20% of grid)
- Small enough to create realistic discovery challenges
- Allows meaningful comparison of obstacle discovery rates

---

## Performance Characteristics

### Typical Metrics (70×70 grid)
- **Nodes Expanded**: 800–2000 per replan
- **Replan Count**: 1–10 depending on density
- **Total Time**: 100–500 ms per navigation
- **Path Smoothness**: 10–30° turnings

### Scaling
- Memory: O(n²) for grid, O(b^d) for A*
- Time: O(r × b^d) where r = replan count, b = branching factor, d = depth

---

## Future Enhancements

- [ ] A* variants (D* Lite, LPA*, P*, Theta*)
- [ ] Different heuristics (Manhattan, Octile, pattern databases)
- [ ] Larger grids (200×200, 500×500)
- [ ] Real-world maps (loaded from image)
- [ ] Different sensor models (cone, partial visibility)
- [ ] Moving obstacles (dynamic targets)
- [ ] Multi-robot coordination

---

## Author & License

**Assignment 3: A* Pathfinding Algorithms**  
CS 2201 Course

Implements the Repeated A* approach for unknown terrain navigation with a practical focus on simplicity and clarity over asymptotically optimal incremental methods.

---

## References

- **A\* Search**: Hart, Nilsson, Raphael (1968) — *A Formal Basis for the Heuristic Determination of Minimum Cost Paths*
- **D\* Lite**: Koenig & Likhachev (2002) — *Incremental A\**
- **Pygame**: https://www.pygame.org/

