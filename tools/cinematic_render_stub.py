#!/usr/bin/env python
"""Render a local cinematic preview from LSFS 3D render cache data.

This is a preview renderer, not the final SPEC-4 renderer. It accepts a
canonical render cache manifest, an S38 converted sequence.json bundle, an S273
external render bundle, or a single JSONL frame, then writes frame_####.png
images plus render_summary.json.

Usage:
  python tools/cinematic_render_stub.py <manifest.json|sequence.json|external_render_bundle.json|frame.jsonl> <out_dir> --frames 12
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
SPRAY = (230, 250, 255, 225)
FOAM = (238, 238, 220, 215)
MOTION = (255, 255, 255, 95)
MESH_EDGE = (215, 245, 255, 62)


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


def read_obj_mesh(path):
    vertices = []
    faces = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("v "):
                parts = line.split()
                if len(parts) >= 4:
                    vertices.append((as_float(parts[1]), as_float(parts[2]), as_float(parts[3])))
            elif line.startswith("f "):
                face = []
                for token in line.split()[1:]:
                    head = token.split("/")[0]
                    idx = as_int(head, 0)
                    if idx > 0:
                        face.append(idx - 1)
                if len(face) >= 3:
                    faces.append(face)
    return {"vertices": vertices, "faces": faces}


def resolve_path(base_dir, path):
    if os.path.isabs(path):
        return path
    candidate = os.path.join(base_dir, path)
    if os.path.isfile(candidate):
        return candidate
    return path


def load_water_reconstruction(path):
    if not path:
        return None
    data = read_json(path)
    if data.get("reconstructor") != "lsfs_water_reconstruction":
        fail(f"{path}: not an LSFS water reconstruction index")
    base_dir = os.path.dirname(os.path.abspath(path))
    frames = []
    for frame in data.get("frames", []):
        mesh = frame.get("mesh")
        if not isinstance(mesh, str) or not mesh:
            fail(f"{path}: reconstruction frame missing mesh")
        mesh_path = resolve_path(base_dir, mesh)
        if not os.path.isfile(mesh_path):
            fail(f"{path}: missing mesh {mesh!r}")
        frames.append({
            "mesh": mesh_path,
            "vertex_count": as_int(frame.get("vertex_count")),
            "face_count": as_int(frame.get("face_count")),
        })
    if not frames:
        fail(f"{path}: water reconstruction has no frames")
    return frames


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


def select_resampled(items, out_index, out_count):
    if not items:
        return None
    if out_count <= 1 or len(items) == 1:
        return items[0]
    src_index = round(out_index * (len(items) - 1) / max(1, out_count - 1))
    return items[src_index]


def load_bundle_asset(entry, key, label):
    asset = (entry.get("assets") or {}).get(key) or {}
    path = asset.get("path") or asset.get("repo_path")
    if not path:
        fail(f"{label}: missing {key} asset path")
    resolved = os.path.abspath(path) if os.path.isabs(path) else os.path.abspath(path.replace("/", os.sep))
    if not os.path.isfile(resolved):
        fail(f"{label}: missing {key} asset {path!r}")
    return resolved


def load_external_bundle(path, requested_frames):
    data = read_json(path)
    if data.get("schema") != "lsfs_bridge_external_render_bundle":
        fail(f"{path}: not an LSFS external render bundle")
    bundle_frames = data.get("frames", [])
    if not bundle_frames:
        fail(f"{path}: external render bundle has no frames")
    frames = []
    mesh_frames = []
    out_count = max(1, requested_frames)
    for out_index in range(out_count):
        entry = select_resampled(bundle_frames, out_index, out_count)
        label = f"{path}: frames[{entry.get('output_frame', out_index)}]"
        camera_path = load_bundle_asset(entry, "camera", label)
        particles_path = load_bundle_asset(entry, "particles", label)
        phase_path = load_bundle_asset(entry, "phase_cells", label)
        mesh_path = load_bundle_asset(entry, "water_mesh", label)
        payload = read_json(camera_path)
        frame = {
            "source": f"external_bundle:{entry.get('output_frame', out_index)}",
            "header": payload.get("header", {}),
            "camera": payload.get("camera", {}),
            "cinematic": payload.get("cinematic_metadata"),
            "phase_cells": read_phase_csv(phase_path),
            "particles": read_particle_csv(particles_path),
        }
        frames.append(normalize_frame(frame))
        mesh_frames.append({
            "mesh": mesh_path,
            "vertex_count": as_int(entry.get("water_mesh_vertex_count")),
            "face_count": as_int(entry.get("water_mesh_face_count")),
        })
    return frames, mesh_frames


def read_particle_csv(path):
    out = []
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            age = row.get("age", "")
            rec = {
                "section": "particle",
                "kind": row.get("kind", "primary"),
                "render_channel": row.get("render_channel", ""),
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
    if data.get("schema") == "lsfs_bridge_external_render_bundle":
        fail(f"{path}: external render bundle input requires the selected-frame loader")
    if data.get("lsfs_cache3d_manifest_version") == 1:
        return load_manifest(path)
    fail(f"{path}: expected manifest, sequence.json, external render bundle, or JSONL frame")


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


def default_render_channel(particle):
    channel = particle.get("render_channel")
    if channel in ("droplet", "spray", "foam", "bubble", "water", "air"):
        return channel
    kind = particle.get("kind", "primary")
    if kind == "secondary_bubble":
        return "bubble"
    if kind == "secondary_droplet":
        return "droplet"
    return "water" if particle.get("phase", "liquid") == "liquid" else "air"


def secondary_color_for_channel(channel):
    if channel == "spray":
        return SPRAY
    if channel == "foam":
        return FOAM
    if channel == "bubble":
        return BUBBLE
    return DROPLET


def select_mesh_frame(mesh_frames, out_index, out_count):
    if not mesh_frames:
        return None
    if out_count <= 1 or len(mesh_frames) == 1:
        return mesh_frames[0]
    idx = round(out_index * (len(mesh_frames) - 1) / max(1, out_count - 1))
    return mesh_frames[idx]


def draw_mesh_overlay(img, frame, mesh_frame, width, height, basis, scale):
    if not mesh_frame:
        return 0, 0
    mesh = read_obj_mesh(mesh_frame["mesh"])
    if not mesh["vertices"] or not mesh["faces"]:
        return 0, 0
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    projected = [project(v, frame, width, height, basis, scale) for v in mesh["vertices"]]
    max_faces = min(len(mesh["faces"]), 6000)
    stride = max(1, len(mesh["faces"]) // max_faces)
    for face in mesh["faces"][::stride]:
        points = []
        for idx in face:
            if 0 <= idx < len(projected):
                px, py, _ = projected[idx]
                points.append((px, py))
        if len(points) >= 3:
            for a, b in zip(points, points[1:] + points[:1]):
                draw.line([a, b], fill=MESH_EDGE, width=1)
    img.alpha_composite(layer)
    return len(mesh["vertices"]), len(mesh["faces"])


def render_frame(frame, out_path, width, height, secondary_channel, mesh_frame=None):
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
    mesh_vertex_count = 0
    mesh_face_count = 0

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
    channel_counts = {"droplet": 0, "spray": 0, "foam": 0, "bubble": 0}
    for particle in frame["particles"]:
        pos = vec3(particle.get("position"))
        vel = vec3(particle.get("velocity"))
        px, py, _ = project(pos, frame, width, height, basis, scale)
        if px < -80 or py < -80 or px > width + 80 or py > height + 80:
            continue
        kind = particle.get("kind", "primary")
        phase = particle.get("phase", "liquid")
        channel = default_render_channel(particle)
        volume_weight = max(0.25, as_float(particle.get("volume"), cell_volume) / cell_volume)
        if kind == "primary" and phase == "liquid":
            draw_ellipse(particle_draw, water_mask_draw, px, py, max(0.7, scale * 0.035 * volume_weight),
                         PRIMARY_DOT, mask_value=210)
        elif kind in ("secondary_droplet", "secondary_bubble"):
            if channel in channel_counts:
                channel_counts[channel] += 1
            if secondary_channel != "all" and channel != secondary_channel:
                continue
            color = secondary_color_for_channel(channel)
            speed = length(vel)
            radius = max(1.8, min(9.0, scale * 0.055 * math.sqrt(volume_weight) + speed * 0.08))
            end = project(vector_add(pos, vector_mul(vel, -0.12)), frame, width, height, basis, scale)
            particle_draw.line([(px, py), (end[0], end[1])], fill=MOTION, width=max(1, int(radius * 0.35)))
            draw_ellipse(particle_draw, secondary_mask_draw, px, py, radius, color)

    water_layer = water_layer.filter(ImageFilter.GaussianBlur(radius=0.55))
    particle_layer = particle_layer.filter(ImageFilter.GaussianBlur(radius=0.35))
    img = Image.alpha_composite(img, water_layer)
    img = Image.alpha_composite(img, particle_layer)
    mesh_vertex_count, mesh_face_count = draw_mesh_overlay(
        img, frame, mesh_frame, width, height, basis, scale)
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
        "secondary_channel_counts": channel_counts,
        "secondary_channel_filter": secondary_channel,
        "mesh_vertex_count": mesh_vertex_count,
        "mesh_face_count": mesh_face_count,
        "occupancy": occupancy,
    }


def count_nonzero(mask):
    hist = mask.histogram()
    return sum(hist[1:])


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Render cinematic PNG previews from LSFS cache data")
    parser.add_argument("src", help="render cache manifest, converted sequence.json, external render bundle, or JSONL frame")
    parser.add_argument("out_dir", help="output directory")
    parser.add_argument("--frames", type=int, default=12, help="number of preview frames to write")
    parser.add_argument("--width", type=int, default=1280, help="output image width")
    parser.add_argument("--height", type=int, default=720, help="output image height")
    parser.add_argument("--min-occupancy", type=float, default=0.01,
                        help="minimum water-or-secondary pixel occupancy required per frame")
    parser.add_argument("--secondary-channel", choices=("all", "droplet", "spray", "foam", "bubble"),
                        default="all", help="secondary render channel to draw")
    parser.add_argument("--water-reconstruction",
                        help="optional S41 water_reconstruction.json mesh overlay")
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
        source_data = None
        if os.path.isfile(args.src) and args.src.lower().endswith(".json"):
            source_data = read_json(args.src)
        if source_data and source_data.get("schema") == "lsfs_bridge_external_render_bundle":
            source_frames, bundle_mesh_frames = load_external_bundle(args.src, args.frames)
            mesh_frames = load_water_reconstruction(args.water_reconstruction) or bundle_mesh_frames
        else:
            source_frames = load_source(args.src)
            mesh_frames = load_water_reconstruction(args.water_reconstruction)
        os.makedirs(args.out_dir, exist_ok=True)
        summaries = []
        for i in range(args.frames):
            if args.frames == 1:
                src_index = 0
            else:
                src_index = round(i * (len(source_frames) - 1) / max(1, args.frames - 1))
            frame = source_frames[src_index % len(source_frames)]
            out_path = os.path.join(args.out_dir, f"frame_{i:04d}.png")
            summaries.append(render_frame(frame,
                                          out_path,
                                          args.width,
                                          args.height,
                                          args.secondary_channel,
                                          select_mesh_frame(mesh_frames, i, args.frames)))
        min_occupancy = min(item["occupancy"] for item in summaries) if summaries else 0.0
        summary = {
            "renderer": "lsfs_cinematic_render_stub",
            "version": 1,
            "source": args.src,
            "width": args.width,
            "height": args.height,
            "secondary_channel": args.secondary_channel,
            "water_reconstruction": args.water_reconstruction,
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
