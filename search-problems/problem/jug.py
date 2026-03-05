"""
Implementation of the Milk and Water Jug Problem.

Problem:
- Jug 1 capacity: 4 liters
- Jug 2 capacity: 3 liters
- Initial state: (0, 0)
- Goal: Measure exactly 2 liters in one of the jugs

Allowed operations:
1. Fill Jug 1
2. Fill Jug 2
3. Empty Jug 1
4. Empty Jug 2
5. Pour Jug 1 -> Jug 2
6. Pour Jug 2 -> Jug 1
"""

from model.state import State


class JugProblem:
    """Implementation of the Milk and Water Jug Problem."""
    
    JUG1_CAPACITY = 4
    JUG2_CAPACITY = 3
    GOAL_AMOUNT = 2
    
    def __init__(self):
        """Initialize the jug problem."""
        self.initial_state = State(0, 0)
        self.nodes_explored = 0
    
    def is_goal(self, state: State) -> bool:
        """Check if state is a goal state."""
        return state.is_goal()
    
    def get_successors(self, state: State) -> list:
        """
        Generate all successor states from the given state.
        
        Returns a list of (action, successor_state) tuples.
        """
        successors = []
        
        # 1. Fill Jug 1
        if state.jug1 < self.JUG1_CAPACITY:
            successors.append(("Fill Jug 1", State(self.JUG1_CAPACITY, state.jug2)))
        
        # 2. Fill Jug 2
        if state.jug2 < self.JUG2_CAPACITY:
            successors.append(("Fill Jug 2", State(state.jug1, self.JUG2_CAPACITY)))
        
        # 3. Empty Jug 1
        if state.jug1 > 0:
            successors.append(("Empty Jug 1", State(0, state.jug2)))
        
        # 4. Empty Jug 2
        if state.jug2 > 0:
            successors.append(("Empty Jug 2", State(state.jug1, 0)))
        
        # 5. Pour Jug 1 -> Jug 2
        if state.jug1 > 0 and state.jug2 < self.JUG2_CAPACITY:
            # Amount to pour is minimum of: jug1 content and jug2 remaining capacity
            amount = min(state.jug1, self.JUG2_CAPACITY - state.jug2)
            new_jug1 = state.jug1 - amount
            new_jug2 = state.jug2 + amount
            successors.append(("Pour Jug 1 -> Jug 2", State(new_jug1, new_jug2)))
        
        # 6. Pour Jug 2 -> Jug 1
        if state.jug2 > 0 and state.jug1 < self.JUG1_CAPACITY:
            # Amount to pour is minimum of: jug2 content and jug1 remaining capacity
            amount = min(state.jug2, self.JUG1_CAPACITY - state.jug1)
            new_jug1 = state.jug1 + amount
            new_jug2 = state.jug2 - amount
            successors.append(("Pour Jug 2 -> Jug 1", State(new_jug1, new_jug2)))
        
        return successors
    
    def reset_counter(self):
        """Reset the nodes explored counter."""
        self.nodes_explored = 0
