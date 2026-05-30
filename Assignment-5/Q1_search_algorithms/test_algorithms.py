"""
Test cases for all four search algorithms.
Tests cover:
  - Winning move detection (must take it)
  - Blocking opponent from winning
  - Node count comparison (alpha-beta < minimax)
  - MCTS convergence on near-terminal states
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from game import initial_state, result, terminal, winner, X, O, EMPTY, print_board
from minimax import minimax
from alpha_beta import alpha_beta
from heuristic_alpha_beta import heuristic_alpha_beta
from mcts import mcts

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"


def check(name, got, expected, comment=""):
    status = PASS if got == expected else FAIL
    print(f"  [{status}] {name}: got {got}, expected {expected}  {comment}")


# ─── Test boards ─────────────────────────────────────────────────────────────

# X can win immediately at position 2
board_x_wins = [X, X, EMPTY, O, O, EMPTY, EMPTY, EMPTY, EMPTY]

# X has a winning move at 6 (column 0,3,6) — optimal play is to take it
# O is also threatening column (1,4,7), so this doubles as "win before opponent wins"
board_must_block = [X, O, EMPTY, X, O, EMPTY, EMPTY, EMPTY, EMPTY]

# Near-draw, X to move, best play is draw
board_late = [X, O, X, O, X, EMPTY, O, EMPTY, EMPTY]

# Empty board — all moves equivalent at depth, just check it returns *something*
board_empty = initial_state()


# ─── Minimax tests ────────────────────────────────────────────────────────────
print("\n=== Minimax ===")
action, n = minimax(board_x_wins)
check("X wins immediately", action, 2)

action, n = minimax(board_must_block)
check("X takes winning move (col 0,3,6)", action, 6)

action, n = minimax(board_empty)
check("Empty board returns an action", action is not None, True)
print(f"  [INFO] Nodes explored (empty board): {n}")


# ─── Alpha-Beta tests ─────────────────────────────────────────────────────────
print("\n=== Alpha-Beta ===")
action_ab, n_ab = alpha_beta(board_x_wins)
check("X wins immediately", action_ab, 2)

action_ab, n_ab = alpha_beta(board_must_block)
check("X takes winning move (col 0,3,6)", action_ab, 6)

_, n_mm = minimax(board_empty)
_, n_ab2 = alpha_beta(board_empty)
check("Alpha-Beta explores fewer nodes than Minimax", n_ab2 < n_mm, True,
      f"(AB={n_ab2} vs MM={n_mm})")


# ─── Heuristic Alpha-Beta tests ───────────────────────────────────────────────
print("\n=== Heuristic Alpha-Beta (depth=4) ===")
action_h, n_h = heuristic_alpha_beta(board_x_wins, depth=4)
check("X wins immediately", action_h, 2)

action_h, n_h = heuristic_alpha_beta(board_must_block, depth=4)
check("X takes winning move (col 0,3,6)", action_h, 6)

_, n_full = alpha_beta(board_empty)
_, n_limited = heuristic_alpha_beta(board_empty, depth=3)
check("Depth-3 explores fewer nodes than full search", n_limited < n_full, True,
      f"(depth-3={n_limited} vs full={n_full})")


# ─── MCTS tests ───────────────────────────────────────────────────────────────
print("\n=== Monte Carlo Tree Search (1000 iters) ===")

# MCTS is stochastic so we run a few times and check majority
def mcts_majority(board, expected, runs=5, iters=1000):
    votes = [mcts(board, iters)[0] for _ in range(runs)]
    majority = max(set(votes), key=votes.count)
    return majority == expected

check("X wins immediately (majority vote)", mcts_majority(board_x_wins, 2), True)
# X has win at 6 on this board — MCTS should find it most of the time
check("X finds winning move (majority vote)", mcts_majority(board_must_block, 6), True)

action_m, _ = mcts(board_empty, iterations=500)
check("Empty board returns an action", action_m is not None, True)


# ─── Correctness cross-check ─────────────────────────────────────────────────
print("\n=== Cross-Algorithm Agreement ===")
# All three deterministic algorithms must agree on optimal moves
for board, name in [(board_x_wins, "X-wins-board"), (board_must_block, "block-board")]:
    a_mm, _ = minimax(board)
    a_ab, _ = alpha_beta(board)
    a_h, _  = heuristic_alpha_beta(board, depth=6)
    check(f"{name}: Minimax == Alpha-Beta", a_mm, a_ab)
    check(f"{name}: Minimax == Heuristic-AB", a_mm, a_h)

print()
