#!/usr/bin/env python
"""Render a lightweight 2D preview from Mitsuba XML export geometry."""

import argparse
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from build_bridge_review_package import posix_rel, read_json, require_file, write_json, write_text

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None
    ImageDraw = None


BG_TOP = (7, 12, 17)
BG_BOTTOM = (19, 27, 34)
WATER = (64, 170, 225, 96)
WATER_RIM = (195, 240, 255, 150)
PHASE = (42, 96, 162, 118)
SPRAY = (230, 250, 255, 220)
FOAM = (245, 245, 225, 225)
BUBBLE = (255, 210, 126, 220)
DROPLET = (190, 230, 255, 220)


def fail(message):
    raise SystemExit(message)


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(path.replace("/", os.sep))


def as_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def selected_items(items, requested=None):
    if not items:
        return []
    if requested is None or requested <= 0 or requested >= len(items):
        return items
    if requested == 1:
        return [items[0]]
    indices = sorted(set(round(i * (len(items) - 1) / float(requested - 1)) for i in range(requested)))
    return [items[index] for index in indices]


def xml_attr_child(node, tag, name):
    for child in node:
        if child.tag == tag and child.attrib.get("name") == name:
            return child
    return None


def parse_scene(path):
    root = ET.parse(path).getroot()
    water_mesh = None
    spheres = []
    for shape in root.iter("shape"):
        shape_type = shape.attrib.get("type")
        if shape_type == "obj":
            filename = xml_attr_child(shape, "string", "filename")
            if filename is not None:
                water_mesh = resolve_path(filename.attrib.get("value"))
        elif shape_type == "sphere":
            center = xml_attr_child(shape, "point", "center")
            radius_node = xml_attr_child(shape, "float", "radius")
            ref = xml_attr_child(shape, "ref", "bsdf")
            if center is None:
                continue
            spheres.append({
                "x": as_float(center.attrib.get("x")),
                "y": as_float(center.attrib.get("y")),
                "z": as_float(center.attrib.get("z")),
                "radius": as_float(radius_node.attrib.get("value"), 0.05) if radius_node is not None else 0.05,
                "material": ref.attrib.get("id") if ref is not None else "",
            })
    return {
        "water_mesh": water_mesh,
        "spheres": spheres,
    }


def read_obj_vertices(path, max_vertices):
    vertices = []
    if not path or not os.path.isfile(path):
        return vertices
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("v "):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            vertices.append((as_float(parts[1]), as_float(parts[2]), as_float(parts[3])))
    if max_vertices > 0 and len(vertices) > max_vertices:
        return selected_items(vertices, max_vertices)
    return vertices


def color_for_material(material):
    if "phase_volume" in material:
        return PHASE
    if "foam" in material:
        return FOAM
    if "bubble" in material:
        return BUBBLE
    if "droplet" in material:
        return DROPLET
    return SPRAY


def make_background(width, height):
    img = Image.new("RGBA", (width, height), BG_TOP + (255,))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        t = y / float(max(1, height - 1))
        color = tuple(int(BG_TOP[i] * (1.0 - t) + BG_BOTTOM[i] * t) for i in range(3))
        draw.line([(0, y), (width, y)], fill=color + (255,))
    return img


def projector(bounds, width, height):
    x_min, x_max, z_min, z_max = bounds
    pad = 24
    sx = (width - 2 * pad) / max(1e-6, x_max - x_min)
    sz = (height - 2 * pad) / max(1e-6, z_max - z_min)
    scale = min(sx, sz)
    x_offset = (width - scale * (x_max - x_min)) * 0.5
    z_offset = (height - scale * (z_max - z_min)) * 0.5

    def project(x, z):
        px = x_offset + (x - x_min) * scale
        py = height - (z_offset + (z - z_min) * scale)
        return px, py, scale
    return project


def draw_circle(draw, mask, x, y, radius, fill):
    box = (x - radius, y - radius, x + radius, y + radius)
    draw.ellipse(box, fill=fill)
    mask.ellipse(box, fill=255)


def render_frame(scene, vertices, out_path, args):
    width = args.width
    height = args.height
    project = projector((args.x_min, args.x_max, args.z_min, args.z_max), width, height)
    img = make_background(width, height)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    mask_img = Image.new("L", (width, height), 0)
    mask = ImageDraw.Draw(mask_img)

    for index, (x, _y, z) in enumerate(vertices):
        px, py, scale = project(x, z)
        radius = 1.2 if index % 8 else 1.8
        draw_circle(draw, mask, px, py, radius, WATER_RIM if index % 8 == 0 else WATER)

    for sphere in scene["spheres"]:
        px, py, scale = project(sphere["x"], sphere["z"])
        radius = max(1.4, sphere["radius"] * scale * args.proxy_pixel_scale)
        draw_circle(draw, mask, px, py, radius, color_for_material(sphere["material"]))

    img = Image.alpha_composite(img, overlay)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.convert("RGB").save(out_path)
    pixels = width * height
    hist = mask_img.histogram()
    occupied = sum(hist[1:])
    return occupied / float(max(1, pixels))


def render_preview(args):
    if Image is None:
        fail("Pillow is required for Mitsuba XML preview rendering")
    root = os.getcwd()
    export_path = require_file(args.export, "mitsuba export")
    export = read_json(export_path)
    if export.get("schema") != "lsfs_mitsuba_xml_export":
        fail(f"{args.export}: expected lsfs_mitsuba_xml_export schema")
    if export.get("status") != "ready":
        fail(f"{args.export}: export status is {export.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    mesh_cache = {}
    frames = []
    min_occupancy = None
    total_spheres = 0
    for index, frame in enumerate(selected_items(export.get("frames") or [], args.frames)):
        xml_path = resolve_path((frame.get("xml_scene") or {}).get("path") or (frame.get("xml_scene") or {}).get("repo_path"))
        scene = parse_scene(xml_path)
        mesh = scene.get("water_mesh")
        if mesh not in mesh_cache:
            mesh_cache[mesh] = read_obj_vertices(mesh, args.max_water_vertices)
        out_path = os.path.join(out_dir, f"frame_{index:04d}.png")
        occupancy = render_frame(scene, mesh_cache[mesh], out_path, args)
        min_occupancy = occupancy if min_occupancy is None else min(min_occupancy, occupancy)
        total_spheres += len(scene["spheres"])
        frames.append({
            "frame": index,
            "source_output_frame": frame.get("output_frame"),
            "xml_scene": posix_rel(xml_path, root),
            "png": posix_rel(out_path, root),
            "water_vertices_drawn": len(mesh_cache[mesh]),
            "sphere_shapes": len(scene["spheres"]),
            "occupancy": occupancy,
        })

    summary = {
        "schema": "lsfs_mitsuba_xml_preview",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "renderer": "mitsuba_xml_preview",
        "source": {
            "path": export_path,
            "repo_path": posix_rel(export_path, root),
        },
        "frame_count": len(frames),
        "width": args.width,
        "height": args.height,
        "projection": "xz_topdown",
        "bounds": {
            "x_min": args.x_min,
            "x_max": args.x_max,
            "z_min": args.z_min,
            "z_max": args.z_max,
        },
        "min_occupancy": min_occupancy,
        "secondary_channel": "all",
        "water_reconstruction": True,
        "max_water_vertices": args.max_water_vertices,
        "total_sphere_shapes": total_spheres,
        "frames": frames,
    }
    summary_path = os.path.join(out_dir, "render_summary.json")
    write_json(summary_path, summary)
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(f"status=ok frames={len(frames)} min_occupancy={min_occupancy} summary={summary_path}")
    return summary_path


def markdown_report(summary, summary_path, root, next_text):
    lines = [
        "# Mitsuba XML Preview",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary: `{posix_rel(summary_path, root)}`",
        f"Source export: `{summary.get('source', {}).get('repo_path')}`",
        "",
        "## Result",
        "",
        f"- Frames: `{summary.get('frame_count')}`",
        f"- Resolution: `{summary.get('width')} x {summary.get('height')}`",
        f"- Projection: `{summary.get('projection')}`",
        f"- Minimum occupancy: `{summary.get('min_occupancy')}`",
        f"- Total sphere shapes: `{summary.get('total_sphere_shapes')}`",
        f"- Max water vertices per frame: `{summary.get('max_water_vertices')}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Source Output | Water Vertices | Sphere Shapes | Occupancy | PNG |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    frames = summary.get("frames", [])
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('source_output_frame')} | "
            f"{frame.get('water_vertices_drawn')} | {frame.get('sphere_shapes')} | "
            f"{frame.get('occupancy')} | `{frame.get('png')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Preview a Mitsuba XML export as 2D PNG frames")
    parser.add_argument("export")
    parser.add_argument("out_dir")
    parser.add_argument("--frames", type=int)
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=540)
    parser.add_argument("--x-min", type=float, default=0.0)
    parser.add_argument("--x-max", type=float, default=36.0)
    parser.add_argument("--z-min", type=float, default=0.0)
    parser.add_argument("--z-max", type=float, default=28.0)
    parser.add_argument("--max-water-vertices", type=int, default=7000)
    parser.add_argument("--proxy-pixel-scale", type=float, default=0.85)
    parser.add_argument("--report")
    parser.add_argument("--next", default="Use this preview to inspect Mitsuba XML geometry before offline rendering.")
    args = parser.parse_args(argv)
    if args.frames is not None and args.frames <= 0:
        parser.error("frames must be positive")
    if args.width <= 0 or args.height <= 0:
        parser.error("width and height must be positive")
    if args.x_max <= args.x_min or args.z_max <= args.z_min:
        parser.error("invalid projection bounds")
    if args.max_water_vertices <= 0:
        parser.error("max-water-vertices must be positive")
    if args.proxy_pixel_scale <= 0.0:
        parser.error("proxy-pixel-scale must be positive")
    render_preview(args)


if __name__ == "__main__":
    main()
