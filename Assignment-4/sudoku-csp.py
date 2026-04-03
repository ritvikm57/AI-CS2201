"""
pip install matplotlib requests
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.patches import FancyBboxPatch, Rectangle
import requests
from copy import deepcopy

def fetch_puzzle():
    try:
        response = requests.get("https://sudoku-api.vercel.app/api/dosuku", timeout=10)
        data = response.json()
        grid_raw = data["newboard"]["grids"][0]["value"]
        difficulty = data["newboard"]["grids"][0]["difficulty"]
        grid = [[0 if cell is None else cell for cell in row] for row in grid_raw]
        return grid, difficulty
    except Exception as e:
        print(f"Error fetching puzzle: {e}")
        return None, None

grid_initial, difficulty = fetch_puzzle()
if grid_initial is None:
    print("Failed to fetch Sudoku puzzle. Exiting.")
    exit(1)

steps = []
cell_states = {}

def record(assignment, cell, digit, event, msg):
    state_copy = deepcopy(cell_states)
    steps.append((deepcopy(assignment), state_copy, cell, digit, event, msg))

def get_constraints(row, col):
    impossible = set()
    for c in range(9):
        if assignment[row][c] != 0:
            impossible.add(assignment[row][c])
    for r in range(9):
        if assignment[r][col] != 0:
            impossible.add(assignment[r][col])
    box_row, box_col = (row // 3) * 3, (col // 3) * 3
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if assignment[r][c] != 0:
                impossible.add(assignment[r][c])
    return impossible

def get_mrv_cell():
    min_remaining = 10
    best_cell = None
    for r in range(9):
        for c in range(9):
            if assignment[r][c] == 0:
                impossible = get_constraints(r, c)
                remaining = 9 - len(impossible)
                if remaining < min_remaining:
                    min_remaining = remaining
                    best_cell = (r, c)
    return best_cell

def backtrack():
    cell = get_mrv_cell()
    if cell is None:
        return True
    row, col = cell
    impossible = get_constraints(row, col)
    for digit in range(1, 10):
        if digit not in impossible:
            assignment[row][col] = digit
            cell_states[(row, col)] = 'active'
            record(assignment, (row, col), digit, 'assign',
                   f"Assign  [R{row+1}C{col+1}] = {digit}")
            if backtrack():
                cell_states[(row, col)] = 'solved'
                return True
            assignment[row][col] = 0
            cell_states[(row, col)] = 'backtracked'
            record(assignment, (row, col), digit, 'backtrack',
                   f"Backtrack  [R{row+1}C{col+1}] ≠ {digit}")
    return False

assignment = deepcopy(grid_initial)
for r in range(9):
    for c in range(9):
        if assignment[r][c] != 0:
            cell_states[(r, c)] = 'given'

backtrack()
steps.append((deepcopy(assignment), deepcopy(cell_states), None, None, 'done', '✓  Solution found!'))

BG     = '#0F0F1A'
PANEL  = '#16162A'
BORDER = '#2A2A42'
TXT    = '#E0E0F0'
TXT2   = '#8888AA'
ACCENT = '#6C63FF'

# ── Cell colour scheme ───────────────────────
#   state          bg          text
CELL_STYLE = {
    'given':       ('#DDEEFF', '#1A1A2E'),   # soft blue bg, near-black text
    'solved':      ('#C8F5C8', '#1A3A1A'),   # soft green bg, dark green text
    'active':      ('#FFF59D', '#2A2000'),   # soft yellow bg, dark brown text
    'backtracked': ('#FFCDD2', '#3A0000'),   # soft red bg,    dark red text
    'empty':       (PANEL,     TXT2),        # dark bg, dim text (shouldn't show digits)
}

plt.rcParams.update({'font.family': 'monospace', 'text.color': TXT})

fig = plt.figure(figsize=(16, 9), facecolor=BG)

fig.text(0.5, 0.965, 'Sudoku Solver  —  CSP Backtracking with MRV Heuristic',
         ha='center', va='top', fontsize=14, color=TXT,
         fontweight='bold', fontfamily='sans-serif')
fig.text(0.5, 0.940,
         'Variables: 81 cells    |    Domain: {1-9}    |    Constraints: Alldiff(row, column, 3×3 box)',
         ha='center', va='top', fontsize=9, color=TXT2, fontfamily='sans-serif')
diff_text = fig.text(0.98, 0.965,
         f'Difficulty: {difficulty.capitalize() if difficulty else "Unknown"}',
         ha='right', va='top', fontsize=10, color=ACCENT,
         fontweight='bold', fontfamily='sans-serif')

ax_grid = fig.add_axes([0.08, 0.15, 0.50, 0.75])
ax_info = fig.add_axes([0.615, 0.50, 0.37, 0.42])
ax_cst  = fig.add_axes([0.615, 0.10, 0.37, 0.37])

for ax in [ax_grid, ax_info, ax_cst]:
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
        spine.set_linewidth(1.2)

step_idx   = [0]
stats      = {'steps': 0, 'backtracks': 0}
auto_timer = [None]

def panel_header(ax, title):
    ax.set_title(title, color=TXT2, fontsize=9, pad=7,
                 fontfamily='sans-serif', loc='left', x=0.02)

def draw_sudoku_grid(ax, sudoku_assignment, cell_states_dict, active_cell=None):
    ax.clear()
    ax.set_facecolor('#0A0A14')   # slightly darker than PANEL so grid pops
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
        spine.set_linewidth(1.2)
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 9)
    ax.set_aspect('equal')
    ax.invert_yaxis()
    ax.axis('off')

    for r in range(9):
        for c in range(9):
            digit = sudoku_assignment[r][c]
            state = cell_states_dict.get((r, c), 'empty')

            # Override state to 'active' if this is the highlighted cell
            if (r, c) == active_cell:
                state = 'active'

            bg, fg = CELL_STYLE.get(state, CELL_STYLE['empty'])

            rect = Rectangle((c, r), 1, 1, facecolor=bg, edgecolor='none')
            ax.add_patch(rect)

            if digit != 0:
                weight = 'bold' if state == 'given' else 'normal'
                size   = 15    if state == 'given' else 13
                ax.text(c + 0.5, r + 0.5, str(digit),
                        ha='center', va='center',
                        fontsize=size, fontweight=weight,
                        color=fg, fontfamily='monospace')

    # Thin cell lines
    for i in range(10):
        ax.plot([i, i], [0, 9], color='#2A2A40', linewidth=0.5)
        ax.plot([0, 9], [i, i], color='#2A2A40', linewidth=0.5)

    # Thick 3×3 box lines
    for i in range(0, 10, 3):
        ax.plot([i, i], [0, 9], color='#6060A0', linewidth=2.5)
        ax.plot([0, 9], [i, i], color='#6060A0', linewidth=2.5)

def draw_frame(idx):
    assignment_grid, cell_st, active_cell, digit, event, msg = steps[idx]

    draw_sudoku_grid(ax_grid, assignment_grid, cell_st, active_cell)
    panel_header(ax_grid, 'SUDOKU GRID')

    ev_colors = {'assign': '#4DB87A', 'backtrack': '#E8534A', 'done': '#4A9EE0'}
    ec = ev_colors.get(event, TXT2)
    ax_grid.text(0.5, -0.08, msg, transform=ax_grid.transAxes,
                 ha='center', va='top', fontsize=10, color=ec,
                 fontweight='bold', fontfamily='sans-serif')

    prog = idx / max(len(steps) - 1, 1)
    bar_ax = ax_grid.inset_axes([0.05, -0.12, 0.90, 0.025])
    bar_ax.set_xlim(0, 1); bar_ax.set_ylim(0, 1)
    bar_ax.set_facecolor('#1E1E30')
    bar_ax.add_patch(FancyBboxPatch((0, 0), prog, 1, boxstyle='square,pad=0',
                                    facecolor=ACCENT, edgecolor='none'))
    bar_ax.axis('off')
    ax_grid.text(0.02, -0.145, f'Step {idx + 1} / {len(steps)}',
                 transform=ax_grid.transAxes, ha='left', va='top',
                 fontsize=8.5, color=TXT2, fontfamily='sans-serif')

    # ── Info panel ───────────────────────────
    ax_info.clear()
    ax_info.set_facecolor(PANEL)
    for spine in ax_info.spines.values():
        spine.set_edgecolor(BORDER); spine.set_linewidth(1.2)
    ax_info.axis('off')
    panel_header(ax_info, 'CELL STATUS')

    filled    = sum(1 for r in range(9) for c in range(9) if assignment_grid[r][c] != 0)
    remaining = 81 - filled
    ax_info.text(0.5, 0.85, f'Filled: {filled} / 81',
                 transform=ax_info.transAxes, ha='center', va='center',
                 fontsize=11, color=TXT, fontweight='bold')
    ax_info.text(0.5, 0.72, f'Remaining: {remaining}',
                 transform=ax_info.transAxes, ha='center', va='center',
                 fontsize=11, color=TXT2)
    ax_info.text(0.5, 0.59, f'Steps: {stats["steps"]}   Backtracks: {stats["backtracks"]}',
                 transform=ax_info.transAxes, ha='center', va='center',
                 fontsize=9, color=TXT2)

    # Legend swatches
    legend = [
        ('given',       'Given (fixed)'),
        ('solved',      'Solved by CSP'),
        ('active',      'Currently trying'),
        ('backtracked', 'Backtracked'),
    ]
    for i, (state, label) in enumerate(legend):
        bg, fg = CELL_STYLE[state]
        y = 0.44 - i * 0.13
        ax_info.add_patch(FancyBboxPatch((0.08, y - 0.04), 0.12, 0.08,
                                          boxstyle='round,pad=0.01',
                                          facecolor=bg, edgecolor=BORDER,
                                          linewidth=0.8,
                                          transform=ax_info.transAxes))
        ax_info.text(0.14, y, 'A', transform=ax_info.transAxes,
                     ha='center', va='center', fontsize=9,
                     color=fg, fontweight='bold')
        ax_info.text(0.26, y, label, transform=ax_info.transAxes,
                     fontsize=8.5, color=TXT, va='center')

    # ── Constraint panel ─────────────────────
    ax_cst.clear()
    ax_cst.set_facecolor(PANEL)
    for spine in ax_cst.spines.values():
        spine.set_edgecolor(BORDER); spine.set_linewidth(1.2)
    ax_cst.axis('off')
    panel_header(ax_cst, 'CONSTRAINT STATUS')

    if active_cell:
        r, c = active_cell
        row_vals = [assignment_grid[r][i] for i in range(9) if assignment_grid[r][i] != 0]
        col_vals = [assignment_grid[i][c] for i in range(9) if assignment_grid[i][c] != 0]
        box_r, box_c = (r // 3) * 3, (c // 3) * 3
        box_vals = [assignment_grid[i][j]
                    for i in range(box_r, box_r+3)
                    for j in range(box_c, box_c+3)
                    if assignment_grid[i][j] != 0]
        constraints = [
            (len(row_vals) == len(set(row_vals)), f'Row {r+1}: Alldiff'),
            (len(col_vals) == len(set(col_vals)), f'Col {c+1}: Alldiff'),
            (len(box_vals) == len(set(box_vals)), f'Box [{box_r//3+1},{box_c//3+1}]: Alldiff'),
        ]
        for i, (ok, label) in enumerate(constraints):
            y2 = 0.80 - i * 0.28
            st_col = '#4DB87A' if ok else '#E8534A'
            ax_cst.text(0.12, y2, '✓' if ok else '✗',
                        transform=ax_cst.transAxes,
                        fontsize=14, color=st_col, va='center', fontweight='bold')
            ax_cst.text(0.30, y2, label,
                        transform=ax_cst.transAxes,
                        fontsize=9, color=TXT, va='center')
    else:
        ax_cst.text(0.5, 0.5, '—', transform=ax_cst.transAxes,
                    ha='center', va='center', fontsize=20, color=TXT2)

    fig.canvas.draw_idle()

def on_next(event):
    if step_idx[0] < len(steps) - 1:
        _, _, _, _, ev, _ = steps[step_idx[0]]
        if ev == 'backtrack':
            stats['backtracks'] += 1
        stats['steps'] += 1
        step_idx[0] += 1
        draw_frame(step_idx[0])

def on_prev(event):
    if step_idx[0] > 0:
        step_idx[0] -= 1
        draw_frame(step_idx[0])

def on_auto(event):
    if auto_timer[0]:
        auto_timer[0] = None
        btn_auto.label.set_text('▶  Auto')
        return
    btn_auto.label.set_text('⏸  Pause')
    def tick():
        if step_idx[0] < len(steps) - 1 and auto_timer[0]:
            on_next(None)
            fig.canvas.flush_events()
            plt.pause(0.15)
            tick()
        else:
            auto_timer[0] = None
            btn_auto.label.set_text('▶  Auto')
    auto_timer[0] = True
    tick()

def on_reset(event):
    auto_timer[0] = None
    btn_auto.label.set_text('▶  Auto')
    step_idx[0] = 0
    stats['steps'] = 0
    stats['backtracks'] = 0
    draw_frame(0)

def on_new_puzzle(event):
    global grid_initial, assignment, cell_states, steps, difficulty
    auto_timer[0] = None
    btn_auto.label.set_text('▶  Auto')
    new_grid, new_diff = fetch_puzzle()
    if new_grid is None:
        return
    grid_initial = new_grid
    difficulty   = new_diff
    assignment   = deepcopy(grid_initial)
    cell_states  = {}
    steps        = []
    for r in range(9):
        for c in range(9):
            if assignment[r][c] != 0:
                cell_states[(r, c)] = 'given'
    backtrack()
    steps.append((deepcopy(assignment), deepcopy(cell_states), None, None, 'done', '✓  Solution found!'))
    step_idx[0] = 0
    stats['steps'] = 0
    stats['backtracks'] = 0
    diff_text.set_text(f'Difficulty: {difficulty.capitalize() if difficulty else "Unknown"}')
    draw_frame(0)

BTN_FC  = '#1E1E32'
BTN_HOV = '#2A2A48'

ax_prev  = fig.add_axes([0.08, 0.015, 0.09, 0.042])
ax_next  = fig.add_axes([0.18, 0.015, 0.09, 0.042])
ax_auto  = fig.add_axes([0.28, 0.015, 0.09, 0.042])
ax_reset = fig.add_axes([0.38, 0.015, 0.09, 0.042])
ax_new   = fig.add_axes([0.48, 0.015, 0.10, 0.042])

btn_prev  = Button(ax_prev,  '◀  Prev',    color=BTN_FC, hovercolor=BTN_HOV)
btn_next  = Button(ax_next,  'Next  ▶',    color=BTN_FC, hovercolor=BTN_HOV)
btn_auto  = Button(ax_auto,  '▶  Auto',    color=BTN_FC, hovercolor=BTN_HOV)
btn_reset = Button(ax_reset, '↺  Reset',   color=BTN_FC, hovercolor=BTN_HOV)
btn_new   = Button(ax_new,   'New Puzzle', color=BTN_FC, hovercolor=BTN_HOV)

for btn in [btn_prev, btn_next, btn_auto, btn_reset, btn_new]:
    btn.label.set_color(TXT)
    btn.label.set_fontsize(9)
    btn.label.set_fontfamily('sans-serif')
    for spine in btn.ax.spines.values():
        spine.set_edgecolor(BORDER)

btn_prev.on_clicked(on_prev)
btn_next.on_clicked(on_next)
btn_auto.on_clicked(on_auto)
btn_reset.on_clicked(on_reset)
btn_new.on_clicked(on_new_puzzle)

draw_frame(0)

final_grid   = steps[-1][0]
solution_str = '\n'.join(''.join(str(d) for d in row) for row in final_grid)
print(f"\n{'='*70}")
print(f"SUDOKU - SOLUTION FOUND")
print(f"{'='*70}")
print(f"Difficulty: {difficulty}")
print(f"Total steps: {len(steps)}")
print(f"\nSolution:\n{solution_str}")
print(f"{'='*70}\n")

plt.show()