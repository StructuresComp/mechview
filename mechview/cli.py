"""
mechview — CLI entry point.

Subcommands:
    mechview init             copy index.html to the current directory
    mechview rod  [options]   generate rod data.js in the current directory
    mechview shell [options]  generate shell data.js in the current directory

Run `mechview <subcommand> --help` for options.
"""

import argparse
import shutil
import importlib.resources
from pathlib import Path

from mechview.generate_synthetic_rod   import generate as generate_rod,   main as _rod_main
from mechview.generate_synthetic_shell import generate as generate_shell, main as _shell_main


def cmd_init(args):
    src = importlib.resources.files("mechview") / "index.html"
    dst = Path.cwd() / "index.html"
    with importlib.resources.as_file(src) as p:
        shutil.copy(p, dst)
    print(f"index.html → {dst}")
    print("Run `mechview rod` or `mechview shell` to generate data.js, then open index.html in Chrome.")


def main():
    p = argparse.ArgumentParser(
        prog="mechview",
        description="3D animation viewer for rods, beams, and shells.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # init
    sub.add_parser("init", help="copy index.html to the current directory")

    # rod
    r = sub.add_parser("rod", help="generate rod/beam data.js")
    r.add_argument("--frames",     type=int,              default=250,      help="number of snapshots (default 250)")
    r.add_argument("--nv",         type=int,              default=50,       help="nodes per snapshot (default 50)")
    r.add_argument("--turns",      type=float,            default=3.0,      help="max helix turns (default 3.0)")
    r.add_argument("--radius",     type=float,            default=0.12,     help="max helix radius (default 0.12)")
    r.add_argument("--rod-radius", type=float,            default=0.008,    help="visual tube radius (default 0.008)")
    r.add_argument("--wall",       type=float,            default=None,     help="wall y-position, e.g. -1.05 (default: none)")
    r.add_argument("--color",      type=lambda x: int(x, 0), default=0xff3311, help="colour as hex integer (default 0xff3311)")
    r.add_argument("--output",     type=str,              default="data.js", help="output path (default: data.js)")

    # shell
    s = sub.add_parser("shell", help="generate shell/plate data.js")
    s.add_argument("--rows",      type=int,              default=20,       help="grid rows (default 20)")
    s.add_argument("--cols",      type=int,              default=20,       help="grid cols (default 20)")
    s.add_argument("--frames",    type=int,              default=120,      help="number of snapshots (default 120)")
    s.add_argument("--amplitude", type=float,            default=0.08,     help="wave amplitude (default 0.08)")
    s.add_argument("--freq",      type=float,            default=2.0,      help="spatial frequency (default 2.0)")
    s.add_argument("--wall",      type=float,            default=None,     help="wall y-position, e.g. -0.25 (default: none)")
    s.add_argument("--color",     type=lambda x: int(x, 0), default=0x4488cc, help="colour as hex integer (default 0x4488cc)")
    s.add_argument("--output",    type=str,              default="data.js", help="output path (default: data.js)")

    args = p.parse_args()

    if args.cmd == "init":
        cmd_init(args)

    elif args.cmd == "rod":
        import json
        data = generate_rod(
            n_frames    = args.frames,
            nv          = args.nv,
            n_turns_max = args.turns,
            radius_max  = args.radius,
            rod_radius  = args.rod_radius,
            wall_y      = args.wall,
            color       = args.color,
        )
        out = Path(args.output)
        out.write_text("const MECHVIEW_DATA = " + json.dumps(data) + ";")
        print(f"Generated {args.frames} frames  |  {args.nv} nodes each  |  {out}")
        print("Open index.html in Chrome (no server needed).")

    elif args.cmd == "shell":
        import json
        data = generate_shell(
            rows      = args.rows,
            cols      = args.cols,
            n_frames  = args.frames,
            amplitude = args.amplitude,
            freq      = args.freq,
            wall_y    = args.wall,
            color     = args.color,
        )
        out = Path(args.output)
        n_tri = len(data["faces"])
        out.write_text("const MECHVIEW_DATA = " + json.dumps(data) + ";")
        print(f"Generated {args.frames} frames  |  {args.rows}×{args.cols} grid ({n_tri} triangles)  |  {out}")
        print("Open index.html in Chrome (no server needed).")
