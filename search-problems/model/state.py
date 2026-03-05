"""
State representation for the Milk and Water Jug Problem.
"""


class State:
    """
    Represents a state in the Milk and Water Jug Problem.
    
    A state is a tuple (jug1, jug2) representing the amount of liquid in each jug.
    """
    
    def __init__(self, jug1: int, jug2: int):
        """
        Initialize a state.
        
        Args:
            jug1: Amount of liquid in jug 1
            jug2: Amount of liquid in jug 2
        """
        self.jug1 = jug1
        self.jug2 = jug2
    
    def __eq__(self, other):
        """Check equality between states."""
        if not isinstance(other, State):
            return False
        return self.jug1 == other.jug1 and self.jug2 == other.jug2
    
    def __hash__(self):
        """Make state hashable for use in sets and dicts."""
        return hash((self.jug1, self.jug2))
    
    def __repr__(self):
        """String representation of state."""
        return f"({self.jug1},{self.jug2})"
    
    def is_goal(self) -> bool:
        """Check if this state is a goal state (2 liters in either jug)."""
        return self.jug1 == 2 or self.jug2 == 2
