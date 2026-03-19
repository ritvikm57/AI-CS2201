"""
UGV Navigation with Dynamic Obstacles — Repeated A*

Part 2 of the pathfinding assignment.
- UGV starts with no knowledge of obstacles
- Grid appears fully free initially
- As UGV moves, it discovers obstacles within sensor radius (5 cells)
- When new obstacle blocks current path, replan using A*
- Track replanning events and time separately

Repeated A* is simpler than D* Lite but still efficient enough for this 70×70 grid.
Each replan only runs A* from current position to goal, not from scratch.
"""

import heapq
import math
import time
import random
import os
import numpy as np
import pygame
from dataclasses import dataclass
from typing import List, Tuple, Optional

GRID_SIZE = 70
CELL_KM = 1.0
START = (0, 0)
GOAL = (69, 69)
SENSOR_RADIUS = 5
DENSITIES = {"low": 0.15, "medium": 0.35, "high": 0.55}

# Movement costs
MOVEMENTS = [
    (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
    (-1, -1, math.sqrt(2)), (-1, 1, math.sqrt(2)),
    (1, -1, math.sqrt(2)), (1, 1, math.sqrt(2)),
]

# Colors
C_WHITE = (255, 255, 255)
C_BLACK = (0, 0, 0)
C_DARK_GRAY = (64, 64, 64)
C_LIGHT_GRAY = (200, 200, 200)
C_GREEN = (0, 220, 0)
C_RED = (220, 0, 0)
C_ORANGE = (255, 165, 0)
C_PALE_BLUE = (100, 149, 237)
C_UGV = (255, 255, 0)
C_PANEL_BG = (30, 30, 40)
C_TEXT = (220, 220, 220)
C_ACCENT = (74, 222, 159)
C_TRAIL = (255, 200, 100)


@dataclass
class MoE:
    path_length_km: float = 0.0
    straight_line_km: float = 0.0
    tortuosity_ratio: float = 0.0
    nodes_expanded: int = 0
    replan_count: int = 0
    replan_time_ms: float = 0.0
    total_time_ms: float = 0.0
    peak_memory: int = 0
    path_smoothness_deg: float = 0.0
    branching_factor: float = 0.0
    obstacles_discovered: int = 0
    path_found: bool = False
    failure_reason: str = ""

    def __str__(self):
        lines = [f"{'Path Found':<28} {'YES' if self.path_found else 'NO'}"]
        if not self.path_found:
            lines.append(f"{'Failure Reason':<28} {self.failure_reason}")
        lines += [
            f"{'Path Length (km)':<28} {self.path_length_km:.2f}",
            f"{'Straight-line (km)':<28} {self.straight_line_km:.2f}",
            f"{'Tortuosity Ratio':<28} {self.tortuosity_ratio:.3f}",
            f"{'Nodes Expanded':<28} {self.nodes_expanded}",
            f"{'Replan Count':<28} {self.replan_count}",
            f"{'Replan Time (ms)':<28} {self.replan_time_ms:.2f}",
            f"{'Total Time (ms)':<28} {self.total_time_ms:.2f}",
            f"{'Peak Memory (nodes)':<28} {self.peak_memory}",
            f"{'Path Smoothness (deg)':<28} {self.path_smoothness_deg:.2f}",
            f"{'Branching Factor':<28} {self.branching_factor:.2f}",
            f"{'Obstacles Discovered':<28} {self.obstacles_discovered}",
        ]
        return "\n".join(lines)

    def comparison_row(self, density):
        na = "N/A"
        return {
            "density": density,
            "path_found": "YES" if self.path_found else "NO",
            "path_length_km": f"{self.path_length_km:.2f}" if self.path_found else na,
            "straight_line_km": f"{self.straight_line_km:.2f}" if self.path_found else na,
            "tortuosity": f"{self.tortuosity_ratio:.3f}" if self.path_found else na,
            "nodes_expanded": str(self.nodes_expanded),
            "replan_count": str(self.replan_count),
            "replan_time_ms": f"{self.replan_time_ms:.2f}",
            "total_time_ms": f"{self.total_time_ms:.2f}",
            "peak_memory": str(self.peak_memory),
            "smoothness": f"{self.path_smoothness_deg:.2f}" if self.path_found else na,
            "branching_factor": f"{self.branching_factor:.2f}",
            "obstacles_discovered": str(self.obstacles_discovered),
        }

    @staticmethod
    def print_comparison(rows):
        fields = [
            ("Path Found", "path_found"),
            ("Path Length (km)", "path_length_km"),
            ("Straight-line (km)", "straight_line_km"),
            ("Tortuosity Ratio", "tortuosity"),
            ("Nodes Expanded", "nodes_expanded"),
            ("Replan Count", "replan_count"),
            ("Replan Time (ms)", "replan_time_ms"),
            ("Total Time (ms)", "total_time_ms"),
            ("Peak Memory", "peak_memory"),
            ("Path Smoothness (°)", "smoothness"),
            ("Branching Factor", "branching_factor"),
            ("Obstacles Discovered", "obstacles_discovered"),
        ]
        print("\n" + "=" * 110)
        print("Repeated A* — Dynamic Obstacles — Comparison Across Density Levels".center(110))
        print("=" * 110)
        print(f"{'Metric':<30} {'LOW':<25} {'MEDIUM':<25} {'HIGH':<25}")
        print("-" * 110)
        for label, key in fields:
            vals = [r[key] for r in rows]
            print(f"{label:<30} {vals[0]:<25} {vals[1]:<25} {vals[2]:<25}")
        print("=" * 110 + "\n")


class Grid:
    def __init__(self, density="low", seed=None):
        self.density = density
        self.seed = seed if seed is not None else int.from_bytes(os.urandom(4), 'big') % 1000000
        self.true_grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
        self.known_grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
        self._generate()

    def _generate(self):
        random.seed(self.seed)
        np.random.seed(self.seed)

        n_obs = int(GRID_SIZE * GRID_SIZE * DENSITIES[self.density])
        available = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)
                     if (r, c) != START and (r, c) != GOAL]
        for r, c in random.sample(available, n_obs):
            self.true_grid[r, c] = 1

        if self.density == "high":
            self._carve_corridor()

        # Initially sense from start
        self._sense(START)

    def _carve_corridor(self):
        r, c = START
        while (r, c) != GOAL:
            self.true_grid[r, c] = 0
            if r < GOAL[0]:
                r += 1
            elif c < GOAL[1]:
                c += 1
            else:
                break
        self.true_grid[GOAL[0]][GOAL[1]] = 0

    def _sense(self, pos):
        r0, c0 = pos
        newly_found = []
        for dr in range(-SENSOR_RADIUS, SENSOR_RADIUS + 1):
            for dc in range(-SENSOR_RADIUS, SENSOR_RADIUS + 1):
                r, c = r0 + dr, c0 + dc
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                    if self.true_grid[r, c] == 1 and self.known_grid[r, c] == 0:
                        self.known_grid[r, c] = 1
                        newly_found.append((r, c))
        return newly_found

    def is_free(self, r, c):
        return 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and self.known_grid[r, c] == 0

    def regenerate(self, density=None):
        if density:
            self.density = density
        self.seed = int.from_bytes(os.urandom(4), 'big') % 1000000
        self.true_grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
        self.known_grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
        self._generate()


class AStar:
    def __init__(self, grid, start, goal):
        self.grid = grid
        self.start = start
        self.goal = goal
        self.open_list = []
        self.closed_list = set()
        self.parent_map = {}
        self.g_values = {start: 0.0}
        self._counter = 0
        self.nodes_expanded = 0
        self.total_neighbor_checks = 0
        self.peak_memory = 0

    def _heuristic(self, pos):
        return math.sqrt((pos[0] - self.goal[0])**2 + (pos[1] - self.goal[1])**2)

    def _reconstruct_path(self, node):
        path = [node]
        while node in self.parent_map:
            node = self.parent_map[node]
            path.append(node)
        return path[::-1]

    def run(self):
        self._counter = 1
        self.open_list = [(self._heuristic(self.start), self._counter, self.start)]

        while self.open_list:
            _, _, current = heapq.heappop(self.open_list)

            self.closed_list.add(current)
            self.nodes_expanded += 1

            if current == self.goal:
                return self._reconstruct_path(self.goal)

            r, c = current
            for dr, dc, cost in MOVEMENTS:
                neighbor = (r + dr, c + dc)
                self.total_neighbor_checks += 1

                if not self.grid.is_free(neighbor[0], neighbor[1]):
                    continue

                if neighbor in self.closed_list:
                    continue

                tentative_g = self.g_values[current] + cost

                if neighbor not in self.g_values or tentative_g < self.g_values[neighbor]:
                    self.parent_map[neighbor] = current
                    self.g_values[neighbor] = tentative_g
                    h = self._heuristic(neighbor)
                    f = tentative_g + h
                    self._counter += 1
                    heapq.heappush(self.open_list, (f, self._counter, neighbor))

            mem = len(self.open_list) + len(self.closed_list)
            if mem > self.peak_memory:
                self.peak_memory = mem

        return None


class Navigator:
    def __init__(self, grid):
        self.grid = grid
        self.pos = START
        self.trail = [START]
        self.path = []
        self.done = False
        self.failed = False

        self.nodes_expanded = 0
        self.total_neighbor_checks = 0
        self.replan_count = 0
        self.replan_time_ms = 0.0
        self.peak_memory = 0
        self.obstacles_discovered = 0
        self.start_time = None

        self._initial_plan()

    def _initial_plan(self):
        astar = AStar(self.grid, self.pos, GOAL)
        self.path = astar.run()
        self.nodes_expanded = astar.nodes_expanded
        self.total_neighbor_checks = astar.total_neighbor_checks
        self.peak_memory = astar.peak_memory

    def step(self):
        if self.done or self.failed:
            return self.done

        # sense and maybe discover new obstacles
        newly_found = self.grid._sense(self.pos)
        self.obstacles_discovered += len(newly_found)

        # check if current path is still valid
        if self.path and len(self.path) > 1:
            next_pos = self.path[1]
            if not self.grid.is_free(next_pos[0], next_pos[1]):
                # replan
                self._replan()

        # if no path, try to get one
        if not self.path or len(self.path) < 2:
            self.path = []
            astar = AStar(self.grid, self.pos, GOAL)
            self.path = astar.run()
            if not self.path or len(self.path) < 2:
                self.failed = True
                return False
            self.replan_count += 1

        # move
        next_pos = self.path[1]
        self.pos = next_pos
        self.path = self.path[1:]
        self.trail.append(self.pos)

        if self.pos == GOAL:
            self.done = True

        return self.done

    def _replan(self):
        t0 = time.time()
        astar = AStar(self.grid, self.pos, GOAL)
        new_path = astar.run()
        self.replan_time_ms += (time.time() - t0) * 1000

        if new_path and len(new_path) > 1:
            self.path = new_path
            self.replan_count += 1
            self.nodes_expanded += astar.nodes_expanded
            self.total_neighbor_checks += astar.total_neighbor_checks
            self.peak_memory = max(self.peak_memory, astar.peak_memory)
        else:
            self.failed = True

    def get_moe(self):
        moe = MoE()
        moe.path_found = self.done
        moe.nodes_expanded = self.nodes_expanded
        moe.replan_count = self.replan_count
        moe.replan_time_ms = self.replan_time_ms
        moe.total_time_ms = (time.time() - self.start_time) * 1000 if self.start_time else 0.0
        moe.peak_memory = self.peak_memory
        moe.obstacles_discovered = self.obstacles_discovered
        moe.branching_factor = (self.total_neighbor_checks / self.nodes_expanded
                                if self.nodes_expanded > 0 else 0.0)
        moe.straight_line_km = math.sqrt((START[0] - GOAL[0])**2 + (START[1] - GOAL[1])**2) * CELL_KM

        if not self.done:
            moe.failure_reason = "Goal unreachable given discovered obstacles"
            return moe

        # trail cost
        trail_cost = 0.0
        for i in range(len(self.trail) - 1):
            dr = abs(self.trail[i+1][0] - self.trail[i][0])
            dc = abs(self.trail[i+1][1] - self.trail[i][1])
            if dr + dc == 2:  # diagonal
                trail_cost += math.sqrt(2)
            else:  # cardinal
                trail_cost += 1.0

        moe.path_length_km = trail_cost * CELL_KM
        moe.tortuosity_ratio = moe.path_length_km / moe.straight_line_km if moe.straight_line_km > 0 else 1.0

        # smoothness
        if len(self.trail) >= 3:
            angles = []
            for i in range(1, len(self.trail) - 1):
                p1, p2, p3 = self.trail[i-1], self.trail[i], self.trail[i+1]
                v1 = (p1[0] - p2[0], p1[1] - p2[1])
                v2 = (p3[0] - p2[0], p3[1] - p2[1])
                turn = abs(math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0]))
                if turn > math.pi:
                    turn = 2 * math.pi - turn
                angles.append(math.degrees(turn))
            moe.path_smoothness_deg = sum(angles) / len(angles) if angles else 0.0

        return moe


class Visualiser:
    CELL_PX = 9
    PANEL_W = 330

    def __init__(self, grid):
        pygame.init()
        self.grid = grid
        self.nav = None

        gw = GRID_SIZE * self.CELL_PX
        gh = GRID_SIZE * self.CELL_PX
        self.grid_w = gw
        self.grid_h = gh
        self.win_w = gw + self.PANEL_W + 20
        self.win_h = gh + 20

        self.screen = pygame.display.set_mode((self.win_w, self.win_h))
        pygame.display.set_caption("UGV Repeated A* — Dynamic Obstacle Navigation")
        self.clock = pygame.time.Clock()

        self.font_sm = pygame.font.Font(None, 14)
        self.font_md = pygame.font.Font(None, 16)
        self.font_lg = pygame.font.Font(None, 20)

        self.running = True
        self.paused = False
        self.steps_per_frame = 1
        self.density = "low"
        self.moe: Optional[MoE] = None
        self.replan_flash = 0

    def new_simulation(self, density=None):
        if density:
            self.density = density
        self.grid.regenerate(self.density)
        self.nav = Navigator(self.grid)
        self.nav.start_time = time.time()
        self.moe = None
        self.paused = False
        self.replan_flash = 0

    def run(self):
        self.new_simulation()
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(60)
        pygame.quit()

    def _handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False
            elif ev.type == pygame.KEYDOWN:
                k = ev.key
                if k in (pygame.K_q, pygame.K_ESCAPE):
                    self.running = False
                elif k == pygame.K_1:
                    self.new_simulation("low")
                elif k == pygame.K_2:
                    self.new_simulation("medium")
                elif k == pygame.K_3:
                    self.new_simulation("high")
                elif k == pygame.K_r:
                    self.new_simulation()
                elif k == pygame.K_SPACE:
                    self.paused = not self.paused
                elif k in (pygame.K_PLUS, pygame.K_EQUALS):
                    self.steps_per_frame = min(20, self.steps_per_frame + 1)
                elif k == pygame.K_MINUS:
                    self.steps_per_frame = max(1, self.steps_per_frame - 1)
                elif k == pygame.K_s:
                    self._instant_solve()
                elif k == pygame.K_c:
                    self._run_comparison()

    def _update(self):
        if self.paused or self.nav is None:
            return
        if self.nav.done or self.nav.failed:
            if self.moe is None:
                self.moe = self.nav.get_moe()
                self._print_moe()
            return

        for _ in range(self.steps_per_frame):
            prev_replan = self.nav.replan_count
            done = self.nav.step()
            if self.nav.replan_count > prev_replan:
                self.replan_flash = 20
            if done or self.nav.failed:
                self.moe = self.nav.get_moe()
                self._print_moe()
                break

        if self.replan_flash > 0:
            self.replan_flash -= 1

    def _instant_solve(self):
        if self.nav is None:
            return
        while not self.nav.done and not self.nav.failed:
            self.nav.step()
        self.moe = self.nav.get_moe()
        self._print_moe()

    def _draw(self):
        self.screen.fill(C_BLACK)
        ox, oy = 10, 10

        # draw grid
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x = ox + c * self.CELL_PX
                y = oy + r * self.CELL_PX
                rect = pygame.Rect(x, y, self.CELL_PX, self.CELL_PX)
                if self.grid.known_grid[r, c] == 1:
                    pygame.draw.rect(self.screen, C_DARK_GRAY, rect)
                else:
                    pygame.draw.rect(self.screen, C_WHITE, rect)

        # sensor radius circle
        if self.nav:
            pr, pc = self.nav.pos
            sr = SENSOR_RADIUS * self.CELL_PX
            cx = ox + pc * self.CELL_PX + self.CELL_PX // 2
            cy = oy + pr * self.CELL_PX + self.CELL_PX // 2
            pygame.draw.circle(self.screen, (80, 80, 100), (cx, cy), sr, 1)

            # trail
            if len(self.nav.trail) > 1:
                for i in range(len(self.nav.trail) - 1):
                    r1, c1 = self.nav.trail[i]
                    r2, c2 = self.nav.trail[i + 1]
                    p1 = (ox + c1 * self.CELL_PX + self.CELL_PX // 2,
                          oy + r1 * self.CELL_PX + self.CELL_PX // 2)
                    p2 = (ox + c2 * self.CELL_PX + self.CELL_PX // 2,
                          oy + r2 * self.CELL_PX + self.CELL_PX // 2)
                    pygame.draw.line(self.screen, C_TRAIL, p1, p2, 2)

            # planned path ahead
            if self.nav.path and len(self.nav.path) > 1:
                for i in range(len(self.nav.path) - 1):
                    r1, c1 = self.nav.path[i]
                    r2, c2 = self.nav.path[i + 1]
                    p1 = (ox + c1 * self.CELL_PX + self.CELL_PX // 2,
                          oy + r1 * self.CELL_PX + self.CELL_PX // 2)
                    p2 = (ox + c2 * self.CELL_PX + self.CELL_PX // 2,
                          oy + r2 * self.CELL_PX + self.CELL_PX // 2)
                    pygame.draw.line(self.screen, C_ORANGE, p1, p2, 2)

            # UGV position
            pygame.draw.circle(self.screen, C_UGV,
                             (ox + pc * self.CELL_PX + self.CELL_PX // 2,
                              oy + pr * self.CELL_PX + self.CELL_PX // 2), 5)

        # start and goal
        pygame.draw.circle(self.screen, C_GREEN,
                         (ox + START[1] * self.CELL_PX + self.CELL_PX // 2,
                          oy + START[0] * self.CELL_PX + self.CELL_PX // 2), 5)
        pygame.draw.circle(self.screen, C_RED,
                         (ox + GOAL[1] * self.CELL_PX + self.CELL_PX // 2,
                          oy + GOAL[0] * self.CELL_PX + self.CELL_PX // 2), 5)

        self._draw_panel(ox + self.grid_w + 10)
        pygame.display.flip()

    def _draw_panel(self, px):
        py = 10
        pw = self.PANEL_W
        ph = self.win_h - 20
        max_y = py + ph - 10
        lh = 18

        pygame.draw.rect(self.screen, C_PANEL_BG, (px, py, pw, ph))
        pygame.draw.rect(self.screen, C_LIGHT_GRAY, (px, py, pw, ph), 1)

        y = py + 10

        def txt(s, colour=C_TEXT, font=None):
            nonlocal y
            if y >= max_y:
                return
            self.screen.blit((font or self.font_sm).render(s, True, colour), (px + 8, y))
            y += lh

        def hr():
            nonlocal y
            if y >= max_y:
                return
            pygame.draw.line(self.screen, (60, 60, 80), (px + 4, y), (px + pw - 4, y))
            y += 6

        txt("REPEATED A* — UGV NAVIGATION", C_ACCENT, self.font_lg)
        txt("Dynamic Obstacle Environment", C_LIGHT_GRAY)
        hr()

        if self.nav:
            if self.nav.done:
                status, sc = "GOAL REACHED", C_GREEN
            elif self.nav.failed:
                status, sc = "FAILED — NO PATH", C_RED
            elif self.paused:
                status, sc = "PAUSED", (255, 200, 0)
            else:
                status, sc = "NAVIGATING...", (100, 200, 255)
            txt(status, sc, self.font_md)
            if self.replan_flash > 0:
                txt("!! REPLANNING !!", (255, 80, 80), self.font_md)

        hr()
        txt(f"Grid:    {GRID_SIZE}x{GRID_SIZE} km")
        txt(f"Density: {self.density.upper()}")
        txt(f"Sensor:  radius {SENSOR_RADIUS} cells")
        txt(f"Seed:    {self.grid.seed}")
        hr()

        if self.nav:
            n = self.nav
            txt("LIVE METRICS", C_ACCENT)
            txt(f"UGV pos:     ({n.pos[0]}, {n.pos[1]})")
            txt(f"Steps taken: {len(n.trail) - 1}")
            txt(f"Replans:     {n.replan_count}")
            txt(f"Obs found:   {n.obstacles_discovered}")
            txt(f"Nodes exp:   {n.nodes_expanded}")
            txt(f"Speed:       {self.steps_per_frame} step/frame")
            hr()

        if self.moe:
            txt("FINAL MoE", C_ACCENT)
            for line in [
                f"Path:       {self.moe.path_length_km:.2f} km",
                f"Straight:   {self.moe.straight_line_km:.2f} km",
                f"Tortuosity: {self.moe.tortuosity_ratio:.3f}",
                f"Replans:    {self.moe.replan_count}",
                f"Replan ms:  {self.moe.replan_time_ms:.1f}",
                f"Total ms:   {self.moe.total_time_ms:.1f}",
                f"Peak mem:   {self.moe.peak_memory}",
                f"Smoothness: {self.moe.path_smoothness_deg:.1f}°",
                f"Branch fac: {self.moe.branching_factor:.2f}",
                f"Obs disc:   {self.moe.obstacles_discovered}",
            ]:
                txt(line)
            hr()

        txt("CONTROLS", C_ACCENT)
        for line in ["1/2/3: density", "R: new map", "SPACE: pause",
                     "+/-: speed", "S: instant", "C: compare", "Q: quit"]:
            txt(line, C_LIGHT_GRAY)

        hr()
        txt("LEGEND", C_ACCENT)
        for colour, label in [
            (C_GREEN, "Start"),
            (C_RED, "Goal"),
            (C_UGV, "UGV"),
            (C_TRAIL, "Trail"),
            (C_ORANGE, "Planned path"),
            (C_DARK_GRAY, "Known obstacle"),
            (C_WHITE, "Free / unknown"),
        ]:
            if y >= max_y:
                break
            pygame.draw.circle(self.screen, colour, (px + 12, y + 6), 4)
            self.screen.blit(self.font_sm.render(label, True, C_TEXT), (px + 22, y))
            y += lh

    def _print_moe(self):
        status = "GOAL REACHED" if self.moe.path_found else "NAVIGATION FAILED"
        print(f"\n{'='*60}")
        print(f"{status} — Density: {self.density.upper()}  Seed: {self.grid.seed}")
        print("=" * 60)
        print(self.moe)
        print("=" * 60 + "\n")

    def _run_comparison(self):
        original = self.density
        rows = []
        for d in ["low", "medium", "high"]:
            print(f"Running {d.upper()}...")
            self.grid.regenerate(d)
            nav = Navigator(self.grid)
            nav.start_time = time.time()
            while not nav.done and not nav.failed:
                nav.step()
            rows.append(nav.get_moe().comparison_row(d))
        MoE.print_comparison(rows)
        self.new_simulation(original)


def main():
    print("=" * 70)
    print("UGV Repeated A* — Dynamic Obstacle Navigation (Part 2)".center(70))
    print("=" * 70)
    print(f"Grid: {GRID_SIZE}x{GRID_SIZE} km  |  Sensor radius: {SENSOR_RADIUS} cells")
    print("Obstacles unknown a-priori — discovered as UGV navigates\n")

    grid = Grid(density="low")
    Visualiser(grid).run()


if __name__ == "__main__":
    main()
