"""
MechView export template — rod / beam.

Fill in the two lines marked YOUR DATA, then run:
    python export_rod_template.py

Output: data.js in the current directory.
Open index.html in Chrome.
"""

import json
from pathlib import Path


# ── YOUR DATA ────────────────────────────────────────────────────────────────
node_positions = None   # np.ndarray or list, shape (n_timesteps, n_nodes, 3)
                        # use z=0 for beams
times          = None   # shape (n_timesteps,) — any units, display only
# ─────────────────────────────────────────────────────────────────────────────

# Optional settings
OBJECT_TYPE = "rod"    # "rod" or "beam"
ROD_RADIUS  = 0.02     # visual tube radius, same units as your coordinates
COLOR       = 0xff3311 # tube colour as hex RGB integer
WALL        = None     # wall obstacle: {"center": [x,y,z], "size": [w,h,d]}
                       # or None for no wall

# If your solver uses 1-based or non-sequential node labels, remap here:
#   label_to_index = {label: i for i, label in enumerate(sorted_labels)}
#   node_positions = node_positions[:, sorted_order, :]  # reorder columns

frames = []
for step, positions in enumerate(node_positions):
    frames.append({
        "t":     float(times[step]),
        "nodes": [[float(x), float(y), float(z)] for x, y, z in positions],
        # "label": f"Step {step}",  # optional per-frame overlay text
    })

data = {
    "object_type": OBJECT_TYPE,
    "nv":          len(frames[0]["nodes"]),
    "rod_radius":  ROD_RADIUS,
    "color":       COLOR,
    "obstacles":   [WALL] if WALL else [],
    "frames":      frames,
}

Path("data.js").write_text("const MECHVIEW_DATA = " + json.dumps(data) + ";")
print(f"Wrote data.js  ({len(frames)} frames, {data['nv']} nodes each)")
print("Open index.html in Chrome.")
