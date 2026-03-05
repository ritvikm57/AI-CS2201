# Uninformed Search Algorithms in Python

### BFS, DFS and IDDFS using the Milk & Water Jug Problem

## Overview

This project demonstrates the implementation of **Uninformed Search algorithms** using the **Milk and Water Jug Problem** as a search problem.

The algorithms implemented are:

* **Breadth First Search (BFS)** - Explores level by level, guarantees optimal solution
* **Depth First Search (DFS)** - Explores deep paths first, memory efficient
* **Iterative Deepening Depth First Search (IDDFS)** - Combines advantages of BFS and DFS

These algorithms explore the **state space of the problem** to reach a goal state.

The implementation is written in **Python** and structured using separate packages for each search strategy.

---

## Problem Description

The **Milk and Water Jug Problem** is a classic Artificial Intelligence search problem.

We are given:

* Jug 1 capacity = **4 liters**
* Jug 2 capacity = **3 liters**
* Initial state = **(0,0)** (both jugs empty)

**Goal:**

Measure **exactly 2 liters of water** in one of the jugs.

**State Representation:**

A state is represented as `(Jug1, Jug2)`

Example: `(3,0)` means Jug1 contains 3 liters and Jug2 contains 0 liters.

---

## Allowed Operations

From any state we can perform the following operations:

1. **Fill Jug1** - Fill jug1 to capacity
2. **Fill Jug2** - Fill jug2 to capacity
3. **Empty Jug1** - Empty jug1 completely
4. **Empty Jug2** - Empty jug2 completely
5. **Pour Jug1 → Jug2** - Pour from jug1 to jug2 until jug2 is full or jug1 is empty
6. **Pour Jug2 → Jug1** - Pour from jug2 to jug1 until jug1 is full or jug2 is empty

These operations generate the **successor states** used by the search algorithms.

---

## Project Structure

```
search-problems/
├── model/
│   └── state.py              # State representation
├── problem/
│   └── jug.py                # Jug problem implementation
├── bfs/
│   └── bfs.py                # Breadth First Search
├── dfs/
│   └── dfs.py                # Depth First Search
├── iddfs/
│   └── iddfs.py              # Iterative Deepening DFS
├── main.py                   # Main program
└── README.md                 # This file
```

### Module Descriptions

**`model/state.py`**
- Defines the `State` class representing jug configurations
- Implements state equality, hashing, and goal checking
- State format: `(jug1_amount, jug2_amount)`

**`problem/jug.py`**
- Implements the `JugProblem` class
- Defines jug capacities and goal condition
- Generates successor states based on allowed operations
- Tracks nodes explored during search

**`bfs/bfs.py`**
- Implements Breadth First Search using a queue
- Guarantees optimal (shortest path) solution
- Higher memory usage due to frontier storage

**`dfs/dfs.py`**
- Implements Depth First Search using recursion
- Lower memory usage but may not find optimal solution
- Explores deep paths before backtracking

**`iddfs/iddfs.py`**
- Implements Iterative Deepening DFS
- Performs depth-limited searches with increasing limits
- Combines memory efficiency of DFS with optimality of BFS

**`main.py`**
- Runs all three algorithms on the problem
- Compares performance metrics
- Displays solution paths and analysis

---

## Running the Project

### Prerequisites

- Python 3.6 or higher
- No external dependencies required (uses only Python standard library)

### Installation

```bash
# Navigate to the project directory
cd /path/to/search-problems
```

### Execution

```bash
python main.py
```

### Expected Output

```
============================================================
UNINFORMED SEARCH ALGORITHMS
Milk and Water Jug Problem
============================================================

Problem Setup:
  Jug 1 capacity: 4 liters
  Jug 2 capacity: 3 liters
  Initial state: (0, 0)
  Goal: Measure exactly 2 liters in one jug

...

============================================================
BREADTH FIRST SEARCH (BFS)
============================================================
Solution found!

State sequence:
  0: (0,0)
  1: (0,3)
  2: (3,0)
  3: (3,3)
  4: (4,2)

Solution length: 4 steps
Nodes explored: 11

...

============================================================
ALGORITHM COMPARISON
============================================================
Algorithm       Solution Length    Nodes Explored      
-----------------------------------------------------------
BFS             4                  11                  
DFS             4                  8                   
IDDFS           4                  17                  
```

---

## Algorithms Implemented

### 1. Breadth First Search (BFS)

**How it works:**

BFS explores the search space **level by level**. It uses a **queue** (FIFO) to store nodes to be explored.

**Algorithm:**
1. Start with initial state in queue
2. While queue is not empty:
   - Remove front state from queue
   - If goal → return solution
   - Otherwise, add all unvisited successors to queue

**Properties:**

| Property | Value |
|----------|-------|
| Complete | ✓ Yes (always finds solution if one exists) |
| Optimal | ✓ Yes (finds shortest path for uniform cost) |
| Time Complexity | O(b^d) where b=branching factor, d=depth |
| Space Complexity | O(b^d) - stores entire frontier |
| Memory Usage | High |

**Advantages:**
- Guaranteed to find shortest path
- Complete for finite spaces
- Predictable solution quality

**Disadvantages:**
- High memory consumption
- Slow for deep solutions
- Not suitable for very large search spaces

---

### 2. Depth First Search (DFS)

**How it works:**

DFS explores the **deepest branches first** before backtracking. It uses a **stack** (LIFO) or recursion.

**Algorithm:**
1. Start with initial state
2. Recursively explore:
   - If goal → return solution
   - For each unvisited successor:
     - Recursively search successor
     - If solution found → return it
   - Backtrack

**Properties:**

| Property | Value |
|----------|-------|
| Complete | ✗ No (may not find solution in infinite spaces) |
| Optimal | ✗ No (may find longer solutions) |
| Time Complexity | O(b^m) where m=max depth |
| Space Complexity | O(bm) - stores only current path |
| Memory Usage | Low |

**Advantages:**
- Very low memory usage
- Fast for solutions in deep parts of tree
- Suitable for large search spaces

**Disadvantages:**
- Does not guarantee optimal solution
- May explore irrelevant branches deeply
- Incomplete for infinite search spaces

---

### 3. Iterative Deepening DFS (IDDFS)

**How it works:**

IDDFS combines the advantages of BFS and DFS. It performs **depth-limited searches** with increasing depth limits.

**Algorithm:**
```
For each depth limit d = 0, 1, 2, 3, ...:
  Perform depth-limited DFS with limit d
  If solution found → return it
```

**Example progression:**
```
Depth Limit = 0  (explore only initial state)
Depth Limit = 1  (explore states at depth ≤ 1)
Depth Limit = 2  (explore states at depth ≤ 2)
Depth Limit = 3  (explore states at depth ≤ 3)
...
```

**Properties:**

| Property | Value |
|----------|-------|
| Complete | ✓ Yes (like BFS) |
| Optimal | ✓ Yes (like BFS) |
| Time Complexity | O(b^d) - same as BFS |
| Space Complexity | O(bd) - same as DFS |
| Memory Usage | Low |

**Advantages:**
- Memory efficient like DFS
- Optimal solution like BFS
- Combines best of both worlds
- Works well for unknown solution depth

**Disadvantages:**
- Re-explores nodes multiple times
- Higher computation cost than BFS
- More node expansions overall

---

## Performance Comparison

### For the Jug Problem

| Metric | BFS | DFS | IDDFS |
|--------|-----|-----|-------|
| **Solution Depth** | 4 steps | 4 steps | 4 steps |
| **Nodes Explored** | 11 | 8 | 17 |
| **Solution Quality** | Optimal | Optimal | Optimal |
| **Memory Usage** | High | Low | Low |
| **Computation Cost** | Moderate | Low | High |

### Analysis

**BFS Performance:**
- Explores nodes systematically level by level
- Guarantees the shortest path solution
- Uses more memory to maintain queue of frontier nodes
- Efficient for this problem as solution is not very deep

**DFS Performance:**
- Explores fewer nodes than BFS for this problem
- May get lucky finding solution quickly via backtracking
- Uses minimal memory (only current path)
- Not guaranteed to find shortest path (though it did here)

**IDDFS Performance:**
- Re-explores nodes at lower depths multiple times
- Total nodes explored is higher due to repeated searches
- Memory usage remains low
- Guarantees optimal solution without BFS's high memory cost
- Better for problems where solution depth is unknown

---

## Trade-offs Summary

### Memory vs Solution Quality

```
         Low Memory                    High Memory
DFS ◄──────────────────────► BFS
     IDDFS (good compromise)
```

### Optimality vs Speed

```
No Guarantee               Guarantees Optimal
DFS ◄──────────────────────► BFS
     IDDFS (good compromise)
```

---

## When to Use Each Algorithm

### Use BFS When:
- Solution depth is small
- Memory is available
- You need the shortest path
- Optimal solution is critical

### Use DFS When:
- Memory is very limited
- Solutions are deep in the tree
- Any solution is acceptable
- Search space is very large

### Use IDDFS When:
- Memory is limited but solution depth is unknown
- You need optimal solution but want low memory
- Balanced performance is desired
- Standard choice for uninformed search in practice

---

## Key Concepts

### Search Space
The set of all possible states reachable from the initial state through legal operations.

### Frontier (Open Set)
The set of states that have been discovered but not yet explored.

### Visited (Closed Set)
The set of states that have been explored.

### Successor Function
The function that generates all valid next states from a given state.

### Completeness
An algorithm is complete if it finds a solution whenever one exists.

### Optimality
An algorithm is optimal if it finds the solution with the best cost (shortest path).

---

## Implementation Notes

### State Representation
States are represented using the `State` class which:
- Stores jug1 and jug2 amounts
- Implements `__hash__()` for use in sets
- Implements `__eq__()` for equality comparison
- Provides `is_goal()` method for goal checking

### Avoiding Cycles
All algorithms maintain a `visited` set to prevent exploring the same state twice, which:
- Prevents infinite loops in cyclic search spaces
- Significantly reduces nodes explored
- Trades memory for time

### Parent Tracking
Each algorithm maintains a `parent_map` to reconstruct the solution path:
- Maps each state to its parent state
- Allows backtracking from goal to initial state
- Enables printing the complete solution sequence

---

## Conclusion

This project demonstrates how different **uninformed search strategies** explore the same problem space with different characteristics:

**Key Insights:**

1. **BFS guarantees optimal solutions** but uses more memory
2. **DFS uses less memory** but may produce non-optimal solutions
3. **IDDFS provides optimal solutions with lower memory usage**, making it a practical choice for many problems

These algorithms form the **foundation** for more advanced search techniques like:
- A* Search (informed search)
- Branch and Bound
- Constraint Satisfaction
- Game Tree Search (Minimax)

Understanding these fundamental algorithms is essential for anyone working in **Artificial Intelligence and Computer Science**.

---

## Author

Implementation in **Python** for educational purposes in AI/CS courses.

A comprehensive demonstration of uninformed search algorithms used in solving classic AI problems.
