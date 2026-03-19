# Dijkstra's Algorithm: Indian Cities Road Network

A visualization of Dijkstra's shortest path algorithm applied to major Indian cities using Google Maps distance data.

## Files

### `fetch_india_distance.py`
Builds a sparse road graph of Indian cities using the Google Maps Distance Matrix API.

**Usage:**
```bash
pip install requests
python fetch_india_distance.py --key YOUR_API_KEY
# or via environment variable:
GOOGLE_MAPS_API_KEY=your_key python fetch_india_distance.py
```

**Arguments:**
- `--key KEY` - Google Maps API key
- `--k K` - Number of nearest neighbors to keep per city (default: 6)
- `--delay DELAY` - Delay between API requests in seconds (default: 0.25)
- `--out-dir DIR` - Output directory (default: current directory)

**Output Files:**
- `india_distances.json` - Full NxN distance matrix
- `india_edges.json` - Sparse edge list
- `india_edges.csv` - Same edge list as CSV

**Strategy:**
- Fetches road distances from each city to all others
- Keeps each city's K nearest neighbors
- Uses union rule: keeps edge if either city considers the other in top-K
- ~80 API requests total, ~$0.03 cost

### `dijkstra_india.py`
Interactive pygame visualization of Dijkstra's algorithm on the India road network.

**Requirements:**
```bash
pip install pygame requests
```

**Controls:**
- **Left-click** a city → set as SOURCE
- **Right-click** a city → set as DESTINATION
- **SPACE** → run Dijkstra instantly
- **S** → step-by-step mode
- **A** → auto-play steps
- **R** → reset view
- **+/-** or **Scroll** → zoom
- **Click + drag** → pan
- **ESC/Q** → quit

**Features:**
- Real-time shortest path calculation
- Step-by-step algorithm visualization
- Auto-play mode for animations
- Pan and zoom navigation
- Color-coded cities and edges
- Distance information overlay

## Data

The visualization uses:
- Major Indian cities as nodes
- Google Maps road distances as edge weights
- City coordinates from OpenStreetMap Nominatim API (cached in `city_coords.json`)
- Pre-computed edge data in `india_edges.json`

## Example Usage

1. Generate the road network data:
   ```bash
   python fetch_india_distance.py --key YOUR_GOOGLE_MAPS_KEY
   ```

2. Launch the visualization:
   ```bash
   python dijkstra_india.py
   ```

3. Click cities to set source/destination, press SPACE to find shortest path

## Algorithm

Dijkstra's algorithm finds the shortest path between two nodes in a weighted graph:
1. Initialize distances to all nodes as infinity except source (distance 0)
2. Use a priority queue to process nodes in order of distance
3. For each node, update distances to unvisited neighbors
4. Continue until destination is reached or all nodes are visited
5. Reconstruct path by backtracking through parent pointers

Time Complexity: O((V + E) log V) where V = cities, E = roads
