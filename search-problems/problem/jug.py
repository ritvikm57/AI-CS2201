"""Milk and Water Jug Problem implementation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from model.state import State


class JugProblem:
    """Milk and Water Jug Problem: reach state with 2 liters in either jug."""
    
    JUG1_CAPACITY = 4
    JUG2_CAPACITY = 3
    GOAL_AMOUNT = 2
    
    def __init__(self):
        self.initial_state = State(0, 0)
        self.nodes_explored = 0
    
    def is_goal(self, state: State) -> bool:
        return state.is_goal()
    
    def get_successors(self, state: State) -> list:
        """Generate successor states from allowed operations."""
        successors = []
        
        if state.jug1 < self.JUG1_CAPACITY:
            successors.append(("Fill Jug 1", State(self.JUG1_CAPACITY, state.jug2)))
        
        if state.jug2 < self.JUG2_CAPACITY:
            successors.append(("Fill Jug 2", State(state.jug1, self.JUG2_CAPACITY)))
        
        if state.jug1 > 0:
            successors.append(("Empty Jug 1", State(0, state.jug2)))
        
        if state.jug2 > 0:
            successors.append(("Empty Jug 2", State(state.jug1, 0)))
        
        if state.jug1 > 0 and state.jug2 < self.JUG2_CAPACITY:
            amount = min(state.jug1, self.JUG2_CAPACITY - state.jug2)
            new_jug1 = state.jug1 - amount
            new_jug2 = state.jug2 + amount
            successors.append(("Pour Jug 1 -> Jug 2", State(new_jug1, new_jug2)))
        
        if state.jug2 > 0 and state.jug1 < self.JUG1_CAPACITY:
            amount = min(state.jug2, self.JUG1_CAPACITY - state.jug1)
            new_jug1 = state.jug1 + amount
            new_jug2 = state.jug2 - amount
            successors.append(("Pour Jug 2 -> Jug 1", State(new_jug1, new_jug2)))
        
        return successors
    
    def reset_counter(self):
        self.nodes_explored = 0
