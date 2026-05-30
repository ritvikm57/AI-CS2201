"""
Alpha-Beta Pruning Search
Same result as Minimax but prunes branches that cannot affect the outcome.
Alpha = best already found for MAX (lower bound)
Beta  = best already found for MIN (upper bound)
When alpha >= beta, the current branch is pruned.
"""

from game import terminal, utility, actions, result, player, X

nodes_explored = 0


def alpha_beta_value(board, alpha, beta, is_maximizing):
    global nodes_explored
    nodes_explored += 1

    if terminal(board):
        return utility(board)

    if is_maximizing:
        val = float('-inf')
        for action in actions(board):
            val = max(val, alpha_beta_value(result(board, action), alpha, beta, False))
            alpha = max(alpha, val)
            if alpha >= beta:
                break  # beta cutoff — MIN won't allow this branch
        return val
    else:
        val = float('inf')
        for action in actions(board):
            val = min(val, alpha_beta_value(result(board, action), alpha, beta, True))
            beta = min(beta, val)
            if alpha >= beta:
                break  # alpha cutoff — MAX won't allow this branch
        return val


def alpha_beta(board):
    """Returns optimal action with alpha-beta pruning."""
    global nodes_explored
    nodes_explored = 0

    current = player(board)
    best_action = None

    if current == X:
        best_val = float('-inf')
        for action in actions(board):
            val = alpha_beta_value(result(board, action), float('-inf'), float('inf'), False)
            if val > best_val:
                best_val = val
                best_action = action
    else:
        best_val = float('inf')
        for action in actions(board):
            val = alpha_beta_value(result(board, action), float('-inf'), float('inf'), True)
            if val < best_val:
                best_val = val
                best_action = action

    return best_action, nodes_explored
