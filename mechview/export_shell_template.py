"""
MechView export template — shell / plate.

Fill in the two lines marked YOUR DATA, then run:
    python export_shell_template.py

Output: data.js in the current directory.
Open index.html in Chrome.
"""

import json
from pathlib import Path


# ── YOUR DATA ────────────────────────────────────────────────────────────────
node_positions = None   # np.ndarray or list, shape (n_timesteps, n_nodes, 3)
faces          = None   # list of [i, j, k], shape (n_triangles, 3), 0-based, STATIC
# ─────────────────────────────────────────────────────────────────────────────

# Optional settings
COLOR = 0x4488cc  # shell colour as hex RGB integer
WALL  = None      # wall obstacle: {"center": [x,y,z], "size": [w,h,d]}
                  # or None for no wall

# If your solver uses 1-based or non-sequential node labels, remap here:
#   label_to_index = {label: i for i, label in enumerate(sorted_labels)}
#   faces = [[label_to_index[a], label_to_index[b], label_to_index[c]]
#             for a, b, c in your_connectivity]

frames = []
for step, positions in enumerate(node_positions):
    frames.append({
        "t":     float(step),
        "nodes": [[float(x), float(y), float(z)] for x, y, z in positions],
        # "label": f"Step {step}",  # optional per-frame overlay text
    })

data = {
    "object_type": "shell",
    "nv":          len(frames[0]["nodes"]),
    "faces":       faces,
    "color":       COLOR,
    "obstacles":   [WALL] if WALL else [],
    "frames":      frames,
}

Path("data.js").write_text("const MECHVIEW_DATA = " + json.dumps(data) + ";")
print(f"Wrote data.js  ({len(frames)} frames, {data['nv']} nodes, {len(faces)} triangles)")
print("Open index.html in Chrome.")
