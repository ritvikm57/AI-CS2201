"""
Heuristic Alpha-Beta Search (Depth-Limited)
Extends alpha-beta with a depth limit. When the limit is reached,
an evaluation function estimates the position value instead of searching further.
This makes it usable for games too large to solve exactly (like Chess or Connect-4).
"""

from game import terminal, utility, actions, result, player, X, O, EMPTY, WIN_LINES

nodes_explored = 0


def evaluate(board):
    """
    Heuristic evaluation of a non-terminal board state.
    Counts 'threats' — lines where one player can still win.

    Score breakdown:
      +10  for X having 2 in a line with the third cell empty
      -10  for O having 2 in a line with the third cell empty
      +3   for X having 1 in a line (all others empty)
      -3   for O having 1 in a line (all others empty)
    """
    score = 0
    for line in WIN_LINES:
        vals = [board[i] for i in line]
        xs = vals.count(X)
        os = vals.count(O)
        if os == 0:  # X can still win this line
            if xs == 2:
                score += 10
            elif xs == 1:
                score += 3
        if xs == 0:  # O can still win this line
            if os == 2:
                score -= 10
            elif os == 1:
                score -= 3
    return score


def h_alpha_beta_value(board, depth, alpha, beta, is_maximizing):
    global nodes_explored
    nodes_explored += 1

    if terminal(board):
        return utility(board) * 100  # scale so terminal wins outweigh heuristic scores

    if depth == 0:
        return evaluate(board)

    if is_maximizing:
        val = float('-inf')
        for action in actions(board):
            val = max(val, h_alpha_beta_value(result(board, action), depth - 1, alpha, beta, False))
            alpha = max(alpha, val)
            if alpha >= beta:
                break
        return val
    else:
        val = float('inf')
        for action in actions(board):
            val = min(val, h_alpha_beta_value(result(board, action), depth - 1, alpha, beta, True))
            beta = min(beta, val)
            if alpha >= beta:
                break
        return val


def heuristic_alpha_beta(board, depth=4):
    """Returns best action found within the given depth limit."""
    global nodes_explored
    nodes_explored = 0

    current = player(board)
    best_action = None

    if current == X:
        best_val = float('-inf')
        for action in actions(board):
            val = h_alpha_beta_value(result(board, action), depth - 1, float('-inf'), float('inf'), False)
            if val > best_val:
                best_val = val
                best_action = action
    else:
        best_val = float('inf')
        for action in actions(board):
            val = h_alpha_beta_value(result(board, action), depth - 1, float('-inf'), float('inf'), True)
            if val < best_val:
                best_val = val
                best_action = action

    return best_action, nodes_explored
