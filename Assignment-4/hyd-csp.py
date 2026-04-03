"""
pip install matplotlib networkx
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.patches import FancyBboxPatch
import networkx as nx

# ─────────────────────────────────────────────
# CSP Definition
# ─────────────────────────────────────────────
VARIABLES = [
    'Adilabad', 'KomBheem', 'Mancherial', 'Nirmal', 'Nizamabad',
    'Jagtial', 'Rajanna', 'Karimnagar', 'Peddapalli', 'Jayashankar',
    'Mulugu', 'BhadKoth', 'Khammam', 'Mahabubabad', 'Warangal_R',
    'Warangal_U', 'Jangaon', 'Yadadri', 'Medchal', 'Hyderabad',
    'Rangareddy', 'Vikarabad', 'Sangareddy', 'Medak', 'Siddipet',
    'Kamareddy', 'Nagarkurnool', 'Wanaparthy', 'Gadwal', 'Mahabubnagar',
    'Nalgonda', 'Suryapet', 'Bhongir'
]

NEIGHBORS = {
    'Adilabad':    ['KomBheem', 'Nirmal', 'Mancherial'],
    'KomBheem':    ['Adilabad', 'Mancherial'],
    'Mancherial':  ['Adilabad', 'KomBheem', 'Nirmal', 'Jagtial', 'Peddapalli'],
    'Nirmal':      ['Adilabad', 'Mancherial', 'Nizamabad', 'Kamareddy'],
    'Nizamabad':   ['Nirmal', 'Kamareddy', 'Medak', 'Sangareddy'],
    'Jagtial':     ['Mancherial', 'Rajanna', 'Karimnagar', 'Peddapalli'],
    'Rajanna':     ['Jagtial', 'Karimnagar', 'Siddipet'],
    'Karimnagar':  ['Jagtial', 'Rajanna', 'Peddapalli', 'Warangal_U', 'Siddipet'],
    'Peddapalli':  ['Mancherial', 'Jagtial', 'Karimnagar', 'Jayashankar'],
    'Jayashankar': ['Peddapalli', 'Mulugu', 'Warangal_R', 'Warangal_U'],
    'Mulugu':      ['Jayashankar', 'BhadKoth', 'Warangal_R'],
    'BhadKoth':    ['Mulugu', 'Khammam'],
    'Khammam':     ['BhadKoth', 'Mahabubabad', 'Suryapet', 'Nalgonda'],
    'Mahabubabad': ['Khammam', 'Warangal_R', 'Suryapet'],
    'Warangal_R':  ['Jayashankar', 'Mulugu', 'Mahabubabad', 'Warangal_U', 'Jangaon'],
    'Warangal_U':  ['Karimnagar', 'Jayashankar', 'Warangal_R', 'Jangaon'],
    'Jangaon':     ['Warangal_R', 'Warangal_U', 'Yadadri', 'Bhongir'],
    'Yadadri':     ['Jangaon', 'Bhongir', 'Nalgonda', 'Medchal'],
    'Medchal':     ['Yadadri', 'Hyderabad', 'Rangareddy', 'Sangareddy', 'Medak'],
    'Hyderabad':   ['Medchal', 'Rangareddy'],
    'Rangareddy':  ['Hyderabad', 'Medchal', 'Vikarabad', 'Nagarkurnool', 'Nalgonda'],
    'Vikarabad':   ['Rangareddy', 'Mahabubnagar'],
    'Sangareddy':  ['Nizamabad', 'Medak', 'Medchal'],
    'Medak':       ['Nizamabad', 'Sangareddy', 'Medchal', 'Siddipet', 'Kamareddy'],
    'Siddipet':    ['Rajanna', 'Karimnagar', 'Medak', 'Bhongir'],
    'Kamareddy':   ['Nirmal', 'Nizamabad', 'Medak'],
    'Nagarkurnool':['Rangareddy', 'Wanaparthy', 'Mahabubnagar'],
    'Wanaparthy':  ['Nagarkurnool', 'Gadwal', 'Mahabubnagar'],
    'Gadwal':      ['Wanaparthy', 'Mahabubnagar'],
    'Mahabubnagar':['Vikarabad', 'Nagarkurnool', 'Wanaparthy', 'Gadwal'],
    'Nalgonda':    ['Khammam', 'Mahabubabad', 'Suryapet', 'Yadadri', 'Rangareddy', 'Bhongir'],
    'Suryapet':    ['Khammam', 'Mahabubabad', 'Nalgonda'],
    'Bhongir':     ['Jangaon', 'Yadadri', 'Nalgonda', 'Siddipet'],
}

COLORS = ['Coral', 'Teal', 'Violet', 'Amber']

COLOR_MAP = {
    'Coral':   '#FF6B6B',
    'Teal':    '#4ECDC4',
    'Violet':  '#9B59B6',
    'Amber':   '#F39C12',
    None:      '#2E2E3E'
}

POSITIONS = {
    'Adilabad':    (3.0, 9.5),
    'KomBheem':    (4.5, 9.2),
    'Mancherial':  (5.0, 8.5),
    'Nirmal':      (2.5, 8.5),
    'Nizamabad':   (1.8, 7.5),
    'Kamareddy':   (2.2, 6.8),
    'Jagtial':     (5.2, 7.8),
    'Rajanna':     (4.5, 7.0),
    'Karimnagar':  (5.5, 7.0),
    'Peddapalli':  (5.8, 7.8),
    'Jayashankar': (6.5, 7.5),
    'Mulugu':      (7.2, 7.0),
    'BhadKoth':    (8.0, 6.5),
    'Khammam':     (7.8, 5.5),
    'Mahabubabad': (7.0, 6.0),
    'Warangal_R':  (6.8, 6.8),
    'Warangal_U':  (6.2, 6.8),
    'Jangaon':     (5.8, 6.0),
    'Siddipet':    (4.0, 6.2),
    'Medak':       (2.8, 6.0),
    'Sangareddy':  (2.2, 5.8),
    'Medchal':     (3.5, 5.2),
    'Bhongir':     (5.2, 5.2),
    'Yadadri':     (5.0, 4.8),
    'Nalgonda':    (5.8, 4.5),
    'Suryapet':    (6.8, 4.5),
    'Hyderabad':   (3.2, 4.5),
    'Rangareddy':  (2.8, 4.0),
    'Vikarabad':   (1.8, 3.5),
    'Nagarkurnool':(3.0, 3.0),
    'Wanaparthy':  (3.8, 2.5),
    'Gadwal':      (3.2, 1.8),
    'Mahabubnagar':(2.2, 2.5),
}

# ─────────────────────────────────────────────
# Solver — forward-only greedy (no backtracking)
# ─────────────────────────────────────────────
steps = []

def record(assignment, var, event, msg):
    steps.append((dict(assignment), var, event, msg))

def is_consistent(var, color, assignment):
    return all(assignment.get(nb) != color for nb in NEIGHBORS[var])

def greedy_solve():
    assignment = {}
    for var in VARIABLES:
        for color in COLORS:
            if is_consistent(var, color, assignment):
                assignment[var] = color
                record(assignment, var, 'assign', f"Assign  {var} = {color}")
                break
        else:
            record(assignment, var, 'fail', f"✗  No color available for {var}!")
            return False
    return True

greedy_solve()
steps.append((steps[-1][0], None, 'done', '✓  Solution found!'))

# ─────────────────────────────────────────────
# Graph
# ─────────────────────────────────────────────
G = nx.Graph()
G.add_nodes_from(VARIABLES)
for v, nbs in NEIGHBORS.items():
    for nb in nbs:
        if not G.has_edge(v, nb):
            G.add_edge(v, nb)

# ─────────────────────────────────────────────
# Figure Layout
# ─────────────────────────────────────────────
BG      = '#0F0F1A'
PANEL   = '#16162A'
BORDER  = '#2A2A42'
TXT     = '#E0E0F0'
TXT2    = '#8888AA'
ACCENT  = '#6C63FF'

plt.rcParams.update({'font.family': 'monospace', 'text.color': TXT})

fig = plt.figure(figsize=(18, 10), facecolor=BG)

fig.text(0.5, 0.965, 'Telangana Map Coloring (33 Districts)  —  CSP Greedy Solver',
         ha='center', va='top', fontsize=14, color=TXT,
         fontweight='bold', fontfamily='sans-serif')
fig.text(0.5, 0.940,
         'Variables: Adilabad · KomBheem · ... · Bhongir    |    Domain: {Coral, Teal, Violet, Amber}    |    Constraint: no adjacent districts share a color',
         ha='center', va='top', fontsize=8.5, color=TXT2, fontfamily='sans-serif')

ax_map  = fig.add_axes([0.02,  0.08, 0.54, 0.83])
ax_info = fig.add_axes([0.585, 0.44, 0.40, 0.47])
ax_cst  = fig.add_axes([0.585, 0.08, 0.40, 0.33])

for ax in [ax_map, ax_info, ax_cst]:
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
        spine.set_linewidth(1.2)

step_idx   = [0]
stats      = {'steps': 0}
auto_timer = [None]

def panel_header(ax, title):
    ax.set_title(title, color=TXT2, fontsize=9, pad=7,
                 fontfamily='sans-serif', loc='left', x=0.02)

# ─────────────────────────────────────────────
# Draw
# ─────────────────────────────────────────────
def draw_frame(idx):
    assignment, hl_var, event, msg = steps[idx]

    # ── Graph panel ──────────────────────────
    ax_map.clear()
    ax_map.set_facecolor(PANEL)
    for spine in ax_map.spines.values():
        spine.set_edgecolor(BORDER); spine.set_linewidth(1.2)
    ax_map.axis('off')
    panel_header(ax_map, 'CONSTRAINT GRAPH')

    node_colors, edge_colors, node_sizes, lws = [], [], [], []
    for v in G.nodes():
        c = assignment.get(v)
        node_colors.append(COLOR_MAP.get(c, COLOR_MAP[None]))
        if v == hl_var:
            edge_colors.append('#FFFFFF')
            node_sizes.append(3000)
            lws.append(5.0)
        else:
            edge_colors.append('#FFD700' if v == 'Hyderabad' else BORDER)
            node_sizes.append(3000 if v == 'Hyderabad' else 900)
            lws.append(5.0 if v == 'Hyderabad' else 1.2)

    nx.draw_networkx_edges(G, pos=POSITIONS, ax=ax_map,
                           edge_color='#3A3A5A', width=1.8, alpha=0.8)
    nx.draw_networkx_nodes(G, pos=POSITIONS, ax=ax_map,
                           node_color=node_colors, edgecolors=edge_colors,
                           linewidths=lws, node_size=node_sizes)

    labels = {v: ('★ HYD' if v == 'Hyderabad' else v[:6]) for v in G.nodes()}
    nx.draw_networkx_labels(G, pos=POSITIONS, ax=ax_map, labels=labels,
                            font_color='#FFFFFF', font_weight='bold',
                            font_size=7, font_family='sans-serif')

    ev_colors = {'assign': '#4DB87A', 'fail': '#E8534A', 'done': '#4A9EE0'}
    ec = ev_colors.get(event, TXT2)
    ax_map.text(0.5, 0.03, msg, transform=ax_map.transAxes,
                ha='center', va='bottom', fontsize=11, color=ec,
                fontweight='bold', fontfamily='sans-serif')

    prog = idx / max(len(steps) - 1, 1)
    bar_ax = ax_map.inset_axes([0.05, 0.005, 0.90, 0.018])
    bar_ax.set_xlim(0, 1); bar_ax.set_ylim(0, 1)
    bar_ax.set_facecolor('#1E1E30')
    bar_ax.add_patch(FancyBboxPatch((0, 0), prog, 1, boxstyle='square,pad=0',
                                    facecolor=ACCENT, edgecolor='none'))
    bar_ax.axis('off')

    ax_map.text(0.02, 0.975, f'Step {idx + 1} / {len(steps)}',
                transform=ax_map.transAxes, ha='left', va='top',
                fontsize=8.5, color=TXT2, fontfamily='sans-serif')
    ax_map.text(0.98, 0.975, f'Steps: {stats["steps"]}',
                transform=ax_map.transAxes, ha='right', va='top',
                fontsize=8.5, color=TXT2, fontfamily='sans-serif')

    # ── Info panel ───────────────────────────
    ax_info.clear()
    ax_info.set_facecolor(PANEL)
    for spine in ax_info.spines.values():
        spine.set_edgecolor(BORDER); spine.set_linewidth(1.2)
    ax_info.axis('off')
    panel_header(ax_info, 'VARIABLE ASSIGNMENTS')

    col_x = [0.08, 0.30, 0.52, 0.75]
    for i, col in enumerate(COLORS):
        ax_info.add_patch(FancyBboxPatch((col_x[i], 0.86), 0.18, 0.09,
                                          boxstyle='round,pad=0.01',
                                          facecolor=COLOR_MAP[col],
                                          edgecolor='#111122', linewidth=0.8,
                                          transform=ax_info.transAxes))
        ax_info.text(col_x[i] + 0.09, 0.905, col,
                     transform=ax_info.transAxes, ha='center', va='center',
                     fontsize=7, color='#111122', fontweight='bold',
                     fontfamily='sans-serif')

    row_h  = 0.74 / len(VARIABLES)
    start_y = 0.77
    for i, v in enumerate(VARIABLES):
        y     = start_y - i * row_h
        c     = assignment.get(v)
        hex_c = COLOR_MAP.get(c, COLOR_MAP[None])
        is_hl = v == hl_var

        if is_hl:
            ax_info.add_patch(FancyBboxPatch((0.03, y - row_h * 0.45), 0.94, row_h * 0.9,
                                              boxstyle='round,pad=0.005',
                                              facecolor='#1E3A2A', edgecolor='none',
                                              transform=ax_info.transAxes))

        ax_info.add_patch(FancyBboxPatch((0.05, y - row_h * 0.35), 0.06, row_h * 0.7,
                                          boxstyle='round,pad=0.003',
                                          facecolor=hex_c, edgecolor=BORDER, linewidth=0.4,
                                          transform=ax_info.transAxes))

        label_col = '#4DB87A' if is_hl else (TXT if c else TXT2)
        ax_info.text(0.15, y, v[:8], transform=ax_info.transAxes,
                     fontsize=6.5, color=label_col, va='center',
                     fontweight='bold' if is_hl else 'normal')
        ax_info.text(0.35, y, '→', transform=ax_info.transAxes,
                     fontsize=7, color=TXT2, va='center')
        ax_info.text(0.42, y, c if c else '—', transform=ax_info.transAxes,
                     fontsize=6.5, color=label_col, va='center',
                     fontweight='bold' if c else 'normal')

        if c:
            conflicts = [nb for nb in NEIGHBORS[v] if assignment.get(nb) == c]
            st_col = '#E8534A' if conflicts else '#4DB87A'
            ax_info.text(0.58, y, '✗' if conflicts else '✓',
                         transform=ax_info.transAxes, fontsize=6,
                         color=st_col, va='center')

    # ── Constraint panel ─────────────────────
    ax_cst.clear()
    ax_cst.set_facecolor(PANEL)
    for spine in ax_cst.spines.values():
        spine.set_edgecolor(BORDER); spine.set_linewidth(1.2)
    ax_cst.axis('off')
    panel_header(ax_cst, 'CONSTRAINT CHECK')

    if hl_var:
        nbs      = NEIGHBORS.get(hl_var, [])
        hl_color = assignment.get(hl_var)
        row_h2   = min(0.80 / max(len(nbs), 1), 0.22)
        for j, nb in enumerate(nbs[:5]):
            y2       = 0.88 - j * (row_h2 + 0.03)
            nb_color = assignment.get(nb)
            conflict = nb_color is not None and nb_color == hl_color
            bg = '#3A1E1E' if conflict else '#1E3A2A'
            sym, sc = ('✗', '#E8534A') if conflict else ('✓', '#4DB87A')

            ax_cst.add_patch(FancyBboxPatch((0.04, y2 - row_h2 * 0.45), 0.92, row_h2,
                                             boxstyle='round,pad=0.01',
                                             facecolor=bg, edgecolor='none',
                                             transform=ax_cst.transAxes))
            ax_cst.text(0.10, y2, sym, transform=ax_cst.transAxes,
                        fontsize=11, color=sc, va='center', fontweight='bold')
            ax_cst.text(0.22, y2, f'{hl_var[:8]}  ≠  {nb[:8]}',
                        transform=ax_cst.transAxes, fontsize=8, color=TXT, va='center')
            disp_c = COLOR_MAP.get(nb_color, TXT2)
            ax_cst.add_patch(FancyBboxPatch((0.65, y2 - 0.045), 0.18, 0.09,
                                             boxstyle='round,pad=0.005',
                                             facecolor=disp_c,
                                             edgecolor='#111122', linewidth=0.5,
                                             transform=ax_cst.transAxes))
            ax_cst.text(0.74, y2, nb_color if nb_color else 'unset',
                        transform=ax_cst.transAxes, fontsize=7,
                        color='#111122' if nb_color else TXT2,
                        ha='center', va='center',
                        fontweight='bold' if nb_color else 'normal')
    else:
        ax_cst.text(0.5, 0.5, '—', transform=ax_cst.transAxes,
                    ha='center', va='center', fontsize=20, color=TXT2)

    fig.canvas.draw_idle()

# ─────────────────────────────────────────────
# Button callbacks
# ─────────────────────────────────────────────
def on_next(event):
    if step_idx[0] < len(steps) - 1:
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
    draw_frame(0)

# ─────────────────────────────────────────────
# Buttons
# ─────────────────────────────────────────────
BTN_FC  = '#1E1E32'
BTN_HOV = '#2A2A48'

ax_prev  = fig.add_axes([0.03,  0.015, 0.10, 0.042])
ax_next  = fig.add_axes([0.145, 0.015, 0.10, 0.042])
ax_auto  = fig.add_axes([0.260, 0.015, 0.10, 0.042])
ax_reset = fig.add_axes([0.375, 0.015, 0.10, 0.042])

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

final_assignment = steps[-1][0]
solution = ', '.join(f'{v}={final_assignment[v]}' for v in sorted(final_assignment.keys()))
print(f"\n{'='*70}")
print(f"TELANGANA MAP COLORING - SOLUTION FOUND")
print(f"{'='*70}")
print(f"Total steps: {len(steps)}")
print(f"Solution: {solution}")
print(f"{'='*70}\n")

plt.show()