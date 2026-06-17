#!/usr/bin/env python
"""Preview renderer for LSFS 3D JSONL render caches.

Reads JSONL frames produced by apps/export_render_cache3d.cpp and writes a
quick projected PNG sequence plus an animated GIF. This is a cache/schema
consumer and smoke-visualization tool, not the final SPEC-4 ray tracer.

Usage:
  python tools/render_cache_preview.py <manifest.json|cache.jsonl|cache-dir|glob> [out_dir] [scale]
"""

import glob
import json
import os
import sys

import numpy as np
from PIL import Image

try:
    from scipy.ndimage import gaussian_filter

    def blur2d(a, sigma):
        return gaussian_filter(a, sigma)
except Exception:

    def blur2d(a, sigma):
        sigma = max(0.25, float(sigma))
        r = max(1, int(3 * sigma))
        x = np.arange(-r, r + 1)
        k = np.exp(-(x * x) / (2.0 * sigma * sigma))
        k /= k.sum()
        a = np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 1, a)
        a = np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 0, a)
        return a


BG_TOP = np.array([7, 10, 16], float)
BG_BOT = np.array([20, 27, 34], float)
WATER_DEEP = np.array([12, 45, 92], float)
WATER_SHALLOW = np.array([65, 160, 215], float)
RIM = np.array([185, 230, 250], float)
DROPLET = np.array([195, 240, 255], float)
BUBBLE = np.array([245, 205, 120], float)


def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def lerp(a, b, t):
    return a + (b - a) * t[..., None]


def cache_inputs(src):
    if os.path.isfile(src) and src.lower().endswith(".json"):
        manifest_files = cache_inputs_from_manifest(src)
        if manifest_files is not None:
            return manifest_files
    if any(ch in src for ch in "*?[]"):
        files = sorted(glob.glob(src))
    elif os.path.isdir(src):
        files = sorted(glob.glob(os.path.join(src, "*.jsonl")))
    else:
        files = [src]
    return [p for p in files if os.path.isfile(p)]


def resolve_manifest_path(base_dir, path):
    if os.path.isabs(path):
        return path
    base_candidate = os.path.join(base_dir, path)
    if os.path.isfile(base_candidate):
        return base_candidate
    return path


def cache_inputs_from_manifest(path):
    with open(path, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return None
    if data.get("lsfs_cache3d_manifest_version") != 1:
        return None

    base_dir = os.path.dirname(os.path.abspath(path))
    frames = data.get("frames", [])
    files = []
    for frame in frames:
        frame_path = frame.get("path")
        if not isinstance(frame_path, str) or not frame_path:
            raise RuntimeError(f"{path}: manifest frame missing path")
        files.append(resolve_manifest_path(base_dir, frame_path))
    missing = [p for p in files if not os.path.isfile(p)]
    if missing:
        raise RuntimeError(f"{path}: manifest references missing frame {missing[0]}")
    return files


def read_cache(path):
    frame = {
        "path": path,
        "dims": None,
        "dx": 1.0,
        "frame": None,
        "time": 0.0,
        "phase_cells": [],
        "particles": [],
    }
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"{path}:{line_no}: invalid JSON: {exc}") from exc

            section = rec.get("section")
            if section == "header":
                frame["dims"] = tuple(int(v) for v in rec["dims"])
                frame["dx"] = float(rec.get("dx", 1.0))
                frame["frame"] = int(rec.get("frame", 0))
                frame["time"] = float(rec.get("time", 0.0))
            elif section == "phase_cell":
                frame["phase_cells"].append(rec)
            elif section == "particle":
                frame["particles"].append(rec)

    if not frame["dims"]:
        raise RuntimeError(f"{path}: missing header dims")
    return frame


def pixel_from_position(pos, dx, scale, height):
    x = float(pos[0]) / dx * scale
    y = float(pos[1]) / dx * scale
    return int(x), int(height - 1 - y)


def add_particle(field, pos, dx, scale, weight):
    height, width = field.shape
    pi, pj = pixel_from_position(pos, dx, scale, height)
    if 0 <= pi < width and 0 <= pj < height:
        field[pj, pi] += weight


def splat_phase_cells(field, cells, dims, scale):
    nx, ny, nz = dims
    height, width = field.shape
    z_norm = max(1.0, nz / 12.0)
    for cell in cells:
        i = int(cell.get("i", 0))
        j = int(cell.get("j", 0))
        level = int(cell.get("level", 0))
        step = max(1, 1 << max(0, level))
        phi = max(0.0, float(cell.get("phi", 0.0)))
        if phi <= 0.0:
            continue

        x0 = max(0, i * scale)
        x1 = min(width, (i + step) * scale)
        y0 = max(0, height - min(ny, j + step) * scale)
        y1 = min(height, height - j * scale)
        if x0 >= x1 or y0 >= y1:
            continue

        # Coarse MR cells represent multiple z layers; weight by z extent while
        # keeping the reference normalized enough for small smoke previews.
        field[y0:y1, x0:x1] += phi * step / z_norm


def render_frame(frame, scale):
    nx, ny, nz = frame["dims"]
    dx = frame["dx"]
    width, height = nx * scale, ny * scale
    liquid = np.zeros((height, width), float)
    droplets = np.zeros((height, width), float)
    bubbles = np.zeros((height, width), float)

    splat_phase_cells(liquid, frame["phase_cells"], frame["dims"], scale)

    cell_volume = max(1e-12, dx * dx * dx)
    for p in frame["particles"]:
        pos = p.get("position")
        if not pos or len(pos) != 3:
            continue
        volume_weight = max(0.25, float(p.get("volume", cell_volume)) / cell_volume)
        kind = p.get("kind", "primary")
        phase = p.get("phase", "liquid")
        if kind == "secondary_droplet":
            add_particle(droplets, pos, dx, scale, volume_weight)
        elif kind == "secondary_bubble":
            add_particle(bubbles, pos, dx, scale, volume_weight)
        elif phase == "liquid":
            add_particle(liquid, pos, dx, scale, 0.18 * volume_weight)

    liquid = blur2d(liquid, max(0.5, scale * 0.75))
    droplets = blur2d(droplets, max(0.5, scale * 0.45))
    bubbles = blur2d(bubbles, max(0.5, scale * 0.55))

    nz_liquid = liquid[liquid > 1e-7]
    ref = np.percentile(nz_liquid, 82) if nz_liquid.size else 1.0
    opacity = smoothstep(liquid / (ref + 1e-9))

    gy = np.linspace(0, 1, height)[:, None]
    bg = BG_TOP[None, None, :] * (1 - gy[..., None]) + BG_BOT[None, None, :] * gy[..., None]
    bg = np.broadcast_to(bg, (height, width, 3)).copy()

    water = lerp(WATER_SHALLOW, WATER_DEEP, smoothstep(opacity))
    gradj, gradi = np.gradient(opacity)
    grad = np.sqrt(gradi * gradi + gradj * gradj)
    rim = smoothstep(grad / (grad.max() + 1e-9) * 3.0)
    topface = np.clip(gradj, 0, None)
    topface /= topface.max() + 1e-9
    spec = rim * (0.4 + 0.6 * smoothstep(topface * 2.0))

    out = bg * (1 - opacity[..., None]) + water * opacity[..., None]
    out += RIM[None, None, :] * spec[..., None] * 0.85

    if droplets.max() > 1e-9:
        d = smoothstep(droplets / (np.percentile(droplets[droplets > 1e-9], 90) + 1e-9))
        out = out * (1 - 0.55 * d[..., None]) + DROPLET[None, None, :] * (0.55 * d[..., None])
    if bubbles.max() > 1e-9:
        b = smoothstep(bubbles / (np.percentile(bubbles[bubbles > 1e-9], 90) + 1e-9))
        out = out * (1 - 0.45 * b[..., None]) + BUBBLE[None, None, :] * (0.45 * b[..., None])

    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "."
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "render_cache_preview"
    scale = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    if scale <= 0:
        print("scale must be positive", file=sys.stderr)
        return 2

    files = cache_inputs(src)
    if not files:
        print(f"no JSONL cache frames found for {src}", file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    images = []
    for idx, path in enumerate(files):
        frame = read_cache(path)
        img = render_frame(frame, scale)
        png = os.path.join(out_dir, f"cache_preview_{idx:03d}.png")
        img.save(png)
        images.append(img)

    gif = os.path.join(out_dir, "cache_preview.gif")
    images[0].save(gif, save_all=True, append_images=images[1:], duration=120, loop=0)
    print(f"rendered {len(images)} frames -> {gif}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
