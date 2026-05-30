"""
Tic-Tac-Toe game environment used to test all search algorithms.
Board is represented as a list of 9 values: 'X', 'O', or ' ' (empty).
Positions:
  0 | 1 | 2
  3 | 4 | 5
  6 | 7 | 8
"""

EMPTY = ' '
X = 'X'
O = 'O'

WIN_LINES = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # cols
    [0, 4, 8], [2, 4, 6]              # diagonals
]


def initial_state():
    return [EMPTY] * 9


def player(board):
    """Returns whose turn it is (X always goes first)."""
    xs = board.count(X)
    os = board.count(O)
    return X if xs == os else O


def actions(board):
    """Returns list of available moves (indices of empty cells)."""
    return [i for i, v in enumerate(board) if v == EMPTY]


def result(board, action):
    """Returns new board after applying action."""
    b = board[:]
    b[action] = player(board)
    return b


def winner(board):
    """Returns winner ('X' or 'O') or None."""
    for line in WIN_LINES:
        vals = [board[i] for i in line]
        if vals[0] != EMPTY and vals[0] == vals[1] == vals[2]:
            return vals[0]
    return None


def terminal(board):
    """Returns True if the game is over."""
    return winner(board) is not None or EMPTY not in board


def utility(board):
    """Returns +1 if X wins, -1 if O wins, 0 for draw."""
    w = winner(board)
    if w == X:
        return 1
    elif w == O:
        return -1
    return 0


def print_board(board):
    rows = []
    for r in range(3):
        row = ' | '.join(board[r*3:(r+1)*3])
        rows.append(' ' + row)
    print('\n-----------\n'.join(rows))
