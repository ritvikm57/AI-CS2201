# Iterative Deepening Depth First Search (IDDFS)

## Overview

Iterative Deepening Depth First Search (IDDFS) is an uninformed search algorithm that combines the advantages of **Breadth First Search (BFS)** and **Depth First Search (DFS)**.

It performs **depth-limited searches** with **increasing depth limits** until a solution is found.

## How IDDFS Works

1. **Initialization**
   - Set depth limit to 0

2. **Main Loop**
   - Perform depth-limited DFS with current depth limit
   - If solution found, return it
   - Increment depth limit
   - Repeat until solution is found or depth exceeds some maximum

3. **Depth-Limited DFS**
   - Like DFS but stops exploring when depth limit reached
   - Explores all nodes at depths 0, 1, 2, ..., limit

## Algorithm Pseudocode

```python
def IDDFS(problem, max_depth=50):
    for depth_limit in range(max_depth):
        result = depth_limited_dfs(problem, depth_limit)
        if result is not None:
            return result
    return None

def depth_limited_dfs(problem, depth_limit, state, depth=0, visited=set()):
    visited.add(state)
    
    if problem.is_goal(state):
        return state
    
    if depth < depth_limit:
        for action, successor in problem.get_successors(state):
            if successor not in visited:
                result = depth_limited_dfs(problem, depth_limit, successor, depth + 1, visited)
                if result is not None:
                    return result
    
    return None
```

## Characteristics

| Property | Value |
|----------|-------|
| **Data Structure** | Stack (LIFO) / Recursion |
| **Complete** | ✓ Yes |
| **Optimal** | ✓ Yes |
| **Time Complexity** | O(b^d) |
| **Space Complexity** | O(bd) |
| **Memory Usage** | Low |

Where:
- b = branching factor
- d = depth of solution

## Implementation Details

### Python Implementation

```python
def iddfs(problem):
    """Iterative Deepening DFS algorithm."""
    problem.reset_counter()
    
    # Iteratively increase depth limit
    for depth_limit in range(0, 50):  # Max depth of 50
        visited = set()
        parent_map = {}
        
        def dfs_limited(state, depth, parent=None):
            """Depth-limited DFS helper function."""
            if state in visited:
                return None
            
            visited.add(state)
            parent_map[state] = parent
            problem.nodes_explored += 1
            
            if problem.is_goal(state):
                return state
            
            if depth > 0:
                for action, successor in problem.get_successors(state):
                    result = dfs_limited(successor, depth - 1, state)
                    if result is not None:
                        return result
            
            return None
        
        goal_state = dfs_limited(problem.initial_state, depth_limit)
        
        if goal_state is not None:
            return reconstruct_path(goal_state, parent_map), problem.nodes_explored
    
    return None, problem.nodes_explored
```

### Key Points

- Creates new visited set for each depth limit iteration
- Maintains parent map to reconstruct solution path
- Explores nodes in order of depth from shallow to deep
- Re-explores nodes with each depth limit increase
- Guarantees finding shallowest goal state

## Advantages

1. **Memory Efficient** - Uses O(bd) space like DFS
2. **Complete** - Always finds solution if one exists
3. **Optimal** - Finds solution at shallowest depth
4. **Practical Balance** - Best of BFS and DFS for many problems
5. **Unknown Depth** - Works well when solution depth is unknown
6. **Scalable** - Can handle large search spaces with memory constraints

## Disadvantages

1. **Re-explores Nodes** - Nodes explored multiple times at different depth limits
2. **Higher Computation** - More node expansions than BFS
3. **Repeated Work** - Earlier depth limits repeat earlier searches
4. **Overhead** - Multiple passes through search space
5. **Slower than DFS** - Takes longer than simple DFS

## Example: Jug Problem

### Example Trace

```
IDDFS Execution on Jug Problem:

Depth Limit = 0:
  Explore: (0,0)
  Is goal? No
  No solution at depth 0
  
Depth Limit = 1:
  Explore: (0,0)
    Successors: (4,0), (0,3)
  Explore: (4,0)
  Explore: (0,3)
  No solution at depth ≤ 1
  
Depth Limit = 2:
  Explore: (0,0)
    Explore: (4,0)
      Explore: (4,3), (0,0)✓
    Explore: (0,3)
      Explore: (3,0), (0,0)✓
  No solution at depth ≤ 2
  Nodes explored: 1 + 2 + 4 + ... = many
  
...continues...

Depth Limit = 4:
  Explore all nodes up to depth 4
  ...
  Find: (0,0) → (0,3) → (3,0) → (3,3) → (4,2) ✓
  GOAL FOUND!
```

### Performance Statistics

- **Total Nodes Explored:** 17
- **Solution Length:** 4 steps
- **Memory Peak:** Only nodes on current path
- **Computation:** Multiple passes through search tree

## Time and Space Complexity Analysis

### Time Complexity: O(b^d)

Although IDDFS explores nodes multiple times, the total is still O(b^d):

```
Depth 0: 1 node
Depth 1: b + 1 nodes (explore 1 root + b children at limit 1)
Depth 2: b² + b + 1 nodes (explore full tree + shallower nodes)
...
Total: 1 + b + b² + ... + b^d = (b^(d+1) - 1)/(b-1) ≈ O(b^d)
```

The re-exploration factor is small (only 1/(b-1) overhead).

### Space Complexity: O(bd)

- Only needs to maintain current path on stack
- Path length is at most d
- Each level can have at most b alternatives
- Total: O(b × d) space

## Comparison: Why IDDFS Doesn't Use Much More Time

Although IDDFS re-explores nodes, the total overhead is minimal:

For b=10, d=5:

| Algorithm | Nodes | Calculation |
|-----------|-------|-------------|
| BFS | ~111,110 | 10^0 + 10^1 + ... + 10^5 |
| DFS | ~100,000 | Up to 10^5 (just first path) |
| IDDFS | ~123,456 | 1 + 10 + (10+10²) + (10+10²+10³) + ... |

IDDFS explores only ~11% more nodes than BFS!

## When to Use IDDFS

✓ **Use IDDFS when:**
- Memory is limited but optimality is needed
- Solution depth is unknown
- Want balanced performance
- Need both completeness and optimality
- Search space is large and memory critical
- Standard uninformed search needed

✗ **Don't use IDDFS when:**
- Solution is known to be very deep (use DFS)
- Memory is not a constraint (use BFS)
- Time is extremely critical (use BFS or DFS)
- Problem has very low branching factor (overhead not worth it)

## Variants

### IDDFS Variations

1. **IDDFS with f-limit** - Combines with heuristics (IDA*)
2. **Progressive Deepening** - For incremental computation
3. **Bounded IDDFS** - With maximum depth bound

### Related Algorithms

1. **IDA*** - IDDFS with heuristic function
2. **Depth-Limited Search (DLS)** - Single depth limit
3. **Depth-Limited DFS** - DFS with depth control

## Practical Applications

- **Game AI** - Game tree search (when memory matters)
- **Puzzle Solving** - Optimal solutions with limited memory
- **Plan Generation** - AI planning with memory constraints
- **Network Routing** - Finding shortest paths with memory limits
- **Robotics** - Path planning with computational constraints
- **Natural Language** - Parsing with depth limits

## Step-by-Step Comparison

### BFS Approach
```
All nodes at depth 1
  → All nodes at depth 2
     → ...
        → Goal found
```

### DFS Approach
```
First branch fully explored
  → Backtrack
     → Second branch fully explored
        → Backtrack
           → Goal found (wherever it is)
```

### IDDFS Approach
```
Explore depth ≤ 0 (root only)
  → Explore depth ≤ 1
     → Explore depth ≤ 2
        → Continue until goal found
```

## Memory vs Time Trade-off

```
BFS:   Maximum memory, minimum time
IDDFS: Minimal memory, reasonable time (only ~11% worse than BFS)
DFS:   Minimal memory, unpredictable time
```

## Important Considerations

### The Re-exploration Overhead

Despite re-exploring nodes, the overhead is small because:
- Nodes at shallow depths are explored multiple times in successive iterations
- But shallow levels are exponentially smaller than deep levels
- Total overhead: only a constant factor

### When Branching Factor is Small

If b = 2, overhead is minimal:
- IDDFS cost: 2 × O(2^d) ≈ O(2^d)
- BFS cost: O(2^d)
- Difference is minimal!

### Practical Implementation Tips

1. **Reuse Visited Set** - Consider whether to reset between depth limits
2. **Early Termination** - Stop as soon as goal found
3. **Memoization** - Cache results of subproblems if applicable
4. **Depth Increment** - Can increment by more than 1 for efficiency

## Conclusion

IDDFS is often called the "best of both worlds" for uninformed search:

**Key Insights:**

1. **Combines BFS benefits** - Complete and optimal
2. **Has DFS efficiency** - Low memory usage O(bd)
3. **Minimal overhead** - Only ~11-20% more nodes explored than BFS
4. **Practical choice** - Used in many real AI systems
5. **Flexible** - Can be extended with heuristics (IDA*)

IDDFS is particularly valuable when:
- Search space is too large for BFS to fit in memory
- Solution depth is unknown
- Both completeness and optimality are required

This algorithm demonstrates an important principle in AI: **sometimes using the same space multiple times is better than using more memory**.

## See Also

- [BFS - Breadth First Search](../bfs/README.md)
- [DFS - Depth First Search](../dfs/README.md)
- [Jug Problem - Problem Definition](../problem/jug.py)
- [Main - Algorithm Comparison](../main.py)
