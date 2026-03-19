"""
dijkstra_india.py — Dijkstra's Algorithm on India's Road Network
=================================================================
Loads road edges from india_edges.json (same folder).
City coordinates are fetched automatically from OpenStreetMap's
Nominatim API on first run, then cached in city_coords.json.

Requirements:
    pip install pygame requests

Controls:
    Left-click  a city  → set as SOURCE
    Right-click a city  → set as DESTINATION
    SPACE               → run Dijkstra (instant result)
    S                   → step-by-step mode (press again to advance)
    A                   → auto-play steps
    R                   → reset view
    Scroll / +/-        → zoom
    Click + drag        → pan
    ESC / Q             → quit
"""

import heapq
import json
import sys
import time
from pathlib import Path

import pygame
import requests


BG        = (10,  12,  16)
PANEL_BG  = (14,  17,  24)
BORDER    = (37,  42,  53)
EDGE_DEF  = (30,  35,  48)
EDGE_VIS  = (60,  45, 100)
EDGE_PATH = (245, 158,  11)
NODE_DEF  = (42,  48,  64)
NODE_VIS  = (167, 139, 250)   # settled
NODE_FRO  = (245, 158,  11)   # frontier
NODE_SRC  = (239,  68,  68)   # source
NODE_DST  = ( 74, 222, 159)   # destination
NODE_PATH = (245, 158,  11)   # on shortest path
TEXT      = (200, 205, 216)
TEXT2     = (122, 129, 150)
TEXT3     = ( 61,  68,  85)
ACCENT    = ( 74, 222, 159)


def load_edges(path: Path) -> list[tuple[str, str, int]]:
    """Load edges from india_edges.json."""
    with open(path) as f:
        data = json.load(f)
    return [(e["from"], e["to"], e["km"]) for e in data]


def geocode_cities(cities: list[str], cache_path: Path) -> dict[str, tuple[float, float]]:
    """Get coordinates for cities, reading from cache or fetching from Nominatim API."""
    coords: dict[str, tuple[float, float]] = {}

    # Load existing cache
    if cache_path.exists():
        with open(cache_path) as f:
            coords = json.load(f)

    missing = [c for c in cities if c not in coords]

    if missing:
        print(f"Geocoding {len(missing)} cities via Nominatim (this runs once)...")
        headers = {"User-Agent": "dijkstra-india-visualizer/1.0"}

        for i, city in enumerate(missing):
            url = "https://nominatim.openstreetmap.org/search"
            params = {"q": f"{city}, India", "format": "json", "limit": 1}
            try:
                r = requests.get(url, params=params, headers=headers, timeout=10)
                r.raise_for_status()
                results = r.json()
                if results:
                    coords[city] = (float(results[0]["lat"]), float(results[0]["lon"]))
                    print(f"  [{i+1}/{len(missing)}] {city}: {coords[city]}")
                else:
                    print(f"  [{i+1}/{len(missing)}] {city}: NOT FOUND — skipping")
            except Exception as e:
                print(f"  [{i+1}/{len(missing)}] {city}: ERROR ({e}) — skipping")
            time.sleep(1.1)   # Nominatim rate limit

        # Save updated cache
        with open(cache_path, "w") as f:
            json.dump(coords, f, indent=2)
        print(f"Coords cached to {cache_path}")

    return coords


def normalise_coords(
    coords: dict[str, tuple[float, float]]
) -> dict[str, tuple[float, float]]:
    """Convert (lat, lon) to normalized (x, y) in [0, 1] for canvas rendering."""
    lats = [v[0] for v in coords.values()]
    lons = [v[1] for v in coords.values()]
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)

    normed = {}
    for city, (lat, lon) in coords.items():
        x = (lon - lon_min) / (lon_max - lon_min)
        y = 1.0 - (lat - lat_min) / (lat_max - lat_min)  # flip y so north is up
        normed[city] = (x, y)
    return normed


def build_adj(edges: list[tuple[str, str, int]]) -> dict[str, list[tuple[str, int]]]:
    adj: dict[str, list[tuple[str, int]]] = {}
    for a, b, km in edges:
        adj.setdefault(a, []).append((b, km))
        adj.setdefault(b, []).append((a, km))
    return adj


def dijkstra_steps(src: str, dst: str, adj: dict) -> tuple[list[dict], list[str], float]:
    """Run Dijkstra and record a snapshot at every settle event."""
    dist   = {c: float("inf") for c in adj}
    prev:  dict[str, str] = {}
    visited: set[str] = set()
    dist[src] = 0
    pq = [(0, src)]
    frontier: set[str] = {src}
    steps: list[dict] = []

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        frontier.discard(u)

        steps.append({
            "visited":  frozenset(visited),
            "frontier": frozenset(frontier),
            "dist":     dict(dist),
            "current":  u,
        })

        if u == dst:
            break

        for nb, km in adj[u]:
            if nb not in visited:
                nd = d + km
                if nd < dist[nb]:
                    dist[nb] = nd
                    prev[nb] = u
                    frontier.add(nb)
                    heapq.heappush(pq, (nd, nb))

    # Reconstruct path
    path: list[str] = []
    cur: str | None = dst
    while cur:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    if not path or path[0] != src:
        path = []

    return steps, path, dist[dst]


# ── App ────────────────────────────────────────────────────────────────────────

class App:
    W, H      = 1400, 860
    PANEL     = 300
    MAP_PAD   = (40, 40, 40, 40)   # top, right, bottom, left

    def __init__(self, edges, norm_coords, raw_edges):
        self.edges       = edges          # list of (a, b, km)
        self.coords      = norm_coords    # {city: (nx, ny)}
        self.raw_edges   = raw_edges      # same list, for km lookup
        self.adj         = build_adj(edges)
        self.cities      = sorted(self.coords.keys())

        pygame.init()
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption("Dijkstra — India Road Network")
        self.clock  = pygame.time.Clock()

        self.font_sm  = pygame.font.SysFont("monospace", 11)
        self.font_md  = pygame.font.SysFont("monospace", 13)
        self.font_lg  = pygame.font.SysFont("monospace", 20, bold=True)
        self.font_xl  = pygame.font.SysFont("monospace", 32, bold=True)
        self.font_lbl = pygame.font.SysFont("monospace", 10)

        # Pan / zoom
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.zoom     = 1.0
        self.dragging = False
        self.drag_start = (0, 0)

        # Selection & algorithm state
        self.src: str | None = "Delhi"
        self.dst: str | None = "Chennai"
        self.steps:      list[dict] = []
        self.step_idx:   int  = -1     # -1 = show full result
        self.path:       list[str] = []
        self.total_dist: float = float("inf")
        self.auto_play   = False
        self.auto_timer  = 0.0
        self.AUTO_DELAY  = 0.08

        self._run()


    def _map_rect(self):
        W, H = self.screen.get_size()
        pt, pr, pb, pl = self.MAP_PAD
        return (self.PANEL + pl, pt, W - self.PANEL - pl - pr, H - pt - pb)

    def _city_xy(self, city: str) -> tuple[int, int]:
        nx, ny = self.coords[city]
        mx, my, mw, mh = self._map_rect()
        x = mx + (nx + self.offset_x) * mw * self.zoom
        y = my + (ny + self.offset_y) * mh * self.zoom
        return int(x), int(y)

    def _city_at(self, mx: int, my: int, radius: int = 12) -> str | None:
        for city in self.cities:
            cx, cy = self._city_xy(city)
            if (mx - cx) ** 2 + (my - cy) ** 2 <= radius ** 2:
                return city
        return None

    def _edge_km(self, a: str, b: str) -> int | None:
        for ea, eb, km in self.raw_edges:
            if (ea == a and eb == b) or (ea == b and eb == a):
                return km
        return None


    def _run(self):
        if not self.src or not self.dst or self.src == self.dst:
            return
        if self.src not in self.adj or self.dst not in self.adj:
            return
        self.steps, self.path, self.total_dist = dijkstra_steps(self.src, self.dst, self.adj)
        self.step_idx  = -1
        self.auto_play = False

    def _current_state(self) -> dict | None:
        if self.step_idx >= 0 and self.step_idx < len(self.steps):
            return self.steps[self.step_idx]
        return self.steps[-1] if self.steps else None


    def draw(self):
        W, H = self.screen.get_size()
        self.screen.fill(BG)
        state     = self._current_state()
        show_path = self.step_idx < 0 or self.step_idx == len(self.steps) - 1
        self._draw_edges(state, show_path)
        self._draw_nodes(state, show_path)
        self._draw_panel(W, H, state, show_path)
        self._draw_hints(W, H)
        pygame.display.flip()

    def _draw_edges(self, state, show_path: bool):
        visited  = state["visited"] if state else set()
        path_set = (set(zip(self.path, self.path[1:])) if show_path and self.path else set())

        for a, b, km in self.edges:
            if a not in self.coords or b not in self.coords:
                continue
            x1, y1 = self._city_xy(a)
            x2, y2 = self._city_xy(b)
            on_path   = (a, b) in path_set or (b, a) in path_set
            both_vis  = a in visited and b in visited

            if on_path:
                pygame.draw.line(self.screen, EDGE_PATH, (x1, y1), (x2, y2), 3)
                mx, my = (x1 + x2) // 2, (y1 + y2) // 2
                lbl = self.font_lbl.render(str(km), True, (200, 140, 30))
                self.screen.blit(lbl, (mx - lbl.get_width() // 2, my - 8))
            elif both_vis:
                pygame.draw.line(self.screen, EDGE_VIS, (x1, y1), (x2, y2), 1)
            else:
                pygame.draw.line(self.screen, EDGE_DEF, (x1, y1), (x2, y2), 1)

    def _draw_nodes(self, state, show_path: bool):
        visited  = state["visited"]  if state else set()
        frontier = state["frontier"] if state else set()
        current  = state["current"]  if state else None
        dist_map = state["dist"]     if state else {}
        path_set = set(self.path) if show_path else set()

        for city in self.cities:
            if city not in self.coords:
                continue
            cx, cy = self._city_xy(city)

            if city == self.src:              col, r = NODE_SRC,  8
            elif city == self.dst:            col, r = NODE_DST,  8
            elif city == current:             col, r = NODE_FRO,  7
            elif city in path_set:            col, r = NODE_PATH, 6
            elif city in visited:             col, r = NODE_VIS,  5
            elif city in frontier:            col, r = NODE_FRO,  5
            else:                             col, r = NODE_DEF,  4

            pygame.draw.circle(self.screen, col, (cx, cy), r)
            border = tuple(min(255, c + 60) for c in col)
            pygame.draw.circle(self.screen, border, (cx, cy), r, 1)

            important = city in {self.src, self.dst, current} or city in path_set or city in frontier
            if important or self.zoom > 1.4:
                lbl_col = (NODE_SRC  if city == self.src  else
                           NODE_DST  if city == self.dst  else
                           EDGE_PATH if city in path_set  else TEXT2)
                surf = self.font_lbl.render(city, True, lbl_col)
                self.screen.blit(surf, (cx - surf.get_width() // 2, cy + r + 2))

            # Tentative distance during stepping
            if state and dist_map.get(city, float("inf")) < float("inf") and city != self.src:
                d_surf = self.font_lbl.render(str(dist_map[city]), True, (100, 90, 160))
                self.screen.blit(d_surf, (cx - d_surf.get_width() // 2, cy - r - 12))

    def _draw_panel(self, W, H, state, show_path: bool):
        pygame.draw.rect(self.screen, PANEL_BG, (0, 0, self.PANEL, H))
        pygame.draw.line(self.screen, BORDER, (self.PANEL, 0), (self.PANEL, H), 1)

        x, y = 16, 16
        n_cities = len(self.cities)
        n_edges  = len(self.edges)
        self.screen.blit(self.font_lg.render("DIJKSTRA.india", True, ACCENT), (x, y)); y += 32
        self.screen.blit(self.font_sm.render(f"{n_cities} cities  {n_edges} edges", True, TEXT3), (x, y)); y += 24
        self._hr(x, y); y += 14

        self._label(x, y, "SOURCE  (left-click)"); y += 16
        self.screen.blit(self.font_md.render(self.src or "—", True, NODE_SRC if self.src else TEXT3), (x, y)); y += 22
        self._label(x, y, "DESTINATION  (right-click)"); y += 16
        self.screen.blit(self.font_md.render(self.dst or "—", True, NODE_DST if self.dst else TEXT3), (x, y)); y += 26
        self._hr(x, y); y += 14

        if self.path:
            self.screen.blit(self.font_xl.render(f"{self.total_dist:,} km", True, ACCENT), (x, y)); y += 38
            self.screen.blit(self.font_sm.render(f"{self.src} → {self.dst}  ({len(self.path)} cities)", True, TEXT2), (x, y)); y += 22
        elif self.src and self.dst:
            self.screen.blit(self.font_md.render("No path found", True, (239, 68, 68)), (x, y)); y += 24
        self._hr(x, y); y += 14

        if self.step_idx >= 0 and state:
            self._label(x, y, f"STEP  {self.step_idx + 1} / {len(self.steps)}"); y += 16
            self.screen.blit(self.font_md.render(f"Settled: {state['current']}", True, NODE_FRO), (x, y)); y += 18
            d = state["dist"].get(state["current"], "?")
            self.screen.blit(self.font_sm.render(f"Distance: {d} km", True, TEXT2), (x, y)); y += 18
            self.screen.blit(self.font_sm.render(f"Queue: {len(state['frontier'])} cities", True, TEXT2), (x, y)); y += 22
            self._hr(x, y); y += 14

        if show_path and self.path:
            self._label(x, y, "SHORTEST PATH"); y += 16
            for i, city in enumerate(self.path):
                if y > H - 90:
                    self.screen.blit(self.font_sm.render(f"  … {len(self.path)-i} more", True, TEXT3), (x, y))
                    break
                col = NODE_SRC if city == self.src else NODE_DST if city == self.dst else EDGE_PATH
                self.screen.blit(self.font_sm.render(city, True, col), (x + 8, y))
                if i < len(self.path) - 1:
                    km = self._edge_km(city, self.path[i + 1])
                    if km:
                        d_surf = self.font_sm.render(f"{km} km ↓", True, TEXT3)
                        self.screen.blit(d_surf, (self.PANEL - x - d_surf.get_width(), y))
                y += 14

        ly = H - 90
        self._label(x, ly, "LEGEND"); ly += 14
        for label, col in [("Source", NODE_SRC), ("Destination", NODE_DST),
                            ("In queue", NODE_FRO), ("Settled", NODE_VIS), ("Path", EDGE_PATH)]:
            pygame.draw.circle(self.screen, col, (x + 5, ly + 5), 4)
            self.screen.blit(self.font_sm.render(label, True, TEXT2), (x + 14, ly))
            ly += 13

    def _draw_hints(self, W, H):
        hints = ["SPACE: run   S: step   A: auto   R: reset", "+/-/scroll: zoom   drag: pan"]
        for i, h in enumerate(hints):
            t = self.font_sm.render(h, True, TEXT3)
            self.screen.blit(t, (self.PANEL + 8, H - 14 - (len(hints) - i - 1) * 14))

    def _label(self, x, y, text):
        self.screen.blit(self.font_sm.render(text, True, TEXT3), (x, y))

    def _hr(self, x, y):
        pygame.draw.line(self.screen, BORDER, (x, y), (self.PANEL - x, y))


    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                self._handle(event)

            if self.auto_play and self.step_idx >= 0:
                self.auto_timer += dt
                if self.auto_timer >= self.AUTO_DELAY:
                    self.auto_timer = 0
                    if self.step_idx < len(self.steps) - 1:
                        self.step_idx += 1
                    else:
                        self.auto_play = False

            self.draw()

    def _handle(self, event):
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        elif event.type == pygame.KEYDOWN:
            k = event.key
            if k in (pygame.K_ESCAPE, pygame.K_q):
                pygame.quit(); sys.exit()
            elif k == pygame.K_SPACE:
                self.step_idx = -1; self.auto_play = False; self._run()
            elif k == pygame.K_s:
                if not self.steps: self._run()
                if self.step_idx < 0:       self.step_idx = 0
                elif self.step_idx < len(self.steps) - 1: self.step_idx += 1
                self.auto_play = False
            elif k == pygame.K_a:
                if not self.steps: self._run()
                if self.step_idx < 0: self.step_idx = 0
                self.auto_play = not self.auto_play; self.auto_timer = 0
            elif k == pygame.K_r:
                self.step_idx = -1; self.auto_play = False
                self.path = []; self.steps = []; self.total_dist = float("inf")
            elif k in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                self.zoom = min(self.zoom * 1.15, 6.0)
            elif k in (pygame.K_MINUS, pygame.K_KP_MINUS):
                self.zoom = max(self.zoom / 1.15, 0.3)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if mx > self.PANEL:
                city = self._city_at(mx, my)
                if event.button == 1:
                    if city: self.src = city; self._run()
                    else:    self.dragging = True; self.drag_start = (mx, my)
                elif event.button == 3:
                    if city: self.dst = city; self._run()
                elif event.button == 4: self.zoom = min(self.zoom * 1.1, 6.0)
                elif event.button == 5: self.zoom = max(self.zoom / 1.1, 0.3)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                dx = event.pos[0] - self.drag_start[0]
                dy = event.pos[1] - self.drag_start[1]
                _, _, mw, mh = self._map_rect()
                self.offset_x += dx / (mw * self.zoom)
                self.offset_y += dy / (mh * self.zoom)
                self.drag_start = event.pos

        elif event.type == pygame.VIDEORESIZE:
            self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)



if __name__ == "__main__":
    base        = Path(__file__).parent
    edges_path  = base / "india_edges.json"
    coords_path = base / "city_coords.json"

    if not edges_path.exists():
        print(f"ERROR: {edges_path} not found. Run fetch_india_distance.py first.")
        sys.exit(1)

    print("Loading edges...")
    edges = load_edges(edges_path)

    # Collect unique city names from edges
    cities = sorted({c for a, b, _ in edges for c in (a, b)})
    print(f"Found {len(cities)} cities, {len(edges)} edges.")

    print("Loading / fetching coordinates...")
    raw_coords = geocode_cities(cities, coords_path)

    # Drop any cities that failed geocoding
    valid_cities = [c for c in cities if c in raw_coords]
    if len(valid_cities) < len(cities):
        missing = set(cities) - set(valid_cities)
        print(f"Warning: no coords for {missing} — those cities will be hidden.")
        edges = [(a, b, km) for a, b, km in edges if a in raw_coords and b in raw_coords]

    norm_coords = normalise_coords(raw_coords)

    print("Launching visualiser...")
    App(edges, norm_coords, edges).run()