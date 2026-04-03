"""
pip install matplotlib
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.patches import FancyBboxPatch
from copy import deepcopy
import sys

# ─────────────────────────────────────────────
# CSP Solver — column-by-column variable order
# O, C1, R  →  column 1 constraints fire immediately
# W, C2, U  →  column 2 constraints fire immediately
# T, C3, F  →  column 3 constraints fire immediately
# Result: 1,739 steps instead of 2,813,932
# ─────────────────────────────────────────────
steps = []
VARIABLES   = ['O', 'C1', 'R', 'W', 'C2', 'U', 'T', 'C3', 'F']
LETTER_VARS = ['T', 'W', 'O', 'F', 'U', 'R']
CARRY_VARS  = ['C1', 'C2', 'C3']
sys.setrecursionlimit(10000)

def record(assignment, var, event, msg):
    steps.append((dict(assignment), var, event, msg))

def check_constraints(assignment):
    # Alldiff on letters assigned so far
    vals = [assignment[v] for v in LETTER_VARS if v in assignment]
    if len(vals) != len(set(vals)):
        return False
    # No leading zeros
    if assignment.get('T') == 0 or assignment.get('F') == 0:
        return False
    # Column 1: O + O = R + 10*C1
    if all(v in assignment for v in ['O', 'R', 'C1']):
        if assignment['O'] * 2 != assignment['R'] + 10 * assignment['C1']:
            return False
    # Column 2: C1 + W + W = U + 10*C2
    if all(v in assignment for v in ['C1', 'W', 'U', 'C2']):
        if assignment['C1'] + assignment['W'] * 2 != assignment['U'] + 10 * assignment['C2']:
            return False
    # Column 3: C2 + T + T = O + 10*C3
    if all(v in assignment for v in ['C2', 'T', 'O', 'C3']):
        if assignment['C2'] + assignment['T'] * 2 != assignment['O'] + 10 * assignment['C3']:
            return False
    # C3 = F
    if 'C3' in assignment and 'F' in assignment:
        if assignment['C3'] != assignment['F']:
            return False
    return True

def get_domain(var, assignment):
    if var in CARRY_VARS:
        return [0, 1]
    used   = {assignment[v] for v in LETTER_VARS if v in assignment}
    domain = [d for d in range(10) if d not in used]
    if var in ['T', 'F']:
        domain = [d for d in domain if d != 0]
    return domain

def backtrack(assignment):
    if len(assignment) == len(VARIABLES):
        return check_constraints(assignment)
    var = next(v for v in VARIABLES if v not in assignment)
    for val in get_domain(var, assignment):
        assignment[var] = val
        record(assignment, var, 'assign', f"Assign  {var} = {val}")
        if check_constraints(assignment):
            if backtrack(assignment):
                return True
        del assignment[var]
        record(assignment, var, 'backtrack', f"Backtrack  {var} ≠ {val}")
    return False

backtrack({})
steps.append((steps[-1][0], None, 'done', '✓  Solution found!'))

# ─────────────────────────────────────────────
# Figure Layout
# ─────────────────────────────────────────────
BG     = '#0F0F1A'
PANEL  = '#16162A'
BORDER = '#2A2A42'
TXT    = '#E0E0F0'
TXT2   = '#8888AA'
ACCENT = '#6C63FF'

plt.rcParams.update({'font.family': 'monospace', 'text.color': TXT})

fig = plt.figure(figsize=(16, 9), facecolor=BG)

fig.text(0.5, 0.965, 'Cryptarithmetic Puzzle  —  TWO + TWO = FOUR',
         ha='center', va='top', fontsize=14, color=TXT,
         fontweight='bold', fontfamily='sans-serif')
fig.text(0.5, 0.940,
         'Variables: T,W,O,F,U,R ∈ {0..9} | C1,C2,C3 ∈ {0,1}    |    Constraints: Alldiff + Column equations + No leading zeros',
         ha='center', va='top', fontsize=9, color=TXT2, fontfamily='sans-serif')

ax_puzzle = fig.add_axes([0.05, 0.12, 0.52, 0.78])
ax_info   = fig.add_axes([0.625, 0.50, 0.35, 0.42])
ax_cst    = fig.add_axes([0.625, 0.10, 0.35, 0.37])

for ax in [ax_puzzle, ax_info, ax_cst]:
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

# ─────────────────────────────────────────────
# Draw Puzzle
# Fixed layout — all columns evenly spaced
#
#         C3  C2  C1       (carry row, small)
#          T   W   O       (row 1)
#       +  T   W   O       (row 2)
#        ─────────────
#         F   O   U   R    (result row)
# ─────────────────────────────────────────────
def draw_puzzle(ax, assignment):
    ax.clear()
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER); spine.set_linewidth(1.2)

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    panel_header(ax, 'PUZZLE')

    # Column x positions: 4 columns for FOUR (F O U R)
    # TWO is right-aligned to match O U R columns
    #   col:   F    O    U    R
    #   x:     3    5    7    9
    #   TWO:        T    W    O  → x: 5-2=3? no, TWO right-aligns O→9, W→7, T→5... wait
    # Right-align TWO with FOUR:
    #   R col x=8, O col x=6, U col x=4, F col x=2
    #   TWO: O→8, W→6, T→4   (right-aligned with FOUR's R,U,O)

    col = {'F': 2, 'O_res': 4, 'U': 6, 'R': 8,   # FOUR positions
           'T': 4, 'W': 6, 'O': 8}                # TWO positions (right-aligned)

    ROW_TWO1  = 7.5   # first TWO
    ROW_TWO2  = 5.5   # second TWO (after +)
    ROW_SEP   = 4.2   # separator line
    ROW_FOUR  = 2.8   # FOUR result
    ROW_CARRY = 8.8   # carry digits

    def cell(ax, x, y, var, result_var=False, small=False):
        """Draw one letter/digit cell"""
        key = var if not result_var else var  # same key
        val = assignment.get(var)
        val_str = str(val) if val is not None else var
        assigned = val is not None
        color = TXT if assigned else TXT2
        size  = 10 if small else 22
        weight = 'bold' if assigned else 'normal'
        ax.text(x, y, val_str, ha='center', va='center',
                fontsize=size, fontweight=weight, color=color,
                fontfamily='monospace')

    # Carry digits (small, accent color)
    for carry_var, x in [('C3', col['T']-1.5), ('C2', col['T']), ('C1', col['W'])]:
        val = assignment.get(carry_var)
        val_str = f"[{val}]" if val is not None else f"[{carry_var}]"
        color = ACCENT if val is not None else TXT2
        ax.text(x, ROW_CARRY, val_str, ha='center', va='center',
                fontsize=9, color=color, fontweight='bold')

    # TWO row 1
    for var, x in [('T', col['T']), ('W', col['W']), ('O', col['O'])]:
        cell(ax, x, ROW_TWO1, var)

    # + sign and TWO row 2
    ax.text(col['T'] - 2, ROW_TWO2, '+', ha='center', va='center',
            fontsize=24, color=TXT, fontweight='bold')
    for var, x in [('T', col['T']), ('W', col['W']), ('O', col['O'])]:
        cell(ax, x, ROW_TWO2, var)

    # Separator line
    ax.plot([col['F'] - 0.6, col['R'] + 0.6], [ROW_SEP, ROW_SEP],
            color='#6060A0', linewidth=2.5)

    # FOUR row — F,O,U,R each at their own column
    for var, x in [('F', col['F']), ('O', col['O_res']), ('U', col['U']), ('R', col['R'])]:
        cell(ax, x, ROW_FOUR, var)

    # Solution banner at bottom when done
    if all(v in assignment for v in LETTER_VARS):
        T = assignment['T']; W = assignment['W']; O = assignment['O']
        F = assignment['F']; U = assignment['U']; R = assignment['R']
        TWO  = T * 100 + W * 10 + O
        FOUR = F * 1000 + O * 100 + U * 10 + R
        ax.text(5, 1.2, f"TWO = {TWO}   |   {TWO} + {TWO} = {FOUR}",
                ha='center', va='center', fontsize=13,
                color='#4A9EE0', fontweight='bold', fontfamily='sans-serif')

# ─────────────────────────────────────────────
# Constraint status helper
# ─────────────────────────────────────────────
def get_constraint_status(name, assignment):
    if name == 'col1':
        if all(v in assignment for v in ['O', 'R', 'C1']):
            lhs = assignment['O'] * 2
            rhs = assignment['R'] + 10 * assignment['C1']
            return lhs == rhs, f"O+O = {lhs}  vs  R+10·C1 = {rhs}"
        return None, 'O + O = R + 10·C1'
    elif name == 'col2':
        if all(v in assignment for v in ['C1', 'W', 'U', 'C2']):
            lhs = assignment['C1'] + assignment['W'] * 2
            rhs = assignment['U'] + 10 * assignment['C2']
            return lhs == rhs, f"C1+W+W = {lhs}  vs  U+10·C2 = {rhs}"
        return None, 'C1 + W + W = U + 10·C2'
    elif name == 'col3':
        if all(v in assignment for v in ['C2', 'T', 'O', 'C3']):
            lhs = assignment['C2'] + assignment['T'] * 2
            rhs = assignment['O'] + 10 * assignment['C3']
            return lhs == rhs, f"C2+T+T = {lhs}  vs  O+10·C3 = {rhs}"
        return None, 'C2 + T + T = O + 10·C3'
    elif name == 'c3f':
        if 'C3' in assignment and 'F' in assignment:
            ok = assignment['C3'] == assignment['F']
            return ok, f"C3={assignment['C3']}  vs  F={assignment['F']}"
        return None, 'C3 = F'
    return None, '—'

# ─────────────────────────────────────────────
# Draw Frame
# ─────────────────────────────────────────────
def draw_frame(idx):
    assignment, hl_var, event, msg = steps[idx]

    draw_puzzle(ax_puzzle, assignment)

    ev_colors = {'assign': '#4DB87A', 'backtrack': '#E8534A', 'done': '#4A9EE0'}
    ec = ev_colors.get(event, TXT2)
    ax_puzzle.text(0.5, 0.04, msg, transform=ax_puzzle.transAxes,
                   ha='center', va='bottom', fontsize=11, color=ec,
                   fontweight='bold', fontfamily='sans-serif')

    prog = idx / max(len(steps) - 1, 1)
    bar_ax = ax_puzzle.inset_axes([0.05, 0.005, 0.90, 0.018])
    bar_ax.set_xlim(0, 1); bar_ax.set_ylim(0, 1)
    bar_ax.set_facecolor('#1E1E30')
    bar_ax.add_patch(FancyBboxPatch((0, 0), prog, 1, boxstyle='square,pad=0',
                                    facecolor=ACCENT, edgecolor='none'))
    bar_ax.axis('off')
    ax_puzzle.text(0.02, 0.975, f'Step {idx + 1} / {len(steps)}',
                   transform=ax_puzzle.transAxes, ha='left', va='top',
                   fontsize=8.5, color=TXT2, fontfamily='sans-serif')
    ax_puzzle.text(0.98, 0.975,
                   f'Steps: {stats["steps"]}   Backtracks: {stats["backtracks"]}',
                   transform=ax_puzzle.transAxes, ha='right', va='top',
                   fontsize=8.5, color=TXT2, fontfamily='sans-serif')

    # ── Info panel ───────────────────────────
    ax_info.clear()
    ax_info.set_facecolor(PANEL)
    for spine in ax_info.spines.values():
        spine.set_edgecolor(BORDER); spine.set_linewidth(1.2)
    ax_info.axis('off')
    panel_header(ax_info, 'VARIABLE ASSIGNMENTS')

    ax_info.text(0.5, 0.94, 'Letters', transform=ax_info.transAxes,
                 fontsize=9, color=TXT2, ha='center', fontweight='bold')
    for i, var in enumerate(LETTER_VARS):
        y     = 0.82 - i * 0.115
        val   = assignment.get(var)
        is_hl = var == hl_var
        col   = ('#4DB87A' if event == 'assign' else '#E8534A') if is_hl else (TXT if val is not None else TXT2)
        ax_info.text(0.15, y, var, transform=ax_info.transAxes,
                     fontsize=11, color=ACCENT if is_hl else TXT, va='center', fontweight='bold')
        ax_info.text(0.38, y, '→', transform=ax_info.transAxes, fontsize=9, color=TXT2, va='center')
        ax_info.text(0.52, y, str(val) if val is not None else '—',
                     transform=ax_info.transAxes, fontsize=11, color=col, va='center',
                     fontweight='bold' if val is not None else 'normal')

    ax_info.text(0.5, 0.16, 'Carry digits', transform=ax_info.transAxes,
                 fontsize=9, color=TXT2, ha='center', fontweight='bold')
    for i, var in enumerate(CARRY_VARS):
        y   = 0.08 - i * 0.10
        val = assignment.get(var)
        ax_info.text(0.15, y, var, transform=ax_info.transAxes,
                     fontsize=9, color=ACCENT, va='center', fontweight='bold')
        ax_info.text(0.38, y, '→', transform=ax_info.transAxes, fontsize=8, color=TXT2, va='center')
        ax_info.text(0.52, y, str(val) if val is not None else '—',
                     transform=ax_info.transAxes, fontsize=9,
                     color=TXT if val is not None else TXT2, va='center',
                     fontweight='bold' if val is not None else 'normal')

    # ── Constraint panel ─────────────────────
    ax_cst.clear()
    ax_cst.set_facecolor(PANEL)
    for spine in ax_cst.spines.values():
        spine.set_edgecolor(BORDER); spine.set_linewidth(1.2)
    ax_cst.axis('off')
    panel_header(ax_cst, 'COLUMN CONSTRAINTS')

    cst_defs = [
        ('col1', 'O + O = R + 10·C1'),
        ('col2', 'C1 + W + W = U + 10·C2'),
        ('col3', 'C2 + T + T = O + 10·C3'),
        ('c3f',  'C3 = F'),
    ]
    for i, (name, label) in enumerate(cst_defs):
        y3 = 0.85 - i * 0.22
        status, detail = get_constraint_status(name, assignment)
        if status is None:
            sym, sc, bg = '◯', TXT2, PANEL
        elif status:
            sym, sc, bg = '✓', '#4DB87A', '#1E3A2A'
        else:
            sym, sc, bg = '✗', '#E8534A', '#3A1E1E'

        ax_cst.add_patch(FancyBboxPatch((0.04, y3 - 0.09), 0.92, 0.17,
                                         boxstyle='round,pad=0.01',
                                         facecolor=bg, edgecolor='none',
                                         transform=ax_cst.transAxes))
        ax_cst.text(0.10, y3, sym, transform=ax_cst.transAxes,
                    fontsize=12, color=sc, va='center', fontweight='bold')
        ax_cst.text(0.22, y3 + 0.04, label, transform=ax_cst.transAxes,
                    fontsize=8, color=TXT, va='center')
        ax_cst.text(0.22, y3 - 0.04, detail, transform=ax_cst.transAxes,
                    fontsize=7, color=TXT2, va='center', fontfamily='monospace')

    fig.canvas.draw_idle()

# ─────────────────────────────────────────────
# Buttons
# ─────────────────────────────────────────────
def on_next(event):
    if step_idx[0] < len(steps) - 1:
        _, _, ev, _ = steps[step_idx[0]]
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
            plt.pause(0.02)
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

BTN_FC  = '#1E1E32'
BTN_HOV = '#2A2A48'

ax_prev  = fig.add_axes([0.08,  0.015, 0.10, 0.042])
ax_next  = fig.add_axes([0.191, 0.015, 0.10, 0.042])
ax_auto  = fig.add_axes([0.302, 0.015, 0.10, 0.042])
ax_reset = fig.add_axes([0.413, 0.015, 0.10, 0.042])

btn_prev  = Button(ax_prev,  '◀  Prev',  color=BTN_FC, hovercolor=BTN_HOV)
btn_next  = Button(ax_next,  'Next  ▶',  color=BTN_FC, hovercolor=BTN_HOV)
btn_auto  = Button(ax_auto,  '▶  Auto',  color=BTN_FC, hovercolor=BTN_HOV)
btn_reset = Button(ax_reset, '↺  Reset', color=BTN_FC, hovercolor=BTN_HOV)

for btn in [btn_prev, btn_next, btn_auto, btn_reset]:
    btn.label.set_color(TXT)
    btn.label.set_fontsize(10)
    btn.label.set_fontfamily('sans-serif')
    for spine in btn.ax.spines.values():
        spine.set_edgecolor(BORDER)

btn_prev.on_clicked(on_prev)
btn_next.on_clicked(on_next)
btn_auto.on_clicked(on_auto)
btn_reset.on_clicked(on_reset)

# ─────────────────────────────────────────────
# Launch
# ─────────────────────────────────────────────
draw_frame(0)

final = steps[-1][0]
T,W,O,F,U,R = [final[v] for v in LETTER_VARS]
TWO  = T*100 + W*10 + O
FOUR = F*1000 + O*100 + U*10 + R
print(f"\n{'='*70}")
print(f"CRYPTARITHMETIC - SOLUTION FOUND")
print(f"{'='*70}")
print(f"TWO = {TWO}")
print(f"{TWO} + {TWO} = {FOUR}")
print(f"T={T}, W={W}, O={O}, F={F}, U={U}, R={R}")
print(f"C1={final['C1']}, C2={final['C2']}, C3={final['C3']}")
print(f"Total steps: {len(steps)}")
print(f"{'='*70}\n")

plt.show()