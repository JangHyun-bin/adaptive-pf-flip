#!/usr/bin/env python
"""Render a local cinematic preview from LSFS 3D render cache data.

This is a preview renderer, not the final SPEC-4 renderer. It accepts either a
canonical render cache manifest or an S38 converted sequence.json bundle, then
writes frame_####.png images plus render_summary.json.

Usage:
  python tools/cinematic_render_stub.py <manifest.json|sequence.json|frame.jsonl> <out_dir> --frames 12
"""

import argparse
import csv
import glob
import json
import math
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:
    Image = None
    ImageDraw = None
    ImageFilter = None


BG_TOP = (8, 11, 16)
BG_BOTTOM = (23, 30, 37)
WATER_DEEP = (18, 60, 105, 72)
WATER_MID = (56, 145, 205, 96)
WATER_RIM = (185, 232, 250, 90)
PRIMARY_DOT = (70, 178, 230, 42)
DROPLET = (204, 245, 255, 210)
BUBBLE = (255, 212, 126, 205)
MOTION = (255, 255, 255, 95)


class RenderError(Exception):
    pass


def fail(message):
    raise RenderError(message)


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        fail(f"{path}: invalid JSON: {exc}")


def read_jsonl(path):
    records = []
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                fail(f"{path}:{line_no}: invalid JSON: {exc}")
            if not isinstance(rec, dict):
                fail(f"{path}:{line_no}: expected object record")
            records.append(rec)
    if not records:
        fail(f"{path}: empty JSONL frame")
    return records


def resolve_path(base_dir, path):
    if os.path.isabs(path):
        return path
    candidate = os.path.join(base_dir, path)
    if os.path.isfile(candidate):
        return candidate
    return path


def section(records, name):
    found = [rec for rec in records if rec.get("section") == name]
    if not found:
        return None
    if len(found) > 1 and name not in ("particle", "phase_cell", "particles"):
        fail(f"expected one {name!r} section, found {len(found)}")
    return found[0]


def sections(records, name):
    return [rec for rec in records if rec.get("section") == name]


def as_float(value, fallback=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def as_int(value, fallback=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def vec3(value, fallback=(0.0, 0.0, 0.0)):
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return (as_float(value[0]), as_float(value[1]), as_float(value[2]))
    return fallback


def vector_add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def vector_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vector_mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def length(a):
    return math.sqrt(max(0.0, dot(a, a)))


def normalize(a, fallback):
    n = length(a)
    if n <= 1e-12:
        return fallback
    return (a[0] / n, a[1] / n, a[2] / n)


def load_manifest(path):
    data = read_json(path)
    if data.get("lsfs_cache3d_manifest_version") != 1:
        fail(f"{path}: not an LSFS render cache manifest")
    base_dir = os.path.dirname(os.path.abspath(path))
    frames = []
    for frame in data.get("frames", []):
        frame_path = resolve_path(base_dir, frame.get("path", ""))
        if not os.path.isfile(frame_path):
            fail(f"{path}: missing frame {frame.get('path')!r}")
        frames.append(load_jsonl_frame(frame_path, frame.get("path", frame_path)))
    if not frames:
        fail(f"{path}: manifest contains no frames")
    return frames


def load_jsonl_frame(path, display_path=None):
    records = read_jsonl(path)
    header = section(records, "header")
    camera = section(records, "camera")
    if header is None or camera is None:
        fail(f"{path}: missing header or camera section")
    frame = {
        "source": display_path or path,
        "header": header,
        "camera": camera,
        "cinematic": section(records, "cinematic_metadata"),
        "phase_cells": sections(records, "phase_cell"),
        "particles": sections(records, "particle"),
    }
    return normalize_frame(frame)


def load_sequence(path):
    data = read_json(path)
    if data.get("converter") != "lsfs_render_cache_converter":
        fail(f"{path}: not an LSFS converted sequence")
    base_dir = os.path.dirname(os.path.abspath(path))
    frames = []
    for entry in data.get("frames", []):
        camera_path = resolve_path(base_dir, entry.get("camera", ""))
        particles_path = resolve_path(base_dir, entry.get("particles", ""))
        phase_path = resolve_path(base_dir, entry.get("phase_cells", ""))
        if not os.path.isfile(camera_path):
            fail(f"{path}: missing camera file {entry.get('camera')!r}")
        if not os.path.isfile(particles_path):
            fail(f"{path}: missing particles file {entry.get('particles')!r}")
        if not os.path.isfile(phase_path):
            fail(f"{path}: missing phase cells file {entry.get('phase_cells')!r}")
        payload = read_json(camera_path)
        frame = {
            "source": entry.get("source_cache", camera_path),
            "header": payload.get("header", {}),
            "camera": payload.get("camera", {}),
            "cinematic": payload.get("cinematic_metadata"),
            "phase_cells": read_phase_csv(phase_path),
            "particles": read_particle_csv(particles_path),
        }
        frames.append(normalize_frame(frame))
    if not frames:
        fail(f"{path}: sequence contains no frames")
    return frames


def read_particle_csv(path):
    out = []
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            age = row.get("age", "")
            rec = {
                "section": "particle",
                "kind": row.get("kind", "primary"),
                "index": as_int(row.get("index")),
                "phase": row.get("phase", "liquid"),
                "position": [as_float(row.get("x")), as_float(row.get("y")), as_float(row.get("z"))],
                "velocity": [as_float(row.get("vx")), as_float(row.get("vy")), as_float(row.get("vz"))],
                "volume": as_float(row.get("volume"), 1.0),
            }
            if age != "":
                rec["age"] = as_int(age)
            out.append(rec)
    return out


def read_phase_csv(path):
    out = []
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            out.append({
                "section": "phase_cell",
                "i": as_int(row.get("i")),
                "j": as_int(row.get("j")),
                "k": as_int(row.get("k")),
                "level": as_int(row.get("level")),
                "marker": as_int(row.get("marker")),
                "phi": as_float(row.get("phi")),
                "liquid_volume": as_float(row.get("liquid_volume")),
            })
    return out


def normalize_frame(frame):
    header = frame["header"]
    dims = header.get("dims", [1, 1, 1])
    dx = max(1e-12, as_float(header.get("dx"), 1.0))
    frame["dims"] = (as_int(dims[0], 1), as_int(dims[1], 1), as_int(dims[2], 1))
    frame["dx"] = dx
    frame["frame"] = as_int(header.get("frame"), 0)
    frame["time"] = as_float(header.get("time"), 0.0)
    return frame


def load_source(path):
    if not os.path.isfile(path):
        fail(f"{path}: input not found")
    if path.lower().endswith(".jsonl"):
        return [load_jsonl_frame(path)]
    data = read_json(path)
    if data.get("converter") == "lsfs_render_cache_converter":
        return load_sequence(path)
    if data.get("lsfs_cache3d_manifest_version") == 1:
        return load_manifest(path)
    fail(f"{path}: expected manifest, sequence.json, or JSONL frame")


def make_background(width, height):
    img = Image.new("RGB", (width, height), BG_BOTTOM)
    draw = ImageDraw.Draw(img)
    denom = max(1, height - 1)
    for y in range(height):
        t = y / denom
        color = tuple(int(BG_TOP[i] * (1.0 - t) + BG_BOTTOM[i] * t) for i in range(3))
        draw.line([(0, y), (width, y)], fill=color)
    return img.convert("RGBA")


def camera_basis(frame):
    cam = frame["camera"]
    position = vec3(cam.get("position"), (0.0, 0.0, 1.0))
    target = vec3(cam.get("target"), (0.0, 0.0, 0.0))
    up_hint = vec3(cam.get("up"), (0.0, 1.0, 0.0))
    forward = normalize(vector_sub(target, position), (0.0, 0.0, -1.0))
    right = normalize(cross(forward, up_hint), (1.0, 0.0, 0.0))
    up = normalize(cross(right, forward), (0.0, 1.0, 0.0))
    return position, target, right, up, forward


def view_scale(frame, width, height):
    cinematic = frame.get("cinematic") or {}
    bounds_min = vec3(cinematic.get("frame_bounds_min"), (0.0, 0.0, 0.0))
    default_max = (
        frame["dims"][0] * frame["dx"],
        frame["dims"][1] * frame["dx"],
        frame["dims"][2] * frame["dx"],
    )
    bounds_max = vec3(cinematic.get("frame_bounds_max"), default_max)
    extent = max(bounds_max[0] - bounds_min[0],
                 bounds_max[1] - bounds_min[1],
                 bounds_max[2] - bounds_min[2],
                 frame["dx"])
    return min(width, height) * 0.74 / extent


def project(point, frame, width, height, basis, scale):
    _, target, right, up, forward = basis
    rel = vector_sub(point, target)
    x = width * 0.5 + dot(rel, right) * scale
    y = height * 0.54 - dot(rel, up) * scale
    z = dot(rel, forward)
    return x, y, z


def draw_ellipse(draw, mask_draw, cx, cy, radius, color, mask_value=255):
    r = max(0.75, radius)
    box = [cx - r, cy - r, cx + r, cy + r]
    draw.ellipse(box, fill=color)
    mask_draw.ellipse(box, fill=mask_value)


def phase_cell_center(cell, dx):
    step = 1 << max(0, as_int(cell.get("level"), 0))
    return (
        (as_float(cell.get("i")) + 0.5 * step) * dx,
        (as_float(cell.get("j")) + 0.5 * step) * dx,
        (as_float(cell.get("k")) + 0.5 * step) * dx,
    ), step


def render_frame(frame, out_path, width, height):
    img = make_background(width, height)
    water_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    particle_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    water_mask = Image.new("L", (width, height), 0)
    secondary_mask = Image.new("L", (width, height), 0)
    water_draw = ImageDraw.Draw(water_layer, "RGBA")
    particle_draw = ImageDraw.Draw(particle_layer, "RGBA")
    water_mask_draw = ImageDraw.Draw(water_mask)
    secondary_mask_draw = ImageDraw.Draw(secondary_mask)
    basis = camera_basis(frame)
    scale = view_scale(frame, width, height)
    dx = frame["dx"]

    depth_sorted_cells = []
    for cell in frame["phase_cells"]:
        phi = max(0.0, as_float(cell.get("phi")))
        liquid_volume = max(0.0, as_float(cell.get("liquid_volume")))
        if phi <= 0.0 and liquid_volume <= 0.0:
            continue
        center, step = phase_cell_center(cell, dx)
        px, py, depth = project(center, frame, width, height, basis, scale)
        if px < -80 or py < -80 or px > width + 80 or py > height + 80:
            continue
        depth_sorted_cells.append((depth, px, py, step, min(1.0, max(phi, liquid_volume / max(dx ** 3, 1e-12)))))
    depth_sorted_cells.sort()

    for _, px, py, step, weight in depth_sorted_cells:
        radius = max(1.2, step * dx * scale * 0.54)
        alpha = int(42 + 86 * min(1.0, weight))
        color = WATER_MID if weight > 0.15 else WATER_DEEP
        water_draw.ellipse([px - radius, py - radius, px + radius, py + radius],
                           fill=(color[0], color[1], color[2], alpha))
        water_mask_draw.ellipse([px - radius, py - radius, px + radius, py + radius], fill=255)

    rim = water_mask.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(radius=1.2))
    rim_layer = Image.new("RGBA", (width, height), (WATER_RIM[0], WATER_RIM[1], WATER_RIM[2], 0))
    rim_layer.putalpha(rim.point(lambda p: min(95, int(p * 0.72))))
    water_layer = Image.alpha_composite(water_layer, rim_layer)

    cell_volume = max(1e-12, dx ** 3)
    for particle in frame["particles"]:
        pos = vec3(particle.get("position"))
        vel = vec3(particle.get("velocity"))
        px, py, _ = project(pos, frame, width, height, basis, scale)
        if px < -80 or py < -80 or px > width + 80 or py > height + 80:
            continue
        kind = particle.get("kind", "primary")
        phase = particle.get("phase", "liquid")
        volume_weight = max(0.25, as_float(particle.get("volume"), cell_volume) / cell_volume)
        if kind == "primary" and phase == "liquid":
            draw_ellipse(particle_draw, water_mask_draw, px, py, max(0.7, scale * 0.035 * volume_weight),
                         PRIMARY_DOT, mask_value=210)
        elif kind in ("secondary_droplet", "secondary_bubble"):
            color = DROPLET if kind == "secondary_droplet" else BUBBLE
            speed = length(vel)
            radius = max(1.8, min(9.0, scale * 0.055 * math.sqrt(volume_weight) + speed * 0.08))
            end = project(vector_add(pos, vector_mul(vel, -0.12)), frame, width, height, basis, scale)
            particle_draw.line([(px, py), (end[0], end[1])], fill=MOTION, width=max(1, int(radius * 0.35)))
            draw_ellipse(particle_draw, secondary_mask_draw, px, py, radius, color)

    water_layer = water_layer.filter(ImageFilter.GaussianBlur(radius=0.55))
    particle_layer = particle_layer.filter(ImageFilter.GaussianBlur(radius=0.35))
    img = Image.alpha_composite(img, water_layer)
    img = Image.alpha_composite(img, particle_layer)
    img.convert("RGB").save(out_path)

    total_pixels = width * height
    water_pixels = count_nonzero(water_mask)
    secondary_pixels = count_nonzero(secondary_mask)
    occupancy = (water_pixels + secondary_pixels) / max(1, total_pixels)
    return {
        "path": os.path.basename(out_path),
        "source": frame["source"],
        "frame": frame["frame"],
        "time": frame["time"],
        "water_pixels": water_pixels,
        "secondary_pixels": secondary_pixels,
        "occupancy": occupancy,
    }


def count_nonzero(mask):
    hist = mask.histogram()
    return sum(hist[1:])


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Render cinematic PNG previews from LSFS cache data")
    parser.add_argument("src", help="render cache manifest, converted sequence.json, or JSONL frame")
    parser.add_argument("out_dir", help="output directory")
    parser.add_argument("--frames", type=int, default=12, help="number of preview frames to write")
    parser.add_argument("--width", type=int, default=1280, help="output image width")
    parser.add_argument("--height", type=int, default=720, help="output image height")
    parser.add_argument("--min-occupancy", type=float, default=0.01,
                        help="minimum water-or-secondary pixel occupancy required per frame")
    args = parser.parse_args(argv)
    if args.frames <= 0:
        parser.error("frames must be positive")
    if args.width <= 0 or args.height <= 0:
        parser.error("width and height must be positive")
    if args.min_occupancy < 0.0 or not math.isfinite(args.min_occupancy):
        parser.error("min-occupancy must be finite and non-negative")
    return args


def main(argv=None):
    if Image is None:
        print("status=fail error=Pillow is required for cinematic preview rendering", file=sys.stderr)
        return 1
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        source_frames = load_source(args.src)
        os.makedirs(args.out_dir, exist_ok=True)
        summaries = []
        for i in range(args.frames):
            if args.frames == 1:
                src_index = 0
            else:
                src_index = round(i * (len(source_frames) - 1) / max(1, args.frames - 1))
            frame = source_frames[src_index % len(source_frames)]
            out_path = os.path.join(args.out_dir, f"frame_{i:04d}.png")
            summaries.append(render_frame(frame, out_path, args.width, args.height))
        min_occupancy = min(item["occupancy"] for item in summaries) if summaries else 0.0
        summary = {
            "renderer": "lsfs_cinematic_render_stub",
            "version": 1,
            "source": args.src,
            "width": args.width,
            "height": args.height,
            "frame_count": len(summaries),
            "min_occupancy": min_occupancy,
            "frames": summaries,
        }
        summary_path = os.path.join(args.out_dir, "render_summary.json")
        with open(summary_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(summary, f, indent=2, sort_keys=True)
            f.write("\n")
        if min_occupancy < args.min_occupancy:
            fail(f"minimum occupancy {min_occupancy:.6g} below required {args.min_occupancy:.6g}")
    except RenderError as exc:
        print(f"status=fail error={exc}", file=sys.stderr)
        return 1

    print(f"frames={len(summaries)}")
    print(f"min_occupancy={min_occupancy:.17g}")
    print(f"summary={summary_path}")
    print("status=ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
