"""Depth First Search (DFS) algorithm."""

from model.state import State


def dfs(problem):
    """Depth First Search - explores deep paths first, uses minimal memory."""
    problem.reset_counter()
    
    visited = set()
    parent_map = {}
    
    def dfs_recursive(state, parent=None):
        if state in visited:
            return None
        
        visited.add(state)
        parent_map[state] = parent
        problem.nodes_explored += 1
        
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


def reconstruct_path(state, parent_map):
    """Trace path from initial state to goal state."""
    path = []
    current = state
    
    while current is not None:
        path.append(current)
        current = parent_map.get(current)
    
    return list(reversed(path))
