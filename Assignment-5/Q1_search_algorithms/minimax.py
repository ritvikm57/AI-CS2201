"""
Minimax Search Algorithm
Performs exhaustive game-tree search, assuming both players play optimally.
X is the maximising player, O is the minimising player.
"""

from game import terminal, utility, actions, result, player, X

nodes_explored = 0


def minimax_value(board, is_maximizing):
    global nodes_explored
    nodes_explored += 1

    if terminal(board):
        return utility(board)

    if is_maximizing:
        best = float('-inf')
        for action in actions(board):
            val = minimax_value(result(board, action), False)
            best = max(best, val)
        return best
    else:
        best = float('inf')
        for action in actions(board):
            val = minimax_value(result(board, action), True)
            best = min(best, val)
        return best


def minimax(board):
    """
    Returns the optimal action for the current player.
    X maximises, O minimises.
    """
    global nodes_explored
    nodes_explored = 0

    current = player(board)
    best_action = None

    if current == X:
        best_val = float('-inf')
        for action in actions(board):
            val = minimax_value(result(board, action), False)
            if val > best_val:
                best_val = val
                best_action = action
    else:
        best_val = float('inf')
        for action in actions(board):
            val = minimax_value(result(board, action), True)
            if val < best_val:
                best_val = val
                best_action = action

    return best_action, nodes_explored
