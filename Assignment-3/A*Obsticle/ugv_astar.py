"""
A* pathfinding sim for UGV on a grid with obstacles

Uses A* with euclidean heuristic. 70x70 grid cells.
Keys: 1/2/3 for density, R for new seed, SPACE to pause, +/- for speed, C to compare, Q to quit

Tracks path length, tortuosity, nodes expanded, time, memory, smoothness
"""

import heapq
import math
import time
import random
import os
import numpy as np
import pygame
from dataclasses import dataclass
from typing import List, Tuple, Optional, Iterator
import sys


@dataclass
class MoE:
    # Measures of Effectiveness - tracks all the perf metrics
    path_length_km: float = 0.0
    straight_line_distance_km: float = 0.0
    tortuosity_ratio: float = 0.0
    nodes_expanded: int = 0
    open_list_size: int = 0
    computation_time_ms: float = 0.0
    peak_memory: int = 0
    path_smoothness_deg: float = 0.0
    branching_factor: float = 0.0
    path_found: bool = False
    failure_reason: str = ""

    def __str__(self) -> str:
        if not self.path_found:
            return (
                f"{'PATH FOUND':<25} {'NO':<15}\n"
                f"{'Failure Reason':<25} {self.failure_reason:<15}\n"
                f"{'Nodes Expanded':<25} {self.nodes_expanded:<15}\n"
                f"{'Open List Size':<25} {self.open_list_size:<15}\n"
                f"{'Computation Time (ms)':<25} {self.computation_time_ms:<15.2f}\n"
                f"{'Peak Memory (cells)':<25} {self.peak_memory:<15}\n"
                f"{'Branching Factor':<25} {self.branching_factor:<15.2f}"
            )
        return (
            f"{'Path Found':<25} {'YES':<15}\n"
            f"{'Path Length (km)':<25} {self.path_length_km:<15.2f}\n"
            f"{'Straight-line Distance (km)':<25} {self.straight_line_distance_km:<15.2f}\n"
            f"{'Tortuosity Ratio':<25} {self.tortuosity_ratio:<15.3f}\n"
            f"{'Nodes Expanded':<25} {self.nodes_expanded:<15}\n"
            f"{'Open List Size':<25} {self.open_list_size:<15}\n"
            f"{'Computation Time (ms)':<25} {self.computation_time_ms:<15.2f}\n"
            f"{'Peak Memory (cells)':<25} {self.peak_memory:<15}\n"
            f"{'Path Smoothness (deg)':<25} {self.path_smoothness_deg:<15.2f}\n"
            f"{'Branching Factor':<25} {self.branching_factor:<15.2f}"
        )


class Grid:
    # Grid management - obstacles, seeding, etc
    GRID_SIZE = 70
    CELL_SIZE_KM = 1.0
    START = (0, 0)
    GOAL = (69, 69)

    def __init__(self, density: str = "low", seed: Optional[int] = None):
        self.density = density
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.grid = np.zeros((self.GRID_SIZE, self.GRID_SIZE), dtype=int)
        self._generate_obstacles()

    def _generate_obstacles(self):
        # set seeds for reproducibility
        random.seed(self.seed)
        np.random.seed(self.seed)

        # density determines % of obstacles
        if self.density == "low":
            obstacle_percentage = 0.15
        elif self.density == "medium":
            obstacle_percentage = 0.35
        else:  # high
            obstacle_percentage = 0.55

        # Generate random obstacles
        # total cells and how many should be obstacles
        total_cells = self.GRID_SIZE * self.GRID_SIZE
        num_obstacles = int(total_cells * obstacle_percentage)

        # pick random cells (but not start/goal)
        available_cells = [
            (r, c) for r in range(self.GRID_SIZE)
            for c in range(self.GRID_SIZE)
            if (r, c) != self.START and (r, c) != self.GOAL
        ]

        # randomly place obstacles
        obstacle_cells = random.sample(available_cells, num_obstacles)
        for r, c in obstacle_cells:
            self.grid[r, c] = 1

        # for high density, make sure there's at least a path through
        if self.density == "high":
            self._carve_corridor()

    def _carve_corridor(self):
        # Carve a path through high density so goal is reachable
        r, c = self.START
        while (r, c) != self.GOAL:
            self.grid[r, c] = 0
            # move closer to goal
            if r < self.GOAL[0]:
                r += 1
            elif c < self.GOAL[1]:
                c += 1
            else:
                break

    def is_free(self, row: int, col: int) -> bool:
        return (0 <= row < self.GRID_SIZE and
                0 <= col < self.GRID_SIZE and
                self.grid[row, col] == 0)  # 0 = free, 1 = obstacle

    def regenerate(self, density: str = None):
        # new obstacles, new seed
        if density:
            self.density = density
        # use os.urandom for independent seed generation
        self.seed = int.from_bytes(os.urandom(4), 'big') % 1000000
        self.grid = np.zeros((self.GRID_SIZE, self.GRID_SIZE), dtype=int)
        self._generate_obstacles()


class AStar:
    # A* implementation - straight forward priority queue based search
    # 8 directions - cardinal moves (1.0 cost) + diagonals (sqrt2 cost)
    MOVEMENTS = [
        (-1, 0, 1.0),   # up
        (1, 0, 1.0),    # down
        (0, -1, 1.0),   # left
        (0, 1, 1.0),    # right
        (-1, -1, math.sqrt(2)),  # up-left diagonal
        (-1, 1, math.sqrt(2)),   # up-right
        (1, -1, math.sqrt(2)),   # down-left
        (1, 1, math.sqrt(2))     # down-right
    ]

    def __init__(self, grid: Grid):
        self.grid = grid
        self.start = grid.START
        self.goal = grid.GOAL
        self.open_list = []
        self.closed_list = set()
        self.parent_map = {}
        self.g_values = {self.start: 0.0}
        self.start_time = None
        self.max_open_size = 0
        self.path = None
        self._counter = 0  # counter for heapq tiebreaker instead of id()
        self.total_neighbor_checks = 0  # track for branching factor

    def _heuristic(self, pos: Tuple[int, int]) -> float:
        # euclidean distance to goal - standard heuristic
        return math.sqrt((pos[0] - self.goal[0])**2 + (pos[1] - self.goal[1])**2)

    def _reconstruct_path(self, node: Tuple[int, int]) -> List[Tuple[int, int]]:
        # walk back through parent map to rebuild the path
        path = [node]
        while node in self.parent_map:
            node = self.parent_map[node]
            path.append(node)
        return path[::-1]

    def _calculate_path_smoothness(self, path: List[Tuple[int, int]]) -> float:
        if len(path) < 3:
            return 0.0

        angles = []
        for i in range(1, len(path) - 1):
            p1 = path[i-1]
            p2 = path[i]
            p3 = path[i+1]

            # vectors between points
            v1 = (p1[0] - p2[0], p1[1] - p2[1])
            v2 = (p3[0] - p2[0], p3[1] - p2[1])

            # use atan2 to get heading angles (kinda hacky but works)
            angle1 = math.atan2(v1[1], v1[0])
            angle2 = math.atan2(v2[1], v2[0])
            turn_angle = abs(angle2 - angle1)

            # normalize to [0, 180]
            if turn_angle > math.pi:
                turn_angle = 2 * math.pi - turn_angle

            angles.append(math.degrees(turn_angle))

        return sum(angles) / len(angles) if angles else 0.0

    def step(self) -> bool:
        # single step of astar - expand best node and check neighbors
        if not self.open_list:
            return False

        # get node with lowest f value from heap
        _, _, current = heapq.heappop(self.open_list)

        # add to closed list first
        self.closed_list.add(current)

        if current == self.goal:
            return True

        # expand all neighbors
        r, c = current
        for dr, dc, cost in self.MOVEMENTS:
            neighbor = (r + dr, c + dc)
            self.total_neighbor_checks += 1

            if not self.grid.is_free(neighbor[0], neighbor[1]):
                continue

            if neighbor in self.closed_list:
                continue

            tentative_g = self.g_values[current] + cost
            nr, nc = neighbor  # just for convenience

            # only consider if this path is better or new
            if neighbor not in self.g_values or tentative_g < self.g_values[neighbor]:
                self.parent_map[neighbor] = current
                self.g_values[neighbor] = tentative_g
                h = self._heuristic(neighbor)
                f = tentative_g + h
                self._counter += 1
                heapq.heappush(self.open_list, (f, self._counter, neighbor))

        self.max_open_size = max(self.max_open_size, len(self.open_list))
        return False

    def run(self) -> Optional[List[Tuple[int, int]]]:
        # run the full search
        self.start_time = time.time()
        self._counter = 1
        self.open_list = [(self._heuristic(self.start), self._counter, self.start)]
        self.g_values[self.start] = 0.0

        while self.open_list:
            if self.step():
                self.path = self._reconstruct_path(self.goal)
                return self.path

        return None

    def step_iterator(self) -> Iterator[Tuple[set, List[Tuple[int, int]]]]:
        # generator for animation - yields closed list and frontier
        self.start_time = time.time()
        self._counter = 1
        self.open_list = [(self._heuristic(self.start), self._counter, self.start)]
        self.g_values[self.start] = 0.0

        while self.open_list:
            frontier = [item[2] for item in self.open_list]
            yield set(self.closed_list), frontier

            if self.step():
                self.path = self._reconstruct_path(self.goal)
                yield set(self.closed_list), []
                break

    def get_metrics(self) -> MoE:
        # compile all the metrics after search
        moe = MoE()
        moe.computation_time_ms = (time.time() - self.start_time) * 1000
        moe.nodes_expanded = len(self.closed_list)
        moe.open_list_size = len(self.open_list)
        moe.peak_memory = self.max_open_size + len(self.closed_list)

        # Straight-line distance
        moe.straight_line_distance_km = self._heuristic(self.start) * Grid.CELL_SIZE_KM

        if self.path is None:
            moe.path_found = False
            moe.failure_reason = "No path found - goal unreachable"
            return moe

        moe.path_found = True

        # calc path length
        path_cost = 0.0
        for i in range(len(self.path) - 1):
            current = self.path[i]
            next_node = self.path[i + 1]
            dr = abs(next_node[0] - current[0])
            dc = abs(next_node[1] - current[1])
            if dr + dc == 1:  # Cardinal
                path_cost += 1.0
            else:  # Diagonal
                path_cost += math.sqrt(2)
        moe.path_length_km = path_cost * Grid.CELL_SIZE_KM

        # Tortuosity
        if moe.straight_line_distance_km > 0:
            moe.tortuosity_ratio = moe.path_length_km / moe.straight_line_distance_km
        else:
            # edge case: start == goal (shouldn't happen but just in case)
            moe.tortuosity_ratio = 1.0 if len(self.path) == 1 else float('inf')

        # Path smoothness
        moe.path_smoothness_deg = self._calculate_path_smoothness(self.path)

        # Branching factor = avg neighbors per node
        if moe.nodes_expanded > 0:
            moe.branching_factor = self.total_neighbor_checks / moe.nodes_expanded
        else:
            moe.branching_factor = 0.0

        return moe


class Visualiser:
    # pygame stuff - rendering, events, animation
    # all pygame colors we use
    COLOR_WHITE = (255, 255, 255)
    COLOR_BLACK = (0, 0, 0)
    COLOR_DARK_GRAY = (64, 64, 64)
    COLOR_LIGHT_GRAY = (200, 200, 200)
    COLOR_GREEN = (0, 255, 0)
    COLOR_RED = (255, 0, 0)
    COLOR_ORANGE = (255, 165, 0)
    COLOR_PALE_BLUE = (100, 149, 237)
    COLOR_PANEL_BG = (40, 40, 40)
    COLOR_TEXT = (255, 255, 255)

    def __init__(self, grid: Grid):
        pygame.init()
        self.grid = grid
        self.cell_pixel_size = 8  # 8 pixels per cell for visibility
        self.grid_width = grid.GRID_SIZE * self.cell_pixel_size
        self.grid_height = grid.GRID_SIZE * self.cell_pixel_size
        self.panel_width = 320
        self.window_width = self.grid_width + self.panel_width + 20
        self.window_height = self.grid_height + 20

        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("UGV A* Pathfinding Simulation")
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.Font(None, 14)
        self.font_normal = pygame.font.Font(None, 16)
        self.font_title = pygame.font.Font(None, 18)

        self.astar = None
        self.frontier_iterator = None
        self.closed_list = set()
        self.frontier = []
        self.path = []
        self.moe = None
        self.running = True
        self.paused = False
        self.animation_speed = 50  # steps per frame (can increase or decrease)
        self.density = "low"
        self.comparison_table = None

    def generate_new_grid(self, density: str = None):
        # fresh grid
        if density:
            self.density = density
        self.grid.regenerate(self.density)
        self.closed_list = set()
        self.frontier = []
        self.path = []
        self.moe = None
        self.frontier_iterator = None

    def start_search(self):
        # kick off the search
        self.astar = AStar(self.grid)
        self.frontier_iterator = self.astar.step_iterator()
        self.closed_list = set()
        self.frontier = []
        self.path = []

    def update_animation(self):
        # move animation forward
        if self.frontier_iterator is None or self.paused:
            return

        try:
            for _ in range(self.animation_speed):
                self.closed_list, self.frontier = next(self.frontier_iterator)
        except StopIteration:
            # search finished
            self.moe = self.astar.get_metrics()
            self.path = self.astar.path if self.astar.path else []
            self.frontier_iterator = None
            print("\n" + "=" * 50)
            print(f"SEARCH COMPLETE - Density: {self.density.upper()}")
            print(f"Grid Seed: {self.grid.seed}")
            print("=" * 50)
            print(self.moe)
            print("=" * 50 + "\n")

    def draw(self):
        # render everything
        self.screen.fill(self.COLOR_BLACK)

        # draw grid boundary
        grid_rect = pygame.Rect(10, 10, self.grid_width, self.grid_height)
        pygame.draw.rect(self.screen, self.COLOR_LIGHT_GRAY, grid_rect, 1)

        grid_offset_x = 10
        grid_offset_y = 10

        # render all cells
        for r in range(self.grid.GRID_SIZE):
            for c in range(self.grid.GRID_SIZE):
                x = grid_offset_x + c * self.cell_pixel_size
                y = grid_offset_y + r * self.cell_pixel_size
                rect = pygame.Rect(x, y, self.cell_pixel_size, self.cell_pixel_size)

                if self.grid.grid[r, c] == 1:
                    pygame.draw.rect(self.screen, self.COLOR_DARK_GRAY, rect)
                else:
                    pygame.draw.rect(self.screen, self.COLOR_WHITE, rect)

        # blue overlay on visited nodes
        for node in self.closed_list:
            r, c = node
            x = grid_offset_x + c * self.cell_pixel_size
            y = grid_offset_y + r * self.cell_pixel_size
            rect = pygame.Rect(x, y, self.cell_pixel_size, self.cell_pixel_size)
            pygame.draw.rect(self.screen, self.COLOR_PALE_BLUE, rect)

        # Draw frontier (open list) - draw as filled squares like closed nodes
        for node in self.frontier:
            r, c = node
            x = grid_offset_x + c * self.cell_pixel_size
            y = grid_offset_y + r * self.cell_pixel_size
            rect = pygame.Rect(x, y, self.cell_pixel_size, self.cell_pixel_size)
            # use a lighter shade to distinguish from closed nodes
            pygame.draw.rect(self.screen, (150, 180, 255), rect)

        # draw the final path in orange
        if self.path and len(self.path) > 1:
            for i in range(len(self.path) - 1):
                r1, c1 = self.path[i]
                r2, c2 = self.path[i + 1]
                x1 = grid_offset_x + c1 * self.cell_pixel_size + self.cell_pixel_size // 2
                y1 = grid_offset_y + r1 * self.cell_pixel_size + self.cell_pixel_size // 2
                x2 = grid_offset_x + c2 * self.cell_pixel_size + self.cell_pixel_size // 2
                y2 = grid_offset_y + r2 * self.cell_pixel_size + self.cell_pixel_size // 2
                pygame.draw.line(self.screen, self.COLOR_ORANGE, (x1, y1), (x2, y2), 2)

        # start (green) and goal (red) markers
        start_x = grid_offset_x + self.grid.START[1] * self.cell_pixel_size + self.cell_pixel_size // 2
        start_y = grid_offset_y + self.grid.START[0] * self.cell_pixel_size + self.cell_pixel_size // 2
        goal_x = grid_offset_x + self.grid.GOAL[1] * self.cell_pixel_size + self.cell_pixel_size // 2
        goal_y = grid_offset_y + self.grid.GOAL[0] * self.cell_pixel_size + self.cell_pixel_size // 2

        pygame.draw.circle(self.screen, self.COLOR_GREEN, (start_x, start_y), 4)
        pygame.draw.circle(self.screen, self.COLOR_RED, (goal_x, goal_y), 4)

        # Draw sidebar panel
        self.draw_panel(grid_offset_x + self.grid_width + 10)

        pygame.display.flip()

    def draw_panel(self, x_offset):
        # right side panel with metrics
        panel_x = x_offset
        panel_y = 10
        panel_rect = pygame.Rect(panel_x, panel_y, self.panel_width, self.window_height - 20)
        pygame.draw.rect(self.screen, self.COLOR_PANEL_BG, panel_rect)
        pygame.draw.rect(self.screen, self.COLOR_LIGHT_GRAY, panel_rect, 1)

        y = panel_y + 10
        line_height = 20
        max_y = panel_y + self.window_height - 40  # bounds check

        # Title
        if y < max_y:
            title = self.font_title.render("A* PATHFINDING", True, self.COLOR_ORANGE)
            self.screen.blit(title, (panel_x + 5, y))
        y += line_height + 5

        # Status
        if y < max_y:
            if self.frontier_iterator is not None:
                status = "Searching..." if not self.paused else "Paused"
                color = (255, 200, 0)
            elif self.moe is not None:
                status = "Complete" if self.moe.path_found else "Failed"
                color = (0, 255, 0) if self.moe.path_found else (255, 0, 0)
            else:
                status = "Ready"
                color = (100, 200, 255)

            status_text = self.font_normal.render(status, True, color)
            self.screen.blit(status_text, (panel_x + 5, y))
        y += line_height + 5

        # Grid info
        if y < max_y:
            grid_text = self.font_small.render(f"Grid: 70x70 km", True, self.COLOR_TEXT)
            self.screen.blit(grid_text, (panel_x + 5, y))
        y += line_height

        if y < max_y:
            density_text = self.font_small.render(f"Density: {self.density.upper()}", True, self.COLOR_TEXT)
            self.screen.blit(density_text, (panel_x + 5, y))
        y += line_height

        if y < max_y:
            seed_text = self.font_small.render(f"Seed: {self.grid.seed}", True, self.COLOR_TEXT)
            self.screen.blit(seed_text, (panel_x + 5, y))
        y += line_height + 10

        # MoE display
        if self.moe and y < max_y:
            y = self.draw_moe_panel(panel_x + 5, y, line_height, max_y)

        # Controls (only if space)
        y += 10
        control_lines = [
            "CONTROLS:",
            "1/2/3: Low/Med/High",
            "R: New seed",
            "SPACE: Pause/Resume",
            "+/-: Speed",
            "C: Compare all",
            "Q: Quit"
        ]
        for line in control_lines:
            if y < max_y:
                ctrl_text = self.font_small.render(line, True, self.COLOR_TEXT)
                self.screen.blit(ctrl_text, (panel_x + 5, y))
            y += line_height

    def draw_moe_panel(self, x, y, line_height, max_y) -> int:
        # display moe values in the panel with bounds check
        moe_lines = [
            f"Status: {'Found' if self.moe.path_found else 'NOT FOUND'}",
            f"Path: {self.moe.path_length_km:.2f} km",
            f"Straight: {self.moe.straight_line_distance_km:.2f} km",
            f"Tortuosity: {self.moe.tortuosity_ratio:.3f}",
            f"Expanded: {self.moe.nodes_expanded}",
            f"Open List: {self.moe.open_list_size}",
            f"Time: {self.moe.computation_time_ms:.1f} ms",
            f"Memory: {self.moe.peak_memory}",
            f"Smoothness: {self.moe.path_smoothness_deg:.1f}°",
            f"Branch Factor: {self.moe.branching_factor:.2f}",
        ]

        if not self.moe.path_found and self.moe.failure_reason:
            moe_lines = [f"Reason: {self.moe.failure_reason}"] + moe_lines

        for line in moe_lines:
            if y < max_y:
                text = self.font_small.render(line, True, self.COLOR_TEXT)
                self.screen.blit(text, (x, y))
            y += line_height

        return y

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.running = False

                elif event.key == pygame.K_1:
                    self.generate_new_grid("low")
                    self.start_search()

                elif event.key == pygame.K_2:
                    self.generate_new_grid("medium")
                    self.start_search()

                elif event.key == pygame.K_3:
                    self.generate_new_grid("high")
                    self.start_search()

                elif event.key == pygame.K_r:
                    self.generate_new_grid()
                    self.start_search()

                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused

                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    # ramp up speed
                    self.animation_speed = min(500, self.animation_speed + 50)

                elif event.key == pygame.K_MINUS:
                    # slow it down
                    self.animation_speed = max(1, self.animation_speed - 50)

                elif event.key == pygame.K_c:
                    self.run_comparison()

    def run_comparison(self):
        # run all 3 densities and compare
        original_density = self.density  # save current density
        
        print("\n" + "=" * 100)
        print("COMPARISON TABLE: A* Performance Across Density Levels".center(100))
        print("=" * 100)

        results = {}
        for density in ["low", "medium", "high"]:
            print(f"\nRunning on {density.upper()} density...")
            self.generate_new_grid(density)
            astar = AStar(self.grid)
            astar.run()
            results[density] = astar.get_metrics()

        # print comparison table
        header = f"{'Metric':<30} {'LOW':<25} {'MEDIUM':<25} {'HIGH':<25}"
        print("\n" + header)
        print("-" * 105)

        metrics = [
            ("Path Found", lambda m: "YES" if m.path_found else "NO"),
            ("Path Length (km)", lambda m: f"{m.path_length_km:.2f}" if m.path_found else "N/A"),
            ("Straight-line (km)", lambda m: f"{m.straight_line_distance_km:.2f}" if m.path_found else "N/A"),
            ("Tortuosity Ratio", lambda m: f"{m.tortuosity_ratio:.3f}" if m.path_found else "N/A"),
            ("Nodes Expanded", lambda m: f"{m.nodes_expanded}"),
            ("Open List Size", lambda m: f"{m.open_list_size}"),
            ("Computation Time (ms)", lambda m: f"{m.computation_time_ms:.2f}"),
            ("Peak Memory", lambda m: f"{m.peak_memory}"),
            ("Path Smoothness (°)", lambda m: f"{m.path_smoothness_deg:.2f}" if m.path_found else "N/A"),
            ("Branching Factor", lambda m: f"{m.branching_factor:.2f}"),
        ]

        for metric_name, metric_fn in metrics:
            # format and print each metric row
            low_val = metric_fn(results["low"])
            med_val = metric_fn(results["medium"])
            high_val = metric_fn(results["high"])
            row = f"{metric_name:<30} {low_val:<25} {med_val:<25} {high_val:<25}"
            print(row)

        print("=" * 105 + "\n")
        
        # restore original density and restart search
        self.generate_new_grid(original_density)
        self.start_search()

    def run(self):
        # main loop - 60 fps
        self.generate_new_grid()
        self.start_search()

        while self.running:
            self.handle_events()
            self.update_animation()
            self.draw()
            self.clock.tick(60)

        pygame.quit()


def main():
    # setup and run
    print("=" * 70)
    print("UGV A* PATHFINDING SIMULATION".center(70))
    print("=" * 70)
    print("\nInitializing 70x70 km grid with A* search algorithm...")
    print("pygame version:", pygame.__version__)
    print("\nPress any key (1/2/3) to start, or Q to quit\n")

    grid = Grid(density="low")
    visualiser = Visualiser(grid)
    visualiser.run()


if __name__ == "__main__":
    main()
