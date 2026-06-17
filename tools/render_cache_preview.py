#!/usr/bin/env python
"""Preview renderer for LSFS 3D JSONL render caches.

Reads JSONL frames produced by apps/export_render_cache3d.cpp and writes a
quick projected PNG sequence plus an animated GIF. This is a cache/schema
consumer and smoke-visualization tool, not the final SPEC-4 ray tracer.

Usage:
  python tools/render_cache_preview.py <manifest.json|cache.jsonl|cache-dir|glob> [out_dir] [scale] [options]
"""

import argparse
import glob
import json
import math
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
AGE_YOUNG = np.array([170, 235, 255], float)
AGE_OLD = np.array([255, 112, 70], float)
SPEED_SLOW = np.array([70, 145, 255], float)
SPEED_FAST = np.array([255, 238, 145], float)


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


def add_colored_particle(weight_field, color_field, pos, dx, scale, weight, color):
    height, width = weight_field.shape
    pi, pj = pixel_from_position(pos, dx, scale, height)
    if 0 <= pi < width and 0 <= pj < height:
        weight_field[pj, pi] += weight
        color_field[pj, pi, :] += color * weight


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


def secondary_particles(frame, dx):
    cell_volume = max(1e-12, dx * dx * dx)
    out = []
    for p in frame["particles"]:
        kind = p.get("kind", "primary")
        if kind not in ("secondary_droplet", "secondary_bubble"):
            continue
        pos = p.get("position")
        vel = p.get("velocity", [0.0, 0.0, 0.0])
        if not pos or len(pos) != 3 or not vel or len(vel) != 3:
            continue
        volume_weight = max(0.25, float(p.get("volume", cell_volume)) / cell_volume)
        speed = math.sqrt(sum(float(v) * float(v) for v in vel))
        age = max(0.0, float(p.get("age", 0.0)))
        out.append({
            "kind": kind,
            "position": pos,
            "weight": volume_weight,
            "age": age,
            "speed": speed,
        })
    return out


def secondary_color(particle, mode, max_age, max_speed):
    if mode == "type":
        return DROPLET if particle["kind"] == "secondary_droplet" else BUBBLE
    if mode == "age":
        t = particle["age"] / max(max_age, 1.0)
        return AGE_YOUNG * (1.0 - t) + AGE_OLD * t
    if mode == "speed":
        t = particle["speed"] / max(max_speed, 1e-9)
        return SPEED_SLOW * (1.0 - t) + SPEED_FAST * t
    raise ValueError(f"unknown secondary mode: {mode}")


def overlay_secondary(out, frame, scale, options):
    dx = frame["dx"]
    secondary = secondary_particles(frame, dx)
    if not secondary or options.secondary_gain <= 0.0:
        return out

    height, width, _ = out.shape
    weight = np.zeros((height, width), float)
    color = np.zeros((height, width, 3), float)
    max_age = max(p["age"] for p in secondary)
    max_speed = max(p["speed"] for p in secondary)

    for p in secondary:
        c = secondary_color(p, options.secondary_mode, max_age, max_speed)
        add_colored_particle(weight, color, p["position"], dx, scale, p["weight"], c)

    sigma = max(0.5, scale * 0.5 * options.secondary_radius)
    weight = blur2d(weight, sigma)
    for channel in range(3):
        color[:, :, channel] = blur2d(color[:, :, channel], sigma)

    nz_weight = weight[weight > 1e-9]
    ref = np.percentile(nz_weight, 88) if nz_weight.size else 1.0
    alpha = smoothstep(weight / (ref + 1e-9)) * np.clip(options.secondary_gain, 0.0, 4.0) * 0.68
    alpha = np.clip(alpha, 0.0, 1.0)
    color = color / (weight[..., None] + 1e-9)
    return out * (1.0 - alpha[..., None]) + color * alpha[..., None]


def render_frame(frame, scale, options):
    nx, ny, nz = frame["dims"]
    dx = frame["dx"]
    width, height = nx * scale, ny * scale
    liquid = np.zeros((height, width), float)

    if not options.hide_primary_water:
        splat_phase_cells(liquid, frame["phase_cells"], frame["dims"], scale)

    cell_volume = max(1e-12, dx * dx * dx)
    for p in frame["particles"]:
        pos = p.get("position")
        if not pos or len(pos) != 3:
            continue
        volume_weight = max(0.25, float(p.get("volume", cell_volume)) / cell_volume)
        kind = p.get("kind", "primary")
        phase = p.get("phase", "liquid")
        if kind == "primary" and phase == "liquid" and not options.hide_primary_water:
            add_particle(liquid, pos, dx, scale, 0.18 * volume_weight)

    liquid = blur2d(liquid, max(0.5, scale * 0.75))

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
    out = overlay_secondary(out, frame, scale, options)

    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Preview LSFS 3D render cache frames")
    parser.add_argument("src", nargs="?", default=".",
                        help="manifest JSON, JSONL frame, directory, or glob")
    parser.add_argument("out_dir", nargs="?", default="render_cache_preview",
                        help="output directory for PNG frames and GIF")
    parser.add_argument("scale", nargs="?", type=int, default=6,
                        help="pixels per simulation cell")
    parser.add_argument("--secondary-mode", choices=("type", "age", "speed"), default="type",
                        help="secondary droplet/bubble coloring mode")
    parser.add_argument("--secondary-gain", type=float, default=1.0,
                        help="secondary overlay opacity multiplier")
    parser.add_argument("--secondary-radius", type=float, default=1.0,
                        help="secondary particle splat radius multiplier")
    parser.add_argument("--hide-primary-water", action="store_true",
                        help="render only background plus secondary particle overlay")
    args = parser.parse_args(argv)
    if args.scale <= 0:
        parser.error("scale must be positive")
    if args.secondary_gain < 0.0 or not np.isfinite(args.secondary_gain):
        parser.error("secondary-gain must be finite and non-negative")
    if args.secondary_radius <= 0.0 or not np.isfinite(args.secondary_radius):
        parser.error("secondary-radius must be finite and positive")
    return args


def main(argv=None):
    options = parse_args(sys.argv[1:] if argv is None else argv)
    src = options.src
    out_dir = options.out_dir
    scale = options.scale

    files = cache_inputs(src)
    if not files:
        print(f"no JSONL cache frames found for {src}", file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    images = []
    for idx, path in enumerate(files):
        frame = read_cache(path)
        img = render_frame(frame, scale, options)
        png = os.path.join(out_dir, f"cache_preview_{idx:03d}.png")
        img.save(png)
        images.append(img)

    gif = os.path.join(out_dir, "cache_preview.gif")
    images[0].save(gif, save_all=True, append_images=images[1:], duration=120, loop=0)
    print(f"rendered {len(images)} frames -> {gif}")
    print(f"secondary_mode={options.secondary_mode}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
