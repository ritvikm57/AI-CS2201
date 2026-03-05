"""
Depth First Search (DFS) implementation for the Jug Problem.

DFS explores the deepest branch first before backtracking using a stack.
- Complete: May not find solution in infinite spaces
- Optimal: Does not guarantee optimal solution
- Memory: Low memory usage compared to BFS
"""

from model.state import State


def dfs(problem):
    """
    Depth First Search algorithm.
    
    Args:
        problem: The search problem (JugProblem)
    
    Returns:
        Tuple of (solution_path, nodes_explored) or (None, nodes_explored) if no solution
    """
    problem.reset_counter()
    
    visited = set()
    parent_map = {}
    
    def dfs_recursive(state, parent=None):
        """Recursive DFS helper function."""
        if state in visited:
            return None
        
        visited.add(state)
        parent_map[state] = parent
        problem.nodes_explored += 1
        
        # Check if goal state reached
        if problem.is_goal(state):
            return state
        
        # Explore successors
        for action, successor in problem.get_successors(state):
            result = dfs_recursive(successor, state)
            if result is not None:
                return result
        
        return None
    
    # Start DFS from initial state
    goal_state = dfs_recursive(problem.initial_state)
    
    if goal_state is None:
        return None, problem.nodes_explored
    
    return reconstruct_path(goal_state, parent_map), problem.nodes_explored


def reconstruct_path(state, parent_map):
    """Reconstruct the path from initial state to goal state."""
    path = []
    current = state
    
    while current is not None:
        path.append(current)
        current = parent_map.get(current)
    
    return list(reversed(path))
