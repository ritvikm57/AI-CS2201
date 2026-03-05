# Depth First Search (DFS)

## Overview

Depth First Search (DFS) is an uninformed search algorithm that explores the search space by **going as deep as possible** before backtracking. It uses a **stack (LIFO)** data structure (or recursion) to manage the frontier of nodes to be explored.

## How DFS Works

1. **Initialization**
   - Start with the initial state
   - Mark initial state as visited

2. **Recursive Exploration**
   - For current state:
     - If it's the goal state, return the solution
     - For each unvisited successor:
       - Mark successor as visited
       - Recursively explore successor
       - If solution found, return it
       - Otherwise, backtrack and try next successor

3. **Path Reconstruction**
   - Trace back from goal state to initial state using parent map

## Algorithm Pseudocode

```python
def DFS(problem, state=problem.initial_state, visited=set()):
    visited.add(state)
    
    if problem.is_goal(state):
        return state  # Found goal
    
    for action, successor in problem.get_successors(state):
        if successor not in visited:
            result = DFS(problem, successor, visited)
            if result is not None:
                return result  # Solution found in subtree
    
    return None  # No solution found in this path
```

## Characteristics

| Property | Value |
|----------|-------|
| **Data Structure** | Stack (LIFO) / Recursion |
| **Complete** | ✗ No (for infinite spaces) |
| **Optimal** | ✗ No |
| **Time Complexity** | O(b^m) |
| **Space Complexity** | O(bm) |
| **Memory Usage** | Low |

Where:
- b = branching factor
- m = maximum depth of search tree (can be infinite)

## Implementation Details

### Python Implementation

```python
def dfs(problem):
    """Depth First Search algorithm."""
    visited = set()
    parent_map = {}
    
    def dfs_recursive(state, parent=None):
        """Recursive DFS helper function."""
        if state in visited:
            return None
        
        visited.add(state)
        parent_map[state] = parent
        
        if problem.is_goal(state):
            return state
        
        for action, successor in problem.get_successors(state):
            result = dfs_recursive(successor, state)
            if result is not None:
                return result
        
        return None
    
    goal_state = dfs_recursive(problem.initial_state)
    
    if goal_state is None:
        return None, problem.nodes_explored
    
    return reconstruct_path(goal_state, parent_map), problem.nodes_explored
```

### Key Points

- Uses recursion to implement the stack implicitly
- Maintains `visited` set to prevent revisiting states
- Backtracks when a path leads to a dead end
- Returns immediately when goal is found
- Tracks parent relationships for path reconstruction

## Advantages

1. **Low Memory Usage** - Only stores current path on stack
2. **Space Efficient** - O(bm) vs O(b^d) for BFS
3. **Fast for Some Problems** - May find solution quickly if lucky
4. **Natural Implementation** - Recursive implementation is intuitive
5. **Suitable for Deep Solutions** - Efficiently explores deep trees
6. **Scalable** - Can handle larger search spaces than BFS

## Disadvantages

1. **Incomplete** - May not find solution in infinite/cyclic spaces
2. **Not Optimal** - May find longer/worse solutions
3. **Unpredictable** - Performance depends on order of successors
4. **Can Get Stuck** - May explore deep irrelevant branches
5. **No Optimality Guarantee** - Even if solution exists closer

## Example: Jug Problem

### Example Trace

For the Milk & Water Jug Problem:

```
DFS Exploration Order (depends on successor ordering):

Start: (0,0) - Visit
  Expand: [(4,0), (0,3)]
  
Go to (4,0) - Visit
  Expand: [(4,3), (0,0)✓]
  
Go to (4,3) - Visit
  Expand: [(4,3)✓ (already visited), (0,3), (1,3)]
  
Go to (0,3) - Visit
  Expand: [(3,0), (0,3)✓]
  
Go to (3,0) - Visit
  Expand: [(3,3), (4,0)✓]
  
Go to (3,3) - Visit
  Expand: [(4,2), ...other states...]
  
Go to (4,2) - GOAL FOUND! ✓
  
Path: (0,0) → (0,3) → (3,0) → (3,3) → (4,2)
```

### Performance Statistics

- **Nodes Explored:** 8 (fewer than BFS in this case!)
- **Solution Length:** 4 steps
- **Memory Peak:** Only nodes on current path stored

## Time and Space Complexity Analysis

### Time Complexity: O(b^m)

- Worst case: explore all nodes in tree of depth m
- Each node has b successors
- Total nodes: worst case O(b^m)
- Can be faster if solution found on first path explored

### Space Complexity: O(bm)

- Only need to store nodes on current path from root to leaf
- Path length at most m
- Each node stores b-1 alternatives
- Much more memory efficient than BFS

## When to Use DFS

✓ **Use DFS when:**
- Memory is very limited
- Search space is very large
- Deep solutions are expected
- Any solution quickly is acceptable
- Problem has finite depth bound
- Need to save memory over optimality

✗ **Don't use DFS when:**
- Solution quality matters
- Shortest path is required
- Solution might not be bounded
- Search space is infinite/cyclic

## Variants

### DFS Variations

1. **Depth-Limited Search (DLS)** - DFS with maximum depth limit
2. **Iterative Deepening DFS (IDDFS)** - DFS with increasing depth limits
3. **Backtracking** - DFS with intelligent pruning
4. **Recursive Backtracking** - For constraint satisfaction problems

## Practical Applications

- **Maze Solving** - Finding any path through maze
- **Puzzle Solving** - Backtracking solutions (N-Queens, Sudoku)
- **Tree/Graph Traversal** - Preorder, inorder, postorder tree traversals
- **Topological Sorting** - Ordering nodes in directed acyclic graphs
- **Cycle Detection** - Detecting cycles in graphs
- **Game Tree Search** - Minimax for game playing (chess, tic-tac-toe)
- **Constraint Satisfaction** - CSP solving with backtracking

## Comparison with Other Uninformed Searches

| Aspect | BFS | DFS | IDDFS |
|--------|-----|-----|-------|
| Memory | High | Low | Low |
| Optimal | Yes | No | Yes |
| Complete | Yes | No | Yes |
| Speed (avg) | Medium | Fast | Medium |
| Best For | Shortest Path | Memory Limited | Balanced |

## Complexity Comparison

```
        Best Case    Average Case   Worst Case
BFS:    O(1)         O(b^d)        O(b^d)
DFS:    O(1)         O(b^m)        O(b^m)
IDDFS:  O(b^d)       O(b^d)        O(b^d)

Where d = solution depth, m = max depth, b = branching factor
```

## Important Notes

### Cyclic Check
Always maintain a `visited` set to:
- Prevent infinite loops in cyclic graphs
- Avoid re-exploring states
- Ensure termination

Without cycle checking, DFS can loop forever!

### Successor Ordering
The order of successor generation affects:
- Performance (how quickly goal is found)
- Solution quality (which solution is returned first)
- Memory usage (depends on search tree structure)

### Bounded Depth
For infinite spaces, always use **Depth-Limited Search** or **IDDFS** instead of pure DFS.

## Conclusion

DFS is a memory-efficient uninformed search algorithm, making it practical for large search spaces where memory is a constraint. However, it sacrifices optimality and completeness. For problems requiring optimal solutions, other algorithms should be used.

DFS forms the basis for many practical algorithms:
- **IDDFS** - Adds completeness and optimality
- **Backtracking** - Adds intelligent pruning
- **Minimax** - For game tree search
- **Topological Sort** - For dependency ordering

Understanding DFS is fundamental to computer science and AI problem solving.
