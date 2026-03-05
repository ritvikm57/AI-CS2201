"""Iterative Deepening Depth First Search (IDDFS) algorithm."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from model.state import State


def iddfs(problem):
    """IDDFS - repeats DFS with increasing depth limits, optimal + low memory."""
    problem.reset_counter()
    
    for depth_limit in range(0, 50):
        visited = set()
        parent_map = {}
        
        def dfs_limited(state, depth, parent=None):
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


def reconstruct_path(state, parent_map):
    """Trace path from initial state to goal state."""
    path = []
    current = state
    
    while current is not None:
        path.append(current)
        current = parent_map.get(current)
    
    return list(reversed(path))
