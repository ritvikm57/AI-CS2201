# Breadth First Search (BFS)

## Overview

Breadth First Search (BFS) is an uninformed search algorithm that explores the search space **level by level**. It uses a **queue (FIFO)** data structure to manage the frontier of nodes to be explored.

## How BFS Works

1. **Initialization**
   - Start with the initial state in the queue
   - Mark initial state as visited

2. **Main Loop**
   - While queue is not empty:
     - Dequeue front state
     - If it's the goal state, return the solution
     - For each unvisited successor:
       - Mark as visited
       - Enqueue successor
       - Record parent relationship

3. **Path Reconstruction**
   - Trace back from goal state to initial state using parent map

## Algorithm Pseudocode

```python
def BFS(problem):
    frontier = Queue()
    frontier.enqueue(problem.initial_state)
    visited = {problem.initial_state}
    parent_map = {problem.initial_state: None}
    
    while not frontier.is_empty():
        state = frontier.dequeue()
        
        if problem.is_goal(state):
            return reconstruct_path(state, parent_map)
        
        for action, successor in problem.get_successors(state):
            if successor not in visited:
                visited.add(successor)
                parent_map[successor] = state
                frontier.enqueue(successor)
    
    return None  # No solution found
```

## Characteristics

| Property | Value |
|----------|-------|
| **Data Structure** | Queue (FIFO) |
| **Complete** | ✓ Yes |
| **Optimal** | ✓ Yes (uniform cost) |
| **Time Complexity** | O(b^d) |
| **Space Complexity** | O(b^d) |
| **Memory Usage** | High |

Where:
- b = branching factor (average number of successors per state)
- d = depth of shallowest goal state

## Implementation Details

### Python Implementation

```python
from collections import deque

def bfs(problem):
    """Breadth First Search algorithm."""
    frontier = deque([problem.initial_state])
    visited = {problem.initial_state}
    parent_map = {problem.initial_state: None}
    
    while frontier:
        state = frontier.popleft()  # Dequeue from front
        
        if problem.is_goal(state):
            return reconstruct_path(state, parent_map), problem.nodes_explored
        
        for action, successor in problem.get_successors(state):
            if successor not in visited:
                visited.add(successor)
                parent_map[successor] = state
                frontier.append(successor)  # Enqueue at back
    
    return None, problem.nodes_explored
```

### Key Points

- Uses Python's `deque` (double-ended queue) for efficient FIFO operations
- Maintains `visited` set to prevent cycles
- Tracks parent relationships to reconstruct the solution path
- Explores nodes in order of distance from initial state

## Advantages

1. **Completeness** - Always finds a solution if one exists
2. **Optimality** - Finds the shortest path for uniform cost problems
3. **Predictable** - Explores in a systematic, level-by-level manner
4. **Well-studied** - Extensive research and optimizations available
5. **Suitable for shallow solutions** - Fast when solution is not too deep

## Disadvantages

1. **High Memory Usage** - Must store all nodes at current frontier level
2. **Space Complexity** - O(b^d) space can be prohibitive for large search spaces
3. **Slow for Deep Solutions** - Explores all nodes up to solution depth
4. **Inefficient with Constraints** - Doesn't prioritize promising states

## Example: Jug Problem

### Example Trace

For the Milk & Water Jug Problem with initial state (0,0) and goal state containing 2 liters:

```
BFS Frontier Expansion:

Level 0:
  Queue: [(0,0)]

Level 1:
  Explore: (0,0)
  Queue: [(4,0), (0,3)]

Level 2:
  Explore: (4,0)
  Additional: (4,3), (0,0) [visited]
  Explore: (0,3)
  Additional: (3,0), (0,0) [visited]
  Queue: [(4,3), (3,0), (3,3), (0,3) if from 4,3...]

...continues until goal is found...

Goal found at Level 4:
  (0,0) → (0,3) → (3,0) → (3,3) → (4,2) ✓
```

### Performance Statistics

- **Nodes Explored:** 11
- **Solution Length:** 4 steps
- **Memory Peak:** All 11 frontier nodes stored simultaneously

## Time and Space Complexity Analysis

### Time Complexity: O(b^d)

- In worst case, must explore all nodes up to depth d
- Each node has b successors
- Total nodes: 1 + b + b² + ... + b^d = (b^(d+1) - 1) / (b - 1) ≈ O(b^d)

### Space Complexity: O(b^d)

- Must maintain entire queue of frontier nodes
- At depth d, frontier can contain up to b^d nodes
- Storage grows exponentially with search depth

## When to Use BFS

✓ **Use BFS when:**
- Solution depth is relatively small
- You have sufficient memory available
- Shortest path is required
- Problem has uniform edge costs
- Solution quality is critical

✗ **Don't use BFS when:**
- Search space is very large
- Memory is extremely limited
- Solutions are known to be deep
- Any solution quickly is acceptable

## Variants

### BFS Variations

1. **Bidirectional BFS** - Search from both initial and goal states
2. **BFS with Priority Queue** - Weighted BFS (essentially Dijkstra's)
3. **Bounded BFS** - Limited depth to control memory

## Practical Applications

- **Graph Shortest Path** - Finding shortest routes in networks
- **Social Network Analysis** - Finding connections/degrees of separation
- **Puzzle Solving** - Sliding puzzles, mazes (when optimality needed)
- **Web Crawling** - Visiting pages in breadth-first order
- **Natural Language Processing** - Parse tree exploration

## Comparison with Other Uninformed Searches

| Aspect | BFS | DFS | IDDFS |
|--------|-----|-----|-------|
| Memory | High | Low | Low |
| Optimal | Yes | No | Yes |
| Complete | Yes | No | Yes |
| Speed | Medium | Fast | Slower |
| Uses | Shortest Path | Depth Limit | Balanced |

## Conclusion

BFS is a fundamental and widely-used uninformed search algorithm. It guarantees finding the shortest path but at the cost of high memory usage. For problems where optimality is critical and the search space is manageable, BFS is an excellent choice.

The main challenge is managing memory for large search spaces, which has led to developments of more sophisticated algorithms that can balance the trade-offs between memory and solution quality.
