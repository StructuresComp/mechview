# MechView

Visualise rod, beam, and shell/plate configurations from any simulation as a 3D animation.
I initially developed this to visualize results from Discrete Elastic Rods and Discrete Shells algorithms.
However, it works with any simulation that produces node positions over time.

**No server. No install. Open `index.html` in Chrome.**

---

## Install

```bash
pip install git+https://github.com/StructuresComp/mechview
```

---

## Use case 1 — quick and dirty

Say you ran a simulation. You have 1000 time steps. At each step you have N nodes,
each with an (x, y, z) position. You want a 3D animation and save it in a video.

**Step 1:** Copy the viewer and a template into your working directory.

```bash
mechview init
```

This drops three files in the current directory:
- `index.html` — the viewer
- `export_rod_template.py` — template for rods and beams
- `export_shell_template.py` — template for shells and plates

**Step 2:** Copy the relevant template, rename it, and fill in your data.

For a rod or beam — open `export_rod_template.py` and replace the placeholder with your arrays:

```python
# YOUR DATA — replace these two lines
node_positions = my_solver.get_positions()   # shape: (n_timesteps, n_nodes, 3)
times          = my_solver.get_times()       # shape: (n_timesteps,)
```

For a shell or plate — open `export_shell_template.py` and replace:

```python
# YOUR DATA — replace these two lines
node_positions = my_solver.get_positions()   # shape: (n_timesteps, n_nodes, 3)
faces          = my_mesh.get_connectivity()  # shape: (n_triangles, 3), 0-based, static
```

**Step 3:** Run your script. It writes `data.js` next to `index.html`.

**Step 4:** Open `index.html` in Chrome.

---

## Use case 2 — integrated pipeline

mechview is a pip dependency of a larger package that runs many simulations automatically.
The pipeline writes `data.js` programmatically through its own adapter and fetches
`index.html` from the installed mechview package:

```python
import importlib.resources
import shutil
from pathlib import Path

src = importlib.resources.files("mechview") / "index.html"
with importlib.resources.as_file(src) as p:
    shutil.copy(p, output_dir / "index.html")
```

No CLI involved. See the schema below to write `data.js` directly.

---

## Schema — rod / beam

```js
const MECHVIEW_DATA = {
  "object_type": "rod",    // or "beam" (z=0 for beams)
  "nv":          20,       // number of nodes per frame
  "rod_radius":  0.02,     // visual tube radius, same units as your node coords
  "color":       16724753, // optional — RGB as integer (e.g. 0xff3311 = 16724753)

  "obstacles": [           // optional — rigid boxes
    { "center": [0.0, -1.05, 0.0], "size": [2.0, 0.04, 2.0] }
  ],

  "fps":    12,            // optional — playback speed, frames per second (default 12)
  "camera": {              // optional — initial view (default: looking along -z at the rod)
    "position": [0.8, 0.6, 1.6],
    "target":   [0.0, 0.0, 0.0]
  },
  "ghost": {               // optional — style of a second, translucent tube drawn from
    "color":      4491212, //   each frame's "ghost_nodes" (e.g. a target shape)
    "opacity":    0.35,
    "rod_radius": 0.015
  },
  "curves": [              // optional — styles of extra thin tubes drawn from each frame's
    { "color": 1710617, "opacity": 1.0, "rod_radius": 0.004 },  //   "curves" (e.g. a stripe
    { "color": 1710617, "opacity": 1.0, "rod_radius": 0.010 }   //   along the rod, a marker)
  ],

  "frames": [
    {
      "t":           0.0,                             // time (display only)
      "nodes":       [[x0,y0,z0], [x1,y1,z1], ...],  // exactly nv entries, 0-based
      "label":       "Step 0\ninitial state",         // optional overlay text; "\n" = new line
      "ghost_nodes": [[x0,y0,z0], ...],               // optional — the ghost tube for this
                                                      //   frame (any number of nodes >= 2)
      "curves":      [[[x,y,z], ...], [[x,y,z], [x,y,z]]]  // optional — nodes of curve k (as
    },                                                //   styled above); 2 nodes = a straight
                                                      //   segment; [] or missing = not drawn
    ...
  ]
};
```

Three.js is y-up: if your simulation has z up, rotate the coordinates before exporting,
e.g. (x, y, z) → (x, z, −y). Do not just swap y and z: that is a reflection, which mirrors
the shape (a right-handed helix would look left-handed).

## Schema — shell / plate

```js
const MECHVIEW_DATA = {
  "object_type": "shell",  // or "plate"
  "nv":          400,      // total number of nodes (same every frame)
  "color":       4491212,  // optional — RGB as integer (e.g. 0x4488cc = 4491212)

  "faces": [               // STATIC — one row per triangle, 0-based node indices
    [0, 1, 20],
    [1, 21, 20],
    ...
  ],

  "obstacles": [],         // optional

  "frames": [
    {
      "t":     0.0,
      "nodes": [[x0,y0,z0], [x1,y1,z1], ...],  // exactly nv entries
      "label": "Step 0"                         // optional
    },
    ...
  ]
};
```

**`faces` is static** — same connectivity every frame, only `nodes` changes.

**Node indices are 0-based.** If your solver uses 1-based or non-sequential labels:

```python
label_to_index = {label: i for i, label in enumerate(sorted_labels)}
faces = [[label_to_index[a], label_to_index[b], label_to_index[c]]
         for a, b, c in your_connectivity]
```

---

## CLI reference (use case 1)

```
mechview init             copy index.html + templates to the current directory
mechview rod  [options]   generate synthetic rod/beam data.js (helix animation)
mechview shell [options]  generate synthetic shell/plate data.js (waving plate)
```

**Rod options:**

| Flag | Default | Description |
|---|---|---|
| `--frames N` | 250 | number of snapshots |
| `--nv N` | 50 | nodes per snapshot |
| `--turns N` | 3.0 | max helix turns |
| `--radius R` | 0.12 | max helix radius |
| `--rod-radius R` | 0.008 | visual tube radius |
| `--wall Y` | none | wall y-position, e.g. `-1.05` |
| `--color 0xRRGGBB` | `0xff3311` | tube colour |
| `--output PATH` | `data.js` | output file |

**Shell options:**

| Flag | Default | Description |
|---|---|---|
| `--rows N` | 20 | grid rows |
| `--cols N` | 20 | grid cols |
| `--frames N` | 120 | number of snapshots |
| `--amplitude A` | 0.08 | wave amplitude |
| `--freq F` | 2.0 | spatial frequency |
| `--wall Y` | none | wall y-position, e.g. `-0.25` |
| `--color 0xRRGGBB` | `0x4488cc` | shell colour |
| `--output PATH` | `data.js` | output file |

---

## Viewer controls

| Input | Action |
|---|---|
| **▶ Play / ⏸ Pause** | Start or stop animation |
| **Slider** | Jump to any frame |
| **Left-drag** | Orbit (rotate) |
| **Right-drag** | Pan |
| **Scroll** | Zoom |
| **⏺ Record** | Capture all frames as PNGs → downloads `frames.zip` |

---

## Making a video

1. Click **⏺ Record** and wait for `frames.zip` to download.
2. Extract and encode:
   ```bash
   unzip frames.zip -d frames/
   ffmpeg -framerate 12 -i frames/frame_%06d.png -c:v libx264 -pix_fmt yuv420p output.mp4
   ```
   `-framerate 12` matches the viewer's default playback speed (`FPS = 12` in `index.html`);
   if `data.js` sets `"fps"`, use that value. The status line after recording shows the
   command with the right frame rate.

---

## Customising the look

Open `index.html` — every visual parameter has a comment next to it.

| What to change | Where in `index.html` |
|---|---|
| Playback speed | `let FPS = 12;` (or `"fps"` in `data.js`) |
| Background colour | `scene.background = new THREE.Color(...)` |
| Ambient light intensity | `new THREE.AmbientLight(0xffffff, 0.28)` — second arg |
| Shadow sharpness | `spotLight.penumbra` (0 = hard, 1 = soft) |
| Key light position | `spotLight.position.set(x, y, z)` |
| Rod colour | `color: objectColor ?? 0xff3311` inside `buildTube()` |
| Shell colour | `color: objectColor ?? 0x4488cc` inside `initShell()` |

---

## Files

```
mechview/
├── pyproject.toml
├── requirements.txt
├── README.md
└── mechview/
    ├── __init__.py
    ├── cli.py                       ← mechview command entry point
    ├── index.html                   ← viewer (copied to cwd by mechview init)
    ├── generate_synthetic_rod.py    ← rod/beam synthetic data
    └── generate_synthetic_shell.py  ← shell/plate synthetic data
```

**Runtime dependencies:** none — Three.js and JSZip load from CDN.
**Python:** `numpy` only.
**Video encoding:** `ffmpeg` (`brew install ffmpeg` / `apt install ffmpeg`).
