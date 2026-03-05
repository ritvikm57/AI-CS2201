"""State representation for the Milk and Water Jug Problem."""


class State:
    """Represents a state in the Milk and Water Jug Problem as (jug1, jug2)."""
    
    def __init__(self, jug1: int, jug2: int):
        self.jug1 = jug1
        self.jug2 = jug2
    
    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.jug1 == other.jug1 and self.jug2 == other.jug2
    
    def __hash__(self):
        return hash((self.jug1, self.jug2))
    
    def __repr__(self):
        return f"({self.jug1},{self.jug2})"
    
    def is_goal(self) -> bool:
        return self.jug1 == 2 or self.jug2 == 2
