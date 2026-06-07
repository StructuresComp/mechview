#!/usr/bin/env python3
"""
Generate synthetic animation data for mechview.

Creates a rod that starts straight and gradually winds into a helix.
Total arc length is normalized to 1.0 in every frame so everything
fits comfortably in the scene regardless of physical scale.

Output: data.js in the same folder as this script.

Usage:
    python generate_synthetic_rod.py
    python generate_synthetic_rod.py --frames 100 --nv 30 --turns 4 --radius 0.15

Dependencies: numpy
"""

import argparse
import json
import numpy as np
from pathlib import Path


# Visual constants — normalised units (rod_length = 1).
# Anyone writing their own adapter should use the same values for consistency.
WALL_WIDTH     = 2.0   # obstacle box x-extent
WALL_DEPTH     = 2.0   # obstacle box z-extent
WALL_THICKNESS = 0.04  # obstacle box y-extent


def make_frame(alpha: float, nv: int, n_turns_max: float, radius_max: float) -> list:
    """
    Build one snapshot.

    alpha in [0, 1]: 0 = straight rod along -Y axis, 1 = full helix.

    Parameterise by t in [0, 1] along the rod:
        x(t) = R * cos(2*pi*n_turns*t)
        y(t) = -t
        z(t) = R * sin(2*pi*n_turns*t)

    Then rescale all coordinates so total arc length = 1.
    """
    t = np.linspace(0.0, 1.0, nv)

    R       = alpha * radius_max
    n_turns = alpha * n_turns_max

    # Rod hangs along -Y; helix coils in X-Z plane so the camera
    # (looking along -Z) sees the oscillations clearly.
    pts = np.stack([
        R * np.cos(2 * np.pi * n_turns * t),
        -t,
        R * np.sin(2 * np.pi * n_turns * t),
    ], axis=1)

    # Normalize arc length to 1
    seg_lengths = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    total = float(seg_lengths.sum())
    if total > 1e-10:
        pts = pts / total

    return [[float(p[0]), float(p[1]), float(p[2])] for p in pts]


def generate(
    n_frames:    int   = 250,
    nv:          int   = 50,
    n_turns_max: float = 3.0,
    radius_max:  float = 0.12,
    rod_radius:  float = 0.008,
    wall_y:      float = None,
    color:       int   = 0xff3311,
) -> dict:
    """Return the data dict ready to be serialised as data.js."""
    frames = []
    for i in range(n_frames):
        alpha = i / max(n_frames - 1, 1)
        frames.append({
            "t":     round(alpha * 10.0, 4),
            "nodes": make_frame(alpha, nv, n_turns_max, radius_max),
        })

    obstacles = []
    if wall_y is not None:
        obstacles.append({
            "center": [0.0, float(wall_y), 0.0],
            "size":   [WALL_WIDTH, WALL_THICKNESS, WALL_DEPTH],
        })

    return {
        "object_type": "rod",
        "nv":          nv,
        "rod_radius":  rod_radius,
        "color":       color,
        "obstacles":   obstacles,
        "frames":      frames,
    }


def main():
    p = argparse.ArgumentParser(description="Synthetic helix animation for mechview.")
    p.add_argument("--frames",     type=int,   default=250,   help="number of snapshots (default 250)")
    p.add_argument("--nv",         type=int,   default=50,    help="nodes per snapshot (default 50)")
    p.add_argument("--turns",      type=float, default=3.0,   help="max helix turns (default 3)")
    p.add_argument("--radius",     type=float, default=0.12,  help="max helix radius before normalisation (default 0.12)")
    p.add_argument("--rod-radius", type=float, default=0.008, help="visual tube radius (default 0.008)")
    p.add_argument("--wall",       type=float,            default=None,     help="wall y-position in normalised units, e.g. -1.05 (default: no wall)")
    p.add_argument("--color",      type=lambda x: int(x, 0), default=0xff3311, help="tube colour as hex integer, e.g. 0xff3311 (default: 0xff3311)")
    p.add_argument("--output",     type=str,              default=None,     help="output path (default: data.js next to this script)")
    args = p.parse_args()

    data = generate(
        n_frames    = args.frames,
        nv          = args.nv,
        n_turns_max = args.turns,
        radius_max  = args.radius,
        rod_radius  = args.rod_radius,
        wall_y      = args.wall,
        color       = args.color,
    )

    out = Path(args.output) if args.output else Path(__file__).parent / "data.js"
    out.write_text("const MECHVIEW_DATA = " + json.dumps(data) + ";")

    print(f"Generated {args.frames} frames  |  {args.nv} nodes each  |  {out}")
    print("Open index.html in Chrome (no server needed).")
    print()
    print("To record and make a video:")
    print("  Press 'Record' in mechview, extract frames.zip, then:")
    print("  ffmpeg -framerate 12 -i frame_%06d.png -c:v libx264 -pix_fmt yuv420p out.mp4")


if __name__ == "__main__":
    main()
