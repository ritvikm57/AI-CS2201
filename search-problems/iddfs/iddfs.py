"""
Iterative Deepening Depth First Search (IDDFS) implementation for the Jug Problem.

IDDFS combines advantages of BFS and DFS by repeatedly performing depth-limited search
with increasing depth limits.
- Complete: Always finds a solution if one exists
- Optimal: Finds optimal depth solution like BFS
- Memory: Low memory usage like DFS, but re-explores nodes
"""

from model.state import State


def iddfs(problem):
    """
    Iterative Deepening Depth First Search algorithm.
    
    Args:
        problem: The search problem (JugProblem)
    
    Returns:
        Tuple of (solution_path, nodes_explored) or (None, nodes_explored) if no solution
    """
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
            
            # Check if goal state reached
            if problem.is_goal(state):
                return state
            
            # Only expand if depth limit not reached
            if depth > 0:
                for action, successor in problem.get_successors(state):
                    result = dfs_limited(successor, depth - 1, state)
                    if result is not None:
                        return result
            
            return None
        
        # Start depth-limited DFS from initial state
        goal_state = dfs_limited(problem.initial_state, depth_limit)
        
        if goal_state is not None:
            return reconstruct_path(goal_state, parent_map), problem.nodes_explored
    
    return None, problem.nodes_explored


def reconstruct_path(state, parent_map):
    """Reconstruct the path from initial state to goal state."""
    path = []
    current = state
    
    while current is not None:
        path.append(current)
        current = parent_map.get(current)
    
    return list(reversed(path))
