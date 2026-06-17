#!/usr/bin/env python
"""Assemble LSFS preview PNG frames into an animated GIF.

Usage:
  python tools/assemble_frames.py build/cinematic_preview build/cinematic_preview.gif --fps 12
"""

import argparse
import glob
import os
import sys

try:
    from PIL import Image
except ImportError:
    Image = None


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Assemble PNG frames into a GIF")
    parser.add_argument("frame_dir", help="directory containing frame_####.png files")
    parser.add_argument("out_gif", help="output GIF path")
    parser.add_argument("--fps", type=float, default=12.0, help="frames per second")
    parser.add_argument("--pattern", default="frame_*.png", help="frame filename glob")
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    return args


def main(argv=None):
    if Image is None:
        print("status=fail error=Pillow is required to assemble GIFs; PNG frames were not modified",
              file=sys.stderr)
        return 1
    args = parse_args(sys.argv[1:] if argv is None else argv)
    pattern = os.path.join(args.frame_dir, args.pattern)
    paths = sorted(glob.glob(pattern))
    if not paths:
        print(f"status=fail error=no frames matched {pattern}", file=sys.stderr)
        return 1
    images = []
    try:
        for path in paths:
            with Image.open(path) as img:
                images.append(img.convert("P", palette=Image.Palette.ADAPTIVE))
        parent = os.path.dirname(os.path.abspath(args.out_gif))
        if parent:
            os.makedirs(parent, exist_ok=True)
        duration_ms = max(1, int(round(1000.0 / args.fps)))
        images[0].save(args.out_gif,
                       save_all=True,
                       append_images=images[1:],
                       duration=duration_ms,
                       loop=0)
    except OSError as exc:
        print(f"status=fail error={exc}", file=sys.stderr)
        return 1

    print(f"frames={len(images)}")
    print(f"gif={args.out_gif}")
    print("status=ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
