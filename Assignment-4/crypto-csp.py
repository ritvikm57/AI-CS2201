"""
pip install matplotlib
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.patches import FancyBboxPatch, Rectangle
from copy import deepcopy

# ─────────────────────────────────────────────
# CSP Solver for TWO + TWO = FOUR
# ─────────────────────────────────────────────
steps = []

VARIABLES = ['T', 'W', 'O', 'F', 'U', 'R', 'C1', 'C2', 'C3']
LETTER_VARS = ['T', 'W', 'O', 'F', 'U', 'R']
CARRY_VARS = ['C1', 'C2', 'C3']

def record(assignment, var, event, msg):
    steps.append((dict(assignment), var, event, msg))

def is_alldiff(vars_list, assignment):
    """Check if assigned variables have different values"""
    vals = [assignment.get(v) for v in vars_list if v in assignment]
    return len(vals) == len(set(vals))

def check_constraints(assignment):
    """Check if all constraints are satisfied"""
    # Alldiff
    if not is_alldiff(LETTER_VARS, assignment):
        return False
    
    # No leading zeros
    if 'T' in assignment and assignment['T'] == 0:
        return False
    if 'F' in assignment and assignment['F'] == 0:
        return False
    
    # Column constraints (only check if all variables are assigned)
    if len([v for v in LETTER_VARS if v in assignment]) == 6:
        if all(v in assignment for v in CARRY_VARS):
            # O + O = R + 10*C1
            if assignment['O'] + assignment['O'] != assignment['R'] + 10 * assignment['C1']:
                return False
            # C1 + W + W = U + 10*C2
            if assignment['C1'] + assignment['W'] + assignment['W'] != assignment['U'] + 10 * assignment['C2']:
                return False
            # C2 + T + T = O + 10*C3
            if assignment['C2'] + assignment['T'] + assignment['T'] != assignment['O'] + 10 * assignment['C3']:
                return False
            # C3 = F
            if assignment['C3'] != assignment['F']:
                return False
    
    return True

def get_domain(var, assignment):
    """Get valid domain for a variable given current assignment"""
    if var in CARRY_VARS:
        return [0, 1]
    else:
        domain = list(range(10))
        if var in ['T', 'F']:
            domain = [d for d in domain if d != 0]
        return domain

def backtrack(assignment):
    if len(assignment) == len(VARIABLES):
        # Check all constraints one more time
        if check_constraints(assignment):
            return True
        return False
    
    # Select unassigned variable
    var = next(v for v in VARIABLES if v not in assignment)
    
    # Try each value in domain
    for val in get_domain(var, assignment):
        assignment[var] = val
        record(assignment, var, 'assign', f"Assign  {var} = {val}")
        
        # Check constraints
        if check_constraints(assignment):
            if backtrack(assignment):
                return True
        
        del assignment[var]
        record(assignment, var, 'backtrack', f"Backtrack  {var} ≠ {val}")
    
    return False

# Solve
backtrack({})
steps.append((steps[-1][0], None, 'done', '✓  Solution found!'))

# ─────────────────────────────────────────────
# Figure Layout
# ─────────────────────────────────────────────
BG      = '#0F0F1A'
PANEL   = '#16162A'
BORDER  = '#2A2A42'
TXT     = '#E0E0F0'
TXT2    = '#8888AA'
ACCENT  = '#6C63FF'

plt.rcParams.update({
    'font.family': 'monospace',
    'text.color':  TXT,
})

fig = plt.figure(figsize=(16, 9), facecolor=BG)

# Title bar
fig.text(0.5, 0.965, 'Cryptarithmetic Puzzle  —  TWO + TWO = FOUR',
         ha='center', va='top', fontsize=14, color=TXT,
         fontweight='bold', fontfamily='sans-serif')
fig.text(0.5, 0.940, 'Variables: T, W, O, F, U, R ∈ {0..9} | C1, C2, C3 ∈ {0,1}    |    Constraints: Alldiff + Column equations + No leading zeros',
         ha='center', va='top', fontsize=9, color=TXT2, fontfamily='sans-serif')

# Axes
ax_puzzle = fig.add_axes([0.08, 0.25, 0.48, 0.65])
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
# ─────────────────────────────────────────────
def draw_puzzle(ax, assignment):
    """Draw the TWO + TWO = FOUR puzzle"""
    ax.clear()
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
        spine.set_linewidth(1.2)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    panel_header(ax, 'PUZZLE')
    
    # Draw the addition problem in a nice format
    # Layout:
    #       T  W  O
    #    +  T  W  O
    #    ----------
    #    F  O  U  R
    
    # Positions
    lines = [
        # Line 1: T W O (with some spacing)
        [(2, 7, 'T'), (4, 7, 'W'), (6, 7, 'O')],
        # Line 2: + T W O (with + sign)
        [(1, 2, '+'), (2, 5, 'T'), (4, 5, 'W'), (6, 5, 'O')],
        # Line 3: separator (dashes)
        [(2, 3, '-'), (4, 3, '-'), (6, 3, '-')],
        # Line 4: F O U R
        [(1.5, 1, 'F'), (2, 1, 'O'), (4, 1, 'U'), (6, 1, 'R')],
    ]
    
    for line in lines:
        for x, y, var in line:
            if var == '+':
                ax.text(x, y, '+', fontsize=20, color=TXT,
                       ha='center', va='center', fontweight='bold')
            elif var == '-':
                ax.text(x, y, '─', fontsize=16, color=TXT2,
                       ha='center', va='center')
            else:
                # Check if assigned
                val = assignment.get(var)
                val_str = str(val) if val is not None else var
                txt_col = '#FFFFFF' if val is not None else TXT2
                txt_size = 18 if val is not None else 14
                ax.text(x, y, val_str, fontsize=txt_size, color=txt_col,
                       ha='center', va='center', fontweight='bold',
                       fontfamily='monospace')
    
    # Carry digits above (C2, C1, C3)
    carry_pos = [(3.8, 8, 'C2'), (5.8, 8, 'C1'), (1.5, 2, 'C3')]
    for x, y, var in carry_pos:
        val = assignment.get(var)
        if val is not None:
            ax.text(x, y, f'[{val}]', fontsize=10, color=ACCENT,
                   ha='center', va='center', fontweight='bold',
                   fontfamily='sans-serif')
        else:
            ax.text(x, y, f'[?]', fontsize=10, color=TXT2,
                   ha='center', va='center', fontweight='normal',
                   fontfamily='sans-serif')

# ─────────────────────────────────────────────
# Check constraint status
# ─────────────────────────────────────────────
def get_constraint_status(name, assignment):
    """Returns (satisfied, reason)"""
    if name == 'O+O':
        if 'O' in assignment and 'R' in assignment and 'C1' in assignment:
            result = assignment['O'] + assignment['O']
            expected = assignment['R'] + 10 * assignment['C1']
            return result == expected, f"{assignment['O']} + {assignment['O']} = {expected}"
        return None, '—'
    
    elif name == 'C1+W+W':
        if all(v in assignment for v in ['C1', 'W', 'U', 'C2']):
            result = assignment['C1'] + assignment['W'] + assignment['W']
            expected = assignment['U'] + 10 * assignment['C2']
            return result == expected, f"{assignment['C1']} + {assignment['W']} + {assignment['W']} = {expected}"
        return None, '—'
    
    elif name == 'C2+T+T':
        if all(v in assignment for v in ['C2', 'T', 'O', 'C3']):
            result = assignment['C2'] + assignment['T'] + assignment['T']
            expected = assignment['O'] + 10 * assignment['C3']
            return result == expected, f"{assignment['C2']} + {assignment['T']} + {assignment['T']} = {expected}"
        return None, '—'
    
    elif name == 'C3=F':
        if 'C3' in assignment and 'F' in assignment:
            return assignment['C3'] == assignment['F'], f"{assignment['C3']} = {assignment['F']}"
        return None, '—'
    
    return None, '—'

# ─────────────────────────────────────────────
# Draw Frame
# ─────────────────────────────────────────────
def draw_frame(idx):
    assignment, hl_var, event, msg = steps[idx]
    
    # ── Puzzle ───────────────────────────────
    draw_puzzle(ax_puzzle, assignment)
    
    # Step message
    ev_colors = {'assign': '#4DB87A', 'backtrack': '#E8534A', 'done': '#4A9EE0'}
    ec = ev_colors.get(event, TXT2)
    ax_puzzle.text(0.5, 0.05, msg, transform=ax_puzzle.transAxes,
                  ha='center', va='bottom', fontsize=10, color=ec,
                  fontweight='bold', fontfamily='sans-serif')
    
    # Progress bar
    prog = idx / max(len(steps) - 1, 1)
    bar_ax = ax_puzzle.inset_axes([0.05, -0.05, 0.90, 0.025])
    bar_ax.set_xlim(0, 1); bar_ax.set_ylim(0, 1)
    bar_ax.set_facecolor('#1E1E30')
    bar_ax.add_patch(FancyBboxPatch((0, 0), prog, 1,
                                    boxstyle='square,pad=0',
                                    facecolor=ACCENT, edgecolor='none'))
    bar_ax.axis('off')
    
    ax_puzzle.text(0.02, -0.065, f'Step {idx + 1} / {len(steps)}',
                  transform=ax_puzzle.transAxes, ha='left', va='top',
                  fontsize=8.5, color=TXT2, fontfamily='sans-serif')
    
    # ── Info panel (assignments) ─────────────
    ax_info.clear()
    ax_info.set_facecolor(PANEL)
    for spine in ax_info.spines.values():
        spine.set_edgecolor(BORDER); spine.set_linewidth(1.2)
    ax_info.axis('off')
    panel_header(ax_info, 'VARIABLE ASSIGNMENTS')
    
    # Letters
    ax_info.text(0.5, 0.92, 'Letters', transform=ax_info.transAxes,
                fontsize=9, color=TXT2, ha='center', fontweight='bold',
                fontfamily='sans-serif')
    
    row_h = 0.13
    start_y = 0.80
    for i, var in enumerate(LETTER_VARS):
        y = start_y - i * row_h
        val = assignment.get(var)
        is_hl = var == hl_var
        val_str = str(val) if val is not None else '—'
        val_col = ('#4DB87A' if event == 'assign' else '#E8534A') if is_hl else (TXT if val is not None else TXT2)
        
        ax_info.text(0.15, y, f'{var}', transform=ax_info.transAxes,
                    fontsize=10, color=(ACCENT if is_hl else TXT), va='center',
                    fontweight='bold')
        ax_info.text(0.40, y, '→', transform=ax_info.transAxes,
                    fontsize=9, color=TXT2, va='center')
        ax_info.text(0.55, y, val_str, transform=ax_info.transAxes,
                    fontsize=10, color=val_col, va='center',
                    fontweight='bold' if val is not None else 'normal')
    
    # Carries
    ax_info.text(0.5, 0.18, 'Carries', transform=ax_info.transAxes,
                fontsize=9, color=TXT2, ha='center', fontweight='bold',
                fontfamily='sans-serif')
    
    row_h2 = 0.12
    start_y2 = 0.08
    for i, var in enumerate(CARRY_VARS):
        y2 = start_y2 - i * row_h2
        val = assignment.get(var)
        val_str = str(val) if val is not None else '—'
        val_col = TXT if val is not None else TXT2
        
        ax_info.text(0.15, y2, f'{var}', transform=ax_info.transAxes,
                    fontsize=9, color=ACCENT, va='center', fontweight='bold')
        ax_info.text(0.40, y2, '→', transform=ax_info.transAxes,
                    fontsize=8, color=TXT2, va='center')
        ax_info.text(0.55, y2, val_str, transform=ax_info.transAxes,
                    fontsize=9, color=val_col, va='center',
                    fontweight='bold' if val is not None else 'normal')
    
    # ── Constraint panel ─────────────────────
    ax_cst.clear()
    ax_cst.set_facecolor(PANEL)
    for spine in ax_cst.spines.values():
        spine.set_edgecolor(BORDER); spine.set_linewidth(1.2)
    ax_cst.axis('off')
    panel_header(ax_cst, 'COLUMN CONSTRAINTS')
    
    constraints = [
        ('O+O', "O + O = R + 10·C1"),
        ('C1+W+W', "C1 + W + W = U + 10·C2"),
        ('C2+T+T', "C2 + T + T = O + 10·C3"),
        ('C3=F', "C3 = F"),
    ]
    
    row_h3 = 0.20
    start_y3 = 0.85
    for i, (name, label) in enumerate(constraints):
        y3 = start_y3 - i * (row_h3 + 0.05)
        
        status, detail = get_constraint_status(name, assignment)
        
        if status is None:
            st_col = TXT2
            sym = '◯'
        elif status:
            st_col = '#4DB87A'
            sym = '✓'
        else:
            st_col = '#E8534A'
            sym = '✗'
        
        ax_cst.text(0.08, y3, sym, transform=ax_cst.transAxes,
                   fontsize=11, color=st_col, va='center', fontweight='bold')
        ax_cst.text(0.22, y3, label, transform=ax_cst.transAxes,
                   fontsize=8, color=TXT, va='center')
        ax_cst.text(0.60, y3, detail, transform=ax_cst.transAxes,
                   fontsize=7, color=TXT2, va='center', fontfamily='monospace')
    
    fig.canvas.draw_idle()

# ─────────────────────────────────────────────
# Button callbacks
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
            plt.pause(0.30)
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

# ─────────────────────────────────────────────
# Buttons
# ─────────────────────────────────────────────
BTN_FC   = '#1E1E32'
BTN_HOV  = '#2A2A48'

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

# Final solution
final_assignment = steps[-1][0]
T, W, O, F, U, R = [final_assignment[v] for v in LETTER_VARS]
TWO = T * 100 + W * 10 + O
FOUR = F * 1000 + O * 100 + U * 10 + R

print(f"\n{'='*70}")
print(f"CRYPTARITHMETIC - SOLUTION FOUND")
print(f"{'='*70}")
print(f"TWO = {TWO}")
print(f"{TWO} + {TWO} = {FOUR}")
print(f"\nVariable assignments:")
print(f"  T={T}, W={W}, O={O}, F={F}, U={U}, R={R}")
print(f"  C1={final_assignment['C1']}, C2={final_assignment['C2']}, C3={final_assignment['C3']}")
print(f"\nTotal steps: {len(steps)}")
print(f"{'='*70}\n")

plt.show()
