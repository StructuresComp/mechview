#!/usr/bin/env python3
"""
Generate synthetic animated shell/plate data for mechview.

Creates an M×N rectangular mesh deforming with a travelling sine wave in Y.
Plate spans 1×1 in the X-Z plane, centred at the origin.

Output: data.js in the same folder as this script.

Usage:
    python generate_synthetic_shell.py
    python generate_synthetic_shell.py --rows 30 --cols 30 --frames 120 --wall -0.15

Dependencies: numpy
"""

import argparse
import json
import numpy as np
from pathlib import Path


# Visual constants — same units as node coordinates (plate size = 1×1).
# Use the same values in your own adapter for consistency.
WALL_WIDTH     = 2.0   # obstacle box x-extent
WALL_DEPTH     = 2.0   # obstacle box z-extent
WALL_THICKNESS = 0.04  # obstacle box y-extent


def make_grid(rows: int, cols: int) -> tuple:
    """
    Flat M×N grid in the X-Z plane, centred at origin, spanning 1×1.

    Returns:
        rest_nodes : np.ndarray (rows*cols, 3)  rest positions, y = 0
        faces      : list of [i, j, k]  triangle connectivity, 0-based, static
    """
    xs = np.linspace(-0.5, 0.5, cols)
    zs = np.linspace(-0.5, 0.5, rows)
    XX, ZZ = np.meshgrid(xs, zs)

    rest_nodes = np.stack([XX.ravel(), np.zeros(rows * cols), ZZ.ravel()], axis=1)

    # Each quad (i,j) → two triangles with consistent winding
    faces = []
    for i in range(rows - 1):
        for j in range(cols - 1):
            a = i * cols + j
            b = i * cols + (j + 1)
            c = (i + 1) * cols + j
            d = (i + 1) * cols + (j + 1)
            faces.append([a, b, c])
            faces.append([b, d, c])

    return rest_nodes, faces


def make_frame(rest_nodes: np.ndarray, t: float, amplitude: float, freq: float) -> list:
    """Travelling sine-wave deformation in Y:  y = A * sin(2π*freq*x − 2π*t)."""
    nodes = rest_nodes.copy()
    nodes[:, 1] = amplitude * np.sin(2 * np.pi * freq * rest_nodes[:, 0] - 2 * np.pi * t)
    return [[float(x), float(y), float(z)] for x, y, z in nodes]


def generate(
    rows:      int   = 20,
    cols:      int   = 20,
    n_frames:  int   = 120,
    amplitude: float = 0.08,
    freq:      float = 2.0,
    wall_y:    float = None,
    color:     int   = 0x4488cc,
) -> dict:
    """Return the data dict ready to be serialised as data.js."""
    rest_nodes, faces = make_grid(rows, cols)

    frames = []
    for i in range(n_frames):
        t = i / max(n_frames - 1, 1)
        frames.append({
            "t":     round(t * 4.0, 4),
            "nodes": make_frame(rest_nodes, t, amplitude, freq),
        })

    obstacles = []
    if wall_y is not None:
        obstacles.append({
            "center": [0.0, float(wall_y), 0.0],
            "size":   [WALL_WIDTH, WALL_THICKNESS, WALL_DEPTH],
        })

    return {
        "object_type": "shell",
        "nv":          rows * cols,
        "faces":       faces,
        "color":       color,
        "obstacles":   obstacles,
        "frames":      frames,
    }


def main():
    p = argparse.ArgumentParser(description="Synthetic waving plate for mechview.")
    p.add_argument("--rows",      type=int,   default=20,   help="grid rows (default 20)")
    p.add_argument("--cols",      type=int,   default=20,   help="grid cols (default 20)")
    p.add_argument("--frames",    type=int,   default=120,  help="number of snapshots (default 120)")
    p.add_argument("--amplitude", type=float, default=0.08, help="wave amplitude (default 0.08)")
    p.add_argument("--freq",      type=float, default=2.0,  help="spatial frequency (default 2.0)")
    p.add_argument("--wall",      type=float,            default=None,     help="wall y-position, e.g. -0.25 (default: no wall)")
    p.add_argument("--color",     type=lambda x: int(x, 0), default=0x4488cc, help="shell colour as hex integer, e.g. 0x4488cc (default: 0x4488cc)")
    p.add_argument("--output",    type=str,              default=None,     help="output path (default: data.js next to this script)")
    args = p.parse_args()

    data = generate(
        rows      = args.rows,
        cols      = args.cols,
        n_frames  = args.frames,
        amplitude = args.amplitude,
        freq      = args.freq,
        wall_y    = args.wall,
        color     = args.color,
    )

    out = Path(args.output) if args.output else Path(__file__).parent / "data.js"
    out.write_text("const MECHVIEW_DATA = " + json.dumps(data) + ";")

    n_tri = len(data["faces"])
    print(f"Generated {args.frames} frames  |  {args.rows}×{args.cols} grid ({n_tri} triangles)  |  {out}")
    print("Open index.html in Chrome (no server needed).")
    print()
    print("To record and make a video:")
    print("  Press 'Record' in mechview, extract frames.zip, then:")
    print("  ffmpeg -framerate 12 -i frame_%06d.png -c:v libx264 -pix_fmt yuv420p out.mp4")


if __name__ == "__main__":
    main()
