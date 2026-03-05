# Uninformed Search Algorithms in Python

Implementation of **BFS, DFS, and IDDFS** using the **Milk & Water Jug Problem**.

## Problem

- **Jug 1:** 4 liters capacity
- **Jug 2:** 3 liters capacity
- **Start:** (0, 0) 
- **Goal:** 2 liters in either jug
- **Operations:** Fill, Empty, Pour (between jugs)

## Algorithms

**BFS (Breadth First Search)**
- Explores level-by-level using a queue
- Finds shortest path
- Higher memory usage
- Time: O(b^d), Space: O(b^d)

**DFS (Depth First Search)**
- Explores deepest paths first using recursion
- Memory efficient
- May not find shortest path
- Time: O(b^m), Space: O(bm)

**IDDFS (Iterative Deepening)**
- Repeats DFS with increasing depth limits
- Finds shortest path with low memory
- Explores nodes multiple times
- Time: O(b^d), Space: O(bd)

## Running

```bash
python3 main.py
```

Example output:
```
BFS: Solutions length 4, Nodes explored 10
DFS: Solution length 6, Nodes explored 7
IDDFS: Solution length 6, Nodes explored 41
```

## Structure

```
model/state.py       - State (jug1, jug2) representation
problem/jug.py       - Problem definition & operations
bfs/bfs.py          - Breadth First Search
dfs/dfs.py          - Depth First Search  
iddfs/iddfs.py      - Iterative Deepening DFS
main.py             - Run & compare all algorithms
```

## Key Insights

- **BFS** guarantees shortest path but uses more memory
- **DFS** uses minimal memory but may find longer solutions
- **IDDFS** combines both: optimal + low memory with re-exploration trade-off
- **state.py is kept separate** following Python best practices for code organization
