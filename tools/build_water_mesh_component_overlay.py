#!/usr/bin/env python3
"""Build labeled overlays for projected LSFS water mesh components."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover
    Image = None
    ImageDraw = None

import analyze_water_mesh_component_visibility as visibility


COLORS = [
    (78, 170, 255, 220),
    (255, 104, 72, 230),
    (255, 206, 84, 220),
    (118, 220, 148, 220),
    (206, 134, 255, 220),
]


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def resolve_frame_image(frame):
    output = frame.get("output_png")
    if not isinstance(output, str) or not output:
        return None
    path = Path(output)
    return path if path.is_absolute() else path.resolve()


def projected_points(component, vertices, camera, width, height, max_points):
    points = []
    step = max(1, int(math.ceil(len(component["vertex_indices"]) / float(max(1, max_points)))))
    for vi in component["vertex_indices"][::step]:
        item = visibility.project_camera_point(vertices[vi], camera, width, height)
        if item is None:
            continue
        x = item["x"] * width
        y = (1.0 - item["y"]) * height
        points.append((x, y, item["x"], item["y"]))
    return points


def component_bounds(component, vertices, camera, width, height):
    items = []
    for vi in component["vertex_indices"]:
        item = visibility.project_camera_point(vertices[vi], camera, width, height)
        if item is not None:
            items.append(item)
    if not items:
        return None
    xs = [item["x"] for item in items]
    ys = [item["y"] for item in items]
    min_x = min(xs) * width
    max_x = max(xs) * width
    min_y = (1.0 - max(ys)) * height
    max_y = (1.0 - min(ys)) * height
    inside = sum(1 for item in items if 0.0 <= item["x"] <= 1.0 and 0.0 <= item["y"] <= 1.0)
    return {
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y,
        "inside_ratio": inside / float(max(1, len(component["vertex_indices"]))),
        "projected": len(items),
    }


def draw_component(draw, component, bounds, points, color, would_filter):
    if bounds is None:
        return
    width = max(2, 4 if would_filter else 2)
    box = [bounds["min_x"], bounds["min_y"], bounds["max_x"], bounds["max_y"]]
    draw.rectangle(box, outline=color, width=width)
    radius = 1.8 if would_filter else 1.2
    for x, y, nx, ny in points:
        if -0.1 <= nx <= 1.1 and -0.1 <= ny <= 1.1:
            draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)
    label = (
        f"C{component['rank']} faces={component['face_count']} "
        f"ratio={component['face_ratio']:.3f}"
    )
    if would_filter:
        label += " filter"
    label_x = max(6, min(box[0] + 6, 620))
    label_y = max(6, min(box[1] + 6, 340))
    text_bg = (8, 12, 16, 190)
    draw.rectangle([label_x - 4, label_y - 3, label_x + 245, label_y + 15], fill=text_bg)
    draw.text((label_x, label_y), label, fill=color)


def make_sheet(paths, out_path: Path, thumb_width):
    images = []
    resampling = getattr(Image, "Resampling", Image)
    resample_filter = getattr(resampling, "LANCZOS", getattr(Image, "BICUBIC", 3))
    for path in paths:
        with Image.open(path) as img:
            panel = img.convert("RGB")
            scale = thumb_width / float(panel.width)
            images.append(panel.resize((thumb_width, max(1, int(round(panel.height * scale)))), resample_filter))
    if not images:
        return
    pad = 12
    label_h = 26
    panel_h = max(img.height for img in images)
    sheet_w = pad + thumb_width + pad
    sheet_h = pad + len(images) * (label_h + panel_h + pad)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (14, 18, 22))
    draw = ImageDraw.Draw(sheet)
    for index, img in enumerate(images):
        y = pad + index * (label_h + panel_h + pad)
        draw.text((pad + 6, y + 7), f"overlay frame {index:04d}", fill=(224, 234, 240))
        cell = Image.new("RGB", (thumb_width, panel_h), (8, 10, 12))
        cell.paste(img, ((thumb_width - img.width) // 2, (panel_h - img.height) // 2))
        sheet.paste(cell, (pad, y + label_h))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)


def build_overlays(scene_spec_path: Path, reconstruction_path: Path, out_dir: Path,
                   filter_threshold, max_points, thumb_width):
    spec = read_json(scene_spec_path)
    width = int(spec.get("width", 640))
    height = int(spec.get("height", 360))
    meshes = visibility.reconstruction_meshes(reconstruction_path)
    mesh_cache = {}
    overlays = []
    component_rows = []
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for frame in spec.get("frames", []):
        image_path = resolve_frame_image(frame)
        selected_index = visibility.mesh_frame_index(frame.get("water_mesh", ""))
        if image_path is None or selected_index not in meshes:
            continue
        mesh_path = meshes[selected_index]["path"]
        if mesh_path not in mesh_cache:
            vertices, faces = visibility.parse_obj(mesh_path)
            mesh_cache[mesh_path] = (vertices, faces, visibility.mesh_components(vertices, faces))
        vertices, _faces, components = mesh_cache[mesh_path]
        with Image.open(image_path) as base:
            image = base.convert("RGBA")
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for component in components:
            would_filter = component["face_ratio"] < filter_threshold
            color = COLORS[(component["rank"] - 1) % len(COLORS)]
            if would_filter:
                color = (255, 86, 58, 235)
            bounds = component_bounds(component, vertices, frame.get("camera", {}), width, height)
            points = projected_points(component, vertices, frame.get("camera", {}), width, height, max_points)
            draw_component(draw, component, bounds, points, color, would_filter)
            component_rows.append({
                "render_frame": frame.get("index"),
                "selected_mesh_frame": selected_index,
                "component_rank": component["rank"],
                "face_count": component["face_count"],
                "face_ratio": component["face_ratio"],
                "would_filter": would_filter,
                "inside_ratio": None if bounds is None else bounds["inside_ratio"],
                "projected_vertex_count": None if bounds is None else bounds["projected"],
            })
        composed = Image.alpha_composite(image, overlay).convert("RGB")
        out_path = frames_dir / f"overlay_{int(frame.get('index', len(overlays))):04d}.png"
        composed.save(out_path)
        overlays.append(str(out_path))
    sheet_path = out_dir / "component_overlay_sheet.png"
    make_sheet([Path(path) for path in overlays], sheet_path, thumb_width)
    return {
        "schema": "lsfs_water_mesh_component_overlay",
        "version": 1,
        "scene_spec": str(scene_spec_path),
        "water_reconstruction": str(reconstruction_path),
        "filter_threshold": filter_threshold,
        "overlay_frames": overlays,
        "overlay_sheet": str(sheet_path),
        "component_rows": component_rows,
        "would_filter_components": sum(1 for row in component_rows if row["would_filter"]),
        "visible_would_filter_components": sum(
            1 for row in component_rows
            if row["would_filter"] and (row.get("inside_ratio") or 0.0) > 0.0
        ),
    }


def write_report(path: Path, summary, title) -> None:
    rows = summary.get("component_rows", [])
    lines = [
        f"# {title}",
        "",
        "## Status",
        "",
        "Passed.",
        "",
        "## Artifacts",
        "",
        f"- Overlay sheet: `{summary['overlay_sheet']}`",
        f"- Overlay frames: `{len(summary['overlay_frames'])}`",
        "",
        "## Summary",
        "",
        f"- Filter threshold: `{summary['filter_threshold']}`",
        f"- Component rows: `{len(rows)}`",
        f"- Would-filter components: `{summary['would_filter_components']}`",
        f"- Visible would-filter components: `{summary['visible_would_filter_components']}`",
        "",
        "## Components",
        "",
        "| Render frame | Mesh frame | Component | Face ratio | Would filter | Inside ratio |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.get('render_frame')} | {row.get('selected_mesh_frame')} | "
            f"{row.get('component_rank')} | {row.get('face_ratio'):.6g} | "
            f"`{row.get('would_filter')}` | {row.get('inside_ratio')} |"
        )
    lines.extend([
        "",
        "## Next",
        "",
        "Use the overlay sheet to classify whether the would-filter component is an artifact or meaningful separated water.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene_spec")
    parser.add_argument("water_reconstruction")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--filter-threshold", type=float, default=0.24)
    parser.add_argument("--max-points", type=int, default=800)
    parser.add_argument("--thumb-width", type=int, default=420)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Water Mesh Component Overlay")
    return parser.parse_args()


def main():
    if Image is None:
        raise RuntimeError("Pillow is required to build component overlays")
    args = parse_args()
    summary = build_overlays(Path(args.scene_spec),
                             Path(args.water_reconstruction),
                             Path(args.out_dir),
                             args.filter_threshold,
                             args.max_points,
                             args.thumb_width)
    summary_path = Path(args.out_dir) / "component_overlay_summary.json"
    write_json(summary_path, summary)
    if args.report:
        write_report(Path(args.report), summary, args.title)
    print("status=ok")
    print(f"frames={len(summary['overlay_frames'])}")
    print(f"would_filter_components={summary['would_filter_components']}")
    print(f"visible_would_filter_components={summary['visible_would_filter_components']}")
    print(f"sheet={summary['overlay_sheet']}")
    print(f"summary={summary_path}")
    if args.report:
        print(f"report={args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
