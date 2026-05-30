"""
Monte Carlo Tree Search (MCTS)
Four phases: Selection, Expansion, Simulation (rollout), Backpropagation.

UCB1 formula used for selection:
  UCB1 = (wins / visits) + C * sqrt(ln(parent_visits) / visits)
where C is the exploration constant (typically sqrt(2)).
"""

import math
import random
from game import terminal, utility, actions, result, player, X, EMPTY


class MCTSNode:
    def __init__(self, board, parent=None, action=None):
        self.board = board
        self.parent = parent
        self.action = action       # action that led to this state
        self.children = []
        self.visits = 0
        self.wins = 0.0
        self.untried_actions = actions(board)

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def best_child(self, c=math.sqrt(2)):
        """UCB1 selection."""
        return max(
            self.children,
            key=lambda n: (n.wins / n.visits) + c * math.sqrt(math.log(self.visits) / n.visits)
        )

    def expand(self):
        action = self.untried_actions.pop(random.randrange(len(self.untried_actions)))
        child_board = result(self.board, action)
        child = MCTSNode(child_board, parent=self, action=action)
        self.children.append(child)
        return child

    def update(self, reward):
        self.visits += 1
        self.wins += reward


def rollout(board):
    """Random rollout until terminal state."""
    while not terminal(board):
        move = random.choice(actions(board))
        board = result(board, move)
    return utility(board)


def mcts(board, iterations=1000):
    """
    Runs MCTS for the given number of iterations and returns the best action.
    Rewards are from X's perspective (X=+1, O=-1, draw=0).
    """
    root = MCTSNode(board)
    root_player = player(board)

    for _ in range(iterations):
        # 1. Selection
        node = root
        while not terminal(node.board) and node.is_fully_expanded():
            node = node.best_child()

        # 2. Expansion
        if not terminal(node.board) and not node.is_fully_expanded():
            node = node.expand()

        # 3. Simulation
        reward = rollout(node.board)

        # 4. Backpropagation
        while node is not None:
            # flip reward if this node was played by O (we store wins from X's view)
            node.update(reward)
            node = node.parent

    # Pick child with highest visit count (most robust)
    best = max(root.children, key=lambda n: n.visits)
    return best.action, iterations
