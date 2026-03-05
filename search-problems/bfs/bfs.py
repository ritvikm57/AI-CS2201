"""Breadth First Search (BFS) algorithm."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from collections import deque
from model.state import State


def bfs(problem):
    """Breadth First Search - explores level by level, guarantees shortest path."""
    problem.reset_counter()
    
    frontier = deque([problem.initial_state])
    visited = {problem.initial_state}
    parent_map = {problem.initial_state: None}
    
    while frontier:
        state = frontier.popleft()
        problem.nodes_explored += 1
        
        if problem.is_goal(state):
            return reconstruct_path(state, parent_map), problem.nodes_explored
        
        for action, successor in problem.get_successors(state):
            if successor not in visited:
                visited.add(successor)
                parent_map[successor] = state
                frontier.append(successor)
    
    return None, problem.nodes_explored


def reconstruct_path(state, parent_map):
    """Trace path from initial state to goal state."""
    path = []
    current = state
    
    while current is not None:
        path.append(current)
        current = parent_map[current]
    
    return list(reversed(path))
